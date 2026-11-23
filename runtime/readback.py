"""Verify authored meaning in normalized API exports, allowing added defaults."""
def contains(actual,expected,path='$'):
    if isinstance(expected,dict):
        if not isinstance(actual,dict): raise ValueError('Readback object mismatch '+path)
        for k,v in expected.items():
            if k not in actual: raise ValueError('Readback missing '+path+'/'+k)
            contains(actual[k],v,path+'/'+k)
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(actual)!=len(expected): raise ValueError('Readback list mismatch '+path)
        for i,v in enumerate(expected): contains(actual[i],v,path+'/'+str(i))
    elif isinstance(expected,bool):
        if type(actual) is not bool or actual!=expected: raise ValueError('Readback Boolean mismatch '+path)
    elif actual!=expected: raise ValueError('Readback value mismatch '+path)

def verify_authored(actual,expected):
    root=actual['definition.json'];want=expected['definition.json']
    contains(root['semanticModelReference'],want['semanticModelReference'],'semanticModelReference')
    sheets={s['recordGuid']:s for s in root['sheets']}
    if len(sheets)!=len(root['sheets']): raise ValueError('Duplicate exported sheet identity')
    for s in want['sheets']:
        if s['recordGuid'] not in sheets: raise ValueError('Missing authored sheet')
        current=sheets[s['recordGuid']]
        contains(current,{k:v for k,v in s.items() if k not in ('order','workloadItemEntityVisuals')},'sheet')
        # Import/export may enumerate embedded references before direct visuals.
        # Identity, embedding and kind must match; display stacking is verified in properties.
        actual_visuals={v['visualId']:v for v in current['workloadItemEntityVisuals']}
        expected_visuals={v['visualId']:v for v in s['workloadItemEntityVisuals']}
        if len(actual_visuals)!=len(current['workloadItemEntityVisuals']) or set(actual_visuals)!=set(expected_visuals):raise ValueError('Visual identity inventory mismatch')
        for vid,v in expected_visuals.items():contains(actual_visuals[vid],v,'sheet/visual/'+vid)
    for name,wantpart in expected.items():
        if name=='definition.json': continue
        if name not in actual: raise ValueError('Missing authored part '+name)
        if name.endswith('/dataInput.json'):
            records={c['measureGuid']:c for c in actual[name]['columns']}
            if len(records)!=len(actual[name]['columns']): raise ValueError('Duplicate exported input identity')
            for c in wantpart['columns']:
                if c['measureGuid'] not in records: raise ValueError('Missing input record')
                contains(records[c['measureGuid']],c,name+'/'+c['measureGuid'])
        else: contains(actual[name],wantpart,name)
    return {'status':'passed-authored-fields-readback','nativeCalculation':'not-tested',
            'dashboardGeometry':'checked-against-definition'}
