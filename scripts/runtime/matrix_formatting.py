"""Offline, owner-specific Matrix formatting. No network or arbitrary state writer.

Input/output is visualState, not an ALM or native API envelope. Operation identities
live in a task-local ledger, never in invented native properties.
"""
import copy
import json
import math
import re
import uuid
from decimal import Decimal
from pathlib import Path
from .paths import ASSETS

SNAPSHOT = json.loads((ASSETS/'fixtures/matrix-formatting-v1.json').read_text(encoding='utf-8'))
CF_SNAPSHOT = json.loads((ASSETS/'fixtures/matrix-cf-v2.json').read_text(encoding='utf-8'))
CATEGORIES = {'locked', 'native', 'custom', 'forecastOpen', 'forecastClosed'}
SCOPES = {'row','column','cell','measure','columnDimension','rowDimension','labelCellGroup',
          'rowGroup','rowMemberInDimension','columnMemberInDimension','columnHierarchy'}
KEYS = {'bold':'1','italic':'2','textColor':'3','fontFamily':'4','background':'5',
        'horizontalAlignment':'6','verticalAlignment':'7','prefix':'8','suffix':'9',
        'percentage':'10','decimals':'11','scaling':'13','fontSize':'16','indent':'17','showScaling':'18'}
HEADER_KEYS = {'1','2','3','4','5','6','7','16','17'}

def merge(base, patch):
    """Recursive maps only; callers must explicitly own any array replacement."""
    result=copy.deepcopy(base)
    for k,v in patch.items():
        if isinstance(v,dict) and isinstance(result.get(k),dict): result[k]=merge(result[k],v)
        else: result[k]=copy.deepcopy(v)
    return result

def require(ok, message):
    if not ok: raise ValueError(message)

def ident(value):
    require(isinstance(value,str) and bool(value.strip()) and '<' not in value, 'Resolved identifier string required')
    return value

def number(value, minimum=0):
    require(type(value) in (int,float,Decimal) and math.isfinite(value) and value>=minimum,'Finite number out of range')
    return value

def native_u32(value, minimum=0):
    require(type(value) is int and minimum<=value<=2**32-1,'Expected native unsigned 32-bit integer')
    return value

def color(value, fill=False):
    require(isinstance(value,str) and (re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?(?:[0-9a-fA-F]{2})?',value)
            or value in {'black','white','transparent'} or (fill and value in {'','nofill'})), 'Use a supported explicit color')
    return value

def pixel_size(value, unit='px'):
    number(value,0.01); require(unit in ('px','pt'),'Size unit must be px or pt')
    exact=float(value)*(96/72 if unit=='pt' else 1)
    px=round(exact,6)
    return px, {'requested':value,'unit':unit,'pixels':px,'rounding':'six decimal places' if px!=exact else 'none'}

def format_values(values, header=False):
    result={}
    for name,v in values.items():
        key=KEYS.get(name,name)
        require(key in (HEADER_KEYS if header else set(KEYS.values())), 'Unsupported format operation: '+name)
        if key in {'1','2','10','18'}: require(type(v) is bool,'Format Boolean required')
        elif key in {'6','7'}: require(type(v) is int and v in (1,2,3),'Alignment must be native 1/2/3')
        elif key in {'11','16','17'}:
            number(v,0.01 if key=='16' else 0)
            if key=='11': require(type(v) is int,'Decimal count must be an integer')
        elif key in {'3','5'}: color(v,key=='5')
        elif key=='13': require(isinstance(v,str) and (v in ('none','auto','autoFixed') or re.fullmatch(r'\d+',v)),'Scaling must be a native string')
        else: require(isinstance(v,str),'Format string required')
        result[key]=v
    require(not(result.get('10') and result.get('9')=='%'),'Percentage and percent suffix would duplicate the symbol')
    return result

