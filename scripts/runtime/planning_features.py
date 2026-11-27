"""Planning writeback, inserted rows, scenarios and row templates as definition parts.

These optional parts sit in a Planning visual folder beside ``dataInput.json``
and ``properties.json``. Each constructor adds new records to a fresh export and
keeps every other part byte for byte. Saving a part configures behavior only:
it runs no writeback and moves no value.

Product values have no defaults: each request states the writeback layout, the
scenario status and first order, and every template-row flag.
"""
import copy
from .construct import schema
from .codec import parts,unpack,scoped_candidate
from .identity import new_native_id

WRITEBACK_TYPES={'PIVOT_LONG':2,'PIVOT_WIDE':3,'DELTA_ONLY':4,'DELTA_WIDE':5}
ROW_TYPES=('StaticRow','CalculatedRow')
AGGREGATIONS=('Sum','Average','Min','Max','Count')
SCENARIO_STATUSES=('ACTIVE','LOCK')
TEMPLATE_ROW_FLAGS=('include_in_total','disabled','distribute_parent_value_to_child','default_value','row_edit_mode')
WRITEBACK_REQUEST={'writeback_type','destinations','column_mapping','excluded_measures','skipped_dimensions','number_precision'}
ROW_REQUEST={'name','dimension_id','row_type','formula','description','include_in_total','column_aggregation'}
SCENARIO_REQUEST={'name','measure_ids','status','order'}
TEMPLATE_REQUEST={'title','rows','no_row_id'}
TEMPLATE_ROW_REQUEST={'title',*TEMPLATE_ROW_FLAGS}

def _native(taken):
    """A new decimal u64 ID, the form exported row and scenario IDs take; it joins ``taken``."""
    value=new_native_id(taken);taken.add(value);return value

def _given(value,key):
    return isinstance(value.get(key),str) and bool(value[key].strip())

def destination_form(value):
    """The connection member of one destination in the form Fabric exports; nothing is filled in.

    An exported destination has tableName, a settings object and connectionId or
    connectionIdVariable. A destination without settings (the article's
    connectionId/databaseId form) fails import on Fabric SQL-backed Plans, and the
    import never reads the schema's portable ``connection``.
    """
    if isinstance(value,dict) and _given(value,'tableName') and isinstance(value.get('settings'),dict):
        for key in ('connectionId','connectionIdVariable'):
            if _given(value,key):return key
    raise ValueError('Supply each writeback destination as Fabric exports it: tableName, a settings object, and '
                     'connectionId or connectionIdVariable. A destination without settings fails import on Fabric '
                     'SQL-backed Plans, and the import ignores a portable connection. Nothing is computed here.')

def _distinct(values,label):
    if not isinstance(values,list) or not values or any(not isinstance(v,str) for v in values) or len(set(values))!=len(values):
        raise ValueError(label+' must list distinct IDs')
    return values

