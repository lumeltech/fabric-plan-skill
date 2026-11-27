"""Planning column presentation with current, grain-specific identities.

Expansion-only recovery was confirmed through a saved-definition observation on 2026-11-14.
Sizing, explicit total defaults and native measure cards are additional requested
defaults, not independently proven causes of that disappearing-column issue.
"""
import copy
from .chart_filters import chart_field_filter, _key, NUMERIC

LAYOUT_DEFAULTS={'tableWidth':80,'chartWidth':150,'labelWidth':120,
    'isResponsive':False,'bulletWidth':300,'maximumChartWidth':200,
    'isMaximumChartWidthAllowed':False,'preferedWidthSelection':'measure'}

def expand_columns(properties):
    """Explicit expansion repair: replace only the two expansion branches."""
    out=copy.deepcopy(properties);vs=out['visualState'];dims=vs.get('columnDimensions',[])
    if not dims:return out
    ids=[d['id'] for d in dims]
    if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):
        raise ValueError('Resolve unique current column-dimension IDs')
    vs['columnExpandCollapse']={'columnExpandCollapse':{},'expandColumnToLastLevel':True}
    vs.setdefault('tableState',{})['columnHierarchyLevel']={i:{'collapsed':'Expanded'} for i in ids}
    return out

def ensure_assigned_measure_filters(properties):
    """Visible assigned Values cards, initialized to All (no predicate).

    Supports current numeric PowerBI, Visual/From Sheets and InfoBridge bindings.
    Preserve explicit existing cards and selections; never copy grouping filters.
    """
    fields=properties.get('pivotAssignments',[])
    groups=[a for a in fields if a.get('dataRoleType')=='Grouping' and a.get('bucketId') in ('rows','columns')]
    regs=properties.setdefault('superFilterAssignments',[])
    key=_key
    present={key(a) for r in regs if r.get('isDefaultMeasure') and not r.get('isContextDimension')
             for a in r.get('pivotAssignments',[]) if a.get('dataRoleType')=='Measure'}
    for a in fields:
        if a.get('dataRoleType')=='Measure' and a.get('dataType') in NUMERIC and key(a) not in present:
            reg=chart_field_filter(a,groups);reg['bucketId']=a['bucketId']
            regs.append(reg);present.add(key(a))
    return properties


def ensure_native_measure_filters(properties):
    """Backward-compatible name; all assigned numeric Values sources supported."""
    return ensure_assigned_measure_filters(properties)

def apply_column_presentation(properties, *, expansion=True, sizing=True,
                              default_column_totals=True, native_measure_filters=True):
    """Five-item recipe. Existing-report use requires the requested change scope.

Keeps measure definitions/storage/formatting, existing sizes and active filters.
Missing column positions use the current authoring defaults (GT Left, subtotal
null). Existing explicit positions, including null/OFF, are preserved.
"""
    out=expand_columns(properties) if expansion else copy.deepcopy(properties)
    vs=out['visualState']
    if sizing:
        sizes=vs.setdefault('layoutSizes',{})
        for key,value in LAYOUT_DEFAULTS.items():sizes.setdefault(key,value)
    if default_column_totals:
        from .roll_forward import TOTALS_DEFAULTS
        totals=vs.setdefault('totals_config',{})
        for key in ('column_grand_total','column_sub_total'):
            totals.setdefault(key,TOTALS_DEFAULTS[key])
    if native_measure_filters:ensure_native_measure_filters(out)
    return out
