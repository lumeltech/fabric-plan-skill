"""Resolve current query output identities, never input-record primary keys.

Fabric SQL sqlPk or OneLake's current query id qualifies output field ids.
Output ids are lossless strings (u64 or generated ids).
"""
import copy
from .identity import xxh3,product_aggregation

def binding_query_id(query):
    """Use the actual registry domain; never invent a numeric OneLake key."""
    qid=query.get('id')
    if not isinstance(qid,str) or not qid or any(c in qid for c in '[]\r\n'):
        raise ValueError('Current query registry identity required')
    pk=query.get('sqlPk')
    if pk is None:return qid
    if isinstance(pk,bool) or not str(pk).isdecimal():
        raise ValueError('Invalid explicit SQL query identity')
    return str(pk)

def find_query(queries,query_id):
    """Resolve the exact current registry or binding id in either storage mode."""
    matches=[q for q in queries if str(query_id) in (q['id'],binding_query_id(q))]
    if len(matches)!=1:raise ValueError('Resolve one current query, not a source-record ID')
    return matches[0]

def output_catalog(query):
    qid=query['id']; native=binding_query_id(query);meta=query['meta']
    if not query.get('sourceId'):
        raise ValueError('Current query registry identities required')
    fields=[];seen=set()
    for role in ('dimensions','columns','measures'):
        selected='selected'+role[0].upper()+role[1:]
        # A saved post-transform selection can differ from source/base metadata.
        # Preserve an explicit empty selection; never fall back by truthiness.
        for f in meta[selected] if selected in meta else meta.get(role,[]):
            fid=f['id']
            if not isinstance(fid,str) or not fid or fid in seen:
                raise ValueError('Ambiguous/non-string output identity')
            seen.add(fid);key=native+'['+fid+']'
            fields.append({'id':key,'sourceId':key,'queryId':native,'queryGuid':qid,
                'sourceGuid':query['sourceId'],'outputId':fid,'columnName':f.get('alias') or f['name'],
                'tableName':query['name'],'role':role,'nativeType':f.get('type'),
                'dataType':f.get('dataType')})
    return fields

def resolve_assignment(assignment,query,*,expected_output_id):
    """Caller proves the expected output id using the current query + lineage.

    A name only match, input row id, or output ordinal is not accepted.
    This returns a NEW consumer. Existing Planning formulas require an explicit
    internal-id migration before changing their measureGuid; see repair guide.
    """
    a=copy.deepcopy(assignment)
    if a.get('sourceType')!='InfoBridge':raise ValueError('InfoBridge assignment required')
    if str(a.get('queryId')) not in (query['id'],binding_query_id(query)):
        raise ValueError('Assignment belongs to a different query')
    matches=[f for f in output_catalog(query) if f['outputId']==expected_output_id]
    if len(matches)!=1:raise ValueError('Expected field missing from query output')
    f=matches[0]
    if a.get('columnName')!=f['columnName'] or a.get('tableName')!=f['tableName']:
        raise ValueError('Output identity conflicts with intended column/query')
    a.update(id=f['id'],sourceId=f['id'],queryId=f['queryId'])
    # The proven native UI assignment has no source-record override. The query
    # registry supplies source ownership; do not force a source into queryId.
    a.pop('infoBridgeSourceId',None);a.pop('infoBridgeSourceGuid',None)
    aggregation=product_aggregation(a.get('aggregationType'))
    if a.get('columnType')!='Measure' and aggregation not in ('sum','minimum','maximum','count','average'):
        raise ValueError('Explicit aggregation required')
    if a.get('columnType')!='Measure':a['aggregationType']=aggregation
    key=f['id'] if a['columnType']=='Measure' else aggregation.upper()+'__'+f['id']
    a['measureGuid']=str(xxh3(key))
    return a

