"""Planning descriptions, semantic measure colors and rich application defaults.

Only documented Matrix text/format and Intelligence constructors are used.
No values, formulas, input permissions, storage IDs or selection policies change.
"""
import copy,html,math,re
from .planning_integrity import complete_styles
from .header_sizing import fit_header

PALETTE={'input':{'text':'#8A5700','tint':'#FFF4D6','label':'Input / Forecast'},
         'formula':{'text':'#6B3FA0','tint':'#F2EAFB','label':'Formula'},
         'powerbi':{'text':'#1F5AA6','tint':'#EAF2FC','label':'Power BI'},
         'linked':{'text':'#176B62','tint':'#E7F4F1','label':'From Sheets'}}

def measure_roles(properties,records):
    by_id={str(c['measureGuid']):c for c in records}
    assignments={str(a.get('measureGuid')):a for a in properties.get('pivotAssignments',[]) if a.get('dataRoleType')=='Measure'}
    result={}
    for m in properties['visualState']['manage_measures']:
        key=str(m['id']);a=assignments.get(key,{});record=by_id.get(key,{})
        mt=record.get('columnMeta',{}).get('measure_type',{})
        if 'VisualColumn' in mt:mt=mt['VisualColumn']
        if a.get('sourceType') in ('Visual','InfoBridge'):role='linked'
        elif a.get('sourceType')=='PowerBI':role='powerbi'
        elif 'Formula' in mt:role='formula'
        elif 'DataInput' in mt or 'Forecast' in mt:role='input'
        elif 'Native' in mt:role='powerbi'
        else:raise ValueError('Resolve actual measure kind before color coding: '+m.get('label',key))
        result[key]={'role':role,'label':m.get('label',record.get('name',key))}
    return result

def legend_html(roles,palette=PALETTE):
    used={r['role'] for r in roles.values()}
    return ' &nbsp; '.join('<span style="font-family:Arial;color:'+palette[k]['text']+';font-weight:bold">'+html.escape(palette[k]['label'])+'</span>' for k in palette if k in used)

