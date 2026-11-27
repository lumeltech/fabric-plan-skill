"""Native DataInput/Forecast record constraints; no value/unit changes on repair."""
import math
from decimal import Decimal

DATA_INPUT_KINDS = {
    'Number', 'ShortText', 'LongText', 'SingleSelect', 'MultiSelect',
    'Date', 'Person', 'Checkbox', 'Simulation',
}

def static_bounds(number):
    """Reject fractional static min/max; decimals remain valid defaults/formulas."""
    if not isinstance(number,dict):raise ValueError('Expected numeric input metadata')
    for name in ('min_value','max_value'):
        setting=number.get(name)
        if not isinstance(setting,dict) or 'Static' not in setting:continue
        value=setting['Static']
        if isinstance(value,bool) or not isinstance(value,(int,float,Decimal)):
            raise ValueError(name+' Static requires a whole number')
        if isinstance(value,Decimal):finite=value.is_finite()
        else:finite=isinstance(value,int) or math.isfinite(value)
        if not finite or value!=int(value):
            raise ValueError(name+' Static does not support decimal values; use a resolved measure bound or explicit whole-unit storage with matching formulas/formatting')
    return number

def distribution_default(spec,fallback=False):
    """AverageLeaf permits parent distribution for input/forecast numeric measures."""
    if 'distribute' in spec:
        if not isinstance(spec['distribute'],bool):raise ValueError('distribute must be a Boolean')
        return spec['distribute']
    row=spec.get('aggregation','Sum');column=spec.get('columnAggregation',row)
    return True if 'AverageLeaf' in (row,column) else fallback

def unwrap_measure_type(kind):
    if not isinstance(kind,dict) or len(kind)!=1:
        raise ValueError('Calculated measure_type requires one tagged branch')
    if 'VisualColumn' in kind:
        branch=kind['VisualColumn']
        if not isinstance(branch,dict) or len(branch)!=1 or not set(branch)<= {'DataInput','Formula'}:
            raise ValueError('VisualColumn supports DataInput or Formula')
        return branch
    return kind

def input_permission(value):
    if value in ('Edit','ReadAndEdit'):
        return value
    if isinstance(value,dict) and set(value)=={'BasedOnFormula'} and isinstance(value['BasedOnFormula'],str):
        return value
    raise ValueError('Invalid native allow_input')

def input_metadata(payload):
    if not isinstance(payload,dict):
        raise ValueError('DataInput configuration must be an object')
    required={'id','title','column_type','allow_input','bound_to_filter_context'}
    if not required<=payload.keys():
        raise ValueError('Incomplete DataInput configuration')
    if not isinstance(payload['id'],str) or not isinstance(payload['title'],str):
        raise ValueError('DataInput id/title require strings')
    input_permission(payload['allow_input'])
    if type(payload['bound_to_filter_context']) is not bool:
        raise ValueError('Nested context binding must be Boolean')
    column_type=payload['column_type']
    if not isinstance(column_type,dict) or len(column_type)!=1 or not set(column_type)<=DATA_INPUT_KINDS:
        raise ValueError('DataInput column_type must contain one supported native kind')
    if 'on_change_formula' in payload and payload['on_change_formula'] is not None and not isinstance(payload['on_change_formula'],str):
        raise ValueError('on_change_formula must be a string or null')
    if 'disable_write_access' in payload and type(payload['disable_write_access']) is not bool:
        raise ValueError('disable_write_access must be Boolean')
    from .cube_contract import saved_cube_binding
    cube=saved_cube_binding(payload.get('cube_partition_measure_id'),payload.get('cube_model'))
    if payload.get('cube_partition_measure_id')!=cube.get('cube_partition_measure_id') or payload.get('cube_model')!=cube.get('cube_model'):
        raise ValueError('Invalid saved Cube binding')
    number=column_type.get('Number')
    if number is not None:static_bounds(number)
    return payload

def check_record(record):
    meta=record.get('columnMeta',record)
    raw_kind=meta.get('measure_type')
    if raw_kind is None:return
    kind=unwrap_measure_type(raw_kind)
    if 'DataInput' in kind:
        payload=input_metadata(kind['DataInput'])
        if 'boundToFilterContext' in record:
            expected=10 if payload['bound_to_filter_context'] else 20
            if record['boundToFilterContext']!=expected or isinstance(record['boundToFilterContext'],bool):
                raise ValueError('Context binding encoding mismatch')
    if 'Forecast' in kind:
        from .forecast import validate_forecast_config
        payload=validate_forecast_config(kind['Forecast'])
        if 'boundToFilterContext' in record:
            expected=10 if payload['bound_to_filter_context'] else 20
            if record['boundToFilterContext']!=expected or isinstance(record['boundToFilterContext'],bool):
                raise ValueError('Forecast context binding encoding mismatch')
    if 'Formula' in kind:
        formula=kind['Formula']
        if not isinstance(formula,dict) or not isinstance(formula.get('formula'),str):
            raise ValueError('Formula configuration requires formula text')
        if 'cube_model' in formula:
            raise ValueError('Formula does not support cube_model')
        if 'cube_partition_measure_id' in formula:
            from .cube_contract import saved_cube_binding
            cube=saved_cube_binding(formula['cube_partition_measure_id'])
            if formula.get('cube_partition_measure_id')!=cube.get('cube_partition_measure_id'):
                raise ValueError('Invalid Formula Cube identity')

def check_records(records):
    for record in records:check_record(record)
