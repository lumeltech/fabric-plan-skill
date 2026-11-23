"""Portable business recipes: discover, compile and create/resume without chat state.

Recipes compile locally. Model intake uses the documented semantic model API.
"""
import copy,re,time,uuid
from pathlib import Path
from .codec import load,save,dumps,sha,parts,pack
from .planning_presentation import build_application
from .forecast_review import apply_negative_variance
from .transport import Client

ROOT=Path(__file__).resolve().parents[1]
CASES=ROOT/'examples/five-usecases'

def catalog():return load(CASES/'index.json')

def recipe(key):
    if isinstance(key,dict):
        required={'id','title','prompt','spec','post','expected'}
        if not required<=key.keys():raise ValueError('Adapted recipe needs '+', '.join(sorted(required)))
        return copy.deepcopy(key)
    if key not in {x['id'] for x in catalog()}:raise ValueError('Unknown usecase; use usecase list')
    return load(CASES/(key+'.json'))

def current_model(config,run):
    """Read authorized model metadata. No data queries. TMDL selected schema branch."""
    c=Client(config['apiBase'],config['tokenEnvironment'],config.get('allowedHosts'),Path(run)/'model-api')
    ref=copy.deepcopy(config['modelReference']);w=ref['semanticModelWorkspaceId'];m=ref['semanticModelId']
    item=c.request('GET',f'/workspaces/{w}/semanticModels/{m}')['body']
    label='model-definition-'+uuid.uuid4().hex
    r=c.request('POST',f'/workspaces/{w}/semanticModels/{m}/getDefinition?format=TMDL',{},label=label)
    definition=c.finish(r,label)['body'];save(Path(run)/'model-definition.json',definition)
    decoded=parts(definition);fields=[];q=r"(?:'((?:[^']|'')+)'|([^\s=]+))"
    types={'int64':'Int64','double':'Double','decimal':'Decimal','string':'String','dateTime':'DateTime','boolean':'Boolean'}
    for name,b in decoded.items():
        if not name.startswith('definition/tables/') or not name.endswith('.tmdl'):continue
        s=b.decode('utf-8-sig');t=re.search('^table '+q,s,re.M)
        if not t:raise ValueError('Unrecognized TMDL table declaration: '+name)
        tn=(t[1] or t[2]).replace("''", "'");matches=list(re.finditer(r'^\t(measure|column) '+q,s,re.M))
        for i,x in enumerate(matches):
            kind=x[1];cn=(x[2] or x[3]).replace("''", "'");body=s[x.end():matches[i+1].start() if i+1<len(matches) else len(s)]
            dt=re.search(r'^\t\tdataType: (\w+)',body,re.M);fmt=re.search(r'^\t\tformatString: (.+)',body,re.M)
            # These five recipes use numeric measures; TMDL commonly omits their
            # return type. Non-numeric measure authoring needs an explicit catalog.
            dtype=types.get(dt[1]) if dt else 'Double' if kind=='measure' else None
            if not dtype:continue
            fields.append({'id':tn+'['+cn+']','tableName':tn,'columnName':cn,'columnType':'Measure' if kind=='measure' else 'Column','dataType':dtype,'formatString':fmt[1] if fmt else ''})
    if not fields:raise ValueError('Selected TMDL branch unavailable; supply a current model catalog per runtime-guide.md')
    ref['semanticModelName']=item.get('displayName',ref.get('semanticModelName'))
    model={'reference':ref,'fields':fields};save(Path(run)/'current-model.json',model);return model

def field_requirements(case):
    keys=set()
    for s in case['spec']['sheets']:
        keys.update(s['rows']+s['columns']);keys.update(m['source'] for m in s['measures'] if m['kind']=='Native')
        for g in s.get('dimensionKeyGroups',[]):keys.update([g['leaf'],g['key'],*g['ancestors']])
    for d in case['spec']['dashboards']:
        keys.update(s['field'] for s in d['slicers'])
        for chart in d['charts']:keys.update([chart['field'],chart['category']])
    return sorted(keys)

