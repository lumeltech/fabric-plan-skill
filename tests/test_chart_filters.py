import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,unittest
from runtime.chart_filters import ensure_chart_filters,audit_chart_filters,chart_field_filter
from runtime.intelligence import card
from runtime.identity import Registry

def field(name='Pay',bucket='AC',role='Measure',source='InfoBridge'):
    key='7[18446744073709551614]' if source=='InfoBridge' else 'Facts['+name+']'
    a={'id':key,'sourceId':key,'columnName':name,'tableName':'Current Output' if source=='InfoBridge' else 'Facts',
       'sourceType':source,'columnType':'Column','dataType':'Double','dataRoleType':role,
       'bucketId':bucket,'order':0,'customName':'Displayed '+name}
    if source=='InfoBridge':a['queryId']='7'
    if role=='Measure':a['aggregationType']='sum'
    return a

class ChartFilterTests(unittest.TestCase):
    def test_card_factory_and_hidden_scope_are_not_interchangeable(self):
        a=field();a['measureGuid']='901'
        p=card({'fields':[]},{'field':a['id'],'label':'Pay','aggregation':'sum'},Registry(),query_fields=[a])
        self.assertEqual(audit_chart_filters(p)['assignedFields'],1)
        scope={'superFilterAssignments':[{'filter':[{'selected':'Budget'}]}]}
        p['visualState']['embeddedSuperFilter']=copy.deepcopy(scope)
        p['superFilterAssignments']=[]
        with self.assertRaises(ValueError):audit_chart_filters(p)
        ensure_chart_filters(p)
        self.assertEqual(p['visualState']['embeddedSuperFilter'],scope)
        self.assertEqual(p['superFilterAssignments'][0]['filter'],[])
        self.assertEqual(p['superFilterAssignments'][0]['pivotAssignments'][0]['id'],a['id'])

    def test_grouped_comparison_fields_each_get_own_filter(self):
        dim=field('Region','axis','Grouping','PowerBI');dim['dataType']='String'
        a=field();b=field('Pay','PY');b['aggregationType']='max'
        p={'pivotAssignments':[dim,a,b]};ensure_chart_filters(p)
        self.assertEqual(audit_chart_filters(p)['visibleFieldFilters'],3)
        regs=p['superFilterAssignments']
        self.assertEqual(regs[1]['pivotAssignments'],[dim,a])
        self.assertEqual(regs[2]['pivotAssignments'],[dim,b])
        # A saved 'max' is written back as the product's 'maximum'.
        self.assertEqual(regs[2]['configuration']['sheetDataItemAggregationType'],'maximum')
        self.assertEqual(regs[2]['bucketId'],'AC')
        # A dimension used to evaluate a measure is not its own field card.
        p['superFilterAssignments']=regs[1:]
        with self.assertRaises(ValueError):audit_chart_filters(p)

    def test_repeated_repair_preserves_selection_context_and_geometry(self):
        a=field();context={'isContextDimension':True,'pivotAssignments':[field('Scenario','Category','Grouping','PowerBI')],'filter':[{'chosen':'Budget'}]}
        p={'pivotAssignments':[a],'superFilterAssignments':[context],
           'position':{'x':24,'y':300},'dimension':{'width':450,'height':130}}
        ensure_chart_filters(p);r=p['superFilterAssignments'][1]
        r['filter']=[{'filterType':'RANGE','rangeFilter':[{'from':100}]}]
        r['configuration']['isExpanded']=True;r['configuration']['sort'][0]['direction']='DESC'
        before=copy.deepcopy(p);ensure_chart_filters(p)
        self.assertEqual(p,before);audit_chart_filters(p)

    def test_semantic_dax_and_aggregated_columns_are_distinct(self):
        a=field('Revenue',source='PowerBI');a['columnType']='Measure';a.pop('aggregationType')
        b=field('Units',source='PowerBI')
        p={'pivotAssignments':[a,b]};ensure_chart_filters(p);audit_chart_filters(p)
        self.assertTrue(p['superFilterAssignments'][0]['isDaxMeasure'])
        self.assertFalse(p['superFilterAssignments'][1]['isDaxMeasure'])
        self.assertNotIn('aggregationType',p['superFilterAssignments'][0]['pivotAssignments'][0])

    def test_stale_nested_query_and_sort_identity_are_rejected(self):
        for mutate in (lambda r:r['pivotAssignments'][0].update(queryId='8'),
                       lambda r:r['configuration']['sort'][0].update(columnId='7[11]')):
            p={'pivotAssignments':[field()]};ensure_chart_filters(p);mutate(p['superFilterAssignments'][0])
            with self.assertRaises(ValueError):audit_chart_filters(p)

    def test_hidden_or_duplicate_registration_does_not_pass(self):
        for change in ('hide','duplicate'):
            p={'pivotAssignments':[field()]};ensure_chart_filters(p)
            if change=='hide':p['superFilterAssignments'][0]['configuration']['hide']=True
            else:p['superFilterAssignments'].append(copy.deepcopy(p['superFilterAssignments'][0]))
            with self.assertRaises(ValueError):audit_chart_filters(p)

    def test_dimension_numeric_type_keeps_grouping_role(self):
        a=field('Year','axis','Grouping','PowerBI');a['dataType']='Int64'
        p={'pivotAssignments':[a]};ensure_chart_filters(p);audit_chart_filters(p)
        r=p['superFilterAssignments'][0]
        self.assertEqual(r['configuration']['visualType'],'NUMERIC')
        self.assertFalse(r['isDefaultMeasure']);self.assertFalse(r['isDaxMeasure'])
