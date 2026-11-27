"""External Planning Context and ordinary semantic slicers are different roles.

These authoring shapes are observed in a native export. Runtime context hashes
are deliberately not generated or copied; the service owns that cache.
"""
import copy, math
from decimal import Decimal
from .construct import field, guid

NUMERIC={'Int64','Double','Decimal'}

def selection(model, key, *, values=None, between=None):
    a=field(model,key,'rows',0)
    if a['columnType']!='Column': raise ValueError('Filters require a semantic dimension column')
    typ=a['dataType']
    if typ not in NUMERIC|{'String','Boolean'}: raise ValueError('Selected filter data type needs its own factory')
    if values is not None and between is not None: raise ValueError('Choose VALUES or RANGE, never intersect stale defaults')
    native='number' if typ in NUMERIC else 'boolean' if typ=='Boolean' else 'string'
    dto={'columnDataType':[typ],'columnIds':[key],'columnNames':[a['columnName']],
         'columnType':['Column'],'dataType':[native],'sourceType':['PowerBI'],'tableNames':[a['tableName']]}
    def valid(v):
        if typ=='String': return isinstance(v,str)
        if typ=='Boolean': return isinstance(v,bool)
        return not isinstance(v,bool) and isinstance(v,(int,float,Decimal)) and math.isfinite(v) and (typ!='Int64' or v==int(v))
    if values is not None:
        if not isinstance(values,list) or not values or any(not valid(v) for v in values): raise ValueError('Explicit, correctly typed selected members required')
        if len({(type(v).__name__,v) for v in values})!=len(values): raise ValueError('Duplicate selected member')
        return [{**dto,'filterType':'VALUES','valuesFilter':[{'id':[v],'label':[str(v)]} for v in values],
                 'valuesFilterApplicationType':'include'}]
    if between is not None:
        if typ not in NUMERIC or not isinstance(between,list) or len(between)!=2 or not all(valid(v) for v in between) or between[0]>between[1]:
            raise ValueError('Numeric range requires ordered typed endpoints')
        return [{**dto,'filterType':'RANGE','rangeFilter':[{'from':between[0],'fromCondition':'IS_GREATER_THAN_OR_EQUAL_TO',
                 'logicalOperator':'and','to':between[1],'toCondition':'IS_LESS_THAN_OR_EQUAL_TO'}]}]
    return []

def registration(model, spec, *, context=False):
    allowed={'field','label','values','between','singleSelect','required'}
    if set(spec)-allowed: raise ValueError('Unconsumed filter options: '+','.join(sorted(set(spec)-allowed)))
    key=spec['field']; a=field(model,key,'rows',0)
    if a['columnType']!='Column': raise ValueError('Context/slicer must use a dimension')
    single=spec.get('singleSelect',context); required=spec.get('required',context)
    if not isinstance(single,bool) or not isinstance(required,bool): raise ValueError('Filter flags must be Boolean')
    filters=selection(model,key,values=spec.get('values'),between=spec.get('between'))
    if context and (not single or spec.get('between') is not None or len(spec.get('values',[]))!=1):
        raise ValueError('This Context factory requires one explicit selected member')
    if required and not filters: raise ValueError('Required selector needs an explicit initial selection')
    if single and len(spec.get('values',[]))>1: raise ValueError('Single-select has multiple members')
    a['bucketId']='Category' if context else 'category'
    cfg={'filterMode':'basic','filterOperator':'is','hide':False,'isExpanded':True,
         'isSliderAndChartsEnabled':True,'locked':False,'measureFilter':{'maxValue':None,'minValue':None},
         'measureSearch':True,'name':spec.get('label',a['columnName']),'paneWidth':200,'selectAll':False,
         'selectAllState':'UNSELECTED','sheetDataItemAggregationType':'sum','singleSelect':single,
         'sort':[{'columnId':key,'columnName':a['columnName'],'direction':'ASC','id':key}],
         'toolBarTrigger':False,'topN':{'displayOthers':True,'otherLabel':'Others','rankMeasure':'',
         'rankMeasureLabel':'','rankMode':'TOP','rankType':'value','rankValue':5},'visualType':'FACET'}
    out={'configuration':cfg,'filter':filters,'filterLevel':'visual','id':'filter_'+guid(),
         'pivotAssignments':[a],'position':'RIGHT'}
    if context: out['isContextDimension']=True
    else: out.update(bucketId='category',isDefault=True,isDefaultMeasure=False,isDaxMeasure=False)
    return out

def prepare_context(model, spec):
    """Return a new spec and registrations; never move Context onto visible axes."""
    out=copy.deepcopy(spec); contexts=out.get('context',[])
    if not isinstance(contexts,list): raise ValueError('context must be a list')
    keys=[c['field'] for c in contexts]
    if len(keys)!=len(set(keys)): raise ValueError('Duplicate Context field')
    if set(keys)&set(out.get('rows',[])+out.get('columns',[])): raise ValueError('Context is external; remove it from visible axes')
    for pivot in out.get('pivots',[]):
        if set(keys)&set((pivot.get('rows') or [])+(pivot.get('columns') or [])): raise ValueError('Saved pivot must keep Context external')
    if contexts and ('filterContextSettings' in out or any(x.get('isContextDimension') for x in out.get('superFilterAssignments',[]))):
        raise ValueError('Use symbolic Context or native Context overrides, not both')
    registrations=[registration(model,c,context=True) for c in contexts]
    if contexts:
        for m in out.get('measures',[]):
            if m['kind']=='DataInput':
                if m.get('context_bound') is False: raise ValueError('Storage-context inputs must remain bound to Context')
                m['context_bound']=True
        descriptors=out.setdefault('lookupContextAssignments',[])
        existing={a['id'] for a in descriptors}
        for i,key in enumerate(keys):
            if key not in existing: descriptors.append(field(model,key,'rows',len(out.get('rows',[]))+i))
    return out,registrations

