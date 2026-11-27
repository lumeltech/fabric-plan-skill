"""Existing-table initialization and bounded insert/update serialization.

Delete/upsert/replaceAll/distribute and audits/approvals require their full
operation contracts and are not silently mapped to ordinary row saves.
"""
import os,subprocess,copy,math
from decimal import Decimal
from pathlib import Path
from .codec import dumps
from .surfaces import powertable_source
from .paths import ASSETS

def row_access_setting(name,source_id,enabled):
    from .construct import guid
    setting={'name':name,'recordGuid':guid(),'sourceId':source_id,'settings':{'enabled':enabled}}
    # Product default: Add/Update carry "All users"; any other enabled action needs an audience too.
    if name in ('ROW_ADD','ROW_UPDATE') or enabled:
        setting['filters']=[{'recordGuid':guid(),'name':'all_users','filterType':1,'filter':{}}]
    return setting

def configured_table(name, table, connection, columns, *, explicit=False, creation_mode=2,
                     allow_add=True, allow_update=True, allow_delete=False):
    """Complete ALM grid from verified target source/schema; no old report/template.

    SQL rows are never changed by this constructor. Row actions reflect the
    authorized maintenance scope and still require effective runtime access.
    """
    from .construct import guid,schema,sheet_properties
    from .codec import load
    if creation_mode not in (1,2):
        raise ValueError('Use supported from-scratch (1) or existing-table (2) creation mode')
    if not columns or len({c['columnName'] for c in columns})!=len(columns):
        raise ValueError('Complete unique physical column configurations required')
    for c in columns:
        if not {'columnName','columnGuid','columnMeta','columnType','recordGuid'}<=c.keys():
            raise ValueError('Use column_config with physical SQL metadata')
    if any(not isinstance(x,bool) for x in (allow_add,allow_update,allow_delete)):
        raise ValueError('Row-action flags must be Boolean')
    source=powertable_source(table,connection,explicit)
    source['source'].update(creationMode=creation_mode,tableType=1)
    sid,vid=guid(),guid();prefix=f'sheets/{sid}/visuals/{vid}/'
    state=load(ASSETS/'fixtures/powertable-presentation-defaults.json')
    names=[c['columnName'] for c in columns]
    state.update(columnMeta={n:{'width':210 if n.endswith('Name') else 150} for n in names},
        manageMeasures=[{'id':n,'label':n,'measureType':'data','name':n,'order':i,'visible':True} for i,n in enumerate(names)],
        assignmentColumnMap={},superFilterAssignments=[],superFilter={},newOptionsForSelectPersisted={},
        pivotPersistProperties={},superFilterMetaConfig={'orderedFilterIds':[]},
        embeddedSuperFilter={'incomingFilterAssignments':[],'superFilterAssignments':[]},
        groupingColumn=None,sortingColumn=None)
    props={'visualType':30,'pivotAssignments':[],'superFilterAssignments':[],'visualState':state,
        'position':{'x':0,'y':0},'dimension':{'width':1,'height':1},'visualInteractions':{},'lockAspectRatio':False}
    raw={f'sheets/{sid}/sheet.json':sheet_properties(),
        prefix+'properties.json':{'$schema':schema('PowerTable/Properties'),'properties':{'schema':'0.0.1','properties':props}},
        prefix+'source.json':source,
        prefix+'columnConfigs.json':{'$schema':schema('PowerTable/ColumnConfigs'),'columnConfigs':copy.deepcopy(columns)},
        prefix+'sourceSettings.json':{'$schema':schema('PowerTable/Settings'),'sourceSettings':[
            row_access_setting(action,source['source']['recordGuid'],enabled)
            for action,enabled in [('ROW_ADD',allow_add),('ROW_UPDATE',allow_update),('ROW_DELETE',allow_delete)]]}}
    declaration={'recordGuid':sid,'displayName':name,'sheetType':'POWERTABLE','isHidden':False,
        'workloadItemEntityVisuals':[{'visualId':vid,'visualType':'POWERTABLE','isEmbedded':False}]}
    return declaration,raw,{'sheetGuid':sid,'visualGuid':vid,'sourceGuid':source['source']['recordGuid'],
        'sqlSchemaReadback':'required','rowSave':'not-tested'}

TABLE_REQUEST={'name','connection','table','catalog','creation_mode','columns','lookup_catalog',
               'allow_add','allow_update','allow_delete','forms','automations'}

