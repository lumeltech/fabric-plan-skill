"""Offline regressions: selection isolation, exact Auto wire and preservation."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,tempfile,unittest
from pathlib import Path
from runtime.chart_filters import ensure_chart_filters,audit_chart_filters
from runtime.column_presentation import ensure_assigned_measure_filters
from runtime.filters import ensure_axis_filters,select_axis_filter
from runtime.display_defaults import (auto_number_formatting,planning_display_defaults,
                                      clear_measure_filter_selections,measure_filter_card)
from runtime.usecases import catalog,recipe,field_requirements,prepare

ROOT=Path(__file__).resolve().parents[1]

def dimension():
    return {'id':'Calendar[Year]','sourceId':'Calendar[Year]','columnName':'Year','tableName':'Calendar',
            'sourceType':'PowerBI','dataType':'Int64','dataRoleType':'Grouping','columnType':'Column','bucketId':'columns','order':0}

def value(source='PowerBI'):
    return {'id':'Facts[Amount]' if source=='PowerBI' else '7[17]' if source=='InfoBridge' else '17',
            'sourceId':'Facts[Amount]' if source=='PowerBI' else '7[17]' if source=='InfoBridge' else '17',
            'columnName':'Amount','tableName':'Facts','sourceType':source,'dataType':'Double',
            'dataRoleType':'Measure','columnType':'Measure' if source=='PowerBI' else 'Column',
            'bucketId':'ameasure','order':0,'measureGuid':'123',
            **({'queryId':'7','aggregationType':'sum'} if source=='InfoBridge' else {}),
            **({'visualId':'9','aggregationType':'sum'} if source=='Visual' else {})}

class DisplayDefaultsTests(unittest.TestCase):
    def test_dimension_selection_never_leaks_into_measure_evaluation_grain(self):
        for source in ('PowerBI','InfoBridge','Visual'):
            p={'pivotAssignments':[dimension(),value(source)]}
            ensure_axis_filters(p);ensure_assigned_measure_filters(p)
            before=copy.deepcopy(p['pivotAssignments'])
            selected=[{'columnIds':['Calendar[Year]'],'filterType':'VALUES','valuesFilter':[{'id':[2026]}]}]
            select_axis_filter(p,'Calendar[Year]',selected)
            cards=p['superFilterAssignments'];self.assertEqual(len(cards),2)
            self.assertEqual(cards[0]['filter'],selected)
            self.assertEqual(cards[1]['filter'],[])
            self.assertIsNone(cards[1]['configuration']['alphaNumericValues']['minValue'])
            self.assertEqual(cards[1]['pivotAssignments'],before)
            self.assertEqual(p['pivotAssignments'],before)

    def test_chart_value_cards_are_visible_at_all_and_existing_choices_survive(self):
        a=value('InfoBridge');a['bucketId']='AC'
        p={'pivotAssignments':[dimension(),a]};ensure_chart_filters(p)
        self.assertEqual(audit_chart_filters(p)['visibleFieldFilters'],2)
        m=next(r for r in p['superFilterAssignments'] if measure_filter_card(r))
        self.assertEqual(m['filter'],[]);self.assertFalse(m['configuration']['hide'])
        m['filter']=[{'filterType':'RANGE','rangeFilter':[{'from':100}]}]
        before=copy.deepcopy(p);ensure_chart_filters(p)
        self.assertEqual(p,before)

    def test_explicit_reset_keeps_cards_dimension_selection_context_and_bindings(self):
        p={'pivotAssignments':[dimension(),value()]};ensure_axis_filters(p);ensure_assigned_measure_filters(p)
        regs=p['superFilterAssignments'];regs[0]['filter']=[{'year':2026}]
        regs[1]['filter']=[{'wrongYear':2026}];regs[1]['configuration']['alphaNumericValues']['minValue']=5
        context={'isContextDimension':True,'isDefaultMeasure':True,'filter':[{'scenario':'Budget'}]}
        regs.append(context);before=copy.deepcopy(p)
        q=clear_measure_filter_selections(p)
        self.assertEqual(p,before);self.assertEqual(len(q['superFilterAssignments']),3)
        self.assertEqual(q['superFilterAssignments'][0],regs[0]);self.assertEqual(q['superFilterAssignments'][2],context)
        self.assertEqual(q['superFilterAssignments'][1]['filter'],[])
        self.assertIsNone(q['superFilterAssignments'][1]['configuration']['alphaNumericValues']['minValue'])
        self.assertEqual(q['pivotAssignments'],p['pivotAssignments'])

    def test_auto_changes_only_scaling_and_is_idempotent_across_operation_order(self):
        vs={'manage_measures':[{'id':'123'}],'numberFormatting':{'formatType':'default','scalingFactor':'autoFixed'},
            'formatConfig':{'measure':{'123':[{'format':{'3':'#1F5AA6','10':True,'11':1,'8':'USD '},'order':2}]},
                            'cell':{'cell-id':[{'format':{'1':True},'order':99}]},'formatSize':3}}
        q=auto_number_formatting(vs,['123'])
        self.assertEqual(q['formatConfig']['measure']['123'][-1],{'format':{'13':'auto'},'order':100})
        self.assertEqual(q['formatConfig']['formatSize'],101)
        self.assertEqual(q['formatConfig']['measure']['123'][0],vs['formatConfig']['measure']['123'][0])
        self.assertEqual(q['numberFormatting'],vs['numberFormatting'])
        self.assertEqual(q,auto_number_formatting(q,['123']))
        self.assertNotEqual(q,vs)

    def test_explicit_fixed_scaling_preserved_unless_reset_requested(self):
        vs={'manage_measures':[{'id':'123'}],'formatConfig':{'measure':{'123':[{'format':{'13':'1000000','9':'USD'},'order':4}]}}}
        q=auto_number_formatting(vs,['123']);self.assertEqual(q['formatConfig']['measure'],vs['formatConfig']['measure'])
        q=auto_number_formatting(vs,['123'],overwrite=True)
        self.assertEqual(q['formatConfig']['measure']['123'][-1]['format'],{'13':'auto'})
        self.assertEqual(q['formatConfig']['measure']['123'][0],vs['formatConfig']['measure']['123'][0])

    def test_numeric_types_not_source_names_decide_auto(self):
        for kind in ('DataInput','Forecast','Formula','VisualColumn'):
            p={'pivotAssignments':[],'visualState':{'manage_measures':[{'id':'123'},{'id':'456'}]}}
            records=[{'measureGuid':mid,'columnMeta':{'data_type':typ,'measure_type':{kind:{}}}} for mid,typ in [('123','Number'),('456','Text')]]
            q=planning_display_defaults(p,records)
            self.assertIn('123',q['visualState']['formatConfig']['measure']);self.assertNotIn('456',q['visualState']['formatConfig']['measure'])
        for source in ('PowerBI','Visual','InfoBridge'):
            p={'pivotAssignments':[value(source)],'visualState':{'manage_measures':[{'id':'123'}]}}
            q=planning_display_defaults(p)
            self.assertEqual(q['visualState']['formatConfig']['measure']['123'][0]['format'],{'13':'auto'})

    def test_unknown_measure_identity_rejected(self):
        with self.assertRaises(ValueError):auto_number_formatting({'manage_measures':[]},['foreign'])

    def test_all_five_recipe_builds_keep_year_only_on_dimension_and_numeric_auto(self):
        # Synthetic schema assembled from the shipped symbolic recipe contracts.
        # No model data, cached report or live API is consulted.
        for entry in catalog():
            c=recipe(entry['id']);native={m['source'] for s in c['spec']['sheets'] for m in s['measures'] if m['kind']=='Native'}
            fields=[]
            for key in field_requirements(c):
                table,col=key.split('[',1);col=col[:-1]
                fields.append({'id':key,'tableName':table,'columnName':col,'columnType':'Measure' if key in native else 'Column',
                    'dataType':'Double' if key in native else 'Int64' if col in ('Year','Quarter','MonthNumber') or col.endswith(('ID','Key')) else 'String'})
            model={'reference':json.loads((ROOT/'assets/fixtures/model.json').read_text())['reference'],'fields':fields}
            with tempfile.TemporaryDirectory() as tmp:
                b,_,_=prepare(c,model,tmp,'Offline '+c['title'])
                for path,obj in b['raw'].items():
                    if not path.endswith('/properties.json'):continue
                    p=obj['properties'];vs=p.get('visualState',{})
                    if 'manage_measures' not in vs:continue
                    measure_cards=[r for r in p['superFilterAssignments'] if measure_filter_card(r)]
                    self.assertTrue(measure_cards,c['id'])
                    for r in measure_cards:self.assertEqual(r['filter'],[],(c['id'],r['configuration']['name']))
                    selected=[r for r in p['superFilterAssignments'] if r['filter']]
                    self.assertEqual(len(selected),1,c['id'])
                    self.assertEqual(selected[0]['pivotAssignments'][0]['columnName'],'Year')
                    for m in vs['manage_measures']:
                        self.assertTrue(any(e['format'].get('13')=='auto' for e in vs['formatConfig']['measure'][m['id']]),(c['id'],m['label']))

if __name__=='__main__':unittest.main()
