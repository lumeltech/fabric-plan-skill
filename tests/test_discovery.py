"""Portable discovery and the executable command paths it exposes; no live APIs."""
import ast
from contextlib import redirect_stdout
import copy
import io
import json
from pathlib import Path
import shlex
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
    def test_every_leaf_guide_is_reachable_without_a_second_hop(self):
        import plan
        root = ROOT / 'references'
        leaves = {p.relative_to(root).as_posix() for p in root.rglob('*.md')}
        modules = catalog()['modules']
        self.assertEqual(len({m['id'] for m in modules}), len(modules))
        guides = {g['file'] for m in modules for g in m['guides']}
        self.assertEqual(leaves, guides)
        listing = render(discover(), compact=True)
        for file in guides:
            self.assertIn('python plan.py reference ' + file, listing)
            with patch.object(sys, 'argv', ['plan.py', 'reference', file]), redirect_stdout(io.StringIO()) as out:
                plan.main()
            text = (root / file).read_text(encoding='utf-8-sig')
            self.assertEqual(out.getvalue().strip(), text.strip())
            self.assertNotRegex(text, r'(?i)(?:[\w/-]+\.md\b|plan\.py (?:discover|reference)\b)')

    def test_catalog_exposes_only_local_or_public_operations(self):
        data = catalog()
        self.assertFalse((ROOT / 'references' / 'intelligence').exists())
        self.assertEqual({op for m in data['modules'] for op in m['operations']}, set(data['actions']))
        for module in ('INTELLIGENCE', 'F24', 'BUSINESS-NAVIGATION', 'METADATA-BACKEND'):
            with self.assertRaises(ValueError):
                discover(module=module)
        for action in data['actions'].values():
            self.assertIn(action['phase'], {'local', 'public-read', 'public-write'})
            if action['phase'] != 'local':
                self.assertIn(action['command'].split()[2:4], [['api', 'export'], ['api', 'create'], ['api', 'update']])

    def test_every_advertised_callable_exists(self):
        for op in catalog()['actions'].values():
            for symbol in op['symbols']:
                module,name=symbol.rsplit('.',1)
                tree=ast.parse((ROOT/Path(*module.split('.')).with_suffix('.py')).read_text(encoding='utf-8-sig'))
                self.assertTrue(any(isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name for n in tree.body),symbol)

    def test_cli_parser_accepts_complete_advertised_commands(self):
        import argparse
        import plan
        # Exercise argparse choices and required flags, but stop before dispatch.
        parse = argparse.ArgumentParser.parse_args
        class Parsed(Exception):
            pass
        def parse_only(parser):
            parse(parser)
            raise Parsed
        for action in catalog()['actions'].values():
            if action['command']:
                argv = shlex.split(action['command'])[1:]
                with self.subTest(argv=argv), patch.object(sys, 'argv', argv), patch.object(argparse.ArgumentParser, 'parse_args', parse_only):
                    with self.assertRaises(Parsed):
                        plan.main()

    def test_business_queries_route_to_actionable_guides(self):
        for query, expected in [('rolling forecast', 'F09'), ('quarterly commentary', 'F05'),
                                ('from sheets', 'F19'), ('negative variance', 'F15'),
                                ('employee master', 'POWERTABLE'), ('compare PowerTable sheets', 'POWERTABLE')]:
            self.assertIn(expected, [m['id'] for m in discover(query)['modules'][:3]], query)
        approval = discover(module='f13')['modules'][0]
        self.assertEqual(approval['operations'], [])
        self.assertIn('Guidance only', render(discover(module='F13')))
        self.assertEqual(discover('zzzznotafeature')['count'], 0)

    def test_json_cli_is_read_only_and_portable(self):
        result = subprocess.run([sys.executable, str(ROOT/'plan.py'), 'discover', '--module', 'F19', '--json'],
                                cwd=ROOT.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        route = json.loads(result.stdout)['modules'][0]
        self.assertIn('python plan.py reference measure-source-bindings.md',
                      {guide['command'] for guide in route['guides']})
        self.assertTrue(all(op['phase'] == 'local' for op in route['operations']))

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
        with tempfile.TemporaryDirectory(dir=ROOT) as td:
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

if __name__=='__main__':unittest.main()
