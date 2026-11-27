"""Current native Cube request contract used by the redesigned breakdown flow."""
import copy


def _string(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + ' requires a non-empty string')
    return value


def _identifier_map(value, field):
    if not isinstance(value, dict):
        raise ValueError(field + ' must be an object')
    result = {}
    for key, label in value.items():
        _string(key, field + ' key')
        result[key] = _string(label, field + ' label')
    return result


def dimension_record(value, field, *, lookup=False):
    """A checked copy of one cube dimension; a lookup dimension cannot carry lookups."""
    allowed = {'id', 'label', 'dataType', 'type', 'distinctValueCount'}
    if not lookup:
        allowed.add('lookups')
    if not isinstance(value, dict) or not {'id', 'label', 'dataType', 'type'} <= set(value) or set(value) - allowed:
        raise ValueError(field + ' has an invalid dimension contract')
    result = {key: copy.deepcopy(value[key]) for key in value if key != 'lookups'}
    for key in ('id', 'label', 'dataType', 'type'):
        _string(result[key], field + '.' + key)
    count = result.get('distinctValueCount')
    if count is not None and (isinstance(count, bool) or not isinstance(count, int) or count < 0):
        raise ValueError(field + '.distinctValueCount requires null or a nonnegative integer')
    if 'lookups' in value:
        if not isinstance(value['lookups'], list):
            raise ValueError(field + '.lookups must be an array')
        result['lookups'] = [
            dimension_record(item, field + '.lookups/' + str(index), lookup=True)
            for index, item in enumerate(value['lookups'])
        ]
    return result


def reference_measure(value, field):
    """A checked copy of one cube measure reference with exactly its six members."""
    required = {'id', 'label', 'type', 'isNative', 'aggregationType', 'dataType'}
    if not isinstance(value, dict) or set(value) != required:
        raise ValueError(field + ' has an invalid reference-measure contract')
    result = copy.deepcopy(value)
    for key in ('id', 'label', 'type', 'aggregationType', 'dataType'):
        _string(result[key], field + '.' + key)
    if type(result['isNative']) is not bool:
        raise ValueError(field + '.isNative must be Boolean')
    return result


def _partition(value, field):
    if not isinstance(value, dict) or set(value) != {'name', 'dataAssignment'}:
        raise ValueError(field + ' has an invalid partition contract')
    assignment = value['dataAssignment']
    if not isinstance(assignment, dict) or set(assignment) != {'dimensions', 'timeDimensions'}:
        raise ValueError(field + '.dataAssignment must contain dimensions and timeDimensions')
    if not isinstance(assignment['dimensions'], list) or not isinstance(assignment['timeDimensions'], list):
        raise ValueError(field + '.dataAssignment dimensions must be arrays')
    return {
        'name': _string(value['name'], field + '.name'),
        'dataAssignment': {
            'dimensions': [
                dimension_record(item, field + '.dimensions/' + str(index))
                for index, item in enumerate(assignment['dimensions'])
            ],
            'timeDimensions': [
                dimension_record(item, field + '.timeDimensions/' + str(index), lookup=True)
                for index, item in enumerate(assignment['timeDimensions'])
            ],
        },
    }


def multi_dimension_settings(
    referenceMeasures,
    newPartitions,
    existingPartitions,
    visualMeasureIdMapping=None,
    sourceMeasureId=None,
    nativeMeasureMapping=None,
    cubeModel=None,
):
    """Validate and copy a current native Cube creation-settings payload."""
    if not all(isinstance(value, list) for value in (referenceMeasures, newPartitions, existingPartitions)):
        raise ValueError('Cube references and partitions must be arrays')
    result = {
        'referenceMeasures': [
            reference_measure(value, 'referenceMeasures/' + str(index))
            for index, value in enumerate(referenceMeasures)
        ],
        'newPartitions': [
            _partition(value, 'newPartitions/' + str(index))
            for index, value in enumerate(newPartitions)
        ],
        'existingPartitions': [
            _partition(value, 'existingPartitions/' + str(index))
            for index, value in enumerate(existingPartitions)
        ],
    }
    if visualMeasureIdMapping is not None:
        result['visualMeasureIdMapping'] = _identifier_map(visualMeasureIdMapping, 'visualMeasureIdMapping')
    if sourceMeasureId is not None:
        result['sourceMeasureId'] = _string(sourceMeasureId, 'sourceMeasureId')
    if nativeMeasureMapping is not None:
        if not isinstance(nativeMeasureMapping, list):
            raise ValueError('nativeMeasureMapping must be an array')
        result['nativeMeasureMapping'] = [
            reference_measure(value, 'nativeMeasureMapping/' + str(index))
            for index, value in enumerate(nativeMeasureMapping)
        ]
    if cubeModel is not None:
        if cubeModel != 'DYNAMIC':
            raise ValueError('cubeModel supports the native DYNAMIC value only')
        result['cubeModel'] = cubeModel
    return result


def saved_cube_binding(cube_partition_measure_id=None, cube_model=None):
    """Validate optional fields preserved on saved DataInput/Forecast records."""
    if cube_partition_measure_id is None and cube_model is None:
        return {}
    if cube_partition_measure_id is None:
        raise ValueError('cube_model requires an actual cube_partition_measure_id')
    result = {'cube_partition_measure_id': _string(
        cube_partition_measure_id, 'cube_partition_measure_id'
    )}
    if cube_model is not None:
        if cube_model != 'DYNAMIC':
            raise ValueError('cube_model supports the native DYNAMIC value only')
        result['cube_model'] = cube_model
    return result
