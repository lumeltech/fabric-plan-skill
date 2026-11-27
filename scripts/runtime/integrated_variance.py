"""Reference-derived Analytics+ integrated variance presentation, without rebinding."""
import copy
from pathlib import Path
from .codec import load,loads,dumps
from .paths import ASSETS

PREFIX='hiddenProperties_!!!_'

def integrated_variance_config():
    return copy.deepcopy(load(ASSETS/'fixtures/integrated-variance-column.json')['measureConfig'])

def apply_integrated_variance(properties):
    """Style one current numeric AC/PY comparison; preserve all field identities.

    The saved reference supplies the vertical variant. Do not infer another enum
    from an orientation name. No API, input/column writes or runtime checks here.
    """
    out=copy.deepcopy(properties)
    if out.get('visualType')!=50:
        raise ValueError('Integrated variance requires ANALYTICS_PLUS visualType 50')
    vs=out.setdefault('visualState',{})
    typ=out.get('chartType',vs.get('chartType'))
    if typ not in (None,'COLUMN_VERTICAL','COLUMN_INTEGRATED_VERTICAL'):
        raise ValueError('Selected contract is vertical bar/column only; resolve the requested family explicitly')
    assignments=out.get('pivotAssignments',[])
    measures=[a for a in assignments if a.get('dataRoleType')=='Measure']
    if len(measures)!=2 or sorted(a.get('bucketId','') for a in measures)!=['AC','PY']:
        raise ValueError('Resolve one actual/current AC and one baseline PY assignment before choosing this chart')
    if any(a.get('dataType') not in ('Int64','Double','Decimal') for a in measures):
        raise ValueError('Integrated comparison requires numeric assigned measures')
    if not any(a.get('dataRoleType')=='Grouping' for a in assignments):
        raise ValueError('Preserve/resolve the chart category assignment before choosing this chart')
    fixture=load(ASSETS/'fixtures/integrated-variance-column.json')
    out['chartType']=fixture['chartType']
    if 'chartType' in vs:vs['chartType']=fixture['chartType']
    def current(key):
        value=vs.get(PREFIX+key,{})
        value=loads(value) if isinstance(value,str) else copy.deepcopy(value)
        if not isinstance(value,dict):raise ValueError('Expected object state for '+key)
        return value
    # Preserve existing grouping/template metadata while aligning every selector.
    template=current('template')
    for k,v in fixture['templateDefaults'].items():template.setdefault(k,copy.deepcopy(v))
    template.update(copy.deepcopy(fixture['templateSelection']))
    vs[PREFIX+'template']=dumps(template).strip()
    mode=current('chartsMode');mode.update(fixture['chartsMode'])
    vs[PREFIX+'chartsMode']=dumps(mode).strip()
    config=current('measureConfig')
    config.setdefault('instanceId',fixture['measureConfig']['instanceId'])
    config['config']=copy.deepcopy(fixture['measureConfig']['config'])
    vs[PREFIX+'measureConfig']=dumps(config).strip()
    return out
