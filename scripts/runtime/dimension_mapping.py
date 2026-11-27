"""Construct ID/Skip mappings and their native lookup descriptors from live metadata.

For new coordinates only. This is not a migration of existing input values.
The returned pivot is lookup metadata; it must not replace visible assignments.
"""
import copy,re

BUCKETS={'rows':'Row','columns':'Column','ameasure':'ACMeasure'}

def leaf_key_mapping(model, assignments, groups, *, overrides=None, existing=None):
    """Default redundant same-entity ancestors to Skip; keep visible assignments.

    Groups are resolved by the author from model metadata/business grain, not by
    guessing that the last column or every field in a table is an ancestor.
    None in overrides means retain the native label/default key strategy.
    Existing storage changes require a separate migration, not this constructor.
    """
    fields={f['id']:f for f in model['fields']}
    assigned={a['id']:a for a in assignments if a.get('bucketId') in ('rows','columns')}
    mappings={}; support={}; used=set()
    if not isinstance(groups,list) or not groups: raise ValueError('Resolved leaf key groups required')
    for g in groups:
        if set(g)-{'leaf','key','ancestors','unique','determinesAncestors','evidence','isTime'}:
            raise ValueError('Unknown leaf-key group option')
        leaf=g['leaf'];key=g['key'];ancestors=g.get('ancestors',[])
        if not isinstance(ancestors,list) or any(not isinstance(x,str) for x in [leaf,key,*ancestors]):
            raise ValueError('Resolved string identities required')
        if not g.get('evidence') or g.get('unique') is not True or g.get('determinesAncestors') is not True:
            raise ValueError('Leaf key needs uniqueness and ancestor-dependency evidence from metadata/business contract')
        if g.get('isTime') or any(re.search(r'\b(year|quarter|month|week|day|date)\b',fields.get(x,{}).get('columnName',''),re.I) for x in [leaf,*ancestors]):
            raise ValueError('Calendar key reduction needs its separate period/grain contract; do not auto-skip it')
        if leaf not in assigned or key not in fields: raise ValueError('Resolve the assigned leaf and semantic key')
        if any(x not in assigned or fields[x]['tableName']!=fields[leaf]['tableName'] or assigned[x]['bucketId']!=assigned[leaf]['bucketId'] for x in ancestors):
            raise ValueError('Only confirmed same-table, same-axis ancestors may be excluded')
        group={leaf,*ancestors}
        if len(group)!=len(ancestors)+1 or used&group: raise ValueError('Overlapping or repeated leaf hierarchy')
        used.update(group);mappings[leaf]={'ID':key}
        for ancestor in ancestors:mappings[ancestor]={'Skip':{}};support[ancestor]=leaf
    for field,strategy in (overrides or {}).items():
        if field not in assigned: raise ValueError('Override must refer to an assigned dimension')
        if strategy is None:mappings.pop(field,None);support.pop(field,None)
        else:mappings[field]=copy.deepcopy(strategy)
    result=dimension_mapping(model,assignments,mappings,skip_support={k:v for k,v in support.items() if mappings.get(k)=={'Skip':{}}})
    if existing is not None and (existing.get('mappings') or {})!=result['mappings']:
        raise ValueError('Existing storage identity would change; use an explicit supported value migration, not a style/key patch')
    return result

