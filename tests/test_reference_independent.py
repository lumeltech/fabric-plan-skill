"""Independent synthetic forward tests; no reference report, network, or native UI."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy
import unittest
from runtime.construct import field, planning
from runtime.identity import Registry
from runtime.dimension_mapping import dimension_mapping, validate_mapping
from runtime.table_columns import column_config
from runtime.connected_components import contribution, bridge_consumer, embedded_planning
from runtime.bridge import append_check, Query
from runtime.definition_audit import audit_definition
from runtime.codec import loads

def model():
    def f(table,name,typ='String',kind='Column'):
        return {'id':table+'['+name+']','tableName':table,'columnName':name,'columnType':kind,'dataType':typ}
    return {'fields':[f('Staff','Name'),f('Staff','ID','Int64'),f('Staff','Department'),
        f('Version','Name'),f('Version','ID','Int64'),f('Period','Month'),f('Period','ID','Int64'),
        f('Measures','Pay','Double','Measure')]}

def catalog():
    def f(name,numeric=False):return {'id':'source-'+name,'name':name,'alias':name,
        'type':'DOUBLE' if numeric else 'VARCHAR','dataType':'NUMERIC' if numeric else 'TEXT_COLUMN', **({'measureGuid':'source-'+name,'columnType':'DI','isHierarchyColumn':False} if numeric else {})}
    return {'dimensions':[f('Region'),f('Version'),f('Employee')],
            'columns':[f('Month')],'measures':[f('Salary',True)]}

def normalize(name='Salary',dims=None):
    return contribution(name,'new-source',catalog(),dims or ['Region','Version'],['Month'],
        [{'name':'Compensation','expression':'"Salary"','id':'out-compensation','requires':['Salary']},
         {'name':'Revenue','expression':'0.0','id':'out-revenue','requires':[],'zeroIsValid':True}],
        {'period':'Month','scenario':'Version','currency':'USD','signConvention':'positive-expense'})

def dbmeta(**changes):
    return {'type':'int','isIdentity':False,'isNullable':False,'isPrimaryKey':False,
            'isUnique':False,'isCompositeUnique':False,**changes}

class IndependentReferenceTests(unittest.TestCase):
    def test_context_only_lookup_is_not_extra_visible_axis(self):
        m=model()
        spec={'name':'Synthetic Workforce','rows':['Staff[Name]'],'columns':['Period[Month]'],
              'measures':[{'key':'pay','kind':'Native','source':'Measures[Pay]','label':'Pay'}],
              'dimensionIdMappings':{'Staff[Name]':{'ID':'Staff[ID]'},'Period[Month]':{'ID':'Period[ID]'},
                                     'Version[Name]':{'ID':'Version[ID]'}},
              'lookupContextAssignments':[field(m,'Version[Name]','rows',1)]}
        before=copy.deepcopy(spec)
        _,raw,_=planning(m,spec,Registry())
        props=next(v['properties'] for k,v in raw.items() if k.endswith('properties.json'))
        self.assertEqual(spec,before)
        self.assertEqual([a['id'] for a in props['pivotAssignments'] if a['bucketId']=='rows'],['Staff[Name]'])
        ids=[d['id'] for d in props['visualState']['dimension_id_mapping']['pivot']]
        self.assertIn('Version[Name]',ids);self.assertIn('Version[ID]',ids)
        self.assertEqual(validate_mapping(props['visualState']['dimension_id_mapping'])['mappingCount'],3)

    def test_mapping_rejects_cross_table_key(self):
        m=model();a=[field(m,'Staff[Name]','rows',0)]
        with self.assertRaises(ValueError):dimension_mapping(m,a,{'Staff[Name]':{'ID':'Version[ID]'}})

    def test_skip_requires_retained_entity_identity(self):
        m=model();a=[field(m,'Staff[Name]','rows',0),field(m,'Staff[Department]','rows',1)]
        mappings={'Staff[Name]':{'ID':'Staff[ID]'},'Staff[Department]':{'Skip':{}}}
        with self.assertRaises(ValueError):dimension_mapping(m,a,mappings)
        result=dimension_mapping(m,a,mappings,skip_support={'Staff[Department]':'Staff[Name]'})
        self.assertEqual(result['mappings']['Staff[Department]'],{'Skip':{}})

    def test_missing_descriptor_pair_fails_audit(self):
        m=model();result=dimension_mapping(m,[field(m,'Staff[Name]','rows',0)],{'Staff[Name]':{'ID':'Staff[ID]'}})
        result['pivot'].pop()
        with self.assertRaises(ValueError):validate_mapping(result)

    def test_lookup_keeps_foreign_key_and_displays_label(self):
        col={'name':'CategoryKey','dbMeta':dbmeta()}
        lookup={'schema':'master','table':'Category','key':'ID','label':'Caption'}
        remote=[{'schema':'master','table':'Category','columns':[{'name':'ID','type':'int','isPrimaryKey':True},{'name':'Caption','type':'nvarchar'}]}]
        before=copy.deepcopy((col,lookup,remote))
        result=column_config(col,'database-lookup',lookup=lookup,lookup_catalog=remote)
        self.assertEqual((col,lookup,remote),before)
        self.assertEqual(result['columnGuid'],'CategoryKey');self.assertEqual(result['displayName'],'Caption')
        link=result['columnMeta']['optionLinking']['lookupConfig'][0]
        self.assertEqual((link['id'],link['linkingColumn']),('ID','CategoryKey'))
        self.assertNotEqual(result['recordGuid'],column_config(col,'database-lookup',lookup=lookup,lookup_catalog=remote)['recordGuid'])

    def test_lookup_rejects_nonunique_remote_key(self):
        with self.assertRaises(ValueError):column_config({'name':'CategoryKey','dbMeta':dbmeta()},'database-lookup',
          lookup={'schema':'master','table':'Category','key':'ID','label':'Caption'},
          lookup_catalog=[{'schema':'master','table':'Category','columns':[{'name':'ID','type':'int','isUnique':False},{'name':'Caption','type':'nvarchar'}]}])

    def test_generated_sql_identity_is_not_editable(self):
        c=column_config({'name':'ID','dbMeta':dbmeta(isIdentity=True,isPrimaryKey=True)},'integer')
        self.assertEqual((c['allowEdit'],c['hideColumn'],c['mandatory']),(0,0,1))

    def test_contribution_casts_and_aggregates_to_common_grain(self):
        q=normalize();steps=q['transformationSteps']
        self.assertTrue(all(s['meta']['value']['formulaQuery'].startswith('CAST((') for s in steps if s['meta']['type']==130))
        self.assertEqual([f['alias'] for f in q['meta']['selectedDimensions']],['Region','Version'])
        self.assertEqual([f['type'] for f in q['meta']['selectedMeasures']],['DOUBLE','DOUBLE'])
        self.assertTrue(q['aggregatedToGrain']);append_check([q,normalize('Other')])

    def test_contribution_must_not_merge_distinct_scenarios(self):
        with self.assertRaises(ValueError):normalize(dims=['Region'])

    def test_append_rejects_reordered_dimensions(self):
        with self.assertRaises(ValueError):append_check([normalize(),normalize('Other',['Version','Region'])])

    def test_contribution_rejects_colliding_output_identities(self):
        with self.assertRaises(ValueError):
            contribution('Broken','source',catalog(),['Region','Version'],['Month'],
                [{'name':'A','expression':'"Salary"','id':'duplicate','requires':['Salary']},
                 {'name':'B','expression':'"Salary"','id':'duplicate','requires':['Salary']}],
                {'period':'Month','scenario':'Version','currency':'USD','signConvention':'positive-expense'})

    def test_year_filter_after_month_projection_rejected(self):
        q=Query('Fresh','new-source',catalog()).load_planning().pivot(['Region','Version'],['Month'],{'Salary':'sum'})
        with self.assertRaises(ValueError):q.filter_equals([{'field':'Year','value':'2027'}])
        q.filter_equals([{'field':'Version','value':'Forecast'},{'field':'Region','value':'West'}])
        clauses=q.record['transformationSteps'][-1]['meta']['value']
        self.assertEqual([c['condition'] for c in clauses],['Where','And'])

    def test_numeric_filter_accepts_lossless_decoded_decimal(self):
        conditions=loads('[{"field":"Salary","value":1.5}]')
        q=Query('Fresh','source',catalog()).load_planning().filter_equals(conditions)
        self.assertEqual(q.record['transformationSteps'][-1]['meta']['value'][0]['value'],conditions[0]['value'])

    def test_bridge_consumer_rejects_empty_output_identity(self):
        f={'id':'','queryId':'query-current','columnName':'Revenue','tableName':'Revenue Plan','columnType':'Column','dataType':'Double','sourceType':'InfoBridge'}
        with self.assertRaises(ValueError):bridge_consumer(f,'destination','123','Revenue')

    def test_embedded_owner_guid_is_reused_without_duplicate_properties(self):
        owner={'sheetType':'PLANNING','workloadItemEntityVisuals':[{'visualId':'ABC','visualType':'PLANNING','isEmbedded':False}]}
        before=copy.deepcopy(owner)
        ref=embedded_planning(owner,'abc')
        self.assertEqual(ref,{'visualId':'ABC','visualType':'PLANNING','isEmbedded':True});self.assertEqual(owner,before)
        with self.assertRaises(ValueError):embedded_planning(owner,'missing')

    def test_audit_accepts_case_variant_owner_path_and_rejects_collisions(self):
        raw={'definition.json':{'sheets':[{'recordGuid':'s','displayName':'Owner','sheetType':'PLANNING','isHidden':True,
             'workloadItemEntityVisuals':[{'visualId':'ABC','visualType':'PLANNING','isEmbedded':False}]},
             {'recordGuid':'d','displayName':'Dashboard','sheetType':'REPORTING','workloadItemEntityVisuals':[
             {'visualId':'abc','visualType':'PLANNING','isEmbedded':True}]}]},
             'sheets/s/visuals/abc/properties.json':{'properties':{'visualState':{}}}}
        result=audit_definition(raw)
        self.assertEqual(result['embeddedPlanning'][0]['ownerSheet'],'Owner');self.assertEqual(result['issues'],[])
        raw['sheets/s/visuals/ABC/properties.json']=raw['sheets/s/visuals/abc/properties.json']
        with self.assertRaises(ValueError):audit_definition(raw)

if __name__=='__main__':unittest.main()
