"""Independent geometry reader/auditor and native page-property transactions."""
import copy, math
from decimal import Decimal
from .codec import sha,dumps
def number(v): return not isinstance(v,bool) and isinstance(v,(int,float,Decimal)) and math.isfinite(v)
def rect(p):
    r={**p.get('position',{}),**p.get('dimension',{})}
    if any(not number(r.get(k)) for k in ('x','y','width','height')) or min(r['x'],r['y'])<0 or min(r['width'],r['height'])<=0:
        raise ValueError('Missing/invalid geometry')
    return {k:r[k] for k in ('x','y','width','height')}
def overlap(a,b,gap=0):
    # JSON readback retains Decimal precision; layout builders may use floats.
    # Normalize only for arithmetic, preserving the original saved coordinates.
    a={k:Decimal(str(v)) for k,v in a.items()};b={k:Decimal(str(v)) for k,v in b.items()};gap=Decimal(str(gap))
    return a['x']<b['x']+b['width']+gap and b['x']<a['x']+a['width']+gap and a['y']<b['y']+b['height']+gap and b['y']<a['y']+a['height']+gap
def inventory(response,allow_empty=False):
    if response.get('statusCode')!=200 or not isinstance(response.get('payload',{}).get('visuals'),list): raise ValueError('Need successful complete page inventory')
    payload=response['payload']; page=payload['properties']['properties']; dim=page['canvasStyle']['dimension']; unit=dim['elementScalingUnit']
    if unit not in ('pixel','percentage'): raise ValueError('Unknown layout unit')
    bounds={'width':dim['width'],'height':dim['height']} if unit=='pixel' else {'width':1,'height':1}
    if any(not number(v) or v<=0 for v in bounds.values()): raise ValueError('Invalid canvas')
    out={}; overrides=page.get('reactiveVisualProperties',[])
    if any(o.get('visualId') not in {v.get('id') for v in payload['visuals']} for o in overrides): raise ValueError('Orphan page-local visual override')
    for v in payload['visuals']:
        key=v['id']
        if not isinstance(key,str) or key in out: raise ValueError('Missing/duplicate runtime visual ID')
        direct=v.get('properties',{}); direct=direct.get('properties',direct)
        matches=[o for o in overrides if o['visualId']==key]
        if len(matches)>1 or (v.get('isEmbedded') and len(matches)!=1): raise ValueError('Missing/duplicate embedded override')
        p=matches[0]['properties'] if v.get('isEmbedded') else direct
        out[key]={'rectangle':rect(p),'embedded':bool(v.get('isEmbedded')),'properties':p,'ownerProperties':direct,'record':v}
    if not out and not allow_empty: raise ValueError('Empty inventory is not passed validation')
    return {'bounds':bounds,'unit':unit,'visuals':out,'page':page,'payload':payload,'fingerprint':sha(dumps(response))}
def audit(response,gap=0,reserved=(),backgrounds=(),alignment_groups=()):
    inv=inventory(response); v=inv['visuals']; b=inv['bounds']; errors=[]
    if not number(gap) or gap<0: raise ValueError('Invalid spacing')
    if not set(backgrounds)<=v.keys(): raise ValueError('Unknown explicit background ID')
    for key,x in v.items():
        r=x['rectangle']
        if r['x']+r['width']>b['width'] or r['y']+r['height']>b['height']: errors.append(key+': out of bounds')
        if key not in backgrounds:
            for area in reserved:
                rect({'position':area,'dimension':area})
                if overlap(r,area,gap): errors.append(key+': reserved-area overlap')
    pairs=list(v)
    for i,a in enumerate(pairs):
        for bkey in pairs[i+1:]:
            if a not in backgrounds and bkey not in backgrounds and overlap(v[a]['rectangle'],v[bkey]['rectangle'],gap): errors.append(a+' / '+bkey+': overlap or insufficient gap')
    for g in alignment_groups:
        axis=g['axis']; ids=g['ids']; tolerance=g.get('tolerance',1e-8)
        if axis not in ('x','y','width','height') or len(ids)<2 or any(i not in v for i in ids): raise ValueError('Invalid alignment group')
        values=[v[i]['rectangle'][axis] for i in ids]
        if max(values)-min(values)>tolerance: errors.append('Misalignment '+','.join(ids))
    if errors: raise ValueError('; '.join(errors))
    return {'status':'passed-static-geometry','count':len(v),'unit':inv['unit'],'rendered':'not-run'}
