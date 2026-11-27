"""Complete Navigator render defaults without changing state overrides or shape profiles.

Disabled icons still need padding: native rendering reads it before visibility.
Only missing text/icon/padding members are filled. Explicit null or malformed
members fail before a write; HOVER/PRESSED/ACTIVE remain partial overrides.
"""
import copy
import math
from decimal import Decimal
from pathlib import Path
from .codec import load
from .paths import ASSETS


def _overlay(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        result[key] = (_overlay(result[key], value)
                       if isinstance(value, dict) and isinstance(result.get(key), dict)
                       else copy.deepcopy(value))
    return result


def _fill(default, current, path):
    if not isinstance(current, dict):
        raise ValueError(path + ' must be an object, not null')
    result = copy.deepcopy(current)
    for key, value in default.items():
        child = path + '.' + key
        if key not in result:
            result[key] = copy.deepcopy(value)
        elif isinstance(value, dict):
            result[key] = _fill(value, result[key], child)
        elif result[key] is None:
            raise ValueError(child + ' cannot be null')
    return result


def _padding(value, path):
    if not isinstance(value, dict):
        raise ValueError(path + ' must be an object')
    for key in ('topPadding', 'bottomPadding', 'leftPadding', 'rightPadding'):
        number = value.get(key)
        if (isinstance(number, bool) or not isinstance(number, (int, float, Decimal))
                or not math.isfinite(number) or number < 0):
            raise ValueError(path + '.' + key + ' must be a finite nonnegative number')
    for key in ('isEnabled', 'isCustomPaddingSize'):
        if not isinstance(value.get(key), bool):
            raise ValueError(path + '.' + key + ' must be boolean')


def complete_defaults(state):
    """Return a copy with complete shared DEFAULT render groups; preserve overrides."""
    result = copy.deepcopy(state)
    try:
        style = result['style']
        shape = style['DEFAULT']['shapeState']
    except (KeyError, TypeError):
        raise ValueError('Navigator requires style.DEFAULT.shapeState') from None
    if not isinstance(shape, dict):
        raise ValueError('Navigator style.DEFAULT.shapeState must be an object')
    seed = load(ASSETS / 'fixtures/navigator-builder-20261112.json')
    base = seed['style']['DEFAULT']['shapeState']
    for group in ('text', 'icon', 'padding'):
        shape[group] = _fill(base[group], shape.get(group, {}), 'style.DEFAULT.shapeState.' + group)
    # Validate effective render state without serializing inherited overrides.
    for name in ('DEFAULT', 'HOVER', 'PRESSED', 'ACTIVE'):
        override = style.get(name, {})
        if not isinstance(override, dict) or not isinstance(override.get('shapeState', {}), dict):
            raise ValueError('Navigator style.' + name + '.shapeState must be an object')
        effective = _overlay(shape, override.get('shapeState', {}))
        for group in ('text', 'icon'):
            if not isinstance(effective.get(group), dict):
                raise ValueError('Navigator style.' + name + '.' + group + ' must be an object')
            _padding(effective[group].get('padding'), 'style.' + name + '.' + group + '.padding')
        _padding(effective.get('padding'), 'style.' + name + '.padding')
    return result


def require_complete_defaults(state):
    """Read-only gate for authored ALM definitions, not proof of dashboard rendering."""
    if complete_defaults(state) != state:
        raise ValueError('Incomplete Navigator defaults; construct with navigator_api.state or navigator_defaults.complete_defaults before saving')
    return True
