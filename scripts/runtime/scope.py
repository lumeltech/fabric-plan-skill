"""Continue useful authorized work when an individual construction module is unavailable.

This is a local scope diagnostic, not permission to deploy a reduced application.
The provisioner requires complete scope or an explicitly composed documented route. Agents should try the bundled component adapters first. Every omitted
or substituted requirement is recorded; unsafe dependencies are never zeroed.
"""
import copy,re

TOP={'name','sheets','requiredCapabilities','home','dashboards','theme'}
SHEET={'name','sheetId','visualId','rows','columns','measures','pivots','activePivot','capabilities','pivot',
       'row_expand_state_config','filterContextSettings','superFilterAssignments','header','comments','hidden',
       'dimensionKeyGroups','dimensionKeyOverrides','dimensionIdMappings','dimensionSkipSupport','lookupContextAssignments','context','columnTimeLevels','conditionalFormatting'}
CONTROL=re.compile(r'lock|approval|permission|security|access.?policy',re.I)
VISIBILITY=re.compile(r'rls|ols|security|row.?access|data.?access|visibility.?policy',re.I)
MEASURE_COMMON={'key','kind','label','description','visible','aggregation','columnAggregation','inputKind','visual_column','anchor'}
MEASURE_KEYS={'Native':MEASURE_COMMON|{'source','role','sourceAggregation'},'Formula':MEASURE_COMMON|{'formula'},
              'Forecast':MEASURE_COMMON|{'actuals','start','end','openDefault','timezone','periodUtc','referenceTimezone','referenceForecast','distribute','allow_input'},
              'DataInput':MEASURE_COMMON|{'default_value','min_value','max_value','context_bound','distribute','allow_input','on_change'}}