def writeback_config(writeback_type=None,destinations=None,*,columns,dimensions,column_mapping=None,
                     excluded_measures=None,skipped_dimensions=None,number_precision=None):
    """One writeback.json: layout, destinations copied as given and measure-to-column mapping.

    ``column_mapping`` maps a measure GUID of this visual to its writeback column
    name. A destination is never completed or hashed here; copy it from a fresh
    export of a writeback already configured for the same target.
    """
    from .validate import Schemas,Invalid
    if writeback_type is None:raise ValueError('writeback_type required; layouts have no default')
    if not isinstance(writeback_type,str) or writeback_type not in WRITEBACK_TYPES:
        raise ValueError('writeback_type must be PIVOT_LONG, PIVOT_WIDE, DELTA_ONLY or DELTA_WIDE')
    if not isinstance(destinations,list) or not destinations:raise ValueError('At least one complete writeback destination is required')
    for d in destinations:destination_form(d)
    by_id={c.get('measureGuid'):c for c in columns if isinstance(c,dict)}
    def measure(mid):
        if not isinstance(mid,str) or mid not in by_id:raise ValueError('Writeback reference is not a measure of this visual: '+str(mid))
        return mid
    part={'$schema':schema('Planning/Writeback'),'writebackType':WRITEBACK_TYPES[writeback_type],'destinations':copy.deepcopy(destinations)}
    if column_mapping is not None:
        if not isinstance(column_mapping,dict) or not column_mapping:raise ValueError('column_mapping must map measure GUIDs to writeback column names')
        if any(not isinstance(n,str) or not n.strip() for n in column_mapping.values()):raise ValueError('Writeback column names must be non-empty text')
        if len({n.strip().casefold() for n in column_mapping.values()})!=len(column_mapping):raise ValueError('Writeback column names must be unique')
        part['wbTableColumnMapping']={measure(mid):{'visualName':by_id[mid]['name'],'wbColumnName':name} for mid,name in column_mapping.items()}
    if excluded_measures is not None:
        part['excludedMeasureGuids']=[measure(m) for m in _distinct(excluded_measures,'excluded_measures')]
        if set(part['excludedMeasureGuids'])&set(column_mapping or {}):raise ValueError('A measure cannot be both mapped and excluded')
    if skipped_dimensions is not None:
        for dimension in _distinct(skipped_dimensions,'skipped_dimensions'):
            if dimension not in dimensions:raise ValueError('Skipped dimension is not a dimension of this visual: '+dimension)
        part['skippedDimensionIds']=list(skipped_dimensions)
    if number_precision is not None:
        if isinstance(number_precision,bool) or not isinstance(number_precision,int) or number_precision<0:
            raise ValueError('number_precision must be a nonnegative integer')
        part['numberPrecision']={'decimal':number_precision}
    checker=Schemas();url=part['$schema']
    checker.check({k:v for k,v in part.items() if k!='destinations'},url)
    for destination in destinations:
        # Exports can omit settingsHash and carry connectionIdVariable instead of connectionId, and
        # the import accepts both; only those two schema-required members are relaxed here.
        view=copy.deepcopy(destination)
        if not _given(view,'settingsHash'):view['settingsHash']='not-exported'
        if not _given(view,'connectionId'):view['connectionId']='00000000-0000-4000-8000-000000000000'
        try:checker.check({'$schema':url,'writebackType':part['writebackType'],'destinations':[view]},url)
        except Invalid as e:raise ValueError('Writeback destination does not match the published Writeback schema: '+str(e))
    return part

def inserted_row(name=None,dimension_id=None,row_type=None,*,visual_id,row_dimensions,taken,formula=None,description=None,
                 include_in_total=None,column_aggregation=None):
    """One insertRows.json record: a StaticRow or CalculatedRow on a row dimension of the visual.

    The row is not positioned; the product places it. Only the optional members
    the request states are written.
    """
    if not isinstance(name,str) or not name.strip():raise ValueError('Inserted row name must be non-empty text')
    if not isinstance(dimension_id,str) or dimension_id not in row_dimensions:
        raise ValueError('Inserted row dimension_id is not a row dimension of this visual: '+str(dimension_id))
    if row_type not in ROW_TYPES:
        raise ValueError('row_type must be StaticRow or CalculatedRow; ForecastRow and PercentContributionRow have no '
                         'documented fields, so copy those rows from an export')
    config={}
    if row_type=='CalculatedRow':
        if not isinstance(formula,str) or not formula.strip():raise ValueError('A CalculatedRow needs a non-empty formula')
        config['formula']=formula
        if description is not None:
            if not isinstance(description,str):raise ValueError('Calculated row description must be text')
            config['description']=description
    elif formula is not None or description is not None:raise ValueError('formula and description apply only to a CalculatedRow')
    row_id=_native(taken);name=name.strip()
    meta={'id':row_id,'row_type':{row_type:config},'title':name}
    if include_in_total is not None:
        if not isinstance(include_in_total,bool):raise ValueError('include_in_total must be Boolean')
        meta['include_in_total']=include_in_total
    if column_aggregation is not None:
        if column_aggregation not in AGGREGATIONS:raise ValueError('column_aggregation must be Sum, Average, Min, Max or Count')
        meta['column_aggregation']=column_aggregation
    return {'id':row_id,'visualId':visual_id,'name':name,'dimensionId':dimension_id,'rowMeta':meta}

