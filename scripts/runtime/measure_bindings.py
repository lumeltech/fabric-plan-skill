"""Source-aware measure construction from exact current catalog identities.

Labels are presentation only. A Native Planning companion is not a From Sheets
output. These functions construct assignments; they do not query values or render.
"""
import copy
from .construct import field
from .identity import Registry
from .semantic_values import semantic_value
from .identity import native_id

NUMERIC={'Double','Decimal','Int64'}

def record_kind(record):
    meta=record['columnMeta'];kind=meta['measure_type']
    if str(meta['id'])!=str(record['measureGuid']):
        raise ValueError('Column metadata and registered measure identities disagree')
    if 'VisualColumn' in kind:kind=kind['VisualColumn']
    if len(kind)!=1:raise ValueError('Resolve the actual native measure type')
    return next(iter(kind))

def sheet_column_id(record):
    """External From Sheets key from a fresh, owner-scoped native catalog.

    Fabric SQL records expose a row id. OneLake records omit it; a record migrated
    from Fabric SQL keeps that key as sqlPk, and a native OneLake record uses its
    measureGuid. Never fabricate a SQL key or mutate the source record.
    An explicitly malformed id is an error, not a backend fallback signal.
    """
    record_kind(record)
    mid=native_id(record['measureGuid'])
    value=record.get('id')
    if value is None:value=record.get('sqlPk')
    if value is None:return mid
    if isinstance(value,bool) or not isinstance(value,(str,int)):
        raise ValueError('Invalid explicit source column identity')
    return native_id(str(value))

def check_record_owner(record,visual_id):
    # OneLake owner-scoped column responses can omit visualId. The caller must
    # obtain the record from that owner's catalog; a present id must agree.
    if record.get('visualId') is not None and str(record['visualId'])!=str(visual_id):
        raise ValueError('Source visual, column record and source measureGuid must agree')

def semantic_measure(model,field_id,bucket='AC',order=0,label=None,aggregation=None):
    a=semantic_value(model,field_id,Registry(),bucket=bucket,order=order,label=label,aggregation=aggregation)
    if label is not None:a.update(customName=label,name=label,isRenamed=label!=a['columnName'])
    return a

def resolve_measure(request,*,model=None,sheets=(),queries=()):
    """Explicit source namespace plus exact field/column/output IDs required.

    PowerBI: fieldId. Visual: visualId, sourceMeasureGuid, optional columnId plus the current
    owner catalog. InfoBridge: queryId, outputId, assignment from current metadata.
    Each returned binding has a source-specific ID and internal measureGuid.
    """
    source=request['sourceType'];bucket=request.get('bucket','AC');order=request.get('order',0)
    if bucket not in ('AC','PY','ameasure'):raise ValueError('Unsupported destination measure bucket')
    if source=='PowerBI':
        return semantic_measure(model,request['fieldId'],bucket,order,request.get('label'),request.get('aggregation'))
    if source=='Visual':
        owners=[s for s in sheets if str(s['visualId'])==str(request['visualId'])]
        if len(owners)!=1:raise ValueError('Missing/ambiguous current source visual')
        owner=owners[0]
        matches=[c for c in owner['columns'] if (sheet_column_id(c)==str(request['columnId'])
            if 'columnId' in request else c['measureGuid']==request['sourceMeasureGuid'])]
        if len(matches)!=1:raise ValueError('Source column is absent or ambiguous in this visual')
        c=matches[0]
        check_record_owner(c,owner['visualId'])
        if c['measureGuid']!=request['sourceMeasureGuid']:
            raise ValueError('Source visual, column record and source measureGuid must agree')
        if record_kind(c) not in ('DataInput','Formula','Forecast'):
            raise ValueError('Not a local sheet output; retain its original PowerBI/InfoBridge/Visual source')
        managed=owner['properties']['visualState']['manage_measures']
        if len([m for m in managed if m['id']==c['measureGuid']])!=1:
            raise ValueError('Source measure is not registered exactly once in visual state')
        from .forecast_review import from_sheet_assignment
        return from_sheet_assignment(c,owner['visualId'],owner['name'],request.get('label'),bucket,order)
    if source=='InfoBridge':
        from .consumer_bindings import output_catalog,resolve_assignment,find_query
        query=find_query(queries,request['queryId'])
        outputs=[f for f in output_catalog(query) if f['outputId']==request['outputId']]
        if len(outputs)!=1:raise ValueError('Missing/ambiguous selected query output')
        a=resolve_assignment(request['assignment'],query,expected_output_id=request['outputId'])
        if a.get('dataRoleType')!='Measure' or a.get('dataType') not in NUMERIC:
            raise ValueError('Use the typed numeric query output assignment')
        from .bridge import field_family
        output=outputs[0]
        if output.get('dataType') in NUMERIC:
            if a['dataType']!=output['dataType']:raise ValueError('Assignment data type differs from current query output')
        elif field_family({'type':output.get('nativeType'),'dataType':output.get('dataType'),'name':output['columnName']})!='number':
            raise ValueError('The actual query output is not numeric')
        a.update(bucketId=bucket,order=order)
        if request.get('label') is not None:a.update(name=request['label'],customName=request['label'])
        return a
    raise ValueError('Explicit PowerBI, Visual or InfoBridge source required')

