"""Contract fixtures test compatibility, precision, and mutation/readback boundaries."""
import base64,copy,os,tempfile,unittest,socket
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch
from runtime import input_factories as inputs,rule_factories as rules
from runtime.cube_contract import multi_dimension_settings
from runtime import powertable_factory as pt,home_api,navigator_api
from runtime.transport import Client,HttpError
from runtime.codec import loads

class BuilderContracts(unittest.TestCase):
    def setUp(self):
        td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);self.path=Path(td.name)
        env=patch.dict(os.environ,{'BUILDER_TEST_TOKEN':'synthetic-contract-token'});env.start();self.addCleanup(env.stop)
        net=patch.object(socket.socket,'connect',side_effect=AssertionError('No live network in contract tests'));net.start();self.addCleanup(net.stop)
    def node(self):
        node=os.environ.get('FABRIC_PLAN_NODE')
        if not node:self.skipTest('Set FABRIC_PLAN_NODE for compression tests')
        return node
    def test_all_nine_factories_and_visual_formula(self):
        settings={'Number':{'default_value':{'Static':Decimal('123.456789012345678901')}},'ShortText':{},'LongText':{},
          'SingleSelect':{},'MultiSelect':{},'Date':{},'Person':{},'Checkbox':{},
          'Simulation':{'source_measure_id':'salary','simulation_slider':True,'simulation_range':100,
            'distribute_parent_value_to_children':False,'simulation_value_align':'right','variance_formatting_style':'percentage'}}
        for kind,cfg in settings.items():
            with self.subTest(kind=kind):
                value=inputs.input_create('18446744073709551615',kind,kind,cfg,'',visual_column=True,measures={'salary':'401'})
                self.assertEqual(value['columnMeta']['id'],'18446744073709551615')
                self.assertEqual(set(value['columnMeta']['measure_type']['VisualColumn']),{'DataInput'})
        formula=inputs.formula_create('501','Loaded pay','${salary} * 1.2',{'salary':'401'},True)
        self.assertEqual(formula['columnMeta']['measure_type'],{'VisualColumn':{'Formula':{'formula':'M_401 * 1.2'}}})
        self.assertNotIn('boundToFilterContext',formula)
    def test_unsupported_branches_and_wrong_types_fail(self):
        for kind,settings in [('Approval',{}),('Person',{'default_value':{'Static':'x'}}),('Date',{'format':'MM/DD/YYYY'}),
            ('Checkbox',{'default_value':{'Static':1}}),('Simulation',{}),('Number',{'max_value':{'Static':float('inf')}})]:
            with self.subTest(kind=kind),self.assertRaises(ValueError):inputs.metadata(kind,settings)
        with self.assertRaises(ValueError):inputs.input_create('501','X','Number',{},'',context_encoding='legacy-0-1')
        with self.assertRaises(ValueError):rules.selector('columns',{'PeriodRange':{'from':1}})
        with self.assertRaises(ValueError):rules.distribute_rows('MeasureIdWithReference')
    def test_context_and_reference_resolution_are_separate(self):
        r=inputs.input_create('501','X','Checkbox',{'default_value':{'Dimension':'approved'}},'',dimensions={'approved':'401'},context_bound=False)
        self.assertEqual(r['boundToFilterContext'],20)
        self.assertEqual(r['columnMeta']['measure_type']['DataInput']['column_type']['Checkbox']['default_value'],{'Dimension':'401'})
        with self.assertRaises(ValueError):inputs.metadata('ShortText',{'default_value':{'Measure':'absent'}})
    def test_select_advanced_style_preserves_optional_native_fields(self):
        r=inputs.input_create('501','Owner','SingleSelect',{'advanced':{
            'visual_identifier':'Owner visual','columns':'Id,Label'}},'config')
        self.assertEqual(r['columnMeta']['measure_type']['DataInput']['column_type']['SingleSelect']['advanced'],
            {'visual_identifier':'Owner visual','columns':'Id,Label'})
        with self.assertRaises(ValueError):inputs.metadata('SingleSelect',{'advanced':{'rows':'Name'}})
        with self.assertRaises(ValueError):inputs.metadata('SingleSelect',{'advanced':{'columns':1}})
    def test_saved_cube_bindings_and_lookup_dimensions_are_preserved(self):
        p=inputs.input_create('501','Dynamic assumption','Number',{},'config',
            cube_partition_measure_id='partition-region-v2',cube_model='DYNAMIC')
        di=p['columnMeta']['measure_type']['DataInput']
        self.assertEqual(di['cube_partition_measure_id'],'partition-region-v2')
        self.assertEqual(di['cube_model'],'DYNAMIC')
        f=inputs.formula_create('502','Cube formula','1 + 1',{},
            cube_partition_measure_id='702')['columnMeta']['measure_type']['Formula']
        self.assertEqual(f['cube_partition_measure_id'],'702')
        settings=multi_dimension_settings(
            referenceMeasures=[{'id':'701','label':'Sales','type':'Measure','isNative':True,'aggregationType':'Sum','dataType':'Double'}],
            newPartitions=[{'name':'Region plan','dataAssignment':{
                'dimensions':[{'id':'Region[RegionId]','label':'RegionId','dataType':'String','type':'Column',
                    'distinctValueCount':4,'lookups':[{'id':'Region[RegionName]','label':'RegionName','dataType':'String','type':'Column'}]}],
                'timeDimensions':[]}}],
            existingPartitions=[],cubeModel='DYNAMIC')
        self.assertEqual(settings['cubeModel'],'DYNAMIC')
        self.assertEqual(settings['newPartitions'][0]['dataAssignment']['dimensions'][0]['lookups'][0]['id'],'Region[RegionName]')
        with self.assertRaises(ValueError):multi_dimension_settings(
            referenceMeasures=[],newPartitions=[],existingPartitions=[],cubeModel='LEGACY')
        with self.assertRaises(ValueError):inputs.input_create(
            '501','Invalid cube','Number',{},'config',cube_model='DYNAMIC')
    def test_rules_keep_logical_identity(self):
        r=rules.new_rule('501','Locked approved plan',rules.lock(True),rows={'Dimension':'401'},measures={'SelectedMeasures':['601']})
        self.assertEqual(r['ruleOperation']['New']['rule_id'],'501');self.assertNotIn('id',r['ruleOperation']['New'])
        with self.assertRaises(ValueError):rules.min_max({'Static':{}},{'Static':{}})
        with self.assertRaises(ValueError):rules.min_max({'Static':{'value':1,'is_exclusive':True}},{'Static':{'value':1}})
    def test_insert_compression_preserves_unicode_decimal_and_u64(self):
        meta=[{'id':'id','isPrimaryKey':True,'isEditable':False},{'id':'Name'},{'id':'Amount'},{'id':'ExternalKey'}]
        rows=[['地域 – Málaga',Decimal('123.456789012345678901'),18446744073709551615]]
        p=pt.row_save(meta,'insert',rows,generated_keys=['id'],visual_meta={'rowIds':[],'optionsMeta':{}},node=self.node())
        out=home_api.decode_roles(p['data'],self.node())
        self.assertEqual(out['createData']['records'],rows)
        self.assertEqual([m['id'] for m in p['metaData']],['Name','Amount','ExternalKey'])
        with self.assertRaises(ValueError):pt.row_save(meta,'insert',rows,visual_meta={'rowIds':[],'optionsMeta':{}},node=self.node())
        # Synthetic capture above tests persistence only, not a product capture factory.
    def test_navigator_new_shape_is_not_legacy_corner_profile(self):
        s=navigator_api.state('NAVIGATOR_BUTTON',page_target='201',palette={'fill':'#FFFFFF','activeFill':'#087F8C'})
        keys=s['style']['DEFAULT']['shapeState']['cornerRadius'].keys()
        self.assertEqual(set(keys),{'topLeft','topRight','bottomRight','bottomLeft','isCustomCornerRadius','isEnabled'})
        self.assertEqual(s['navigatorButtonState']['pageDestinationId'],'201')
        with self.assertRaises(ValueError):navigator_api.validate_targets(s,['202'],[])
        with self.assertRaises(ValueError):navigator_api.state(web_url='https://example.invalid')
if __name__=='__main__':unittest.main()
