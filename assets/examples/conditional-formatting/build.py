"""Generate a complete fresh example using this package only; no network."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.codec import load,save
from runtime.planning_presentation import build_application,application_defaults
from runtime.scope import prepare_scope
from runtime.workflow import preflight,SUPPORTED

def generate(out):
    model=load(ROOT/'assets/fixtures/model.json')
    spec=load(Path(__file__).with_name('application.json'))
    scoped=prepare_scope(application_defaults(model,spec),SUPPORTED,model)
    if any(x['status'] in ('omitted','alternative') for x in scoped['coverage']):
        raise ValueError('The complete example must be supported')
    preflight(scoped['spec'])
    result=build_application(model,scoped['spec'])
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for key in ('raw','envelope','home','homeSpec','identities','dashboardIdentities','defaultsCheck'):
        save(out/(key+'.json'),result[key])
    save(out/'model.json',model);save(out/'application.json',spec)
    save(out/'evidence.json',{'construction':'new report from bundled model/spec and standard builder',
        'planningSheets':2,'requestedRules':[len(s['conditionalFormatting']) for s in spec['sheets']],
        'home':'generated','dashboards':len(result['dashboardIdentities']),
        'liveDeployment':'not run; synthetic model','UI':'not tested'})
    return result

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: build.py OUTPUT_DIRECTORY')
    generate(sys.argv[1]);print('Fresh two-sheet report generated; no live deployment or UI validation.')
