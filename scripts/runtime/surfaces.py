"""Home rich text, bookmarks, PowerTable source and eligibility utilities."""
import copy, re
from .codec import dumps,loads
from .construct import guid,schema
def lexical(text):
    if not isinstance(text,str): raise ValueError('Text must be string')
    children=[]
    for paragraph in text.split('\n'):
        children.append({'children':[{'detail':0,'format':0,'mode':'normal','style':'font-family: Arial;','text':paragraph,'type':'text','version':1}],
          'direction':None,'format':'','indent':0,'type':'paragraph','version':1,'textFormat':0,'textStyle':''})
    return dumps({'root':{'children':children,'direction':None,'format':'','indent':0,'type':'root','version':1}}).strip()
def home_item(kind,title='',description='',asset=None,columns=4,exclusions=()):
    if kind not in ('text','image','preview-cards','header-image-text'): raise ValueError('Home item type')
    item={'id':guid(),'instanceId':guid(),'type':kind}
    if kind in ('text','header-image-text'): item['instanceState']={'text':{'title':lexical(title),'description':lexical(description)}}
    if kind=='preview-cards':
        if columns not in (3,4): raise ValueError('Cards support three or four columns')
        item['instanceState']={'previewCards':{'columns':columns,'unSelectedEntityIds':list(exclusions)}}
    if kind=='image' and not asset: raise ValueError('Image needs actual uploaded asset reference')
    if kind in ('image','header-image-text'):
        item['imageConfig']={'sizingMode':'fit'}
        if asset:
            if asset.startswith(('blob:','data:','file:')): raise ValueError('Persist returned opaque asset, not pixels/temp URL')
            item['imageConfig']['source']=asset
    return item
def home_layout(items,rows):
    from .home_fit import assert_home_fit,positive_number
    out={'items':copy.deepcopy(items),'rows':[]}; ids={x['id'] for x in items}
    if not items or not rows or len(ids)!=len(items) or len({x['instanceId'] for x in items})!=len(items): raise ValueError('Missing/duplicate Home content')
    for special in ('preview-cards','header-image-text'):
        if sum(x['type']==special for x in items)>1: raise ValueError('Duplicate special Home block')
    used=[]
    for row in rows:
        seq=row['itemIds']; widths=row.get('widths',[None]*len(seq))
        if not seq or len(seq)>6 or len(seq)!=len(widths) or any(i not in ids for i in seq): raise ValueError('Home row references/widths')
        if any(x['type'] in ('preview-cards','header-image-text') for x in items if x['id'] in seq) and len(seq)!=1: raise ValueError('Hero/cards require own row')
        if any(w is not None and not positive_number(w) for w in widths): raise ValueError('Invalid Home pixel width')
        r={'id':row.get('id') or guid(),'itemIds':seq,'widths':widths,'height':row.get('height'),'defaultHeightRatio':None}
        if r['height'] is not None:
            if not positive_number(r['height']): raise ValueError('Home height must be finite and positive')
            r['isHeightManual']=True
        out['rows'].append(r); used.extend(seq)
    if sorted(used)!=sorted(ids): raise ValueError('Every Home item must occur exactly once')
    if len({r['id'] for r in out['rows']})!=len(out['rows']): raise ValueError('Duplicate Home row identity')
    assert_home_fit(out)
    return out
def bookmark(name,page_id,visual_id,snapshot,order=0,record_id=None,slug=None):
    if not page_id or not visual_id or not snapshot: raise ValueError('Bookmark needs real owner and captured authored state')
    slug=(slug or guid()).upper()
    # Snapshot is from this run's authored visual, never an old report template.
    return {'recordGuid':record_id or guid(),'name':name,'bookmarkType':20,'bookmarkSlug':slug,
       'cloudMeta':{'bookmarkMeta':{'bookmarkSlug':slug,'bookmarkOrder':order,'isDefaultBookmark':False,
          'activePageId':page_id,'activeSelection':[visual_id],
          'bookmarkConfig':{'includeData':True,'includeDisplay':True,'includeCurrentPage':True,'accumulationType':'all-visuals'},
          'pageLevelFilterAssignments':[],'workloadLevelFilterAssignments':[],'entityLevelVariables':[],'workloadLevelVariables':[],
          'visualGroupMap':{},'visualSelectionState':{},'crossFilters':[],'crossFiltersMeta':{},'sourceVisualFilters':[],
          'focusModeVisualId':None,'spotlightId':None,'drillthroughEntityConfig':{}},
          'bookmarkVisualMeta':{visual_id:copy.deepcopy(snapshot)}}}
