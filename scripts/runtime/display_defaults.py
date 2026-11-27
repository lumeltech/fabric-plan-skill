"""Unrestricted measure cards and reference-derived Matrix Auto scaling.

No network or data mutations. Assignments, storage, formulas and selections on
retained dimension/context cards are never rewritten by these helpers.
"""
import copy
from .matrix_formatting import SCOPES

NUMERIC={'Number','Int64','Double','Decimal'}

def numeric_measure_ids(properties, records=()):
    """Resolve numeric managed measures by typed assignment/record, never label."""
    assignments={str(a['measureGuid']):a for a in properties.get('pivotAssignments',[])
                 if a.get('dataRoleType')=='Measure' and a.get('measureGuid') is not None}
    metadata={str(c['measureGuid']):c.get('columnMeta',{}) for c in records}
    result=[]
    for m in properties['visualState'].get('manage_measures',[]):
        mid=m['id'];a=assignments.get(mid)
        typ=a.get('dataType') if a is not None else metadata.get(mid,{}).get('data_type')
        if typ in NUMERIC:result.append(mid)
    return result

def auto_number_formatting(state, measure_ids, *, overwrite=False):
    """Add numeric property 13='auto', preserving every other format property.

    Default authoring preserves explicit existing per-measure scaling. A scoped
    user-requested reset passes overwrite=True. This is not a global mode switch;
    global settings and deliberate cell/row/column overrides are kept untouched.
    """
    out=copy.deepcopy(state);ids=list(dict.fromkeys(measure_ids))
    known={m['id'] for m in out.get('manage_measures',[])}
    if any(not isinstance(mid,str) or mid not in known for mid in ids):
        raise ValueError('Resolve numeric managed measure identities before formatting')
    fc=out.setdefault('formatConfig',{});measure=fc.setdefault('measure',{})
    orders=[e['order'] for scope in SCOPES for entries in fc.get(scope,{}).values() for e in entries]
    size=fc.get('formatSize',0)
    if any(type(n) is not int or n<0 for n in [size,*orders]):raise ValueError('Invalid format operation order')
    next_order=max([size,*[n+1 for n in orders]])
    for mid in ids:
        entries=measure.setdefault(mid,[])
        scalings=sorted((e for e in entries if '13' in e.get('format',{})),key=lambda e:e['order'])
        if scalings and (not overwrite or scalings[-1]['format']['13']=='auto'):continue
        entries.append({'format':{'13':'auto'},'order':next_order});next_order+=1
    fc['formatSize']=next_order;fc.setdefault('__lastHouseKeepedSize',0)
    return out

def measure_filter_card(registration):
    """Classify by role, not numeric data type (Year remains a dimension)."""
    if registration.get('isContextDimension'):return False
    return bool(registration.get('isDefaultMeasure') or registration.get('isDaxMeasure') or
                any(a.get('dataRoleType')=='Measure' for a in registration.get('pivotAssignments',[])))

def clear_measure_filter_selections(properties):
    """Explicit reset to All. Keep cards and their exact source assignments.

    Clear predicates only when authorized. Keep hidden Context, embedded scope,
    dimension selections, pane configuration and ALL value/comparison bindings.
    """
    out=copy.deepcopy(properties)
    for reg in out.get('superFilterAssignments',[]):
        if not measure_filter_card(reg):continue
        reg['filter']=[]
        cfg=reg.setdefault('configuration',{});cfg['selectAll']=True
        cfg.pop('selectAllState',None)
        if 'alphaNumericValues' in cfg:cfg['alphaNumericValues']={'minValue':None,'maxValue':None,'equalValue':None}
        if 'measureFilter' in cfg:cfg['measureFilter']={'minValue':None,'maxValue':None}
        if 'selectedPreset' in cfg:cfg['selectedPreset']=[]
    return out

def planning_display_defaults(properties, records=(), *, overwrite_scaling=False, clear_measure_selections=False):
    out=clear_measure_filter_selections(properties) if clear_measure_selections else copy.deepcopy(properties)
    mids=numeric_measure_ids(out,records)
    out['visualState']=auto_number_formatting(out['visualState'],mids,overwrite=overwrite_scaling)
    return out
