"""Resumable API-only provisioning with explicit per-module fallbacks.

Unsupported requested features are recorded and isolated before compiling the
supported subset. They do not prevent independent application work.
"""
from pathlib import Path
from .codec import load,save,sha,dumps,pack
from .transport import Client,plan_operation
from .validate import validate_plan,schema_report
from .surfaces import home_item,home_layout
from .home_fit import readable_home_layout

SUPPORTED={'planning.anchor-measure','planning.conditional-formatting','planning.numeric','planning.formula','planning.native-measure','planning.forecast',
           'planning.pivots','planning.conditional-edit-policy','planning.dimension-id-mapping','planning.filter-context',
           'intelligence.slicers','intelligence.cards','intelligence.charts','intelligence.text','intelligence.embeds','home.text','home.cards','home.visibility'}

def preflight(spec):
    requested=spec.get('requiredCapabilities')
    if not isinstance(requested,list) or not requested: raise ValueError('Agent must enumerate requiredCapabilities from the complete business request')
    unknown=set(requested)-SUPPORTED
    if unknown: raise ValueError('API_CONSTRUCTION_GAP: '+', '.join(sorted(unknown)))
    allowed={'name','sheets','requiredCapabilities','home','dashboards'}
    if set(spec)-allowed: raise ValueError('Unconsumed spec modules: '+', '.join(sorted(set(spec)-allowed)))
    for s in spec['sheets']:
        known={'name','sheetId','visualId','rows','columns','measures','pivots','activePivot','capabilities','pivot',
               'row_expand_state_config','filterContextSettings','superFilterAssignments','header','comments','hidden',
               'dimensionKeyGroups','dimensionKeyOverrides','dimensionIdMappings','dimensionSkipSupport','lookupContextAssignments','context','columnTimeLevels','conditionalFormatting'}
        if set(s)-known: raise ValueError('Unconsumed/unsupported sheet modules: '+', '.join(sorted(set(s)-known)))
        for m in s['measures']:
            if m['kind'] not in ('Native','Formula','DataInput','Forecast') or m.get('inputKind','Number')!='Number':
                raise ValueError('API_CONSTRUCTION_GAP: complete selected input factory')
        if any(k in s for k in ('data_input_rules','measureModelConfig','advancedLookup','forecast')):
            raise ValueError('API_CONSTRUCTION_GAP: selected feature needs complete API factory')
    if spec.get('home'):
        h=spec['home'];order=h.get('order',1)
        if isinstance(order,bool) or not isinstance(order,int) or order<0: raise ValueError('Invalid Home priority')
        if not isinstance(h.get('show',True),bool): raise ValueError('Home visibility must be Boolean')
        if not isinstance(h.get('roleId','__everyone__'),str) or not h.get('roleId','__everyone__'): raise ValueError('Home role identity required')
        if any(b['type'] not in ('text','preview-cards') for b in spec['home']['blocks']):
            raise ValueError('API_CONSTRUCTION_GAP: Home uploaded assets/advanced nodes')
    return {'status':'passed-construction-subset','runtimeAcceptance':'separate'}

def compile_home(spec):
    items=[]; symbols={}
    for block in spec['blocks']:
        key=block['key']
        if key in symbols: raise ValueError('Duplicate Home block key')
        item=home_item(block['type'],block.get('title',''),block.get('description',''),columns=block.get('columns',4))
        items.append(item);symbols[key]=item['id']
    rows=[{'itemIds':[symbols[k] for k in r['blocks']],**{k:v for k,v in r.items() if k in ('height','widths')}} for r in spec['rows']]
    return readable_home_layout(items,rows,content_width_px=spec.get('contentWidthPx'))

def home_delivery(authored):
    return {'visibility':'public-create', 'show':authored['raw']['planProperties.json']['properties']['homeLayout']['show'],
            'roleId':authored['homeSpec']['roleId'], 'content':'constructed-locally-not-published',
            'gap':'Role-specific Home content and priority cannot be published through the documented public Plan transport.'}

