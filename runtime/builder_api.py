"""Offline validation of supplied column records."""
from .readback import contains

def column_matches(actual,expected):
    contains(actual['columnMeta'],expected['columnMeta'])
    # Writes use columnType; OneLake catalog records can expose dataInputType.
    # Resolve only this readback alias, without relaxing type or metadata checks.
    actual_type=actual.get('columnType',actual.get('dataInputType'))
    if 'columnType' in actual and 'dataInputType' in actual and actual['columnType']!=actual['dataInputType']:
        raise ValueError('Conflicting native column type aliases')
    if 'columnType' in expected and actual_type!=expected['columnType']:
        raise ValueError('Native column readback mismatch: columnType')
    # The enclosing native context flag is independent of the inner Boolean.
    for key in ('measureGuid','name','boundToFilterContext'):
        if key in expected and actual.get(key)!=expected[key]:raise ValueError('Native column readback mismatch: '+key)
