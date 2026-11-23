"""Dashboard visibility through public Plan definition operations."""
import uuid

def visibility(client,workspace,plan,sheet_guid,visible,label):
    from .codec import unpack,parts,patch,sha,definition_hash
    from .transport import plan_operation
    if not isinstance(visible,bool): raise ValueError('Visibility must be Boolean')
    current=plan_operation(client,workspace,'export',plan,label=label+'-export-'+uuid.uuid4().hex)['body']
    root=unpack(current)['definition.json'];matches=[s for s in root['sheets'] if s['recordGuid']==sheet_guid]
    if len(matches)!=1: raise ValueError('Missing or duplicate staged dashboard')
    if matches[0].get('isHidden') is (not visible): return {'visible':visible,'write':'already-matched'}
    matches[0]['isHidden']=not visible
    envelope=patch(current,{'definition.json':root},{'definition.json':sha(parts(current)['definition.json'])})
    plan_operation(client,workspace,'update',plan,definition=envelope,label=label,baseline_hash=definition_hash(current))
    check=plan_operation(client,workspace,'export',plan,label=label+'-verify-'+uuid.uuid4().hex)['body']
    actual=next(s for s in unpack(check)['definition.json']['sheets'] if s['recordGuid']==sheet_guid)
    if actual.get('isHidden') is not (not visible): raise ValueError('Dashboard visibility readback mismatch')
    return {'visible':visible,'write':'saved'}
