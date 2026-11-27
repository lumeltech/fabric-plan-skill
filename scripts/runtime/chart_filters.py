"""Ordinary Intelligence visual-level filters, separate from hidden scope.

Observed numeric-filter and grouped chart/semantic-measure export shapes.
Call after assigning or resolving chart fields; preserve selections and Context.
"""
import copy
from .construct import guid
from .identity import product_aggregation

NUMERIC={'Int64','Double','Decimal'}

def _measure(a):
    role=a.get('dataRoleType')
    if role not in ('Grouping','Measure'):
        raise ValueError('Resolve the chart field role before registering filters')
    return role=='Measure'

def _key(a):
    # The same field can be grouped or aggregated, or compared in two buckets.
    return tuple(a.get(k) for k in ('id','sourceId','sourceType','visualId','queryId','bucketId','columnType','dataRoleType','aggregationType'))

def _leaf(reg):
    """Dimensions inside a measure filter are evaluation grain, not own cards."""
    assignments=reg.get('pivotAssignments',[])
    if reg.get('isContextDimension') or not reg.get('isDefault'):
        return None
    if reg.get('isDefaultMeasure'):
        leaves=[a for a in assignments if a.get('dataRoleType')=='Measure']
        return leaves[0] if len(leaves)==1 else None
    return assignments[0] if len(assignments)==1 else None

def chart_field_filter(assignment, groupings=()):
    a=copy.deepcopy(assignment);measure=_measure(a)
    if not a.get('id') or not a.get('sourceId') or not a.get('bucketId'):
        raise ValueError('Complete current field identity and bucket required')
    if a.get('sourceType')=='InfoBridge' and not a.get('queryId'):
        raise ValueError('InfoBridge query identity required')
    if measure and a.get('dataType') not in NUMERIC:
        raise ValueError('Nonnumeric measure needs an explicitly supported chart filter contract')
    sort={'id':a['id'],'columnId':a['id'],'columnName':a['columnName'],'direction':'ASC'}
    if a.get('queryId') is not None:sort['queryId']=a['queryId']
    cfg={'name':a.get('customName') or a.get('name') or a['columnName'],
         'hide':False,'isExpanded':False,'locked':False,'singleSelect':False,
         'selectAll':True,'measureSearch':True,'sort':[sort],
         'topN':{'rankMode':'TOP','rankValue':5,'rankType':'value','rankMeasure':'',
                 'displayOthers':True,'otherLabel':'Others','rankMeasureLabel':''},
         'sheetDataItemAggregationType':product_aggregation(a.get('aggregationType')) or 'sum',
         'toolBarTrigger':False,'paneWidth':200}
    if a.get('dataType') in NUMERIC:
        cfg.update(filterMode='advanced',visualType='NUMERIC',scale='none',
                   enableNumericToFacet=False,filterOperator='between',slider=False,regex='',
                   alphaNumericValues={'minValue':None,'maxValue':None,'equalValue':None})
    else:cfg.update(filterMode='basic',visualType='FACET',filterOperator='is')
    dimensions=copy.deepcopy(list(groupings)) if measure else []
    return {'id':'filter_'+guid(),'pivotAssignments':dimensions+[a],
            'isDefault':True,'isDefaultMeasure':measure,
            'isDaxMeasure':a.get('sourceType')=='PowerBI' and a.get('columnType')=='Measure',
            # The inspected chart's measure filter uses AC even for PY; its
            # nested assignment retains the real comparison bucket.
            'bucketId':'AC' if measure else a['bucketId'],
            'configuration':cfg,'filter':[],'position':'RIGHT','filterLevel':'visual'}

def ensure_chart_filters(props):
    """Add only absent ordinary cards; no selection or hidden-scope mutation."""
    fields=props.get('pivotAssignments',[])
    groupings=[a for a in fields if not _measure(a)]
    regs=props.setdefault('superFilterAssignments',[])
    present={_key(leaf) for reg in regs if (leaf:=_leaf(reg)) is not None}
    for a in fields:
        if _key(a) not in present:
            regs.append(chart_field_filter(a,groupings));present.add(_key(a))
    return props

