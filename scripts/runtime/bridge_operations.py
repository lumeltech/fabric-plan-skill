"""InfoBridge operation-specific construction, learned from video + fresh API reads.

Pure constructors: no old report, network, file upload, refresh or database mutation.
Output catalogs/IDs are supplied explicitly, then reconciled with destination readback.
Portable source type names are NOT native source enums or transformation step codes.
"""
import copy,re
from .construct import guid
from .bridge import Query,GROUPS,catalog_meta,field_family,append_check

TOKEN=re.compile(r'\{\{query_id:([^}]+)\}\}')
DERIVED={'APPEND':(140,'Append Query'),'MERGE':(150,'Merge Query'),'JOIN':(230,'Join Query'),'SQL_SOURCE':(10,'Query from SQL')}

def name(f):return f.get('alias') or f['name']
def selected_catalog(query):
    return {g:copy.deepcopy(query['meta'].get(k,[])) for g,k in GROUPS.items()}
def projected_signature(query,*,measures=False):
    groups=('dimensions','columns')+ (('measures',) if measures else ())
    return [(g,name(f),field_family(f)) for g in groups for f in query['meta'].get(GROUPS[g],[])]
def append_compatibility(inputs,*,allow_measure_union=False):
    """General Append contract. Financial contributions use stricter append_check.

    A union of optional measures is an observed export shape, not permission to treat missing
    financial contributions as zero. Return missing-measure names for explicit policy.
    """
    if len(inputs)<2:raise ValueError('Append needs at least two queries')
    expected=projected_signature(inputs[0]);measure_types={};missing={}
    for q in inputs:
        if projected_signature(q)!=expected:raise ValueError('Normalize dimension names, order, roles and types before append')
        for f in q['meta'].get('selectedMeasures',[]):
            n=name(f);t=field_family(f)
            if n in measure_types and measure_types[n]!=t:raise ValueError('Incompatible measure type: '+n)
            measure_types[n]=t
    for q in inputs:
        absent=sorted(set(measure_types)-{name(f) for f in q['meta'].get('selectedMeasures',[])})
        if absent and not allow_measure_union:raise ValueError('Measure union requires explicit opt-in')
        missing[q['queryId']]=absent
    return {'dimensions':expected,'measures':measure_types,'missingMeasures':missing}

def query_references(kind,meta):
    refs=meta.get('queries',[])
    if not isinstance(refs,list):raise ValueError('queries must be an array')
    if kind in ('APPEND','SQL_SOURCE'):
        if any(not isinstance(x,(str,int)) or isinstance(x,bool) for x in refs):raise ValueError('Scalar query references required')
        ids=[str(x) for x in refs]
    elif kind=='MERGE':
        if any(not isinstance(x,dict) or 'id' not in x or not isinstance(x.get('sourceMeasures'),list) for x in refs):raise ValueError('Merge needs per-query sourceMeasures')
        ids=[str(x['id']) for x in refs]
    elif kind=='JOIN':
        if any(not isinstance(x,dict) or 'sourceId' not in x or not isinstance(x.get('joinColumnName'),list) for x in refs):raise ValueError('Join needs query IDs and join columns')
        ids=[str(x['sourceId']) for x in refs]
    else:return []
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate query dependency')
    if kind=='SQL_SOURCE' and set(TOKEN.findall(meta.get('sql','')))!=set(ids):raise ValueError('SQL tokens and metadata query references differ; resolve current numeric IDs before reconstruction')
    return ids

def reconcile_meta(kind,meta,query_map,*,measure_maps=None):
    """Rewrite explicit execution slots only. query_map can map Q IDs <-> sqlPk.

    Merge measure IDs have their own per-query mapping; never replace them using a
    query-ID map. Names, literals, unrelated IDs and captions remain byte-equivalent.
    """
    out=copy.deepcopy(meta)
    def mapped(x):
        key=str(x)
        if key not in query_map:raise ValueError('Unresolved execution identity: '+key)
        return query_map[key]
    if 'queries' in out:
        refs=out['queries']
        if kind in ('APPEND','SQL_SOURCE'):out['queries']=[mapped(x) for x in refs]
        elif kind=='MERGE':
            for r in refs:
                old=str(r['id']);r['id']=mapped(old)
                if measure_maps is not None:
                    for f in r['sourceMeasures']:
                        k=(old,str(f['id']))
                        if k not in measure_maps:raise ValueError('Unresolved merge measure identity')
                        f['id']=measure_maps[k]
        elif kind=='JOIN':
            for r in refs:r['sourceId']=mapped(r['sourceId'])
        else:raise ValueError('Unknown execution reference profile')
    if isinstance(out.get('sql'),str):out['sql']=TOKEN.sub(lambda m:'{{query_id:'+str(mapped(m[1]))+'}}',out['sql'])
    return out