def request_items(items,label,allowed):
    """A request's non-empty list of objects, each using only the allowed fields."""
    if not isinstance(items,list) or not items or any(not isinstance(i,dict) for i in items):
        raise ValueError(label+' entries must be a non-empty list of objects')
    for spec in items:
        if set(spec)-allowed:raise ValueError('Unsupported '+label+' field: '+', '.join(sorted(set(spec)-allowed)))
    return items

def _insert_rows(raw,path,items,visual_id,row_dimensions):
    from .validate import Schemas
    request_items(items,'inserted-row',ROW_REQUEST)
    current=copy.deepcopy(raw.get(path) or {'$schema':schema('Planning/InsertRows'),'rows':[]})
    rows=current.get('rows')
    if not isinstance(rows,list):raise ValueError('Existing insertRows.json has no rows list')
    taken={str(v) for r in rows if isinstance(r,dict) for v in (r.get('id'),(r.get('rowMeta') or {}).get('id')) if v is not None}
    names={(r.get('dimensionId'),str(r.get('name','')).strip().casefold()) for r in rows if isinstance(r,dict)}
    new=[]
    for spec in items:
        record=inserted_row(visual_id=visual_id,row_dimensions=row_dimensions,taken=taken,**spec)
        key=(record['dimensionId'],record['name'].casefold())
        if key in names:raise ValueError('This dimension already has an inserted row named '+record['name'])
        names.add(key);new.append(record)
    Schemas().check({'$schema':schema('Planning/InsertRows'),'rows':new},schema('Planning/InsertRows'))
    rows.extend(new)
    return current,[r['name'] for r in new]

def scenario_record(name=None,measure_ids=None,status=None,*,order,measures,taken):
    """One scenarios.json record: name, status, order and the visual measures it covers.

    Simulations, dimension hashes and auto-writeback flags are not generated.
    """
    if not isinstance(name,str) or not name.strip():raise ValueError('Scenario name must be non-empty text')
    if status is None:raise ValueError('Scenario status required; it has no default')
    if status not in SCENARIO_STATUSES:raise ValueError('Scenario status must be ACTIVE or LOCK')
    if (not isinstance(measure_ids,list) or not measure_ids or any(not isinstance(m,str) for m in measure_ids)
            or len(set(measure_ids))!=len(measure_ids)):
        raise ValueError('Scenario measure_ids must list distinct measure GUIDs')
    for mid in measure_ids:
        if mid not in measures:raise ValueError('Scenario measure is not a measure of this visual: '+mid)
    return {'name':name.strip(),'status':status,'meta':{'measureIds':list(measure_ids),'scenarioGuid':_native(taken),'order':order}}

def _scenarios(raw,path,items,measures):
    request_items(items,'scenario',SCENARIO_REQUEST)
    current=copy.deepcopy(raw.get(path) or {'$schema':schema('planning/scenarios'),'scenarios':[]})
    records=current.get('scenarios')
    if not isinstance(records,list):raise ValueError('Existing scenarios.json has no scenarios list')
    metas=[s.get('meta') if isinstance(s,dict) and isinstance(s.get('meta'),dict) else {} for s in records]
    taken={str(m['scenarioGuid']) for m in metas if 'scenarioGuid' in m}
    orders={m['order'] for m in metas if isinstance(m.get('order'),int) and not isinstance(m.get('order'),bool)}
    names={str(s.get('name','')).strip().casefold() for s in records if isinstance(s,dict)}
    new=[]
    for spec in items:
        spec=dict(spec);order=spec.pop('order',None)
        if order is None:
            if not orders:raise ValueError('Scenario order required for the first scenario; later ones follow the highest order')
            order=max(orders)+1
        if isinstance(order,bool) or not isinstance(order,int) or order<0:raise ValueError('Scenario order must be a nonnegative integer')
        if order in orders:raise ValueError('Scenario order '+str(order)+' is taken')
        record=scenario_record(order=order,measures=measures,taken=taken,**spec)
        if record['name'].casefold() in names:raise ValueError('A scenario with this name already exists: '+record['name'])
        names.add(record['name'].casefold());orders.add(order);new.append(record)
    records.extend(new)
    return current,[s['name'] for s in new]

