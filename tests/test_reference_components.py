import unittest,copy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from runtime.dimension_mapping import dimension_mapping,validate_mapping
from runtime.table_columns import column_config
from runtime.construct import field,planning
from runtime.identity import Registry
from runtime.connected_components import contribution,bridge_consumer,embedded_planning
from runtime.bridge import Query,append_check,append_source,portable
from runtime.definition_audit import audit_definition

def model():
    def f(t,c,typ='String'):return {'id':f'{t}[{c}]','tableName':t,'columnName':c,'dataType':typ,'columnType':'Column'}
    return {'fields':[f('People','Name'),f('People','Key','Int64'),f('People','Team'),f('Version','Name'),f('Version','Key','Int64'),f('Period','Month'),f('Period','Key','Int64')]}
def db(name='ProductKey',typ='int',identity=False):
    return {'name':name,'dbMeta':{'type':typ,'isIdentity':identity,'isNullable':False,'isPrimaryKey':identity,
       'isUnique':False,'isCompositeUnique':False,'maxLength':4,'uniqueConstraintName':None}}
def catalog():
    def f(n,typ='VARCHAR'):return {'id':'current-'+n,'name':n,'alias':n,'type':typ,'dataType':'NUMERIC' if typ=='DOUBLE' else 'TEXT_COLUMN', **({'measureGuid':'current-'+n,'columnType':'DI','isHierarchyColumn':False} if typ=='DOUBLE' else {})}
    return {'dimensions':[f('Region'),f('Version'),f('Employee')],'columns':[f('Month')],'measures':[f('Pay','DOUBLE')]}
def normalized(name='Workforce',pay=True):
    return contribution(name,'source',catalog(),['Region','Version'],['Month'],[
       {'name':'Compensation','expression':'"Pay"' if pay else '0.0','id':'out1','requires':['Pay'] if pay else [],'zeroIsValid':not pay},
       {'name':'Revenue','expression':'0.0','id':'out2','requires':[],'zeroIsValid':True}],
       {'period':'Month','scenario':'Version','currency':'USD','signConvention':'costs-positive'})

class MappingTests(unittest.TestCase):
    def test_context_pair_and_skip_keep_axes(self):
        m=model();axis=[field(m,'People[Name]','rows',0),field(m,'People[Team]','rows',1),field(m,'Period[Month]','columns',0)]
        before=copy.deepcopy(axis)
        out=dimension_mapping(m,axis,{'People[Name]':{'ID':'People[Key]'},'People[Team]':{'Skip':{}},'Version[Name]':{'ID':'Version[Key]'}},
            descriptor_only_assignments=[field(m,'Version[Name]','rows',2)],skip_support={'People[Team]':'People[Name]'})
        self.assertEqual(axis,before);self.assertEqual(validate_mapping(out)['mappingCount'],3)
        self.assertEqual({p['id'] for p in out['pivot']},{'People[Name]','People[Key]','People[Team]','Period[Month]','Version[Name]','Version[Key]'})
    def test_cross_table_and_missing_descriptor_rejected(self):
        m=model();a=[field(m,'People[Name]','rows',0)]
        for mappings in ({'People[Name]':{'ID':'Version[Key]'}},{'Version[Name]':{'ID':'Version[Key]'}},{'People[Name]':{'Skip':{}}}):
            with self.assertRaises(ValueError):dimension_mapping(m,a,mappings)
    def test_incomplete_pair_detected(self):
        m=model();s=dimension_mapping(m,[field(m,'People[Name]','rows',0)],{'People[Name]':{'ID':'People[Key]'}})
        s['pivot'].pop()
        with self.assertRaises(ValueError):validate_mapping(s)
    def test_planning_builder_consumes_mapping(self):
        m=model();s={'name':'Fresh workforce','rows':['People[Name]'],'columns':['Period[Month]'],
          'dimensionIdMappings':{'People[Name]':{'ID':'People[Key]'}},'measures':[{'key':'pay','kind':'DataInput','label':'Pay'}]}
        _,raw,_=planning(m,s,Registry());p=next(v['properties'] for k,v in raw.items() if k.endswith('properties.json'))
        self.assertEqual([a['id'] for a in p['pivotAssignments']],['People[Name]','Period[Month]'])
        self.assertEqual(validate_mapping(p['visualState']['dimension_id_mapping'])['mappingCount'],1)

