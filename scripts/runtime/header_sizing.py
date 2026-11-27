"""Content-based native rich-text header sizing, approved 2026-11-15.

Calculates saved geometry at authoring time, not an application resize handler.
"""
import copy, ctypes, math, re, json, os, unicodedata
from pathlib import Path
from ctypes import wintypes
from functools import lru_cache
from html.parser import HTMLParser
from .paths import ASSETS

def styles(raw):
    return dict((k.strip().lower(),v.strip()) for k,v in
                (p.split(':',1) for p in raw.split(';') if ':' in p))

# Fabric's inherited text size when no element in the header sets one.
DEFAULT_SIZE=13.0
# Arial's normal line height (ascent + descent + line gap is about 1.15 em). The
# product's title CSS sets paragraph line-height to its initial (normal) value.
LINE_HEIGHT=1.15
VOID={'br','img','hr','input','wbr'}

class Paragraphs(HTMLParser):
    """Paragraph runs with the font size and weight in effect at each run.

    The product sets header sizes on spans and forces paragraph margins to 0, so
    every element's inline font-size counts, the innermost one wins, and
    paragraph margins are ignored.
    """
    def __init__(self):
        super().__init__(convert_charrefs=True);self.paragraphs=[];self.current=None;self.stack=[]
    def size(self):
        return next((e[1] for e in reversed(self.stack) if e[1] is not None),DEFAULT_SIZE)
    def bold(self):
        return any(e[2] for e in self.stack)
    def handle_starttag(self,tag,attrs):
        s=styles(dict(attrs).get('style',''))
        if tag=='br':
            if self.current is not None:self.current['runs'].append(('\n',self.bold(),self.size()))
            return
        if tag in VOID:return
        size=float(s['font-size'].replace('px','')) if 'font-size' in s else None
        self.stack.append((tag,size,tag in ('strong','b') or s.get('font-weight') in ('bold','700')))
        if tag=='p':self.current={'runs':[]}
    def handle_data(self,data):
        if self.current is not None:self.current['runs'].append((data,self.bold(),self.size()))
    def handle_endtag(self,tag):
        closing_size=self.size()
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:del self.stack[i:];break
        if tag=='p' and self.current is not None:
            sizes=[size for text,_,size in self.current['runs'] if text.strip()]
            self.current['size']=max(sizes) if sizes else closing_size
            self.paragraphs.append(self.current);self.current=None