def prepare_scope(spec, supported, model=None):
    if not isinstance(spec,dict) or not isinstance(spec.get('name'),str) or not spec['name'].strip():
        raise ValueError('A named application request is required')
    report=[]
    def record(path,status,reason,alternative=None):
        r={'path':path,'status':status,'reason':reason}
        if alternative:r['alternative']=alternative
        report.append(r)
    out={k:copy.deepcopy(v) for k,v in spec.items() if k in TOP};out['sheets']=[]
    requests=spec.get('requiredCapabilities',[])
    if not isinstance(requests,list) or any(not isinstance(x,str) for x in requests): raise ValueError('Capability inventory must be a string list')
    unsupported=set(requests)-set(supported)
    unknown_top=set(spec)-TOP
    global_control=any(CONTROL.search(k) for k in unsupported|unknown_top)
    global_visibility=any(VISIBILITY.search(k) for k in unsupported|unknown_top)
    for cap in requests:
        record('capability:'+cap,'omitted' if cap in unsupported else 'available',
               'No composed provisioner phase; try bundled component adapter separately' if cap in unsupported else 'Implemented provisioner phase')
    for k in set(spec)-TOP:
        record(k,'omitted','No composed provisioner phase for this module')
    for index,source in enumerate(spec.get('sheets',[])):
        path='sheets['+str(index)+']'
        if not isinstance(source,dict):record(path,'omitted','Malformed sheet request');continue
        if global_visibility:
            record(path,'omitted','Unimplemented shared data-access control; read-only presentation would still disclose data');continue
        if source.get('sheetType','PLANNING')!='PLANNING':record(path,'omitted','Selected non-Planning sheet needs its component adapter');continue
        sheet={k:copy.deepcopy(v) for k,v in source.items() if k in SHEET}
        extra=set(source)-SHEET-{'sheetType'}
        if any(VISIBILITY.search(k) for k in extra):
            record(path,'omitted','Unimplemented sheet data-access control');continue
        uncertain_control=global_control or 'data_input_rules' in extra or any(CONTROL.search(k) for k in extra)
        for k in extra:
            record(path+'.'+k,'alternative' if k=='measureModelConfig' else 'omitted','No composed writer for this module',
                'Keep supported calculations in a flat measure list' if k=='measureModelConfig' else None)
        kept=[];removed=set()
        for m in source.get('measures',[]):
            key=m.get('key') if isinstance(m,dict) else None
            if not isinstance(m,dict) or m.get('kind') not in ('Native','Formula','DataInput','Forecast') or m.get('inputKind','Number')!='Number':
                removed.add(key);record(path+'.measure:'+str(key),'omitted','Selected input/calculation factory unavailable to composed provisioner');continue
            if m['kind']=='Forecast' and any(not isinstance(m.get(k),str) or not m[k].strip() for k in ('actuals','start','end')):
                removed.add(key);record(path+'.measure:'+str(key),'omitted','Forecast requires resolved actuals and explicit start/end; continue independent measures');continue
            extra_measure=set(m)-MEASURE_KEYS[m['kind']]
            for prop in extra_measure:
                record(path+'.measure:'+str(key)+'.'+prop,'omitted','No consumed property writer for this measure option')
            if any(VISIBILITY.search(k) for k in extra_measure):
                removed.add(key);record(path+'.measure:'+str(key),'omitted','Unimplemented measure data-access control');continue
            measure_control=any(CONTROL.search(k) or k=='data_input_rules' for k in extra_measure)
            if (uncertain_control or measure_control) and m['kind'] in ('DataInput','Forecast'):
                removed.add(key);record(path+'.measure:'+str(key),'omitted','Required control could not be constructed; retain available read-only measures');continue
            kept.append({k:copy.deepcopy(v) for k,v in m.items() if k in MEASURE_KEYS[m['kind']]})
        def refs(m):
            result=set()
            if m.get('kind')=='Forecast': result.add(m['actuals'])
            def walk(x):
                if isinstance(x,dict):
                    if set(x)=={'Measure'}:result.add(x['Measure'])
                    for y in x.values():walk(y)
                elif isinstance(x,list):
                    for y in x:walk(y)
                elif isinstance(x,str):result.update(re.findall(r'\$\{([\w.-]+)\}',x))
            walk(m);return result
        changed=True
        while changed:
            changed=False;alive={m['key'] for m in kept}
            for m in list(kept):
                missing=refs(m)-alive
                if missing:
                    kept.remove(m);removed.add(m['key']);changed=True
                    record(path+'.measure:'+m['key'],'omitted','Dependent source unavailable: '+', '.join(sorted(str(x) for x in missing)))
        sheet['measures']=kept
        if not kept:record(path,'omitted','No supported independent measures remain');continue
        if removed and any(k in sheet for k in ('pivots','pivot')):
            for k in ('pivots','pivot','activePivot'):sheet.pop(k,None)
            record(path+'.pivots','alternative','Requested measure selection changed','Use the default view of retained measures')
        # A failed sheet is isolated; do not prevent independent sheets being built.
        if model is not None:
            from .construct import planning
            from .identity import Registry
            try:planning(model,sheet,Registry())
            except (ValueError,KeyError,TypeError) as e:
                record(path,'omitted','Sheet construction failed: '+str(e));continue
        out['sheets'].append(sheet);record(path,'retained','Supported independent Planning sheet')
    if out.get('dashboards') and model is not None:
        from .construct import build
        retained=[]
        for i,page in enumerate(out['dashboards']):
            from .intelligence import slicer,card,chart
            from .identity import Registry
            page=copy.deepcopy(page)
            for group,constructor in [('slicers',lambda x:slicer(model,x)),('cards',lambda x:card(model,x,Registry())),('charts',lambda x:chart(model,x,Registry()))]:
                if group=='charts' and group not in page: continue
                good=[]
                for j,component in enumerate(page.get(group,[])):
                    try: constructor(component)
                    except (ValueError,KeyError,TypeError) as e:
                        record('dashboards['+str(i)+'].'+group+'['+str(j)+']','omitted','Visual construction failed: '+str(e));continue
                    good.append(component)
                page[group]=good
            try: build(model,{**out,'dashboards':retained+[page]})
            except (ValueError,KeyError,TypeError) as e:
                record('dashboards['+str(i)+']','omitted','Dashboard construction failed: '+str(e));continue
            retained.append(page);record('dashboards['+str(i)+']','retained','Native workspace with '+str(len(page['slicers']))+' slicers and '+str(len(page['cards']))+' cards plus text/embed; runtime verification separate')
        out['dashboards']=retained
    if out.get('home'):
        h=out['home'];blocks=[];old_keys=set();bad=False
        for b in h.get('blocks',[]):
            if b.get('type') in ('text','preview-cards'):blocks.append(b)
            else:
                old_keys.add(b.get('key'))
                # The purpose and wording survive without fabricating an image upload.
                if b.get('key') and (b.get('title') or b.get('description')):
                    blocks.append({'key':b['key'],'type':'text','title':b.get('title',''),'description':b.get('description','')})
                    record('home.'+b['key'],'alternative','Advanced node/asset omitted','Native text with the requested title and description')
                else:record('home.block','omitted','Unsupported Home block has no usable text')
        h['blocks']=blocks;keys={b['key'] for b in blocks};rows=[]
        for r in h.get('rows',[]):
            retained=[k for k in r.get('blocks',[]) if k in keys]
            if retained:
                nr=copy.deepcopy(r);nr['blocks']=retained
                if len(retained)!=len(r.get('blocks',[])):nr.pop('widths',None)
                rows.append(nr)
        h['rows']=rows
        if not blocks:out.pop('home');record('home','omitted','No supported Home content remains')
    # Capabilities describe the retained draft. Original requested coverage stays in report.
    caps=set(requests)&set(supported)
    for s in out['sheets']:
        for m in s['measures']:caps.add({'Native':'planning.native-measure','DataInput':'planning.numeric','Formula':'planning.formula','Forecast':'planning.forecast'}[m['kind']])
    if out.get('home'):caps.add('home.text')
    # Availability of a constructor is not evidence that requested content exists.
    configured={'planning.anchor-measure':any('anchor' in m for s in out['sheets'] for m in s['measures']),
        'planning.conditional-formatting':any(s.get('conditionalFormatting') for s in out['sheets']),
        'planning.filter-context':any(s.get('context') or any(r.get('isContextDimension') for r in s.get('superFilterAssignments',[])) for s in out['sheets']),
        'intelligence.slicers':any(d.get('slicers') for d in out.get('dashboards',[])),
        'intelligence.cards':any(d.get('cards') for d in out.get('dashboards',[])),
        'intelligence.charts':any(d.get('charts') for d in out.get('dashboards',[])),
        'intelligence.text':bool(out.get('dashboards')),'intelligence.embeds':any('table' not in d for d in out.get('dashboards',[])),
        'intelligence.matrix':any('table' in d for d in out.get('dashboards',[])),'plan.theme':out.get('theme') is not None}
    for cap,present in configured.items():
        if cap in requests and not present:
            record('capability:'+cap,'omitted','Constructor available but no matching authored content remains; supply a resolved configuration before claiming this requirement complete')
    out['requiredCapabilities']=sorted(caps)
    return {'spec':out,'coverage':report,'policy':'continue-independent-work',
            'completeOriginalScope':not any(r['status'] in ('omitted','alternative') for r in report)}