class TableTests(unittest.TestCase):
    def lookup(self):return {'schema':'ops','table':'Products','key':'Key','label':'Title'}
    def metadata(self):return [{'schema':'ops','table':'Products','columns':[{'name':'Key','type':'int','isPrimaryKey':True},{'name':'Title','type':'nvarchar'}]}]
    def test_sql_key_display_label_and_new_record_identity(self):
        args={'column':db(),'kind':'database-lookup','lookup':self.lookup(),'lookup_catalog':self.metadata()}
        a=column_config(**args);b=column_config(**args)
        self.assertNotEqual(a['recordGuid'],b['recordGuid']);self.assertEqual(a['columnGuid'],'ProductKey');self.assertEqual(a['displayName'],'Title')
        link=a['columnMeta']['optionLinking']['lookupConfig'][0]
        self.assertEqual((link['id'],link['linkingColumn']),('Key','ProductKey'))
    def test_missing_or_nonunique_lookup_rejected(self):
        meta=self.metadata();meta[0]['columns'][0]['isPrimaryKey']=False
        with self.assertRaises(ValueError):column_config(db(),'database-lookup',lookup=self.lookup(),lookup_catalog=meta)
        with self.assertRaises(ValueError):column_config(db(),'database-lookup',lookup=self.lookup(),lookup_catalog=[])
    def test_identity_is_readonly_displayed_and_mandatory_when_not_null(self):
        # The product shows every column, including an identity key, on the Columns tab,
        # and makes a NOT NULL or primary-key column mandatory.
        c=column_config(db('RowKey',identity=True),'integer')
        self.assertEqual((c['allowEdit'],c['hideColumn'],c['mandatory']),(0,0,1))
    def test_date_decimal_keep_physical_metadata(self):
        for kind,typ in [('date','date'),('decimal','decimal')]:
            source=db('Value',typ);c=column_config(source,kind)
            self.assertEqual(c['columnMeta']['dbMeta'],source['dbMeta'])
        with self.assertRaises(ValueError):column_config(db('Value','varchar'),'decimal')

class BridgeTests(unittest.TestCase):
    def test_normalizes_before_append(self):
        a=normalized();b=normalized('Other',False);sig=append_check([a,b])
        self.assertEqual([x[1] for x in sig['fields']],['Region','Version','Month','Compensation','Revenue'])
        self.assertTrue(all(x[2]=='DOUBLE' for x in sig['fields'] if x[0]=='measures'))
        formulas=[s['meta']['value']['formulaQuery'] for s in a['transformationSteps'] if s['meta']['type']==130]
        self.assertTrue(all(x.startswith('CAST((') and x.endswith(' AS DOUBLE)') for x in formulas))
        self.assertEqual(a['transformationSteps'][-1]['meta']['type'],50)
        src,edges=append_source('Consolidated',[a,b])
        sources=[{'sourceGuid':'source','queries':[a,b]},src]
        # Each source must own its actual query IDs; generated IDs are distinct.
        self.assertEqual(len(portable(sources,edges)['sources']),2)
    def test_year_scenario_type_drift_rejected(self):
        with self.assertRaises(ValueError):Query('Q','s',catalog()).load_planning().pivot(['Region'],['Year'],{'Pay':'sum'})
        for mutation in ('version','type','order'):
            a=normalized();b=normalized('Other')
            if mutation=='version': b['semantics']['scenario']='Unscoped'
            elif mutation=='type':b['meta']['selectedMeasures'][0]['type']='DECIMAL(2,1)'
            else:b['meta']['selectedDimensions'].reverse()
            with self.assertRaises(ValueError):append_check([a,b])
    def test_filter_array_current_alias_and_schema(self):
        c=catalog();c['dimensions'][0]['alias']='Territory'
        q=Query('Q','s',c).load_planning().filter_equals([{'field':'Territory','value':'West'},{'field':'Version','value':'Budget'}])
        value=q.record['transformationSteps'][-1]['meta']['value']
        self.assertEqual([x['condition'] for x in value],['Where','And'])
        with self.assertRaises(ValueError):q.filter_equals([{'field':'Year','value':'2028'}])
        with self.assertRaises(ValueError):q.filter_equals([{'field':'Pay','value':'one'}])
    def test_consumer_companions_exact_identity(self):
        f={'id':'Qcurrent[output-key]','queryId':'Qcurrent','columnName':'Pay','tableName':'Current Pay',
          'columnType':'Column','dataType':'Double','sourceType':'InfoBridge'}
        out=bridge_consumer(f,'fresh-visual','18446744073709551615','Linked Pay')
        self.assertEqual(out['assignment']['sourceId'],f['id']);self.assertEqual(out['dataInputColumn']['measureGuid'],'18446744073709551615')
        self.assertEqual(out['dataInputColumn']['visualId'],'fresh-visual')
        with self.assertRaises(ValueError):bridge_consumer({**f,'sourceType':'PowerBI'},'v','4','Pay')

class EmbedAuditTests(unittest.TestCase):
    def test_embed_keeps_owner_and_case_insensitive_guid(self):
        owner={'recordGuid':'owner','displayName':'Inputs','sheetType':'PLANNING','isHidden':True,
               'workloadItemEntityVisuals':[{'visualId':'AB-CD','visualType':'PLANNING','isEmbedded':False}]}
        before=copy.deepcopy(owner);v=embedded_planning(owner,'ab-cd');self.assertEqual(owner,before)
        raw={'definition.json':{'sheets':[owner,{'recordGuid':'page','displayName':'Dashboard','workloadItemEntityVisuals':[v]}]},
             'sheets/owner/visuals/ab-cd/properties.json':{'properties':{'visualState':{}}}}
        a=audit_definition(raw);self.assertEqual(a['issues'],[]);self.assertTrue(a['embeddedPlanning'][0]['ownerHidden'])
        raw['sheets/owner/visuals/AB-CD/properties.json']=raw['sheets/owner/visuals/ab-cd/properties.json']
        with self.assertRaises(ValueError):audit_definition(raw)

if __name__=='__main__':unittest.main()
