import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,unittest
from runtime.bridge import Query,planning_source,portable,validate_graph,reconcile_execution
from runtime.bridge_operations import *

def field(n,typ='VARCHAR',id=None):return {'id':id or n+'-id','name':n,'alias':n,'type':typ, **({'measureGuid':id or n+'-id','columnType':'DI','isHierarchyColumn':False} if typ=='DOUBLE' else {})}
def catalog(extra=False):
    return {'dimensions':[field('Region'),field('Employee')],'columns':[field('Month')],
            'measures':[field('Pay','DOUBLE')]+([field('Variance','DOUBLE')] if extra else [])}
def branch(title='one',extra=False):
    return Query(title,'src',catalog(extra),query_id='Q'+title).load_planning().pivot(['Region'],['Month'],{n:'sum' for n in (['Pay','Variance'] if extra else ['Pay'])}).result({})
def sources_for(*queries):
    extra=any(any(f['name']=='Variance' for f in q['meta']['measures']) for q in queries)
    s=planning_source('People','visual',catalog(extra),[{'id':'Pay-id','name':'Pay'}],[]);s['sourceGuid']='src';s['queries']=list(queries);return s

class InfoBridgeOperations(unittest.TestCase):
    def test_query_has_complete_null_writeback_and_string_identity(self):
        q=Query('one','s',catalog()).load_planning().record
        self.assertRegex(q['queryId'],r'^Q[0-9a-f]{32}$');self.assertEqual(q['writebackDestinations'],[]);self.assertIsNone(q['writebackSettings'])
    def test_filter_tolerates_descriptor_without_datatype(self):
        q=Query('one','s',catalog()).filter_equals([{'field':'Region','value':'West'}])
        self.assertNotIn('dataType',q.record['transformationSteps'][0]['meta']['value'][0]['sourceColumn'])
        with self.assertRaises(ValueError):q.filter_equals([{'field':'Pay','value':'10'}])
    def test_auxiliary_dates_are_not_fabricated_business_fields(self):
        c=catalog();c['dateColumns']=[{'name':'Month','alias':'Month','isTimeInterval':True}];c['hierarchyColumns']=[{'name':'cellType'}]
        q=Query('one','s',c);self.assertNotIn('cellType',q.fields())
        self.assertNotIn('id',q.record['meta']['dateColumns'][0]);self.assertEqual(len(q.fields()),4)
    def test_text_type_can_be_read_from_datatype_without_mutation(self):
        c=catalog();c['dimensions'][0].pop('type');c['dimensions'][0]['dataType']='TEXT_COLUMN'
        q=Query('one','s',c).filter_equals([{'field':'Region','value':'West'}])
        self.assertNotIn('type',q.record['meta']['selectedDimensions'][0])
    def test_replace_value_does_not_rename_column(self):
        q=Query('one','s',catalog()).find_replace(['Region'],'West','West Combined')
        self.assertIn('Region',q.fields());self.assertEqual(q.record['transformationSteps'][0]['meta']['type'],200)
        self.assertEqual(q.record['transformationSteps'][0]['meta']['value']['flags'],{'fullMatch':True,'matchCase':False,'useRegex':False})
    def test_rename_preserves_preceding_descriptor_and_changes_output(self):
        q=Query('one','s',catalog()).rename('Region','RegionName','fresh-id')
        v=q.record['transformationSteps'][0]['meta']['value'];self.assertEqual(v['sourceColumn']['id'],'Region-id')
        self.assertEqual(v['sourceColumn']['sourceType'],'dimensions');self.assertEqual(q.fields()['RegionName'][1]['id'],'fresh-id')
        with self.assertRaises(ValueError):q.filter_equals([{'field':'Region','value':'West'}])
    def test_union_is_opt_in_and_never_adds_zero(self):
        a,b=branch(),branch('two',True)
        with self.assertRaises(ValueError):append_compatibility([a,b])
        result=append_compatibility([a,b],allow_measure_union=True)
        self.assertEqual(result['missingMeasures']['Qone'],['Variance'])
        out=selected_catalog(b);s,e=append_queries('Stack',[a,b],out,allow_measure_union=True)
        self.assertEqual(s['queries'][0]['transformationSteps'][0]['meta']['type'],140)
        self.assertEqual(len(s['queries'][0]['transformationSteps']),1)
        validate_graph(portable([sources_for(a,b),s],e))
    def test_append_rejects_dimension_role_order_and_currency_mismatch(self):
        a,b=branch(),branch('two');b['meta']['selectedDimensions'][0]['alias']='Area'
        with self.assertRaises(ValueError):append_queries('Stack',[a,b],selected_catalog(a))
        b=branch('two');a['semantics']={'currency':'USD'};b['semantics']={'currency':'EUR'}
        with self.assertRaises(ValueError):append_queries('Stack',[a,b],selected_catalog(a),financial=True)
    def test_numeric_widening_not_confused_with_type_equality(self):
        a,b=branch(),branch('two');b['meta']['selectedMeasures'][0]['type']='DECIMAL(2,1)'
        append_compatibility([a,b])
        with self.assertRaises(ValueError):append_check([a,b])
    def test_merge_uses_structured_query_and_measure_selection(self):
        a,b=branch(),branch('two');sel={q['queryId']:[{'id':'17','name':'Pay','alias':'Pay','aggregationType':'sum'}] for q in (a,b)}
        s,e=merge_queries('Combined',[a,b],sel,selected_catalog(a))
        self.assertEqual(s['type'],'MERGE');self.assertEqual(s['meta']['queries'][0]['id'],'Qone')
        self.assertEqual(s['meta']['queries'][0]['sourceMeasures'][0]['id'],'17')
        self.assertEqual(s['queries'][0]['transformationSteps'][0]['meta']['type'],150)
        validate_graph(portable([sources_for(a,b),s],e))
    def test_merge_mismatched_measure_rejected(self):
        a,b=branch(),branch('two');sel={q['queryId']:[{'id':'1','name':'Missing','alias':'Missing','aggregationType':'sum'}] for q in (a,b)}
        with self.assertRaises(ValueError):merge_queries('Combined',[a,b],sel,selected_catalog(a))
    def test_join_is_not_merge_and_retains_ordered_base_query(self):
        a,b=branch(),branch('two');s,e=join_queries('Lookup',a,b,['Region'],['Region'],selected_catalog(a))
        self.assertEqual(s['meta']['joinType'],'LEFT_OUTER');self.assertTrue(s['meta']['queries'][0]['isBaseQuery'])
        self.assertNotIn('isBaseQuery',s['meta']['queries'][1]);self.assertEqual(s['queries'][0]['transformationSteps'][0]['meta']['type'],230)
        validate_graph(portable([sources_for(a,b),s],e))
        with self.assertRaises(ValueError):join_queries('Lookup',a,b,['Nope'],['Region'],selected_catalog(a))
    def test_lookup_duplicates_and_null_keys_block_fanout(self):
        with self.assertRaises(ValueError):lookup_key_check([{'R':'W'},{'R':'W'}],['R'])
        with self.assertRaises(ValueError):lookup_key_check([{}],['R'])
        self.assertEqual(lookup_key_check([{'R':'W'},{'R':'E'}],['R'])['uniqueKeys'],2)
    def test_power_table_source_uses_editable_220_not_planning(self):
        s=editable_source('FX','v',catalog(),destination_id='d',mde_source_id='m',table_name='Rates')
        self.assertEqual(s['type'],'EDITABLE');self.assertEqual(s['meta']['source']['infoBridgeSourceType'],220)
        self.assertEqual(s['meta']['source']['editable']['mdeSourceId'],'m')
        self.assertIsNone(s['meta']['source']['editable']['mdeSuperfilter'])
        self.assertEqual(s['queries'][0]['transformationSteps'][0]['meta']['type'],10)
    def test_sql_reference_sets_and_source_load_code(self):
        a=branch();s,e=sql_source('West',[a],"select * from {{query_id:Qone}} where Region = 'West'",selected_catalog(a))
        self.assertEqual(s['queries'][0]['transformationSteps'][0]['meta']['type'],10)
        validate_graph(portable([sources_for(a),s],e))
        with self.assertRaises(ValueError):sql_source('Bad',[a],'select * from {{query_id:unknown}}',selected_catalog(a))
    def test_sql_stale_numeric_reference_is_diagnostic(self):
        with self.assertRaises(ValueError):query_references('SQL_SOURCE',{'queries':['1'],'sql':'select * from {{query_id:Qone}}'})
    def test_nested_reconciliation_preserves_captions_measure_ids_and_literals(self):
        m={'queries':[{'id':'Qone','sourceMeasures':[{'id':'17','name':'Pay'}]}],'caption':'Qone'}
        o=reconcile_meta('MERGE',m,{'Qone':'4'});self.assertEqual(o['queries'][0]['id'],'4');self.assertEqual(o['queries'][0]['sourceMeasures'][0]['id'],'17');self.assertEqual(o['caption'],'Qone')
        o=reconcile_meta('MERGE',m,{'Qone':'4'},measure_maps={('Qone','17'):'29'});self.assertEqual(o['queries'][0]['sourceMeasures'][0]['id'],'29')
        o=reconcile_meta('JOIN',{'queries':[{'sourceId':'Qone','sourceName':'Qone','joinColumnName':['Qone']}]},{'Qone':4})
        self.assertEqual(o['queries'][0]['sourceId'],4);self.assertEqual(o['queries'][0]['sourceName'],'Qone')
        q={'type':'SQL_SOURCE','meta':{'queries':['Qone'],'sql':"select * from {{query_id:Qone}} where X='Qone'"},'transformationSteps':[]}
        o=reconcile_execution(q,{'Qone':'4'});self.assertIn('{{query_id:4}}',o['meta']['sql']);self.assertIn("X='Qone'",o['meta']['sql'])
    def test_execution_mapping_uses_sqlpk_not_array_position(self):
        self.assertEqual(execution_map([{'id':'Qx','sqlPk':'19'},{'id':'Qy','sqlPk':4}]),{'Qx':'19','Qy':'4'})
        with self.assertRaises(ValueError):execution_map([{'id':'Qx','sqlPk':1},{'id':'Qy','sqlPk':1}])
    def test_missing_edges_and_cycles_rejected(self):
        a,b=branch(),branch('two');s,e=append_queries('Stack',[a,b],selected_catalog(a))
        with self.assertRaises(ValueError):portable([sources_for(a,b),s],e[:1])
        e[0]['queryId']=s['queries'][0]['queryId'];s['meta']['queries'][0]=e[0]['queryId'];s['queries'][0]['meta']['queries'][0]=e[0]['queryId']
        with self.assertRaises(ValueError):portable([sources_for(a,b),s],e)
    def test_step_catalog_flags_year_only_when_absent_at_that_stage(self):
        a=branch();a['transformationSteps'][1]['meta']['value']['sourceColumns']=[field('Year','INTEGER')]
        source=sources_for(a);report=audit_step_columns(source,a)
        self.assertIn('Year',report['issues'][0]['unavailableFromSourceSnapshot'])
        source['meta']['columns'].append(field('Year','INTEGER'));self.assertEqual(audit_step_columns(source,a)['issues'],[])
    def test_query_spec_is_sequential_and_does_not_eval(self):
        q=construct_query('q','s',catalog(),[{'operation':'pivot','arguments':{'rows':['Region'],'columns':['Month'],'measures':{'Pay':'sum'}}},{'operation':'add','arguments':{'name':'Total','expression':'"Pay"*2','output_id':'derived','requires':['Pay']}}])
        self.assertEqual([s['meta']['type'] for s in q['transformationSteps']],[10,50,130])
        with self.assertRaises(ValueError):construct_query('q','s',catalog(),[{'operation':'__class__','arguments':{}}])
    def test_add_measure_case_can_return_text(self):
        expression='CASE WHEN "Pay" > 1000000 THEN \'high\' ELSE \'low\' END'
        q=Query('q','s',catalog()).add('Band',expression,'band-id',requires=['Pay'],output_type='VARCHAR')
        st=q.record['transformationSteps'][-1]
        self.assertEqual(st['meta']['type'],130);self.assertEqual(st['meta']['value']['formulaQuery'],expression)
        field=q.fields()['Band'][1]
        self.assertEqual(field['type'],'VARCHAR');self.assertNotIn('aggregationType',field)
    def test_add_dimension_accepts_conditional_sql(self):
        expression='CASE WHEN "Region" IN (\'West\', \'East\') THEN \'Domestic\' ELSE \'International\' END'
        q=Query('q','s',catalog()).add('Market',expression,'market-id',kind='dimension',requires=['Region'],output_type='VARCHAR')
        self.assertEqual(q.record['transformationSteps'][-1]['meta']['type'],170)
        self.assertEqual(q.record['transformationSteps'][-1]['meta']['value']['formulaQuery'],expression)
        self.assertEqual(q.fields()['Market'][0],'dimensions')
    def test_conditional_numeric_expression_keeps_null_and_declared_dependencies(self):
        expression='CASE WHEN "Pay" IS NULL THEN NULL WHEN "Pay" > 0 THEN "Pay" * 1.05 ELSE 0 END'
        q=Query('q','s',catalog()).add('Adjusted',expression,'adjusted-id',requires=['Pay'],output_type='DOUBLE')
        self.assertEqual(q.fields()['Adjusted'][1]['aggregationType'],'sum')
        self.assertEqual(q.record['transformationSteps'][-1]['meta']['value']['formulaQuery'],expression)
        with self.assertRaises(ValueError):q.add('Invalid','"Absent"','x',requires=['Absent'])
    def test_text_conditional_result_cannot_be_summed(self):
        q=Query('q','s',catalog()).add('Band',"CASE WHEN \"Pay\" > 0 THEN 'high' ELSE 'low' END",'band-id',output_type='VARCHAR',requires=['Pay'])
        with self.assertRaises(ValueError):q.pivot(['Region'],['Month'],{'Band':'sum'})

if __name__=='__main__':unittest.main()