def table_from_request(request):
    """Configured PowerTable parts from verified physical metadata with product defaults.

    Supply either ``table`` (physical metadata, e.g. from ``sql_definition.physical_table``)
    or ``catalog`` = ``{"schema", "table", "rows", "unique_rows"}`` holding the
    sqldb-cli results of ``PHYSICAL_METADATA_SQL`` and ``UNIQUE_METADATA_SQL``.
    ``columns`` overrides product defaults per physical column. Optional
    ``forms``/``automations`` are added as definition parts of the same visual.
    """
    from .sql_definition import catalog_table
    from .table_columns import table_column_configs
    from .powertable_features import feature_parts
    from .validate import check_powertable_parts
    if not isinstance(request,dict) or set(request)-TABLE_REQUEST:
        raise ValueError('Unsupported PowerTable table request field: '+', '.join(sorted(set(request)-TABLE_REQUEST)) if isinstance(request,dict) else 'Request object required')
    if not isinstance(request.get('name'),str) or not request['name'].strip():raise ValueError('PowerTable sheet name required')
    if ('table' in request)==('catalog' in request):raise ValueError('Supply exactly one of table or catalog')
    if 'catalog' in request:
        catalog=request['catalog']
        if not isinstance(catalog,dict) or set(catalog)!={'schema','table','rows','unique_rows'}:
            raise ValueError('catalog needs schema, table, rows and unique_rows')
        table=catalog_table(catalog['rows'],catalog['unique_rows'],schema=catalog['schema'],table=catalog['table'])
    else:table=request['table']
    columns=table_column_configs(table,request.get('columns'),lookup_catalog=request.get('lookup_catalog'))
    declaration,raw,ids=configured_table(request.get('name'),table,request.get('connection') or {},columns,explicit=True,
        creation_mode=request.get('creation_mode',2),allow_add=request.get('allow_add',True),
        allow_update=request.get('allow_update',True),allow_delete=request.get('allow_delete',False))
    prefix=f"sheets/{ids['sheetGuid']}/visuals/{ids['visualGuid']}/"
    if request.get('forms') or request.get('automations'):
        changes,summary=feature_parts(prefix,raw,forms=request.get('forms'),automations=request.get('automations'))
        raw.update(changes);ids.update(forms=summary['forms'],automations=summary['automations'])
    check_powertable_parts(raw,prefix)
    ids['columnTypes']={c['columnName']:c['columnType'] for c in columns}
    return declaration,raw,ids

def add_table_to_definition(envelope,declaration,new_parts):
    """Append one configured PowerTable sheet; every existing part keeps its bytes."""
    from .codec import parts,unpack,patch,pack,sha
    raw=unpack(envelope);root=copy.deepcopy(raw['definition.json']);sheets=root['sheets']
    if not isinstance(declaration.get('displayName'),str) or not declaration['displayName'].strip():raise ValueError('Sheet name required')
    if declaration['displayName'].strip().casefold() in {s['displayName'].casefold() for s in sheets}:
        raise ValueError('Existing sheet name; choose another name or reconcile the existing sheet')
    if declaration['recordGuid'] in {s['recordGuid'] for s in sheets} or set(new_parts)&set(raw):
        raise ValueError('Sheet identity or part collision')
    sheet=copy.deepcopy(declaration);sheet['order']=max((s.get('order',0) for s in sheets),default=-1)+1
    sheets.append(sheet)
    out=patch(envelope,{'definition.json':root},{'definition.json':sha(parts(envelope)['definition.json'])})
    out.get('definition',out)['parts'].extend(pack(new_parts)['definition']['parts'])
    after=parts(out)
    for path,payload in parts(envelope).items():
        if path!='definition.json' and after[path]!=payload:raise ValueError('Unrelated part changed: '+path)
    return out

def source_request(table,connection,explicit=False,creation_mode=2):
    if creation_mode not in (1,2):
        raise ValueError('Use supported from-scratch (1) or existing-table (2) creation mode')
    # The initialization request is not a complete exported source.json. Its
    # response must be reconciled before ALM construction; do not invent labels.
    s=powertable_source(table,connection,explicit,require_metadata=False)['source']
    return {'tableName':s['tableName'],'schema':s['schemaName'],'dbName':s['dbName'],'dbHost':s['dbHost'],
        'connectionId':s['connectionId'],'creationMode':creation_mode,'sqlTargetArtifact':s['sqlTargetArtifact']}

def existing_source(table,connection,explicit=False):
    return source_request(table,connection,explicit,2)

def compress_json(value,node=None):
    node=node or os.environ.get('FABRIC_PLAN_NODE') or os.environ.get('FABRIC_PLAN_HTTP_NODE')
    if not node:raise ValueError('Set Node path for bundled LZUTF8 encoder')
    result=subprocess.run([node,str(Path(__file__).resolve().parents[1]/'tools/encode-lzutf8.cjs')],
      input=dumps(value),text=True,encoding='utf-8',capture_output=True,timeout=30)
    if result.returncode:raise ValueError('LZUTF8 encoding failed')
    return result.stdout.strip()

