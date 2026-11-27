"""Storage-context contracts, separate from ordinary page/global filtering.

This module validates authoring evidence. It never changes stored coordinates,
copies runtime context hashes, or claims live filter propagation was tested.
"""
import copy,math


def signature(owner):
    """Canonical context fields, ID mappings and typed initial selections.

    Accept a symbolic sheet spec or fresh native Planning properties. Labels,
    order and filter registration UUIDs do not identify storage coordinates.
    """
    if 'visualState' not in owner:
        axes=set(owner.get('rows',[])+owner.get('columns',[]))
        mappings=owner.get('dimensionIdMappings',{})
        items=[]
        for c in owner.get('context',[]):
            if c.get('singleSelect',True) is not True or c.get('between') is not None:
                raise ValueError('Storage Context requires one selected member')
            items.append((c['field'],c.get('values',[]),None))
        if any(r.get('isContextDimension') for r in owner.get('superFilterAssignments',[])):
            raise ValueError('Use symbolic context before construction; native overrides need a current native audit')
    else:
        from .filters import audit_context
        audit_context(owner)
        axes={a['id'] for a in owner.get('pivotAssignments',[]) if a.get('bucketId') in ('rows','columns')}
        mappings=owner['visualState'].get('dimension_id_mapping',{}).get('mappings') or {}
        items=[]
        for r in owner.get('superFilterAssignments',[]):
            if not r.get('isContextDimension'):continue
            if len(r.get('pivotAssignments',[]))!=1 or r.get('configuration',{}).get('singleSelect') is not True:
                raise ValueError('Storage Context requires one semantic field and single selection')
            a=r['pivotAssignments'][0];fs=r.get('filter',[])
            if len(fs)!=1 or fs[0].get('filterType')!='VALUES' or fs[0].get('columnIds')!=[a['id']]:
                raise ValueError('Unresolved Context selection')
            vals=fs[0].get('valuesFilter',[])
            if len(vals)!=1 or len(vals[0].get('id',[]))!=1:
                raise ValueError('Storage Context requires exactly one selected member')
            items.append((a['id'],vals[0]['id'],a.get('dataType')))
    result={}
    for field,values,data_type in items:
        if field in axes:raise ValueError('Row/column dimensions already define storage grain; do not repeat them in Context: '+field)
        if field in result or len(values)!=1:raise ValueError('Duplicate or unselected Context: '+field)
        mapping=mappings.get(field)
        if mapping is not None and (not isinstance(mapping,dict) or set(mapping)!={'ID'}):
            raise ValueError('Storage Context cannot be skipped or use an unresolved key strategy')
        value=values[0]
        if value is None or not isinstance(value,(str,int,float,bool)):
            raise ValueError('Explicit typed Context member required')
        typ=type(value).__name__
        if isinstance(value,(int,float)) and not isinstance(value,bool):
            if not math.isfinite(value):raise ValueError('Finite Context member required')
            typ='number'
        result[field]={'key':copy.deepcopy(mapping),'selection':{'type':typ,'value':value}}
    return dict(sorted(result.items()))


def require_same(source,destination):
    """Require the same context identity and initial selection on both owners."""
    a,b=signature(source),signature(destination)
    if a!=b:
        raise ValueError('Connected Planning storage Context mismatch; align source and destination fields, keys and selections. Page/global filters are not substitutes.')
    return {'status':'matched-storage-context','fields':list(a),'runtimeInputIsolation':'not-tested'}


def query_contract(query,source_owners,output_map):
    """Prove context survives a query using current owner and output evidence.

    output_map maps semantic context IDs to selected query output field IDs.
    This is a build-time sidecar, not an invented native query property. Native
    transforms still need their own lineage/aggregation contract.
    """
    from .consumer_bindings import output_catalog,binding_query_id
    if not source_owners:raise ValueError('Current source owners are required for query context lineage')
    expected=signature(source_owners[0])
    for owner in source_owners[1:]:require_same(source_owners[0],owner)
    if set(output_map)!=set(expected):raise ValueError('Query must retain every storage Context field')
    fields={f['outputId']:f for f in output_catalog(query)}
    if len(set(output_map.values()))!=len(output_map):raise ValueError('Context fields cannot collapse onto one query output')
    for fid in output_map.values():
        if fid not in fields or fields[fid]['role'] not in ('dimensions','columns'):
            raise ValueError('Context lineage must resolve to an actual selected query dimension')
    return {'queryId':binding_query_id(query),'signature':expected,'outputMap':copy.deepcopy(output_map)}


def require_query(contract,destination,query_id):
    if not isinstance(contract,dict) or contract.get('queryId')!=str(query_id):
        raise ValueError('From Queries needs a verified storage-context sidecar from current source/output metadata')
    if contract.get('signature')!=signature(destination):
        raise ValueError('From Queries destination storage Context differs from source lineage')
    if set(contract.get('outputMap',{}))!=set(contract['signature']):
        raise ValueError('Query context lineage is incomplete')
    return {'status':'matched-query-storage-context','fields':list(contract['signature']),'runtimeInputIsolation':'not-tested'}


def audit_links(destination,owners,query_contracts=None):
    """Audit Planning From Sheets/Queries consumers against their actual owners."""
    results=[];query_contracts=query_contracts or {}
    for a in destination.get('pivotAssignments',[]):
        if a.get('sourceType')=='Visual':
            matches=[o for o in owners if str(o['visualId'])==str(a.get('visualId'))]
            if len(matches)!=1:raise ValueError('Resolve one current linked source owner for context validation')
            results.append(require_same(matches[0]['properties'],destination))
        elif a.get('sourceType')=='InfoBridge':
            qid=str(a.get('queryId'));results.append(require_query(query_contracts.get(qid),destination,qid))
    return {'links':len(results),'checks':results,'runtimeInputIsolation':'not-tested'}
