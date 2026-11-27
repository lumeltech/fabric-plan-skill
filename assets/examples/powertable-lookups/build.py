"""Offline Supply Policy example. All identities and catalogs here are illustrative."""
from pathlib import Path
import copy,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.codec import pack,save
from runtime.table_columns import column_config
from runtime.powertable_factory import configured_table
from runtime.powertable_config import repair_definition

def dbmeta(identity=False):
    return {'type':'int','isIdentity':identity,'isNullable':False,'isPrimaryKey':identity,
            'isUnique':identity,'isCompositeUnique':False}

def sample():
    conn={'connectionId':'00000000-0000-4000-8000-000000000001','artifactId':'00000000-0000-4000-8000-000000000002',
          'workspaceId':'00000000-0000-4000-8000-000000000003','dbHost':'sql.example.invalid','dbName':'IllustrativeSQL',
          'connectionName':'Illustrative connection','workspaceName':'Illustrative workspace','dbDisplayName':'Illustrative SQL'}
    columns=[column_config({'name':'PolicyID','dbMeta':dbmeta(True)},'integer')]
    names=['ProductID','RegionID','MonthID','ScenarioID']
    columns += [column_config({'name':n,'dbMeta':dbmeta()},'integer',allow_edit=False) for n in names]
    columns += [column_config({'name':'SafetyStockUnits','dbMeta':dbmeta()},'integer')]
    table={'name':'SupplyPolicy','schema':'dbo','physicalType':'U','primaryKey':['PolicyID'],
           'columns':['PolicyID',*names,'SafetyStockUnits']}
    lookups={name:{'schema':'dbo','table':table,'key':name,'label':label} for name,table,label in
             [('ProductID','Product','ProductCode'),('RegionID','Region','RegionCode'),
              ('MonthID','Month','MonthName'),('ScenarioID','Scenario','ScenarioCode')]}
    lookups['RegionID']['chain']=[{'column':'CurrencyID','schema':'dbo','table':'Currency','key':'CurrencyID','label':'CurrencyCode'}]
    catalog=[]
    for key,remote_table,label in [('ProductID','Product','ProductCode'),('RegionID','Region','RegionCode'),
                            ('MonthID','Month','MonthName'),('ScenarioID','Scenario','ScenarioCode'),
                            ('CurrencyID','Currency','CurrencyCode')]:
        remote=[{'name':key,'type':'int','isPrimaryKey':True},{'name':label,'type':'nvarchar'}]
        if remote_table=='Region':remote.append({'name':'CurrencyID','type':'int'})
        catalog.append({'schema':'dbo','table':remote_table,'columns':remote})
    source_metadata={'connection':{'id':conn['connectionId'],'displayName':conn['connectionName']},
                     'workspace':{'id':conn['workspaceId'],'displayName':conn['workspaceName']},
                     'database':{'id':conn['artifactId'],'displayName':conn['dbDisplayName'],'workspaceId':conn['workspaceId']}}
    sheet,raw,ids=configured_table('Supply Policy',table,conn,columns,explicit=True,allow_add=False)
    source_path=next(p for p in raw if p.endswith('/source.json'))
    # Reproduce only the omitted configuration, not a copied live report.
    raw[source_path]['source']['meta']={'totalRows':12}
    baseline=pack({'definition.json':{'sheets':[sheet]},**raw,
                   'infobridge.json':{'illustrativeUntouchedNativeId':9007199254740993123}})
    request={'sheet_guid':ids['sheetGuid'],'lookups':lookups,'lookup_catalog':catalog,'source_metadata':source_metadata}
    return baseline,request,{'table':table,'connection':conn,'columns':columns}

def main(out):
    baseline,request,inputs=sample()
    candidate,manifest=repair_definition(baseline,**request)
    save(out/'baseline.json',baseline);save(out/'repair.request.json',request)
    save(out/'candidate.json',candidate);save(out/'changes.json',manifest)
    # New authoring uses the same constructor with explicit read-only lookup keys.
    columns=[column_config({'name':c['columnName'],'dbMeta':c['columnMeta']['dbMeta']},'database-lookup',
                           lookup=request['lookups'][c['columnName']],lookup_catalog=request['lookup_catalog'],allow_edit=False)
             if c['columnName'] in request['lookups'] else copy.deepcopy(c) for c in inputs['columns']]
    sheet,raw,_=configured_table('New Supply Policy',inputs['table'],inputs['connection'],columns,explicit=True,allow_add=False)
    save(out/'new-configured-table.json',pack({'definition.json':{'sheets':[sheet]},**raw}))
    print('Created offline lookup/source examples; no network, row changes or deployment.')

if __name__=='__main__':main(Path(sys.argv[1]))