def dimension_mapping(model, assignments, mappings, *, descriptor_only_assignments=(), skip_support=None):
    fields={f['id']:f for f in model['fields']}
    if len(fields)!=len(model['fields']): raise ValueError('Duplicate semantic field identity')
    if not isinstance(mappings,dict) or not mappings: raise ValueError('Explicit ID/Skip mappings required')
    skip_support=skip_support or {}
    if set(skip_support)-set(mappings): raise ValueError('Unexpected Skip evidence')
    descriptors=[]; by_id={}
    for a in [*assignments,*descriptor_only_assignments]:
        if a.get('sourceType')!='PowerBI':
            if a.get('bucketId')=='ameasure': continue
            raise ValueError('Only semantic dimension identity mappings supported')
        if a.get('id') not in fields or a.get('bucketId') not in BUCKETS:
            raise ValueError('Unresolved field or native role')
        f=fields[a['id']]
        if a.get('columnType')!=f['columnType'] or a.get('dataType')!=f['dataType']:
            raise ValueError('Assignment differs from current semantic metadata')
        if any(a.get(k) for k in ('fieldParameterDataType','groupDataType','relationships')):
            raise ValueError('Grouped/parameter lookup descriptor needs its own contract')
        agg=a.get('aggregationType') or 'None'
        agg={'sum':'Sum','avg':'Average','average':'Average','min':'Min','minimum':'Min','max':'Max','maximum':'Max',
             'count':'Count','none':'None'}.get(agg,agg)
        if agg not in ('Sum','Average','Min','Max','Count','None'): raise ValueError('Unsupported native lookup aggregation')
        d={'aggregation_type':agg,'bucket_type':BUCKETS[a['bucketId']],
           'column_name':f['columnName'],'column_type':f['columnType'],
           'custom_name':a.get('customName'),'external_data_type':f['dataType'],
           'field_parameter_data_type':None,'group_data_type':None,'id':f['id'],
           'name':a.get('name',f['columnName']),'order':a['order'],'relationships':None,'source_type':'PowerBI'}
        if d['id'] in by_id:
            if by_id[d['id']]!=d: raise ValueError('Conflicting dimension descriptor roles')
            continue
        descriptors.append(d);by_id[d['id']]=d
    for label,strategy in mappings.items():
        if label not in by_id or fields[label]['columnType']!='Column' or by_id[label]['bucket_type']=='ACMeasure':
            raise ValueError('Mapped dimension needs a full lookup descriptor: '+label)
        if not isinstance(strategy,dict) or set(strategy) not in ({'ID'},{'Skip'}):
            raise ValueError('Only observed ID and Skip strategies implemented')
        if 'Skip' in strategy:
            if strategy['Skip']!={}: raise ValueError('Skip payload must be empty object')
            retained=skip_support.get(label)
            if retained not in mappings or set(mappings[retained])!={'ID'} or fields[retained]['tableName']!=fields[label]['tableName']:
                raise ValueError('Skip requires an explicitly retained entity key from the same table')
            continue
        key=strategy['ID']
        if key not in fields or fields[key]['columnType']!='Column' or fields[key]['tableName']!=fields[label]['tableName'] or key==label:
            raise ValueError('ID strategy requires a distinct same-table semantic key')
        base=by_id[label];f=fields[key]
        d={**copy.deepcopy(base),'id':key,'column_name':f['columnName'],'name':f['columnName'],
           'custom_name':None,'external_data_type':f['dataType'],'column_type':'Column'}
        if key in by_id:
            if by_id[key]!=d: raise ValueError('Key descriptor already has incompatible role/order')
        else: descriptors.append(d);by_id[key]=d
    return {'mappings':copy.deepcopy(mappings),'pivot':descriptors}

def validate_mapping(state):
    """Audit descriptor completeness independently of construction; not key uniqueness."""
    mappings=state.get('mappings') or {}; descriptors=state.get('pivot',[])
    ids=[d['id'] for d in descriptors]
    if len(ids)!=len(set(ids)): raise ValueError('Duplicate lookup descriptors')
    required={'aggregation_type','bucket_type','column_name','column_type','custom_name','external_data_type',
              'field_parameter_data_type','group_data_type','id','name','order','relationships','source_type'}
    for label,strategy in mappings.items():
        if not isinstance(strategy,dict) or set(strategy) not in ({'ID'},{'Skip'}): raise ValueError('Unknown mapping strategy')
        for key in ([label,strategy['ID']] if 'ID' in strategy else [label]):
            d=next((d for d in descriptors if d['id']==key),None)
            if d is None or not required<=d.keys(): raise ValueError('Incomplete dimension lookup pair: '+key)
    return {'mappingCount':len(mappings),'descriptorCount':len(descriptors),'status':'complete-descriptors',
            'keyUniqueness':'requires-model-query','renamePersistence':'not-tested'}
