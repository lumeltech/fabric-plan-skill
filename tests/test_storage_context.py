import copy,unittest
from unittest.mock import Mock,patch
from tempfile import TemporaryDirectory
from runtime.storage_context import signature,require_same,query_contract,require_query,audit_links
from runtime.consumer_bindings import numeric_output_fields
from runtime.construct import build,planning
from runtime.identity import Registry
from test_context_intelligence import example,owner_parts


class StorageContextTests(unittest.TestCase):
    def setUp(self):
        self.model,self.spec=example()
        self.props,self.records=owner_parts(build(self.model,self.spec))

    def test_axis_grain_is_not_repeated_as_context(self):
        s=self.spec['sheets'][0]
        for key in (s['rows'][0],s['columns'][0]):
            bad=copy.deepcopy(s);bad['context'].append({'field':key,'values':['A']})
            with self.assertRaisesRegex(ValueError,'already define storage grain'):signature(bad)

    def test_page_and_global_filters_do_not_change_storage_signature(self):
        p=copy.deepcopy(self.props);before=signature(p)
        p['superFilterAssignments'].append({'filterLevel':'page','filter':[{'columnIds':['Time[Year]'],'valuesFilter':[{'id':[2027]}]}]})
        p['workloadLevelFilterAssignments']=[{'field':'Geography[Area]','values':['West']}]
        self.assertEqual(before,signature(p))
        require_same(self.props,p)

    def test_order_registration_ids_and_labels_are_not_identity(self):
        p=copy.deepcopy(self.props)
        r=next(r for r in p['superFilterAssignments'] if r.get('isContextDimension'))
        mirror=next(r for r in p['visualState']['embeddedSuperFilter']['superFilterAssignments'] if r.get('isContextDimension'))
        for item in [r,mirror]:item.update(id='fresh');item['configuration']['name']='Version label'
        require_same(self.props,p)

    def test_mismatched_fields_selection_or_key_rejected(self):
        a=self.spec['sheets'][0]
        for mutation in ['field','selection','key','missing']:
            b=copy.deepcopy(a)
            if mutation=='field':b['context'][0]['field']='Version[Key]'
            if mutation=='selection':b['context'][0]['values']=['Other']
            if mutation=='key':b['dimensionIdMappings'].pop('Version[Name]')
            if mutation=='missing':b['context']=[]
            with self.subTest(mutation=mutation),self.assertRaisesRegex(ValueError,'Context mismatch'):require_same(a,b)

    def test_unbound_forecast_and_visual_input_rejected(self):
        from runtime.filters import audit_context
        for kind in ['Forecast','DataInput']:
            r=copy.deepcopy(self.records[0]);r['columnMeta']['measure_type']={'VisualColumn':{kind:{'bound_to_filter_context':False}}}
            r['boundToFilterContext']=20
            with self.assertRaisesRegex(ValueError,'not bound'):audit_context(self.props,[r])

    def query(self):
        return {'id':'Qfresh','sourceId':'source-current','name':'Output','meta':{
            'selectedDimensions':[{'id':'v','name':'Version','type':'VARCHAR'}],
            'selectedColumns':[],
            'selectedMeasures':[{'id':'amount','name':'Planned','type':'DOUBLE'}]}}

    def test_query_keeps_verified_context_for_both_storage_modes(self):
        for sqlpk in [None,42]:
            q=self.query();q['sqlPk']=sqlpk
            proof=query_contract(q,[self.props],{'Version[Name]':'v'})
            f=numeric_output_fields(q,storage_context=proof)[0]
            self.assertEqual(f['storageContext']['queryId'],str(sqlpk) if sqlpk else 'Qfresh')
            require_query(proof,self.props,f['queryId'])

    def test_query_lost_context_wrong_owner_and_wrong_output_rejected(self):
        q=self.query()
        for mapping in [{},{'Version[Name]':'amount'},{'Version[Name]':'absent'}]:
            with self.assertRaises(ValueError):query_contract(q,[self.props],mapping)
        other=copy.deepcopy(self.props);other['visualState']['dimension_id_mapping']['mappings'].pop('Version[Name]')
        with self.assertRaises(ValueError):query_contract(q,[self.props,other],{'Version[Name]':'v'})
        with self.assertRaises(ValueError):require_query(None,self.props,'Qfresh')

    def test_query_context_mandatory_in_planning_constructor(self):
        q=self.query();s=copy.deepcopy(self.spec['sheets'][0])
        field=numeric_output_fields(q)[0]
        s['measures']=[{'key':'linked','label':'Linked Plan','kind':'Native','source':field['id']}]
        with self.assertRaisesRegex(ValueError,'sidecar'):planning(self.model,s,Registry(),query_fields=[field])
        proof=query_contract(q,[self.props],{'Version[Name]':'v'})
        field=numeric_output_fields(q,storage_context=proof)[0]
        planning(self.model,s,Registry(),query_fields=[field])

    def test_saved_consumer_audit(self):
        p=copy.deepcopy(self.props);p['pivotAssignments'].append({'sourceType':'Visual','visualId':'21','bucketId':'ameasure'})
        result=audit_links(p,[{'visualId':'21','properties':self.props}])
        self.assertEqual(result['links'],1)

    def test_no_storage_context_is_valid_without_forcing_version(self):
        a={'rows':['Product[Name]'],'columns':['Time[Month]']}
        b={'rows':[],'columns':['Time[Month]'],'superFilterAssignments':[{'filterLevel':'global'}]}
        self.assertEqual(require_same(a,b)['fields'],[])


if __name__=='__main__':unittest.main()
