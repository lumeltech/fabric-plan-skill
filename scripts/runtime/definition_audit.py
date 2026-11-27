"""Read-only audit of decoded Plan parts. Never treats persistence as execution."""
import copy
from .dimension_mapping import validate_mapping
from .bridge import GROUPS

def audit_definition(raw):
    index={}
    for path in raw:
        key=path.casefold()
        if key in index: raise ValueError('Case-colliding part paths')
        index[key]=path
    def part(path):
        key=path.casefold()
        if key not in index: raise ValueError('Missing part '+path)
        return raw[index[key]]
    sheets=part('definition.json')['sheets'];owners={};embeds=[];mappings=[];lookups=[];issues=[];consumers=[]
    for sheet in sheets:
        for v in sheet.get('workloadItemEntityVisuals',[]):
            key=v['visualId'].casefold()
            if v.get('isEmbedded'): embeds.append({'page':sheet['displayName'],'visualId':v['visualId']});continue
            if key in owners: raise ValueError('Multiple direct owners for portable visual')
            owners[key]=(sheet,v)
            prefix='sheets/'+sheet['recordGuid']+'/visuals/'+v['visualId']+'/'
            props=part(prefix+'properties.json').get('properties',{})
            if v['visualType']=='POWERTABLE':
                columns=part(prefix+'columnConfigs.json')['columnConfigs']
                for c in columns:
                    for target in c.get('columnMeta',{}).get('optionLinking',{}).get('lookupConfig',[]):
                        lookups.append({'sheet':sheet['displayName'],'column':c['columnName'],'displayName':c['displayName'],
                            'selectionMethod':c['columnMeta'].get('selectionMethod'),'target':copy.deepcopy(target)})
            state=props.get('visualState',{})
            if state.get('dimension_id_mapping',{}).get('mappings'):
                m=state['dimension_id_mapping']
                try: status=validate_mapping(m)
                except ValueError as e: status={'status':'invalid','error':str(e)};issues.append({'sheet':sheet['displayName'],'error':str(e)})
                mappings.append({'sheet':sheet['displayName'],'mappings':copy.deepcopy(m['mappings']),**status})
            for a in props.get('pivotAssignments',[]):
                if a.get('sourceType')=='InfoBridge':consumers.append({'sheet':sheet['displayName'],'visualType':v['visualType'],
                    'queryId':a.get('queryId'),'fieldId':a.get('sourceId',a.get('id')),'label':a.get('name')})
    for embed in embeds:
        owner=owners.get(embed['visualId'].casefold())
        if not owner or owner[1]['visualType']!='PLANNING': issues.append({'embed':embed,'error':'Missing direct Planning owner'})
        else:
            embed['ownerSheet']=owner[0]['displayName'];embed['ownerHidden']=owner[0].get('isHidden',False)
    bridge=raw.get(index.get('connectedplanning/infobridge.json'),{'sources':[]})
    queries=[q for s in bridge['sources'] for q in s['queries']];by_id={q['queryId']:q for q in queries}
    def signature(q):
        return [[g,f.get('alias') or f['name'],f.get('type'),f.get('dataType')] for g,s in GROUPS.items() for f in q['meta'].get(s,[])]
    append=[]
    for q in queries:
        if q['type']!='APPEND':continue
        ids=q['meta'].get('queries',[])
        if any(not isinstance(k,str) or k not in by_id for k in ids):
            issues.append({'query':q['name'],'error':'Unresolved append query identity'});continue
        shapes=[signature(by_id[k]) for k in ids]
        append.append({'query':q['name'],'inputs':[by_id[k]['name'] for k in ids],
                       'exactOrderedSchemasMatch':bool(shapes) and all(s==shapes[0] for s in shapes),
                       'completeTypes':all(f[2] is not None and f[3] is not None for s in shapes for f in s),
                       'schemas':dict(zip([by_id[k]['name'] for k in ids],shapes))})
    for c in consumers:
        if c['queryId'] not in by_id:issues.append({'consumer':c,'error':'Query ID absent from export'})
    return {'partCount':len(raw),'sheetCount':len(sheets),'queryCount':len(queries),'embeddedPlanning':embeds,
            'dimensionMappings':mappings,'powerTableLookups':lookups,'appendQueries':append,'queryConsumers':consumers,
            'issues':issues,'evidence':'saved-definition-only','runtimePropagation':'not-tested','rendering':'not-tested'}
