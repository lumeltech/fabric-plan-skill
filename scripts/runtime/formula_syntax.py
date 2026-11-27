"""Native Planning equality checks, not a DAX/SQL parser or engine validator."""
import re

def _tokens(text):
    i=0
    while i<len(text):
        c=text[i]
        if c.isspace():i+=1;continue
        if text.startswith('//',i):
            end=text.find('\n',i);i=len(text) if end<0 else end+1;continue
        if text.startswith('/*',i):
            end=text.find('*/',i+2)
            if end<0:raise ValueError('Unclosed formula comment')
            i=end+2;continue
        start=i
        if c in ('"',"'"):
            quote=c;i+=1
            while i<len(text):
                if text[i]=='\\':i+=2;continue
                if text[i]==quote:
                    if i+1<len(text) and text[i+1]==quote:i+=2;continue
                    i+=1;break
                i+=1
            else:raise ValueError('Unclosed formula string')
            yield ('quoted',text[start:i],start);continue
        if c=='[':
            # Display-name references are atomic; equality inside a label is text.
            i+=1;quote=None
            # Quotes delimit only a quoted reference, not an apostrophe in an
            # ordinary display label such as [Customer's amount].
            content_start=i
            while content_start<len(text) and text[content_start].isspace():content_start+=1
            while i<len(text):
                if text[i]=='\\':i+=2;continue
                if quote:
                    if text[i]==quote:quote=None
                elif i==content_start and text[i] in ('"',"'"):quote=text[i]
                elif text[i]==']':i+=1;break
                i+=1
            else:raise ValueError('Unclosed formula reference')
            yield ('reference',text[start:i],start);continue
        match=re.match(r'[A-Za-z_][A-Za-z_0-9]*',text[i:])
        if match:
            i+=len(match[0]);yield ('word',match[0],start);continue
        if text[i:i+2] in ('==','!=','<=','>=','<>'):
            i+=2;yield ('operator',text[start:i],start);continue
        i+=1;yield ('operator',c,start)

def equality_issues(formula):
    if not isinstance(formula,str):raise ValueError('Formula must be text')
    tokens=list(_tokens(formula));issues=[]
    for i,(kind,value,pos) in enumerate(tokens):
        if kind!='operator' or value!='=':continue
        declaration=(i>=2 and tokens[i-2][0]=='word' and tokens[i-2][1].lower()=='var' and tokens[i-1][0] in ('word','quoted'))
        if not declaration:
            issues.append({'offset':pos,'line':formula.count('\n',0,pos)+1,
                'message':'Comparison requires ==; a single = is reserved for var declarations.'})
    return issues

def check_formula(formula):
    issues=equality_issues(formula)
    if issues:raise ValueError('Invalid Planning equality at offset '+str(issues[0]['offset'])+': '+issues[0]['message'])
    return formula

def repair_equality(formula):
    """Explicit local candidate only. Preserve declarations, literals and >=/<=/!=/==."""
    issues=equality_issues(formula);fixed=formula
    for issue in reversed(issues):
        i=issue['offset'];fixed=fixed[:i]+'=='+fixed[i+1:]
    check_formula(fixed)
    return {'formula':fixed,'changes':issues,'runtimeValidation':'not run'}
