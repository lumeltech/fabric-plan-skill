import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy
import unittest
from runtime.codec import load
from runtime.construct import build, field
from runtime.identity import Registry, xxh3
from runtime.intelligence import card, column_chart
from runtime.chart_filters import audit_chart_filters
from runtime.measure_bindings import registered_measure, resolve_measure
from runtime.planning_presentation import build_application
from runtime.semantic_values import semantic_value
from runtime.validate import validate_plan
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def model_spec():
    model=load(ROOT/'assets/fixtures/model.json')
    model['fields']=[
        {'id':t+'['+c+']','tableName':t,'columnName':c,'dataType':d,'columnType':k}
        for t,c,d,k in [('Area','Name','String','Column'),('Area','Code','Int64','Column'),
                       ('Period','Month','String','Column'),('Facts','Amount','Double','Column'),
                       ('Facts','Rate','Double','Column'),('Metrics','Baseline','Double','Measure')]]
    spec={'name':'Column-based estimates','requiredCapabilities':['planning.native-measure'],
          'sheets':[{'name':'Estimates','rows':['Area[Name]'],'columns':['Period[Month]'],
                     'measures':[{'key':'amount','kind':'Native','source':'Facts[Amount]','label':'Estimate'},
                                 {'key':'rate','kind':'Native','source':'Facts[Rate]','label':'Rate',
                                  'aggregation':'None','columnAggregation':'None'}]}]}
    return model,spec


