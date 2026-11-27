"""Local From Sheets, conditional formatting and comparison chart constructors."""
import copy
from .codec import dumps
from .identity import xxh3,native_id

def from_sheet_assignment(source,source_visual,source_name,label=None,bucket='ameasure',order=1):
    """source is a current /datainput/column/ record, NOT an ALM record.

    Fabric SQL uses the source row id; OneLake can use source measureGuid when
    the row id is absent. Runtime visual IDs differ from ALM visual GUIDs.
    This selected constructor supports numeric SUM at same/subset grain.
    """
    from .measure_bindings import record_kind,sheet_column_id
    if record_kind(source) not in ('DataInput','Formula','Forecast'):
        raise ValueError('Native companions are not From Sheets outputs; resolve the original source assignment')
    if source.get('visualId') is not None and str(source['visualId'])!=str(source_visual):
        raise ValueError('Source column belongs to a different visual')
    if isinstance(source_visual,bool) or not str(source_visual).isdecimal():
        raise ValueError('Resolve native source column and visual IDs before linking')
    native_id(str(source_visual));source_id=sheet_column_id(source)
    if source['columnMeta'].get('data_type')!='Number':raise ValueError('SUM requires numeric source')
    if bucket not in ('ameasure','AC','PY'):raise ValueError('Selected supported destination bucket required')
    mid=str(xxh3('SUM__'+source_id));label=label or source['name']
    return {'aggregationType':'sum','bucketId':bucket,'columnName':source['name'],
        'columnType':'Column','customName':label,'dataRoleType':'Measure','dataType':'Double',
        'formatString':'#,0.00','id':source_id,'sourceId':source_id,
        'measureGuid':mid,'sourceType':'Visual','tableName':source_name,'visualId':str(source_visual),
        'name':label,'order':order,'isFlatHierarchy':False,'isRenamed':True}

def negative_variance_rule(measure_id,label='Variance',rule_name=None):
    native_id(measure_id)
    from .matrix_formatting import conditional_rule
    return conditional_rule(_negative_request(measure_id,label,rule_name),
        {'measure':{measure_id},'labels':{measure_id:label},'rowDimensionOrder':[]})

def _negative_request(measure_id,label,rule_name=None):
    return {'id':rule_name or 'negative_variance_'+measure_id,'label':label+' below zero',
        'target':measure_id,'test':measure_id,'operator':'<','threshold':0,
        'rowScope':'both','columnScope':'both','excludeRowTotal':False,'excludeColumnTotal':False,
        'appearance':{'textColor':'#B42318','background':'#FEE4E2','bold':True}}

def apply_negative_variance(properties,measure_id,label='Variance'):
    from .matrix_formatting import compile_formatting
    out=copy.deepcopy(properties)
    out['visualState']=compile_formatting(out['visualState'],{'rules':[_negative_request(measure_id,label)]})['state']
    return out

def variance_config(*, integrated=True):
    if integrated:
        from .integrated_variance import integrated_variance_config
        return integrated_variance_config()
    def item(role,chart,typ,order,axis,visible):
        return {'role':role,'isVisible':visible,'chartIsVisible':visible,'enable':visible,
            'chart':chart,'type':typ,'order':order,'calcFormula':'','isWaterfallMeasure':False,
            'yAxis':axis,'isTrellis':False,'dimension':None,'legendMeasureInfoText':''}
    return {'instanceId':'DEFAULT_VISUAL_INSTANCE','config':[
        item('\u0394PY%','variancePin','RELATIVE_VARIANCE',0,'none',False),
        item('\u0394PY','varianceBar','ABSOLUTE_VARIANCE',1,'none',True),
        item('AC','groupedBar','ACTUAL',0,'yAxis1',True),item('PY','groupedBar','ACTUAL',1,'yAxis1',True)]}

def comparison_chart(properties,forecast_assignment,actuals_assignment, *, integrated=True):
    """Configure a type-50 comparison, integrated variance by default.

    AC and PY are chart comparison roles, independent of source namespace.
    Native AC-PY compares the supplied left and right measures. Keep their actual
    business captions and typed source IDs. Ordinary cards are reconciled to the
    surviving fields so an old binding cannot linger under the same caption.
    """
    out=copy.deepcopy(properties)
    if out.get('visualType')!=50:raise ValueError('Use an ANALYTICS_PLUS column chart')
    ac=copy.deepcopy(forecast_assignment);ac.update(bucketId='AC',order=0)
    py=copy.deepcopy(actuals_assignment);py.update(bucketId='PY',order=0)
    out['pivotAssignments']=[a for a in out['pivotAssignments'] if a.get('dataRoleType')!='Measure']+[ac,py]
    if integrated:
        from .integrated_variance import apply_integrated_variance
        out=apply_integrated_variance(out)
    else:
        out['visualState']['hiddenProperties_!!!_measureConfig']=dumps(variance_config(integrated=False)).strip()
    from .chart_filters import reconcile_chart_filters
    reconcile_chart_filters(out)
    return out
