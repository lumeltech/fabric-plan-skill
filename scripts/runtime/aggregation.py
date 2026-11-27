"""Native JetStream aggregation methods used by visualState registration."""
from .identity import native_id

SCALAR_METHODS = {
    'Sum', 'Formula', 'Min', 'Max', 'Average', 'AverageLeaf',
    'StandardDeviation', 'VisibleRounding', 'First', 'Last', 'None',
    'Earliest', 'Latest', 'Median', 'Variance', 'DistinctCount', 'Count',
    'Subtraction', 'Product', 'Division', 'AverageExclusiveZero', 'VisualSum',
}
WEIGHTED_METHODS = {'WeightedAverage', 'WeightedAverageRow'}


def resolve(value, measure_ids=None):
    """Resolve symbolic measure weights to the exact native aggregation wire shape."""
    if isinstance(value, str):
        if value not in SCALAR_METHODS:
            raise ValueError('Unsupported aggregation: ' + value)
        return value
    if not isinstance(value, dict) or len(value) != 1:
        raise ValueError('Aggregation must be a canonical string or one tagged weighted method')
    method, reference = next(iter(value.items()))
    if method not in WEIGHTED_METHODS or not isinstance(reference, str):
        raise ValueError('Weighted aggregation requires a string reference')
    if method == 'WeightedAverage' and measure_ids and reference in measure_ids:
        reference = measure_ids[reference]
    if method == 'WeightedAverageRow':
        return {method: native_id(reference)}
    return {method: native_id(reference)}


def validate_config(config):
    """Validate every authored/saved AggregationConfig measure scope."""
    if not isinstance(config, dict):
        raise ValueError('aggregation_config must be an object')
    allowed = {
        'measure_aggregation',
        'row_measure_aggregation',
        'row_member_measure_aggregation',
        'row_dimension_aggregation',
    }
    for key in allowed:
        if key in config and not isinstance(config[key], dict):
            raise ValueError('aggregation_config.' + key + ' must be an object')
    for method in config.get('row_dimension_aggregation', {}).values():
        resolve(method)
    for by_owner in ('measure_aggregation',):
        for pair in config.get(by_owner, {}).values():
            if not isinstance(pair, dict) or set(pair) - {'row', 'column'}:
                raise ValueError('Measure aggregation requires row/column scope')
            for method in pair.values():
                resolve(method)
    for scope in ('row_measure_aggregation', 'row_member_measure_aggregation'):
        for member_map in config.get(scope, {}).values():
            if not isinstance(member_map, dict):
                raise ValueError(scope + ' entries must be objects')
            for pair in member_map.values():
                if not isinstance(pair, dict) or set(pair) - {'row', 'column'}:
                    raise ValueError(scope + ' requires row/column scopes')
                for method in pair.values():
                    resolve(method)
    return True
