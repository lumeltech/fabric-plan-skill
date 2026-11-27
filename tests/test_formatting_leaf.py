import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,unittest,subprocess,sys,tempfile
from pathlib import Path
from runtime.matrix_formatting import compile_formatting,format_values,pixel_size,SNAPSHOT
from runtime.dimension_mapping import leaf_key_mapping
from runtime.construct import build,field
from runtime.scope import prepare_scope
from runtime.workflow import SUPPORTED,preflight

ROOT=Path(__file__).resolve().parents[1]
BIG='18446744073709550001'

def state():
    return {'manage_measures':[{'id':BIG,'label':'Amount'},{'id':'2','label':'Comment'},{'id':'3','label':'Flag'}],
        'rowDimensions':[{'id':'product'}],'columnDimensions':[{'id':'year'}],
        'globalStyles':{'fontSize':'12','privateFutureOption':True},
        'formatConfig':{'measure':{BIG:[{'format':{'4':'Arial'},'order':7}]},'formatSize':8},
        'businessPolicy':{'closed':'unchanged'},'filters':[{'opaque':'preserve'}],
        'row_height_config':{'default_row_height':26,'sub_total_row_height':26,'custom_row_height':{'root':38},'row_level_height':[40]}}

def rule(id='sign',target=BIG,test=BIG,threshold=0,scope='both',icon=None):
    app={'textColor':'#A60000'}
    if icon:app={'icon':icon,'iconColor':'#A60000'}
    return dict(id=id,label='Indicator',target=target,test=test,operator='<',threshold=threshold,
                rowScope=scope,columnScope=scope,excludeRowTotal=scope=='child',excludeColumnTotal=scope=='child',appearance=app)

def model():
    fields=[]
    for table,names in [('Product',['Brand','Category','SKU','Key']),('Region',['Area','Region','Key']),('Calendar',['Year','Month'])]:
        fields += [dict(id=f'{table}[{n}]',tableName=table,columnName=n,columnType='Column',dataType='Text') for n in names]
    return {'fields':fields}

def group():
    return dict(leaf='Product[SKU]',key='Product[Key]',ancestors=['Product[Brand]','Product[Category]'],
                unique=True,determinesAncestors=True,evidence='Synthetic stable unique key contract')

def assignments(m):
    return [field(m,k,'rows',i) for i,k in enumerate(['Product[Brand]','Product[Category]','Product[SKU]','Region[Area]','Region[Region]'])]

