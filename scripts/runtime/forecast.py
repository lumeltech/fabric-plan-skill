"""Native Forecast construction: actual closed history and explicit open defaults.

Full ISO date labels and epoch-second boundaries follow the native UI save shape.
Time-extension axes carry explicit calendar roles.
No current-date inference, synthetic baseline, or alternative input-measure emulation.
"""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import calendar, copy, json, math, os, re, shutil, subprocess
from .identity import native_id

def validate_forecast_config(config):
    """Validate current native Forecast fields without discarding extensions."""
    if not isinstance(config,dict):
        raise ValueError('Forecast configuration must be an object')
    required={'forecast_version','forecast_period','bound_to_filter_context'}
    if not required<=config.keys():
        raise ValueError('Incomplete Forecast configuration')
    version=config['forecast_version']
    if isinstance(version,bool) or not isinstance(version,(int,float)) or not math.isfinite(version):
        raise ValueError('forecast_version must be a finite number')
    period=config['forecast_period']
    if not isinstance(period,dict) or not isinstance(period.get('start'),str) or not isinstance(period.get('end'),str):
        raise ValueError('forecast_period requires ISO date-time strings')
    for key in ('start_utc','end_utc'):
        if key in period and period[key] is not None and (isinstance(period[key],bool) or not isinstance(period[key],int) or period[key]<0):
            raise ValueError('Forecast UTC boundaries must be nonnegative epoch seconds')
    if type(config['bound_to_filter_context']) is not bool:
        raise ValueError('Forecast context binding must be Boolean')
    closed=config.get('closed_period_till')
    if closed is not None and not isinstance(closed,str):
        raise ValueError('closed_period_till must be a string or null')
    auto=config.get('auto_close_forecast_settings')
    if auto is not None:
        if not isinstance(auto,dict):
            raise ValueError('Invalid automatic forecast closure settings')
        for key in ('auto_close_by','calendar_close_value','workday_close_value'):
            if key in auto and (isinstance(auto[key],bool) or not isinstance(auto[key],int) or auto[key]<0):
                raise ValueError('Automatic closure values must be unsigned integers')
        if 'extend_range' in auto and auto['extend_range'] not in ('Extended','None'):
            raise ValueError('Automatic closure extend_range must be Extended or None')
    display=config.get('forecast_value_display')
    if display is not None and display!='Actual' and not (
            isinstance(display,dict) and set(display)=={'Forecast'} and isinstance(display['Forecast'],dict)
            and set(display['Forecast'])=={'forecast_value_retain_blanks'}
            and type(display['Forecast']['forecast_value_retain_blanks']) is bool):
        raise ValueError('Invalid Forecast display contract')
    for key in ('forecast_allowed_user_permissions','disable_write_access'):
        if key in config and type(config[key]) is not bool:
            raise ValueError(key+' must be Boolean')
    for key in ('open_period_config','closed_period_config'):
        value=config.get(key)
        if value is None:continue
        if not isinstance(value,dict) or not isinstance(value.get('method'),dict) or len(value['method'])!=1:
            raise ValueError(key+' requires one tagged method')
        method,argument=next(iter(value['method'].items()))
        if method=='Formula' and not isinstance(argument,str):
            raise ValueError(key+' Formula requires a string')
        elif method=='LinkToMeasure':
            native_id(argument)
        elif method=='DataInput':
            if argument!='Blank':
                if not isinstance(argument,dict) or len(argument)!=1:
                    raise ValueError(key+' DataInput requires one tagged default')
                tag,default=next(iter(argument.items()))
                if tag in ('Formula','Row'):
                    if not isinstance(default,str):raise ValueError(key+' '+tag+' requires a string')
                elif tag=='Measure':
                    native_id(default)
                elif tag=='StaticValue':
                    if isinstance(default,bool) or not isinstance(default,(int,float)) or not math.isfinite(default):
                        raise ValueError(key+' StaticValue requires a finite number')
                else:raise ValueError('Unsupported Forecast DataInput default')
        else:raise ValueError('Unsupported Forecast period method')
    edit=config.get('edit_config')
    if edit is not None:
        if not isinstance(edit,dict):
            raise ValueError('Forecast edit_config must be an object')
        if 'aggregate_total' in edit and edit['aggregate_total'] not in (
                None,'AllPeriods','ClosedPeriods','OpenPeriods'):
            raise ValueError('Invalid aggregate_total')
        if 'on_change_formula' in edit and edit['on_change_formula'] is not None and not isinstance(edit['on_change_formula'],str):
            raise ValueError('Forecast on_change_formula must be a string or null')
        if 'allow_input' in edit and edit['allow_input'] is not None:
            from .input_constraints import input_permission
            input_permission(edit['allow_input'])
        if edit.get('number_column_metadata') is not None:
            from .input_constraints import static_bounds
            static_bounds(edit['number_column_metadata'])
            distribute=edit['number_column_metadata'].get('distribute_parent_value_to_children')
            if distribute is not None and type(distribute) is not bool:
                raise ValueError('Forecast distribution setting must be Boolean')
    from .cube_contract import saved_cube_binding
    cube=saved_cube_binding(config.get('cube_partition_measure_id'),config.get('cube_model'))
    if config.get('cube_partition_measure_id')!=cube.get('cube_partition_measure_id'):
        raise ValueError('Invalid Forecast Cube identity')
    if config.get('cube_model')!=cube.get('cube_model'):
        raise ValueError('Invalid Forecast Cube model')
    return config

