"""Arial is an application requirement, including local formatting overrides.

Checks authored definitions only. Never rewrites formulas, captions, stored values
or an existing report during an unrelated repair.
"""
import re,copy,uuid
from .codec import loads,dumps

FONT_KEYS = {'fontFamily', 'font_family', 'headerFontFamily', 'titleFontFamily'}
CSS_FONT = re.compile(r'font-family\s*:\s*([^;<>]+?)(?=;|["\']?\s*>|$)', re.I)

def arial(value):
    return isinstance(value, str) and value.split(',')[0].strip(' \t\r\n\"\'').casefold() == 'arial'

def font_issues(value, path=''):
    issues=[]
    def visit(obj, p, key=''):
        if isinstance(obj, dict):
            for k,v in obj.items():
                q=p+'/'+k
                if k in FONT_KEYS and v and not arial(v):issues.append(q)
                visit(v,q,k)
        elif isinstance(obj, list):
            # Matrix styles are ordered operations; check the effective family.
            formats=[x for x in obj if isinstance(x,dict) and isinstance(x.get('format'),dict)]
            if formats and len(formats)==len(obj):
                fonts=[x['format']['4'] for x in sorted(formats,key=lambda x:x.get('order',0)) if '4' in x['format']]
                if fonts and not arial(fonts[-1]):issues.append(p+'/effective-font')
            for i,v in enumerate(obj):visit(v,p+'/'+str(i),key)
        elif isinstance(obj,str):
            if key in ('content','formattedTitle','style','textStyle'):
                for m in CSS_FONT.finditer(obj):
                    if not arial(m[1]):issues.append(p+'/font-family')
            # These documented boundaries contain serialized visual/Lexical JSON.
            if (key.startswith('hiddenProperties_!!!_') or key in ('text','title','description')) and obj.lstrip().startswith('{'):
                try:decoded=loads(obj)
                except (ValueError,TypeError):return
                if isinstance(decoded,dict):visit(decoded,p+'/$json')
    visit(value,path)
    return issues

def require_arial(raw,home_layout):
    issues=[];planning=0
    for name,obj in raw.items():
        if not name.endswith('/properties.json'):continue
        p=obj.get('properties',{});vs=p.get('visualState',{})
        if 'manage_measures' in vs:
            planning+=1
            if not arial(vs.get('globalStyles',{}).get('fontFamily')):
                issues.append(name+'/properties/visualState/globalStyles/fontFamily')
        issues.extend(font_issues(vs,name+'/properties/visualState'))
    issues.extend(font_issues(home_layout,'Home'))
    if issues:raise ValueError('Required Arial font missing or overridden: '+', '.join(dict.fromkeys(issues)))
    return {'font':'Arial','planningDefaultsChecked':planning,'authoredOverrides':'passed','rendering':'not-tested'}

def normalize_arial(properties):
    """Normalize documented style boundaries, including service-expanded chart JSON.

    Used for new application defaults or an explicitly requested font change.
    Does not inspect formula strings, stored inputs or arbitrary JSON strings.
    """
    out=copy.deepcopy(properties)
    def visit(obj,key=''):
        if isinstance(obj,dict):
            for k,v in list(obj.items()):
                if k in FONT_KEYS and v:obj[k]='Arial'
                elif k=='format' and isinstance(v,dict) and '4' in v:
                    obj[k]=visit(v,k);obj[k]['4']='Arial'
                else:obj[k]=visit(v,k)
        elif isinstance(obj,list):return [visit(v,key) for v in obj]
        elif isinstance(obj,str):
            if key in ('content','formattedTitle','style','textStyle'):
                return CSS_FONT.sub(lambda m:m[0].replace(m[1],'Arial'),obj)
            if (key.startswith('hiddenProperties_!!!_') or key in ('text','title','description')) and obj.lstrip().startswith('{'):
                try:decoded=loads(obj)
                except (ValueError,TypeError):return obj
                if isinstance(decoded,dict):
                    changed=visit(decoded)
                    return dumps(changed) if changed!=loads(obj) else obj
        return obj
    state=out.get('visualState')
    if isinstance(state,dict):
        out['visualState']=visit(state)
        if 'manage_measures' in state:
            out['visualState'].setdefault('globalStyles',{})['fontFamily']='Arial'
    return out
