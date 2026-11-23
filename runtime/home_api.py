"""Offline layout decoding and Home visibility through public Plan definitions."""
import os,subprocess,copy,uuid,urllib.parse
from pathlib import Path
from .codec import loads,unpack,patch,parts,sha,definition_hash
from .transport import plan_operation

def decode_roles(payload,node=None):
    if isinstance(payload,dict): return payload
    if not isinstance(payload,str): raise ValueError('Unknown Home metadata encoding')
    node=node or os.environ.get('FABRIC_PLAN_HTTP_NODE') or os.environ.get('FABRIC_PLAN_NODE')
    if not node: raise ValueError('Set FABRIC_PLAN_NODE for bundled LZUTF8 decoder')
    result=subprocess.run([node,str(Path(__file__).resolve().parents[1]/'tools/decode-lzutf8.cjs')],
        input=payload,text=True,encoding='utf-8',capture_output=True,timeout=30)
    if result.returncode: raise ValueError('Invalid Home metadata compression')
    out=loads(result.stdout)
    if not isinstance(out,dict): raise ValueError('Home metadata must be object')
    return out

def visibility_via_alm(client,workspace,plan,show,label):
    """Fresh-export scoped mutation. ALM has no documented server CAS guarantee."""
    if not isinstance(show,bool): raise ValueError('Home visibility must be Boolean')
    before=plan_operation(client,workspace,'export',plan,label=label+'-before-'+uuid.uuid4().hex)['body']
    raw=unpack(before); name='planProperties.json'; props=copy.deepcopy(raw[name])
    props.setdefault('properties',{}).setdefault('homeLayout',{})['show']=show
    # A resumed completed write verifies current state rather than reusing stale body.
    if raw[name]!=props:
        candidate=patch(before,{name:props},{name:sha(parts(before)[name])})
        plan_operation(client,workspace,'update',plan,definition=candidate,label=label,baseline_hash=definition_hash(before))
    after=plan_operation(client,workspace,'export',plan,label=label+'-after-'+uuid.uuid4().hex)['body']
    new=unpack(after)
    if new[name].get('properties',{}).get('homeLayout',{}).get('show') is not show:
        raise ValueError('Home visibility readback failed')
    return {'visibility':'passed-persisted-workload-show','rendering':'not-tested',
        'concurrency':'fresh-export merge; API has no documented server compare-and-swap'}
