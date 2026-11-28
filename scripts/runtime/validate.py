"""Offline pinned-schema validator and Plan-specific structural acceptance.
Implements only keywords present in the bundled schema closure. Unknown validation
keywords fail closed; annotation/default fields do not construct application state.
"""
import re, uuid, urllib.parse, decimal, copy, json
from pathlib import Path
from .codec import load,sha,pointer_get,dumps
from .identity import native_id
from .construct import acyclic
from .paths import ASSETS
class SchemaGap(ValueError): pass
class Invalid(ValueError): pass
ANNOTATIONS={'$schema','$id','$comment','title','description','default','examples','readOnly','writeOnly','deprecated','definitions','$defs'}
KEYS={'$ref','type','required','properties','additionalProperties','patternProperties','propertyNames','items','additionalItems','minItems','maxItems','uniqueItems','minProperties','maxProperties','minLength','maxLength','pattern','format','minimum','maximum','exclusiveMinimum','exclusiveMaximum','multipleOf','enum','const','anyOf','oneOf','allOf','not','if','then','else','dependencies','contains'}|ANNOTATIONS
class Schemas:
    def __init__(self,root=None):
        root=Path(root or ASSETS/'schemas'); self.docs={}; self.unavailable=[]
        for s in load(root/'manifest.json')['schemas']:
            if s['status']!='downloaded': self.unavailable.append(s); continue
            b=(root/s['file']).read_bytes()
            if sha(b)!=s['sha256']: raise ValueError('Schema checksum mismatch')
            self.docs[s['url']]=load(root/s['file'])
    def check(self,value,url):
        if url not in self.docs: raise SchemaGap('Schema not bundled: '+url)
        self._check(value,self.docs[url],url,'$'); return True
    def _check(self,v,s,url,path):
        if s is True: return
        if s is False: raise Invalid(path+': rejected')
        if not isinstance(s,dict): raise SchemaGap('Invalid schema node')
        unknown=set(s)-KEYS
        if unknown: raise SchemaGap('Unsupported schema keywords: '+','.join(sorted(unknown)))
        def fail(msg): raise Invalid(path+': '+msg)
        if '$ref' in s:
            u,frag=urllib.parse.urldefrag(urllib.parse.urljoin(url,s['$ref']))
            if u not in self.docs: raise SchemaGap('Missing transitive schema: '+u)
            return self._check(v,pointer_get(self.docs[u],urllib.parse.unquote(frag)),u,path)
        for key in ('anyOf','oneOf'):
            if key in s:
                matches=0
                for branch in s[key]:
                    try: self._check(v,branch,url,path); matches+=1
                    except Invalid: pass
                if (key=='anyOf' and not matches) or (key=='oneOf' and matches!=1): fail(key+' branches matched '+str(matches))
        for branch in s.get('allOf',[]): self._check(v,branch,url,path)
        if 'not' in s:
            try: self._check(v,s['not'],url,path)
            except Invalid: pass
            else: fail('not')
        if 'if' in s:
            try: self._check(v,s['if'],url,path); branch='then'
            except Invalid: branch='else'
            if branch in s: self._check(v,s[branch],url,path)
        def eq(a,b):
            if isinstance(a,bool) or isinstance(b,bool): return type(a) is type(b) and a==b
            if isinstance(a,dict) and isinstance(b,dict): return a.keys()==b.keys() and all(eq(a[k],b[k]) for k in a)
            if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(eq(x,y) for x,y in zip(a,b))
            return a==b
        if 'const' in s and not eq(v,s['const']): fail('const mismatch')
        if 'enum' in s and not any(eq(v,x) for x in s['enum']): fail('enum mismatch')
        typ=s.get('type'); types=[typ] if isinstance(typ,str) else typ or []
        num=isinstance(v,(int,float,decimal.Decimal)) and not isinstance(v,bool)
        if types:
            ok={'null':v is None,'boolean':isinstance(v,bool),'object':isinstance(v,dict),'array':isinstance(v,list),'string':isinstance(v,str),'number':num,'integer':num and v==int(v)}
            if any(t not in ok for t in types): raise SchemaGap('Unsupported type')
            if not any(ok[t] for t in types): fail('type mismatch '+str(types))
        if num:
            for key,cmp in [('minimum',lambda a,b:a>=b),('maximum',lambda a,b:a<=b),('exclusiveMinimum',lambda a,b:a>b),('exclusiveMaximum',lambda a,b:a<b)]:
                if key in s and not cmp(v,s[key]): fail(key)
            if 'multipleOf' in s and decimal.Decimal(str(v))%decimal.Decimal(str(s['multipleOf']))!=0: fail('multipleOf')
        if isinstance(v,str):
            if len(v)<s.get('minLength',0) or len(v)>s.get('maxLength',float('inf')): fail('string length')
            if 'pattern' in s and not re.search(s['pattern'],v): fail('pattern')
            fmt=s.get('format')
            if fmt=='uuid':
                try: uuid.UUID(v)
                except ValueError: fail('UUID')
            elif fmt in ('uri','uri-reference'):
                if fmt=='uri' and not urllib.parse.urlsplit(v).scheme: fail('URI')
            elif fmt in ('date','date-time'):
                import datetime
                try: datetime.datetime.fromisoformat(v.replace('Z','+00:00')) if fmt=='date-time' else datetime.date.fromisoformat(v)
                except ValueError: fail('date format')
            elif fmt not in (None,): raise SchemaGap('Unimplemented format '+fmt)
        if isinstance(v,list):
            if len(v)<s.get('minItems',0) or len(v)>s.get('maxItems',float('inf')): fail('array length')
            if s.get('uniqueItems') and any(eq(v[i],v[j]) for i in range(len(v)) for j in range(i+1,len(v))): fail('duplicate array item')
            items=s.get('items',{})
            for i,x in enumerate(v): self._check(x,items[i] if isinstance(items,list) and i<len(items) else s.get('additionalItems',True) if isinstance(items,list) else items,url,path+'/'+str(i))
            if 'contains' in s:
                found=False
                for x in v:
                    try: self._check(x,s['contains'],url,path); found=True
                    except Invalid: pass
                if not found: fail('contains')
        if isinstance(v,dict):
            missing=set(s.get('required',[]))-v.keys()
            if missing: fail('missing '+','.join(sorted(missing)))
            if len(v)<s.get('minProperties',0) or len(v)>s.get('maxProperties',float('inf')): fail('property count')
            for k,x in v.items():
                if 'propertyNames' in s: self._check(k,s['propertyNames'],url,path)
                rules=[]
                if k in s.get('properties',{}): rules.append(s['properties'][k])
                for pattern,rule in s.get('patternProperties',{}).items():
                    if re.search(pattern,k): rules.append(rule)
                if not rules: rules=[s.get('additionalProperties',True)]
                for rule in rules: self._check(x,rule,url,path+'/'+k)
            for k,dep in s.get('dependencies',{}).items():
                if k in v:
                    if isinstance(dep,list):
                        if set(dep)-v.keys(): fail('dependent keys')
                    else: self._check(v,dep,url,path)

