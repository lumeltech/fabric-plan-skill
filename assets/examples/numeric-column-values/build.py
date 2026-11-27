"""Portable numeric-column application; only bundled resources, no live calls."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.codec import load,save
from runtime.planning_presentation import build_application
from runtime.chart_filters import audit_chart_filters
from runtime.validate import validate_plan

def build_example(output):
    output=Path(output)
    model=load(ROOT/'assets/fixtures/model.json')
    model['fields']=[{'id':t+'['+c+']','tableName':t,'columnName':c,'dataType':d,'columnType':'Column'}
        for t,c,d in [('Market','Name','String'),('Period','Month','String'),
                      ('Facts','Estimate','Double'),('Facts','Baseline','Double'),('Facts','Rate','Double')]]
    spec={'name':'Synthetic column-based estimates','requiredCapabilities':['planning.native-measure','intelligence.charts'],
          'sheets':[{'name':'Estimate review','rows':['Market[Name]'],'columns':['Period[Month]'],
                     'measures':[{'key':'estimate','kind':'Native','source':'Facts[Estimate]','label':'Estimate'},
                                 {'key':'baseline','kind':'Native','source':'Facts[Baseline]','label':'Baseline'},
                                 {'key':'rate','kind':'Native','source':'Facts[Rate]','label':'Average rate',
                                  'sourceAggregation':'average','aggregation':'None','columnAggregation':'None'}]}],
          'dashboards':[{'name':'Estimate intelligence','owner':'Estimate review','cards':[
                {'field':'Facts[Estimate]','label':'Estimate'}], 'slicers':[], 'charts':[
                {'field':'Facts[Estimate]','comparisonField':'Facts[Baseline]',
                 'category':'Market[Name]','label':'Estimate versus baseline'}]}]}
    b=build_application(model,spec)
    for name,obj in b['raw'].items():
        if name.endswith('/properties.json') and obj['properties'].get('visualType')==50:
            audit_chart_filters(obj['properties'])
    save(output/'model.json',model);save(output/'spec.json',spec)
    save(output/'definition.json',b['envelope']);save(output/'raw.json',b['raw']);save(output/'home.json',b['home'])
    save(output/'checks.json',{'definition':validate_plan(b['raw']),'defaults':b['defaultsCheck'],
                             'liveWrites':0,'runtime':'not-tested'})
    print('Built synthetic column-based application; source Sum defaults and explicit Average, Home and Navigator included.')

if __name__=='__main__':build_example(sys.argv[1])