class SemanticValueTests(unittest.TestCase):
    def test_complete_application_with_no_explicit_dax_measures(self):
        model,spec=model_spec();model['fields']=[f for f in model['fields'] if f['columnType']!='Measure']
        result=build_application(model,spec)
        self.assertEqual(result['defaultsCheck']['planningOwners'],1)
        self.assertEqual(result['defaultsCheck']['dashboardsWithPageNavigator'],1)
        found=0
        for path,obj in result['raw'].items():
            if not path.endswith('/properties.json'):continue
            p=obj['properties']
            for a in p.get('pivotAssignments',[]):
                if a.get('sourceType')=='PowerBI' and a.get('dataRoleType')=='Measure':
                    self.assertEqual(a['columnType'],'Column')
                    self.assertEqual(a['aggregationType'],'sum');self.assertTrue(a['customSource'])
                    self.assertEqual(a['measureGuid'],str(xxh3('SUM__'+a['id'])))
                    found+=1
            if 'manage_measures' in p.get('visualState',{}):
                rid=next(a['measureGuid'] for a in p['pivotAssignments'] if a['id']=='Facts[Rate]')
                self.assertEqual(p['visualState']['aggregation_config']['measure_aggregation'][rid],{'row':'None','column':'None'})
            elif p.get('visualType')==50:audit_chart_filters(p)
        self.assertGreaterEqual(found,3)

    def test_grid_totals_do_not_determine_source_query(self):
        m,s=model_spec();s['sheets'][0]['measures'][0].update(aggregation='Min',columnAggregation='Max')
        b=build(m,s);p=next(o['properties'] for k,o in b['raw'].items() if k.endswith('/properties.json') and 'manage_measures' in o['properties'].get('visualState',{}))
        a=next(x for x in p['pivotAssignments'] if x['id']=='Facts[Amount]')
        self.assertEqual(a['aggregationType'],'sum')
        self.assertEqual(p['visualState']['aggregation_config']['measure_aggregation'][a['measureGuid']],{'row':'Min','column':'Max'})

    def test_all_native_grid_aggregation_variants_are_preserved(self):
        scalar=('Sum','Formula','Min','Max','Average','AverageLeaf','StandardDeviation',
            'VisibleRounding','First','Last','None','Earliest','Latest','Median','Variance',
            'DistinctCount','Count','Subtraction','Product','Division','AverageExclusiveZero','VisualSum')
        for aggregation in scalar:
            with self.subTest(aggregation=aggregation):
                model,spec=model_spec()
                spec['sheets'][0]['measures'][0]['aggregation']=aggregation
                result=build(model,spec)
                props=next(o['properties'] for k,o in result['raw'].items()
                    if k.endswith('/properties.json') and 'manage_measures' in o['properties'].get('visualState',{}))
                measure=next(x for x in props['pivotAssignments'] if x['id']=='Facts[Amount]')
                self.assertEqual(props['visualState']['aggregation_config']['measure_aggregation'][measure['measureGuid']]['row'],aggregation)
        model,spec=model_spec()
        spec['sheets'][0]['measures'][0].update(
            aggregation={'WeightedAverage':'rate'},columnAggregation={'WeightedAverageRow':'701'})
        result=build(model,spec)
        props=next(o['properties'] for k,o in result['raw'].items()
            if k.endswith('/properties.json') and 'manage_measures' in o['properties'].get('visualState',{}))
        amount=next(x for x in props['pivotAssignments'] if x['id']=='Facts[Amount]')
        rate=next(x for x in props['pivotAssignments'] if x['id']=='Facts[Rate]')
        self.assertEqual(props['visualState']['aggregation_config']['measure_aggregation'][amount['measureGuid']],{
            'row':{'WeightedAverage':rate['measureGuid']},'column':{'WeightedAverageRow':'701'}})

    def test_weighted_average_dependency_is_structurally_resolved(self):
        model,spec=model_spec()
        spec['sheets'][0]['measures'][0].update(
            aggregation={'WeightedAverage':'rate'},columnAggregation={'WeightedAverageRow':'701'})
        result=build(model,spec)
        key=next(k for k in result['raw'] if k.endswith('/properties.json')
                 and 'manage_measures' in result['raw'][k]['properties'].get('visualState',{}))
        amount=next(x for x in result['raw'][key]['properties']['pivotAssignments'] if x['id']=='Facts[Amount]')
        rate=next(x for x in result['raw'][key]['properties']['pivotAssignments'] if x['id']=='Facts[Rate]')
        self.assertEqual(validate_plan(result['raw'])['measureRecords'],len(spec['sheets'][0]['measures']))
        pair=result['raw'][key]['properties']['visualState']['aggregation_config']['measure_aggregation'][amount['measureGuid']]
        self.assertEqual(pair['row'],{'WeightedAverage':rate['measureGuid']})
        raw=copy.deepcopy(result['raw'])
        registered=raw[key]['properties']['visualState']['aggregation_config']['measure_aggregation']
        # A weight that is not one of the grid's measures cannot be resolved on import.
        registered[amount['measureGuid']]={**pair,'row':{'WeightedAverage':'9999999999999999999'}}
        with self.assertRaisesRegex(ValueError,'Unresolved weighted-average measure'):validate_plan(raw)
        # The aggregation contract refuses a reference that is not even a native id.
        registered[amount['measureGuid']]={**pair,'row':{'WeightedAverage':'ghost'}}
        with self.assertRaisesRegex(ValueError,'decimal u64'):validate_plan(raw)
        registered[amount['measureGuid']]=pair
        self.assertEqual(validate_plan(raw)['status'],'passed-structural-invariants')

    def test_explicit_source_override_and_average_alias(self):
        m,s=model_spec();s['sheets'][0]['measures'][1]['sourceAggregation']='Average'
        from runtime.scope import prepare_scope
        from runtime.workflow import SUPPORTED
        prepared=prepare_scope(s,SUPPORTED,m)
        self.assertEqual(prepared['spec']['sheets'][0]['measures'][1]['sourceAggregation'],'Average')
        b=build_application(m,s)
        p=next(o['properties'] for k,o in b['raw'].items() if k.endswith('/properties.json') and 'manage_measures' in o['properties'].get('visualState',{}))
        a=next(x for x in p['pivotAssignments'] if x['id']=='Facts[Rate]')
        self.assertEqual(a['aggregationType'],'average')
        self.assertEqual(a['measureGuid'],str(xxh3('AVERAGE__Facts[Rate]')))
        c=card(m,{'field':'Facts[Rate]','label':'Average rate','aggregation':'avg'},Registry())
        self.assertEqual(c['pivotAssignments'][0]['aggregationType'],'average')

    def test_card_default_and_comparison_mixed_source_kinds(self):
        m,_=model_spec()
        self.assertEqual(card(m,{'field':'Facts[Amount]','label':'Total'},Registry())['pivotAssignments'][0]['aggregationType'],'sum')
        p=column_chart(m,{'category':'Area[Name]','field':'Facts[Amount]','comparisonField':'Metrics[Baseline]','label':'Estimate vs baseline'},Registry())
        audit_chart_filters(p)
        a={x['id']:x for x in p['pivotAssignments']}
        self.assertEqual(a['Facts[Amount]']['aggregationType'],'sum')
        self.assertNotIn('aggregationType',a['Metrics[Baseline]'])
        self.assertEqual(a['Metrics[Baseline]']['columnType'],'Measure')
        p=column_chart(m,{'category':'Area[Name]','field':'Facts[Amount]','comparisonField':'Facts[Rate]','comparisonAggregation':'max','label':'Selected comparison'},Registry())
        self.assertEqual(next(a for a in p['pivotAssignments'] if a['id']=='Facts[Rate]')['aggregationType'],'maximum')

    def test_column_chart_category_uses_the_axis_bucket(self):
        m,_=model_spec()
        p=column_chart(m,{'category':'Area[Name]','field':'Facts[Amount]','label':'Amount by area'},Registry())
        self.assertEqual(next(a for a in p['pivotAssignments'] if a['id']=='Area[Name]')['bucketId'],'axis')

    def test_non_sum_aggregations_use_product_names_and_prefixes(self):
        m,_=model_spec()
        for alias,name in (('avg','average'),('min','minimum'),('max','maximum'),('minimum','minimum'),('sum','sum')):
            with self.subTest(alias=alias):
                registry=Registry();a=semantic_value(m,'Facts[Amount]',registry,aggregation=alias)
                self.assertEqual(a['aggregationType'],name)
                self.assertEqual(a['measureGuid'],str(xxh3(name.upper()+'__Facts[Amount]')))

    def test_grouping_and_dax_are_not_reaggregated(self):
        m,_=model_spec();a=field(m,'Area[Code]','rows',0)
        self.assertNotIn('aggregationType',a)
        d=resolve_measure({'sourceType':'PowerBI','fieldId':'Metrics[Baseline]'},model=m)
        self.assertNotIn('aggregationType',d)
        with self.assertRaisesRegex(ValueError,'reaggregate'):
            semantic_value(m,'Metrics[Baseline]',Registry(),aggregation='sum')
        with self.assertRaisesRegex(ValueError,'numeric'):
            semantic_value(m,'Area[Name]',Registry())
        with self.assertRaisesRegex(ValueError,'Unsupported'):
            semantic_value(m,'Facts[Amount]',Registry(),aggregation='nonsense')

    def test_existing_ui_aggregation_change_retains_registered_identity(self):
        m,_=model_spec()
        a=semantic_value(m,'Facts[Amount]',Registry(),aggregation='average')
        old=a['measureGuid'];a['aggregationType']='sum'
        p={'pivotAssignments':[a],'visualState':{'manage_measures':[{'id':old}]}}
        record={'id':'17','visualId':'2','measureGuid':old,'name':'Amount',
                'columnMeta':{'id':old,'measure_type':{'Native':{'measure_role':'ACMeasure'}}}}
        out=registered_measure(p,record,'2','Owner',model=m)
        self.assertEqual(out['aggregationType'],'sum');self.assertEqual(out['measureGuid'],old)
        before=copy.deepcopy(p);registered_measure(p,record,'2','Owner',model=m)
        self.assertEqual(p,before)
        a.pop('aggregationType')
        with self.assertRaisesRegex(ValueError,'persisted source column aggregation'):
            registered_measure(p,record,'2','Owner',model=m)


if __name__=='__main__':unittest.main()