def check_powertable_parts(raw,prefix):
    """Require the PowerTable companions to describe one coherent source owner."""
    required=('source.json','columnConfigs.json','sourceSettings.json','properties.json')
    for leaf in required:
        if prefix+leaf not in raw: raise ValueError('Missing PowerTable companion '+leaf)
    source=raw[prefix+'source.json'].get('source')
    if not isinstance(source,dict) or not isinstance(source.get('recordGuid'),str) or not source['recordGuid']:
        raise ValueError('PowerTable source record identity required')
    source_id=source['recordGuid']
    columns=raw[prefix+'columnConfigs.json'].get('columnConfigs')
    if not isinstance(columns,list) or not columns: raise ValueError('PowerTable requires configured columns')
    names=[];record_guids=[]
    for column in columns:
        if not isinstance(column,dict) or not {'columnGuid','columnName','columnType','columnMeta','displayName'}<=column.keys():
            raise ValueError('Incomplete PowerTable column configuration')
        names.append(column['columnName']);record_guids.append(column.get('recordGuid'))
    if any(not isinstance(name,str) or not name for name in names) or len(names)!=len(set(names)):
        raise ValueError('PowerTable physical column names must be unique')
    concrete_guids=[guid for guid in record_guids if guid is not None]
    if any(not isinstance(guid,str) or not guid for guid in concrete_guids) or len(concrete_guids)!=len(set(concrete_guids)):
        raise ValueError('PowerTable column record identities must be unique')
    settings=raw[prefix+'sourceSettings.json'].get('sourceSettings')
    if not isinstance(settings,list) or not settings: raise ValueError('PowerTable source settings required')
    setting_names=[]
    for setting in settings:
        if not isinstance(setting,dict) or setting.get('sourceId')!=source_id:
            raise ValueError('PowerTable setting belongs to a different source')
        if not isinstance(setting.get('name'),str) or not isinstance(setting.get('settings'),dict):
            raise ValueError('Incomplete PowerTable source setting')
        if type(setting['settings'].get('enabled')) is not bool:
            raise ValueError('PowerTable source setting requires Boolean enabled')
        if setting['name'] in ('ROW_ADD','ROW_UPDATE','ROW_DELETE'):
            filters=setting.get('filters',[])
            if not isinstance(filters,list):
                raise ValueError('PowerTable row-access filters must be a list')
            if setting['settings']['enabled'] and not filters:
                raise ValueError('Enabled PowerTable row action requires a row-access selection')
            for access in filters:
                if not isinstance(access,dict) or not isinstance(access.get('recordGuid'),str) or not access['recordGuid']:
                    raise ValueError('PowerTable row-access filter record identity required')
                if not isinstance(access.get('name'),str) or not access['name']:
                    raise ValueError('PowerTable row-access filter name required')
                if access.get('filterType') not in (1,2,3) or not isinstance(access.get('filter'),dict):
                    raise ValueError('Invalid PowerTable row-access filter')
        setting_names.append(setting['name'])
    if len(setting_names)!=len(set(setting_names)): raise ValueError('Duplicate PowerTable source setting')
    outer=raw[prefix+'properties.json'].get('properties')
    inner=outer.get('properties') if isinstance(outer,dict) and isinstance(outer.get('properties'),dict) else outer
    if not isinstance(inner,dict) or inner.get('visualType')!=30 or not isinstance(inner.get('visualState'),dict):
        raise ValueError('Invalid configured PowerTable visual properties')
    state=inner['visualState'];column_meta=state.get('columnMeta');measures=state.get('manageMeasures')
    if not isinstance(column_meta,dict) or set(column_meta)!=set(names):
        raise ValueError('PowerTable visual column catalog differs from columnConfigs')
    if not isinstance(measures,list) or [item.get('id') for item in measures]!=names:
        raise ValueError('PowerTable managed-column order differs from columnConfigs')
    features=check_powertable_features(raw,prefix,set(concrete_guids))
    return {'sourceId':source_id,'columns':len(names),'settings':len(settings),**features}