def numeric_output_fields(query,*,storage_context=None):
    """Typed additive Values from current selected output metadata."""
    out=[]
    for f in output_catalog(query):
        if f['role']!='measures':continue
        typ=str(f.get('nativeType','')).upper()
        if typ in ('INTEGER','INT','BIGINT','SMALLINT','TINYINT'):dt='Int64'
        elif typ in ('DOUBLE','FLOAT','REAL'):dt='Double'
        elif typ.startswith(('DECIMAL','NUMERIC')):dt='Decimal'
        else:raise ValueError('Resolve numeric output type: '+f['columnName'])
        f.update(sourceType='InfoBridge',columnType='Column',dataType=dt,aggregationType='sum')
        f['measureGuid']=str(xxh3('SUM__'+f['id']))
        if storage_context is not None:
            if storage_context.get('queryId')!=binding_query_id(query):raise ValueError('Storage-context evidence belongs to a different query')
            f['storageContext']=copy.deepcopy(storage_context)
        out.append(f)
    return out

def assert_resolved(assignment,query,*,check_measure_guid=True):
    f=[f for f in output_catalog(query) if f['id']==assignment.get('id')]
    if len(f)!=1:raise ValueError('Consumer is absent from current output catalog')
    expected=resolve_assignment(assignment,query,expected_output_id=f[0]['outputId'])
    keys=['id','sourceId','queryId','columnName','tableName','sourceType']
    if check_measure_guid:keys.append('measureGuid')
    if any(assignment.get(k)!=expected.get(k) for k in keys):raise ValueError('Consumer catalog mismatch')
    return {'binding':'matched-current-query-output','queryStatus':query.get('status'),
            'rendering':'not-tested','dataPropagation':'not-tested'}

def audit_visual_consumers(props,queries):
    """Check chart/Planning references against current metadata, including filters.

    queries is keyed by binding_query_id (SQL sqlPk or OneLake id). Existing internal measureGuid
    aliases remain intact; this verifies external identity, not formula execution.
    """
    assignments=list(props.get('pivotAssignments',[]))
    for reg in props.get('superFilterAssignments',[]):
        assignments.extend(reg.get('pivotAssignments',[]))
    checks=[]
    for a in assignments:
        if a.get('sourceType')!='InfoBridge':continue
        query=queries.get(str(a.get('queryId')))
        if query is None:raise ValueError('Current query metadata missing for consumer')
        checks.append(assert_resolved(a,query,check_measure_guid=False))
    if props.get('visualType')==50:
        from .chart_filters import audit_chart_filters
        audit_chart_filters(props)
    return {'infoBridgeReferences':len(checks),'catalogChecks':checks,
            'rendering':'not-tested','dataPropagation':'not-tested'}

def restore_import_bindings(current,intended,queries):
    """Repair only observed import identity drift using this deployment's intent.

    intended is the same item's pre-publication native properties or a resolved
    current-run construction manifest, never an unrelated old report. Fresh query
    metadata must prove every intended output. The caller still uses current ETags.
    Other property differences require reconciliation, not blind replacement.
    """
    audit_visual_consumers(intended,queries)
    allowed=set()
    def register(assignments,prefix):
        for i,a in enumerate(assignments):
            if a.get('sourceType')=='InfoBridge':
                allowed.update(prefix+(i,k) for k in ('id','sourceId'))
    register(intended.get('pivotAssignments',[]),('pivotAssignments',))
    for i,reg in enumerate(intended.get('superFilterAssignments',[])):
        nested=reg.get('pivotAssignments',[])
        register(nested,('superFilterAssignments',i,'pivotAssignments'))
        valid={a['id'] for a in nested if a.get('sourceType')=='InfoBridge'}
        for j,s in enumerate(reg.get('configuration',{}).get('sort',[])):
            if s.get('id') in valid and s.get('columnId')==s['id']:
                allowed.update(('superFilterAssignments',i,'configuration','sort',j,k) for k in ('id','columnId'))
    changes=[]
    def compare(a,b,path=()):
        if type(a)!=type(b):raise ValueError('Unexpected property type drift')
        if isinstance(a,dict):
            if a.keys()!=b.keys():raise ValueError('Unexpected property membership drift')
            for k in a:compare(a[k],b[k],path+(k,))
        elif isinstance(a,list):
            if len(a)!=len(b):raise ValueError('Unexpected property list drift')
            for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+(i,))
        elif a!=b:
            if path not in allowed:raise ValueError('Non-identity change requires reconciliation: '+str(path))
            changes.append({'path':list(path),'from':a,'to':b})
    compare(current,intended)
    return copy.deepcopy(intended),changes
