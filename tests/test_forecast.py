import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest
from runtime.forecast import forecast_config
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
