"""Closed native New-rule branches. Engine mounting remains profile-specific."""
from .identity import native_id
from .input_factories import numeric,boolean,string

def selector(scope,value):
    units={'rows':{'All'},'columns':{'All'},'measures':{'AllMeasures','AllVisualColumns'}}
    variants={'rows':{'Selected','Dimension'},'columns':{'Selected'},'measures':{'SelectedMeasures','SelectedVisualColumns'}}
    if scope not in units:raise ValueError('Rule scope')
    if isinstance(value,str) and value in units[scope]:return value
    if not isinstance(value,dict) or len(value)!=1:raise ValueError('Rule selector union')
    tag,ids=next(iter(value.items()))
    if tag not in variants[scope]:raise ValueError('Selector branch requires an additional contract')
    if tag=='Dimension':return {tag:native_id(ids)}
    if not isinstance(ids,list) or not ids or len(set(ids))!=len(ids):raise ValueError('Nonempty unique selection required')
    return {tag:[native_id(x) for x in ids]}

def lock(all_children=False):return {'Lock':{'all_children':boolean(all_children)}}

def distribute_rows(reference='Equal',dimensions='All',weights=None):
    if dimensions!='All':
        if not isinstance(dimensions,list) or not dimensions or len(set(dimensions))!=len(dimensions):raise ValueError('Selected distribution dimensions')
        dimensions={'SelectedDimensions':[native_id(x) for x in dimensions]}
    if reference in ('Equal','SelfWeight'):
        if weights is not None:raise ValueError('Weights only apply to ManualInput')
        ref=reference
    elif reference=='ManualInput':
        if not isinstance(weights,dict) or not weights:raise ValueError('Manual weights required')
        for k,v in weights.items():native_id(k);numeric(v)
        # This conservative builder requires nonnegative weights and a positive total;
        # it does not claim the engine normalizes/rounds or excludes locked children.
        if any(v<0 for v in weights.values()) or sum(weights.values())<=0:raise ValueError('Manual weights must be nonnegative with positive total')
        ref={'ManualInput':{'weights':dict(weights)}}
    else:raise ValueError('Measure/column distribution needs the full selected reference configuration')
    return {'Distribute':{'operation':{'Row':{'apply_to_dimensions':dimensions,'reference':ref}}}}

def distribute_columns_by_measure(measure_id):
    """Saved UI profile: Column / All dimensions / Measure / Weights from Row Use Self.

    Use Self is represented by an absent source-row member, not SelfMeasure.
    Additional row/period/range configurations require their own confirmed shape.
    This serializes a native reference; it does not calculate or normalize weights.
    """
    return {'Distribute':{'operation':{'Column':{'apply_to_dimensions':'All',
        'reference':{'MeasureIdWithReference':{'measure':{'Measure':native_id(measure_id)}}}}}}}

def distribute_rows_by_measure(measure_id,weights_period='CurrentYear'):
    """Saved Planning UI profile: Row / All dimensions / Measure / CurrentYear.

    The weight period is independent of the outer destination selectors. This
    does not establish runtime lock exclusion or total-conservation behavior.
    """
    if weights_period!='CurrentYear':
        raise ValueError('Captured Row measure profile uses CurrentYear weights')
    return {'Distribute':{'operation':{'Row':{'apply_to_dimensions':'All',
        'reference':{'MeasureIdWithReference':{'measure':{'Measure':native_id(measure_id)},
        'weights_from':{'Period':weights_period}}}}}}}

def _checked_distribution(payload):
    if not isinstance(payload,dict) or set(payload)!={'operation'}:
        raise ValueError('Distribution operation required')
    operation=payload['operation']
    if not isinstance(operation,dict) or len(operation)!=1:
        raise ValueError('Exactly one distribution axis required')
    if 'Column' in operation:
        col=operation['Column']
        if not isinstance(col,dict) or set(col)!={'apply_to_dimensions','reference'} or col['apply_to_dimensions']!='All':
            raise ValueError('Captured Column profile uses All dimensions')
        ref=col['reference']
        if not isinstance(ref,dict) or set(ref)!={'MeasureIdWithReference'}:
            raise ValueError('Captured Column profile requires MeasureIdWithReference')
        config=ref['MeasureIdWithReference']
        if not isinstance(config,dict) or set(config)!={'measure'}:
            raise ValueError('Additional source-row/period/range fields need their own contract; Use Self omits them')
        measure=config['measure']
        if not isinstance(measure,dict) or set(measure)!={'Measure'}:
            raise ValueError('Explicit weighting Measure required; SelfMeasure is a different choice')
        return distribute_columns_by_measure(measure['Measure'])
    if set(operation)!={'Row'}:raise ValueError('Unknown distribution axis')
    row=operation['Row']
    if not isinstance(row,dict) or set(row)!={'apply_to_dimensions','reference'}:raise ValueError('Row distribution fields')
    dims=row['apply_to_dimensions'];ref=row['reference'];weights=None
    if isinstance(dims,dict):
        if set(dims)!={'SelectedDimensions'}:raise ValueError('Dimension applicability union')
        dims=dims['SelectedDimensions']
    if isinstance(ref,dict):
        if set(ref)=={'MeasureIdWithReference'}:
            config=ref['MeasureIdWithReference']
            if dims!='All' or not isinstance(config,dict) or set(config)!={'measure','weights_from'}:
                raise ValueError('Captured Row measure profile fields')
            measure=config['measure'];period=config['weights_from']
            if not isinstance(measure,dict) or set(measure)!={'Measure'} or period!={'Period':'CurrentYear'}:
                raise ValueError('Captured Row requires explicit Measure and CurrentYear weights')
            return distribute_rows_by_measure(measure['Measure'])
        if set(ref)!={'ManualInput'} or set(ref['ManualInput'])!={'weights'}:raise ValueError('Unclosed reference branch')
        weights=ref['ManualInput']['weights'];ref='ManualInput'
    return distribute_rows(ref,dims,weights)

