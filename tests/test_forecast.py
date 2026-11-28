import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest
from unittest import mock
from datetime import date, timedelta
from zoneinfo import ZoneInfoNotFoundError
import calendar, copy, os, shutil
from runtime import forecast as forecast_module
from runtime.forecast import forecast_config, forecast_period, resolve_time_levels, validate_forecast_config
from runtime.input_constraints import check_record

class ForecastTests(unittest.TestCase):
    def make(self,**kw):
        s=dict(actuals='actual',start='2026-11-01',end='2035-12-31',timezone='UTC');s.update(kw)
        return forecast_config(s,{'actual':'123456789012345'}, {'actual':'Native'},
            columns=['Calendar[Year]','Calendar[Quarter]','Calendar[MonthName]'])
    def test_unspecified_open_is_blank_and_closed_is_actual(self):
        c=self.make()
        self.assertEqual(c['open_period_config']['method'],{'DataInput':'Blank'})
        self.assertEqual(c['closed_period_config']['method'],{'LinkToMeasure':'123456789012345'})
        self.assertIsNone(c['closed_period_till'])
        self.assertIsNone(c['edit_config']['aggregate_total'])
        self.assertTrue(c['edit_config']['number_column_metadata']['distribute_parent_value_to_children'])
    def test_no_timezone_question_uses_utc(self):
        c=self.make(timezone=None,start='2026-01-01',end='2026-12-31')
        self.assertEqual(c['forecast_period']['start_utc'],1767225600)
        self.assertEqual(c['forecast_period']['end_utc'],1798761599)
    def test_formula_is_editable_default_not_readonly_method(self):
        c=self.make(openDefault={'Formula':'COLUMN.ADDMONTH(-1) * 1.1'})
        self.assertEqual(c['open_period_config']['method'],{'DataInput':{'Formula':'COLUMN.ADDMONTH(-1) * 1.1'}})
    def test_reference_cube_binding_survives_forecast_reconstruction(self):
        c=self.make(referenceForecast={
            'cube_partition_measure_id':'701',
            'cube_model':'DYNAMIC',
        })
        self.assertEqual(c['cube_partition_measure_id'],'701')
        self.assertEqual(c['cube_model'],'DYNAMIC')
        with self.assertRaises(ValueError):self.make(cube_model='DYNAMIC')
    def test_nullable_reference_edit_metadata_rehydrates_complete_defaults(self):
        c=self.make(referenceForecast={
            'forecast_value_display':None,
            'edit_config':{'aggregate_total':None,'allow_input':None,
                'on_change_formula':None,'number_column_metadata':None}})
        self.assertEqual(c['forecast_value_display'],'Actual')
        self.assertEqual(c['edit_config']['allow_input'],'ReadAndEdit')
        self.assertEqual(c['edit_config']['number_column_metadata'],
            {'min_value':None,'max_value':None,'default_value':None,
             'distribute_parent_value_to_children':True})
    def test_saved_forecast_types_are_validated(self):
        for key,value in (
                ('forecast_allowed_user_permissions','true'),
                ('disable_write_access',1),
                ('bound_to_filter_context','false')):
            with self.subTest(key=key),self.assertRaises(ValueError):
                self.make(**{'referenceForecast':{key:value}})
        with self.assertRaises(ValueError):self.make(
            referenceForecast={'forecast_value_display':{'Forecast':{'forecast_value_retain_blanks':'true'}}})
        record={'measureGuid':'123456789012345',
            'columnMeta':{'measure_type':{'Forecast':self.make()}},
            'boundToFilterContext':20}
        with self.assertRaises(ValueError):check_record(record)
    def test_invalid_horizon(self):
        with self.assertRaises(ValueError): self.make(end='2025-01-01')
    def test_noncalendar_axis(self):
        with self.assertRaises(ValueError):
            forecast_config(dict(actuals='actual',start='2026-11-01',end='2035-12-31'),
                {'actual':'123456789012345'},{'actual':'Native'},columns=['Product[Name]'])

    def test_saved_configuration_guard_arms(self):
        good=self.make()
        def edited(key,value):
            config=copy.deepcopy(good);config[key]=value;return config
        def with_period(**patch):
            return edited('forecast_period',{**good['forecast_period'],**patch})
        def with_edit(**patch):
            return edited('edit_config',{**good['edit_config'],**patch})
        def with_method(kind,method):
            return edited(kind+'_period_config',{'method':method})
        def auto(**patch):
            return edited('auto_close_forecast_settings',patch)
        def number(**patch):
            return with_edit(number_column_metadata={**good['edit_config']['number_column_metadata'],**patch})
        def bound(cube_id,model):
            config=copy.deepcopy(good);config.update({'cube_partition_measure_id':cube_id,'cube_model':model});return config
        cases=[
            ('not an object',lambda:'x','Forecast configuration must be an object'),
            ('missing required key',lambda:{k:v for k,v in good.items() if k!='bound_to_filter_context'},'Incomplete Forecast configuration'),
            ('version nan',lambda:edited('forecast_version',float('nan')),'forecast_version must be a finite number'),
            ('version boolean',lambda:edited('forecast_version',True),'forecast_version must be a finite number'),
            ('version string',lambda:edited('forecast_version','2'),'forecast_version must be a finite number'),
            ('period without dates',lambda:edited('forecast_period',{'start_utc':0,'end_utc':1}),'forecast_period requires ISO date-time strings'),
            ('negative utc',lambda:with_period(start_utc=-1),'Forecast UTC boundaries must be nonnegative epoch seconds'),
            ('fractional utc',lambda:with_period(end_utc=1.5),'Forecast UTC boundaries must be nonnegative epoch seconds'),
            ('boolean utc',lambda:with_period(start_utc=True),'Forecast UTC boundaries must be nonnegative epoch seconds'),
            ('closed till type',lambda:edited('closed_period_till',5),'closed_period_till must be a string or null'),
            ('auto closure type',lambda:edited('auto_close_forecast_settings','now'),'Invalid automatic forecast closure settings'),
            ('auto closure negative',lambda:auto(auto_close_by=-1),'closure values must be unsigned integers'),
            ('auto closure boolean',lambda:auto(calendar_close_value=True),'closure values must be unsigned integers'),
            ('auto closure range',lambda:auto(extend_range='Maybe'),'extend_range must be Extended or None'),
            ('display contract',lambda:edited('forecast_value_display',{'Forecast':{}}),'Invalid Forecast display contract'),
            ('context binding',lambda:edited('bound_to_filter_context','false'),'Forecast context binding must be Boolean'),
            ('write permission flag',lambda:edited('disable_write_access',1),'disable_write_access must be Boolean'),
            ('two period methods',lambda:with_method('open',{'DataInput':'Blank','Formula':'x'}),'requires one tagged method'),
            ('formula not text',lambda:with_method('closed',{'Formula':5}),'closed_period_config Formula requires a string'),
            ('link not a native id',lambda:with_method('closed',{'LinkToMeasure':'0x10'}),'decimal u64'),
            ('two datainput defaults',lambda:with_method('open',{'DataInput':{'Formula':'x','Row':'y'}}),'DataInput requires one tagged default'),
            ('measure default not a native id',lambda:with_method('open',{'DataInput':{'Measure':'abc'}}),'decimal u64'),
            ('static default not finite',lambda:with_method('open',{'DataInput':{'StaticValue':'1'}}),'StaticValue requires a finite number'),
            ('unknown datainput default',lambda:with_method('open',{'DataInput':{'Bucket':'1'}}),'Unsupported Forecast DataInput default'),
            ('unknown period method',lambda:with_method('open',{'Bucket':'1'}),'Unsupported Forecast period method'),
            ('edit config type',lambda:edited('edit_config','x'),'Forecast edit_config must be an object'),
            ('aggregate total',lambda:with_edit(aggregate_total='All'),'Invalid aggregate_total'),
            ('on change formula',lambda:with_edit(on_change_formula=5),'on_change_formula must be a string or null'),
            ('distribution flag',lambda:number(distribute_parent_value_to_children='yes'),'distribution setting must be Boolean'),
            ('fractional static bound',lambda:number(min_value={'Static':1.5}),'min_value Static does not support decimal'),
            ('cube id must be text',lambda:bound(701,'DYNAMIC'),'cube_partition_measure_id requires a non-empty string'),
            ('cube id blank',lambda:bound('   ','DYNAMIC'),'cube_partition_measure_id requires a non-empty string'),
            ('cube model without id',lambda:bound(None,'DYNAMIC'),'cube_model requires an actual cube_partition_measure_id'),
            ('cube model value',lambda:bound('701','STATIC'),'cube_model supports the native DYNAMIC value only'),
        ]
        for label,build,message in cases:
            with self.subTest(case=label):
                if message:
                    with self.assertRaisesRegex(ValueError,message):validate_forecast_config(build())
                else:
                    with self.assertRaises(ValueError):validate_forecast_config(build())
        # The saved shape is returned untouched, so each case above fails on its own arm.
        self.assertIs(validate_forecast_config(good),good)
        bound=copy.deepcopy(good);bound.update({'cube_partition_measure_id':'701','cube_model':'DYNAMIC'})
        self.assertIs(validate_forecast_config(bound),bound)

    def test_explicit_utc_boundaries(self):
        start,end=date(2026,3,1),date(2026,3,31)
        first=calendar.timegm(start.timetuple());last=calendar.timegm((end+timedelta(days=1)).timetuple())-1
        self.assertEqual(forecast_period({'periodUtc':{'start_utc':first,'end_utc':last}},start,end),
            {'start':'2026-03-01T00:00:00.000Z','end':'2026-03-31T00:00:00.000Z','start_utc':first,'end_utc':last})
        for label,spec,message in [
            ('not an object',{'periodUtc':[first,last]},'periodUtc requires start_utc and end_utc'),
            ('extra key',{'periodUtc':{'start_utc':first,'end_utc':last,'tz':'UTC'}},'periodUtc requires start_utc and end_utc'),
            ('milliseconds',{'periodUtc':{'start_utc':first*1000,'end_utc':last}},'do not match the forecast dates in seconds'),
            ('boolean boundary',{'periodUtc':{'start_utc':True,'end_utc':last}},'must be integer epoch seconds'),
            ('float boundary',{'periodUtc':{'start_utc':first,'end_utc':float(last)}},'must be integer epoch seconds'),
        ]:
            with self.subTest(case=label),self.assertRaisesRegex(ValueError,message):
                forecast_period(spec,start,end)

    def test_reversed_horizon_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Invalid Forecast UTC range'):
            forecast_period({'timezone':'UTC'},date(2026,3,31),date(2026,3,1))

    def test_timezone_must_be_named(self):
        for label,spec,message in [
            ('offset only',{'timezone':120},'IANA name'),
            ('blank',{'timezone':'  '},'IANA name'),
        ]:
            with self.subTest(case=label),self.assertRaisesRegex(ValueError,message):
                forecast_period(spec,date(2026,3,1),date(2026,3,31))

    def test_node_icu_fallback_reproduces_zoneinfo_boundaries(self):
        node=os.environ.get('FABRIC_PLAN_NODE') or shutil.which('node')
        if not node:self.skipTest('Node.js not installed')
        for zone in ('America/Chicago','Asia/Kathmandu'):   # DST step and a half-hour offset
            start,end=date(2026,3,1),date(2026,3,31)
            python=forecast_period({'timezone':zone},start,end)
            def missing(name):raise ZoneInfoNotFoundError(name)
            with mock.patch.object(forecast_module,'ZoneInfo',missing):
                self.assertEqual(forecast_period({'timezone':zone},start,end),python)

    def test_missing_tzdata_names_the_escape_hatches(self):
        def missing(name):raise ZoneInfoNotFoundError(name)
        with mock.patch.object(forecast_module,'ZoneInfo',missing),mock.patch.object(forecast_module.shutil,'which',lambda name:None),\
             mock.patch.dict(os.environ,{'FABRIC_PLAN_NODE':''}):
            for label,zone in [('known zone','America/Chicago'),('unknown zone','Mars/Olympus_Mons')]:
                with self.subTest(case=label),self.assertRaisesRegex(ValueError,'set FABRIC_PLAN_NODE or provide periodUtc'):
                    forecast_period({'timezone':zone},date(2026,3,1),date(2026,3,31))

    def test_calendar_level_resolution_refusals(self):
        columns=['Calendar[Year]','Calendar[Quarter]','Calendar[MonthName]']
        for label,keys,explicit,message in [
            ('unknown column',columns,{'Calendar[Nope]':'Month'},'columnTimeLevels must map actual assigned column'),
            ('unrecognized field',['Calendar[Shift]'],None,'Resolve calendar level and format'),
            ('day needs the native unit',['Calendar[Day]'],None,'Supply the target native timeIntervalUnit'),
            ('writeback casing',['Calendar[Year]'],{'Calendar[Year]':{'timeIntervalUnit':'YEAR'}},'unit casing differs from writeback'),
            ('descending levels',['Calendar[Day]','Calendar[MonthName]'],{'Calendar[Day]':{'timeIntervalUnit':'Day'}},'Unsupported calendar hierarchy'),
            ('unverified week parentage',['Calendar[Year]','Calendar[Quarter]','Calendar[MonthName]','Calendar[Week]'],
             {'Calendar[Week]':{'timeIntervalUnit':'WeekISO'}},'verified calendar parentage'),
        ]:
            with self.subTest(case=label),self.assertRaisesRegex(ValueError,message):
                resolve_time_levels(keys,explicit)
        self.assertEqual(resolve_time_levels(['Calendar[Day]'],{'Calendar[Day]':{'timeIntervalUnit':'Day'}}),
            [{'level':'Day','timeIntervalUnit':'Day'}])
        self.assertEqual(resolve_time_levels(columns,{'Calendar[MonthName]':{'level':'Month','timeIntervalUnit':'Month'}}),
            [{'level':'Year','timeIntervalUnit':'Year'},{'level':'Quarter','timeIntervalUnit':'Quarter'},
             {'level':'Month','timeIntervalUnit':'Month'}])

    def test_construction_refusals(self):
        ids={'actual':'123456789012345','other':'987654321098765'};kinds={'actual':'Native','other':'Formula'}
        base=dict(actuals='actual',start='2026-11-01',end='2035-12-31',timezone='UTC')
        columns=['Calendar[Year]','Calendar[Quarter]','Calendar[MonthName]']
        for label,spec,other_ids,columns,message in [
            ('no columns',dict(base),ids,[],'Forecast requires date hierarchy in Columns'),
            ('unresolved calendar role',dict(base),ids,['Calendar[Shift]'],'Resolve calendar level and format'),
            ('actuals not native',dict(base,actuals='other'),ids,columns,'must resolve to an assigned native actuals measure'),
            ('actuals unresolved',dict(base,actuals='ghost'),ids,columns,'must resolve to an assigned native actuals measure'),
            ('open default measure unresolved',dict(base,openDefault={'Measure':'ghost'}),ids,columns,'Unresolved open-period default measure'),
            ('open default tag unknown',dict(base,openDefault={'Bucket':'1'}),ids,columns,'Unsupported Forecast open default'),
            ('open default type',dict(base,openDefault=7),ids,columns,'Open default must be None, Formula, Measure or StaticValue'),
            ('reference metadata type',dict(base,referenceForecast={'edit_config':{'number_column_metadata':7}}),ids,columns,'number_column_metadata must be an object or null'),
            ('reference formula',dict(base,referenceForecast={'edit_config':{'on_change_formula':'COLUMN.SUM(1)'}}),ids,columns,'require explicit remapping before construction'),
            ('reference default measure',dict(base,referenceForecast={'edit_config':{'number_column_metadata':{'default_value':{'Measure':'1'}}}}),ids,columns,'require explicit remapping before construction'),
            ('reference allow_input formula',dict(base,referenceForecast={'edit_config':{'allow_input':{'Formula':'x'}}}),ids,columns,'needs explicit policy and remapping'),
            ('distribution type',dict(base,distribute='yes'),ids,columns,'distribute must be a Boolean'),
        ]:
            with self.subTest(case=label),self.assertRaisesRegex(ValueError,message):
                forecast_config(spec,other_ids,kinds,columns=columns)
        # A named open-period default is remapped through the identity registry, not copied raw.
        c=forecast_config(dict(base,openDefault={'Measure':'other'}),ids,kinds,columns=columns)
        self.assertEqual(c['open_period_config']['method'],{'DataInput':{'Measure':'987654321098765'}})

    def test_saved_bounds_are_reused_only_for_the_same_horizon(self):
        axis=['Calendar[Year]','Calendar[Quarter]','Calendar[MonthName]']
        chicago=forecast_period({'timezone':'America/Chicago'},date(2026,11,1),date(2035,12,31))
        saved={'start':'2026-11-01T00:00:00.000Z','end':'2035-12-31T00:00:00.000Z',
               'start_utc':chicago['start_utc'],'end_utc':chicago['end_utc']}
        self.assertNotEqual(saved['start_utc'],calendar.timegm(date(2026,11,1).timetuple()))
        def construct(**spec):
            return forecast_config({'actuals':'actual','start':'2026-11-01','end':'2035-12-31',
                'referenceForecast':{'forecast_period':saved},**spec},
                {'actual':'123456789012345'},{'actual':'Native'},columns=axis)
        # No timezone question and the identical nominal horizon: the captured local boundaries are authoritative.
        self.assertEqual(construct()['forecast_period'],saved)
        # An explicit zone is a new question, so the horizon is rebuilt rather than inherited.
        self.assertEqual(construct(timezone='UTC')['forecast_period']['start_utc'],
                         calendar.timegm(date(2026,11,1).timetuple()))
        # A different horizon never borrows the reference offset, which is not a named zone.
        self.assertEqual(construct(end='2030-12-31')['forecast_period']['start_utc'],
                         calendar.timegm(date(2026,11,1).timetuple()))
        # Millisecond or fractional stored values are not epoch seconds, so they are not reused.
        fractional=construct(referenceForecast={'forecast_period':{**saved,'start_utc':float(saved['start_utc'])}})
        self.assertIsInstance(fractional['forecast_period']['start_utc'],int)
        self.assertNotEqual(fractional['forecast_period']['start_utc'],saved['start_utc'])
        # periodUtc on the request outranks both the reference bounds and any zone.
        explicit={'start_utc':chicago['start_utc'],'end_utc':chicago['end_utc']}
        self.assertEqual(construct(periodUtc=explicit)['forecast_period']['start_utc'],chicago['start_utc'])

    def test_open_default_forms(self):
        ids={'actual':'123456789012345'};kinds={'actual':'Native'}
        axis=['Calendar[Year]','Calendar[Quarter]','Calendar[MonthName]']
        def method(**spec):
            return forecast_config({'actuals':'actual','start':'2026-11-01','end':'2035-12-31',**spec},
                ids,kinds,columns=axis)['open_period_config']['method']
        self.assertEqual(method(),{'DataInput':'Blank'})
        self.assertEqual(method(openDefault=None),{'DataInput':'Blank'})
        self.assertEqual(method(openDefault='None'),{'DataInput':'Blank'})
        self.assertEqual(method(openDefault={'Measure':'actual'}),{'DataInput':{'Measure':'123456789012345'}})
        self.assertEqual(method(openDefault={'StaticValue':0}),{'DataInput':{'StaticValue':0}})
        # A Row default survives in saved Forecast records, so the validator accepts it, but the
        # construction request only exposes the tags above.
        with self.assertRaisesRegex(ValueError,'Unsupported Forecast open default'):
            method(openDefault={'Row':'COLUMN.SUM(1)'})
        with self.assertRaisesRegex(ValueError,'Unsupported Forecast open default'):
            method(openDefault={'StaticValue':'1'})
