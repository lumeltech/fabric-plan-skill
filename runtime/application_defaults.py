"""Required presentation baseline for every new Fabric Plan application."""
import copy

def embedded_planning_owners(sheets):
    """Find original Planning sheets by the grid IDs embedded on visible dashboards."""
    embedded = {
        visual['visualId']
        for sheet in sheets if sheet['sheetType'] == 'REPORTING' and not sheet.get('isHidden')
        for visual in sheet.get('workloadItemEntityVisuals', [])
        if visual.get('isEmbedded') and visual.get('visualType') == 'PLANNING'
    }
    return {
        sheet['recordGuid']
        for sheet in sheets if sheet['sheetType'] == 'PLANNING'
        if any(visual.get('visualType') == 'PLANNING' and not visual.get('isEmbedded')
               and visual['visualId'] in embedded for visual in sheet.get('workloadItemEntityVisuals', []))
    }

def require_business_navigation(raw):
    """Underlying Planning pages stay hidden; maintenance remains accessible.

    Reporting pages are visible in the new Plan definition.
    This concerns navigation, not authorization or row-level security.
    """
    owners=[]
    sheets = raw['definition.json']['sheets']
    embedded = embedded_planning_owners(sheets)
    for sheet in sheets:
        if sheet['sheetType']=='PLANNING' and sheet['recordGuid'] in embedded:
            if sheet.get('isHidden') is not True:
                raise ValueError('Underlying Planning sheet must be hidden: '+sheet['displayName'])
            owners.append(sheet['recordGuid'])
        elif sheet['sheetType']=='REPORTING' and sheet.get('isHidden') is not False:
            raise ValueError('Business dashboard must be visible in the public create definition: '+sheet['displayName'])
        elif sheet['sheetType']=='POWERTABLE' and sheet.get('isHidden') is not False:
            raise ValueError('Business PowerTable must be visible: '+sheet['displayName'])
    return owners

def public_home_layout(layout,planning_map):
    """Exclude resolved owner pages from Home cards without copying runtime IDs."""
    out=copy.deepcopy(layout);ids=[]
    for owner in planning_map.values():
        eid=owner.get('entityId')
        if not isinstance(eid,str) or not eid.isdecimal():
            raise ValueError('Resolved native Planning owner entity ID required for Home navigation')
        ids.append(eid)
    for item in out.get('items',[]):
        if item.get('type')!='preview-cards':continue
        cards=item['instanceState']['previewCards']
        cards['unSelectedEntityIds']=list(dict.fromkeys(cards.get('unSelectedEntityIds',[])+ids))
    return out


def home_layout_for_sheets(client,layout,raw,owners):
    """Exclude source sheets from Home preview cards using dashboard placement identities."""
    if not any(item.get('type')=='preview-cards' for item in layout.get('items',[])):
        return copy.deepcopy(layout)
    sheets=raw['definition.json']['sheets']
    hidden={s['recordGuid'] for s in sheets if s['sheetType']=='PLANNING' and s.get('isHidden')}
    by_sheet={o['sheetGuid']:o for o in owners if o.get('sheetGuid') in hidden}
    return public_home_layout(layout,by_sheet)

def require_dashboard_navigators(raw):
    """Require a visible native Page Navigator on each declared Intelligence page.

    Orphan parts, a button, bookmark tabs and a hidden layer do not provide page
    navigation. This construction check does not establish rendered behavior.
    """
    from .layout import rect,overlap
    from .navigator_defaults import require_complete_defaults
    covered=[]
    for sheet in raw['definition.json']['sheets']:
        if sheet['sheetType']!='REPORTING':continue
        sid=sheet['recordGuid'];candidates=[]
        for member in sheet['workloadItemEntityVisuals']:
            if member.get('isEmbedded') or member.get('visualType')!='BI_RUNTIME_INPUT':continue
            p=raw.get(f'sheets/{sid}/visuals/{member["visualId"]}/properties.json',{}).get('properties',{})
            nav=p.get('visualState',{}).get('navigatorState',{})
            if p.get('visualType')!=203 or nav.get('type')!='PAGE_NAVIGATOR_TABS':continue
            layer=p.get('layerProperties',{}).get('layerProperties',{})
            tabs=nav.get('navigatorTabsState',{})
            if layer.get('isHidden') is not False:continue
            # New application defaults include every normal visible page without
            # nonportable selected-ID restrictions. Hidden/tooltip pages stay out.
            if 'selectedPages' in tabs or tabs.get('destinationType')!={'all':True,'hidden':False,'tooltip':False}:continue
            require_complete_defaults(nav)
            r=rect(p)
            canvas=raw[f'sheets/{sid}/sheet.json']['properties']['canvasStyle']['dimension']
            if r['x']<0 or r['y']<0 or r['x']+r['width']>canvas['width'] or r['y']+r['height']>canvas['height']:
                raise ValueError('Required Page Navigator is outside the dashboard canvas: '+sheet['displayName'])
            for other in sheet['workloadItemEntityVisuals']:
                if other==member or other.get('isEmbedded'):continue
                props=raw[f'sheets/{sid}/visuals/{other["visualId"]}/properties.json']['properties']
                if props.get('layerProperties',{}).get('layerProperties',{}).get('isHidden') is True:continue
                if overlap(r,rect(props)):
                    raise ValueError('Required Page Navigator overlaps another dashboard visual: '+sheet['displayName'])
            candidates.append(member['visualId'])
        if not candidates:
            raise ValueError('Required visible Page Navigator with all visible pages is missing: '+sheet['displayName'])
        covered.append(sid)
    return covered

