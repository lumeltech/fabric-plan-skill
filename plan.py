#!/usr/bin/env python3
"""Portable single-file skill runtime. All paths are explicit; no ambient repository."""
import argparse,sys,copy,re,subprocess,os
from pathlib import Path
from runtime.codec import load,save,unpack,pack,parts,sha,dumps,safe_path,definition_hash
from runtime.construct import build
from runtime.validate import validate_plan,schema_report
ROOT=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser(description=__doc__); sp=p.add_subparsers(dest='cmd',required=True)
    ds=sp.add_parser('discover',help='Find bundled guides and supported operations for a business request; local/read-only')
    ds.add_argument('query',nargs='?',default='');ds.add_argument('--module');ds.add_argument('--list',action='store_true');ds.add_argument('--json',action='store_true')
    uc=sp.add_parser('usecase',help='Self-contained five-business-case discovery, model intake and local construction')
    uc.add_argument('action',choices=['list','show','model','build']);uc.add_argument('--case');uc.add_argument('--recipe');uc.add_argument('--config');uc.add_argument('--model');uc.add_argument('--run');uc.add_argument('--name');uc.add_argument('--out')
    bi=sp.add_parser('plan-intent',help='Route agent-interpreted business outcomes, dependencies and unresolved decisions; local only')
    bi.add_argument('--input',required=True);bi.add_argument('--out',required=True)
    fm=sp.add_parser('format-matrix',help='Offline typed Matrix style candidate, preserved state and requirement coverage')
    fm.add_argument('--input',required=True);fm.add_argument('--out',required=True)
    dd=sp.add_parser('planning-display-defaults',help='Offline numeric Auto scaling and explicit reset of measure selections to All; retains cards; no live writes')
    dd.add_argument('--input',required=True);dd.add_argument('--out',required=True)
    cp=sp.add_parser('planning-column-presentation',help='Local Planning column expansion, sizing, totals and unrestricted Values cards; no live writes')
    cp.add_argument('--input',required=True);cp.add_argument('--out',required=True);cp.add_argument('--expansion-only',action='store_true')
    for command in ('inspect-reference-views','fit-planning-header','planning-hierarchy-icons'):
        hf=sp.add_parser(command,help='Local content-based header sizing or gmate hierarchy defaults; no live writes')
        hf.add_argument('--input',required=True);hf.add_argument('--out',required=True)
    for command in ('planning-totals','roll-forward-presentation'):
        rf=sp.add_parser(command,help='Local native Planning totals or resolved Measures in Rows hierarchy; no live writes')
        rf.add_argument('--input',required=True);rf.add_argument('--out',required=True)
    iv=sp.add_parser('integrated-variance',help='Style a resolved AC/PY column comparison as native integrated variance; preserve field bindings')
    iv.add_argument('--input',required=True);iv.add_argument('--out',required=True)
    pp=sp.add_parser('present-planning',help='Offline rich description and semantic measure colors from current typed measure records')
    pp.add_argument('--input',required=True);pp.add_argument('--out',required=True)
    mb=sp.add_parser('resolve-measure-binding',help='Construct a typed PowerBI, From Sheets or InfoBridge assignment from exact current catalog identities')
    mb.add_argument('--input',required=True);mb.add_argument('--out',required=True)
    ac=sp.add_parser('check-application-presentation',help='Offline required rich-dashboard coverage for every Planning owner')
    ac.add_argument('--input',required=True);ac.add_argument('--out',required=True)
    ad=sp.add_parser('check-application-defaults',help='Check typography, dashboard coverage, public Home visibility and a local Home layout; does not publish role-specific content')
    ad.add_argument('--input',required=True);ad.add_argument('--home',required=True);ad.add_argument('--out',required=True)
    for command in ('check-planning-properties','repair-planning-properties'):
        pi=sp.add_parser(command,help='Offline complete-formatting and canonical semantic-name checks/repair; preserves IDs and stored values')
        pi.add_argument('--input',required=True);pi.add_argument('--out',required=True);pi.add_argument('--model')
    lk=sp.add_parser('leaf-key-mapping',help='Offline leaf ID and ancestor Skip storage defaults; no value migration')
    lk.add_argument('--input',required=True);lk.add_argument('--out',required=True)
    b=sp.add_parser('build'); b.add_argument('--model',required=True); b.add_argument('--spec',required=True); b.add_argument('--out',required=True); b.add_argument('--registry')
    ic=sp.add_parser('check-import-contract',help='Verify original requested inputs, formulas and CF against a construction/candidate before import')
    ic.add_argument('--spec',required=True);ic.add_argument('--construction',required=True);ic.add_argument('--candidate');ic.add_argument('--out',required=True)
    v=sp.add_parser('validate'); v.add_argument('raw'); v.add_argument('--out',required=True)
    d=sp.add_parser('decode'); d.add_argument('envelope'); d.add_argument('--out',required=True)
    e=sp.add_parser('encode'); e.add_argument('raw'); e.add_argument('--out',required=True)
    a=sp.add_parser('audit-layout'); a.add_argument('response'); a.add_argument('--gap',type=float,default=0)
    da=sp.add_parser('audit-definition'); da.add_argument('raw'); da.add_argument('--out',required=True)
    r=sp.add_parser('reference'); r.add_argument('name'); r.add_argument('--heading'); r.add_argument('--list',action='store_true')
    t=sp.add_parser('test')
    fre=sp.add_parser('forecast-repair',help='Prepare a scoped ALM update from a working reference sheet')
    fre.add_argument('--baseline',required=True);fre.add_argument('--input',required=True);fre.add_argument('--out',required=True)
    pt=sp.add_parser('repair-powertable-config',help='Local lookup/source metadata candidate; preserves editability, row actions and unrelated parts')
    pt.add_argument('--baseline',required=True);pt.add_argument('--input',required=True);pt.add_argument('--out',required=True)
    ib=sp.add_parser('construct-bridge');ib.add_argument('action',choices=['query','planning-source','append','merge','join','sql','editable-source']);ib.add_argument('--input',required=True);ib.add_argument('--out',required=True)
    for command in ('bridge-planning-catalog','check-bridge-mappings','resolve-bridge-output','bind-bridge-outputs'):
        bm=sp.add_parser(command,help='Local Planning-source lineage construction, graph check, or current query-output identity resolution')
        bm.add_argument('--input',required=True);bm.add_argument('--out',required=True)
    api=sp.add_parser('api'); api.add_argument('action',choices=['export','create','create-blank','update']); api.add_argument('--config',required=True); api.add_argument('--payload'); api.add_argument('--run',required=True); api.add_argument('--label',required=True)
    w=sp.add_parser('provision'); w.add_argument('--config',required=True); w.add_argument('--model',required=True); w.add_argument('--spec',required=True); w.add_argument('--run',required=True)
    ms=sp.add_parser('prepare-maintenance');ms.add_argument('--baseline',required=True);ms.add_argument('--requests',required=True);ms.add_argument('--out',required=True)
    ps=sp.add_parser('prepare-scope');ps.add_argument('--spec',required=True);ps.add_argument('--model');ps.add_argument('--out',required=True)
    cb=sp.add_parser('construct-native'); cb.add_argument('action',choices=['anchor','number-parameter','input','formula','cube-settings','rule','weighted-rule','powertable-source','powertable-rows','navigator','dimension-mapping','table-column','bridge-consumer','contribution','embedded-planning']); cb.add_argument('--input',required=True); cb.add_argument('--out',required=True)
    for command in ('check-formula-syntax','repair-formula-equality','planning-time-axis','planning-time-column'):
        ti=sp.add_parser(command,help='Local native equality/date-axis/as-of VisualColumn helper; no live writes')
        ti.add_argument('--input',required=True);ti.add_argument('--out',required=True)
        if command=='planning-time-column':ti.add_argument('--baseline',required=True)
    args=p.parse_args()
    if hasattr(args,'label') and not re.fullmatch(r'[a-zA-Z0-9_.-]+',args.label): raise ValueError('Unsafe operation label')
    # These helpers construct local candidates only; deployment remains explicit.
    if args.cmd in ('check-formula-syntax','repair-formula-equality'):
        from runtime.formula_syntax import equality_issues,repair_equality
        formula=load(args.input)['formula']
        result=repair_equality(formula) if args.cmd=='repair-formula-equality' else {'issues':equality_issues(formula),'runtimeValidation':'not run'}
        save(args.out,result)
        if args.cmd=='check-formula-syntax' and result['issues']:raise ValueError('Invalid native comparison equality; see result')
    elif args.cmd=='planning-time-axis':
        from runtime.time_authoring import apply_time_axis
        save(args.out,apply_time_axis(**load(args.input)))
    elif args.cmd=='planning-time-column':
        from runtime.time_authoring import add_time_column
        candidate,manifest=add_time_column(load(args.baseline),**load(args.input))
        out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
        save(out/'definition.json',candidate);save(out/'changes.json',manifest)
    elif args.cmd=='repair-powertable-config':
        from runtime.powertable_config import repair_definition
        candidate,manifest=repair_definition(load(args.baseline),**load(args.input))
        out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
        save(out/'definition.json',candidate);save(out/'changes.json',manifest)
        print(dumps(manifest))
    elif args.cmd=='usecase':
        from runtime import usecases
        if args.case and args.recipe:raise ValueError('Select --case or --recipe, not both')
        selected=load(args.recipe) if args.recipe else args.case
        if args.action=='list':print(dumps(usecases.catalog()))
        elif args.action=='show':
            case=usecases.recipe(selected)
            if args.out:save(args.out,case);print('Saved editable recipe: '+args.out)
            else:print(dumps(case))
        elif args.action=='model':
            if not args.config or not args.run:raise ValueError('usecase model requires --config and --run')
            result=usecases.current_model(load(args.config),args.run)
            print(dumps({'model':str(Path(args.run)/'current-model.json'),'fields':len(result['fields'])}))
        else:
            if not selected or not args.model or not args.run:raise ValueError('usecase build requires --case or --recipe, --model and --run')
            _,case,name=usecases.prepare(selected,load(args.model),args.run,args.name)
            print(dumps({'name':name,'expected':case['expected'],'status':'local base only; requested recipe extensions are not deployed','runtimeValidation':'not run'}))
    elif args.cmd=='plan-intent':
        from runtime.business_intent import plan_intent
        save(args.out,plan_intent(load(args.input)))
        print('Saved business decisions and execution routes; no live actions.')
    elif args.cmd=='discover':
        from runtime.discovery import discover,render
        result=discover(args.query,args.module)
        print(dumps(result) if args.json else render(result,compact=args.list or not(args.query or args.module)))
    elif args.cmd=='resolve-measure-binding':
        from runtime.measure_bindings import resolve_measure
        save(args.out,resolve_measure(**load(args.input)))
        print('Saved source-specific binding; no runtime validation.')
    elif args.cmd=='present-planning':
        from runtime.planning_presentation import apply_presentation
        save(args.out,apply_presentation(**load(args.input)))
        print('Saved presentation candidate; runtime not checked.')
    elif args.cmd=='check-application-defaults':
        from runtime.application_defaults import check_application_defaults
        save(args.out,check_application_defaults(load(args.input),load(args.home)))
    elif args.cmd=='check-application-presentation':
        from runtime.planning_presentation import check_application
        save(args.out,check_application(load(args.input)))
    elif args.cmd=='integrated-variance':
        from runtime.integrated_variance import apply_integrated_variance
        save(args.out,apply_integrated_variance(load(args.input)))
        print('Saved integrated-variance candidate; no live writes or runtime validation.')
    elif args.cmd=='planning-display-defaults':
        from runtime.display_defaults import planning_display_defaults
        save(args.out,planning_display_defaults(**load(args.input)))
        print('Saved numeric Auto/filter candidate; no live writes or runtime validation.')
    elif args.cmd=='planning-column-presentation':
        from runtime.column_presentation import expand_columns,apply_column_presentation
        save(args.out,(expand_columns if args.expansion_only else apply_column_presentation)(load(args.input)))
        print('Saved Planning column candidate; no runtime validation.')
    elif args.cmd in ('planning-totals','roll-forward-presentation'):
        from runtime.roll_forward import apply_totals_defaults,roll_forward_presentation
        fn=apply_totals_defaults if args.cmd=='planning-totals' else roll_forward_presentation
        save(args.out,fn(**load(args.input)))
        print('Saved local presentation candidate; no live writes or runtime validation.')
    elif args.cmd in ('fit-planning-header','planning-hierarchy-icons'):
        from runtime.header_sizing import fit_header,apply_hierarchy_icons
        fn=fit_header if args.cmd=='fit-planning-header' else apply_hierarchy_icons
        save(args.out,fn(**load(args.input)))
        print('Saved local presentation candidate; no live writes or runtime validation.')
    elif args.cmd=='format-matrix':
        from runtime.matrix_formatting import compile_formatting
        save(args.out,compile_formatting(**load(args.input)))
        print('Saved local formatting candidate and coverage; rendering not verified.')
    elif args.cmd in ('check-planning-properties','repair-planning-properties'):
        from runtime.planning_integrity import check_properties,repair_properties
        data=load(args.input);model=load(args.model) if args.model else None
        fn=repair_properties if args.cmd=='repair-planning-properties' else check_properties
        save(args.out,fn(data,model));print('Planning integrity result saved; no runtime validation.')
    elif args.cmd=='leaf-key-mapping':
        from runtime.dimension_mapping import leaf_key_mapping
        save(args.out,leaf_key_mapping(**load(args.input)))
        print('Saved local mapping; visible assignments unchanged; no stored-value migration.')
    elif args.cmd=='forecast-repair':
        from runtime.forecast_repair import repair_definition
        result,summary=repair_definition(load(args.baseline),**load(args.input))
        save(args.out,result);save(str(args.out)+'.changes.json',summary)
        print('Scoped Forecast update prepared; publish with plan.py api update')
    elif args.cmd=='build':
        from runtime.identity import Registry
        from runtime.planning_presentation import build_application
        result=build_application(load(args.model),load(args.spec),Registry(load(args.registry)) if args.registry else None)
        out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
        for k in ('raw','envelope','registry','identities','dashboardIdentities','presentationCheck','defaultsCheck','home','homeSpec','evidence','buildRequest','importContract'): save(out/(k+'.json'),result[k])
        save(out/'construction.json',result)
        save(out/'validation.json',{'invariants':validate_plan(result['raw']),'publicSchemas':schema_report(result['raw'])})
        print('Constructed draft in '+str(out.resolve())+'; target initialization and runtime acceptance remain required.')
    elif args.cmd=='check-import-contract':
        from runtime.authoring_flow import require_import_contract
        save(args.out,require_import_contract(load(args.spec),load(args.construction),unpack(load(args.candidate)) if args.candidate else None))
        print('Requested base contents retained; static check only.')
    elif args.cmd=='validate': save(args.out,{'invariants':validate_plan(load(args.raw)),'publicSchemas':schema_report(load(args.raw))}); print('Validation evidence written')
    elif args.cmd=='decode':
        env=load(args.envelope); out=Path(args.out); out.mkdir(parents=True,exist_ok=True); raw=unpack(env)
        save(out/'decoded.json',raw); save(out/'definition-envelope.json',env)
        for name,b in parts(env).items():
            target=out/'parts'/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(b)
        save(out/'hashes.json',{k:sha(b) for k,b in parts(env).items()}); print('Decoded '+str(len(raw))+' parts')
    elif args.cmd=='encode':
        from runtime.planning_integrity import check_definition
        raw=load(args.raw);check_definition(raw);save(args.out,pack(raw))
    elif args.cmd=='audit-layout':
        from runtime.layout import audit
        print(audit(load(args.response),gap=args.gap))
    elif args.cmd=='audit-definition':
        from runtime.definition_audit import audit_definition
        save(args.out,audit_definition(load(args.raw)));print('Saved definition audit; runtime behavior remains separate.')
    elif args.cmd=='reference':
        name=safe_path(args.name)
        references=(ROOT/'references').resolve(); path=(references/name).resolve()
        if not name.parts or any(part.startswith('.') for part in name.parts) or not path.is_relative_to(references):
            raise ValueError('Use bundled reference path')
        text=path.read_text(encoding='utf-8-sig'); lines=text.splitlines()
        if args.list: print('\n'.join(f'{i+1}: {s}' for i,s in enumerate(lines) if s.startswith('#')))
        elif args.heading:
            starts=[i for i,s in enumerate(lines) if s.lstrip('# ').casefold()==args.heading.casefold() and s.startswith('#')]
            if len(starts)!=1: raise ValueError('Heading missing or ambiguous; use --list')
            start=starts[0]; level=len(lines[start])-len(lines[start].lstrip('#')); end=len(lines)
            for i in range(start+1,len(lines)):
                if lines[i].startswith('#') and len(lines[i])-len(lines[i].lstrip('#'))<=level: end=i; break
            print('\n'.join(lines[start:end]))
        else: print(text)
    elif args.cmd in ('bridge-planning-catalog','check-bridge-mappings','resolve-bridge-output','bind-bridge-outputs'):
        from runtime import bridge_identity
        request=load(args.input)
        if args.cmd=='bridge-planning-catalog':result=bridge_identity.planning_catalog(**request)
        elif args.cmd=='resolve-bridge-output':result=bridge_identity.resolve_planning_output(**request)
        elif args.cmd=='bind-bridge-outputs':result=bridge_identity.rebind_planning_outputs(**request)
        else:result=bridge_identity.check_planning_graph(request)
        save(args.out,result);print('Prepared local InfoBridge identity result; no live writes or runtime validation.')
    elif args.cmd=='construct-bridge':
        from runtime import bridge,bridge_operations
        factories={'query':bridge_operations.construct_query,'planning-source':bridge.planning_source,'append':bridge_operations.append_queries,'merge':bridge_operations.merge_queries,'join':bridge_operations.join_queries,'sql':bridge_operations.sql_source,'editable-source':bridge_operations.editable_source}
        result=factories[args.action](**load(args.input))
        if isinstance(result,tuple):result={'source':result[0],'linkedQueries':result[1]}
        save(args.out,result);print('Constructed InfoBridge payload; import, output catalog and values require destination API readback.')
    elif args.cmd=='test':
        # Isolated test process uses only this extracted runtime and explicitly blocks network.
        env=dict(os.environ); env['FABRIC_SKILL_OFFLINE_TEST']='1'
        r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-v'],cwd=str(ROOT),env=env)
        if r.returncode: raise SystemExit(r.returncode)
    elif args.cmd=='inspect-reference-views':
        from runtime.reference_views import audit
        save(args.out,audit(**load(args.input)))
    elif args.cmd=='construct-native':
        from runtime import input_factories,rule_factories,powertable_factory,navigator_api,dimension_mapping,table_columns,connected_components,page_parameters,anchor_measures
        from runtime.cube_contract import multi_dimension_settings
        factories={'anchor':anchor_measures.apply_anchors,'number-parameter':page_parameters.number_parameter,'input':input_factories.input_create,'formula':input_factories.formula_create,'rule':rule_factories.new_rule,'weighted-rule':rule_factories.measure_weighted_rule,
          'powertable-source':powertable_factory.existing_source,'powertable-rows':powertable_factory.row_save,'navigator':navigator_api.state,
          'dimension-mapping':dimension_mapping.dimension_mapping,'table-column':table_columns.column_config,
          'bridge-consumer':connected_components.bridge_consumer,'contribution':connected_components.contribution,
          'embedded-planning':connected_components.embedded_planning,'cube-settings':multi_dimension_settings}
        save(args.out,factories[args.action](**load(args.input)));print('Constructed source-contract payload; destination compatibility/execution not yet verified.')
    elif args.cmd=='prepare-maintenance':
        from runtime.maintenance_shells import add_deferred_powertables
        envelope,manifest=add_deferred_powertables(load(args.baseline),load(args.requests));out=Path(args.out)
        save(out/'envelope.json',envelope);save(out/'decoded.json',unpack(envelope));save(out/'maintenance-manifest.json',manifest)
        print('Prepared native PowerTable sheets; connection and table binding deferred. Publish and verify the sheet catalog.')
    elif args.cmd=='prepare-scope':
        from runtime.scope import prepare_scope
        from runtime.workflow import SUPPORTED
        save(args.out,prepare_scope(load(args.spec),SUPPORTED,load(args.model) if args.model else None));print('Prepared retained scope and per-feature coverage.')
    elif args.cmd=='provision':
        from runtime.workflow import provision
        result=provision(load(args.config),load(args.model),load(args.spec),args.run)
        print(('Created/resumed Plan '+result['planId']+'; see acceptance.json for exact evidence stages.') if result.get('planId') else 'No independent supported sheet remains; see scope-coverage.json.')
    elif args.cmd=='api':
        from runtime.transport import Client,plan_operation
        c=load(args.config); payload=load(args.payload) if args.payload else None
        if args.action!='export':
            if args.action!='create-blank':
                if not payload: raise ValueError('Full reviewed payload required')
                validate_plan(unpack(payload))
            if c.get('authorizedMutation') is not True: raise ValueError('Set authorizedMutation only from current user-authorized scope')
            if args.action=='update' and not c.get('baselineSha256'): raise ValueError('Update requires expected fresh baseline envelope hash')
        client=Client(c['apiBase'],c['tokenEnvironment'],c.get('allowedHosts'),Path(args.run)/'api')
        result=plan_operation(client,c['workspaceId'],args.action,c.get('planId'),payload,c.get('name'),label=args.label,baseline_hash=c.get('baselineSha256'))
        if args.action=='export':
            result['baselineSha256']=definition_hash(result['body'])
        save(Path(args.run)/'result.json',result); print('Saved API result; inspect status; runtime behavior is not verified.')
if __name__=='__main__':
    try: main()
    except (ValueError,RuntimeError,KeyError) as e: print(type(e).__name__+': '+str(e),file=sys.stderr); raise SystemExit(2)
