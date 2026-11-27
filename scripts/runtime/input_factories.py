"""Native input factories from the supplied standalone implementation contracts.

These produce native create payloads, not assumed ALM DataInput equivalents.
Unresolved identity/context variants are explicit arguments, never guessed.
"""
import copy,math
from decimal import Decimal
from .identity import native_id
from .construct import expression

KINDS={'Number':(6,'Number'),'ShortText':(1,'Text'),'LongText':(101,'Text'),
       'SingleSelect':(2,'Text'),'MultiSelect':(3,'Text'),'Date':(4,'DateTime'),
       'Person':(7,'Text'),'Checkbox':(11,'Boolean'),'Simulation':(25,'Number')}
DATE_FORMATS={'DEFAULT_LOCALE','MONTH_DD_YYYY','DD_MONTH_YYYY','DD_FULLMONTH_YYYY',
 'DD_MM_YYYY_SLASH','DD_MM_YYYY_HYPHEN','DD_MM_YY_SLASH','DD_MM_YY_HYPHEN',
 'MM_DD_YYYY_SLASH','MM_DD_YYYY_HYPHEN','MM_DD_YY_SLASH','MM_DD_YY_HYPHEN','DDDD_MMMM_D_YYYY'}

def boolean(v):
    if not isinstance(v,bool): raise ValueError('Expected Boolean')
    return v
def numeric(v):
    if isinstance(v,bool) or not isinstance(v,(int,float,Decimal)): raise ValueError('Expected finite number')
    if isinstance(v,Decimal) and not v.is_finite() or isinstance(v,float) and not math.isfinite(v): raise ValueError('Expected finite number')
    return v
def integer(v,lo,hi):
    if isinstance(v,bool) or not isinstance(v,int) or not lo<=v<=hi: raise ValueError('Integer outside native range')
    return v
def string(v):
    if not isinstance(v,str): raise ValueError('Expected string')
    return v
def fields(obj,allowed):
    if not isinstance(obj,dict) or set(obj)-set(allowed): raise ValueError('Unknown/invalid native metadata field')
def resolve(key,ids):
    if key not in ids: raise ValueError('Unresolved symbolic reference: '+str(key))
    return native_id(ids[key])
def option(v):
    if not isinstance(v,dict) or set(v)!={'display_name','value','color','icon','order'}: raise ValueError('Complete SelectOption required')
    for k in ('display_name','value','color','icon'): string(v[k])
    integer(v['order'],-2**31,2**31-1);return copy.deepcopy(v)

def advanced_style(v):
    if v is None:return None
    fields(v,('visual_identifier','columns'))
    for key,value in v.items():
        if value is not None:string(value)
    return copy.deepcopy(v)

def default_value(value,kind,measures,dimensions):
    if value is None:return None
    if not isinstance(value,dict) or len(value)!=1:raise ValueError('Single tagged default required')
    tag,v=next(iter(value.items()))
    if tag=='Measure':return {tag:resolve(v,measures)}
    if tag=='Dimension' and kind!='Number':return {tag:resolve(v,dimensions)}
    if tag!='Static':raise ValueError('Unsupported default branch')
    if kind=='Number':v=numeric(v)
    elif kind=='Checkbox':v=boolean(v)
    elif kind in ('SingleSelect','MultiSelect'):v=option(v)
    else:v=string(v)
    return {'Static':v}