def recipe_contract(case,model):
    """Offline completeness of symbolic dependencies, scope and chart bindings."""
    spec=case['spec'];post=case['post'];sheets={s['name']:s for s in spec['sheets']}
    if len(sheets)!=len(spec['sheets']):raise ValueError('Duplicate sheet name')
    missing=set(field_requirements(case))-{f['id'] for f in model['fields']}
    if missing:raise ValueError('Missing current model fields: '+', '.join(sorted(missing)))
    if set(post)-{'steps','quarterly','comparisons','negative','percent','periodFilters'}:raise ValueError('Unconsumed recipe extension')
    labels={n:{m['label']:m['kind'] for m in s['measures']} for n,s in sheets.items()}
    for n,s in sheets.items():
        if len(labels[n])!=len(s['measures']):raise ValueError('Ambiguous measure labels: '+n)
    def link(source,target,source_measure,label):
        src=sheets[source];dst=sheets[target]
        from .storage_context import require_same
        require_same(src,dst)
        if not set(dst['rows'])<=set(src['rows']) or dst['columns']!=src['columns'][:len(dst['columns'])]:raise ValueError('Incompatible From Sheets grain')
        if labels[source].get(source_measure) not in ('DataInput','Forecast','Formula'):raise ValueError('From Sheets needs a produced measure; native companions are not outputs')
        if label in labels[target]:raise ValueError('Destination caption collision: '+label)
        labels[target][label]='FromSheets'
    q=post.get('quarterly')
    if q:
        link(q['sourceSheet'],q['targetSheet'],q['sourceForecast'],q['forecastLabel'])
        if q['targetActuals'] not in labels[q['targetSheet']]:raise ValueError('Unresolved quarterly actuals')
        labels[q['targetSheet']][q['varianceLabel']]='Formula';labels[q['targetSheet']][q['commentaryLabel']]='DataInput'
    for step in post.get('steps',[]):
        n=step['sheet']
        for item in step.get('links',[]):link(item['sourceSheet'],n,item['sourceMeasure'],item['label'])
        for f in step.get('formulas',[]):
            if set(re.findall(r'\$\{([^}]+)\}',f['expression']))!=set(f['symbols']):raise ValueError('Formula symbols incomplete')
            if not set(f['symbols'].values())<=set(labels[n]):raise ValueError('Formula dependency order is incomplete')
            if f['label'] in labels[n]:raise ValueError('Formula caption collision')
            labels[n][f['label']]='Formula'
        if step.get('commentary'):labels[n][step['commentary']]='DataInput'
        if not set(step.get('negative',[]))<=set(labels[n]):raise ValueError('Unresolved conditional-format target')
    comparisons={c['owner']:c for c in post['comparisons']}
    if set(comparisons)!=set(sheets):raise ValueError('Every recipe owner requires its explicit comparison contract')
    for name,c in comparisons.items():
        if not {c['left'],c['right']}<=set(labels[name]):raise ValueError('Unresolved chart comparison')
    for kind in ('negative','percent'):
        for name,ls in post.get(kind,{}).items():
            if not set(ls)<=set(labels[name]):raise ValueError('Unresolved '+kind+' formatting')
    if set(post['periodFilters'])!=set(sheets):raise ValueError('Missing planning period selection')
    actual={'planningSheets':len(sheets),'dashboards':len(spec['dashboards']),'comparisonCharts':sum(len(d['charts']) for d in spec['dashboards']),'home':spec['home']['show']}
    if actual!=case['expected']:raise ValueError('Recipe shape differs from expected output')
    return {'shape':actual,'finalMeasures':labels,'dependencies':'resolved symbolically','runtimeValidation':'not run'}

def prepare(key,model,run,name=None):
    run=Path(run);case=recipe(key);p=run/'recipe.json'
    contract=recipe_contract(case,model)
    from .authoring_flow import require_authored_flow
    if p.exists():
        before=load(p)
        if before['case']!=case or before['modelHash']!=sha(dumps(model)) or (name and before['name']!=name):raise ValueError('Resume recipe/model/name drift; do not recreate an existing application')
        cached=load(run/'construction.json')
        require_authored_flow(cached,case['spec'])
        return cached,case,before['name']
    missing=set(field_requirements(case))-{f['id'] for f in model['fields']}
    if missing:raise ValueError('Resolve current model fields; missing: '+', '.join(sorted(missing)))
    name=name or case['title']+' '+str(int(time.time()));spec=copy.deepcopy(case['spec']);spec['name']=name
    b=build_application(model,spec)
    from .filters import selection,select_axis_filter
    from .matrix_formatting import compile_formatting
    for s,ident in zip(spec['sheets'],b['identities']):
        path=f"sheets/{ident['sheetId']}/visuals/{ident['visualId']}/properties.json";props=b['raw'][path]['properties']
        period=case['post']['periodFilters'][s['name']]
        select_axis_filter(props,period['field'],selection(model,period['field'],values=period['values']))
        ids={m['label']:m['id'] for m in props['visualState']['manage_measures']}
        for label in case['post'].get('negative',{}).get(s['name'],[]):props=apply_negative_variance(props,ids[label],label)
        ops=[{'key':'pct-'+ids[label],'scope':'measure','id':ids[label],'format':{'percentage':True,'decimals':1}} for label in case['post'].get('percent',{}).get(s['name'],[])]
        if ops:props['visualState']=compile_formatting(props['visualState'],{'operations':ops})['state']
        b['raw'][path]['properties']=props
    b['envelope']=pack(b['raw']);save(run/'construction.json',b);save(run/'spec.json',spec)
    require_authored_flow(b,spec)
    save(run/'recipe-contract.json',contract)
    save(p,{'case':case,'name':name,'modelHash':sha(dumps(model))})
    save(run/'phase-ledger.json',{'base':'constructed','modelFields':'resolved','expected':case['expected'],
      'pending':['create/import','requested recipe extensions','role-specific Home publication'],
      'runtimeValidation':'not run','completeness':'Local base only; author outstanding recipe extensions in the public definition before using public deployment'})
    return b,case,name