def measure_weighted_rule(logical_id,name,target_measures,weight_measure,measure_ids,*,
                          axis,rows='All',columns='All',disabled=False,weights_period=None):
    """Resolve symbolic keys to native IDs, never labels, positions or another sheet's IDs."""
    if axis not in ('Row','Column'):raise ValueError('Distribution axis must be Row or Column')
    if axis=='Row' and weights_period!='CurrentYear':raise ValueError('Row profile requires explicit CurrentYear weights')
    if axis=='Column' and weights_period is not None:raise ValueError('Captured Column profile omits a weight period')
    if not isinstance(target_measures,list) or not target_measures or len(set(target_measures))!=len(target_measures):
        raise ValueError('Nonempty unique target measure keys required')
    def resolve(key):
        if key not in measure_ids:raise ValueError('Unresolved rule measure '+str(key))
        return native_id(measure_ids[key])
    targets=[resolve(k) for k in target_measures];weight=resolve(weight_measure)
    distribution=distribute_rows_by_measure(weight,weights_period) if axis=='Row' else distribute_columns_by_measure(weight)
    return new_rule(logical_id,name,distribution,
        rows=rows,columns=columns,measures={'SelectedMeasures':targets},disabled=disabled)

def bound(value):
    if not isinstance(value,dict) or len(value)!=1:raise ValueError('Bound union')
    tag,config=next(iter(value.items()))
    if tag not in ('Static','Measure','Variable') or not isinstance(config,dict):raise ValueError('Bound branch')
    allowed={'Static':{'value','is_exclusive'},'Measure':{'measure','is_exclusive'},'Variable':{'value','variable','is_exclusive'}}[tag]
    if set(config)-allowed:raise ValueError('Unknown bound field')
    out=dict(config)
    if 'is_exclusive' in out and out['is_exclusive'] is not None:boolean(out['is_exclusive'])
    if tag=='Static':
        if out.get('value') is not None:numeric(out['value'])
    elif tag=='Measure':native_id(out['measure'])
    else:numeric(out['value']);string(out['variable'])
    return {tag:out}

def new_rule(logical_id,name,rule_type,*,rows='All',columns='All',measures='AllMeasures',disabled=False):
    if not isinstance(rule_type,dict) or len(rule_type)!=1 or next(iter(rule_type)) not in ('Lock','Distribute','MinMax'):raise ValueError('Rule type')
    tag,p=next(iter(rule_type.items()))
    if tag=='Lock':
        if set(p)!={'all_children'}:raise ValueError('Lock fields')
        checked=lock(p['all_children'])
    elif tag=='MinMax':
        if set(p)!={'min','max'}:raise ValueError('MinMax requires min and max configs')
        checked=min_max(p['min'],p['max'])
    else:
        checked=_checked_distribution(p)
    return {'ruleOperation':{'New':{'rule_id':native_id(logical_id),'name':string(name),'rule_type':checked,
      'rows':selector('rows',rows),'columns':selector('columns',columns),'measures':selector('measures',measures),'is_disabled':boolean(disabled)}}}

def min_max(minimum,maximum):
    lo=bound(minimum);hi=bound(maximum)
    blank=lambda x: 'Static' in x and x['Static'].get('value') is None
    if blank(lo) and blank(hi):raise ValueError('At least one bound must be configured')
    if 'Static' in lo and 'Static' in hi and not blank(lo) and not blank(hi):
        a=lo['Static']['value'];b=hi['Static']['value']
        if a>b or (a==b and (lo['Static'].get('is_exclusive') or hi['Static'].get('is_exclusive'))):raise ValueError('Empty allowed bound interval')
    return {'MinMax':{'min':lo,'max':hi}}

def verify_saved_rule(payload,saved_rules):
    """Compare semantic rule fields; resolve persisted ID separately from logical rule_id.

    Accept a current visualState.data_input_rules list or the selected engine's
    unwrapped rules list. Readback does not prove triggers, scope or allocation results.
    """
    if not isinstance(payload,dict) or set(payload)!={'ruleOperation'} or set(payload['ruleOperation'])!={'New'}:
        raise ValueError('New rule payload required')
    requested=payload['ruleOperation']['New']
    if set(requested)!={'rule_id','name','rule_type','rows','columns','measures','is_disabled'}:
        raise ValueError('New rule fields')
    expected=new_rule(requested['rule_id'],requested['name'],requested['rule_type'],rows=requested['rows'],
        columns=requested['columns'],measures=requested['measures'],disabled=requested['is_disabled'])['ruleOperation']['New']
    found=[r for r in saved_rules if str(r.get('rule_id'))==expected['rule_id']]
    if len(found)!=1:raise ValueError('Missing or ambiguous logical rule_id in saved rules')
    saved=found[0]
    for key,value in expected.items():
        if saved.get(key)!=value:raise ValueError('Saved rule mismatch: '+key)
    return {'status':'saved-definition-matched','ruleId':expected['rule_id'],
        'persistedId':native_id(saved['id']),'execution':'not-tested'}
