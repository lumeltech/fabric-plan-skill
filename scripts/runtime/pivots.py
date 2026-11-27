"""Saved native Pivot configs compiled from symbolic axes; no report templates.

This builds persisted state, not an invented controller request. ALM acceptance
and runtime switching are separate evidence stages.
"""
import copy
from .identity import native_id, xxh3

AGGREGATIONS={'Sum','Min','Max','Average','AverageExclusiveZero','AverageLeaf',
              'StandardDeviation','First','Last','Formula','None'}

def compile_pivots(specs, sheet, registry, active=None, capabilities=None):
    capabilities={} if capabilities is None else capabilities
    if not isinstance(specs,list) or not isinstance(capabilities,dict): raise ValueError('Invalid Pivot specification')
    if any(not isinstance(v,bool) for v in capabilities.values()): raise ValueError('Capability flags must be Boolean')
    rows=sheet['rows']; columns=sheet['columns']; dims=sheet['dimensions']; measures=sheet['measures']
    default_id=registry.bind('pivot:default',str(xxh3('default_pivot')))
    configs=[{'id':default_id,'name':'All','row_dimensions':None,'col_dimensions':None,'measures':None,'hidden':False}]
    names={'all'}; ids={'all':default_id}
    for s in specs:
        name=s['name'].strip(); key=s.get('key',name)
        if not name or name.casefold() in names or key in ids: raise ValueError('Duplicate/blank saved Pivot')
        names.add(name.casefold())
        rr=s.get('rows'); cc=s.get('columns')
        if rr is None and cc is None: raise ValueError('Named Pivot needs at least one explicit axis')
        def axis(seq, source, other):
            if seq is None: return None
            if not isinstance(seq,list) or len(seq)!=len(set(seq)): raise ValueError('Invalid Pivot axis')
            allowed=set(source)
            if capabilities.get('PlanningCrossPivot') and capabilities.get('PlanningColumnPivot'): allowed|=set(other)
            if not set(seq)<=allowed: raise ValueError('Pivot axis unavailable or cross-axis gate disabled')
            return [native_id(dims[k]) for k in seq]
        r=axis(rr,rows,columns); c=axis(cc,columns,rows)
        effective_r=r if r is not None else [dims[k] for k in rows]
        effective_c=c if c is not None else [dims[k] for k in columns]
        if set(effective_r)&set(effective_c): raise ValueError('Dimension on both Pivot axes')
        mm=s.get('measures')
        if mm==[]: raise ValueError('Empty explicit Pivot measure selection')
        selected=None
        if mm is not None:
            selected=[]; seen=set()
            for m in mm:
                if m['key'] not in measures or m['key'] in seen: raise ValueError('Unknown/duplicate Pivot measure')
                seen.add(m['key']); agg=m['aggregation']; col=m.get('columnAggregation',agg)
                if agg not in AGGREGATIONS or col not in AGGREGATIONS: raise ValueError('Invalid Pivot aggregation')
                selected.append({'id':measures[m['key']],'aggregation_type':agg,'column_aggregation_type':col})
        if not isinstance(s.get('hidden',False),bool): raise ValueError('hidden must be Boolean')
        pid=registry.custom('pivot:'+sheet['sheetId']+':'+key); ids[key]=pid
        configs.append({'id':pid,'name':name,'row_dimensions':r,'col_dimensions':c,'measures':selected,'hidden':s.get('hidden',False)})
    if active is not None and active not in ids: raise ValueError('Unknown active Pivot')
    active_id=None if active in (None,'all') else ids[active]
    if any(c['id']==active_id and c['hidden'] for c in configs): raise ValueError('Active Pivot is hidden')
    return {'pivot':{'configs':configs,'active_id':active_id},
            'pivotExplorer':{'showPivotExplorer':True,'activePivot':active_id},'ids':ids}

def select_pivot(state,pivot_id):
    out=copy.deepcopy(state); candidates=out['pivot']['configs']
    if pivot_id is not None and not any(c['id']==pivot_id and not c.get('hidden') for c in candidates):
        raise ValueError('Missing/hidden Pivot')
    out['pivot']['active_id']=pivot_id
    out.setdefault('pivotExplorer',{})['activePivot']=pivot_id
    # The native controller resets expansion. Do not invent pagination/expansion shapes.
    return out
