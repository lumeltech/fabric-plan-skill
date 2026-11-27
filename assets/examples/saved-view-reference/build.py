"""Construct a new number parameter from only the delivered package."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from runtime.page_parameters import number_parameter
from runtime.codec import save
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
save(out/'number-parameter.json',number_parameter('Planning assumption','planning_assumption',4))
print('Constructed fresh parameter bundle; no deployment, formula or runtime effects claimed.')
