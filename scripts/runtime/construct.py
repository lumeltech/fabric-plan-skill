"""Model-driven Planning constructors. Business choices are explicit in the spec.
No old report is read. Native initialization/import still requires target acceptance.
"""
import copy, re, uuid, html
from pathlib import Path
from .codec import load, dumps, pack
from .identity import Registry, native_id
from .paths import ASSETS
BASE='https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/'
GRAND_TOTAL_ROW_ID='16017913890930171270'
def schema(name): return BASE+name+'/1.0.0/schema.json'
def guid(): return str(uuid.uuid4())
def merge(a,b):
    r=copy.deepcopy(a)
    for k,v in b.items(): r[k]=merge(r[k],v) if isinstance(v,dict) and isinstance(r.get(k),dict) else copy.deepcopy(v)
    return r
def field(model,key,bucket,order):
    f=next((f for f in model['fields'] if f['id']==key),None)
    if f is None: raise ValueError('Unknown semantic field '+key)
    if bucket not in ('rows','columns','ameasure'): raise ValueError('Unknown bucket')
    if bucket in ('rows','columns') and f['columnType']=='Measure': raise ValueError('Semantic measures belong in Values; measures-in-rows is a separate native layout setting')
    return {'id':key,'sourceId':key,'sourceType':'PowerBI','bucketId':bucket,'columnName':f['columnName'],
       'tableName':f['tableName'],'name':f['columnName'],'columnType':f['columnType'],'dataType':f['dataType'],
       'dataRoleType':'Measure' if bucket=='ameasure' else 'Grouping','order':order,'contents':'',
       'formatString':f.get('formatString',''),'distinctValueCount':0,'isFlatHierarchy':False,'isHierarchyItemInMeasure':False}
def tagged(value,ids):
    if value is None: return None
    if not isinstance(value,dict) or len(value)!=1: raise ValueError('Expected Static or Measure tagged value')
    kind,v=next(iter(value.items()))
    if kind=='Static':
        if isinstance(v,bool) or not isinstance(v,(int,float)):
            from decimal import Decimal
            if isinstance(v,bool) or not isinstance(v,Decimal): raise ValueError('Static Number must be numeric')
        return {'Static':v}
    if kind=='Measure':
        if v not in ids: raise ValueError('Unresolved measure reference '+str(v))
        return {'Measure':ids[v]}
    raise ValueError('Unsupported numeric tag '+kind)
def expression(text,ids):
    # Named placeholders are explicit; never replace arbitrary words in formulas.
    if not isinstance(text,str) or not text.strip(): raise ValueError('Empty formula')
    def sub(m):
        key=m.group(1)
        if key not in ids: raise ValueError('Unresolved formula symbol '+key)
        return 'M_'+ids[key]
    text=re.sub(r'\$\{([A-Za-z_][\w.-]*)\}',sub,text)
    if '${' in text: raise ValueError('Invalid formula placeholder')
    known=set(ids.values())
    for ref in re.findall(r'\bM_([0-9]+)\b',text):
        if ref not in known: raise ValueError('Unresolved native formula identity')
    from .formula_syntax import check_formula
    return check_formula(text)
def acyclic(deps):
    seen=set(); active=set(); order=[]
    def walk(k):
        if k in active: raise ValueError('Dependency cycle at '+k)
        if k in seen: return
        if k not in deps: raise ValueError('Missing dependency '+k)
        active.add(k)
        for n in deps[k]: walk(n)
        active.remove(k); seen.add(k); order.append(k)
    for k in deps: walk(k)
    return order