def row_template(title=None,rows=None,no_row_id=None,*,taken):
    """One dynamicRowTemplates entry: flat static rows in order, each at level 0.

    Every row states the five flags the schema requires. ``no_row_id`` is the
    text written for a missing parent or previous row; no source documents it,
    so the request states it.
    """
    if not isinstance(title,str) or not title.strip():raise ValueError('Row template title must be non-empty text')
    if no_row_id is None:raise ValueError('no_row_id required: the parent_id of a top-level row and the previous_row_id of the '
                                          'first row are undocumented and have no default')
    if not isinstance(no_row_id,str):raise ValueError('no_row_id must be text')
    request_items(rows,'template-row',TEMPLATE_ROW_REQUEST)
    template={'id':_native(taken),'title':title.strip(),'rows':[]};titles=set();previous=no_row_id
    for values in rows:
        label=values.get('title')
        if not isinstance(label,str) or not label.strip():raise ValueError('Template row title must be non-empty text')
        missing=[key for key in TEMPLATE_ROW_FLAGS if key not in values]
        if missing:raise ValueError('Template row '+label+' needs '+', '.join(missing)+'; template-row flags have no default')
        if label.strip().casefold() in titles:raise ValueError('Duplicate template row title: '+label)
        for key in ('include_in_total','disabled','distribute_parent_value_to_child'):
            if not isinstance(values[key],bool):raise ValueError('Template row '+key+' must be Boolean')
        if not isinstance(values['default_value'],str):raise ValueError('Template row default_value must be text (the Static value)')
        if values['row_edit_mode'] is not None and not isinstance(values['row_edit_mode'],str):
            raise ValueError('Template row row_edit_mode must be text or null')
        row_id=_native(taken)
        template['rows'].append({'id':row_id,'row_type':{'StaticRow':{
            'distribute_parent_value_to_child':values['distribute_parent_value_to_child'],
            'default_value':{'Static':values['default_value']},'row_edit_mode':values['row_edit_mode']}},
            'title':label.strip(),'include_in_total':values['include_in_total'],'parent_id':no_row_id,'level':0,
            'previous_row_id':previous,'disabled':values['disabled']})
        titles.add(label.strip().casefold());previous=row_id
    return template

def _row_templates(raw,path,items):
    request_items(items,'row-template',TEMPLATE_REQUEST)
    current=copy.deepcopy(raw.get(path) or {'$schema':schema('Planning/ModelTemplate'),'properties':{'dynamicRowTemplates':[]}})
    props=current.get('properties')
    templates=props.get('dynamicRowTemplates') if isinstance(props,dict) else None
    if not isinstance(templates,list):raise ValueError('Existing modelTemplate.json has no properties.dynamicRowTemplates list')
    taken={str(v) for t in templates if isinstance(t,dict)
           for v in [t.get('id')]+[r.get('id') for r in t.get('rows') or [] if isinstance(r,dict)] if v is not None}
    titles={str(t.get('title','')).strip().casefold() for t in templates if isinstance(t,dict)}
    new=[]
    for spec in items:
        template=row_template(taken=taken,**spec)
        if template['title'].casefold() in titles:raise ValueError('A row template with this title already exists: '+template['title'])
        titles.add(template['title'].casefold());new.append(template)
    templates.extend(new)
    return current,[t['title'] for t in new]

def planning_prefix(raw,sheet_guid,visual_id=None):
    """Folder of the one Planning visual a sheet owns directly."""
    owned=[v for s in raw['definition.json'].get('sheets',[]) if s.get('recordGuid')==sheet_guid
           for v in s.get('workloadItemEntityVisuals') or [] if v.get('visualType')=='PLANNING' and not v.get('isEmbedded',False)
           and visual_id in (None,v.get('visualId'))]
    if len(owned)!=1:raise ValueError('Select a sheet GUID that directly owns one Planning visual; pass visual_id when it owns several')
    prefix=f"sheets/{sheet_guid}/visuals/{owned[0]['visualId']}/"
    for leaf in ('dataInput.json','properties.json'):
        if prefix+leaf not in raw:raise ValueError('Planning visual part missing: '+leaf)
    return prefix,owned[0]['visualId']