class FormattingTests(unittest.TestCase):
    def test_font_units_and_types(self):
        r=compile_formatting(state(),{'typography':{'size':{'value':10,'unit':'pt'},'headerSize':{'value':14}}})
        self.assertEqual(r['state']['globalStyles']['fontSize'],'13.333333')
        self.assertEqual(r['state']['globalStyles']['headerFontSize'],'14px')
        self.assertEqual(r['unitConversions'][0]['rounding'],'six decimal places')
        for bad in (14,'14px','10pt',True):
            s=state();s['globalStyles']['fontSize']=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):compile_formatting(s,{})

    def test_scoped_types_and_header_subset(self):
        for v in ({'fontSize':'14'},{'bold':'semiBold'},{'horizontalAlignment':'center'},{'fontFamily':4},{'scaling':1000}):
            with self.subTest(v=v),self.assertRaises(ValueError):format_values(v)
        with self.assertRaises(ValueError):format_values({'decimals':2},header=True)
        self.assertEqual(format_values({'fontFamily':'Segoe UI','fontSize':14}),{'4':'Segoe UI','16':14})

    def test_preservation_and_failure_atomicity(self):
        s=state();original=copy.deepcopy(s)
        r=compile_formatting(s,{'typography':{'fontFamily':'Segoe UI'}})['state']
        self.assertEqual(s,original);self.assertEqual(r['businessPolicy'],s['businessPolicy'])
        self.assertEqual(r['filters'],s['filters']);self.assertTrue(r['globalStyles']['privateFutureOption'])
        with self.assertRaises(ValueError):compile_formatting(s,{'typography':{'fontSize':13}})
        self.assertEqual(s,original)

    def test_read_edit_modes_complete_and_preserved(self):
        s=state();s['globalStyles']['columnStyle']={'locked':{'edit':{'future':'keep'}},
            'forecastOpen':{'read':{'borderSides':None,'borderWidth':3,'future':7}}}
        req={'columnStyles':{'forecastOpen':{mode:{'background':'#FFFFDD','fontSize':14} for mode in ('read','edit')}}}
        r=compile_formatting(s,req)['state']['globalStyles']['columnStyle']
        self.assertEqual(r['locked']['edit']['future'],'keep')
        self.assertNotIn('read',r['locked'])  # a missing mode stays missing: no Column Style
        self.assertTrue(set(SNAPSHOT['columnStyle'])<=set(r['locked']['edit']))
        self.assertIsNone(r['forecastOpen']['read']['borderSides']);self.assertEqual(r['forecastOpen']['read']['borderWidth'],3)
        self.assertEqual(r['forecastOpen']['read']['future'],7)
        self.assertTrue(set(SNAPSHOT['columnStyle'])<=set(r['forecastOpen']['edit']))
        with self.assertRaises(ValueError):compile_formatting(s,{'columnStyles':{'custom':{'edit':{'presetType':'Customize'}}}})

    def test_header_contrast_and_separate_header_id(self):
        req={'headers':[{'scope':'year','format':{'textColor':'#FFFFFF','background':'#303B5D','fontSize':14},'height':28,'headerId':'year-band'}]}
        r=compile_formatting(state(),req,resolved={'header':['year-band']})['state']
        self.assertEqual(r['columnHierarchyHeader']['year-band']['height'],28)
        self.assertNotIn('year',r['columnHierarchyHeader'])
        for fmt in ({'textColor':'#FFFFFF'},{'textColor':'#FFFFFF','background':'#FFFFFF'}):
            with self.assertRaises(ValueError):compile_formatting(state(),{'headers':[{'scope':'year','format':fmt}]})

    def test_operation_order_and_idempotence(self):
        req={'operations':[{'key':'amount-decimals','scope':'measure','id':BIG,'format':{'decimals':0,'scaling':'none'}}]}
        a=compile_formatting(state(),req);b=compile_formatting(a['state'],req,ledger=a['ledger'])
        self.assertEqual(a,b);self.assertEqual(a['ledger']['amount-decimals']['order'],8)
        self.assertEqual(a['state']['formatConfig']['formatSize'],9)
        self.assertEqual(a['state']['formatConfig']['measure'][BIG][0]['format'],{'4':'Arial'})
        req['operations'][0]['format']['decimals']=2
        c=compile_formatting(b['state'],req,ledger=b['ledger'])
        self.assertEqual(len(c['state']['formatConfig']['measure'][BIG]),2)
        self.assertEqual(c['state']['formatConfig']['formatSize'],9)

    def test_ids_are_lossless_and_resolved(self):
        for mid in (int(BIG),'missing'):
            with self.assertRaises(ValueError):compile_formatting(state(),{'rules':[rule(target=mid)]})
        r=compile_formatting(state(),{'rules':[rule()]})['state']['jet_cfProps']['rules'][0]
        self.assertEqual(r['highlightedMeasure'],BIG)
        self.assertEqual(r['highlightedMeasureName'],'Amount')
        self.assertEqual(r['basedOnMeasureName'],'Amount')

    def test_rule_target_condition_and_leaf_rollup_scope(self):
        req=[rule('negative'),rule('comment','2','3',threshold=1,scope='child',icon='flag')]
        req[1]['operator']='=='
        rr=compile_formatting(state(),{'rules':req})['state']['jet_cfProps']['rules']
        self.assertEqual(rr[0]['columnRuleFor'],'both');self.assertFalse(rr[0]['excludeColumnTotal'])
        c=rr[1];self.assertEqual(c['highlightedMeasure'],'2');self.assertEqual(c['highlightedMeasureName'],'Comment')
        self.assertEqual(c['conditions'][0]['basedOn'],'3');self.assertEqual(c['basedOnMeasureName'],'Flag')
        self.assertEqual(c['ruleFor'],'child');self.assertTrue(c['excludeRowTotal'])
        self.assertFalse(c['applyTextColor']);self.assertFalse(c['applyBackgroundColor']);self.assertEqual(c['icon'],'flag')
        self.assertTrue(set(SNAPSHOT['conditionSeed'])<=set(c['conditions'][0]))
        for r in rr:self.assertFalse(r['includeNull']);self.assertFalse(r['bold']);self.assertFalse(r['hatched'])

    def test_thresholds_strict_boundaries_and_icons_serialized(self):
        # Synthetic expected predicates; not a substitute for the native evaluator.
        for op,threshold,expected in [('>',7,[False,False,True,False]),('<',-3,[True,False,False,False])]:
            r=rule();r.update(operator=op,threshold=threshold)
            for icon in ('up','down','flag'):
                r['appearance']={'icon':icon,'iconColor':'#A60000'}
                out=compile_formatting(state(),{'rules':[r]})['state']['jet_cfProps']['rules'][0]
                c=out['conditions'][0]
                values=[threshold-1,threshold,threshold+1,None]
                actual=[False if v is None else (v>c['comparisonValue'] if c['operator']=='>' else v<c['comparisonValue']) for v in values]
                self.assertEqual(actual,expected);self.assertFalse(out['includeNull'])

    def test_rule_merge_identity_preserves_unrelated_metadata(self):
        a=compile_formatting(state(),{'rules':[rule()]})['state'];r=a['jet_cfProps']['rules'][0]
        r['future']='keep';r['conditions'][0]['future']='keep';r['rankingBuckets']=['inactive-preserve']
        a['cfProps']={'enabled':False,'rules':[{'name':'legacy'}]}
        a['jet_cfProps']['rules'].append({'name':'unrelated','opaque':True})
        b=compile_formatting(a,{'rules':[rule()]})['state']
        self.assertEqual(b['cfProps']['rules'][0],a['cfProps']['rules'][0])
        self.assertEqual(len(b['cfProps']['rules']),2);self.assertTrue(b['cfProps']['enabled'])
        self.assertEqual(len(b['jet_cfProps']['rules']),2)
        self.assertEqual(b['jet_cfProps']['rules'][0]['rankingBuckets'],['inactive-preserve'])
        self.assertEqual(b['jet_cfProps']['rules'][0]['conditions'][0]['future'],'keep')
        self.assertEqual(b['jet_cfProps']['rules'][1],a['jet_cfProps']['rules'][1])

    def test_sizing_preserves_customs_and_no_legacy_write(self):
        a=state();a['globalStyles']['rowHeight']=55
        b=compile_formatting(a,{'sizing':{'rowHeight':28,'measureWidths':{BIG:120},'wrapColumns':True}})['state']
        self.assertEqual(b['row_height_config']['custom_row_height'],{'root':38})
        self.assertEqual(b['row_height_config']['row_level_height'],[40]);self.assertEqual(b['globalStyles']['rowHeight'],55)
        self.assertNotIn('formatType',b.get('numberFormatting',{}))

    def test_zero_null_independent_and_no_calculation_change(self):
        b=compile_formatting(state(),{'numberFormatting':{'showZeroAs':'hyphen','showNullAs':'blank','noOfDecimal':0}})['state']
        self.assertEqual(b['numberFormatting']['showNullAs'],'blank')
        self.assertNotIn('enableNullAsZero',b['numberFormatting'])
        with self.assertRaises(ValueError):compile_formatting(state(),{'numberFormatting':{'enableNullAsZero':True}})
    def test_current_scaling_and_auto_locale_properties_are_typed(self):
        b=compile_formatting(state(),{'numberFormatting':{
            'scalingFactor':'1000000000000','autoLocaleNumberFormat':True}})['state']
        self.assertEqual(b['numberFormatting']['scalingFactor'],'1000000000000')
        self.assertIs(b['numberFormatting']['autoLocaleNumberFormat'],True)
        with self.assertRaises(ValueError):compile_formatting(state(),{'numberFormatting':{'autoLocaleNumberFormat':'true'}})
    def test_safe_current_number_format_contract_is_supported(self):
        patch={'enabled':True,'enableSuffixAsUnit':True,'prefix':'$','suffix':'',
            'positiveValueColor':'#008000','positiveValueFormat':'+x',
            'negativeValueColor':'#A60000','neutralValueColor':'#666666',
            'customNullText':'n/a','customZeroText':'-','formatType':'custom',
            'scalingTextType':'Medium','trillion':'tn','tooltipDecimal':'2',
            'suppressCellErrors':True,'customErrorText':'#ERR',
            'showDisplayUnit':True}
        b=compile_formatting(state(),{'numberFormatting':patch})['state']['numberFormatting']
        self.assertTrue(set(patch)<=set(b))
        self.assertEqual(b['positiveValueFormat'],'+x')
        with self.assertRaises(ValueError):compile_formatting(state(),{
            'numberFormatting':{'positiveValueFormat':'invalid'}})
    def test_number_format_mode_applies_native_scaling_side_effects(self):
        candidate=state();candidate['formatConfig']={
            'measure':{BIG:[{'format':{'13':'1000','4':'Arial'},'order':1}]},
            'cell':{BIG:[{'format':{'13':'none'},'order':2}]},
            'row':{BIG:[{'format':{'13':'auto','1':True},'order':3}]}}
        b=compile_formatting(candidate,{'numberFormatting':{'formatType':'default'}})['state']
        self.assertEqual(b['numberFormatting']['scalingFactor'],'autoFixed')
        self.assertEqual(b['formatConfig']['measure'][BIG][0]['format']['13'],'1000')
        self.assertNotIn(BIG,b['formatConfig']['cell'])
        self.assertEqual(b['formatConfig']['row'][BIG][0]['format'],{'1':True})
        with self.assertRaises(ValueError):compile_formatting(candidate,{
            'numberFormatting':{'formatType':'ibcs','noOfDecimal':2}})
    def test_row_heights_follow_native_u32_contract(self):
        b=compile_formatting(state(),{'sizing':{'rowHeight':28,'subtotalHeight':0}})['state']
        self.assertEqual(b['row_height_config']['default_row_height'],28)
        self.assertEqual(b['row_height_config']['sub_total_row_height'],0)
        for key in ('rowHeight','subtotalHeight'):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):compile_formatting(state(),{'sizing':{key:26.5}})

    def test_unknown_requirement_reported_without_fake_state(self):
        b=compile_formatting(state(),{'selectionBlueBorderOnly':True})
        from runtime.planning_integrity import complete_styles
        self.assertEqual(b['state'],complete_styles(state()));self.assertEqual(b['coverage'][0]['status'],'unsupported-or-unresolved')
        self.assertNotIn('selectionBlueBorderOnly',b['state'])

    def test_cli_decimal_roundtrip_and_rule_counts_derived_from_request(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'candidate.json'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/plan.py'),'format-matrix','--input',str(ROOT/'assets/examples/matrix-formatting.request.json'),'--out',str(p)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            candidate=json.loads(p.read_text())
            request=json.loads((ROOT/'assets/examples/matrix-formatting.request.json').read_text())
            self.assertEqual(len(candidate['state']['jet_cfProps']['rules']),len(request['request']['rules']))
            self.assertEqual(candidate['state']['globalStyles']['columnStyle']['custom']['edit']['fontSize'],13.333333)

    def test_grid_wire_names_and_enums(self):
        with self.assertRaises(ValueError):compile_formatting(state(),{'gridStyles':{'gridBorderColor':'#A6A6A6'}})
        with self.assertRaises(ValueError):compile_formatting(state(),{'gridStyles':{'verticalMinorGridLines':'dashed'}})
        out=compile_formatting(state(),{'gridStyles':{'gridBorderLineWidth':0,'gridBorderLineColor':'#A6A6A6'}})
        self.assertEqual(out['state']['gridStyles']['gridBorderLineWidth'],0)

    def test_forecast_direct_fill_warning(self):
        s=state();s['formatConfig']['measure'][BIG][0]['format']['5']='#FFFFDD'
        r=compile_formatting(s,{'forecastMeasureIds':[BIG]})
        self.assertTrue(any('hide open/closed' in w for w in r['warnings']))

class LeafTests(unittest.TestCase):
    def test_ancestors_skip_two_tables_and_visible_assignments_unchanged(self):
        m=model();a=assignments(m);original=copy.deepcopy(a)
        region=dict(leaf='Region[Region]',key='Region[Key]',ancestors=['Region[Area]'],unique=True,determinesAncestors=True,evidence='Synthetic key contract')
        out=leaf_key_mapping(m,a,[group(),region]);self.assertEqual(a,original)
        self.assertEqual(out['mappings']['Product[Category]'],{'Skip':{}})
        self.assertEqual(out['mappings']['Product[SKU]'],{'ID':'Product[Key]'})
        self.assertEqual(out['mappings']['Region[Region]'],{'ID':'Region[Key]'})
        self.assertTrue(any(d['id']=='Product[Key]' for d in out['pivot']))

    def test_explicit_label_override(self):
        out=leaf_key_mapping(model(),assignments(model()),[group()],overrides={'Product[Brand]':None})
        self.assertNotIn('Product[Brand]',out['mappings']);self.assertEqual(out['mappings']['Product[Category]'],{'Skip':{}})

    def test_ambiguous_key_and_independent_dimension_rejected(self):
        for patch in ({'unique':False},{'determinesAncestors':False},{'evidence':''},{'ancestors':['Region[Area]']}):
            g=group();g.update(patch)
            with self.subTest(patch=patch),self.assertRaises(ValueError):leaf_key_mapping(model(),assignments(model()),[g])

    def test_no_silent_existing_storage_migration(self):
        m=model();a=assignments(m)
        with self.assertRaises(ValueError):leaf_key_mapping(m,a,[group()],existing={'mappings':{}})
        first=leaf_key_mapping(m,a,[group()]);self.assertEqual(leaf_key_mapping(m,a,[group()],existing=first),first)

    def test_calendar_and_leaf_override_cannot_break_skip(self):
        g=group();g['isTime']=True
        with self.assertRaises(ValueError):leaf_key_mapping(model(),assignments(model()),[g])
        with self.assertRaises(ValueError):leaf_key_mapping(model(),assignments(model()),[group()],overrides={'Product[SKU]':None})

    def test_new_builder_and_scope_apply_policy(self):
        m=json.loads((ROOT/'assets/fixtures/model.json').read_text());m['fields'] += [f for f in model()['fields'] if f['id'] not in {x['id'] for x in m['fields']}]
        spec={'name':'Synthetic example','requiredCapabilities':['planning.native-measure','planning.dimension-id-mapping'],'sheets':[{'name':'Plan','rows':['Product[Brand]','Product[Category]','Product[SKU]'],
            'columns':['Calendar[Year]'],'dimensionKeyGroups':[group()],
            'measures':[{'key':'actual','label':'Actual','kind':'Native','source':'Metrics[BasePay]'}]}]}
        out=prepare_scope(spec,SUPPORTED,m);preflight(out['spec']);result=build(m,out['spec'])
        vs=next(v['properties']['visualState'] for k,v in result['raw'].items() if k.endswith('/properties.json'))
        self.assertEqual(len(vs['rowDimensions']),3)
        self.assertEqual(vs['dimension_id_mapping']['mappings']['Product[Brand]'],{'Skip':{}})

    def test_new_forecast_has_no_blanket_background(self):
        m=json.loads((ROOT/'assets/fixtures/model.json').read_text())
        m['fields'].append(dict(id='Calendar[Year]',tableName='Calendar',columnName='Year',columnType='Column',dataType='Text'))
        spec={'name':'Synthetic forecast','sheets':[{'name':'Forecast','rows':['Employee[Employee]'],'columns':['Calendar[Year]'],
            'measures':[{'key':'actual','label':'Actual','kind':'Native','source':'Metrics[BasePay]'},
                {'key':'forecast','label':'Forecast','kind':'Forecast','actuals':'actual','start':'2026-01-01','end':'2026-12-31'}]}]}
        vs=next(v['properties']['visualState'] for k,v in build(m,spec)['raw'].items() if k.endswith('/properties.json'))
        fid=next(m['id'] for m in vs['manage_measures'] if m['label']=='Forecast')
        self.assertNotIn('5',vs['formatConfig']['measure'][fid][0]['format'])
        # Each of the two numeric measures also receives its Auto scaling op.
        self.assertEqual(vs['formatConfig']['formatSize'],4)
        for entries in vs['formatConfig']['measure'].values():
            self.assertTrue(any(e['format'].get('13')=='auto' for e in entries))

if __name__=='__main__':unittest.main()