def _derived(kind,title,inputs,catalog,config,*,source_id=None,query_id=None):
    if not inputs or len({q['queryId'] for q in inputs})!=len(inputs):raise ValueError('Unique upstream queries required')
    sid=source_id or guid(); code,label=DERIVED[kind]
    q=Query(title,sid,catalog,kind=kind,query_id=query_id).step(code,label,{})
    q.record['meta'].update(copy.deepcopy(config))
    if set(query_references(kind,q.record['meta']))!={x['queryId'] for x in inputs}:raise ValueError('Dependency and metadata mismatch')
    source={'sourceGuid':sid,'name':title,'type':kind,'visualId':None,'meta':copy.deepcopy(q.record['meta']),'queries':[q.record]}
    edges=[{'linkedQueryGuid':guid(),'queryId':x['queryId'],'sourceId':sid,'visualId':x.get('visualId')} for x in inputs]
    return source,edges

def append_queries(title,inputs,catalog,*,allow_measure_union=False,financial=False,**ids):
    contract=append_compatibility(inputs,allow_measure_union=allow_measure_union)
    if financial:append_check(inputs)
    temp={'meta':catalog_meta(catalog)}
    if projected_signature(temp)!=contract['dimensions']:raise ValueError('Append output dimensions differ from inputs')
    if {name(f):field_family(f) for f in temp['meta']['selectedMeasures']}!=contract['measures']:raise ValueError('Append output measure union mismatch')
    return _derived('APPEND',title,inputs,catalog,{'queries':[q['queryId'] for q in inputs]},**ids)

def merge_queries(title,inputs,selected_measures,catalog,**ids):
    """Add matching measures at matching grain. selected_measures maps Q ID to
    real selector descriptors {id,name,alias,aggregationType}; preserve native IDs.
    """
    if len(inputs)<2:raise ValueError('Merge needs two inputs')
    dims=projected_signature(inputs[0]);selection=[];expected=None
    for q in inputs:
        if projected_signature(q)!=dims:raise ValueError('Merge input grain mismatch')
        fields=selected_measures.get(q['queryId'],[])
        if not fields or any(not {'id','name','alias','aggregationType'}<=f.keys() for f in fields):raise ValueError('Complete current merge selector fields required')
        by_name={name(f):f for f in q['meta']['selectedMeasures']}
        if len({name(f) for f in fields})!=len(fields) or any(name(f) not in by_name or f['aggregationType']!='sum' for f in fields):raise ValueError('Merge sample supports explicit sum over existing distinct measures')
        sig=[(name(f),field_family(by_name[name(f)])) for f in fields]
        if any(t!='number' for _,t in sig) or (expected is not None and sig!=expected):raise ValueError('Merge measure names/order/types must match')
        expected=sig;selection.append({'id':q['queryId'],'sourceMeasures':copy.deepcopy(fields)})
    output={'meta':catalog_meta(catalog)}
    if projected_signature(output)!=dims or [(name(f),field_family(f)) for f in output['meta']['selectedMeasures']]!=expected:raise ValueError('Merge output contract mismatch')
    return _derived('MERGE',title,inputs,catalog,{'queries':selection},**ids)

def join_queries(title,left,right,left_keys,right_keys,catalog,*,join_type='LEFT_OUTER',**ids):
    if join_type!='LEFT_OUTER':raise ValueError('This observed constructor supports LEFT_OUTER only')
    if not left_keys or len(left_keys)!=len(right_keys) or len(set(left_keys))!=len(left_keys) or len(set(right_keys))!=len(right_keys):raise ValueError('Ordered join keys required')
    def fields(q):return {name(f):f for k in GROUPS.values() for f in q['meta'].get(k,[])}
    lf,rf=fields(left),fields(right)
    for a,b in zip(left_keys,right_keys):
        if a not in lf or b not in rf or field_family(lf[a])!=field_family(rf[b]):raise ValueError('Join key missing or type mismatch')
    refs=[{'sourceId':left['queryId'],'sourceName':left['name'],'joinColumnName':list(left_keys),'isBaseQuery':True},
          {'sourceId':right['queryId'],'sourceName':right['name'],'joinColumnName':list(right_keys)}]
    return _derived('JOIN',title,[left,right],catalog,{'joinType':join_type,'queries':refs},**ids)