def sheet_properties(width=1600,height=1200):
    if not 100<=width<=8000 or not 100<=height<=8000: raise ValueError('Custom canvas outside supported UI range')
    return {'$schema':schema('Sheets/Sheet'),'properties':{
     'entityLevelVariables':[],'filterPanePosition':'RIGHT','controlPanePosition':'right',
     'topPositionFilterExpandConfig':{'isFilterPaneCollapsed':False,'expandedHeight':200},
     'pageLevelFilterAssignments':[],'assignmentColumnMap':{},'visualGroupMap':{},'sourceVisualsMeta':{},'reactiveVisualProperties':[],
     'canvasStyle':{'dimension':{'type':'custom','width':width,'height':height,'elementScalingUnit':'pixel'},
      'background':{'type':'color','value':'#EEF4F6','isEnabled':True,'fillMode':'cover','opacity':0,'color':'#EEF4F6','imageUrl':''},
      'wallpaper':{'isEnabled':False,'value':{'type':'color','color':'#EEF4F6','imageUrl':''},'opacity':0,'fillMode':'cover'},
      'border':{'color':'#D9E3E8','side':'all','width':0,'isEnabled':False},
      'shadow':{'blur':8,'color':'#E0E0E0','isEnabled':False,'placement':'outer','side':'bottom','width':0,'opacity':70,'distance':10,'angle':135},
      'cornerRadius':{'isEnabled':False,'isCustomCornerRadius':False,'radiusBottomLeft':0,'radiusBottomRight':0,'radiusTopLeft':0,'radiusTopRight':0},
      'isLocked':False,'gridLineSettings':{'showGridLines':False,'snapToGrid':False,'gridRows':None,'gridColumns':None,'gridLayoutType':'custom'},
      'showVisualGuide':True,'showSmartGuide':True,'verticalAlign':'top','scrollToZoom':False,
      'mobileCanvas':{'editModeDimension':{'width':390,'height':844},'runtimeDimension':{'width':390,'height':844}}}}}
def comments(enabled=False):
    return {'$schema':schema('Sheets/CommentSettings'),'recordGuid':guid(),'allowComment':enabled,'enableCommentsColumn':False,'notification':False}
def plan_properties():
    edit=['Filter','Data','Fields','Elements','Bookmarks','Personalize','Comments','Variables']
    read=['Filter','Data','Bookmarks','Personalize','Variables','Comments']
    return {'$schema':schema('PlanProperties'),'properties':{'workloadModeConfig':{
       'EDIT':{'show'+n+'Pane':True for n in edit},'READ':{'show'+n+'Pane':n in ('Filter','Bookmarks','Comments') for n in read}},
       'homeLayout':{'show':True},'workloadLevelFilterAssignments':[],'workloadLevelVariables':[],'pageGroupingMeta':{'pageGroupMapping':{},'pageGroups':[]}}}