def find(bounds,dimension,occupied,gap=16,margin=24):
    if min(dimension.values())<=0 or gap<0 or margin<0: raise ValueError('Invalid placement request')
    xs={margin,bounds['width']-margin-dimension['width']}; ys={margin,bounds['height']-margin-dimension['height']}
    for a in occupied:
        rect({'position':a,'dimension':a}); xs.update([a['x']+a['width']+gap,a['x']-dimension['width']-gap]); ys.update([a['y']+a['height']+gap,a['y']-dimension['height']-gap])
    for y in sorted(ys):
        for x in sorted(xs):
            r={'x':x,'y':y,**dimension}
            if x>=margin and y>=margin and x+dimension['width']<=bounds['width']-margin and y+dimension['height']<=bounds['height']-margin and not any(overlap(r,a,gap) for a in occupied): return r
    return None
def placement_batch(response,page_id,visual_id,intended,expected_fingerprint):
    inv=inventory(response)
    if inv['fingerprint']!=expected_fingerprint: raise ValueError('Stale inventory')
    if visual_id not in inv['visuals']: raise ValueError('Unknown runtime visual')
    target=inv['visuals'][visual_id]; b={'visuals':{},'workloadEntities':{},'workload':{},'etags':{'visuals':{},'workloadEntities':{}}}
    page_etag=inv['payload'].get('etag')
    if page_etag is None: raise ValueError('Fresh page ETag required')
    b['etags']['workloadEntities'][page_id]=page_etag
    p=copy.deepcopy(target['properties']); p['position']={k:intended[k] for k in ('x','y')}; p['dimension']={**p.get('dimension',{}),**{k:intended[k] for k in ('width','height')}}
    rect(p)
    if target['embedded']:
        page=copy.deepcopy(inv['page'])
        for o in page['reactiveVisualProperties']:
            if o['visualId']==visual_id: o['properties']=p
        b['workloadEntities'][page_id]={'schema':'0.0.1','properties':page}
    else:
        record=target['record']; flat=record.get('etag'); nested=record.get('properties',{}).get('etag')
        if flat is not None and nested is not None and flat!=nested: raise ValueError('Conflicting visual ETags')
        etag=nested if nested is not None else flat
        if etag is None: raise ValueError('Fresh visual ETag required')
        b['visuals'][visual_id]={'schema':'0.0.1','properties':p}; b['etags']['visuals'][visual_id]=etag
    return b
def verify_unchanged(before,after,target_id,intended,gap=0):
    a=inventory(before); b=inventory(after)
    if set(a['visuals'])!=set(b['visuals']) or a['unit']!=b['unit'] or a['bounds']!=b['bounds']: raise ValueError('Inventory/canvas drift')
    for vid,v in a['visuals'].items():
        if vid!=target_id and v['properties']!=b['visuals'][vid]['properties']: raise ValueError('Unrelated visual changed')
    old=a['visuals'][target_id]; new=b['visuals'][target_id]
    expected_page=copy.deepcopy(a['page'])
    if old['embedded']:
        for entry in expected_page['reactiveVisualProperties']:
            if entry['visualId']==target_id: entry['properties']=copy.deepcopy(new['properties'])
    if b['page']!=expected_page: raise ValueError('Unrelated page property changed')
    if old['embedded'] and old['ownerProperties']!=new['ownerProperties']: raise ValueError('Embedding moved source owner')
    for k in set(old['properties'])|set(new['properties']):
        if k not in ('position','dimension') and old['properties'].get(k)!=new['properties'].get(k): raise ValueError('Unrelated target property changed')
    if new['rectangle']!=intended: raise ValueError('Persisted geometry differs')
    return audit(after,gap=gap)