def home_defaults(spec):
    out=copy.deepcopy(spec);home=out.setdefault('home',{})
    if home.get('show') is False:raise ValueError('Required Home landing page cannot be hidden')
    home.update(show=True);home.setdefault('roleId','__everyone__');home.setdefault('order',1)
    blocks=home.setdefault('blocks',[]);rows=home.setdefault('rows',[])
    keys={b['key'] for b in blocks}
    def add(key,typ,title='',description=''):
        base=key;n=2
        while key in keys:key=base+'-'+str(n);n+=1
        keys.add(key);blocks.append({'key':key,'type':typ,'title':title,'description':description})
        rows.append({'blocks':[key]})
    if not any(b['type']=='text' for b in blocks):
        add('application-overview','text',out['name'],'Use the Intelligence dashboards to select the relevant scope, review charts and work in the embedded planning sheets. '+
            'Planning workspaces: '+', '.join(s['name'] for s in out['sheets'])+'.')
    if not any(b['type']=='preview-cards' for b in blocks):add('available-sheets','preview-cards')
    # Preserve explicitly authored blocks and layout. Fill only orphaned new blocks.
    placed={k for r in rows for k in r['blocks']}
    for b in blocks:
        if b['key'] not in placed:rows.append({'blocks':[b['key']]})
    return out

def check_application_defaults(raw,home_layout):
    from .planning_presentation import check_application,measure_roles,PALETTE
    from .home_fit import assert_home_fit
    result=check_application(raw)
    hidden_owners=require_business_navigation(raw)
    navigation=require_dashboard_navigators(raw)
    if raw['planProperties.json'].get('properties',{}).get('homeLayout',{}).get('show') is not True:
        raise ValueError('Required Home visibility is missing')
    if not home_layout or not {'text','preview-cards'}<={i['type'] for i in home_layout.get('items',[])}:
        raise ValueError('Required Home description and available-sheet cards are missing')
    assert_home_fit(home_layout)
    count=0
    for s in raw['definition.json']['sheets']:
        if s['sheetType']!='PLANNING':continue
        for v in s['workloadItemEntityVisuals']:
            if v.get('isEmbedded'):continue
            stem=f'sheets/{s["recordGuid"]}/visuals/{v["visualId"]}/'
            p=raw[stem+'properties.json']['properties'];vs=p['visualState']
            elements=vs.get('chartCustomTitle',{}).get('customTitle',{}).get('elements',[])
            if not vs.get('showHeaderFooter') or not any(e.get('type')=='TEXT' and '<' in e.get('content','') for e in elements):
                raise ValueError('Required rich Planning description is missing: '+s['displayName'])
            if any('[fields]' in e.get('content','') for e in elements):raise ValueError('Automatic field inventory is not a business description')
            roles=measure_roles(p,raw[stem+'dataInput.json']['columns'])
            for mid,info in roles.items():
                entries=vs.get('formatConfig',{}).get('measure',{}).get(mid,[])
                colors=[e['format']['3'] for e in sorted(entries,key=lambda x:x.get('order',0)) if '3' in e.get('format',{})]
                if not colors or colors[-1].lower()!=PALETTE[info['role']]['text'].lower():
                    raise ValueError('Required source-role text color is missing: '+info['label'])
            count+=1
    from .application_typography import require_arial
    typography=require_arial(raw,home_layout)
    from .navigator_defaults import require_complete_defaults
    navigators=0
    for name,obj in raw.items():
        if not name.endswith('/properties.json'):continue
        vs=obj.get('properties',{}).get('visualState',{})
        if 'navigatorState' in vs:
            require_complete_defaults(vs['navigatorState']);navigators+=1
    return {**result,'hiddenPlanningOwners':len(hidden_owners),'typography':typography,'navigatorDefaultsChecked':navigators,'dashboardsWithPageNavigator':len(navigation),'richPlanningHeaders':count,'measureRoleColors':'passed','homeContent':'passed',
        'homeVisibility':'passed','validation':'static-definition','rendering':'not-tested'}

def require_delivery_phases(authored, *, home_visible, dashboard_geometry, dashboard_visibility):
    """Check the authored baseline and the public definition delivery phases.

    This is not a runtime/UI test. A skipped validation request never skips these
    construction and save phases. Component-only builds cannot pass this gate.
    """
    baseline=check_application_defaults(authored['raw'],authored.get('home'))
    from .authoring_flow import require_authored_flow
    contents=require_authored_flow(authored)
    expected={d['sheetGuid'] for d in authored.get('dashboardIdentities',[])}
    declared={s['recordGuid'] for s in authored['raw']['definition.json']['sheets'] if s['sheetType']=='REPORTING'}
    if not expected or expected!=declared:raise ValueError('Incomplete application dashboard delivery identities')
    if home_visible is not True:
        raise ValueError('Incomplete application: Home visibility must be enabled in the public definition')
    if not expected<=set(dashboard_geometry) or not expected<=set(dashboard_visibility):
        raise ValueError('Incomplete application: each dashboard needs saved geometry and a visible declaration in the public create payload')
    return {'mandatoryDefaults':'passed','baseline':baseline,'importContract':contents,'roleSpecificHome':'not-published',
            'dashboardSaves':len(expected),'runtimeValidation':'not-run'}