def forecast_period(spec, start, end):
    """Nominal ISO date labels plus local-day boundary epoch SECONDS.

    Resolve timezone from the report/user authoring context, never a global
    Chicago default or the execution host. Explicit periodUtc is suitable when
    reusing captured bounds for the identical horizon and timezone.
    """
    supplied=spec.get('periodUtc')
    if supplied is not None:
        if not isinstance(supplied,dict) or set(supplied)!={'start_utc','end_utc'}:
            raise ValueError('periodUtc requires start_utc and end_utc in epoch seconds')
        first,last=supplied['start_utc'],supplied['end_utc']
        if any(isinstance(x,bool) or not isinstance(x,int) for x in (first,last)):
            raise ValueError('Forecast UTC boundaries must be integer epoch seconds')
        # Reject millisecond values and bounds unrelated to the nominal dates.
        if abs(first-calendar.timegm(start.timetuple()))>86400 or abs(last-(calendar.timegm((end+timedelta(days=1)).timetuple())-1))>86400:
            raise ValueError('UTC boundaries do not match the forecast dates in seconds')
    else:
        zone=spec.get('timezone') or spec.get('referenceTimezone') or 'UTC'
        if not isinstance(zone,str) or not zone.strip():
            raise ValueError('Forecast timezone must be an IANA name')
        try:
            tz=timezone.utc if zone=='UTC' else ZoneInfo(zone)
        except ZoneInfoNotFoundError:
            # Windows Python may lack IANA tzdata. Node's bundled ICU supplies it.
            node=os.environ.get('FABRIC_PLAN_NODE') or shutil.which('node')
            if not node:raise ValueError('Timezone data unavailable; set FABRIC_PLAN_NODE or provide periodUtc')
            script=r"""
const [zone,...dates]=process.argv.slice(1);
const fmt=new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});
function wall(t){const p=Object.fromEntries(fmt.formatToParts(new Date(t)).map(x=>[x.type,x.value]));return Date.UTC(+p.year,+p.month-1,+p.day,+p.hour,+p.minute,+p.second);}
const result=dates.map(d=>{const desired=Date.parse(d+'T00:00:00.000Z');let t=desired;for(let i=0;i<8;i++){const delta=desired-wall(t);if(delta===0)return t/1000;t+=delta;}throw Error('Local midnight cannot be resolved; supply explicit periodUtc');});
process.stdout.write(JSON.stringify(result));
"""
            result=subprocess.run([node,'-e',script,zone,start.isoformat(),(end+timedelta(days=1)).isoformat()],capture_output=True,text=True,check=True)
            first,exclusive=json.loads(result.stdout);last=exclusive-1
        else:
            first=int(datetime.combine(start,time.min,tzinfo=tz).timestamp())
            last=int(datetime.combine(end+timedelta(days=1),time.min,tzinfo=tz).timestamp())-1
    if first<0 or last<first:raise ValueError('Invalid Forecast UTC range')
    return {'start':start.isoformat()+'T00:00:00.000Z',
            'end':end.isoformat()+'T00:00:00.000Z',
            'start_utc':first,'end_utc':last}

