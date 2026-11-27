import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,importlib.util,unittest
from pathlib import Path
from runtime.codec import parts,unpack
from runtime.powertable_config import repair_definition,enrich_source
from runtime.powertable_factory import configured_table,existing_source
from runtime.table_columns import column_config,apply_lookup

spec=importlib.util.spec_from_file_location('lookup_example',Path(__file__).resolve().parents[1]/'assets/examples/powertable-lookups/build.py')
example=importlib.util.module_from_spec(spec);spec.loader.exec_module(example)

class PowerTableConfigTests(unittest.TestCase):
    def setUp(self):self.baseline,self.request,self.inputs=example.sample()
    def repaired(self):return repair_definition(self.baseline,**self.request)
    def test_scoped_change_preserves_all_other_part_bytes(self):
        before=parts(self.baseline);candidate,manifest=self.repaired();after=parts(candidate)
        changed={p for p in before if before[p]!=after[p]}
        self.assertEqual(changed,set(manifest['changedParts']))
        self.assertEqual({p.rsplit('/',1)[-1] for p in changed},{'source.json','columnConfigs.json'})
        self.assertEqual(before['infobridge.json'],after['infobridge.json'])
        old=unpack(self.baseline);new=unpack(candidate)
        key=next(p for p in new if p.endswith('/columnConfigs.json'))
        for a,b in zip(old[key]['columnConfigs'],new[key]['columnConfigs']):
            for field in ('columnGuid','recordGuid','columnName','allowEdit','hideColumn','mandatory'):
                self.assertEqual(a[field],b[field])
            self.assertEqual(a['columnMeta']['dbMeta'],b['columnMeta']['dbMeta'])
        source=next(p for p in new if p.endswith('/source.json'))
        for k,v in old[source]['source'].items():
            if k!='meta':self.assertEqual(v,new[source]['source'][k])
        self.assertEqual(new[source]['source']['meta']['totalRows'],12)
        settings=next(p for p in new if p.endswith('/sourceSettings.json'))
        self.assertFalse(next(s for s in new[settings]['sourceSettings'] if s['name']=='ROW_ADD')['settings']['enabled'])
    def test_repair_idempotent(self):
        candidate,_=self.repaired();again,manifest=repair_definition(candidate,**self.request)
        self.assertEqual(candidate,again);self.assertEqual(manifest['changedParts'],[])
    def test_readonly_lookup_keeps_physical_key_and_label_separate(self):
        c=self.inputs['columns'][1]
        result=apply_lookup(c,self.request['lookups']['ProductID'],self.request['lookup_catalog'])
        self.assertEqual(result['columnName'],'ProductID');self.assertEqual(result['displayName'],'ProductCode')
        self.assertEqual(result['allowEdit'],0)
        self.assertFalse(result['columnMeta']['allowAddingNewOptions'])
        self.assertEqual(result['columnMeta']['options'],[])
    def test_chain_uses_preceding_table_fk_and_remote_linking_key(self):
        c=self.inputs['columns'][2]
        lookup=copy.deepcopy(self.request['lookups']['RegionID'])
        lookup['chain'][0]['key']='CurrencyKey'
        catalog=copy.deepcopy(self.request['lookup_catalog'])
        catalog[-1]['columns'][0]['name']='CurrencyKey'
        result=apply_lookup(c,lookup,catalog)
        chain=result['columnMeta']['optionLinking']['lookupConfig']
        self.assertEqual([(h['id'],h['linkingColumn'],h['order']) for h in chain],
                         [('RegionID','RegionID',0),('CurrencyKey','CurrencyID',1)])
    def test_rejects_nonunique_remote_key(self):
        self.request['lookup_catalog'][0]['columns'][0]['isPrimaryKey']=False
        with self.assertRaisesRegex(ValueError,'unique remote key'):self.repaired()
    def test_rejects_wrong_key_type(self):
        self.request['lookup_catalog'][0]['columns'][0]['type']='nvarchar'
        with self.assertRaisesRegex(ValueError,'compatible'):self.repaired()
    def test_rejects_missing_display_column(self):
        self.request['lookups']['ProductID']['label']='UnknownLabel'
        with self.assertRaisesRegex(ValueError,'key/label absent'):self.repaired()
    def test_rejects_missing_chain_fk(self):
        self.request['lookups']['RegionID']['chain'][0]['column']='UnknownFK'
        with self.assertRaisesRegex(ValueError,'preceding lookup table'):self.repaired()
    def test_rejects_metadata_from_reference_connection(self):
        self.request['source_metadata']['connection']['id']='another-connection'
        with self.assertRaisesRegex(ValueError,'destination source'):self.repaired()
    def test_rejects_metadata_from_other_database_workspace(self):
        self.request['source_metadata']['database']['workspaceId']='other-workspace'
        with self.assertRaisesRegex(ValueError,'different workspace'):self.repaired()
    def test_rejects_wrong_sheet_without_mutating_baseline(self):
        before=copy.deepcopy(self.baseline);self.request['sheet_guid']='other-sheet'
        with self.assertRaises(ValueError):self.repaired()
        self.assertEqual(self.baseline,before)
    def test_rejects_unresolved_column(self):
        self.request['lookups']['MissingID']=self.request['lookups']['ProductID']
        with self.assertRaisesRegex(ValueError,'resolve uniquely'):self.repaired()
    def test_source_metadata_null_can_be_completed(self):
        source=next(v['source'] for p,v in unpack(self.baseline).items() if p.endswith('/source.json'))
        source['meta']=None
        repaired=enrich_source(source,**self.request['source_metadata'])
        self.assertEqual(repaired['meta']['workspaceName'],'Illustrative workspace')
        self.assertIsNone(source['meta'])
    def test_configured_constructor_requires_destination_labels(self):
        c=copy.deepcopy(self.inputs['connection']);c.pop('workspaceName')
        with self.assertRaisesRegex(ValueError,'workspaceName'):
            configured_table('Policy',self.inputs['table'],c,self.inputs['columns'],explicit=True,allow_add=False)
        # Native initialization is a separate smaller request, not an ALM source.
        self.assertEqual(existing_source(self.inputs['table'],c,True)['connectionId'],c['connectionId'])
    def test_new_configured_constructor_supplies_meta_and_honors_actions(self):
        _,raw,_=configured_table('Policy',**self.inputs,explicit=True,allow_add=False)
        source=next(v['source'] for p,v in raw.items() if p.endswith('/source.json'))
        self.assertEqual(source['meta']['databaseId'],self.inputs['connection']['artifactId'])
        self.assertEqual(source['meta']['connectionName'],'Illustrative connection')
    def test_identity_cannot_become_editable_or_a_lookup(self):
        c={'name':'PolicyID','dbMeta':example.dbmeta(True)}
        with self.assertRaises(ValueError):column_config(c,'integer',allow_edit=True)
        with self.assertRaises(ValueError):column_config(c,'database-lookup',lookup=self.request['lookups']['ProductID'],lookup_catalog=self.request['lookup_catalog'])

if __name__=='__main__':unittest.main()
