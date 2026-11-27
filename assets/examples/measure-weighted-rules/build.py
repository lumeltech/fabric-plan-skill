"""Offline, package-only Column distribution payload. No credentials or old report.

IDs below are synthetic, deliberately beyond JS safe integer precision. For a real
application supply the current owner's identities from its construction/readback.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from runtime.codec import save
from runtime.rule_factories import measure_weighted_rule

out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
request={'logical_id':'9007199254741001','name':'Distribute target using budget weights',
    'target_measures':['target'],'weight_measure':'budget','axis':'Column',
    'measure_ids':{'target':'9007199254740993','budget':'18446744073709551615'}}
save(out/'weighted-rule.request.json',request)
save(out/'weighted-rule.payload.json',measure_weighted_rule(**request))
row={**request,'logical_id':'9007199254741002','name':'Allocate rows by current-year measure weights','axis':'Row','weights_period':'CurrentYear'}
save(out/'weighted-row-rule.request.json',row)
save(out/'weighted-row-rule.payload.json',measure_weighted_rule(**row))
save(out/'validation.json',{'status':'constructed','reference':'MeasureIdWithReference',
    'axis':'Column','sourceRow':'Use Self (omitted)','liveWrites':0,'execution':'not-tested'})
print('Constructed explicit measure-weighted Column rule; no live writes or runtime claim.')
