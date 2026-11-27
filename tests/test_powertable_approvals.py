"""PowerTable approval workflow (rule type, levels, routing filters) as a public definition part."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,os,subprocess,sys,tempfile,unittest,uuid
from pathlib import Path
from runtime.codec import load,pack,parts,unpack
from runtime.construct import build
from runtime.powertable_factory import add_table_to_definition,table_from_request
from runtime.powertable_features import add_features
from runtime.validate import check_powertable_parts,schema_report,validate_plan
from tests.test_powertable_defaults import request as table_request

ROOT=Path(__file__).resolve().parents[1]
BASE='https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/'


LOOKUP={'tableName':'Approvers','approverColumn':'ApproverEmail',
        'conditionalColumn':[{'columnName':'Region','lookupColumnName':'Region'}]}


def workflow(**extra):
    return {'rule_type':'MANUAL','persist_flag':'SAVE_BEFORE_REVIEW','multi_level_enabled':True,
            'levels':[{'name':'Manager','description':'Line manager'},{'name':'Finance','description':''}],
            'filters':[{'name':'All rows','filter':None,'order':0}],**extra}


class ApprovalWorkflow(unittest.TestCase):
    def setUp(self):
        model=load(ROOT/'assets/fixtures/model.json');spec=load(ROOT/'assets/fixtures/capacity-spec.json')
        sheet,new,self.ids=table_from_request(table_request())
        self.envelope=add_table_to_definition(pack(build(model,spec)['raw']),sheet,new)
        self.prefix=next(k.rsplit('source.json',1)[0] for k in new if k.endswith('/source.json'))
        self.path=self.prefix+'approvals.json'

    def add(self,envelope=None,**request):
        return add_features(envelope or self.envelope,sheet_guid=self.ids['sheetGuid'],**request)

    def test_workflow_is_one_new_nested_record(self):
        candidate,manifest=self.add(approvals=workflow())
        old,new=parts(self.envelope),parts(candidate)
        self.assertEqual(sorted(set(new)-set(old)),[self.path])
        self.assertTrue(all(new[p]==b for p,b in old.items()))
        part=unpack(candidate)[self.path];record=part['approvals']
        uuid.UUID(record.pop('recordGuid'))
        self.assertEqual(part,{'$schema':BASE+'PowerTable/Approvals/1.0.0/schema.json','approvals':{
            'sourceId':self.ids['sourceGuid'],'ruleType':20,'persistFlag':20,'approvalLevel':2,'multiLevelEnabled':1,
            'approvalLevels':[{'name':'Manager','description':'Line manager','level':1},{'name':'Finance','description':'','level':2}],
            'approvalFilter':[{'name':'All rows','filter':None,'order':0}]}})
        merged=unpack(candidate)
        self.assertEqual(check_powertable_parts(merged,self.prefix)['approvals'],1)
        self.assertEqual(next(i['status'] for i in schema_report(merged) if i['path']==self.path),'passed-public-schema')
        self.assertEqual(manifest['addedApprovals'],{'ruleType':'MANUAL','levels':['Manager','Finance']})
        self.assertEqual(manifest['addedParts'],[self.path])
        self.assertTrue(any('top level' in w for w in manifest['warnings']))
        self.assertEqual(manifest['approvers'],'not in definition; no supported public route')
        self.assertEqual(validate_plan(merged)['sheets'],2)

    def test_codes_and_single_level(self):
        from runtime.powertable_features import APPROVAL_RULES,PERSIST_FLAGS
        self.assertEqual((APPROVAL_RULES,PERSIST_FLAGS),({'DEFAULT':10,'MANUAL':20,'LOOKUP':30},
                                                         {'SAVE_AFTER_REVIEW':10,'SAVE_BEFORE_REVIEW':20}))
        candidate,_=self.add(approvals=workflow(rule_type='LOOKUP',persist_flag='SAVE_AFTER_REVIEW',multi_level_enabled=False,
                                                filters=[],levels=[{'name':'Owner','description':'Data owner'}],lookup_config=LOOKUP))
        record=unpack(candidate)[self.path]['approvals']
        self.assertEqual((record['ruleType'],record['persistFlag'],record['multiLevelEnabled'],record['approvalFilter']),(30,10,0,[]))
        self.assertEqual((record['approvalLevel'],record['settings']),(1,{'lookupConfig':LOOKUP}))

    def test_lookup_rule_needs_its_approver_table(self):
        cases=[({'rule_type':'LOOKUP'},'needs lookup_config'),
               ({'rule_type':'MANUAL','lookup_config':LOOKUP},'only to a LOOKUP rule'),
               ({'rule_type':'LOOKUP','lookup_config':{**LOOKUP,'conditionalColumn':[]}},'conditionalColumn'),
               ({'rule_type':'LOOKUP','lookup_config':{'tableName':'Approvers'}},'needs tableName')]
        for change,message in cases:
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,message):
                self.add(approvals=workflow(**change))

    def test_multi_level_flag_is_written_only_as_stated(self):
        one=[{'name':'Owner','description':''}];two=workflow()['levels']
        for levels,flag,code in ((one,True,1),(two,False,0)):
            with self.subTest(levels=len(levels),flag=flag):
                candidate,_=self.add(approvals=workflow(levels=levels,multi_level_enabled=flag))
                self.assertEqual(unpack(candidate)[self.path]['approvals']['multiLevelEnabled'],code)
        # A request without the flag still works, and nothing is derived from the two levels.
        request=workflow();request.pop('multi_level_enabled')
        merged=unpack(self.add(approvals=request)[0])
        self.assertNotIn('multiLevelEnabled',merged[self.path]['approvals'])
        self.assertEqual(check_powertable_parts(merged,self.prefix)['approvals'],1)
        self.assertEqual(next(i['status'] for i in schema_report(merged) if i['path']==self.path),'passed-public-schema')
        with self.assertRaisesRegex(ValueError,'multi_level_enabled must be Boolean'):
            self.add(approvals=workflow(multi_level_enabled=1))

    def test_rule_type_persist_flag_and_first_filter_order_have_no_default(self):
        cases=[({'rule_type':None},'rule_type required'),({'rule_type':'AUTO'},'DEFAULT, MANUAL or LOOKUP'),
               ({'persist_flag':None},'persist_flag required'),({'persist_flag':10},'SAVE_AFTER_REVIEW or SAVE_BEFORE_REVIEW'),
               ({'filters':[{'name':'All rows','filter':None}]},'order required')]
        for change,message in cases:
            spec=workflow(**change);spec={k:v for k,v in spec.items() if v is not None}
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,message):
                self.add(approvals=spec)

    def test_level_and_filter_contract(self):
        level={'name':'Manager','description':''}
        cases=[(workflow(levels=[]),'at least one approval level'),
               (workflow(levels=[{'name':'Manager'}]),'name and description'),
               (workflow(levels=[{**level,'approvers':['a@example.com']}]),'name and description'),
               (workflow(levels=[level,{'name':'MANAGER','description':''}]),'Duplicate approval level'),
               (workflow(filters=[{'name':'Region','filter':'Region = West','order':0}]),'object or null'),
               (workflow(filters=[{'name':'A','filter':{},'order':0},{'name':'B','filter':{},'order':0}]),'order 0 is taken'),
               (workflow(filters=[{'name':'A','filter':{},'order':-1}]),'nonnegative'),
               (workflow(filters=[{'name':'A','filter':{},'order':0},{'name':'a','filter':{},'order':1}]),'Duplicate approval filter'),
               (workflow(approvers=['a@example.com']),'Unsupported approval field')]
        for spec,message in cases:
            with self.subTest(spec=spec),self.assertRaisesRegex(ValueError,message):
                self.add(approvals=spec)

    def test_one_workflow_per_table_and_forms_stay_independent(self):
        fields=[{'column':c} for c in ('Code','FullName','JoinDate','Active')]
        candidate,manifest=self.add(approvals=workflow(),forms=[{'title':'Intake','fields':fields}])
        self.assertEqual(sorted(p.rsplit('/',1)[-1] for p in manifest['addedParts']),['approvals.json','forms.json'])
        with self.assertRaisesRegex(ValueError,'approvals.json already exists'):
            self.add(candidate,approvals=workflow())
        again,manifest=self.add(candidate,forms=[{'title':'Second','fields':fields}])
        self.assertIsNone(manifest['addedApprovals'])
        self.assertEqual(parts(again)[self.path],parts(candidate)[self.path])

    def test_new_forms_use_product_defaults(self):
        fields=[{'column':c} for c in ('Code','FullName','JoinDate','Active')]
        candidate,_=self.add(forms=[{'title':'Intake','fields':fields}])
        form=unpack(candidate)[self.prefix+'forms.json']['forms'][0]
        self.assertEqual((form['restrictMultipleEntry'],form['config']['showLogo']),(0,True))

    def test_powertable_features_command_adds_the_workflow(self):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        tmp=Path(temporary.name)
        (tmp/'request.json').write_text(json.dumps({'sheet_guid':self.ids['sheetGuid'],'approvals':workflow()}),encoding='utf-8')
        (tmp/'baseline.json').write_text(json.dumps(self.envelope),encoding='utf-8')
        result=subprocess.run([sys.executable,str(ROOT/'scripts/plan.py'),'powertable-features','--baseline',str(tmp/'baseline.json'),
                               '--input',str(tmp/'request.json'),'--out',str(tmp/'out')],capture_output=True,text=True,cwd=ROOT,
                              env={**os.environ,'FABRIC_SKILL_OFFLINE_TEST':'1'})
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(load(tmp/'out/changes.json')['addedApprovals'],{'ruleType':'MANUAL','levels':['Manager','Finance']})
        self.assertIn(self.path,unpack(load(tmp/'out/definition.json')))


if __name__=='__main__':
    unittest.main()
