"""Exact numbers, explicit string boundaries, guarded definition changes."""
import json, decimal, math, base64, hashlib, copy, pathlib
def _pairs(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError('Duplicate exact JSON key: '+k)
        d[k]=v
    return d
def loads(s):
    return json.loads(s,parse_float=decimal.Decimal,object_pairs_hook=_pairs,
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON '+x)))
def dumps(v,indent=2):
    # stdlib JSON does not preserve Decimal; serialize recursively, no float cast.
    def enc(x,level):
        if x is None: return 'null'
        if isinstance(x,bool): return 'true' if x else 'false'
        if isinstance(x,(int,decimal.Decimal)):
            if isinstance(x,decimal.Decimal) and not x.is_finite(): raise ValueError('Nonfinite number')
            return str(x)
        if isinstance(x,float):
            if not math.isfinite(x): raise ValueError('Nonfinite number')
            return repr(x)
        if isinstance(x,str): return json.dumps(x,ensure_ascii=False)
        if isinstance(x,(dict,list)):
            if not x: return '{}' if isinstance(x,dict) else '[]'
            pad=' '*indent*(level+1); end=' '*indent*level
            if isinstance(x,dict):
                if not all(isinstance(k,str) for k in x): raise ValueError('Object keys must be strings')
                vals=[json.dumps(k,ensure_ascii=False)+': '+enc(z,level+1) for k,z in x.items()]; a,b='{','}'
            else: vals=[enc(z,level+1) for z in x]; a,b='[',']'
            return a+'\n'+pad+(',\n'+pad).join(vals)+'\n'+end+b
        raise TypeError(type(x).__name__)
    return enc(v,0)+'\n'
def load(p): return loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
    p=pathlib.Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.tmp'); tmp.write_text(dumps(v),encoding='utf-8'); tmp.replace(p)
def sha(b): return hashlib.sha256(b if isinstance(b,bytes) else b.encode()).hexdigest()
def safe_path(name):
    p=pathlib.PurePosixPath(name)
    if not name or '\\' in name or ':' in name or p.is_absolute() or '..' in p.parts or str(p)!=name:
        raise ValueError('Unsafe/noncanonical relative path: '+name)
    return p
def parts(envelope):
    obj=envelope.get('definition',envelope)
    values=obj.get('parts')
    if not isinstance(values,list) or not values: raise ValueError('Definition parts empty/missing')
    seen=set(); decoded={}
    for p in values:
        path=p['path']; safe_path(path)
        if path.casefold() in seen: raise ValueError('Duplicate/case-colliding part: '+path)
        seen.add(path.casefold())
        if p.get('payloadType')!='InlineBase64': raise ValueError('Unsupported payload type')
        decoded[path]=base64.b64decode(p['payload'],validate=True)
    return decoded
def definition_hash(envelope):
    return sha(dumps({k:sha(v) for k,v in sorted(parts(envelope).items())}))
def unpack(envelope): return {k:loads(v.decode('utf-8-sig')) for k,v in parts(envelope).items()}
def pack(raw):
    if not raw: raise ValueError('No parts')
    out={'definition':{'parts':[{'path':str(safe_path(k)),'payloadType':'InlineBase64','payload':base64.b64encode(dumps(v).encode()).decode()} for k,v in raw.items()]}}
    parts(out); return out
def patch(envelope,changes,expected_hashes):
    """Replace only named complete parts; unchanged payload bytes remain identical."""
    old=parts(envelope); out=copy.deepcopy(envelope); root=out.get('definition',out)
    for k in changes:
        if k not in old: raise ValueError('Use explicit new-part construction for '+k)
        if expected_hashes.get(k)!=sha(old[k]): raise ValueError('Stale baseline: '+k)
    for p in root['parts']:
        if p['path'] in changes: p['payload']=base64.b64encode(dumps(changes[p['path']]).encode()).decode()
    return out
def pointer_get(obj,pointer):
    if not pointer: return obj
    if not pointer.startswith('/'): raise ValueError('JSON pointer required')
    for raw in pointer[1:].split('/'):
        key=raw.replace('~1','/').replace('~0','~')
        obj=obj[int(key)] if isinstance(obj,list) else obj[key]
    return obj
def pointer_set(obj,pointer,value):
    parent,_,raw=pointer.rpartition('/'); target=pointer_get(obj,parent)
    key=raw.replace('~1','/').replace('~0','~')
    if isinstance(target,list): target[int(key)]=value
    else: target[key]=value
def decode_strings(obj,pointers):
    out=copy.deepcopy(obj)
    for p in pointers:
        v=pointer_get(out,p)
        if not isinstance(v,str): raise ValueError('Boundary already object: '+p)
        pointer_set(out,p,loads(v))
    return out
