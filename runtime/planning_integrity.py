"""Offline Planning defaults and physical-field consistency, including write guards.

Defaults are the v7 feature-contracts GlobalStyles initializer, not CSS guesses.
Repair fills absent defaults and reconciles semantic grouping names. It never
changes storage keys, IDs, formulas, selected members, From Sheets or business data.
Successful checks are not runtime acceptance.
"""
import copy,json,math,re
from decimal import Decimal
from pathlib import Path
from .codec import load,unpack

ROOT=Path(__file__).resolve().parents[1]
DEFAULTS=load(ROOT/'fixtures/matrix-global-defaults.json')
STYLE_DEFAULT=load(ROOT/'fixtures/matrix-formatting-v1.json')['columnStyle']
CATEGORIES={'native','custom','locked','forecastOpen','forecastClosed'}

def default_global_styles():
    return copy.deepcopy(DEFAULTS)

def _positive(v):
    return not isinstance(v,bool) and isinstance(v,(int,float,Decimal)) and math.isfinite(v) and v>0

def _u32(v):
    return type(v) is int and 0<=v<=2**32-1

def check_styles(state):
    gs=state.get('globalStyles')
    if not isinstance(gs,dict):raise ValueError('Planning globalStyles must be an object')
    missing=set(DEFAULTS)-set(gs)
    if missing:raise ValueError('Incomplete Planning globalStyles: '+', '.join(sorted(missing)))
    for k,d in DEFAULTS.items():
        v=gs[k]
        if isinstance(d,bool):ok=type(v) is bool
        elif isinstance(d,str):ok=isinstance(v,str) and bool(v.strip())
        else:ok=_positive(v)
        if not ok:raise ValueError('Invalid Planning globalStyles.'+k)
    if not re.fullmatch(r'\d+(?:\.\d+)?',gs['fontSize']) or float(gs['fontSize'])<=0:
        raise ValueError('globalStyles.fontSize requires a positive numeric pixel string')
    if not re.fullmatch(r'\d+(?:\.\d+)?(?:px)?',gs['headerFontSize']) or float(gs['headerFontSize'].removesuffix('px'))<=0:
        raise ValueError('globalStyles.headerFontSize requires a positive pixel string')
    for k in ('fontWeight','hierarchyfontWeight','columnHierarchyFontWeight','subTotalFontWeight'):
        if gs[k] not in ('normal','bold','semiBold'):raise ValueError('Unsupported '+k)
    for k in ('fontStyle','hierarchyFontStyle','columnHierarchyFontStyle'):
        if gs[k] not in ('normal','italic'):raise ValueError('Unsupported '+k)
    styles=gs.get('columnStyle',{})
    if not isinstance(styles,dict):raise ValueError('columnStyle must be an object')
    for category,modes in styles.items():
        if category not in CATEGORIES:continue  # Preserve target extensions.
        if not isinstance(modes,dict) or not {'read','edit'}<=modes.keys():raise ValueError('Incomplete Column Style modes: '+category)
        for mode in ('read','edit'):
            entry=modes[mode]
            if not isinstance(entry,dict) or set(STYLE_DEFAULT)-set(entry):raise ValueError('Incomplete Column Style: '+category+'/'+mode)
            if not _positive(entry['fontSize']):raise ValueError('Column Style fontSize must be a positive number')
            for k in ('background','textColor','fillColor','borderColor','fillType','presetType','borderStyle'):
                if not isinstance(entry[k],str):raise ValueError('Invalid Column Style '+k)
            bw=entry['borderWidth']
            if isinstance(bw,bool) or not isinstance(bw,(int,float,Decimal)) or not math.isfinite(bw) or bw<0:raise ValueError('Invalid borderWidth')
            sides=entry['borderSides']
            if sides is not None and (not isinstance(sides,list) or any(type(x) is not int or not 1<=x<=12 for x in sides)):raise ValueError('Invalid borderSides')
    heights=state.get('row_height_config')
    if heights is not None:
        if not isinstance(heights,dict):raise ValueError('row_height_config must be an object')
        if 'default_row_height' in heights and not _u32(heights['default_row_height']):
            raise ValueError('row_height_config.default_row_height requires a native u32')
        if 'sub_total_row_height' in heights and heights['sub_total_row_height'] is not None and not _u32(heights['sub_total_row_height']):
            raise ValueError('row_height_config.sub_total_row_height requires a native u32 or null')
        custom=heights.get('custom_row_height',{})
        if not isinstance(custom,dict) or any(not _u32(value) for value in custom.values()):
            raise ValueError('row_height_config.custom_row_height values require native u32 heights')
        levels=heights.get('row_level_height',[])
        if not isinstance(levels,list) or any(not _u32(value) for value in levels):
            raise ValueError('row_height_config.row_level_height values require native u32 heights')
    return {'status':'complete-typed-defaults','runtime':'not-run'}