def typography(state, request):
    allowed={'fontFamily','size','headerSize','headerHeight','textColor','headerFontColor',
             'fontWeight','fontStyle','hierarchyfontWeight','hierarchyFontStyle',
             'columnHierarchyFontWeight','columnHierarchyFontStyle','subTotalFontWeight'}
    require(not(set(request)-allowed),'Unknown typography property')
    patch={}; translations=[]
    for k,v in request.items():
        if k in ('size','headerSize'):
            require(isinstance(v,dict) and set(v)<= {'value','unit'} and 'value' in v,'Size needs value and optional unit')
            px,e=pixel_size(v['value'],v.get('unit','px'));translations.append(e)
            patch['fontSize' if k=='size' else 'headerFontSize']=format(px,'.12g')+('px' if k=='headerSize' else '')
        elif k=='headerHeight': number(v,1);patch.update(headerHeight=v,isHeightUpdatedManually=True)
        elif k.endswith('Color'):patch[k]=color(v)
        else:
            require(isinstance(v,str),'Typography string required')
            if k.endswith('Weight'):require(v in ('normal','bold','semiBold'),'Unsupported weight')
            if k.endswith('Style'):require(v in ('normal','italic'),'Unsupported font style')
            patch[k]=v
    state['globalStyles']=merge(state.get('globalStyles',{}),patch)
    return translations

def column_styles(state, request):
    require(not(set(request)-CATEGORIES),'Unknown Column Style category')
    styles=state.setdefault('globalStyles',{}).setdefault('columnStyle',{})
    for category,modes in request.items():
        require(isinstance(modes,dict) and set(modes)<= {'read','edit'},'Column Style uses read/edit modes')
        for mode,patch in modes.items():
            require(isinstance(patch,dict),'Use explicit style properties; reset is a separate operation')
            require(not(set(patch)-set(SNAPSHOT['columnStyle'])),'Unsupported Column Style property')
            for k,v in patch.items():
                if k in ('background','textColor','fillColor','borderColor'):color(v,k=='background')
                elif k in ('fontSize','borderWidth'):number(v,0.01 if k=='fontSize' else 0)
                elif k=='presetType':require(v in ('white','gray','hatched'),'Customize is not a persisted preset')
                elif k=='fillType':require(v in ('none','singleSideHatched','doubleSideHatched'),'Unsupported fill type')
                elif k=='borderStyle':require(v in ('none','solid','dotted','dashed','solidDouble','solidThrice'),'Unsupported border style')
                elif k=='borderSides': require(v is None or isinstance(v,list) and all(type(x) is int and 1<=x<=12 for x in v),'Native numeric border sides required')
            old=styles.setdefault(category,{}).get(mode)
            # New entries use a complete portable preset; existing fields, including
            # target-compatible null sides and unknown extension fields, survive.
            styles[category][mode]=merge(merge(SNAPSHOT['columnStyle'],old or {}),patch)

def identities(state, extra):
    managed=state.get('manage_measures',[])
    result={'measure':{ident(m['id']) for m in managed},
            'measureLabels':{ident(m['id']):str(m.get('label',m['id'])) for m in managed}}
    for bucket,scope in [('rowDimensions','rowDimension'),('columnDimensions','columnDimension')]:
        result[scope]={ident(d['id']) for d in state.get(bucket,[])}
    result['rowDimensionOrder']=[d['id'] for d in state.get('rowDimensions',[])]
    result['header']=result['rowDimension']|result['columnDimension']|{'measureHeader'}
    require(not(set(extra)-{'header','column','row','cell','columnHierarchy','labelCellGroup','rowGroup','rowMemberInDimension','columnMemberInDimension'}),'Unknown identity domain')
    for scope,ids in extra.items():
        require(isinstance(ids,list),'Identity catalog must contain arrays of strings')
        result.setdefault(scope,set()).update(ident(i) for i in ids)
    return result

def resolve(ids,scope,key):
    ident(key);require(key in ids.get(scope,set()),'Unresolved '+scope+' identity: '+key)

def headers(state, requests, ids):
    for item in requests:
        require(set(item)<= {'scope','format','height','headerId'},'Unknown header option')
        key=item['scope'];resolve(ids,'header',key)
        fmt=format_values(item['format'],True)
        old=state.setdefault('headerLabelFormat',{}).get(key,{})
        merged=merge(old,fmt)
        if '3' in fmt or '5' in fmt:
            require('3' in merged and '5' in merged,'Pair header text and fill in the same scope')
            require(merged['3'].lower()!=merged['5'].lower(),'Header text and fill cannot match')
        state['headerLabelFormat'][key]=merged
        if 'height' in item:
            number(item['height'],1)
            if key=='measureHeader':
                state['globalStyles']=merge(state.get('globalStyles',{}),{'headerHeight':item['height'],'isHeightUpdatedManually':True})
            else:
                hid=item['headerId'];resolve(ids,'header',hid)
                state.setdefault('columnHierarchyHeader',{}).setdefault(hid,{})['height']=item['height']