def _native_json(value):
    """Exported workload records may hold a JSON object as a string; None if unparseable."""
    if isinstance(value,str):
        try:value=json.loads(value) if value.strip() else {}
        except ValueError:return None
    return value if isinstance(value,dict) else None

def check_powertable_features(raw,prefix,column_guids):
    """Optional Forms, Automations and Approvals parts that the Plan import consumes.

    Accepts product-export shapes (string configs, empty layouts, automations
    without recordGuid); the constructors that author new records stay strict.
    """
    found={}
    if prefix+'forms.json' in raw:
        forms=raw[prefix+'forms.json'].get('forms')
        if not isinstance(forms,list):raise ValueError('PowerTable forms.json requires a forms list')
        guids=[]
        for form in forms:
            if not isinstance(form,dict) or not isinstance(form.get('recordGuid'),str) or not form['recordGuid']:
                raise ValueError('PowerTable form record identity required')
            layout=_native_json(form.get('layoutMeta',{}))
            if not isinstance(form.get('title'),str) or (layout is not None and 'children' in layout and not isinstance(layout['children'],list)):
                raise ValueError('PowerTable form requires a title and list layout children')
            for field in form.get('formFields') or []:
                if not isinstance(field,dict) or not isinstance(field.get('recordGuid'),str):raise ValueError('PowerTable form field identity required')
                # Import resolves columnConfigId through column recordGuids; a stale one is silently dropped.
                if 'columnConfigId' in field and field['columnConfigId'] not in column_guids:
                    raise ValueError('PowerTable form field references an unknown column recordGuid')
                if field.get('required',0) not in (0,1):raise ValueError('PowerTable form field required must be 0 or 1')
            guids.append(form['recordGuid'])
        if len(guids)!=len(set(guids)):raise ValueError('Duplicate PowerTable form identity')
        found['forms']=len(forms)
    if prefix+'automations.json' in raw:
        automations=raw[prefix+'automations.json'].get('automations')
        if not isinstance(automations,list):raise ValueError('PowerTable automations.json requires an automations list')
        for automation in automations:
            trigger=automation.get('triggerType') if isinstance(automation,dict) else None
            if not isinstance(automation,dict) or not isinstance(automation.get('name'),str) or not (
                    type(trigger) is int or (isinstance(trigger,str) and trigger.isdigit())):
                raise ValueError('PowerTable automation requires a name and numeric triggerType')
            config=_native_json(automation.get('config'))
            if config is not None and isinstance(config.get('groups'),dict) and 'entryGroupId' in config and config['entryGroupId'] not in config['groups']:
                raise ValueError('PowerTable automation entry group is unresolved')
        found['automations']=len(automations)
    if prefix+'approvals.json' in raw:
        approval=raw[prefix+'approvals.json'].get('approvals')
        # Import iterates both lists without a null check; an omitted list fails the whole import.
        if not isinstance(approval,dict) or not isinstance(approval.get('approvalLevels'),list) or not isinstance(approval.get('approvalFilter'),list):
            raise ValueError('PowerTable approvals.json requires approvalLevels and approvalFilter lists')
        found['approvals']=1
    return found