def registered_measure(properties,record,visual_id,sheet_name,*,model,bucket='AC',queries=(),sheets=()):
    """Resolve a selected registered measure by origin, never by its display name."""
    kind=record_kind(record)
    check_record_owner(record,visual_id)
    assignments=[a for a in properties.get('pivotAssignments',[]) if a.get('measureGuid')==record['measureGuid']]
    if kind!='Native':
        owner={'name':sheet_name,'visualId':str(visual_id),'columns':[record],'properties':properties}
        return resolve_measure({'sourceType':'Visual','visualId':str(visual_id),'columnId':sheet_column_id(record),
            'sourceMeasureGuid':record['measureGuid'],'bucket':bucket},model=model,sheets=[owner])
    if len(assignments)!=1:raise ValueError('Native companion needs its exact upstream pivot assignment')
    a=assignments[0];origin=a['sourceType']
    if origin=='PowerBI':
        if a.get('columnType')=='Column' and not a.get('aggregationType'):
            raise ValueError('Resolve the persisted source column aggregation before reuse')
        out=semantic_measure(model,a['id'],bucket,label=a.get('customName') or a.get('name'),aggregation=a.get('aggregationType'))
        fields=('id','sourceId','sourceType','columnType','columnName','tableName','dataType')
        if a.get('columnType')=='Measure':fields+=('measureGuid',)
        for key in fields:
            if a.get(key)!=out.get(key):raise ValueError('Semantic assignment/catalog mismatch: '+key)
        if a.get('columnType')=='Column':
            # UI aggregation changes can retain the registered measureGuid. The
            # current owner record is authoritative, not a newly computed hash.
            out['measureGuid']=native_id(a['measureGuid'])
        return out
    if origin=='InfoBridge':
        from .consumer_bindings import output_catalog,find_query,assert_resolved
        query=find_query(queries,a['queryId'])
        assert_resolved(a,query,check_measure_guid=False)
        fs=[f for f in output_catalog(query) if f['id']==a['id']]
        if len(fs)!=1:raise ValueError('Source field missing from current query outputs')
        out=resolve_measure({'sourceType':'InfoBridge','queryId':a['queryId'],'outputId':fs[0]['outputId'],
            'assignment':a,'bucket':bucket},queries=queries)
        # Reuse an existing registered companion without breaking its formulas.
        out['measureGuid']=native_id(a['measureGuid'])
        return out
    if origin=='Visual':
        owners=[s for s in sheets if str(s['visualId'])==str(a['visualId'])]
        if len(owners)!=1:raise ValueError('Resolve the original sheet output before relaying a linked companion')
        cs=[c for c in owners[0]['columns'] if sheet_column_id(c)==str(a['id'])]
        if len(cs)!=1:raise ValueError('Original source column missing')
        return resolve_measure({'sourceType':'Visual','visualId':a['visualId'],'columnId':a['id'],
            'sourceMeasureGuid':cs[0]['measureGuid'],'bucket':bucket,'label':a.get('customName') or a.get('name')},sheets=sheets)
    raise ValueError('Unsupported registered source; do not substitute a sheet link')
