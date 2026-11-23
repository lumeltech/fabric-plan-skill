"""Package-only cold construction; synthetic catalogs, no network or old report.

Creates a new base application with query Values and illustrates a direct
binding using a synthetic owner identity. No binding is saved to a workspace.
"""
from pathlib import Path
import sys,uuid
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from runtime.codec import load,save
from runtime.identity import Registry
from runtime.consumer_bindings import numeric_output_fields,assert_resolved
from runtime.planning_presentation import build_application
from runtime.measure_bindings import resolve_measure
from runtime.linked_values import value_assignment
from runtime.storage_context import query_contract

def build(destination):
    query={'id':str(uuid.uuid4()),'sourceId':str(uuid.uuid4()),'name':'Illustrative saved output',
        'meta':{'selectedMeasures':[{'id':uuid.uuid4().hex,'name':'Plan Total','type':'DOUBLE','dataType':'NUMERIC'}]}}
    # This synthetic source has row/month grain and explicitly no external
    # storage Context. Live callers supply current owner/output evidence.
    proof=query_contract(query,[{'rows':['Region[Region]'],'columns':['Period[Month]'],'context':[]}],{})
    fields=numeric_output_fields(query,storage_context=proof);field=fields[0]
    model=load(ROOT/'fixtures/model.json')
    spec={'name':'Synthetic OneLake linked application '+uuid.uuid4().hex[:8],'queryFields':fields,
        'sheets':[
            {'name':'Source Plan','rows':['Region[Region]'],'columns':['Period[Month]'],
             'measures':[{'key':'input','kind':'DataInput','label':'Plan Input','default_value':{'Static':100},'min_value':{'Static':0}}]},
            {'name':'Review Plan','rows':['Region[Region]'],'columns':['Period[Month]'],
             'measures':[{'key':'query','kind':'Native','label':'Query Total','source':field['id']},
                         {'key':'double','kind':'Formula','label':'Double Total','formula':'${query} * 2'}]}],
        'dashboards':[
            {'name':'Source Dashboard','owner':'Source Plan','slicers':[{'field':'Region[Region]'}],
             'cards':[{'field':'Metrics[BasePay]','label':'Model context'}],
             'charts':[{'category':'Period[Month]','field':'Metrics[BasePay]','label':'Model context trend'}]},
            {'name':'Review Dashboard','owner':'Review Plan','slicers':[{'field':'Region[Region]'}],
             'cards':[{'field':field['id'],'label':'Plan Total','aggregation':'sum'}],
             'charts':[{'category':'Period[Month]','field':field['id'],'label':'Plan Total trend','aggregation':'sum'}]}]}
    b=build_application(model,spec)
    ident=b['identities'][0];prefix=f'sheets/{ident["sheetId"]}/visuals/{ident["visualId"]}/'
    source=b['raw'][prefix+'dataInput.json']['columns'][0]
    source={k:source[k] for k in ('measureGuid','name','columnMeta')}
    owner={'name':'Source Plan','visualId':'1','columns':[source],
        'properties':b['raw'][prefix+'properties.json']['properties']}
    direct=resolve_measure({'sourceType':'Visual','visualId':'1','sourceMeasureGuid':source['measureGuid'],
        'bucket':'ameasure','label':'Direct Plan Input'},sheets=[owner])
    qa=value_assignment(model,field['id'],Registry(),query_fields=fields)
    qa=resolve_measure({'sourceType':'InfoBridge','queryId':query['id'],'outputId':field['outputId'],
        'assignment':qa,'bucket':'ameasure'},queries=[query])
    assert_resolved(qa,query)
    save(destination/'construction.json',b)
    save(destination/'definition.json',b['envelope'])
    save(destination/'bindings.json',{'storageProfile':'OneLake','sourceRecord':source,'direct':direct,
        'queryMetadata':query,'query':qa,'runtime':'not-tested','network':'not-used'})
    return b

if __name__=='__main__':
    build(Path(sys.argv[1]));print('Built fresh synthetic application and both binding payloads from this package; no live deployment.')
