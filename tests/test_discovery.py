"""Portable discovery and the executable command paths it exposes; no live APIs."""
import ast
from contextlib import contextmanager, redirect_stdout
import copy
from decimal import Decimal
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from runtime.discovery import catalog, discover, render
from runtime.codec import load
from runtime.construct import build
from runtime.scope import prepare_scope
from runtime.workflow import preflight, SUPPORTED

ROOT=Path(__file__).resolve().parents[1]


class DiscoveryTests(unittest.TestCase):
    def test_all_numbered_modules_and_related_routes_resolve(self):
        c=catalog(); ids=[m['id'] for m in c['modules']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual({i for i in ids if re.fullmatch(r'F\d\d',i)}, {f'F{i:02}' for i in range(1,31)})
        for m in c['modules']:
            self.assertTrue(m['businessRequests'])
            self.assertTrue(m['prerequisites'])
            self.assertTrue(m['limitations'])
            for other in m['related']:self.assertIn(other,ids)
            for op in m['operations']:self.assertIn(op,c['actions'])
            for g in m['guides']:
                text=(ROOT/'references'/g['file']).read_text(encoding='utf-8-sig')
                if g['heading']:
                    headings=[re.sub(r'^#+\s*','',line) for line in text.splitlines() if line.startswith('#')]
                    self.assertEqual(headings.count(g['heading']),1,(m['id'],g))

    def test_every_advertised_callable_exists(self):
        for op in catalog()['actions'].values():
            for symbol in op['symbols']:
                module,name=symbol.rsplit('.',1)
                tree=ast.parse((ROOT/Path(*module.split('.')).with_suffix('.py')).read_text(encoding='utf-8-sig'))
                self.assertTrue(any(isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name for n in tree.body),symbol)

    def test_advertised_cli_routes_are_accepted_by_parser(self):
        prefixes=set()
        for op in catalog()['actions'].values():
            if op['command']:
                parts=op['command'].split()[2:]
                if '--' in ' '.join(parts):parts=parts[:next(i for i,v in enumerate(parts) if v.startswith('--'))]
                prefixes.add(tuple(parts))
        for prefix in sorted(prefixes):
            result=subprocess.run([sys.executable,str(ROOT/'plan.py'),*prefix,'--help'],capture_output=True,text=True,cwd=ROOT)
            self.assertEqual(result.returncode,0,(prefix,result.stderr))

    def test_callable_only_native_routes_are_not_advertised_as_cli_commands(self):
        catalog_data=catalog()
        blocked={'column-create','column-register','forecast-review','pivot','rule-create',
                 'bridge-query','bridge-inventory','bridge-reload','bridge-poll','bridge-stream',
                 'table-initialize','table-schema','table-save','place','home-priority',
                 'home-effective','bookmark','navigator-create','bookmark-read',
                 'powertable-schema','anchor-save'}
        self.assertEqual(catalog_data['release'],'v50')
        for action in blocked:
            self.assertIsNone(catalog_data['actions'][action]['command'],action)
            self.assertEqual(catalog_data['actions'][action]['phase'],'approved-external-adapter',action)
            self.assertTrue(catalog_data['actions'][action]['symbols'],action)
        rendered=render(discover(module='INTELLIGENCE'))
        self.assertNotIn('python plan.py forecast-review',rendered)
        self.assertNotIn('python plan.py native place',rendered)

    def test_powertable_modes_and_external_sql_companion_are_routed(self):
        route=discover(module='POWERTABLE')['modules'][0]
        guides={g['file'] for g in route['guides']}
        expected={
            'powertable/index.md',
            'powertable/connect-existing-tables.md',
            'powertable/create-from-scratch.md',
            'powertable/modeling.md',
            'powertable/column-mappings.md',
            'powertable/analyze-data.md',
            'powertable/analyze-across-sheets.md',
        }
        self.assertTrue(expected<=guides)
        for query in ('PowerTable from scratch','analyze PowerTable','compare PowerTable sheets'):
            self.assertIn('POWERTABLE',[m['id'] for m in discover(query)['modules']])
        index=(ROOT/'references/powertable/index.md').read_text()
        self.assertIn('github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli',index)
        self.assertIn('external companion',index)

    def test_current_skill_and_core_references_have_clean_encoding(self):
        suspects=('Ã','â€','Â','Æ’')
        paths=[ROOT/'SKILL.md',*(ROOT/'references').glob('*.md')]
        for path in paths:
            text=path.read_text(encoding='utf-8')
            for marker in suspects:
                self.assertNotIn(marker,text,f'{path.relative_to(ROOT)} contains {marker!r}')

    def test_business_search_and_guide_only_limits(self):
        for query,expected in [('rolling forecast','F09'),('quarterly commentary','F05'),
                               ('from sheets','F19'),('negative variance','F15'),
                               ('employee master','POWERTABLE'),('time extension','F09')]:
            self.assertIn(expected,[m['id'] for m in discover(query)['modules']],query)
        approval=discover(module='f13')['modules'][0]
        self.assertEqual(approval['coverage'],'guide-only')
        self.assertEqual(approval['operations'],[])
        self.assertEqual(discover('zzzznotafeature')['count'],0)
        with self.assertRaises(ValueError):discover(module='F99')
        self.assertIn('No complete creation command',render(discover(module='F13')))

    def test_json_cli_is_read_only_and_portable(self):
        result=subprocess.run([sys.executable,str(ROOT/'plan.py'),'discover','--module','F19','--json'],capture_output=True,text=True,cwd=ROOT.parent)
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout)
        self.assertEqual(data['modules'][0]['operations'][0]['id'],'forecast-review')

    def test_intelligence_mode_guides_are_discoverable_and_readable(self):
        result=discover('Intelligence visual design')
        route=next(m for m in result['modules'] if m['id']=='INTELLIGENCE')
        guides={g['file']:g for g in route['guides']}
        expected=['index','discovery','design','authoring','management','feature-master-list']
        for name in expected:
            path=f'intelligence/{name}.md'
            self.assertIn(path,guides)
            self.assertIn(guides[path]['command'],render(discover(module='INTELLIGENCE')))
        result=subprocess.run(
            [sys.executable,str(ROOT/'plan.py'),'reference','intelligence/index.md'],
            capture_output=True,text=True,cwd=ROOT.parent)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Intelligence reference index',result.stdout)
        self.assertIn('features/matrix/_index.md',result.stdout)

    def test_reference_rejects_noncanonical_and_hidden_paths(self):
        import plan
        for name in ['../SKILL.md','intelligence/../../SKILL.md',str(ROOT/'SKILL.md'),
                     'intelligence\\index.md','intelligence/./index.md',
                     'intelligence/.private.md','.']:
            with self.subTest(name=name), patch.object(sys,'argv',['plan.py','reference',name]):
                with self.assertRaises(ValueError):
                    plan.main()

    @unittest.skipIf(sys.platform=='win32','Symlink creation can require privileges on Windows')
    def test_reference_rejects_symlink_outside_reference_root(self):
        import plan
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); references=root/'references'; references.mkdir()
            (root/'outside.md').write_text('Not a bundled reference',encoding='utf-8')
            (references/'escape.md').symlink_to(root/'outside.md')
            with patch.object(plan,'ROOT',root), patch.object(sys,'argv',['plan.py','reference','escape.md']):
                with self.assertRaisesRegex(ValueError,'bundled reference path'):
                    plan.main()

    def test_custom_time_axis_survives_scope_and_preflight(self):
        model=load(ROOT/'fixtures/model.json')
        for key,label in [('Calendar[FY]','FY'),('Calendar[FQ]','FQ')]:
            model['fields'].append(dict(id=key,tableName='Calendar',columnName=label,columnType='Column',dataType='Text'))
        spec=dict(name='Synthetic routed Forecast',requiredCapabilities=['planning.native-measure','planning.forecast'],sheets=[
            dict(name='Forecast',rows=['Employee[Employee]'],columns=['Calendar[FY]','Calendar[FQ]'],
                 columnTimeLevels={'Calendar[FY]':'Year','Calendar[FQ]':'Quarter'},
                 measures=[dict(key='actual',kind='Native',label='Actual',source='Metrics[BasePay]'),
                           dict(key='forecast',kind='Forecast',label='Forecast',actuals='actual',start='2026-01-01',end='2026-12-31')])])
        original=copy.deepcopy(spec)
        scope=prepare_scope(spec,SUPPORTED,model)
        preflight(scope['spec'])
        result=build(model,scope['spec'])
        props=next(v['properties'] for k,v in result['raw'].items() if k.endswith('/properties.json'))
        self.assertEqual([x['timeIntervalUnit'] for x in props['visualState']['columnDimensions']],['Year','Quarter'])
        self.assertEqual(spec,original)

    def test_forecast_review_native_cli_stops_before_authentication(self):
        import plan
        argv=['plan.py','forecast-review','--config','unused','--input','unused','--run','unused']
        with patch.object(sys,'argv',argv), patch('runtime.session.native_session') as session:
            with self.assertRaises(SystemExit):
                plan.main()
            session.assert_not_called()


if __name__=='__main__':unittest.main()