class WindowsFontWidths:
    """Windows Arial glyph widths at 4x precision, no report/UI execution."""
    class Size(ctypes.Structure):
        _fields_=[('cx',wintypes.LONG),('cy',wintypes.LONG)]
    def __init__(self):
        self.g=ctypes.WinDLL('gdi32',use_last_error=True);self.fonts={}
        self.g.CreateCompatibleDC.argtypes=[wintypes.HDC];self.g.CreateCompatibleDC.restype=wintypes.HDC
        self.g.CreateFontW.argtypes=[ctypes.c_int]*5+[wintypes.DWORD]*8+[wintypes.LPCWSTR]
        self.g.CreateFontW.restype=wintypes.HANDLE
        self.g.SelectObject.argtypes=[wintypes.HDC,wintypes.HANDLE];self.g.SelectObject.restype=wintypes.HANDLE
        self.g.GetTextExtentPoint32W.argtypes=[wintypes.HDC,wintypes.LPCWSTR,ctypes.c_int,ctypes.POINTER(self.Size)]
        self.g.DeleteObject.argtypes=[wintypes.HANDLE];self.g.DeleteDC.argtypes=[wintypes.HDC]
        self.dc=self.g.CreateCompatibleDC(None)
        if not self.dc:raise ctypes.WinError(ctypes.get_last_error())
    @lru_cache(maxsize=4096)
    def width(self,text,size,bold):
        key=(size,bold)
        if key not in self.fonts:
            self.fonts[key]=self.g.CreateFontW(-round(size*4),0,0,0,700 if bold else 400,0,0,0,1,0,0,0,0,'Arial')
        font=self.fonts[key]
        if not font:raise ctypes.WinError(ctypes.get_last_error())
        previous=self.g.SelectObject(self.dc,font);result=self.Size()
        ok=self.g.GetTextExtentPoint32W(self.dc,text,len(text.encode('utf-16-le'))//2,ctypes.byref(result))
        self.g.SelectObject(self.dc,previous)
        if not ok:raise ctypes.WinError(ctypes.get_last_error())
        return result.cx/4
    def close(self):
        for f in self.fonts.values():self.g.DeleteObject(f)
        self.g.DeleteDC(self.dc)

def line_count(p,width,fonts):
    count=1;used=0;space=0
    for text,bold,size in p['runs']:
        for word in re.findall(r'\n|[^\S\n]+|\S+',text):
            if word=='\n':count+=1;used=0;space=0;continue
            if word.isspace():space=fonts.width(' ',size,bold);continue
            w=fonts.width(word,size,bold)
            if used and used+space+w>width:count+=1;used=0;space=0
            if w>width:
                for char in word:
                    char_width=fonts.width(char,size,bold)
                    if used and used+char_width>width:count+=1;used=0
                    used+=char_width
                space=0
            else:used+=space+w;space=0
    return count


class PortableFontWidths:
    def __init__(self):
        path=ASSETS/'fixtures/arial-header-metrics.json'
        self.sizes=json.loads(path.read_text(encoding='utf-8'))['sizes']
    def width(self,text,size,bold):
        key=str(int(size)) if size==int(size) else str(size)
        scale=1 if key in self.sizes else size/100
        widths=self.sizes.get(key,self.sizes['100'])['bold' if bold else 'regular']
        total=0
        for char in text:
            if unicodedata.combining(char):continue
            if char in widths:total+=widths[char];continue
            base=unicodedata.normalize('NFKD',char)[0]
            total+=widths.get(base,(100 if unicodedata.east_asian_width(char) in ('W','F') else 60) if key not in self.sizes else size*(1 if unicodedata.east_asian_width(char) in ('W','F') else .6))
        return total*scale
    def close(self):pass

def calculate_header_height(content, width):
    """Span font sizes + wrapped lines at Arial's normal line height + max(8px,8%).

    Paragraph margins add nothing: the product's title CSS forces them to 0.
    """
    if isinstance(width,bool) or not isinstance(width,(int,float)) or not math.isfinite(width) or width<=32:
        raise ValueError('Resolve a positive usable header width larger than the 32px allowance')
    parser=Paragraphs();parser.feed(content)
    if not parser.paragraphs:raise ValueError('Use the documented paragraph-based rich-text header')
    if any(not 0<p['size']<float('inf') for p in parser.paragraphs):raise ValueError('Invalid paragraph font size')
    usable=width-32
    try:fonts=WindowsFontWidths() if os.name=='nt' else PortableFontWidths()
    except (OSError,AttributeError):fonts=PortableFontWidths()
    engine=type(fonts).__name__
    try:lines=[line_count(p,usable,fonts) for p in parser.paragraphs]
    finally:fonts.close()
    content_height=sum(n*p['size']*LINE_HEIGHT for p,n in zip(parser.paragraphs,lines))
    buffer=max(8,math.ceil(content_height*.08))
    height=math.ceil((content_height+buffer)/10)*10
    return {'height':height,'contentHeight':round(content_height,2),'bufferPx':buffer,
            'usableWidth':usable,'paragraphLines':lines,'metrics':engine,
            'sizing':'content-dependent authoring estimate; not runtime auto-resize'}

def fit_header(properties, *, available_width=None):
    """Explicit size-only repair: preserve HTML, identities and non-height state.

    available_width is an authoring input for a known narrower viewport, not a
    serialized native field. Composite image/chart canvases need their own fit.
    """
    out=copy.deepcopy(properties);title=out['visualState']['chartCustomTitle'];canvas=title['customTitle']
    elements=canvas['elements']
    if len(elements)!=1 or elements[0].get('type')!='TEXT':raise ValueError('Expected one rich-text description canvas; preserve composite headers')
    e=elements[0]
    widths=[float(canvas['containerMeta']['width']),float(e['dimension']['width'])]
    if out.get('dimension',{}).get('width') is not None:widths.append(float(out['dimension']['width']))
    if available_width is not None:widths.append(float(available_width))
    if any(not math.isfinite(w) or w<=32 for w in widths):raise ValueError('Resolve valid current header widths')
    sizing=calculate_header_height(e['content'],min(widths));height=sizing['height']
    title['customTitleHeight']=height;canvas['containerMeta']['height']=height
    e['dimension']['height']=str(height);e['layout']['h']=height//10
    return {'properties':out,'sizing':sizing}

def apply_hierarchy_icons(properties, *, reset=False):
    """Business-independent defaults. Explicit existing choices survive repairs."""
    out=copy.deepcopy(properties);table=out['visualState'].setdefault('tableState',{})
    for key in ('expandCollapseIcon','columnExpandCollapseIcon'):
        if reset or key not in table:table[key]='gmate'
    return out
