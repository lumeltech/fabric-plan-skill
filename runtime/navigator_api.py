"""Local Navigator state and target validation."""
import copy
from pathlib import Path
from .codec import load
from .construct import merge
from .navigator_defaults import complete_defaults

def state(kind='BOOKMARK_TABS',*,page_target=None,bookmark_target=None,web_url=None,selected_pages=None,hidden_bookmarks=None,caption='View',palette=None):
    if kind not in ('NAVIGATOR_BUTTON','BOOKMARK_TABS','PAGE_NAVIGATOR_TABS'):raise ValueError('Navigator kind')
    s=load(Path(__file__).resolve().parents[1]/'fixtures/navigator-builder-20261112.json');s['type']=kind
    button={'actionType':'NONE','bookmarkId':None,'webUrl':None,'pageDestinationId':None}
    targets=[x for x in (page_target,bookmark_target,web_url) if x is not None]
    if len(targets)>1 or (targets and kind!='NAVIGATOR_BUTTON'):raise ValueError('Button destinations are exclusive and require button kind')
    if page_target is not None:button.update(actionType='PAGE_NAVIGATION',pageDestinationId=page_target)
    if bookmark_target is not None:button.update(actionType='BOOKMARK_NAVIGATION',bookmarkId=bookmark_target)
    if web_url is not None:
        import urllib.parse
        u=urllib.parse.urlsplit(web_url)
        if u.scheme!='https' or not u.hostname or u.username or u.password:raise ValueError('Explicit HTTPS button destination required')
        button.update(actionType='WEB_URL',webUrl=web_url)
    s['navigatorButtonState']=button
    for key,values in (('selectedPages',selected_pages),('hiddenBookmarks',hidden_bookmarks)):
        if values is not None:
            if not isinstance(values,list) or any(not isinstance(x,str) for x in values) or len(set(values))!=len(values):raise ValueError('Unique destination strings required')
            s['navigatorTabsState'][key]=list(values)
    if not isinstance(caption,str):raise ValueError('Caption string required')
    s['style']['DEFAULT']['shapeState']['text']['value']=caption
    if palette:
        if set(palette)-{'fill','text','activeFill','activeText','border'}:raise ValueError('Unsupported palette key')
        for color in palette.values():
            import re
            if not isinstance(color,str) or not re.fullmatch(r'#[0-9A-Fa-f]{6}',color):raise ValueError('Six-digit color required')
        d=s['style']['DEFAULT']['shapeState'];a=s['style']['ACTIVE']['shapeState']
        if 'fill' in palette:d['fill']['fillColor']=palette['fill']
        if 'text' in palette:d['text']['fontColor']=palette['text']
        if 'border' in palette:d['border']['color']=palette['border']
        if 'activeFill' in palette:a['fill']['fillColor']=palette['activeFill']
        if 'activeText' in palette:a['text']['fontColor']=palette['activeText'];a['icon']['color']=palette['activeText']
    return complete_defaults(s)

def validate_targets(s,pages,bookmarks):
    pages=set(pages);bookmarks=set(bookmarks);button=s['navigatorButtonState'];tabs=s['navigatorTabsState']
    if button.get('pageDestinationId') is not None and button['pageDestinationId'] not in pages:raise ValueError('Missing page destination')
    if button.get('bookmarkId') is not None and button['bookmarkId'] not in bookmarks:raise ValueError('Missing bookmark slug')
    if not set(tabs.get('selectedPages',[]))<=pages or not set(tabs.get('hiddenBookmarks',[]))<=bookmarks:raise ValueError('Unresolved selector reference')
    if s['type']=='BOOKMARK_TABS' and not bookmarks-set(tabs.get('hiddenBookmarks',[])):raise ValueError('Bookmark tabs require actual visible public bookmarks')
    if s['type']=='PAGE_NAVIGATOR_TABS' and not pages:raise ValueError('Page tabs require actual pages')