def measure_references(value):
    found=set()
    def walk(item):
        if isinstance(item,dict):
            for key,nested in item.items():
                if key in ('Measure','LinkToMeasure') and isinstance(nested,str):
                    found.add(nested)
                walk(nested)
        elif isinstance(item,list):
            for nested in item:walk(nested)
    walk(value)
    return found

def validate_plan(raw):
    root=raw['definition.json']; sheets=root['sheets']; seen=set(); owners={}; measures={}; n=0
    # An export can hold a visual's parts under a path whose case differs from the ID in
    # definition.json; match them as the auditor does, case-insensitively (parts() already
    # rejects two paths that collide).
    folded={path.casefold(): path for path in raw}
    if not sheets or not root['semanticModelReference'].get('url'): raise ValueError('Missing sheets/model URL')
    for s in sheets:
        sid=s['recordGuid']; base=f'sheets/{sid}/'
        if sid in seen: raise ValueError('Duplicate sheet')
        seen.add(sid)
        if base+'sheet.json' not in raw: raise ValueError('Missing sheet companion')
        for v in s.get('workloadItemEntityVisuals',[]):
            vid=v['visualId']
            if v.get('isEmbedded'): continue
            if vid in owners: raise ValueError('Multiple visual owners')
            owners[vid]=sid; p=base+f'visuals/{vid}/'
            found=folded.get((p+'properties.json').casefold())
            if found: p=found[:len(found)-len('properties.json')]
            if p+'properties.json' not in raw: raise ValueError('Missing visual properties')
            if v['visualType']=='PLANNING':
                for companion in (p+'dataInput.json',base+'commentSettings.json'):
                    if companion not in raw: raise ValueError('Missing Planning companion '+companion)
                props=raw[p+'properties.json']['properties']; vs=props['visualState']; regs=vs['manage_measures']; cols=raw[p+'dataInput.json']['columns']
                from .input_constraints import check_records
                check_records(cols)
                from .planning_integrity import check_properties
                check_properties(props)
                if any(a.get('bucketId') in ('rows','columns') and a.get('columnType')=='Measure' for a in props.get('pivotAssignments',[])): raise ValueError('Measure cannot be a semantic grouping dimension')
                mids=[native_id(c['measureGuid']) for c in cols]
                if len(set(mids))!=len(mids) or {r['id'] for r in regs}!=set(mids) or len(regs)!=len(mids): raise ValueError('Measure activation registry mismatch')
                deps={x:[] for x in mids}
                from .aggregation import validate_config
                validate_config(vs['aggregation_config'])
                for c in cols:
                    mid=c['measureGuid']; meta=c['columnMeta']; kind=meta['measure_type']
                    if meta['id']!=mid or c['visualId']!=vid or len(kind)!=1: raise ValueError('Input/formula identity/owner mismatch')
                    if mid not in vs['aggregation_config']['measure_aggregation']: raise ValueError('Missing aggregation registration')
                    pair=vs['aggregation_config']['measure_aggregation'][mid]
                    if set(pair)!={'row','column'}: raise ValueError('Incomplete axis aggregation')
                    for method in pair.values():
                        if isinstance(method,dict) and 'WeightedAverage' in method:
                            ref=method['WeightedAverage']
                            if ref not in deps: raise ValueError('Unresolved weighted-average measure')
                            deps[mid].append(ref)
                    if mid not in vs['formatConfig']['measure']: raise ValueError('Missing format registration')
                    for ref in re.findall(r'\bM_([0-9]+)\b',dumps(kind)):
                        if ref not in deps: raise ValueError('Unresolved formula/gate')
                        deps[mid].append(ref)
                    from .input_constraints import unwrap_measure_type
                    branch=unwrap_measure_type(kind)
                    if 'DataInput' in branch:
                        di=branch['DataInput']; expected=10 if di.get('bound_to_filter_context',True) else 20
                        if c.get('boundToFilterContext')!=expected or isinstance(c.get('boundToFilterContext'),bool): raise ValueError('Context binding mismatch')
                        number=di['column_type'].get('Number',{}); low=number.get('min_value'); high=number.get('max_value')
                        if low is not None and high is not None and 'Static' in low and 'Static' in high and low['Static']>high['Static']: raise ValueError('Minimum exceeds maximum')
                        refs=measure_references(di['column_type'])
                        if refs-set(deps): raise ValueError('Unresolved DataInput measure reference')
                        deps[mid].extend(refs)
                    if 'Forecast' in branch:
                        fc=branch['Forecast']; expected=10 if fc.get('bound_to_filter_context',True) else 20
                        if c.get('boundToFilterContext')!=expected or isinstance(c.get('boundToFilterContext'),bool):
                            raise ValueError('Forecast context binding mismatch')
                        refs=measure_references(fc)
                        if refs-set(deps): raise ValueError('Unresolved Forecast measure reference')
                        deps[mid].extend(refs)
                acyclic(deps); measures[vid]=mids; n+=len(cols)
            if v['visualType']=='POWERTABLE':
                for leaf in ('source.json','columnConfigs.json','sourceSettings.json'):
                    if p+leaf not in raw: raise ValueError('Missing PowerTable companion')
                check_powertable_parts(raw,p)
    for s in sheets:
        for v in s.get('workloadItemEntityVisuals',[]):
            if v.get('isEmbedded') and v['visualId'] not in owners: raise ValueError('Embedded source owner unresolved')
    if 'connectedPlanning/infobridge.json' in raw:
        from .bridge import validate_graph
        validate_graph(raw['connectedPlanning/infobridge.json'])
    props=raw['planProperties.json']['properties']; bookmarks=props.get('bookmarks',[]); slugs=set()
    for b in bookmarks:
        bm=b['cloudMeta']['bookmarkMeta']; slug=b['bookmarkSlug']
        if slug in slugs or slug!=bm['bookmarkSlug'] or bm['activePageId'] not in seen: raise ValueError('Invalid public bookmark identity/page')
        slugs.add(slug)
        if not set(b['cloudMeta']['bookmarkVisualMeta'])<=owners.keys(): raise ValueError('Bookmark visual unresolved')
    return {'status':'passed-structural-invariants','sheets':len(sheets),'directVisuals':len(owners),'measureRecords':n,'publicBookmarks':len(bookmarks),'nativeRuntime':'not-run'}

