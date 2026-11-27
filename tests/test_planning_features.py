"""Planning writeback, inserted rows, scenarios and row templates as definition parts."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from runtime.codec import load,pack,parts,unpack
from runtime.construct import build
from runtime.validate import schema_report,validate_plan

ROOT=Path(__file__).resolve().parents[1]
BASE='https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/'
# The two documented destination forms, with synthetic identities.
SCHEMA_FORM={'tableName':'wb_capacity','connectionId':'00000000-0000-4000-8000-000000000001',
             'settings':{'dbSchema':'dbo','dbName':'Planning','dbHost':'sql.example.invalid'},'settingsHash':'synthetic-settings-hash'}
ARTICLE_FORM={'connectionId':'00000000-0000-4000-8000-000000000001','databaseId':'00000000-0000-4000-8000-000000000002',
              'tableName':'wb_capacity','schema':'dbo'}


def fresh_export():
    """One Planning sheet with two Native measures and one DataInput measure."""
    raw=build(load(ROOT/'assets/fixtures/model.json'),load(ROOT/'assets/fixtures/capacity-spec.json'))['raw']
    sheet=raw['definition.json']['sheets'][0];visual=sheet['workloadItemEntityVisuals'][0]['visualId']
    prefix=f"sheets/{sheet['recordGuid']}/visuals/{visual}/"
    measures={c['name']:c['measureGuid'] for c in raw[prefix+'dataInput.json']['columns']}
    state=raw[prefix+'properties.json']['properties']['visualState']
    dims={d['label']:d['id'] for d in state['rowDimensions']+state['columnDimensions']}
    return pack(raw),sheet['recordGuid'],visual,prefix,measures,dims


def status(candidate,path):
    return next(item['status'] for item in schema_report(unpack(candidate)) if item['path']==path)


class PlanningFeatureTestCase(unittest.TestCase):
    def setUp(self):
        self.envelope,self.sheet,self.visual,self.prefix,self.measures,self.dims=fresh_export()

    def add(self,envelope=None,**request):
        from runtime.planning_features import add_planning_features
        return add_planning_features(envelope or self.envelope,sheet_guid=self.sheet,**request)

    def assertOnlyAdded(self,before,candidate,added):
        old,new=parts(before),parts(candidate)
        self.assertEqual(sorted(set(new)-set(old)),sorted(added))
        for path,payload in old.items():
            self.assertEqual(new[path],payload,path)


class Writeback(PlanningFeatureTestCase):
    def writeback(self,**extra):
        return {'writeback_type':'PIVOT_WIDE','destinations':[copy.deepcopy(SCHEMA_FORM)],**extra}

    def test_writeback_part_from_explicit_layout_and_copied_destination(self):
        hours,can_edit=self.measures['Available Hours'],self.measures['CanEdit']
        candidate,manifest=self.add(writeback=self.writeback(
            column_mapping={hours:'available_hours'},excluded_measures=[can_edit],
            skipped_dimensions=[self.dims['Version']],number_precision=2))
        path=self.prefix+'writeback.json'
        self.assertOnlyAdded(self.envelope,candidate,[path])
        self.assertEqual(unpack(candidate)[path],{
            '$schema':BASE+'Planning/Writeback/1.0.0/schema.json','writebackType':3,'destinations':[SCHEMA_FORM],
            'wbTableColumnMapping':{hours:{'visualName':'Available Hours','wbColumnName':'available_hours'}},
            'excludedMeasureGuids':[can_edit],'skippedDimensionIds':[self.dims['Version']],'numberPrecision':{'decimal':2}})
        self.assertEqual((manifest['addedParts'],manifest['changedParts']),([path],[]))
        self.assertEqual(manifest['writeback'],{'writebackType':'PIVOT_WIDE','connections':['connectionId']})
        self.assertEqual(manifest['publicSchema'][path],'passed-public-schema')
        self.assertEqual(status(candidate,path),'passed-public-schema')
        self.assertEqual(validate_plan(unpack(candidate))['sheets'],1)

    def test_layout_codes_and_no_default_layout(self):
        from runtime.planning_features import WRITEBACK_TYPES
        self.assertEqual(WRITEBACK_TYPES,{'PIVOT_LONG':2,'PIVOT_WIDE':3,'DELTA_ONLY':4,'DELTA_WIDE':5})
        request=self.writeback();request.pop('writeback_type')
        with self.assertRaisesRegex(ValueError,'writeback_type required'):self.add(writeback=request)
        with self.assertRaisesRegex(ValueError,'PIVOT_LONG, PIVOT_WIDE, DELTA_ONLY or DELTA_WIDE'):
            self.add(writeback=self.writeback(writeback_type=3))

    def test_article_form_and_portable_connection_are_refused(self):
        # SQL-backed Plans reject a destination without settings; the import never reads `connection`.
        portable={k:v for k,v in SCHEMA_FORM.items() if k!='connectionId'}
        portable['connection']={'connectionId':'00000000-0000-4000-8000-000000000001'}
        for destination in (ARTICLE_FORM,portable):
            with self.subTest(destination=destination),self.assertRaisesRegex(ValueError,'as Fabric exports it'):
                self.add(writeback=self.writeback(destinations=[copy.deepcopy(destination)]))

    def test_exported_destination_without_hash_or_with_a_variable_is_kept(self):
        no_hash={k:v for k,v in SCHEMA_FORM.items() if k!='settingsHash'}
        variable={k:v for k,v in SCHEMA_FORM.items() if k!='connectionId'};variable['connectionIdVariable']='WritebackConnection'
        candidate,manifest=self.add(writeback=self.writeback(destinations=[copy.deepcopy(no_hash),copy.deepcopy(variable)]))
        path=self.prefix+'writeback.json'
        self.assertEqual(unpack(candidate)[path]['destinations'],[no_hash,variable])
        self.assertEqual(manifest['writeback']['connections'],['connectionId','connectionIdVariable'])
        self.assertEqual((manifest['publicSchema'][path],status(candidate,path)),('schema-conflict','schema-conflict'))
        self.assertTrue(any('settingsHash' in w and 'exports' in w for w in manifest['warnings']))
        self.assertTrue(any('settings.database' in w for w in manifest['warnings']))

    def test_destination_is_copied_never_completed(self):
        for destinations in ([],[{'tableName':'wb_capacity'}],['wb_capacity'],[{**SCHEMA_FORM,'settings':None}]):
            with self.subTest(destinations=destinations),self.assertRaisesRegex(ValueError,'complete writeback destination|as Fabric exports it'):
                self.add(writeback=self.writeback(destinations=destinations))
        bad=copy.deepcopy(SCHEMA_FORM);bad['connectionId']='not-a-uuid'
        with self.assertRaisesRegex(ValueError,'published Writeback schema'):
            self.add(writeback=self.writeback(destinations=[bad]))

    def test_references_resolve_in_the_visual(self):
        hours,can_edit=self.measures['Available Hours'],self.measures['CanEdit']
        cases=[({'column_mapping':{'404':'x'}},'not a measure of this visual'),
               ({'excluded_measures':['404']},'not a measure of this visual'),
               ({'skipped_dimensions':['404']},'not a dimension of this visual'),
               ({'column_mapping':{hours:'col',can_edit:'COL'}},'column names must be unique'),
               ({'column_mapping':{hours:'col'},'excluded_measures':[hours]},'both mapped and excluded'),
               ({'number_precision':-1},'number_precision'),
               ({'writeback_filter':{'type':'none'}},'Unsupported writeback field')]
        for extra,message in cases:
            with self.subTest(extra=extra),self.assertRaisesRegex(ValueError,message):
                self.add(writeback=self.writeback(**extra))

    def test_existing_writeback_is_never_rebuilt(self):
        candidate,_=self.add(writeback=self.writeback())
        with self.assertRaisesRegex(ValueError,'writeback.json already exists'):
            self.add(candidate,writeback=self.writeback())

    def test_sheet_must_own_one_planning_visual(self):
        from runtime.planning_features import add_planning_features
        with self.assertRaisesRegex(ValueError,'Planning visual'):
            add_planning_features(self.envelope,sheet_guid='00000000-0000-4000-8000-000000000009',writeback=self.writeback())
        with self.assertRaisesRegex(ValueError,'Planning visual'):
            self.add(visual_id='00000000-0000-4000-8000-000000000009',writeback=self.writeback())
        with self.assertRaisesRegex(ValueError,'Request at least one'):self.add()


class InsertedRows(PlanningFeatureTestCase):
    def rows(self):
        region=self.dims['Region']
        return [{'name':'Manual adjustment','dimension_id':region,'row_type':'StaticRow','include_in_total':True},
                {'name':'Regional total','dimension_id':region,'row_type':'CalculatedRow','formula':'R_1+R_2',
                 'description':'Sum of two regions','column_aggregation':'Sum'}]

    def test_static_and_calculated_rows_become_a_new_part(self):
        candidate,manifest=self.add(insert_rows=self.rows())
        path=self.prefix+'insertRows.json'
        self.assertOnlyAdded(self.envelope,candidate,[path])
        part=unpack(candidate)[path]
        self.assertEqual(part['$schema'],BASE+'Planning/InsertRows/1.0.0/schema.json')
        static,calculated=part['rows']
        for row in part['rows']:
            self.assertRegex(row['id'],r'^[1-9][0-9]*$')
            self.assertEqual((row['rowMeta']['id'],row['visualId'],row['dimensionId'],row['rowMeta']['title']),
                             (row['id'],self.visual,self.dims['Region'],row['name']))
        self.assertNotEqual(static['id'],calculated['id'])
        self.assertEqual((static['name'],static['rowMeta']['row_type'],static['rowMeta']['include_in_total']),
                         ('Manual adjustment',{'StaticRow':{}},True))
        self.assertEqual(calculated['rowMeta']['row_type'],{'CalculatedRow':{'formula':'R_1+R_2','description':'Sum of two regions'}})
        self.assertEqual(calculated['rowMeta']['column_aggregation'],'Sum')
        self.assertNotIn('include_in_total',calculated['rowMeta'])
        self.assertEqual(manifest['insertedRows'],['Manual adjustment','Regional total'])
        self.assertEqual(status(candidate,path),'passed-public-schema')
        self.assertEqual(validate_plan(unpack(candidate))['sheets'],1)

    def test_exported_rows_and_schema_value_are_kept(self):
        raw=unpack(self.envelope);path=self.prefix+'insertRows.json'
        exported={'id':'1601791389093017127','visualId':self.visual,'name':'All','dimensionId':self.dims['Region'],'rowPath':None,
                  'rowMeta':{'id':'1601791389093017127','row_type':{'CalculatedRow':{'formula':'R_3+R_4','include_in_chart':False}},
                             'title':'All','level':0,'disabled':False}}
        raw[path]={'$schema':BASE+'planning/insertRows/1.0.0/schema.json','rows':[exported]}
        envelope=pack(raw)
        candidate,manifest=self.add(envelope,insert_rows=self.rows()[:1])
        part=unpack(candidate)[path]
        self.assertEqual((manifest['changedParts'],manifest['addedParts']),([path],[]))
        self.assertEqual(part['$schema'],raw[path]['$schema'])
        self.assertEqual(part['rows'][0],exported)
        self.assertEqual([r['name'] for r in part['rows']],['All','Manual adjustment'])
        old,new=parts(envelope),parts(candidate)
        self.assertEqual([p for p in old if old[p]!=new[p]],[path])
        with self.assertRaisesRegex(ValueError,'already has an inserted row named'):
            self.add(candidate,insert_rows=[{'name':'manual ADJUSTMENT','dimension_id':self.dims['Region'],'row_type':'StaticRow'}])

    def test_row_contract_is_enforced(self):
        region,month=self.dims['Region'],self.dims['Month']
        def row(**extra):return {'name':'Extra','dimension_id':region,'row_type':'StaticRow',**extra}
        cases=[(row(row_type='ForecastRow'),'StaticRow or CalculatedRow'),
               (row(row_type='CalculatedRow'),'formula'),
               (row(formula='R_1'),'apply only to a CalculatedRow'),
               (row(dimension_id='404'),'not a row dimension'),
               (row(dimension_id=month),'not a row dimension'),
               (row(column_aggregation='Median'),'column_aggregation'),
               (row(include_in_total='yes'),'include_in_total'),
               (row(name=' '),'name'),
               (row(position='top'),'Unsupported inserted-row field')]
        for spec,message in cases:
            with self.subTest(spec=spec),self.assertRaisesRegex(ValueError,message):
                self.add(insert_rows=[spec])
        with self.assertRaisesRegex(ValueError,'already has an inserted row named'):
            self.add(insert_rows=[row(),row(name='EXTRA')])
        with self.assertRaisesRegex(ValueError,'list of objects'):self.add(insert_rows=row())


class Scenarios(PlanningFeatureTestCase):
    def test_scenarios_part_from_explicit_status_and_order(self):
        hours,can_edit=self.measures['Available Hours'],self.measures['CanEdit']
        candidate,manifest=self.add(scenarios=[{'name':'Base','measure_ids':[hours],'status':'ACTIVE','order':1},
                                               {'name':'Stretch','measure_ids':[hours,can_edit],'status':'LOCK'}])
        path=self.prefix+'scenarios.json'
        self.assertOnlyAdded(self.envelope,candidate,[path])
        part=unpack(candidate)[path]
        self.assertEqual(part['$schema'],BASE+'planning/scenarios/1.0.0/schema.json')
        base,stretch=part['scenarios']
        self.assertEqual([(s['name'],s['status'],s['meta']['measureIds'],s['meta']['order']) for s in part['scenarios']],
                         [('Base','ACTIVE',[hours],1),('Stretch','LOCK',[hours,can_edit],2)])
        for scenario in part['scenarios']:
            self.assertEqual(set(scenario),{'name','status','meta'})
            self.assertEqual(set(scenario['meta']),{'measureIds','scenarioGuid','order'})
            self.assertRegex(scenario['meta']['scenarioGuid'],r'^[1-9][0-9]*$')
        self.assertNotEqual(base['meta']['scenarioGuid'],stretch['meta']['scenarioGuid'])
        self.assertEqual(manifest['scenarios'],['Base','Stretch'])
        self.assertEqual(manifest['publicSchema'][path],'schema-gap')
        self.assertTrue(any(path in w and 'pinned' in w for w in manifest['warnings']))
        self.assertTrue(any('neither reads nor exports scenarios.json' in w for w in manifest['warnings']))

    def test_status_and_first_order_have_no_default(self):
        hours=self.measures['Available Hours']
        with self.assertRaisesRegex(ValueError,'status required'):
            self.add(scenarios=[{'name':'Base','measure_ids':[hours],'order':1}])
        with self.assertRaisesRegex(ValueError,'ACTIVE or LOCK'):
            self.add(scenarios=[{'name':'Base','measure_ids':[hours],'status':'DRAFT','order':1}])
        with self.assertRaisesRegex(ValueError,'order required'):
            self.add(scenarios=[{'name':'Base','measure_ids':[hours],'status':'ACTIVE'}])

    def test_exported_scenarios_are_kept_and_extended(self):
        raw=unpack(self.envelope);path=self.prefix+'scenarios.json';hours=self.measures['Available Hours']
        exported={'name':'Scenario 1','status':'ACTIVE','autoWritebackEnabled':'INACTIVE',
                  'meta':{'measureIds':[hours],'scenarioGuid':'88480882635127202','order':1,'dimensionHash':'8018ac06b2278797'},
                  'simulations':[{'measure_simulations':{'default_filter_context_hash':{}}}]}
        raw[path]={'$schema':BASE+'planning/scenarios/1.0.0/schema.json','scenarios':[exported]}
        envelope=pack(raw)
        candidate,manifest=self.add(envelope,scenarios=[{'name':'Scenario 2','measure_ids':[hours],'status':'ACTIVE'}])
        part=unpack(candidate)[path]
        self.assertEqual((manifest['changedParts'],manifest['addedParts']),([path],[]))
        self.assertEqual(part['scenarios'][0],exported)
        self.assertEqual(part['scenarios'][1]['meta']['order'],2)
        old,new=parts(envelope),parts(candidate)
        self.assertEqual([p for p in old if old[p]!=new[p]],[path])
        with self.assertRaisesRegex(ValueError,'already exists'):
            self.add(candidate,scenarios=[{'name':'scenario 1','measure_ids':[hours],'status':'ACTIVE'}])
        with self.assertRaisesRegex(ValueError,'order 1 is taken'):
            self.add(candidate,scenarios=[{'name':'Scenario 3','measure_ids':[hours],'status':'ACTIVE','order':1}])

    def test_scenario_contract_is_enforced(self):
        hours=self.measures['Available Hours']
        def scenario(**extra):return {'name':'Base','measure_ids':[hours],'status':'ACTIVE','order':1,**extra}
        cases=[(scenario(measure_ids=['404']),'not a measure of this visual'),
               (scenario(measure_ids=[]),'measure_ids'),
               (scenario(measure_ids=[hours,hours]),'measure_ids'),
               (scenario(order=-1),'order'),
               (scenario(order=True),'order'),
               (scenario(name=''),'name'),
               (scenario(simulations=[]),'Unsupported scenario field')]
        for spec,message in cases:
            with self.subTest(spec=spec),self.assertRaisesRegex(ValueError,message):
                self.add(scenarios=[spec])
        with self.assertRaisesRegex(ValueError,'already exists'):
            self.add(scenarios=[scenario(),scenario(name='BASE',order=2)])


def template_row(title,**extra):
    return {'title':title,'include_in_total':True,'disabled':False,'distribute_parent_value_to_child':False,
            'default_value':'0','row_edit_mode':None,**extra}


class RowTemplates(PlanningFeatureTestCase):
    def test_flat_template_from_explicit_flags(self):
        candidate,manifest=self.add(row_templates=[{'title':'Opex lines','no_row_id':'',
            'rows':[template_row('Travel'),template_row('Training',include_in_total=False,row_edit_mode='Manual',default_value='')]}])
        path=self.prefix+'modelTemplate.json'
        self.assertOnlyAdded(self.envelope,candidate,[path])
        part=unpack(candidate)[path]
        self.assertEqual((part['$schema'],list(part)),(BASE+'Planning/ModelTemplate/1.0.0/schema.json',['$schema','properties']))
        [template]=part['properties']['dynamicRowTemplates']
        self.assertEqual((set(template),template['title']),({'id','title','rows'},'Opex lines'))
        travel,training=template['rows']
        ids=[template['id'],travel['id'],training['id']]
        self.assertEqual(len(set(ids)),3)
        for value in ids:self.assertRegex(value,r'^[1-9][0-9]*$')
        self.assertEqual(travel,{'id':travel['id'],'title':'Travel','include_in_total':True,'parent_id':'','level':0,
            'previous_row_id':'','disabled':False,'row_type':{'StaticRow':{'distribute_parent_value_to_child':False,
            'default_value':{'Static':'0'},'row_edit_mode':None}}})
        self.assertEqual((training['previous_row_id'],training['parent_id'],training['include_in_total']),(travel['id'],'',False))
        self.assertEqual(training['row_type']['StaticRow'],{'distribute_parent_value_to_child':False,'default_value':{'Static':''},
                                                            'row_edit_mode':'Manual'})
        self.assertEqual(manifest['rowTemplates'],['Opex lines'])
        self.assertEqual(manifest['publicSchema'][path],'schema-gap')

    def test_row_flags_and_empty_reference_have_no_default(self):
        row=template_row('Travel');row.pop('disabled');row.pop('row_edit_mode')
        with self.assertRaisesRegex(ValueError,'needs disabled, row_edit_mode; template-row flags have no default'):
            self.add(row_templates=[{'title':'Opex','no_row_id':'','rows':[row]}])
        with self.assertRaisesRegex(ValueError,'no_row_id required'):
            self.add(row_templates=[{'title':'Opex','rows':[template_row('Travel')]}])

    def test_exported_templates_are_kept_and_extended(self):
        raw=unpack(self.envelope);path=self.prefix+'modelTemplate.json'
        exported={'id':'4000000000000000001','title':'Headcount','rows':[{'id':'4000000000000000002','title':'Hires',
                  'row_type':{'StaticRow':{'distribute_parent_value_to_child':True,'default_value':{'Static':'1'},'row_edit_mode':None}},
                  'include_in_total':True,'parent_id':'','level':0,'previous_row_id':'','disabled':False,'scaling_factor':'Auto'}]}
        raw[path]={'$schema':BASE+'Planning/ModelTemplate/1.0.0/schema.json','properties':{'dynamicRowTemplates':[exported]}}
        envelope=pack(raw)
        candidate,manifest=self.add(envelope,row_templates=[{'title':'Opex','no_row_id':'','rows':[template_row('Travel')]}])
        templates=unpack(candidate)[path]['properties']['dynamicRowTemplates']
        self.assertEqual((manifest['changedParts'],templates[0],[t['title'] for t in templates]),([path],exported,['Headcount','Opex']))
        old,new=parts(envelope),parts(candidate)
        self.assertEqual([p for p in old if old[p]!=new[p]],[path])
        with self.assertRaisesRegex(ValueError,'already exists'):
            self.add(candidate,row_templates=[{'title':'headcount','no_row_id':'','rows':[template_row('Travel')]}])

    def test_template_contract_is_enforced(self):
        def template(*rows,**extra):return {'title':'Opex','no_row_id':'','rows':list(rows),**extra}
        cases=[(template(template_row('Travel',include_in_total='yes')),'include_in_total must be Boolean'),
               (template(template_row('Travel',default_value=0)),'default_value must be text'),
               (template(template_row('Travel',row_edit_mode=5)),'row_edit_mode must be text or null'),
               (template(template_row('Travel'),template_row('TRAVEL')),'Duplicate template row title'),
               (template(),'template-row entries must be a non-empty list of objects'),
               (template(template_row('Travel',parent='Opex')),'Unsupported template-row field'),
               (template(template_row('Travel'),levels=2),'Unsupported row-template field'),
               (template(template_row('Travel'),title=' '),'title must be non-empty'),
               (template(template_row('Travel'),no_row_id=0),'no_row_id must be text')]
        for spec,message in cases:
            with self.subTest(spec=spec),self.assertRaisesRegex(ValueError,message):
                self.add(row_templates=[spec])


class Routing(unittest.TestCase):
    ACTIONS={'planning-writeback','planning-insert-rows','planning-scenarios','planning-row-templates','powertable-approvals','cube-part'}

    def test_constructors_are_local_actions_routed_from_definition_contracts(self):
        from runtime.discovery import catalog
        data=catalog();modules={m['id']:m for m in data['modules']}
        self.assertLessEqual(self.ACTIONS,set(modules['DEFINITION-CONTRACTS']['operations']))
        self.assertEqual({data['actions'][a]['phase'] for a in self.ACTIONS},{'local'})
        self.assertIn('powertable-approvals',modules['POWERTABLE']['operations'])
        self.assertEqual(modules['F13']['operations'],[])
        for module in ('DEFINITION-CONTRACTS','F13'):
            self.assertNotRegex(modules[module]['limitations'],r'No constructor ships|not implemented by this package')
        guide=(ROOT/'references/definition-part-contracts.md').read_text(encoding='utf-8')
        self.assertNotIn('has no constructor for',guide)


class CommandLine(PlanningFeatureTestCase):
    def run_command(self,request,command='planning-features'):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        tmp=Path(temporary.name)
        (tmp/'request.json').write_text(json.dumps(request),encoding='utf-8')
        (tmp/'baseline.json').write_text(json.dumps(self.envelope),encoding='utf-8')
        result=subprocess.run([sys.executable,str(ROOT/'scripts/plan.py'),command,'--baseline',str(tmp/'baseline.json'),
                               '--input',str(tmp/'request.json'),'--out',str(tmp/'out')],capture_output=True,text=True,cwd=ROOT,
                              env={**os.environ,'FABRIC_SKILL_OFFLINE_TEST':'1'})
        return result,tmp/'out'

    def test_command_writes_candidate_and_manifest(self):
        result,out=self.run_command({'sheet_guid':self.sheet,
            'insert_rows':[{'name':'Manual adjustment','dimension_id':self.dims['Region'],'row_type':'StaticRow'}],
            'scenarios':[{'name':'Base','measure_ids':[self.measures['Available Hours']],'status':'ACTIVE','order':1}]})
        self.assertEqual(result.returncode,0,result.stderr)
        manifest=load(out/'changes.json');added=sorted(self.prefix+leaf for leaf in ('insertRows.json','scenarios.json'))
        self.assertEqual((manifest['addedParts'],json.loads(result.stdout)),(added,manifest))
        self.assertEqual(sorted(set(parts(load(out/'definition.json')))-set(parts(self.envelope))),added)

    def test_missing_product_value_fails_without_a_candidate(self):
        result,out=self.run_command({'sheet_guid':self.sheet,'writeback':{'destinations':[SCHEMA_FORM]}})
        self.assertEqual(result.returncode,2)
        self.assertIn('writeback_type required',result.stderr)
        self.assertFalse(out.exists())

    def test_malformed_request_fails_cleanly_without_a_candidate(self):
        scenario={'name':'Base','measure_ids':[self.measures['Available Hours']],'status':'ACTIVE','order':1}
        # The detail text comes from Python's signature binding, so only the field name is asserted.
        cases=[('planning-features',{'sheet_guid':self.sheet,'insert_row':[]},'Invalid request',"'insert_row'"),
               ('planning-features',{'scenarios':[scenario]},'Invalid request',"'sheet_guid'"),
               ('planning-features',[],'Request must be a JSON object',''),
               ('cube-part',{'sheet_guid':self.sheet},'Invalid request',"'sheet_guid'"),
               ('powertable-features',{'sheet_guid':self.sheet,'approval':{}},'Invalid request',"'approval'")]
        for command,request,error,field in cases:
            with self.subTest(command=command,request=request):
                result,out=self.run_command(request,command)
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertIn('ValueError: '+error,result.stderr)
                self.assertIn(field,result.stderr)
                self.assertNotIn('Traceback',result.stderr)
                self.assertFalse(out.exists())


if __name__=='__main__':
    unittest.main()