def ordered_formats(state, requests, ids, ledger):
    fc=state.setdefault('formatConfig',{})
    for scope in SCOPES:fc.setdefault(scope,{})
    orders=[e['order'] for scope in SCOPES for entries in fc[scope].values() for e in entries]
    require(all(type(n) is int and n>=0 for n in orders),'Invalid existing operation order')
    size=fc.get('formatSize',0);require(type(size) is int and size>=0,'Invalid formatSize')
    fc['formatSize']=max([size,*[n+1 for n in orders]])
    fc.setdefault('__lastHouseKeepedSize',0)
    require(type(fc['__lastHouseKeepedSize']) is int and fc['__lastHouseKeepedSize']>=0,'Invalid housekeeping counter')
    for item in requests:
        require(set(item)=={'key','scope','id','format'},'Format request needs stable key, scope, id, format')
        key=ident(item['key']);scope=item['scope'];require(scope in SCOPES,'Unknown format scope')
        resolve(ids,scope,item['id']);fmt=format_values(item['format'])
        entries=fc[scope].setdefault(item['id'],[])
        record=ledger.get(key)
        if record:
            require(record['scope']==scope and record['id']==item['id'],'Operation key reused for another target')
            found=[e for e in entries if e['order']==record['order']]
            require(len(found)==1,'Stale operation ledger; resolve baseline before patching')
            found[0]['format']=merge(found[0]['format'],fmt)
        else:
            # Exact repeat also works when no ledger was retained.
            found=[e for e in entries if e.get('format')==fmt]
            require(len(found)<=1,'Ambiguous repeated format; supply the prior ledger')
            if found:order=found[0]['order']
            else:
                order=fc['formatSize'];fc['formatSize']+=1
                entries.append({'order':order,'format':fmt})
            ledger[key]={'scope':scope,'id':item['id'],'order':order}

def conditional_rule(request, ids):
    required={'id','label','target','test','operator','threshold','rowScope','columnScope',
              'excludeRowTotal','excludeColumnTotal','appearance'}
    require(set(request)==required,'Rule requires explicit target, predicate, scope, totals and appearance')
    r=copy.deepcopy(CF_SNAPSHOT['ruleSeed']);c=copy.deepcopy(CF_SNAPSHOT['conditionSeed'])
    target=request['target'];tested=request['test']
    require(isinstance(request['label'],str) and request['label'],'Rule label required')
    for field in (target,tested):resolve(ids,'measure',field)
    require(request['operator'] in ('>','<','==','!=','>=','<='),'Supported numeric predicate required; equality is ==')
    threshold=request['threshold'];require(type(threshold) in (int,float,Decimal) and math.isfinite(threshold),'Numeric threshold required')
    for k in ('rowScope','columnScope'):require(request[k] in ('parent','child','both'),'Invalid CF scope')
    for k in ('excludeRowTotal','excludeColumnTotal'): require(type(request[k]) is bool,'Total exclusions must be Boolean')
    app=request['appearance'];require(isinstance(app,dict) and set(app)<= {'textColor','background','icon','iconColor','iconPosition','bold','italic'},'Unsupported rule appearance')
    for k in ('textColor','background','iconColor'):
        if k in app:color(app[k],k=='background')
    for k in ('bold','italic'):
        if k in app:require(type(app[k]) is bool,'Boolean appearance required')
    require(app.get('icon') in (None,'up','down','flag'),'Unsupported icon in this constructor')
    require(app.get('iconPosition','left') in ('left','right','iconOnly','textOnly'),'Invalid icon position')
    require(not app.get('icon') or 'iconColor' in app,'Icon requires explicit color')
    key=ident(request['id'])
    native_name=key if key.startswith(target) and key!=target else target+uuid.uuid5(uuid.NAMESPACE_URL,key).hex[:12].upper()
    labels=ids.get('measureLabels',ids.get('labels',{}))
    r.update(name=native_name,displayName=request['label'],enabled=True,ruleType='rule',
        highlightedMeasure=target,highlightedMeasureName=labels.get(target,target),
        basedOn=tested,basedOnMeasureName=labels.get(tested,tested),
        bubbleBasedOn=tested,newRule=True,
        highlightedColumnMembers=None,highlightedRowMembers=None,selectedColumnMeasures=None,ruleFor=request['rowScope'],columnRuleFor=request['columnScope'],
        excludeRowTotal=request['excludeRowTotal'],excludeColumnTotal=request['excludeColumnTotal'],
        conditionalOperator='or',applyTextColor='textColor' in app,applyBackgroundColor='background' in app,
        color=app.get('textColor',r['color']),background=app.get('background',r['background']),
        bold=app.get('bold',False),italic=app.get('italic',False),underline=False,hideCell=False,hatched=False,
        includeNull=False,isIconPresent=bool(app.get('icon')),icon=app.get('icon','up'),iconType='icon',
        iconPosition=app.get('iconPosition','left'),iconColor=app.get('iconColor',r['iconColor']),autoFontColor=True)
    for field in ('basedOn','comparisonMeasure','calculationMeasure1','calculationMeasure2','fromMeasure','toMeasure'):c[field]=tested
    c.update(name='Condition 0',conditionType='singleMeasure',basedOn=tested,valueType='static',
             comparisonMeasure=tested,operator=request['operator'],comparisonValue=threshold)
    r['conditions']=[c]
    dimensions=ids.get('rowDimensionOrder',[])
    r['ranking']['row_dimension_id']=dimensions[-1] if dimensions else None
    # Inactive bucket IDs are fresh per rule; their values do not drive numeric predicates.
    def rekey(value,path='rule'):
        if isinstance(value,dict):
            for k,v in value.items():
                if k=='id':value[k]=uuid.uuid5(uuid.NAMESPACE_URL,native_name+path).hex[:12].upper()
                else:rekey(v,path+'.'+k)
        elif isinstance(value,list):
            for i,v in enumerate(value):rekey(v,path+'.'+str(i))
    rekey(r)
    return r