def resolve_time_levels(columns, explicit=None):
    """Resolve one role per actual column; never insert sample hierarchy levels.

    Explicit metadata takes precedence over recognized field names. Caller owns
    member/format/fiscal recognition. Noncaptured native units must be provided
    from the target contract, not borrowed from writeback's uppercase enums.
    """
    explicit=explicit or {}
    if not isinstance(explicit,dict) or set(explicit)-set(columns):
        raise ValueError('columnTimeLevels must map actual assigned column field keys')
    aliases={'year':'Year','yr':'Year','quarter':'Quarter','qtr':'Quarter',
        'month':'Month','monthname':'Month','monthnumber':'Month','monthno':'Month',
        'halfyear':'HalfYear','half':'HalfYear','week':'Week','weeknumber':'Week',
        'day':'Day','date':'Day','fulldate':'Day'}
    result=[]
    for key in columns:
        raw=explicit.get(key)
        label=raw.get('level') if isinstance(raw,dict) else raw
        label=label or key.rsplit('[',1)[-1].rstrip(']')
        level=aliases.get(re.sub(r'[ _-]','',str(label)).lower())
        if not level:raise ValueError('Resolve calendar level and format for '+key)
        unit=raw.get('timeIntervalUnit') if isinstance(raw,dict) else None
        if not unit:
            if level not in ('Year','Quarter','Month'):
                raise ValueError('Supply the target native timeIntervalUnit for '+key+' ('+level+')')
            unit=level
        if not isinstance(unit,str) or not unit.strip():raise ValueError('Native time interval unit required')
        if level in ('Year','Quarter','Month') and unit!=level:
            raise ValueError('Native calendar unit casing differs from writeback: '+key)
        result.append({'level':level,'timeIntervalUnit':unit})
    patterns={('Year',),('Year','HalfYear'),('Year','Quarter'),('Year','Month'),('Year','Week'),
        ('Year','HalfYear','Quarter'),('Year','HalfYear','Month'),('Year','HalfYear','Week'),
        ('Year','Quarter','Month'),('Year','Quarter','Week'),('Year','Month','Week'),
        ('Year','Month','Day'),('Year','Week','Day'),('Year','Quarter','Month','Day'),('Day',)}
    resolved=tuple(r['level'] for r in result)
    if resolved==('Year','Quarter','Month','Week'):
        week_meta=explicit.get(columns[-1],{})
        if not isinstance(week_meta,dict) or week_meta.get('parentageValidated') is not True:
            raise ValueError('Year/Quarter/Month/Week requires verified calendar parentage; use Year/Week for crossing weeks')
        patterns.add(resolved)
    if resolved not in patterns:
        raise ValueError('Unsupported calendar hierarchy; retain only a documented ordered pattern')
    return result

def forecast_time_axis(dimensions, explicit=None):
    """Forecast time extension follows the actual column dimension granularity."""
    roles=resolve_time_levels([d['externalKey'] for d in dimensions],explicit)
    for d,role in zip(dimensions,roles):
        d.pop('isNative',None)
        d.update(isTimeDimension=True,timeIntervalUnit=role['timeIntervalUnit'])
    return dimensions