def complete_styles(state):
    out=copy.deepcopy(state);gs=out.setdefault('globalStyles',{})
    if not isinstance(gs,dict):raise ValueError('globalStyles must be an object; do not replace invalid state silently')
    for k,v in DEFAULTS.items():gs.setdefault(k,copy.deepcopy(v))
    styles=gs.get('columnStyle',{})
    if not isinstance(styles,dict):raise ValueError('columnStyle must be an object')
    for category,modes in styles.items():
        if category not in CATEGORIES:continue
        if not isinstance(modes,dict):raise ValueError('Column Style category must be an object')
        for mode in ('read','edit'):
            entry=modes.setdefault(mode,{})
            if not isinstance(entry,dict):raise ValueError('Column Style mode must be an object')
            for k,v in STYLE_DEFAULT.items():entry.setdefault(k,copy.deepcopy(v))
    check_styles(out)
    return out

def _field(key):
    # Exact persisted semantic identity is authoritative; no label-to-field guessing.
    if not isinstance(key,str) or not re.fullmatch(r'.+\[.+\]',key):raise ValueError('Resolve physical semantic field identity: '+str(key))
    table,column=key.split('[',1)
    return table,column[:-1]

def _is_group(a):
    return a.get('sourceType')=='PowerBI' and a.get('columnType')=='Column' and a.get('dataRoleType')=='Grouping'

def _names(properties,repair,model=None):
    errors=[];changes=[];fields={f['id']:f for f in model['fields']} if model else None
    query_fields={}
    def collect(x):
        if isinstance(x,dict):
            if x.get('sourceType')=='InfoBridge' and x.get('id') and x.get('queryId') is not None and x.get('columnName'):
                key=(str(x['queryId']),x['id']);name=x['columnName']
                if key in query_fields and query_fields[key]!=name:raise ValueError('Conflicting query output names')
                query_fields[key]=name
            for value in x.values():collect(value)
        elif isinstance(x,list):
            for value in x:collect(value)
    collect(properties)
    def change(obj,key,value,path,remove=False):
        if remove:
            if key not in obj:return
        elif obj.get(key)==value:return
        if repair:
            changes.append({'path':path+'/'+key,'before':copy.deepcopy(obj.get(key)),'after':None if remove else copy.deepcopy(value)})
            if remove:obj.pop(key,None)
            else:obj[key]=copy.deepcopy(value)
        else:errors.append(path+'/'+key)
    def canonical(key):
        table,col=_field(key)
        if fields is not None:
            f=fields.get(key)
            if not f or f.get('columnType')!='Column' or (table,col)!=(f['tableName'],f['columnName']):
                raise ValueError('Semantic grouping is not in current model: '+key)
        return table,col
    def walk(x,path='properties'):
        if isinstance(x,list):
            for i,v in enumerate(x):walk(v,path+'/'+str(i))
            return
        if not isinstance(x,dict):return
        if _is_group(x):
            table,col=canonical(x.get('id'))
            for k,v in (('tableName',table),('columnName',col),('name',col)):change(x,k,v,path)
            # source IDs can represent a different layer; do not rewrite them.
            if 'customName' in x:change(x,'customName',col,path)
            if x.get('isRenamed'):change(x,'isRenamed',False,path)
        for k in ('rowDimensions','columnDimensions'):
            for i,d in enumerate(x.get(k,[])):
                key=d.get('externalKey')
                if d.get('isNative') and isinstance(key,str) and re.fullmatch(r'.+\[.+\]',key):
                    _,col=canonical(key);change(d,'label',col,path+'/'+k+'/'+str(i))
        mapping=x.get('dimension_id_mapping')
        if isinstance(mapping,dict):
            for i,d in enumerate(mapping.get('pivot',[])):
                if d.get('source_type')!='PowerBI' or d.get('column_type')!='Column':continue
                _,col=canonical(d['id']);p=path+'/dimension_id_mapping/pivot/'+str(i)
                change(d,'column_name',col,p);change(d,'name',col,p)
                if d.get('custom_name') not in (None,col):change(d,'custom_name',None,p)
        # Filter captions and their sort metadata are part of this explicit
        # canonical-name repair. Selected member labels and values are untouched.
        assignments=x.get('pivotAssignments',[])
        if isinstance(x.get('configuration'),dict) and len(assignments)==1 and _is_group(assignments[0]):
            _,col=canonical(assignments[0]['id']);change(x['configuration'],'name',col,path+'/configuration')
        if isinstance(x.get('columnId'),str) and x.get('columnName') is not None and re.fullmatch(r'.+\[.+\]',x['columnId']):
            if x.get('queryId') is not None:
                expected=query_fields.get((str(x['queryId']),x['columnId']))
                if expected is None or x['columnName']!=expected:raise ValueError('Query sort descriptor does not match its assigned output')
            else:
                _,col=canonical(x['columnId']);change(x,'columnName',col,path)
        if all(isinstance(x.get(k),list) for k in ('columnIds','columnNames','tableNames','sourceType','columnType')):
            lengths={len(x[k]) for k in ('columnIds','columnNames','tableNames','sourceType','columnType')}
            if len(lengths)!=1:raise ValueError('Filter field arrays have inconsistent lengths')
            cn=list(x['columnNames']);tn=list(x['tableNames'])
            for i,key in enumerate(x['columnIds']):
                if x['sourceType'][i]=='PowerBI' and x['columnType'][i]=='Column':tn[i],cn[i]=canonical(key)
            change(x,'columnNames',cn,path);change(x,'tableNames',tn,path)
        for k,v in list(x.items()):walk(v,path+'/'+k)
    walk(properties)
    if errors:raise ValueError('Inconsistent semantic grouping names; run repair-planning-properties: '+', '.join(errors[:16]))
    return changes