def audit_chart_filters(props):
    """Validate assignment coverage and identity, not rendering or query data."""
    fields=props.get('pivotAssignments',[])
    groupings=[a for a in fields if not _measure(a)]
    regs=props.get('superFilterAssignments',[])
    for a in fields:
        matches=[r for r in regs if (leaf:=_leaf(r)) is not None and _key(leaf)==_key(a)]
        if len(matches)!=1:raise ValueError('Missing/duplicate visual-level filter: '+a['id'])
        r=matches[0];measure=_measure(a);cfg=r.get('configuration',{})
        if r.get('filterLevel')!='visual' or r.get('position')!='RIGHT' or cfg.get('hide') is not False:
            raise ValueError('Assigned field filter is not visible at visual level: '+a['id'])
        def normalize(assignments):
            out=copy.deepcopy(assignments)
            for item in out:
                # Public export normalization may add customSource=true to top-level semantic measures.
                # while preserving the same filter assignment without that flag.
                # It does not change their PowerBI field identity. False and
                # InfoBridge flags remain significant and are not normalized.
                if item.get('sourceType')=='PowerBI' and item.get('columnType')=='Measure' and item.get('customSource') is True:
                    item.pop('customSource')
            return out
        if normalize(r['pivotAssignments'])!=normalize((groupings if measure else [])+[a]):
            raise ValueError('Filter field identities or evaluation grain differ from chart: '+a['id'])
        expected=chart_field_filter(a,groupings)
        for k in ('isDefaultMeasure','isDaxMeasure','bucketId'):
            if r.get(k)!=expected[k]:raise ValueError('Filter role mismatch: '+k)
        if cfg.get('visualType')!=expected['configuration']['visualType']:
            raise ValueError('Filter value type mismatch: '+a['id'])
        if cfg.get('sort')!=expected['configuration']['sort']:
            # Sorting direction can be customized; identity must remain current.
            identity=lambda rows:[{k:v for k,v in x.items() if k!='direction'} for x in rows]
            if identity(cfg.get('sort',[]))!=identity(expected['configuration']['sort']):
                raise ValueError('Filter sort identity mismatch: '+a['id'])
    return {'assignedFields':len(fields),'visibleFieldFilters':len(fields),
            'configuration':'passed','rendering':'not-tested'}

def reconcile_chart_filters(props):
    """Synchronize ordinary cards after an intentional field replacement.

    Retain selection and configuration only for the exact surviving source/role.
    Drop obsolete generated ordinary cards; preserve custom/context registrations.
    Never transfer a selection by display name across source namespaces.
    """
    fields=props.get('pivotAssignments',[]);groupings=[a for a in fields if not _measure(a)]
    active={_key(a):a for a in fields};seen=set();kept=[]
    if len(active)!=len(fields):raise ValueError('Duplicate chart assignment identity')
    for reg in props.get('superFilterAssignments',[]):
        leaf=_leaf(reg)
        if leaf is None:kept.append(reg);continue
        key=_key(leaf)
        if key not in active or key in seen:continue
        a=active[key];updated=copy.deepcopy(reg);expected=chart_field_filter(a,groupings)
        updated['pivotAssignments']=expected['pivotAssignments']
        for name in ('isDefaultMeasure','isDaxMeasure','bucketId'):updated[name]=expected[name]
        # Keep user settings and selections; source-specific sort identities stay aligned.
        oldsort=updated.get('configuration',{}).get('sort',[])
        updated.setdefault('configuration',{}).update(name=expected['configuration']['name'],sort=expected['configuration']['sort'])
        if oldsort:updated['configuration']['sort'][0]['direction']=oldsort[0].get('direction','ASC')
        kept.append(updated);seen.add(key)
    props['superFilterAssignments']=kept
    return ensure_chart_filters(props)