def ordinary_axis_filter(assignment):
    """Planning side-panel grouping field; separate from external Context."""
    a=copy.deepcopy(assignment)
    if a.get('sourceType')!='PowerBI' or a.get('columnType')!='Column' or a.get('dataRoleType')!='Grouping' or a.get('bucketId') not in ('rows','columns'):
        raise ValueError('Semantic grouping assignment required')
    cfg={'name':a['columnName'],'hide':False,'isExpanded':False,'locked':False,
         'filterMode':'basic','visualType':'FACET','singleSelect':False,'selectAll':True,
         'measureSearch':True,'filterOperator':'is','sheetDataItemAggregationType':'sum',
         'toolBarTrigger':False,'paneWidth':200,
         'sort':[{'id':a['id'],'columnId':a['id'],'columnName':a['columnName'],'direction':'ASC'}],
         'topN':{'rankMode':'TOP','rankValue':5,'rankType':'value','rankMeasure':'',
                 'displayOthers':True,'otherLabel':'Others','rankMeasureLabel':''}}
    return {'id':'filter_'+guid(),'pivotAssignments':[a],'isDefault':True,
            'isDefaultMeasure':False,'isDaxMeasure':False,'bucketId':a['bucketId'],
            'configuration':cfg,'filter':[],'position':'RIGHT','filterLevel':'visual'}

def ensure_axis_filters(props):
    regs=props.setdefault('superFilterAssignments',[])
    present={a['id'] for r in regs for a in r.get('pivotAssignments',[]) if not r.get('isDefaultMeasure')}
    for a in props.get('pivotAssignments',[]):
        if a.get('sourceType')=='PowerBI' and a.get('dataRoleType')=='Grouping' and a.get('bucketId') in ('rows','columns') and a['id'] not in present:
            regs.append(ordinary_axis_filter(a));present.add(a['id'])
    return props


def select_axis_filter(props, field_id, selected):
    """Select only the dimension's own ordinary card, never a measure's grain.

    Numeric measure cards carry grouping assignments for evaluation. A matching
    Year inside that list does NOT make the card a Year selector.
    """
    for reg in props.get('superFilterAssignments',[]):
        assignments=reg.get('pivotAssignments',[])
        if reg.get('isContextDimension') or reg.get('isDefaultMeasure') or reg.get('isDaxMeasure'):continue
        if len(assignments)!=1:continue
        a=assignments[0]
        if a.get('dataRoleType')!='Grouping' or a.get('id')!=field_id:continue
        reg['filter']=copy.deepcopy(selected)
        reg.setdefault('configuration',{}).update(selectAll=not bool(selected))
        if selected:reg['configuration']['selectAllState']='UNSELECTED'
        else:reg['configuration'].pop('selectAllState',None)
    return props

def apply_context(props, registrations):
    if not registrations: return
    props['superFilterAssignments'].extend(copy.deepcopy(registrations))
    vs=props['visualState']; embedded=vs.setdefault('embeddedSuperFilter',{}).setdefault('superFilterAssignments',[])
    embedded.extend(copy.deepcopy(registrations))
    vs['filterContextSettings']={'filterContextStatus':True,'isCommentFilterContext':True,'isNoteFilterContext':True}
    # No historical filterContextHashMap or filterContextProperties are seeded.

def forward_filters(props, filters):
    """Seed ordinary selected scope while preserving full Context registrations.

    This is persisted INITIAL filter scope, not an event propagation engine.
    Never freeze slicer defaults into the reusable source Planning owner.
    """
    target=props.setdefault('visualState',{}).setdefault('embeddedSuperFilter',{}).setdefault('superFilterAssignments',[])
    existing={f['columnIds'][0] for x in target for f in x.get('filter',[]) if x.get('isContextDimension')}
    for dto in filters:
        if dto['columnIds'][0] in existing: raise ValueError('Ordinary filter must not overwrite Context')
        target.append({'filter':[copy.deepcopy(dto)]})

def audit_context(props, records=()):
    regs=[r for r in props.get('superFilterAssignments',[]) if r.get('isContextDimension')]
    vs=props['visualState']; mirrored=vs.get('embeddedSuperFilter',{}).get('superFilterAssignments',[])
    axes={a['id'] for a in props.get('pivotAssignments',[]) if a['bucketId'] in ('rows','columns')}
    ids=[]
    for r in regs:
        if r not in mirrored: raise ValueError('Missing exact Context mirror')
        a=r['pivotAssignments'][0];ids.append(a['id'])
        if a['id'] in axes or a['bucketId']!='Category': raise ValueError('Row/column dimensions already define storage grain; Context must be external')
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate Context field')
    if regs:
        if vs.get('filterContextSettings',{}).get('filterContextStatus') is not True: raise ValueError('Context disabled')
        for r in records:
            kind=r['columnMeta']['measure_type']
            kind=kind.get('VisualColumn',kind)
            di=kind.get('DataInput',kind.get('Forecast'))
            if di is not None and (di.get('bound_to_filter_context') is not True or r.get('boundToFilterContext')!=10):
                raise ValueError('Input not bound to Context')
    return {'contexts':len(regs),'status':'passed-static-context','selectionPropagation':'not-tested','inputIsolation':'not-tested'}
