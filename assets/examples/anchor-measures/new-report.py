"""Package-only first-anchor construction; synthetic model, no saved report/network."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.codec import load, save
from runtime.planning_presentation import build_application


def inputs():
    model=load(ROOT/'assets/fixtures/model.json')
    model['fields'].append({'id':'Calendar[Year]','tableName':'Calendar','columnName':'Year',
                            'columnType':'Column','dataType':'Int64'})
    spec={'name':'Illustrative Regional Benefits',
          'requiredCapabilities':['planning.numeric','planning.formula','planning.native-measure','planning.anchor-measure'],
          'sheets':[{'name':'Regional Benefits',
            'header':'Maintain the regional annual benefits policy and review employee costs. Illustrative inputs, not business actuals.',
            'rows':['Region[Region]','Employee[Employee]'],
            'columns':['Calendar[Year]','Period[Month]'],
            'measures':[
              {'key':'salary','kind':'Native','source':'Metrics[BasePay]','label':'Base Salary','aggregation':'Sum'},
              {'key':'benefits','kind':'DataInput','label':'Benefits Rate','aggregation':'AverageLeaf',
               'default_value':{'Static':0.22},'distribute':True,
               'anchor':{'row_fields':['Region[Region]'],'column_fields':['Calendar[Year]'],
                         'display_at_all_levels':False}},
              {'key':'cost','kind':'Formula','label':'Employee Cost','aggregation':'Formula',
               'formula':'${salary} * (1 + ${benefits})'}]}]}
    return model,spec


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    model,spec=inputs()
    result=build_application(model,spec)
    save(args.out,result)
    print('Synthetic first-anchor application constructed; no report deployed or runtime validation run.')