def metadata(kind,settings,measures=None,dimensions=None):
    measures=measures or {};dimensions=dimensions or {};s=copy.deepcopy(settings)
    if kind not in KINDS:raise ValueError('Input kind not closed by this factory')
    if kind=='Number':
        fields(s,('min_value','max_value','default_value','distribute_parent_value_to_children'))
        out={k:default_value(s.get(k),kind,measures,dimensions) for k in ('min_value','max_value','default_value')}
        out['distribute_parent_value_to_children']=boolean(s.get('distribute_parent_value_to_children',False))
        from .input_constraints import static_bounds
        static_bounds(out)
        low=out['min_value'];high=out['max_value'];value=out['default_value']
        if low and high and 'Static' in low and 'Static' in high and low['Static']>high['Static']:raise ValueError('Inverted bounds')
        if value and 'Static' in value:
            if low and 'Static' in low and value['Static']<low['Static']:raise ValueError('Default below minimum')
            if high and 'Static' in high and value['Static']>high['Static']:raise ValueError('Default above maximum')
        return out
    if kind in ('ShortText','LongText'):
        fields(s,('default_value','allow_entry_on_totals_or_subtotals','prevent_null','field_validation','minimum_length','maximum_length','roll_up_delimiter'))
        val=s.get('field_validation','AnyValue')
        if isinstance(val,dict):
            if set(val)!={'Custom'}:raise ValueError('Text validation tag')
            string(val['Custom'])
        elif val not in ('AnyValue','Numeric','NonNumeric','AlphaNumeric','Email','Url'):raise ValueError('Text validation kind')
        low=s.get('minimum_length');high=s.get('maximum_length')
        for v in (low,high):
            if v is not None:integer(v,0,2**32-1)
        if low is not None and high is not None and low>high:raise ValueError('Text length bounds inverted')
        out={'default_value':default_value(s.get('default_value'),kind,measures,dimensions),
             'allow_entry_on_totals_or_subtotals':boolean(s.get('allow_entry_on_totals_or_subtotals',False)),
             'prevent_null':None if s.get('prevent_null') is None else boolean(s['prevent_null']),
             'field_validation':val,'minimum_length':low,'maximum_length':high}
        if s.get('roll_up_delimiter') is not None:
            if s['roll_up_delimiter'] not in (',','|'):raise ValueError('Native text delimiter')
            out['roll_up_delimiter']=s['roll_up_delimiter']
        d=out['default_value']
        if d and 'Static' in d and low is not None and len(d['Static'].encode('utf-8'))<low:
            raise ValueError('Text default below minimum UTF-8 byte bound')
        if d and 'Static' in d and len(d['Static'].encode('utf-8'))>(high if high is not None else 255 if kind=='ShortText' else 25000):
            raise ValueError('Text default exceeds native UTF-8 byte bound')
        return out
    if kind in ('SingleSelect','MultiSelect'):
        fields(s,('options_source','option_style','advanced','default_value','allow_user_to_add_new_option','allow_entry_on_totals_or_subtotals','prevent_null','icon_position'))
        source=s.get('options_source',{'Static':[]})
        if source!='Lookup':
            if not isinstance(source,dict) or set(source)!={'Static'} or not isinstance(source['Static'],list):raise ValueError('Select options source')
            source={'Static':[option(x) for x in source['Static']]}
            if len({x['value'] for x in source['Static']})!=len(source['Static']):raise ValueError('Duplicate stable option value')
        style=s.get('option_style','Chip')
        if style not in ('Chip','Arrow','PlainText'):raise ValueError('Select style')
        out={'options':[],'options_source':source,'option_style':style,'advanced':advanced_style(s.get('advanced')),
          'default_value':default_value(s.get('default_value'),kind,measures,dimensions),
          'allow_user_to_add_new_option':boolean(s.get('allow_user_to_add_new_option',False)),
          'allow_entry_on_totals_or_subtotals':boolean(s.get('allow_entry_on_totals_or_subtotals',False)),
          'prevent_null':None if s.get('prevent_null') is None else boolean(s['prevent_null']),
          'icon_position':None if s.get('icon_position') is None else string(s['icon_position'])}
        d=out['default_value']
        if isinstance(source,dict) and d and 'Static' in d and not any(d['Static']==x for x in source['Static']):raise ValueError('Default option is not in stable option catalog')
        return out
    if kind=='Date':
        fields(s,('format','min_date','max_date','allow_entry_on_totals_or_subtotals','default_value'))
        fmt=s.get('format','DEFAULT_LOCALE')
        if fmt not in DATE_FORMATS:raise ValueError('Native Date format required')
        return {'format':fmt,'min_date':None if s.get('min_date') is None else string(s['min_date']),
          'max_date':None if s.get('max_date') is None else string(s['max_date']),
          'allow_entry_on_totals_or_subtotals':boolean(s.get('allow_entry_on_totals_or_subtotals',False)),
          'default_value':default_value(s.get('default_value'),kind,measures,dimensions)}
    if kind=='Person':
        fields(s,('allow_entry_on_totals_or_subtotals',));return {'allow_entry_on_totals_or_subtotals':boolean(s.get('allow_entry_on_totals_or_subtotals',False))}
    if kind=='Checkbox':
        fields(s,('default_value','edit_on_total'));return {'default_value':default_value(s.get('default_value'),kind,measures,dimensions),
          'edit_on_total':None if s.get('edit_on_total') is None else boolean(s['edit_on_total'])}
    if kind=='Simulation':
        required={'source_measure_id','simulation_slider','simulation_range','distribute_parent_value_to_children','simulation_value_align','variance_formatting_style'}
        fields(s,required)
        if set(s)!=required:raise ValueError('Explicit Simulation metadata/profile required')
        return {'source_measure_id':resolve(s['source_measure_id'],measures),'simulation_slider':boolean(s['simulation_slider']),
          'simulation_range':integer(s['simulation_range'],-2**31,2**31-1),
          'distribute_parent_value_to_children':boolean(s['distribute_parent_value_to_children']),
          'simulation_value_align':string(s['simulation_value_align']),'variance_formatting_style':string(s['variance_formatting_style'])}

