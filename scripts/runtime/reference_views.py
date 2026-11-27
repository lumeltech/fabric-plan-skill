"""Inspect portable saved view relationships without cloning or claiming restore."""
import copy

def audit(raw,*,home_roles=None,home_contents=None):
    sheets=raw['definition.json']['sheets'];pages={s['recordGuid']:s for s in sheets}
    if len(pages)!=len(sheets):raise ValueError('Duplicate page identity')
    owners={};members={};states={};result={'bookmarks':[],'dashboards':[],'parameters':[],
        'powerTables':[],'warnings':[],'runtime':'not-tested'}
    for s in sheets:
        sid=s['recordGuid'];members[sid]={v['visualId'] for v in s['workloadItemEntityVisuals']}
        for v in s['workloadItemEntityVisuals']:
            if v.get('isEmbedded'):continue
            vid=v['visualId'];prefix=f'sheets/{sid}/visuals/{vid}/'
            if vid in owners:raise ValueError('Multiple direct visual owners')
            owners[vid]=sid;states[vid]=raw[prefix+'properties.json']['properties']
            if v['visualType']=='POWERTABLE':
                source=raw.get(prefix+'source.json',{}).get('source',{})
                configs=raw.get(prefix+'columnConfigs.json',{}).get('columnConfigs',[])
                result['powerTables'].append({'page':s['displayName'],'visualId':vid,
                    'table':source.get('tableName'),'schema':source.get('schemaName'),
                    'connectionId':source.get('connectionId'),'creationMode':source.get('creationMode'),
                    'sourceRecordGuid':source.get('recordGuid'),'columnConfigurationPresent':bool(configs),
                    'configuredColumns':len(configs),'primaryKeys':[c['columnName'] for c in configs if c.get('columnMeta',{}).get('isPrimaryKey') is True],
                    'writeback':'not-tested'})
    for s in sheets:
        sid=s['recordGuid'];sp=raw.get(f'sheets/{sid}/sheet.json',{}).get('properties',{})
        # Sheet metadata wraps the properties object in the current ALM profile.
        sp=sp.get('properties',sp)
        variables=sp.get('entityLevelVariables',[])
        for p in variables:result['parameters'].append({'page':s['displayName'],'pageId':sid,'id':p['id'],
            'type':p.get('type'),'scope':p.get('scope'),'technicalName':p.get('technicalName'),'value':p.get('value')})
        embeds=[];navs=[]
        for v in s['workloadItemEntityVisuals']:
            vid=v['visualId']
            if vid not in owners:raise ValueError('Unresolved visual owner: '+vid)
            if v.get('isEmbedded'):embeds.append({'visualId':vid,'ownerPage':pages[owners[vid]]['displayName']})
            n=states[vid].get('visualState',{}).get('navigatorState')
            if n:navs.append({'visualId':vid,'kind':n.get('type'),'hidden':states[vid].get('layerProperties',{}).get('isHidden',False)})
        if s['sheetType']=='REPORTING':result['dashboards'].append({'page':s['displayName'],'pageId':sid,'navigators':navs,'embeddedOwners':embeds})
    bookmarks=raw['planProperties.json']['properties'].get('bookmarks',[]);slugs=set()
    for b in bookmarks:
        slug=b['bookmarkSlug'];meta=b['cloudMeta']['bookmarkMeta'];snaps=b['cloudMeta']['bookmarkVisualMeta'];page=meta.get('activePageId')
        if slug in slugs or meta.get('bookmarkSlug')!=slug:raise ValueError('Duplicate or inconsistent bookmark slug')
        slugs.add(slug)
        if page not in pages or not set(snaps)<=members[page]:raise ValueError('Bookmark page or captured visual is unresolved')
        if not set(meta.get('activeSelection',[]))<=members[page]:raise ValueError('Bookmark selection is not on its captured page')
        current={p['id'] for p in result['parameters'] if p['pageId']==page}
        captured={p['id'] for p in meta.get('entityLevelVariables',[])}
        missing=current-captured
        if missing:result['warnings'].append({'bookmark':b['name'],'kind':'current-parameters-not-captured','parameterIds':sorted(missing)})
        result['bookmarks'].append({'name':b['name'],'slug':slug,'page':pages[page]['displayName'],
            'order':meta.get('bookmarkOrder'),'config':copy.deepcopy(meta.get('bookmarkConfig',{})),
            'capturedVisuals':len(snaps),'currentVisualsNotCaptured':sorted(members[page]-set(snaps)),
            'entityParametersCaptured':sorted(captured),'restore':'not-tested'})
    pp=raw['planProperties.json']['properties'];roles=home_roles or {};content=home_contents or {}
    result['home']={'exportedRoles':len(pp.get('homeLayout',{}).get('roles',[])),
        'exportedShow':pp.get('homeLayout',{}).get('show'),
        'roleMetadataRead':home_roles is not None,'roles':[]}
    for role,metadata in roles.items():
        data=content.get(role,{}).get('data')
        result['home']['roles'].append({'roleId':role,'enabled':metadata.get('homeLayoutEnabled'),
            'contentRead':role in content,'items':len(data.get('items',[])) if isinstance(data,dict) else None,
            'rows':len(data.get('rows',[])) if isinstance(data,dict) else None})
    return result

def audit_native_capture(capture,page):
    """Check runtime IDs before native upsert; exported label-only snapshots differ."""
    visuals={str(v['id']):v for v in page['payload']['visuals']}
    snaps=capture['bookmarkVisualMeta']
    if not snaps or not set(snaps)<=set(visuals):raise ValueError('Capture visual is not a current page member')
    for vid,s in snaps.items():
        current=visuals[vid]['properties']['properties'].get('visualState',{})
        known={m['id'] for m in current.get('manage_measures',[]) if 'id' in m}
        for m in s.get('manage_measures',[]) or []:
            if m.get('id') not in known:raise ValueError('Use current native measure IDs, not portable label-only entries')
    return {'capturedVisuals':len(snaps),'currentVisualsNotCaptured':sorted(set(visuals)-set(snaps)),
            'identityCheck':'passed','restore':'not-tested'}