def merge_rules(state, requests, ids, mirror=True):
    require(type(mirror) is bool,'Compatibility ownership must be explicit')
    rules=[conditional_rule(r,ids) for r in requests]
    require(len({r['id'] for r in requests})==len(requests),'Duplicate requested rule key')
    require(len({r['name'] for r in rules})==len(rules),'Duplicate requested rule identity')
    if not rules:return
    stores=['jet_cfProps','cfProps'] if mirror else ['jet_cfProps']
    # Missing current stores inherit existing records. Existing stores each retain
    # their unrelated rules, even when legacy compatibility content differs.
    original=copy.deepcopy(state)
    for store in stores:
        other='cfProps' if store=='jet_cfProps' else 'jet_cfProps'
        container=state.setdefault(store,copy.deepcopy(original.get(other,{'enabled':True,'rules':[]})))
        existing=container.setdefault('rules',[])
        require(len({r['name'] for r in existing})==len(existing),'Duplicate existing rule identity')
        for request,r in zip(requests,rules):
            matches=[i for i,x in enumerate(existing) if x['name'] in (r['name'],request['id'])]
            require(len(matches)<=1,'Both legacy and current rule IDs exist; reconcile selected rule explicitly')
            if not matches:existing.append(copy.deepcopy(r));continue
            i=matches[0];old=existing[i]
            require(old.get('ruleType','rule')=='rule' and len(old.get('conditions',[]))==1,
                    'Existing complex rule needs its own merge contract')
            # Preserve extensions and inactive UI defaults on a targeted update.
            new=merge(CF_SNAPSHOT['ruleSeed'],old)
            active={'name','displayName','enabled','ruleType','highlightedMeasure','highlightedMeasureName',
                    'basedOn','basedOnMeasureName','bubbleBasedOn',
                    'newRule','highlightedColumnMembers','highlightedRowMembers','selectedColumnMeasures',
                    'ruleFor','columnRuleFor','excludeRowTotal','excludeColumnTotal','conditionalOperator',
                    'applyTextColor','applyBackgroundColor','color','background','bold','italic','underline',
                    'hideCell','hatched','includeNull','isIconPresent','icon','iconType','iconPosition','iconColor','autoFontColor'}
            new.update({k:copy.deepcopy(r[k]) for k in active})
            new['ranking']['row_dimension_id']=r['ranking']['row_dimension_id']
            condition=merge(CF_SNAPSHOT['conditionSeed'],old['conditions'][0])
            active_condition={'name','conditionType','basedOn','valueType','comparisonMeasure','operator','comparisonValue',
                              'calculationMeasure1','calculationMeasure2','fromMeasure','toMeasure'}
            condition.update({k:copy.deepcopy(r['conditions'][0][k]) for k in active_condition})
            new['conditions']=[condition];existing[i]=new
        container['enabled']=True

