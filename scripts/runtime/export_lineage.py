"""Reconcile the observed exported DI label on an actual Formula owner.

Read only the same export's owner records. No names-only identity resolution,
input changes, formula rewrites, query rewiring or copied prior graph.
"""
import copy
from .bridge_identity import SOURCE_TYPES,check_planning_graph

def reconcile(raw):
    key='connectedPlanning/infobridge.json'
    if key not in raw:return {},[]
    graph=copy.deepcopy(raw[key]);changes=[]
    for source in graph.get('sources',[]):
        if source.get('type')!='PLANNING':continue
        vid=source.get('visualId')
        matches=[v for k,v in raw.items() if k.endswith('/visuals/'+str(vid)+'/dataInput.json')]
        if len(matches)!=1:raise ValueError('Current export must resolve one Planning source owner')
        owners={c['measureGuid']:c for c in matches[0]['columns']}
        fields={f['id']:f for f in source['meta']['measures']};expected={}
        for fid,f in fields.items():
            record=owners.get(fid)
            if record is None or f.get('measureGuid')!=fid or record['name']!=f['name']:
                raise ValueError('Source identity differs from current owner')
            kind=record['columnMeta']['measure_type']
            if len(kind)!=1 or next(iter(kind)) not in SOURCE_TYPES:raise ValueError('Unverified owner type')
            expected[fid]=SOURCE_TYPES[next(iter(kind))]
        def visit(obj,path):
            if isinstance(obj,dict):
                fid=obj.get('id')
                if isinstance(fid,str) and fid in expected and 'name' in obj:
                    if obj.get('measureGuid')!=fid or obj['name']!=fields[fid]['name'] or obj.get('isHierarchyColumn') is not False:
                        raise ValueError('Non-type lineage drift needs reconciliation')
                    before=obj.get('columnType');after=expected[fid]
                    if before!=after:
                        if (before,after)!=('DI','FORMULA'):raise ValueError('Unobserved source type drift')
                        obj['columnType']=after;changes.append({'source':source['sourceGuid'],'path':path+['columnType'],'from':before,'to':after})
                for k,v in obj.items():visit(v,path+[k])
            elif isinstance(obj,list):
                for i,v in enumerate(obj):visit(v,path+[i])
        visit(source,[])
    check_planning_graph(graph)
    return ({key:graph} if changes else {}),changes