def header_properties(properties,title,description,roles,palette=PALETTE):
    if not title.strip() or not description.strip():raise ValueError('A sheet-specific business title and description are required')
    out=copy.deepcopy(properties);vs=out['visualState']
    width=float(out.get('dimension',{}).get('width',1552))
    if not math.isfinite(width) or width<=32:raise ValueError('Resolve current header width')
    # Placeholder geometry is replaced below using actual text/font wrapping.
    height=10
    ct=copy.deepcopy(vs.get('chartCustomTitle') or {})
    canvas=copy.deepcopy(ct.get('customTitle') or {})
    elements=canvas.get('elements',[])
    existing=next((e for e in elements if e.get('type') in ('TEXT','DEFAULT_TITLE')),None)
    element=copy.deepcopy(existing or {});eid=element.get('id') or 'planning-description'
    element.update(type='TEXT',id=eid,position={'top':0,'left':0},dimension={'width':str(int(width)),'height':str(height)},
        layout={'x':0,'y':0,'w':64,'h':height//10,'i':eid,'static':False},
        # The product's title CSS forces paragraph margins to 0 and can override a paragraph's
        # font-size, so sizes go on spans as in the product's own header presets.
        content='<div style="font-family:Arial;color:#24364B"><p style="font-family:Arial"><span style="font-family:Arial;font-size:22px"><strong style="font-family:Arial">'+html.escape(title)+'</strong></span></p><p style="font-family:Arial"><span style="font-family:Arial;font-size:14px">'+html.escape(description)+'</span></p><p style="font-family:Arial"><span style="font-family:Arial;font-size:13px">'+legend_html(roles,palette)+'<span style="font-family:Arial;color:#526070"> &nbsp; Editability follows period and lock rules.</span></span></p></div>',
        align='left',verticalAlign='TOP')
    # This writer replaces the description canvas explicitly. Existing siblings
    # in chartCustomTitle survive; callers must not invoke it for a styling-only edit.
    canvas.update(elements=[element],layout=eid,layoutType='CUSTOM',containerPosition='top',containerMeta={**canvas.get('containerMeta',{}),'width':int(width),'height':height})
    ct['customTitle']=canvas;vs['chartCustomTitle']=ct;vs['showHeaderFooter']=True
    return fit_header(out)['properties']

def apply_presentation(properties,records,title,description,*,palette=None,override_colors=False):
    from .matrix_formatting import compile_formatting
    colors=copy.deepcopy(palette or PALETTE)
    for k in PALETTE:
        if k not in colors or not all(isinstance(colors[k].get(p),str) for p in ('text','tint','label')):raise ValueError('Incomplete semantic palette')
        if any(not re.fullmatch(r'#[0-9a-fA-F]{6}',colors[k][p]) for p in ('text','tint')):raise ValueError('Use explicit hex palette colors')
    out=copy.deepcopy(properties);out['visualState']=complete_styles(out['visualState'])
    roles=measure_roles(out,records);operations=[]
    fc=out['visualState'].get('formatConfig',{}).get('measure',{})
    for mid,info in roles.items():
        # Text-only coding preserves open/closed fills, locked cells and CF meaning.
        # Default construction respects explicit text colors. The user's explicit
        # recolor request can override them without removing earlier operations.
        present=any('3' in e.get('format',{}) for e in fc.get(mid,[]))
        if override_colors or not present:
            operations.append({'key':'measure-role-'+mid,'scope':'measure','id':mid,'format':{'textColor':colors[info['role']]['text']}})
    result=compile_formatting(out['visualState'],{'operations':operations})
    out['visualState']=result['state'];out=header_properties(out,title,description,roles,colors)
    return {'properties':out,'roles':roles,'palette':colors,'formatLedger':result['ledger'],'runtime':'not-run'}

def default_description(sheet):
    if sheet.get('header'):return sheet['header']
    kinds={m['kind'] for m in sheet['measures']}
    text='Review '+sheet['name'].strip()+'. '
    if kinds & {'DataInput','Forecast'}:text+='Adjust eligible planning inputs and compare them with the available source measures. '
    else:text+='Review the available source measures and calculated results. '
    if 'Formula' in kinds:text+='Formula measures show calculated outcomes. '
    return text+'Use the dashboard selections to focus the planning grid.'

def application_defaults(model,spec):
    """Normal app entrypoint: one rich Intelligence workspace per Planning owner.

    Missing source contracts are explicit failures, never synthetic chart data.
    Explicitly supplied dashboards/controls are retained and missing requirements
    are filled. Low-level build remains available for component composition.
    """
    from .application_defaults import home_defaults
    out=home_defaults(spec);pages=out.setdefault('dashboards',[])
    names={s['name'] for s in out['sheets']}|{d['name'] for d in pages}
    for sheet in out['sheets']:
        # Business users enter through the dashboard's embedded owner visual.
        # Keep the owner and its data intact, but remove its standalone page.
        sheet['hidden']=True
        sheet['header']=default_description(sheet)
        assigned=sheet.get('columns',[])+sheet.get('rows',[])
        context={x['field'] for x in sheet.get('context',[])}
        fields=[k for k in dict.fromkeys(assigned) if k not in context]
        numeric={f['id']:f for f in model['fields'] if f['dataType'] in ('Double','Decimal','Int64') and f['columnType'] in ('Measure','Column')}
        sources=[m for m in sheet['measures'] if m['kind']=='Native' and m['source'] in numeric]
        source=next((m for m in sources if numeric[m['source']]['columnType']=='Measure'),None)
        if source is None and sources:source=sources[0]
        # Prefer separate business dimensions for useful comparisons; no arbitrary
        # measure totals or copied historical selections are synthesized.
        categories=list(dict.fromkeys((sheet.get('rows',[]) or fields)[:2]))
        matches=[d for d in pages if d['owner']==sheet['name']]
        if source is None:
            # A user-selected semantic KPI is also an explicit, meaningful source.
            for page in matches:
                for card in page.get('cards',[]):
                    if card['field'] in numeric:
                        source={'source':card['field'],'label':card['label'],'sourceAggregation':card.get('aggregation')};break
                if source:break
        if not fields or (source is None and (not matches or any(not d.get('charts') for d in matches))):
            raise ValueError('Rich dashboard requires real dimension and numeric source measure; resolve supported chart bindings for '+sheet['name'])
        if not matches:
            name=sheet['name']+' Dashboard';base=name;n=2
            while name in names:name=base+' '+str(n);n+=1
            names.add(name);page={'name':name,'owner':sheet['name'],'title':sheet['name'],'description':sheet['header'],'slicers':[],'cards':[],'charts':[]}
            pages.append(page);matches=[page]
        # A Matrix page shows a table instead of the embedded grid. When no page
        # embeds this owner, its own Planning page stays visible for input.
        sheet['hidden']=any('table' not in page for page in matches)
        for page in matches:
            page.setdefault('title',sheet['name']);page.setdefault('description',sheet['header']);page.setdefault('cards',[])
            if not page.get('slicers'):page['slicers']=[{'field':k} for k in fields[:4]]
            if not page.get('charts'):
                aggregation=({'aggregation':source.get('sourceAggregation') or 'sum'} if numeric[source['source']]['columnType']=='Column' else {})
                page['charts']=[{'category':k,'field':source['source'],'label':source['label']+' by '+k.split('[',1)[1][:-1],**aggregation} for k in categories]
    return out

def build_application(model,spec,registry=None):
    from .construct import build
    from .workflow import compile_home
    from .codec import pack
    from .application_defaults import check_application_defaults
    prepared=application_defaults(model,spec)
    result=build(model,prepared,registry)
    result['home']=compile_home(prepared['home'])
    result['homeSpec']=prepared['home']
    result['raw']['planProperties.json']['properties'].setdefault('homeLayout',{})['show']=True
    result['envelope']=pack(result['raw'])
    result['presentationCheck']=check_application(result['raw'])
    result['defaultsCheck']=check_application_defaults(result['raw'],result['home'])
    from .authoring_flow import require_import_contract
    result['buildRequest']=copy.deepcopy(spec)
    result['importContract']=require_import_contract(spec,result)
    return result

def check_application(raw):
    root=raw['definition.json'];sheets=root['sheets'];covered=set();matrix_pages=0
    for sheet in sheets:
        if sheet['sheetType']!='REPORTING':continue
        vs=sheet['workloadItemEntityVisuals'];types={v['visualType'] for v in vs if not v.get('isEmbedded')}
        charts=[]
        for v in vs:
            # A tree in a chart slot counts as the page's chart.
            if v.get('isEmbedded') or v['visualType'] not in ('ANALYTICS_PLUS','TREE'):continue
            p=raw[f'sheets/{sheet["recordGuid"]}/visuals/{v["visualId"]}/properties.json']['properties']
            if p.get('chartType',p.get('visualState',{}).get('chartType'))!='CARD' and any(a.get('dataRoleType')=='Grouping' for a in p.get('pivotAssignments',[])):
                charts.append(v)
        if {'BI_TEXT','SUPER_FILTER'}<=types and charts:
            matrix_pages+='INFORIVER' in types
            for v in vs:
                if v.get('isEmbedded') and v['visualType']=='PLANNING':covered.add(v['visualId'])
    owned={v['visualId'] for s in sheets if s['sheetType']=='PLANNING' for v in s['workloadItemEntityVisuals'] if not v.get('isEmbedded')}
    # An owner reviewed on a Matrix page keeps its own visible page for input.
    visible={v['visualId'] for s in sheets if s['sheetType']=='PLANNING' and not s.get('isHidden') for v in s['workloadItemEntityVisuals'] if not v.get('isEmbedded')}
    uncovered=owned-covered
    if uncovered and (not matrix_pages or not uncovered<=visible):raise ValueError('Planning owners missing rich Intelligence dashboard: '+', '.join(sorted(uncovered)))
    return {'planningOwners':len(owned),'coveredByRichDashboard':len(owned&covered),'inputOnVisiblePlanningPage':len(uncovered),'runtime':'not-run'}
