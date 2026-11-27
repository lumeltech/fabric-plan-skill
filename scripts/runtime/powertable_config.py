"""PowerTable lookup/source metadata construction and scoped local repair.

No network, SQL row changes, deployment, or validation of live reports.
"""
import copy
from .codec import unpack,parts,patch,sha
from .table_columns import apply_lookup

def resolved_source_meta(connection):
    """Names are resolved labels from the destination APIs, never template defaults."""
    fields={'connectionName':'connectionName','workspaceId':'workspaceId','workspaceName':'workspaceName',
            'databaseId':'artifactId','dbDisplayName':'dbDisplayName'}
    for key in fields.values():
        if not isinstance(connection.get(key),str) or not connection[key].strip():
            raise ValueError('Configured PowerTable requires resolved source metadata: '+key)
    return {dest:connection[src] for dest,src in fields.items()}

def enrich_source(source,connection,workspace,database):
    """Reconcile saved source with current GET connection/workspace/item records."""
    artifact=source['sqlTargetArtifact']
    for record,expected in ((connection,source['connectionId']),(workspace,artifact['workspaceId']),(database,artifact['artifactId'])):
        if not isinstance(record,dict) or record.get('id')!=expected:
            raise ValueError('Metadata record does not match the destination source binding')
        if not isinstance(record.get('displayName'),str) or not record['displayName'].strip():
            raise ValueError('Current metadata displayName required')
    if database.get('workspaceId',workspace['id'])!=workspace['id']:
        raise ValueError('Database metadata belongs to a different workspace')
    result=copy.deepcopy(source)
    if result.get('meta') is None:result['meta']={}
    if not isinstance(result.get('meta',{}),dict):raise ValueError('Source meta must be an object')
    result.setdefault('meta',{}).update(resolved_source_meta({
        'connectionName':connection['displayName'],'workspaceId':workspace['id'],'workspaceName':workspace['displayName'],
        'artifactId':database['id'],'dbDisplayName':database['displayName']}))
    return result

def backfill_row_access(envelope,*,sheet_guids=None):
    """Give enabled row actions without an audience the product default "All users".

    PowerTables saved without a row-access filter show no selection on the Row
    access tab. Only enabled ROW_ADD/ROW_UPDATE/ROW_DELETE settings with no
    filters change; existing selections and disabled actions are untouched.
    """
    from .construct import guid
    raw=unpack(envelope);original=parts(envelope)
    sheets=[s for s in raw['definition.json']['sheets'] if s.get('sheetType')=='POWERTABLE']
    if sheet_guids is not None:
        if not isinstance(sheet_guids,list) or not set(sheet_guids)<={s['recordGuid'] for s in sheets}:
            raise ValueError('Select current PowerTable sheet GUIDs')
        sheets=[s for s in sheets if s['recordGuid'] in sheet_guids]
    changes={};filled=[]
    for sheet in sheets:
        for visual in sheet.get('workloadItemEntityVisuals',[]):
            path=f"sheets/{sheet['recordGuid']}/visuals/{visual.get('visualId')}/sourceSettings.json"
            if visual.get('visualType')!='POWERTABLE' or visual.get('isEmbedded') or path not in raw:continue
            settings=copy.deepcopy(raw[path])
            for setting in settings.get('sourceSettings',[]):
                if setting.get('name') in ('ROW_ADD','ROW_UPDATE','ROW_DELETE') and setting.get('settings',{}).get('enabled') is True and not setting.get('filters'):
                    setting['filters']=[{'recordGuid':guid(),'name':'all_users','filterType':1,'filter':{}}]
                    filled.append({'sheetGuid':sheet['recordGuid'],'setting':setting['name']})
            if settings!=raw[path]:changes[path]=settings
    from .powertable_features import automation_identity_warnings
    candidate=patch(envelope,changes,{p:sha(original[p]) for p in changes}) if changes else copy.deepcopy(envelope)
    return candidate,{'filled':filled,'changedParts':sorted(changes),'preservedPartCount':len(original)-len(changes),
        'rowAccess':'All users for enabled actions that had no selection','warnings':automation_identity_warnings(raw),
        'deployment':'not run','runtimeValidation':'not run'}

def repair_definition(envelope,*,sheet_guid,lookups,lookup_catalog,source_metadata):
    """Prepare at most two changed parts. Preserve all unrelated encoded bytes."""
    raw=unpack(envelope);original=parts(envelope)
    sheets=[s for s in raw['definition.json']['sheets'] if s['recordGuid']==sheet_guid and s['sheetType']=='POWERTABLE']
    if len(sheets)!=1:raise ValueError('Select one current PowerTable sheet GUID')
    sheet=sheets[0]
    owned=[v for v in sheet['workloadItemEntityVisuals'] if v.get('visualType')=='POWERTABLE' and not v.get('isEmbedded',False)]
    if len(owned)!=1:raise ValueError('One directly owned PowerTable visual required')
    prefixes={p.rsplit('/',1)[0]+'/' for p in raw if p.startswith('sheets/'+sheet_guid+'/visuals/') and p.endswith('/source.json')}
    if len(prefixes)!=1:raise ValueError('Ambiguous PowerTable source parts')
    prefix=next(iter(prefixes))
    if prefix.rstrip('/').rsplit('/',1)[-1].casefold()!=owned[0]['visualId'].casefold():
        raise ValueError('PowerTable source visual owner mismatch')
    col_path,source_path=prefix+'columnConfigs.json',prefix+'source.json'
    columns=copy.deepcopy(raw[col_path]);source=copy.deepcopy(raw[source_path])
    names=[c['columnName'] for c in columns['columnConfigs']]
    if len(names)!=len(set(names)) or not isinstance(lookups,dict) or not set(lookups)<=set(names):
        raise ValueError('Lookup columns must resolve uniquely in this sheet')
    columns['columnConfigs']=[apply_lookup(c,lookups[c['columnName']],lookup_catalog) if c['columnName'] in lookups else c
                              for c in columns['columnConfigs']]
    source['source']=enrich_source(source['source'],**source_metadata)
    changes={p:v for p,v in ((col_path,columns),(source_path,source)) if raw[p]!=v}
    candidate=patch(envelope,changes,{p:sha(original[p]) for p in changes})
    return candidate,{'sheetGuid':sheet_guid,'lookupColumns':list(lookups),'changedParts':list(changes),
        'preservedPartCount':len(original)-len(changes),'columnEditability':'preserved','rowActions':'preserved',
        'sourceBindings':'preserved','deployment':'not run','runtimeValidation':'not run'}
