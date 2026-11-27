"""Local Planning presentation only; never changes calculations or storage."""
import copy

TOTALS_DEFAULTS = {'row_grand_total':'Top', 'row_sub_total':'Top',
                   'column_grand_total':'Left', 'column_sub_total':None}
TOTAL_VALUES = {'row_grand_total':('Top','Bottom',None),
                'row_sub_total':('Top','Bottom','Split',None),
                'column_grand_total':('Left','Right',None),
                'column_sub_total':('Left','Right',None)}

def apply_totals_defaults(properties, *, reset=False):
    """Fill absent positions; explicit null/positions survive unless reset=True."""
    out=copy.deepcopy(properties)
    vs=out['visualState']
    totals=vs.get('totals_config')
    if totals is None:totals={};vs['totals_config']=totals
    if not isinstance(totals,dict):raise ValueError('totals_config must be an object')
    for key,value in TOTALS_DEFAULTS.items():
        if reset or key not in totals:totals[key]=value
        if totals[key] not in TOTAL_VALUES[key]:raise ValueError('Invalid native total position: '+key)
    return out

def roll_forward_presentation(properties, hierarchy, *, totals=True, reset_totals=False, label_width=None):
    """Apply a resolved preorder tree covering each visible measure exactly once.

    hierarchy is [{id: <exact current string ID>, level: <int>}]. Resolve business
    roles before this call. Tree placement does not calculate parent arithmetic.
    """
    out=copy.deepcopy(properties);vs=out['visualState']
    managed=vs['manage_measures'];ids=[m['id'] for m in managed]
    if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)):
        raise ValueError('Resolve unique current string measure IDs')
    visible={m['id'] for m in managed if m.get('visible',True)}
    ordered=[n['id'] for n in hierarchy]
    if not hierarchy or len(ordered)!=len(set(ordered)) or set(ordered)!=visible:
        raise ValueError('Hierarchy must cover every visible measure exactly once; exclude hidden helpers')
    prior=0
    for index,n in enumerate(hierarchy):
        level=n.get('level')
        if type(level) is not int or level<0 or (index==0 and level!=0) or level>prior+1:
            raise ValueError('Preorder levels start at zero and increase by at most one')
        prior=level
    existing={n['id']:n for n in vs.get('measure_tree') or []}
    nodes=[]
    for entry in hierarchy:
        node=copy.deepcopy(existing.get(entry['id']) or {'id':entry['id'],
            'meta':{'hide_in':None,'node_type':{'Measure':{'aggregation':None}},'rules':None}})
        node['level']=entry['level'];nodes.append(node)
    byid={m['id']:m for m in managed}
    vs['manage_measures']=[byid[i] for i in ordered]+[m for m in managed if m['id'] not in visible]
    for index,m in enumerate(vs['manage_measures']):m['order']=index
    vs['layout']={**(vs.get('layout') or {}),'layout_type':'Hierarchy','measure_layout':'Rows'}
    vs['measure_tree']=nodes
    expanded=copy.deepcopy(vs.get('measure_tree_node_expand_state') or {})
    parents=[nodes[i]['id'] for i in range(len(nodes)-1) if nodes[i+1]['level']>nodes[i]['level']]
    expanded.update(default_count=1,max_count=len(nodes),expanded={
        **{k:v for k,v in expanded.get('expanded',{}).items() if k in visible},
        **{key:True for key in parents}})
    vs['measure_tree_node_expand_state']=expanded
    if isinstance(vs.get('ragged_hierarchy_config'),dict):vs['ragged_hierarchy_config']['enabled']=False
    if label_width is not None:
        if isinstance(label_width,bool) or not isinstance(label_width,(int,float)) or not 0<label_width<float('inf'):
            raise ValueError('label_width must be a positive finite pixel width')
        vs.setdefault('layoutSizes',{})['labelWidth']=label_width
    if reset_totals and not totals:raise ValueError('reset_totals requires totals=True')
    return apply_totals_defaults(out,reset=reset_totals) if totals else out
