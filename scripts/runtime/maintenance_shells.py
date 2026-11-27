"""Add unconnected native PowerTable sheets without fake sources or database writes.

A blank PowerTable owns no visual until source initialization. Do not use this
constructor to clear or replace an existing connected sheet.
"""
import copy,uuid
from .construct import guid,sheet_properties
from .codec import parts,unpack,patch,pack,sha

def blank_powertable(name,order,*,sheet_guid=None,table=None):
    if not isinstance(name,str) or not name.strip():raise ValueError('Sheet name required')
    if isinstance(order,bool) or not isinstance(order,(int,float)) or order<0:raise ValueError('Nonnegative order required')
    sid=sheet_guid or guid();uuid.UUID(sid)
    sheet={'recordGuid':sid,'displayName':name.strip(),'sheetType':'POWERTABLE','isHidden':False,'order':order,'workloadItemEntityVisuals':[]}
    raw={f'sheets/{sid}/sheet.json':sheet_properties()}
    manifest={'sheetGuid':sid,'displayName':sheet['displayName'],'status':'connection-required',
      'constructionState':'sheet-only-uninitialized','expectedScreen':'PowerTable welcome/setup screen',
      'configuredPowerTable':False,
      'intendedTable':table,'nativeSourceCreated':False,'dataAccessTested':False,
      'pending':['Select an authorized connection and existing table','Inspect columns and keys','Configure requested lookups and edit rules','Verify save and reopen']}
    return sheet,raw,manifest

def add_deferred_powertables(envelope,requests):
    raw=unpack(envelope);root=copy.deepcopy(raw['definition.json']);existing=root['sheets']
    names={s['displayName'].casefold() for s in existing};ids={s['recordGuid'] for s in existing};added={};manifest=[]
    order=max((s.get('order',0) for s in existing),default=-1)+1
    for req in requests:
        if req['name'].strip().casefold() in names:raise ValueError('Existing sheet name; reconcile without replacing its binding')
        sheet,new,entry=blank_powertable(req['name'],order,sheet_guid=req.get('sheetGuid'),table=req.get('table'))
        if sheet['recordGuid'] in ids:raise ValueError('Existing or duplicate sheet identity')
        if set(new)&(set(raw)|set(added)):raise ValueError('Part collision')
        existing.append(sheet);added.update(new);manifest.append(entry);names.add(sheet['displayName'].casefold());ids.add(sheet['recordGuid']);order+=1
    if not manifest:raise ValueError('No requested maintenance sheets')
    out=patch(envelope,{'definition.json':root},{'definition.json':sha(parts(envelope)['definition.json'])})
    out.get('definition',out)['parts'].extend(pack(added)['definition']['parts'])
    for k,b in parts(envelope).items():
        if k!='definition.json':assert parts(out)[k]==b,'Unrelated part changed'
    return out,manifest