def check_properties(properties,model=None):
    check_styles(properties['visualState']);_names(properties,False,model)
    return {'status':'passed-planning-integrity','runtime':'not-run','policy':'canonical-semantic-grouping-names'}

def repair_properties(properties,model=None):
    out=copy.deepcopy(properties);before=copy.deepcopy(out['visualState'].get('globalStyles',{}))
    out['visualState']=complete_styles(out['visualState']);changes=_names(out,True,model)
    after=out['visualState']['globalStyles']
    for k,v in after.items():
        if k not in before or before[k]!=v:changes.append({'path':'properties/visualState/globalStyles/'+k,'before':before.get(k),'after':copy.deepcopy(v)})
    return {'properties':out,'changes':changes,'check':check_properties(out,model),'runtime':'not-run'}

def _planning(p):
    return isinstance(p,dict) and isinstance(p.get('visualState'),dict) and 'manage_measures' in p['visualState'] and ('rowDimensions' in p['visualState'] or 'columnDimensions' in p['visualState'])

def check_definition(raw):
    from .input_constraints import check_records
    from .bridge_identity import check_planning_graph
    if 'connectedPlanning/infobridge.json' in raw:check_planning_graph(raw['connectedPlanning/infobridge.json'])
    count=0
    for path,obj in raw.items():
        if path.endswith('/dataInput.json') and isinstance(obj,dict):check_records(obj.get('columns',[]))
        p=obj.get('properties') if isinstance(obj,dict) else None
        if path.endswith('/properties.json') and _planning(p):check_properties(p);count+=1
    return {'planningVisualsChecked':count,'runtime':'not-run'}

def guard_write(method,route,body):
    """Called by Client before any network write; rejects, never silently repairs."""
    if method not in ('POST','PUT','PATCH'):return
    route=route.split('?',1)[0].rstrip('/')
    plan=bool(re.search(r'/plans(?:/[^/]+/updateDefinition)?$',route))
    if not plan:return
    if isinstance(body,bytes):body=json.loads(body)
    if not isinstance(body,dict):return
    if plan and isinstance(body.get('definition'),dict):check_definition(unpack(body))