def row_save(metadata,operation,records,*,conditions=None,visual_meta=None,relations=None,generated_keys=(),node=None):
    if operation not in ('insert','update'):raise ValueError('Only explicit insert/update contracts implemented')
    if not isinstance(metadata,list) or not metadata or not isinstance(records,list) or not records:raise ValueError('Metadata and records required')
    ids=[]
    for m in metadata:
        if not isinstance(m,dict) or not isinstance(m.get('id'),str) or not m['id']:raise ValueError('Column identity required')
        if set(m)-{'id','dataType','isPrimaryKey','isNullable','isEditable','isCustomColumn'}:raise ValueError('Unknown metadata field')
        for k in ('isPrimaryKey','isNullable','isEditable','isCustomColumn'):
            if k in m and not isinstance(m[k],bool):raise ValueError('Metadata Boolean')
        ids.append(m['id'])
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate metadata column')
    if any(m.get('isCustomColumn') for m in metadata) and not relations:raise ValueError('Lookup relation metadata required')
    if not isinstance(visual_meta,dict) or not {'rowIds','optionsMeta'}<=visual_meta.keys():raise ValueError('Actual visual/audit metadata required')
    row_ids=visual_meta['rowIds']
    allowed_counts={0,len(records)} if operation=='insert' else {len(records)}
    if not isinstance(row_ids,list) or len(row_ids) not in allowed_counts or any(not isinstance(x,(str,int)) or isinstance(x,bool) for x in row_ids) or len({str(x) for x in row_ids})!=len(row_ids):raise ValueError('Unique scalar row identities required; create may have an empty identity array')
    if not isinstance(visual_meta['optionsMeta'],dict):raise ValueError('Options metadata must be an object')
    def scalar(value,meta):
        if value is None:
            if meta.get('isNullable') is False:raise ValueError('Null value in nonnullable column: '+meta['id'])
            return
        if not isinstance(value,(str,int,float,bool,Decimal)):raise ValueError('Expected scalar row value')
        if isinstance(value,float) and not math.isfinite(value) or isinstance(value,Decimal) and not value.is_finite():raise ValueError('Nonfinite row value')
    if operation=='insert':
        omitted=[m['id'] for m in metadata if m.get('isPrimaryKey') and not m.get('isEditable',True)]
        if set(omitted)!=set(generated_keys):raise ValueError('Verify every omitted noneditable key is database generated')
        exported=[m for m in metadata if m['id'] not in omitted]
        for r in records:
            if not isinstance(r,list) or len(r)!=len(exported):raise ValueError('Insert row must match exported metadata order')
            for value,m in zip(r,exported):scalar(value,m)
        inner={'createData':{'records':copy.deepcopy(records),'visualMeta':copy.deepcopy(visual_meta)}}
    else:
        exported=metadata;keys={m['id'] for m in metadata if m.get('isPrimaryKey')}
        if not keys or not isinstance(conditions,list) or len(conditions)!=len(records):raise ValueError('Update key conditions required for every record')
        if not {'oldRecords','updatedColumns'}<=visual_meta.keys():raise ValueError('Update audit metadata required')
        if not isinstance(visual_meta['oldRecords'],list) or len(visual_meta['oldRecords']) not in (0,len(records)) or any(not isinstance(r,dict) for r in visual_meta['oldRecords']):raise ValueError('Old records must be empty or contain one object per update')
        changed_columns=visual_meta['updatedColumns']
        if not isinstance(changed_columns,list) or any(not isinstance(k,str) for k in changed_columns) or len(set(changed_columns))!=len(changed_columns):raise ValueError('Unique updated-column names required')
        if len({dumps(c) for c in conditions})!=len(conditions):raise ValueError('Duplicate update key conditions')
        changed=set()
        for row,condition in zip(records,conditions):
            if not isinstance(condition,dict) or set(condition)!=keys or any(v is None for v in condition.values()):raise ValueError('Complete non-null primary-key condition required')
            for key,value in condition.items():scalar(value,next(m for m in metadata if m['id']==key))
            if not isinstance(row,dict) or not row or not set(row)<=set(ids) or set(row)&keys:raise ValueError('Update record names/keys')
            if any(not next(m for m in metadata if m['id']==k).get('isEditable',True) for k in row):raise ValueError('Noneditable column update')
            for key,value in row.items():scalar(value,next(m for m in metadata if m['id']==key))
            changed|=set(row)
        if set(visual_meta['updatedColumns'])!=changed:raise ValueError('Updated-column metadata differs from records')
        inner={'updateData':{'records':copy.deepcopy(records),'conditions':copy.deepcopy(conditions),'visualMeta':copy.deepcopy(visual_meta)}}
    return {'data':compress_json(inner,node),'metaData':copy.deepcopy(exported),'relations':copy.deepcopy(relations or {}),
        'incomingRowCount':len(records),'actions':[operation],'scdConfig':None}
