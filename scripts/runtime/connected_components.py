"""Parametric connected-planning components, independent of any saved report."""
import copy
from .bridge import Query
from .identity import native_id,product_aggregation

def contribution(name, source_id, catalog, dimensions, periods, metrics, semantics, *, visual_id=None, query_id=None, dimension_formulas=(),owner_columns=None,identity_mode='portable'):
    """Normalize one additive P&L input before append, preserving explicit context.

    dimensions/periods are ordered current output aliases. Source mappings such
    as Account/PNLGroup must already exist (Query.add(kind='dimension')).
    All metric expressions are explicitly cast; zeros need business opt-in.
    """
    q=Query(name,source_id,catalog,visual_id=visual_id,query_id=query_id,owner_columns=owner_columns,identity_mode=identity_mode).load_planning()
    for d in dimension_formulas:
        q.add(d['name'],d['expression'],d['id'],kind='dimension',requires=d['requires'])
    if not metrics: raise ValueError('Explicit contribution metrics required')
    if not isinstance(semantics,dict) or not {'period','scenario','currency','signConvention'}<=semantics.keys():
        raise ValueError('Explicit append period/scenario/currency/sign semantics required')
    if any(not isinstance(semantics[k],str) or not semantics[k].strip() for k in ('period','scenario','currency','signConvention')):
        raise ValueError('Nonempty append semantics required')
    if semantics['period'] not in periods or semantics['scenario'] not in dimensions:
        raise ValueError('Declared period/scenario must survive in the normalized output grain')
    metric_names=[]
    for metric in metrics:
        if not isinstance(metric,dict) or not {'name','expression','id','requires'}<=metric.keys(): raise ValueError('Complete metric specification required')
        expr=metric['expression']
        # Check zero meaning before adding a cast that would hide literal-zero detection.
        q.add(metric['name'],expr,metric['id'],requires=metric['requires'],zero_is_valid=metric.get('zeroIsValid',False))
        q.record['transformationSteps'][-1]['meta']['value']['formulaQuery']='CAST(('+expr+') AS DOUBLE)'
        metric_names.append(metric['name'])
    q.pivot(dimensions,periods,{n:'sum' for n in metric_names})
    return q.result(semantics)

def embedded_planning(owner_sheet, visual_id):
    """Portable reference only. Page-local geometry uses resolved runtime IDs later."""
    if owner_sheet.get('sheetType')!='PLANNING': raise ValueError('Direct Planning owner required')
    matches=[v for v in owner_sheet['workloadItemEntityVisuals'] if v['visualId'].casefold()==visual_id.casefold() and not v.get('isEmbedded') and v['visualType']=='PLANNING']
    if len(matches)!=1: raise ValueError('Missing/ambiguous direct Planning visual')
    return {'visualId':matches[0]['visualId'],'visualType':'PLANNING','isEmbedded':True}

def bridge_consumer(field, visual_id, measure_id, label, *, order=0, aggregation='sum'):
    """Build assignment and Native companion using the ACTUAL query output catalog.

    This does not allocate/import a query or infer its output ID from its label.
    measure_id is the destination-resolved/registry identity, kept as a string.
    """
    native_id(measure_id)
    required={'id','queryId','columnName','tableName','columnType','dataType','sourceType'}
    if not required<=field.keys() or field['sourceType']!='InfoBridge': raise ValueError('Actual complete InfoBridge field catalog required')
    if any(not isinstance(field[k],str) or not field[k].strip() for k in required): raise ValueError('Nonempty catalog identity and type fields required')
    if field['columnType']!='Column' or field['dataType'] not in ('Double','Int64','Decimal'): raise ValueError('Numeric InfoBridge output required')
    if not isinstance(visual_id,str) or not visual_id.strip() or not isinstance(label,str) or not label.strip() or isinstance(order,bool) or not isinstance(order,int) or order<0: raise ValueError('Destination visual/label/order required')
    aggregation=product_aggregation(aggregation)
    if aggregation not in ('sum','minimum','maximum','average'): raise ValueError('Unverified consumer aggregation')
    assignment={k:copy.deepcopy(field[k]) for k in required}
    assignment.update(aggregationType=aggregation,bucketId='ameasure',customName=label,customSource=True,
        dataRoleType='Measure',distinctValueCount=None,formatString=field.get('formatString',''),isFlatHierarchy=False,
        measureGuid=measure_id,name=label,order=order,sourceId=field['id'])
    for k in ('tableId','infoBridgeSourceId','infoBridgeSourceGuid'):
        if k in field: assignment[k]=copy.deepcopy(field[k])
    record={'boundToFilterContext':10,'columnMeta':{'data_type':'Number','description':None,'id':measure_id,
          'label':label,'name':label,'measure_type':{'Native':{'measure_role':'ACMeasure'}}},
          'dataInputType':6,'description':None,'measureGuid':measure_id,'name':label,'visualId':visual_id}
    native_aggregation={'sum':'Sum','minimum':'Min','maximum':'Max','average':'Average'}[aggregation]
    return {'assignment':assignment,'dataInputColumn':record,
        'manageMeasure':{'id':measure_id,'label':label,'order':order,'visible':True},
        'measureAggregation':{measure_id:{'row':native_aggregation,'column':native_aggregation}},
        'evidence':{'catalogBinding':'constructed','registration':'not-run','values':'not-tested'}}
