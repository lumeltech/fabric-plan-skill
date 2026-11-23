"""Standalone offline example; all identities/data below are illustrative."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from runtime.codec import load,save
from runtime.construct import build
from runtime.time_authoring import add_time_column
from runtime.input_factories import input_create
from runtime.formula_syntax import repair_equality

def sample():
    model=load(ROOT/'fixtures/model.json')
    for name,typ in [('Year','Int64'),('Quarter','Int64'),('MonthName','String'),
                     ('YearMonth','String'),('MonthStart','DateTime'),('Week','Int64')]:
        model['fields'].append(dict(id=f'Calendar[{name}]',tableName='Calendar',columnName=name,columnType='Column',dataType=typ))
    spec={'name':'Illustrative monthly forecast','sheets':[{
        'name':'Monthly Forecast','rows':['Region[Region]'],
        'columns':['Calendar[Year]','Calendar[Quarter]','Calendar[YearMonth]'],
        'measures':[
            {'key':'actual','label':'Actual units','kind':'Native','source':'Metrics[Units]'},
            {'key':'forecast','label':'Forecast units','kind':'Forecast','actuals':'actual',
             'start':'2031-01-01','end':'2031-12-31','timezone':'UTC'},
            {'key':'missing','label':'Missing forecast cells','kind':'Formula','formula':'IF(ISBLANK(${forecast}), 1, 0)'}]}]}
    result=build(model,spec)
    owner=result['identities'][0]
    request={'sheet_id':owner['sheetId'],'visual_id':owner['visualId'],
        'measure_id':'90000000000001001','label':'QTD Forecast units','source_id':owner['measures']['forecast'],
        'missing_id':owner['measures']['missing'],'period':'QTD','offset':0,'month_end':True,
        'row_aggregation':'Sum',
        'parameter':{'parameter_id':'CALC_VARIABLE_example_asof','label':'QTD As Of Date',
          'field':'Calendar[MonthStart]','selected_value':'2031-02-01 00:00:00','technical_name':'ExampleAsOfDate'}}
    candidate,manifest=add_time_column(result['envelope'],**request)
    # Separate local construction example, not a deployed column.
    commentary=input_create('90000000000001002','Quarterly management commentary','LongText',
        {'allow_entry_on_totals_or_subtotals':False},'example-comment-config',visual_column=True)
    return model,spec,result,request,candidate,manifest,commentary

if __name__=='__main__':
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
    model,spec,result,request,candidate,manifest,commentary=sample()
    for name,value in [('model',model),('spec',spec),('baseline',result['envelope']),
        ('time-column.request',request),('candidate',candidate),('changes',manifest),('commentary.local',commentary),
        ('equality.request',{'formula':'var test = 0; IF(AND(test = 0, [Missing FX cells] = 0), [Raw FX effect USD], BLANK)'}),
        ('equality.fixed',repair_equality('var test = 0; IF(AND(test = 0, [Missing FX cells] = 0), [Raw FX effect USD], BLANK)'))]:
        save(out/(name+'.json'),value)
    print('Offline illustrative candidates created; no live report or formula-engine validation.')
