"""Cube partitions, partition measures and their mappings as cube/cube.json records."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,os,subprocess,sys,tempfile,unittest,uuid
from pathlib import Path
from runtime.codec import load,pack,parts,unpack
from runtime.construct import build
from runtime.validate import schema_report,validate_plan

ROOT=Path(__file__).resolve().parents[1]
BASE='https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/'
PATH='cube/cube.json'
REGION={'id':'Region[Region]','label':'Region','type':'Column','dataType':'String','distinctValueCount':3}
MONTH={'id':'Period[Month]','label':'Month','type':'Hierarchy Level','dataType':'Int64'}
HOURS={'id':'Metrics[Hours]','label':'Hours','type':'Measure','dataType':'Number','isNative':True,'aggregationType':'Sum'}
NUMERIC_IDS=('id','cubePartitionId','cubePartitionMeasureId','dataInputColumnId','visualId')


def partition(**extra):
    return {'name':'Breakdown 1','dimensions':[REGION],'time_dimensions':[MONTH],'measures':[HOURS],**extra}


def measure(**extra):
    return {'name':'Available Hours','type':'NUMBER','config':{'label':'Available Hours','data_type':'Number'},**extra}


class CubePart(unittest.TestCase):
    def setUp(self):
        raw=build(load(ROOT/'assets/fixtures/model.json'),load(ROOT/'assets/fixtures/capacity-spec.json'))['raw']
        sheet=raw['definition.json']['sheets'][0]
        self.sheet,self.visual=sheet['recordGuid'],sheet['workloadItemEntityVisuals'][0]['visualId']
        columns=raw[f'sheets/{self.sheet}/visuals/{self.visual}/dataInput.json']['columns']
        self.hours=next(c['measureGuid'] for c in columns if c['name']=='Available Hours')
        self.raw=raw;self.envelope=pack(raw)

    def add(self,envelope=None,**request):
        from runtime.cube_part import add_cube_part
        return add_cube_part(envelope or self.envelope,**request)

    def input_mapping(self,**extra):
        return {'measure':'Available Hours','partition':'Breakdown 1','sheet_guid':self.sheet,'measure_guid':self.hours,**extra}

    def test_new_cube_part_links_records_by_record_guid(self):
        candidate,manifest=self.add(partitions=[partition()],measures=[measure()],
                                    measure_mappings=[{'partition':'Breakdown 1','measure':'Available Hours'}],
                                    input_mappings=[self.input_mapping()])
        old,new=parts(self.envelope),parts(candidate)
        self.assertEqual(sorted(set(new)-set(old)),[PATH])
        self.assertTrue(all(new[p]==b for p,b in old.items()))
        part=unpack(candidate)[PATH]
        self.assertEqual(part['$schema'],BASE+'cube/1.0.0/schema.json')
        [cube],[number],[link],[column]=(part[k] for k in ('cubePartitions','cubePartitionMeasures',
            'cubePartitionMeasureMappings','cubePartitionMeasureDataInputColumnMappings'))
        for record in (cube,number,link,column):
            uuid.UUID(record['recordGuid'])
            self.assertFalse(set(NUMERIC_IDS)&set(record),record)
        self.assertEqual(cube,{'recordGuid':cube['recordGuid'],'name':'Breakdown 1','dimensions':[REGION],'timeDimensions':[MONTH],
                               'measures':[HOURS],'rowCount':0})
        self.assertEqual(number,{'recordGuid':number['recordGuid'],'name':'Available Hours','type':'NUMBER',
                                 'config':{'label':'Available Hours','data_type':'Number'}})
        self.assertEqual(link,{'recordGuid':link['recordGuid'],'cubePartition_RefId':cube['recordGuid'],
                               'cubePartitionMeasure_RefId':number['recordGuid']})
        self.assertEqual(column,{'recordGuid':column['recordGuid'],'dataInputColumnMeasureGuid':self.hours,
                                 'cubePartitionMeasure_RefId':number['recordGuid'],'visual_RefId':self.visual,
                                 'cubePartition_RefId':cube['recordGuid']})
        self.assertEqual((manifest['partitions'],manifest['measures'],manifest['measureMappings'],manifest['inputMappings']),
                         (['Breakdown 1'],['Available Hours'],1,1))
        # The published oneOf for data_type matches Number twice, so the documented value is reported as a reviewed deviation.
        self.assertEqual((manifest['addedParts'],manifest['publicSchema'][PATH]),([PATH],'passed-native-extension'))
        report=next(i for i in schema_report(unpack(candidate)) if i['path']==PATH)
        self.assertEqual(report['status'],'passed-native-extension')
        self.assertIn('Number and Text',report['reason'])
        plain=copy.deepcopy(unpack(candidate)[PATH]);plain['cubePartitionMeasures'][0]['config'].pop('data_type')
        self.assertEqual(schema_report({PATH:plain})[0]['status'],'passed-public-schema')
        self.assertEqual(validate_plan(unpack(candidate))['sheets'],1)

    def test_measure_type_has_no_default(self):
        from runtime.cube_part import MEASURE_TYPES
        self.assertEqual(MEASURE_TYPES,('FORECAST','NUMBER','FORMULA'))
        spec=measure();spec.pop('type')
        with self.assertRaisesRegex(ValueError,'type required'):self.add(measures=[spec])
        with self.assertRaisesRegex(ValueError,'FORECAST, NUMBER or FORMULA'):self.add(measures=[measure(type='PERCENT')])

    def test_exported_records_and_reference_form_are_kept(self):
        exported={'$schema':BASE+'cube/1.0.0/schema.json',
            'cubePartitions':[{'id':7,'status':'ACTIVE','recordGuid':'00000000-0000-4000-8000-000000000071','name':'Breakdown 1',
                               'dimensions':[REGION],'timeDimensions':[MONTH],'measures':[HOURS],'rowCount':0}],
            'cubePartitionMeasures':[{'id':11,'recordGuid':'00000000-0000-4000-8000-000000000111','name':'Plan','type':'NUMBER','config':{}}],
            'cubePartitionMeasureMappings':[{'id':3,'recordGuid':'00000000-0000-4000-8000-000000000031','cubePartitionId':7,'cubePartitionMeasureId':11}],
            'cubePartitionMeasureDataInputColumnMappings':[]}
        raw=copy.deepcopy(self.raw);raw[PATH]=exported;envelope=pack(raw)
        candidate,manifest=self.add(envelope,measures=[measure()],measure_mappings=[{'partition':'breakdown 1','measure':'Available Hours'}])
        part=unpack(candidate)[PATH]
        self.assertEqual((manifest['changedParts'],manifest['addedParts']),([PATH],[]))
        for key,records in exported.items():
            if key!='$schema':self.assertEqual(part[key][:len(records)],records)
        self.assertEqual(part['$schema'],exported['$schema'])
        self.assertEqual(part['cubePartitionMeasureMappings'][1]['cubePartition_RefId'],'00000000-0000-4000-8000-000000000071')
        self.assertTrue(any('numeric' in w for w in manifest['warnings']))
        old,new=parts(envelope),parts(candidate)
        self.assertEqual([p for p in old if old[p]!=new[p]],[PATH])
        with self.assertRaisesRegex(ValueError,'already linked'):
            self.add(candidate,measure_mappings=[{'partition':'Breakdown 1','measure':'Available Hours'}])
        # The exported mapping links partition 7 and measure 11 by numeric ID; that link counts too.
        with self.assertRaisesRegex(ValueError,'Partition measure Plan is already linked to cube partition Breakdown 1'):
            self.add(envelope,measure_mappings=[{'partition':'Breakdown 1','measure':'Plan'}])

    def test_names_and_references_resolve(self):
        cases=[({'partitions':[partition(),partition(name='BREAKDOWN 1')]},'partition named'),
               ({'measures':[measure(),measure(name='available hours')]},'partition measure named'),
               ({'measure_mappings':[{'partition':'Missing','measure':'Available Hours'}],'measures':[measure()]},'No cube partition named Missing'),
               ({'measure_mappings':[{'partition':'Breakdown 1','measure':'Missing'}],'partitions':[partition()]},'No partition measure named Missing'),
               ({'input_mappings':[self.input_mapping(measure_guid='404')],'measures':[measure()],'partitions':[partition()]},'not a measure of this visual'),
               ({'input_mappings':[self.input_mapping(sheet_guid='00000000-0000-4000-8000-000000000009')],'measures':[measure()]},'Planning visual'),
               ({'partitions':[partition(dimensions=[{**REGION,'lookups':[]}])]},'invalid dimension contract'),
               ({'partitions':[partition(dimensions=[],time_dimensions=[])]},'at least one dimension'),
               ({'partitions':[partition(dimensions=[REGION,REGION])]},'Duplicate dimension'),
               ({'measures':[measure(config={'label':'x','owner':'me'})]},'cubePartitionMeasures/0/config'),
               ({'measures':[measure(config='x')]},'config must be an object'),
               ({'partitions':[partition(row_count=5)]},'Unsupported partition field'),
               ({},'Request at least one')]
        for request,message in cases:
            with self.subTest(request=request),self.assertRaisesRegex(ValueError,message):
                self.add(**request)

    def test_command_appends_cube_records(self):
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        tmp=Path(temporary.name)
        request={'partitions':[partition()],'measures':[measure()],'measure_mappings':[{'partition':'Breakdown 1','measure':'Available Hours'}]}
        (tmp/'request.json').write_text(json.dumps(request),encoding='utf-8')
        (tmp/'baseline.json').write_text(json.dumps(self.envelope),encoding='utf-8')
        result=subprocess.run([sys.executable,str(ROOT/'scripts/plan.py'),'cube-part','--baseline',str(tmp/'baseline.json'),
                               '--input',str(tmp/'request.json'),'--out',str(tmp/'out')],capture_output=True,text=True,cwd=ROOT,
                              env={**os.environ,'FABRIC_SKILL_OFFLINE_TEST':'1'})
        self.assertEqual(result.returncode,0,result.stderr)
        manifest=load(tmp/'out/changes.json')
        self.assertEqual((manifest['addedParts'],manifest['measureMappings']),([PATH],1))
        self.assertEqual(unpack(load(tmp/'out/definition.json'))[PATH]['cubePartitions'][0]['name'],'Breakdown 1')


if __name__=='__main__':
    unittest.main()