def input_create(measure_id,label,kind,settings,configuration_id,*,measures=None,dimensions=None,
                 visual_column=False,context_bound=True,context_encoding='native-10-20',allow_input='ReadAndEdit',on_change=None,
                 cube_partition_measure_id=None,cube_model=None):
    mid=native_id(measure_id);string(label);string(configuration_id);boolean(visual_column);boolean(context_bound)
    measures=measures or {};dimensions=dimensions or {}
    from .input_policy import allow_input as resolve_allow_input
    allow_input=resolve_allow_input(allow_input,measures)
    if kind not in KINDS:raise ValueError('Input kind not closed by this factory')
    code,typ=KINDS[kind]
    payload={'id':configuration_id,'title':label,'column_type':{kind:metadata(kind,settings,measures,dimensions)},
             'allow_input':allow_input,'bound_to_filter_context':context_bound}
    from .cube_contract import saved_cube_binding
    payload.update(saved_cube_binding(cube_partition_measure_id,cube_model))
    if on_change is not None:payload['on_change_formula']=expression(on_change,measures)
    mt={'DataInput':payload}
    if visual_column:mt={'VisualColumn':mt}
    if context_encoding=='native-10-20':bound=10 if context_bound else 20
    elif context_encoding=='legacy-0-1':raise ValueError('Legacy encoding polarity is not established; resolve writer/validator before creating')
    else:raise ValueError('Unknown input context encoding')
    return {'measureGuid':mid,'columnType':code,'name':label,'columnMeta':{'id':mid,'label':label,'measure_type':mt,'data_type':typ},'boundToFilterContext':bound}

def formula_create(measure_id,label,formula,measures,visual_column=False,data_type='Number',
                   cube_partition_measure_id=None):
    codes={'Text':1,'Number':6,'Boolean':11,'DateTime':4}
    if data_type not in codes:raise ValueError('Native formula data type')
    boolean(visual_column);mid=native_id(measure_id)
    payload={'formula':expression(formula,measures)}
    if cube_partition_measure_id is not None:
        from .cube_contract import saved_cube_binding
        payload.update(saved_cube_binding(cube_partition_measure_id))
    mt={'Formula':payload}
    if visual_column:mt={'VisualColumn':mt}
    return {'measureGuid':mid,'columnType':codes[data_type],'name':string(label),
            'columnMeta':{'id':mid,'label':label,'measure_type':mt,'data_type':data_type}}
