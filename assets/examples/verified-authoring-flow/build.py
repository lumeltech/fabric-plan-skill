"""Package-only regression: complete base import, rejected reference-only detour."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.codec import load,save
from runtime.planning_presentation import build_application
from runtime.authoring_flow import require_import_contract

def main():
    out=Path(sys.argv[1]) if len(sys.argv)>1 else Path('verified-flow-output')
    model=load(ROOT/'assets/fixtures/model.json')
    spec=load(ROOT/'assets/examples/conditional-formatting/application.json')
    authored=build_application(model,spec)
    save(out/'construction.json',authored);save(out/'requested-spec.json',spec)
    stripped=copy.deepcopy(authored['raw'])
    for path,part in stripped.items():
        if path.endswith('/dataInput.json'):
            part['columns']=[r for r in part['columns'] if 'Native' in r['columnMeta']['measure_type']]
    try:require_import_contract(spec,authored,stripped)
    except ValueError as e:rejected=str(e).startswith('IMPORT_CONTRACT')
    else:rejected=False
    if not rejected:raise AssertionError('Stripped import incorrectly accepted')
    result={'completeBase':authored['importContract'],'referenceOnlyDetourRejected':True,
            'runtime':'not-tested','liveWrites':0}
    save(out/'result.json',result);print(json.dumps(result))

if __name__=='__main__':main()