def maintenance_eligible(table,explicit=False):
    if table.get('physicalType')!='U' or not table.get('primaryKey') or not table.get('columns'): raise ValueError('Verified SQL base table, key and column metadata required')
    if not explicit and not (table.get('businessDimension') and table.get('directLakeLineageVerified')):
        raise ValueError('Automatic maintenance needs business dimension and verified Direct Lake lineage')
    if table.get('assignmentBridge') and not explicit: raise ValueError('Do not auto-expose assignment bridge')
    return True
def powertable_source(table,connection,explicit=False,*,require_metadata=True):
    maintenance_eligible(table,explicit)
    for k in ('connectionId','dbHost','dbName','artifactId','workspaceId'):
        if not connection.get(k): raise ValueError('Missing resolved '+k)
    host=connection['dbHost']
    if host.endswith(',1433'): host=host[:-5]
    if any(c in host for c in ',;=/'): raise ValueError('Expected hostname; non-default port route unresolved')
    result={'$schema':schema('PowerTable/Source'),'source':{'connectionId':connection['connectionId'],'dbHost':host,'dbName':connection['dbName'],
        'schemaName':table['schema'],'tableName':table['name'],'recordGuid':guid(),
        'sqlTargetArtifact':{'artifactId':connection['artifactId'],'workspaceId':connection['workspaceId'],'artifactType':'SQLDbNative'}}}
    if require_metadata:
        from .powertable_config import resolved_source_meta
        result['source']['meta']=resolved_source_meta(connection)
    return result
def reconcile_column_configs(existing,intended,allow_delete=False):
    old={x['columnGuid']:x for x in existing}; new={x['columnGuid']:x for x in intended}
    if len(new)!=len(intended): raise ValueError('Duplicate column GUID')
    if not allow_delete:
        for k,v in old.items(): new.setdefault(k,copy.deepcopy(v))
    for v in new.values():
        if not {'columnGuid','columnName','columnType','columnMeta','displayName'}<=v.keys(): raise ValueError('Incomplete PowerTable column')
    return list(new.values())
PHYSICAL_METADATA_SQL="""SELECT s.name AS schema_name,t.name AS table_name,t.type AS physical_type,
c.column_id,c.name AS column_name,ty.name AS type_name,c.max_length,c.precision,c.scale,
c.is_nullable,c.is_identity,c.is_computed,
CASE WHEN pk.column_id IS NULL THEN 0 ELSE 1 END AS is_primary_key
FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
JOIN sys.columns c ON c.object_id=t.object_id JOIN sys.types ty ON c.user_type_id=ty.user_type_id
LEFT JOIN (SELECT ic.object_id,ic.column_id FROM sys.indexes i JOIN sys.index_columns ic
 ON i.object_id=ic.object_id AND i.index_id=ic.index_id WHERE i.is_primary_key=1) pk
 ON pk.object_id=c.object_id AND pk.column_id=c.column_id
WHERE s.name=@schema AND t.name=@table ORDER BY c.column_id;"""
# Unique indexes and constraints for the same table; filtered indexes do not
# guarantee table-wide uniqueness and are excluded. Feed both result sets to
# sql_definition.catalog_table.
UNIQUE_METADATA_SQL="""SELECT i.name AS index_name,i.is_primary_key,c.name AS column_name,ic.key_ordinal
FROM sys.indexes i JOIN sys.index_columns ic ON i.object_id=ic.object_id AND i.index_id=ic.index_id
JOIN sys.columns c ON c.object_id=ic.object_id AND c.column_id=ic.column_id
JOIN sys.tables t ON t.object_id=i.object_id JOIN sys.schemas s ON s.schema_id=t.schema_id
WHERE s.name=@schema AND t.name=@table AND i.is_unique=1 AND i.has_filter=0 AND ic.is_included_column=0
ORDER BY i.index_id,ic.key_ordinal;"""