def planning(model,spec,registry,*,query_fields=()):
    from .linked_values import value_assignment
    def semantic_value(model,key,registry,**kw):
        return value_assignment(model,key,registry,query_fields=query_fields,**kw)
    from .filters import prepare_context,apply_context,audit_context,ensure_axis_filters
    from .time_authoring import prefer_forecast_axis
    spec=prefer_forecast_axis(model,spec)
    spec,contexts=prepare_context(model,spec)
    sid=spec.get('sheetId') or guid(); vid=spec.get('visualId') or guid(); keys={}
    ms=spec['measures']
    if any(k in spec for k in ('anchors','anchorRequests','anchor_config')) or any(
            any(k in m for k in ('anchor_config','anchorConfig')) for m in ms):
        raise ValueError('Use per-measure anchor with row_fields, column_fields and optional display_at_all_levels')
    for m in ms:
        if 'anchor' in m:
            cfg = m['anchor']
            if not isinstance(cfg, dict) or not {'row_fields','column_fields'} <= cfg.keys() or set(cfg)-{'row_fields','column_fields','display_at_all_levels'}:
                raise ValueError('Use per-measure anchor with row_fields, column_fields and optional display_at_all_levels')
    from .authoring_flow import require_base_input_contract
    for m in ms:require_base_input_contract(m)
    if not ms: raise ValueError('Planning sheet needs at least one measure')
    if len({m['key'] for m in ms})!=len(ms): raise ValueError('Duplicate measure key')
    for m in ms:
        if m['kind']=='Native':
            f=semantic_value(model,m['source'],registry,aggregation=m.get('sourceAggregation'))
            keys[m['key']]=f['measureGuid']
        else: keys[m['key']]=registry.custom(sid+':'+m['key'])
    assignments=[]; axes={}; dims={}
    for bucket in ('rows','columns'):
        axes[bucket]=[]
        for i,key in enumerate(spec.get(bucket,[])):
            a=field(model,key,bucket,i); assignments.append(a)
            from .dimension_hash import generate_dimension_id
            mid=registry.bind('dimension:'+key,generate_dimension_id(key))
            dims[key]=mid; axes[bucket].append({'externalKey':key,'id':mid,'isNative':True,'label':a['name']})
    if any(m['kind']=='Forecast' for m in ms):
        from .forecast import forecast_time_axis
        forecast_time_axis(axes['columns'],spec.get('columnTimeLevels'))
    if not axes['rows'] and not axes['columns']: raise ValueError('Specify business grain explicitly')
    vs={'manage_measures':[],'aggregation_config':{'measure_aggregation':{},'row_measure_aggregation':{},'row_member_measure_aggregation':{},'row_dimension_aggregation':{}},
        'formatConfig':{k:{} for k in ('row','column','cell','measure','columnDimension','rowDimension','labelCellGroup','rowGroup','rowMemberInDimension','columnMemberInDimension','columnHierarchy')},'rowDimensions':axes['rows'],'columnDimensions':axes['columns'],
        'globalStyles':{'fontFamily':'Arial','fontSize':'12'},'layoutSizes':{'labelWidth':230},
        'row_height_config':{'default_row_height':26,'sub_total_row_height':26,'custom_row_height':{GRAND_TOTAL_ROW_ID:26},'row_level_height':[]},
        'dimension_id_mapping':{'mappings':None,'pivot':[]},'measureAttributes':{},
        'totals_config':{'column_grand_total':'Left','column_sub_total':None,'freeze_total':False,'row_grand_total':'Top','row_sub_total':'Top'}}
    records=[]; dependencies={}
    for order,m in enumerate(ms):
        key=m['key']; mid=keys[key]; kind=m['kind']; label=m['label']; deps=[]
        if kind=='Native':
            a=semantic_value(model,m['source'],registry,
                order=sum(x['bucketId']=='ameasure' for x in assignments),
                label=label,aggregation=m.get('sourceAggregation'))
            assignments.append(a)
            payload={'measure_role':m.get('role','ACMeasure')}
        elif kind=='DataInput':
            num={n:tagged(m.get(n),keys) for n in ('default_value','min_value','max_value')}
            from .input_constraints import static_bounds,distribution_default
            static_bounds(num)
            for flag in ('context_bound','distribute'):
                if flag in m and not isinstance(m[flag],bool): raise ValueError(flag+' must be a Boolean')
            low=num['min_value']; high=num['max_value']
            if low is not None and high is not None and 'Static' in low and 'Static' in high and low['Static']>high['Static']:
                raise ValueError('Minimum exceeds maximum')
            num['distribute_parent_value_to_children']=distribution_default(m)
            from .input_policy import allow_input
            permit=allow_input(m.get('allow_input','ReadAndEdit'),keys)
            if isinstance(permit,dict):
                deps+=re.findall(r'\$\{([\w.-]+)\}',m['allow_input']['BasedOnFormula'])
            for n in ('default_value','min_value','max_value'):
                if isinstance(m.get(n),dict) and 'Measure' in m[n]: deps.append(m[n]['Measure'])
            payload={'allow_input':permit,'bound_to_filter_context':m.get('context_bound',True),
                'column_type':{'Number':num},'id':'','on_change_formula':expression(m['on_change'],keys) if m.get('on_change') else '', 'title':label}
            from .cube_contract import saved_cube_binding
            payload.update(saved_cube_binding(m.get('cube_partition_measure_id'),m.get('cube_model')))
            if m.get('on_change'): deps+=re.findall(r'\$\{([\w.-]+)\}',m['on_change'])
        elif kind=='Formula':
            payload={'formula':expression(m['formula'],keys)}; deps+=re.findall(r'\$\{([\w.-]+)\}',m['formula'])
            if m.get('cube_partition_measure_id') is not None:
                from .cube_contract import saved_cube_binding
                payload.update(saved_cube_binding(m['cube_partition_measure_id']))
            if 'cube_model' in m:
                raise ValueError('cube_model is a DataInput/Forecast binding, not a Formula binding')
        elif kind=='Forecast':
            from .forecast import forecast_config
            payload=forecast_config(m,keys,{x['key']:x['kind'] for x in ms},columns=spec['columns'],time_levels=spec.get('columnTimeLevels'))
            deps.append(m['actuals'])
            default=m.get('openDefault')
            if isinstance(default,dict) and 'Measure' in default: deps.append(default['Measure'])
            if isinstance(default,dict) and 'Formula' in default: deps+=re.findall(r'\$\{([\w.-]+)\}',default['Formula'])
            if isinstance(m.get('allow_input'),dict):deps+=re.findall(r'\$\{([\w.-]+)\}',m['allow_input']['BasedOnFormula'])
        else: raise ValueError('Use documented selected-kind constructor for '+kind)
        dependencies[key]=list(set(deps))
        rec={'columnMeta':{'data_type':'Number','description':m.get('description',''),'id':mid,'label':label,'measure_type':{kind:payload}},
             'dataInputType':6,'description':m.get('description'),'measureGuid':mid,'name':label,'visualId':vid}
        if m.get('visual_column'):
            if kind not in ('Formula','DataInput'):raise ValueError('Only Formula/DataInput can be authored as a VisualColumn')
            rec['columnMeta']['measure_type']={'VisualColumn':{kind:payload}}
        if kind in ('DataInput','Forecast'): rec['boundToFilterContext']=10 if payload['bound_to_filter_context'] else 20
        records.append(rec); vs['manage_measures'].append({'id':mid,'label':label,'order':order,'visible':m.get('visible',True)})
        from .aggregation import resolve
        agg=resolve(m.get('aggregation','Formula' if kind=='Formula' else 'Sum'),keys)
        colagg=resolve(m.get('columnAggregation','None' if m.get('visual_column') else agg),keys)
        vs['aggregation_config']['measure_aggregation'][mid]={'row':agg,'column':colagg}
        from .planning_presentation import PALETTE
        role={'Native':'powerbi','DataInput':'input','Formula':'formula','Forecast':'input'}[kind]
        if kind=='Native' and a.get('sourceType')=='InfoBridge':role='linked'
        vs['formatConfig']['measure'][mid]=[{'format':{'4':'Arial','3':PALETTE[role]['text'],**({'5':PALETTE[role]['tint']} if kind!='Forecast' else {})},'order':order}]
    vs['formatConfig']['formatSize']=len(ms)
    vs['formatConfig']['__lastHouseKeepedSize']=0
    acyclic(dependencies)
    if 'dimensionKeyGroups' in spec:
        from .dimension_mapping import leaf_key_mapping
        if 'dimensionIdMappings' in spec: raise ValueError('Use dimensionKeyOverrides with leaf key groups')
        vs['dimension_id_mapping']=leaf_key_mapping(model,assignments,spec['dimensionKeyGroups'],overrides=spec.get('dimensionKeyOverrides'))
    if 'dimensionIdMappings' in spec:
        from .dimension_mapping import dimension_mapping
        vs['dimension_id_mapping']=dimension_mapping(model,[a for a in assignments if a['bucketId'] in ('rows','columns')],spec['dimensionIdMappings'],
            descriptor_only_assignments=spec.get('lookupContextAssignments',()),skip_support=spec.get('dimensionSkipSupport'))
    if 'pivots' in spec:
        if 'pivot' in spec: raise ValueError('Use symbolic pivots or native state, not both')
        from .pivots import compile_pivots
        saved=compile_pivots(spec['pivots'],{'sheetId':sid,'rows':spec.get('rows',[]),
            'columns':spec.get('columns',[]),'dimensions':dims,'measures':keys},registry,
            spec.get('activePivot'),spec.get('capabilities'))
        vs['pivot']=saved['pivot']; vs['pivotExplorer']=saved['pivotExplorer']
    # Runtime-native branches selected in the spec are merged only at declared paths.
    for k in ('pivot','data_input_rules','measureModelConfig','row_expand_state_config','filterContextSettings','tableState','columnExpandCollapse','totals_config'):
        if k in spec:
            if k=='totals_config':vs[k].update(copy.deepcopy(spec[k]))
            else:vs[k]=copy.deepcopy(spec[k])
    props={'pivotAssignments':assignments,'superFilterAssignments':copy.deepcopy(spec.get('superFilterAssignments',[])),
           'visualState':vs,'position':{'x':24,'y':24},'dimension':{'width':1552,'height':900}}
    from .display_defaults import planning_display_defaults
    props=planning_display_defaults(props,records)
    apply_context(props,contexts)
    ensure_axis_filters(props)
    from .planning_integrity import repair_properties
    props=repair_properties(props,model)['properties'];vs=props['visualState']
    from .column_presentation import apply_column_presentation
    mode=spec.get('columnPresentation','expanded')
    if mode not in ('expanded','preserve'):raise ValueError('columnPresentation must be expanded or preserve')
    if mode=='expanded':
        # Explicit authored views/totals retain their intent. Otherwise initialize
        # all bound column levels, not a hard-coded Year/Quarter/Month template.
        props=apply_column_presentation(props,
            expansion=not any(k in spec for k in ('columnExpandCollapse','tableState','pivots','pivot')),
            default_column_totals='totals_config' not in spec)
        vs=props['visualState']
    from .roll_forward import apply_totals_defaults,roll_forward_presentation
    props=apply_totals_defaults(props)
    from .header_sizing import apply_hierarchy_icons
    props=apply_hierarchy_icons(props)
    if 'measureHierarchy' in spec:
        hierarchy=[{'id':keys[n['measure']],'level':n['level']} for n in spec['measureHierarchy']]
        props=roll_forward_presentation(props,hierarchy)
    if 'conditionalFormatting' in spec:
        from .matrix_formatting import compile_formatting,symbolic_rules
        props['visualState']=compile_formatting(props['visualState'],{'rules':symbolic_rules(spec['conditionalFormatting'],keys)})['state']
    audit_context(props,records)
    from .storage_context import require_query
    for a in assignments:
        if a.get('sourceType')=='InfoBridge':
            matched=[f for f in query_fields if f.get('id')==a['id']]
            if len(matched)!=1:raise ValueError('Resolve current query output before validating storage Context')
            require_query(matched[0].get('storageContext'),props,a['queryId'])
    from .planning_presentation import header_properties,measure_roles,default_description
    props=header_properties(props,spec['name'],default_description(spec),measure_roles(props,records))
    if any('anchor' in m for m in ms):
        from .anchor_measures import apply_anchors
        requests = [dict(m['anchor'], measure_id=keys[m['key']]) for m in ms if 'anchor' in m]
        props = apply_anchors(props, vid, requests)['properties']
    prefix=f'sheets/{sid}/'
    raw={prefix+'sheet.json':sheet_properties(),prefix+'commentSettings.json':comments(spec.get('comments',False)),
         prefix+f'visuals/{vid}/properties.json':{'$schema':schema('Planning/Properties'),'properties':props},
         prefix+f'visuals/{vid}/dataInput.json':{'$schema':schema('Planning/DataInput'),'columns':records}}
    declaration={'recordGuid':sid,'displayName':spec['name'],'sheetType':'PLANNING','isHidden':spec.get('hidden',False),
        'workloadItemEntityVisuals':[{'visualId':vid,'visualType':'PLANNING','isEmbedded':False}]}
    return declaration,raw,{'sheetId':sid,'visualId':vid,'measures':keys,'dimensions':dims,'dependencies':dependencies,
        'pivots':saved['ids'] if 'pivots' in spec else {}}