def provision(config,model,spec,run):
    from .scope import prepare_scope
    run=Path(run);run.mkdir(parents=True,exist_ok=True)
    scope=prepare_scope(spec,SUPPORTED,model)
    save(run/'scope-coverage.json',scope)
    if not scope['completeOriginalScope']:
        # Scope analysis is a local diagnostic, never permission to deploy a
        # reduced reference-only substitute for the requested application.
        return {'planId':None,'completion':'Requested flow needs documented component phases; no reduced application deployed',
                'coverage':scope['coverage'],'originalScopeComplete':False,'mutation':'none'}
    spec=scope['spec']
    if not spec['sheets']:
        # No fake financial sheet is created from guessed fields or zero values.
        return {'planId':None,'completion':'No independent supported data sheet remains',
                'coverage':scope['coverage'],'originalScopeComplete':False,'mutation':'none'}
    from .planning_presentation import application_defaults,check_application,build_application
    spec=application_defaults(model,spec)
    preflight(spec)
    if config['name']!=spec['name']: raise ValueError('Creation name and authored Plan name differ')
    if config.get('authorizedMutation') is not True: raise ValueError('Current user authorization required')
    signature=sha(dumps({'model':model,'spec':spec,'target':{k:config[k] for k in ('apiBase','workspaceId','name')}}))
    cp=run/'construction.json'
    if cp.exists():
        authored=load(cp)
        if authored['signature']!=signature: raise ValueError('Resume input drift; reconcile explicitly without recreating the Plan')
    else:
        authored=build_application(model,spec);validate_plan(authored['raw']);check_application(authored['raw'])
        authored.update(signature=signature,publicSchemas=schema_report(authored['raw']))
        save(cp,authored)
    from .application_defaults import check_application_defaults,require_delivery_phases
    # Resumed/cached constructions must satisfy the same mandatory baseline.
    check_application_defaults(authored['raw'],authored.get('home'))
    from .authoring_flow import require_authored_flow
    require_authored_flow(authored,spec)
    client=Client(config['apiBase'],config['tokenEnvironment'],config.get('allowedHosts'),run/'public-api')
    receipt=run/'created-plan.json'
    if (run/'public-api/create-blank.intent.json').exists() or (run/'initial-update.json').exists():
        raise ValueError('This run began with a blank-create deployment. Resume it with its original package.')
    if receipt.exists():
        created=load(receipt)
    else:
        created=plan_operation(client,config['workspaceId'],'create',name=config['name'],
                               definition=pack(authored['raw']),label='create-with-definition')
        save(receipt,created)
    plan=created.get('body',{}).get('id')
    if not plan: raise ValueError('Create receipt has no Plan ID. Reconcile the submitted operation before retrying.')
    from .public_alignment import check_placements
    dashboards=[check_placements(authored['raw'], d) for d in authored.get('dashboardIdentities', [])]
    home=home_delivery(authored)
    phase_errors=[{'phase':'home-role-content','status':'unsupported','error':home['gap']}]
    defaults=require_delivery_phases(authored,home_visible=home['show'],dashboard_geometry=[d['sheetGuid'] for d in dashboards],
        dashboard_visibility=[s['recordGuid'] for s in authored['raw']['definition.json']['sheets'] if s['sheetType']=='REPORTING' and not s['isHidden']])
    evidence={'planId':plan,'construction':'passed','mandatoryDefaults':defaults,'import':created.get('status'),'visibilitySource':'public-create',
        'home':home,'dashboards':dashboards,'calculation':'not-tested','inputEdits':'not-tested','connectedPropagation':'not-tested','rendering':'not-tested',
        'completion':'Supported application saved; evaluate retained scope and runtime checks separately',
        'coverage':scope['coverage'],'originalScopeComplete':scope['completeOriginalScope'] and not phase_errors,'phaseErrors':phase_errors}
    save(run/'acceptance.json',evidence);return evidence