def forecast_config(spec, ids, kinds, *, columns, time_levels=None):
    from .construct import expression
    if not columns:
        raise ValueError('Forecast requires date hierarchy in Columns')
    resolve_time_levels(columns,time_levels)
    source=spec['actuals']
    if source not in ids or kinds.get(source)!='Native':
        raise ValueError('Closed-period actuals must resolve to an assigned native actuals measure')
    native_id(ids[source])
    start=date.fromisoformat(spec['start']); end=date.fromisoformat(spec['end'])
    if start>end: raise ValueError('Forecast start exceeds end')
    default=spec.get('openDefault')
    if default is None or default=='None': value='Blank'
    elif isinstance(default,dict) and len(default)==1:
        tag,v=next(iter(default.items()))
        if tag=='Formula': value={tag:expression(v,ids)}
        elif tag=='Measure':
            if v not in ids: raise ValueError('Unresolved open-period default measure')
            value={tag:ids[v]}
        elif tag=='StaticValue' and isinstance(v,(int,float)) and not isinstance(v,bool): value={tag:v}
        else: raise ValueError('Unsupported Forecast open default')
    else: raise ValueError('Open default must be None, Formula, Measure or StaticValue')
    reference=spec.get('referenceForecast') or {}
    period_spec=copy.deepcopy(spec)
    period=reference.get('forecast_period',{})
    # A saved range is authoritative for the same horizon. An offset alone is
    # not a named timezone; never extrapolate it to different dates/DST rules.
    if not spec.get('timezone') and not spec.get('periodUtc') and all(
            str(period.get(k,''))[:10]==v.isoformat() for k,v in [('start',start),('end',end)]):
        if all(isinstance(period.get(k),int) for k in ('start_utc','end_utc')):
            period_spec['periodUtc']={k:period[k] for k in ('start_utc','end_utc')}
    edit=copy.deepcopy(reference.get('edit_config') or {})
    edit.setdefault('aggregate_total',None)
    from .input_policy import allow_input
    if isinstance(edit.get('allow_input'),dict) and 'allow_input' not in spec:
        raise ValueError('Reference allow_input formula needs explicit policy and remapping for this new Forecast')
    edit['allow_input']=allow_input(spec.get('allow_input','ReadAndEdit'),ids)
    edit.setdefault('on_change_formula',None)
    number=edit.get('number_column_metadata')
    if number is None:
        number={}
        edit['number_column_metadata']=number
    elif not isinstance(number,dict):
        raise ValueError('Reference Forecast number_column_metadata must be an object or null')
    for k in ('min_value','max_value','default_value'):number.setdefault(k,None)
    if edit.get('on_change_formula') or any(isinstance(number.get(k),dict) and 'Measure' in number[k] for k in ('default_value','min_value','max_value')):
        raise ValueError('Reference edit dependencies require explicit remapping before construction')
    from .input_constraints import static_bounds,distribution_default
    static_bounds(number)
    distribute=distribution_default(spec,number.get('distribute_parent_value_to_children',True))
    if not isinstance(distribute,bool):raise ValueError('distribute must be a Boolean')
    number['distribute_parent_value_to_children']=distribute
    result={'forecast_version':reference.get('forecast_version',1),'forecast_period':forecast_period(period_spec,start,end),
        'closed_period_till':reference.get('closed_period_till'),
        'auto_close_forecast_settings':copy.deepcopy(reference.get('auto_close_forecast_settings')),
        'closed_period_config':{'method':{'LinkToMeasure':ids[source]}},
        'open_period_config':{'method':{'DataInput':value}},
        'forecast_value_display':copy.deepcopy(reference.get('forecast_value_display') or 'Actual'),
        'forecast_allowed_user_permissions':reference.get('forecast_allowed_user_permissions',True),
        'disable_write_access':reference.get('disable_write_access',False),
        'bound_to_filter_context':reference.get('bound_to_filter_context',True),'edit_config':edit}
    from .cube_contract import saved_cube_binding
    result.update(saved_cube_binding(
        spec.get('cube_partition_measure_id',reference.get('cube_partition_measure_id')),
        spec.get('cube_model',reference.get('cube_model')),
    ))
    return validate_forecast_config(result)
