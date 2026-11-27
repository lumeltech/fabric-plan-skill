"""Numeric semantic or registered InfoBridge Values; axes remain semantic."""
import copy
from .semantic_values import semantic_value
from .identity import product_aggregation

def value_assignment(model,key,registry,*,query_fields=(),bucket='ameasure',order=0,label=None,aggregation=None):
    if any(f['id']==key for f in model['fields']):
        return semantic_value(model,key,registry,bucket=bucket,order=order,label=label,aggregation=aggregation)
    matches=[f for f in query_fields if f.get('id')==key]
    if len(matches)!=1:raise ValueError('Value absent from current semantic/query catalog')
    f=copy.deepcopy(matches[0]);required={'id','sourceId','queryId','columnName','tableName','columnType','dataType','sourceType'}
    if not required<=f.keys() or f['sourceType']!='InfoBridge' or f['sourceId']!=key:
        raise ValueError('Complete registered InfoBridge identity required')
    if f['dataType'] not in ('Int64','Double','Decimal') or f['columnType']!='Column':
        raise ValueError('Numeric query output Column required')
    if not key.startswith(f['queryId']+'[') or not key.endswith(']'):
        raise ValueError('Query and qualified output identity disagree')
    method=product_aggregation(aggregation or 'sum')
    if method not in ('sum','minimum','maximum','count','average'):raise ValueError('Explicit supported query aggregation required')
    mid=registry.semantic(key,'Column',method)
    f={k:f[k] for k in required}
    f.update(aggregationType=method,measureGuid=mid,bucketId=bucket,order=order,
        customName=label or f['columnName'],name=label or f['columnName'],customSource=True,
        dataRoleType='Measure',isFlatHierarchy=False,distinctValueCount=None,formatString='')
    return f