def symbolic_rules(requests, measures):
    """New-report spec uses stable measure keys; wire IDs are resolved here."""
    require(isinstance(requests,list),'conditionalFormatting must be a list')
    result=copy.deepcopy(requests)
    for rule in result:
        for key in ('target','test'):
            require(rule.get(key) in measures,'Unknown conditional-format measure key: '+str(rule.get(key)))
            rule[key]=measures[rule[key]]
    return result


def sizing(state, request, ids):
    allowed={'measureWidths','columnWidths','labelWidth','rowHeight','subtotalHeight','wrapColumns','indent','responsive','widthPreference'}
    require(set(request)<=allowed,'Unsupported sizing option')
    for prop,scope,owner in [('measureWidths','measure','measureAttributes'),('columnWidths','column','columnMeta')]:
        for key,width in request.get(prop,{}).items():
            resolve(ids,scope,key);number(width,1)
            state.setdefault(owner,{}).setdefault(key,{})['width']=width
    for key,wire in [('rowHeight','default_row_height'),('subtotalHeight','sub_total_row_height')]:
        if key in request:
            native_u32(request[key])
            existing=state.get('row_height_config',{})
            state['row_height_config']=merge(SNAPSHOT['rowHeight'],existing)
            if 'custom_row_height' in existing:
                state['row_height_config']['custom_row_height']=copy.deepcopy(existing['custom_row_height'])
            state['row_height_config'][wire]=request[key]
    for key,wire in [('labelWidth','labelWidth'),('responsive','isResponsive'),('widthPreference','preferedWidthSelection')]:
        if key in request:
            v=request[key]
            if key=='labelWidth':number(v,1)
            elif key=='responsive':require(type(v) is bool,'Responsive must be Boolean')
            else:require(v in ('measure','column'),'Invalid width preference')
            state.setdefault('layoutSizes',{})[wire]=v
    if 'wrapColumns' in request:
        require(type(request['wrapColumns']) is bool,'Wrap must be Boolean')
        state.setdefault('auto_fit_options',{})['wrapCols']=request['wrapColumns']
    if 'indent' in request:number(request['indent']);state.setdefault('gridStyles',{})['indentSpacing']=request['indent']

def simple_slice(state, owner, patch):
    schema=SNAPSHOT['patchTypes'][owner]
    require(set(patch)<=set(schema),'Unknown '+owner+' property')
    for key,value in patch.items():
        kind=schema[key]
        if isinstance(kind,list):require(value in kind and type(value) is type(kind[0]),'Invalid '+key+' enum')
        elif kind=='color':color(value,key in ('gridBackground',))
        elif kind=='boolean':require(type(value) is bool,'Expected Boolean for '+key)
        elif kind=='number':number(value)
        elif kind=='integer':require(type(value) is int and value>=0,'Expected nonnegative integer')
        else:require(isinstance(value,str),'Expected string for '+key)
    update=copy.deepcopy(patch)
    if owner=='numberFormatting' and 'formatType' in patch:
        mode=patch['formatType']
        derived={
            'default':{'ibcsformat':True,'showScalingUnit':False,'scalingFactor':'autoFixed','noOfDecimal':2},
            'ibcs':{'ibcsformat':True,'showScalingUnit':False,'scalingFactor':'autoFixed','noOfDecimal':1},
            'flexible':{'ibcsformat':False,'showScalingUnit':True,'scalingFactor':'auto','noOfDecimal':2},
            'custom':{'ibcsformat':False,'showScalingUnit':False,'scalingFactor':'none','noOfDecimal':2},
        }[mode]
        for key,value in derived.items():
            if key in patch and patch[key]!=value:
                raise ValueError(key+' conflicts with native number-format mode '+mode)
            update[key]=value
        scopes={'ibcs':('measure','cell','row'),'flexible':('measure',),'default':('cell','row'),'custom':()}[mode]
        formats=state.get('formatConfig',{})
        for scope in scopes:
            entries=formats.get(scope,{})
            if not isinstance(entries,dict):raise ValueError('Invalid formatConfig '+scope)
            cleaned={}
            for target,operations in entries.items():
                next_operations=[]
                for operation in operations:
                    fmt={k:v for k,v in operation.get('format',{}).items() if k!='13'}
                    if fmt:
                        item=copy.deepcopy(operation);item['format']=fmt;next_operations.append(item)
                if next_operations:cleaned[target]=next_operations
            formats[scope]=cleaned
    state[owner]=merge(state.get(owner,{}),update)