def public_schema_view(path,obj):
    """Normalize reviewed native extensions only for historical public schemas."""
    value=copy.deepcopy(obj); extensions=[]
    if path=='definition.json':
        reporting_types={'BI_TEXT','SUPER_FILTER','ANALYTICS_PLUS','BI_RUNTIME_INPUT','INFORIVER','TREE'}
        normalized=False
        for sheet in value.get('sheets',[]):
            if sheet.get('sheetType')!='REPORTING':continue
            for visual in sheet.get('workloadItemEntityVisuals',[]):
                if not visual.get('isEmbedded') and visual.get('visualType') in reporting_types:
                    visual['visualType']='PLANNING';normalized=True
        if normalized:extensions.append('Reporting visual types are native Plan extensions absent from the pinned public schema')
    if path=='planProperties.json' and value.get('properties',{}).get('homeLayout')=={'show':True}:
        value['properties']['homeLayout']=''
        extensions.append('Native object homeLayout replaces the historical public string format')
    theme=value.get('properties',{}).get('theme') if path=='planProperties.json' else None
    if isinstance(theme,dict) and {'id','appliedThemes'}&set(theme):
        # Exports carry the theme id and the per-sheet applied-theme map; import rewires its keys.
        value['properties']['theme']={k:v for k,v in theme.items() if k not in ('id','appliedThemes')}
        extensions.append('Native theme members id and appliedThemes extend the historical public theme object')
    if path.endswith('/dataInput.json'):
        normalized=False
        def normalize_input_policy(item):
            nonlocal normalized
            if isinstance(item,dict):
                policy=item.get('allow_input')
                if policy=='Edit' or (isinstance(policy,dict) and set(policy)=={'BasedOnFormula'} and
                                     isinstance(policy['BasedOnFormula'],str) and policy['BasedOnFormula']):
                    item['allow_input']='ReadAndEdit';normalized=True
                if 'bound_to_filter_context' in item and isinstance(item['bound_to_filter_context'],bool):
                    item.pop('bound_to_filter_context');normalized=True
                for key in ('min_value','max_value'):
                    tagged=item.get(key)
                    if isinstance(tagged,dict) and set(tagged)=={'Static'} and isinstance(tagged['Static'],(int,float)) and not isinstance(tagged['Static'],bool):
                        item[key]=tagged['Static'];normalized=True
                for child in item.values():normalize_input_policy(child)
            elif isinstance(item,list):
                for child in item:normalize_input_policy(child)
        normalize_input_policy(value)
        if normalized:extensions.append('Native target-input policy is newer than the pinned public DataInput schema')
    if path.endswith('/automations.json') and isinstance(value.get('automations'),list):
        # The automation engine evaluates one {combinator, rules} group; the public
        # schema describes conditions as an array. Check the group as a one-item array.
        normalized=False
        for automation in value['automations']:
            config=automation.get('config') if isinstance(automation,dict) else None
            trigger=config.get('trigger') if isinstance(config,dict) else None
            trigger_config=trigger.get('triggerConfig') if isinstance(trigger,dict) else None
            if isinstance(trigger_config,dict) and isinstance(trigger_config.get('conditions'),dict):
                trigger_config['conditions']=[trigger_config['conditions']];normalized=True
        if normalized:extensions.append('Native automation conditions are one rule group; the public schema lists an array')
    if path=='cube/cube.json' and isinstance(value.get('cubePartitionMeasures'),list):
        # The schema's oneOf pairs the enum with plain text, so the documented values match both branches and fail.
        normalized=False
        for measure in value['cubePartitionMeasures']:
            config=measure.get('config') if isinstance(measure,dict) else None
            for key in ('data_type','dataType'):
                if isinstance(config,dict) and config.get(key) in ('Number','Text'):config.pop(key);normalized=True
        if normalized:extensions.append('The public cube schema rejects the documented data types Number and Text because both oneOf branches match them')
    return value,extensions

def schema_report(raw):
    s=Schemas(); result=[]
    for path,obj in raw.items():
        if not isinstance(obj,dict) or '$schema' not in obj: result.append({'path':path,'status':'uncovered','reason':'No declared schema'}); continue
        candidate,extensions=public_schema_view(path,obj)
        try:
            s.check(candidate,candidate['$schema'])
            result.append({'path':path,'status':'passed-native-extension' if extensions else 'passed-public-schema',
                           **({'reason':'; '.join(extensions)} if extensions else {})})
        except Invalid as e: result.append({'path':path,'status':'schema-conflict','reason':str(e)})
        except SchemaGap as e: result.append({'path':path,'status':'schema-gap','reason':str(e)})
    return result

def require_public_schema_acceptance(raw):
    report=schema_report(raw)
    blocked=[item for item in report if item['status'] in ('schema-conflict','schema-gap')]
    if blocked:
        details='; '.join(item['path']+': '+item['reason'] for item in blocked)
        raise ValueError('PUBLIC_SCHEMA_VALIDATION: '+details)
    return report