def sql_source(title,inputs,sql,catalog,**ids):
    if not isinstance(sql,str) or not sql.strip() or not TOKEN.findall(sql):raise ValueError('SQL must explicitly reference upstream query tokens')
    # SQL is supplied, not generated from unescaped arbitrary user data. This is
    # the InfoBridge query engine, not an external SQL database write endpoint.
    return _derived('SQL_SOURCE',title,inputs,catalog,{'queries':[q['queryId'] for q in inputs],'sql':sql},**ids)

def editable_source(title,visual_id,catalog,*,destination_id,mde_source_id,table_name,source_id=None,query_id=None):
    if any(not isinstance(x,str) or not x for x in (visual_id,destination_id,mde_source_id,table_name)):raise ValueError('Resolved PowerTable identities required')
    sid=source_id or guid();q=Query(title,sid,catalog,visual_id=visual_id,kind='EDITABLE',query_id=query_id).load_planning()
    meta=copy.deepcopy(q.record['meta']);meta['source']={'infoBridgeSourceType':220,'editable':{'mdeDestinationId':destination_id,'mdeSourceId':mde_source_id,'mdeTableName':table_name,'mdeVisualId':visual_id,'mdeSuperfilter':None}}
    # Source metadata owns connection details; query metadata owns its catalog.
    return {'sourceGuid':sid,'name':title,'type':'EDITABLE','visualId':visual_id,'meta':meta,'queries':[q.record]}

def lookup_key_check(rows,keys,*,allow_duplicates=False):
    """Guard a lookup join against unintended row multiplication before composing it."""
    if not keys:raise ValueError('Lookup key required')
    seen=set();duplicates=[]
    for row in rows:
        key=tuple(row.get(k) for k in keys)
        if any(v is None for v in key):raise ValueError('Null lookup key')
        if key in seen:duplicates.append(key)
        seen.add(key)
    if duplicates and not allow_duplicates:raise ValueError('Lookup join would multiply rows')
    return {'uniqueKeys':len(seen),'duplicates':duplicates}

def execution_map(metadata_records):
    """Query IDs and sqlPk come from readback, never from export list order."""
    from .consumer_bindings import binding_query_id
    out={};used=set()
    for record in metadata_records:
        q=record.get('id');pk=binding_query_id(record)
        if q in out or pk in used:raise ValueError('Incomplete/ambiguous native query identity')
        out[q]=pk;used.add(pk)
    return out

def construct_query(name,source_id,catalog,steps,*,visual_id=None,kind='PLANNING',query_id=None,semantics=None,owner_columns=None,identity_mode='portable'):
    """Agent-built query spec; no eval or arbitrary method dispatch."""
    if kind not in ('PLANNING','EDITABLE'):raise ValueError('Derived sources use their dedicated factories')
    q=Query(name,source_id,catalog,visual_id=visual_id,kind=kind,query_id=query_id,owner_columns=owner_columns,identity_mode=identity_mode).load_planning()
    allowed={'pivot','add','remove','filter_equals','find_replace','rename'}
    for step in steps:
        if set(step)!={'operation','arguments'} or step['operation'] not in allowed:raise ValueError('Unsupported transformation; retain independent modules')
        getattr(q,step['operation'])(**step['arguments'])
    return q.result(semantics or {})

def audit_step_columns(source,query):
    """Detect stale references using the current source base catalog, not final output.
    This is a diagnostic: hidden/context columns missing from a snapshot need current
    source/consumer readback before repair. Unknown transforms are explicit gaps.
    """
    fields={name(f) for g in GROUPS for f in source['meta'].get(g,[])};trace=[];issues=[]
    for step in query['transformationSteps']:
        code=step['meta']['type'];v=step['meta'].get('value');used=[]
        if code==50:
            kept=[name(f) for k in ('sourceDimensions','sourceColumns','sourceMeasures') for f in v.get(k,[])]
            used=kept+[name(f) for f in v.get('removeColumns',[])]
        elif code==180:used=[name(x['sourceColumn']) for x in v]
        elif code==200:used=v['columns']
        elif code==60:used=[name(v['sourceColumn'])]
        elif code==310:used=[name(x) for x in v['sourceColumns']]
        elif code not in (10,130,140,150,170,230):issues.append({'step':step['stepIndex'],'unsupportedType':code})
        absent=sorted(set(used)-fields)
        if absent:issues.append({'step':step['stepIndex'],'unavailableFromSourceSnapshot':absent})
        if code==50:fields=set(kept)
        elif code in (130,170):fields.add(v['columnName'])
        elif code==60:fields.discard(used[0]);fields.add(v['columnName'])
        elif code==310:fields.difference_update(used)
        trace.append({'step':step['stepIndex'],'type':code,'fields':sorted(fields)})
    return {'name':query['name'],'queryId':query['queryId'],'issues':issues,'trace':trace}