def audit(state, request):
    from .planning_integrity import check_styles
    check_styles(state)
    warnings=[]
    gs=state.get('globalStyles',{})
    if 'fontSize' in gs: require(isinstance(gs['fontSize'],str) and re.fullmatch(r'\d+(?:\.\d+)?',gs['fontSize']) and float(gs['fontSize'])>0,'Matrix global fontSize must be a numeric pixel string')
    if 'headerFontSize' in gs:require(isinstance(gs['headerFontSize'],str),'Header font size must be a string')
    for category,modes in request.get('columnStyles',{}).items():
        if set(modes)!={'read','edit'}:warnings.append('Only one mode requested for '+category+'; the other mode is preserved, not inherited.')
    forecasts={m['id'] for m in state.get('manage_measures',[]) if m.get('id') in request.get('forecastMeasureIds',[])}
    for mid in forecasts:
        if any(e.get('format',{}).get('5') not in (None,'','nofill') for e in state.get('formatConfig',{}).get('measure',{}).get(mid,[])):
            warnings.append('Direct background on Forecast '+mid+' can hide open/closed Column Styles; reconcile the specific operation explicitly.')
    if request.get('typography'):
        warnings.append('Inspect existing scoped/Column Style sizes and header-cell overrides; global typography does not override them.')
    if request.get('sizing',{}).get('measureWidths') or request.get('sizing',{}).get('columnWidths'):
        warnings.append('Existing uniform-width policy or a measure width may override the requested rendered-column width.')
    if state.get('themeColors',{}).get('enableRowHover')=='rowHover':
        warnings.append('Row hover can override input backgrounds and CF text with important CSS.')
    return warnings

def compile_formatting(state, request, resolved=None, ledger=None):
    """Return candidate + coverage; leaves the original unchanged on failure."""
    require(isinstance(state,dict) and 'manage_measures' in state,'Resolve a Planning/Matrix visualState first')
    from .planning_integrity import complete_styles
    out=complete_styles(state);ledger=copy.deepcopy(ledger or {});ids=identities(out,resolved or {})
    ids['labels']={m['id']:m.get('label',m['id']) for m in out['manage_measures']}
    coverage=[];translations=[]
    handlers={'typography':lambda x:translations.extend(typography(out,x)),
              'headers':lambda x:headers(out,x,ids),'columnStyles':lambda x:column_styles(out,x),
              'operations':lambda x:ordered_formats(out,x,ids,ledger),
              'rules':lambda x:merge_rules(out,x,ids,request.get('mirrorCompatibilityRules',True)),
              'sizing':lambda x:sizing(out,x,ids)}
    for owner in ('numberFormatting','gridStyles','themeColors'):
        handlers[owner]=lambda x,o=owner:simple_slice(out,o,x)
    for key,value in request.items():
        if key in ('mirrorCompatibilityRules','forecastMeasureIds'):continue
        if key not in handlers:
            coverage.append({'requirement':key,'status':'unsupported-or-unresolved','reason':'No safe Matrix writer for this request; no property invented.'});continue
        handlers[key](value)
        coverage.append({'requirement':key,'status':'supported-and-configured','rendering':'not-yet-verified'})
    for mid in request.get('forecastMeasureIds',[]):resolve(ids,'measure',mid)
    return {'state':out,'ledger':ledger,'coverage':coverage,'unitConversions':translations,
            'warnings':audit(out,request),'contract':SNAPSHOT['contractId'],'rendering':'not-yet-verified'}