def build(model,spec,registry=None):
    """Component assembly only; use build_application/provision for a full flow."""
    registry=registry or Registry(); ref=copy.deepcopy(model['reference'])
    needed=['connectionId','semanticModelId','semanticModelName','semanticModelWorkspaceId','semanticModelWorkspaceName','directLakeMode','directQueryMode','sourceType','url']
    if any(k not in ref for k in needed): raise ValueError('Incomplete resolved semantic model reference')
    if not ref['url'].startswith('https://'): raise ValueError('Model URL missing or invalid')
    raw={'definition.json':{'$schema':schema('Definition'),'workloadItemName':spec['name'],'semanticModelReference':ref,'sheets':[]},'planProperties.json':plan_properties()}
    if spec.get('theme') is not None:
        # Plan-wide: only an explicit request names a theme.
        from .ibcs_report import set_plan_theme
        raw['planProperties.json']=set_plan_theme(raw['planProperties.json'],spec['theme'])
    identities=[];owners={};dashboard_identities=[]
    for s in spec['sheets']:
        if s['name'] in owners: raise ValueError('Duplicate sheet name')
        d,r,i=planning(model,s,registry,query_fields=spec.get('queryFields',())); d['order']=len(identities); raw['definition.json']['sheets'].append(d); raw.update(r); identities.append(i)
        p=r[f'sheets/{i["sheetId"]}/visuals/{i["visualId"]}/properties.json']['properties']
        owners[s['name']]={**i,'contexts':[x for x in p.get('superFilterAssignments',[]) if x.get('isContextDimension')]}
    if not identities: raise ValueError('No requested sheets')
    from .public_alignment import fresh_matrix_ids
    placement_ids = fresh_matrix_ids(raw['definition.json']['sheets'])
    for owner in owners.values():
        owner['placementIds'] = placement_ids[owner['visualId']]
    for spec_page in spec.get('dashboards',[]):
        from .intelligence import dashboard
        if spec_page['name'] in {s['displayName'] for s in raw['definition.json']['sheets']}: raise ValueError('Duplicate dashboard name')
        d,r,i=dashboard(model,spec_page,owners,registry,query_fields=spec.get('queryFields',()),page_count=len(spec['dashboards']));d['order']=len(raw['definition.json']['sheets'])
        raw['definition.json']['sheets'].append(d);raw.update(r);dashboard_identities.append(i)
    from .application_defaults import embedded_planning_owners
    sheets = raw['definition.json']['sheets']
    embedded = embedded_planning_owners(sheets)
    for sheet in sheets:
        if sheet['recordGuid'] in embedded:
            sheet['isHidden'] = True
    return {'raw':raw,'envelope':pack(raw),'registry':registry.entries,'identities':identities,
      'dashboardIdentities':dashboard_identities,
      'evidence':{'construction':'generated','applicationComplete':False,
          'requiredCompletionGate':'runtime.application_defaults.require_delivery_phases',
          'liveImport':'not-run','runtimeCalculation':'not-run','rendered':'not-run'}}
def navigator(recipe=1,patch=None):
    fixtures=ASSETS/'fixtures'
    state=load(fixtures/'navigator-spec-1.json')
    if recipe!=1:
        p=load(fixtures/f'navigator-spec-{recipe}.json')
        if not isinstance(p,dict) or not any(k in p for k in ('type','style','navigatorTabsState','navigatorButtonState')):
            raise ValueError('That spec example is not a Navigator-state recipe')
        state=merge(state,p)
    state['style']['DEFAULT']['shapeState']['text']['fontFamily']='Arial'
    state=merge(state,patch or {})
    if state['type'] not in ('NAVIGATOR_BUTTON','PAGE_NAVIGATOR_TABS','BOOKMARK_TABS'): raise ValueError('Navigator type')
    if not state['style'].get('DEFAULT',{}).get('shapeState'): raise ValueError('Missing Navigator base style')
    tabs=state['navigatorTabsState']
    for k in ('selectedPages','hiddenBookmarks'):
        if k in tabs and (not isinstance(tabs[k],list) or any(not isinstance(x,str) for x in tabs[k])): raise ValueError(k+' must be string array')
    from .navigator_defaults import complete_defaults
    return complete_defaults(state)
