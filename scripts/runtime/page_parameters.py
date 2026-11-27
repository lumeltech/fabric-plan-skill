"""Captured entity-level number parameter profile; no formula or security effects."""
import math,re,uuid

def number_parameter(label,technical_name,value=0,*,parameter_id=None,allow_decimal=False,visible=True):
    if not isinstance(label,str) or not label.strip():raise ValueError('Business parameter label required')
    if not isinstance(technical_name,str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',technical_name):
        raise ValueError('Stable technical parameter name required')
    if any(not isinstance(x,bool) for x in (allow_decimal,visible)):raise ValueError('Boolean options required')
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value):raise ValueError('Finite numeric value required')
    if not allow_decimal and int(value)!=value:raise ValueError('Integer parameter cannot start with a fractional value')
    pid=parameter_id or 'CALC_VARIABLE_'+uuid.uuid4().hex
    if not isinstance(pid,str) or not re.fullmatch(r'CALC_VARIABLE_[A-Za-z0-9_]+',pid):raise ValueError('Native parameter identity required')
    return {'entityVariable':{'id':pid,'label':label,'type':'number','scope':'entity',
        'technicalName':technical_name,'description':'','showInViewMode':visible,
        'allowDecimalValues':allow_decimal,'value':value,'defaultValue':value,'showAsPercentage':False,
        'showAsSlider':False,'interval':1,'interfaceType':'input-box'},
      'visualGlobalVariable':{'id':pid,'valueType':'number','label':label,'title':technical_name,
        'showVariable':visible,'description':'','scaling':'none','isPercentage':False,'showSlider':False},
      'calculatedVariable':{'id':pid,'value':value}}