def _dimensions(raw,prefix,axes=('rowDimensions','columnDimensions')):
    props=raw[prefix+'properties.json'].get('properties')
    state=props.get('visualState') if isinstance(props,dict) else None
    if not isinstance(state,dict):return set()
    return {d['id'] for key in axes for d in state.get(key) or [] if isinstance(d,dict) and isinstance(d.get('id'),str)}

def add_planning_features(envelope,*,sheet_guid,visual_id=None,writeback=None,insert_rows=None,scenarios=None,row_templates=None):
    """Scoped candidate adding Planning feature parts; every other part keeps its bytes."""
    from .validate import schema_report
    raw=unpack(envelope);prefix,vid=planning_prefix(raw,sheet_guid,visual_id)
    columns=raw[prefix+'dataInput.json'].get('columns')
    if not isinstance(columns,list):raise ValueError('Planning dataInput.json has no columns list')
    dimensions=_dimensions(raw,prefix);changes={};summary={}
    if writeback is not None:
        path=prefix+'writeback.json'
        if path in raw:raise ValueError('writeback.json already exists; change the exported part instead of rebuilding it. '
                                        'Fabric exports writeback.json for every Planning visual, so this constructor applies '
                                        'only to a definition without one, such as a newly built Planning sheet.')
        if not isinstance(writeback,dict) or set(writeback)-WRITEBACK_REQUEST:
            raise ValueError('Unsupported writeback field: '+(', '.join(sorted(set(writeback)-WRITEBACK_REQUEST)) if isinstance(writeback,dict) else 'object required'))
        changes[path]=writeback_config(columns=columns,dimensions=dimensions,**writeback)
        summary['writeback']={'writebackType':{v:k for k,v in WRITEBACK_TYPES.items()}[changes[path]['writebackType']],
                              'connections':[destination_form(d) for d in changes[path]['destinations']]}
    if insert_rows is not None:
        path=prefix+'insertRows.json'
        changes[path],summary['insertedRows']=_insert_rows(raw,path,insert_rows,vid,_dimensions(raw,prefix,('rowDimensions',)))
    if scenarios is not None:
        path=prefix+'scenarios.json'
        measures={c.get('measureGuid') for c in columns if isinstance(c,dict)}
        changes[path],summary['scenarios']=_scenarios(raw,path,scenarios,measures)
    if row_templates is not None:
        path=prefix+'modelTemplate.json'
        changes[path],summary['rowTemplates']=_row_templates(raw,path,row_templates)
    if not changes:raise ValueError('Request at least one of writeback, insert_rows, scenarios or row_templates')
    candidate,changed,added=scoped_candidate(envelope,changes)
    report={item['path']:item['status'] for item in schema_report(changes)}
    warnings=[]
    if report.get(prefix+'writeback.json')=='schema-conflict':
        warnings.append('writeback.json keeps destinations as Fabric exports them. The pinned Writeback schema also requires '
                        'settingsHash and connectionId, which exports can omit; Fabric\'s import accepts the exported form.')
    if writeback is not None and any('database' not in d['settings'] for d in changes[prefix+'writeback.json']['destinations']):
        warnings.append('On Fabric SQL-backed Plans the import keeps a destination tableName only when settings.database is set; '
                        'otherwise it keeps the existing table name or creates one.')
    if scenarios is not None:
        warnings.append('The current Fabric Plan import neither reads nor exports scenarios.json, so these scenarios have no '
                        'effect after publishing; create scenarios in the product.')
    warnings+=[path+' declares a $schema with no pinned copy in this package, so the schema report cannot check the whole part'
               for path,state in sorted(report.items()) if state=='schema-gap']
    return candidate,{'sheetGuid':sheet_guid,'visualId':vid,**summary,'changedParts':changed,'addedParts':added,
        'preservedPartCount':len(parts(envelope))-len(changed),'publicSchema':report,'warnings':warnings,
        'deployment':'not run','runtimeValidation':'not run'}
