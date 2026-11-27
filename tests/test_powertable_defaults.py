"""PowerTable product defaults, catalog intake, Forms, Automations and Row access."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import copy,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from runtime.codec import load,pack,parts,unpack
from runtime.construct import build
from runtime.powertable_config import backfill_row_access
from runtime.powertable_factory import add_table_to_definition,table_from_request
from runtime.powertable_features import add_features,automation_record,form_record
from runtime.sql_definition import catalog_table,physical_table
from runtime.table_columns import column_config,default_kind,table_column_configs
from runtime.validate import check_powertable_parts,schema_report,validate_plan

ROOT=Path(__file__).resolve().parents[1]
CONN={'connectionId':'00000000-0000-4000-8000-000000000001','dbHost':'sql.example.invalid','dbName':'Test',
      'artifactId':'00000000-0000-4000-8000-000000000002','workspaceId':'00000000-0000-4000-8000-000000000003',
      'connectionName':'Demo connection','workspaceName':'Demo workspace','dbDisplayName':'Demo SQL'}

def row(i,name,typ,ml=0,p=0,s=0,null=0,ident=0,pk=0,computed=0):
    return {'schema_name':'dbo','table_name':'Employee','physical_type':'U ','column_id':i,'column_name':name,'type_name':typ,
            'max_length':ml,'precision':p,'scale':s,'is_nullable':null,'is_identity':ident,'is_computed':computed,'is_primary_key':pk}

def rows():
    return [row(1,'EmployeeID','int',4,10,0,ident=1,pk=1),row(2,'Code','varchar',20),row(3,'FullName','nvarchar',-1),
            row(4,'JoinDate','date',3,10,0),row(5,'LastLogin','datetime2',8,27,7,null=1),row(6,'Active','bit',1,1,0),
            row(7,'Salary','decimal',9,18,2,null=1),row(8,'Department','varchar',50,null=1)]

UNIQUE=[{'index_name':'UQ_Code','is_primary_key':0,'column_name':'Code','key_ordinal':1}]

def request(**extra):
    return {'name':'Employees','connection':CONN,'catalog':{'schema':'dbo','table':'Employee','rows':rows(),'unique_rows':UNIQUE},**extra}

def columns_of(raw):
    return next(v for k,v in raw.items() if k.endswith('/columnConfigs.json'))['columnConfigs']

def prefix_of(raw):
    return next(k.rsplit('columnConfigs.json',1)[0] for k in raw if k.endswith('/columnConfigs.json'))

def mail(to='hr@example.com'):
    return {'type':'SEND_MAIL','config':{'subject':'New hire','body':'A row was added.','to':[to]}}

class ColumnDefaults(unittest.TestCase):
    def test_product_sql_type_map(self):
        expected={'varchar':'text','nvarchar':'text','char':'text','nchar':'text','text':'text',
                  'int':'integer','bigint':'integer','smallint':'integer','decimal':'decimal','numeric':'decimal',
                  'float':'decimal','money':'decimal','date':'date','datetime':'datetime','datetime2':'datetime',
                  'smalldatetime':'datetime','bit':'checkbox','NVARCHAR(MAX)':'text','datetime2(7)':'datetime',
                  'smallmoney':'decimal','real':'decimal','datetimeoffset':'datetime',
                  'uniqueidentifier':'text','xml':'text','varbinary':'text','time':'text'}
        for sql,kind in expected.items():self.assertEqual(default_kind(sql),kind,sql)
        for sql in ('timestamp','rowversion'):
            with self.assertRaisesRegex(ValueError,'No PowerTable default'):default_kind(sql)

    def test_float_shows_one_decimal_and_other_decimal_types_two(self):
        meta={'isIdentity':False,'isNullable':True,'isPrimaryKey':False,'isUnique':False,'isCompositeUnique':False}
        for sql,places in (('float',1),('decimal',2),('money',2),('real',2)):
            with self.subTest(sql=sql):
                c=column_config({'name':'Value','dbMeta':{**meta,'type':sql}})
                self.assertEqual(c['columnMeta']['noOfDecimals'],places)

    def test_catalog_table_gets_text_date_datetime_checkbox_and_displayed_key(self):
        _,raw,ids=table_from_request(request())
        cols={c['columnName']:c for c in columns_of(raw)}
        self.assertEqual(ids['columnTypes'],{'EmployeeID':6,'Code':1,'FullName':1,'JoinDate':4,'LastLogin':12,
                                             'Active':11,'Salary':13,'Department':1})
        for name in ('Code','FullName','Department'):
            meta=cols[name]['columnMeta']
            self.assertEqual((cols[name]['visualColumnType'],meta['textFieldColumnType'],meta['maximumAllowedLength']),(1,'Any Value',''))
            self.assertNotIn('selectionMethod',meta)
        self.assertTrue(all(c['hideColumn']==0 for c in cols.values()))
        key=cols['EmployeeID']
        # The product makes a NOT NULL or primary-key column mandatory, identity or not.
        self.assertEqual((key['allowEdit'],key['mandatory'],key['columnMeta']['isPrimaryKey']),(0,1,True))
        self.assertEqual((cols['LastLogin']['columnMeta']['format'],cols['LastLogin']['columnMeta']['timeZone']),('DEFAULT_LOCALE_TIME',''))
        self.assertEqual(cols['JoinDate']['columnMeta']['format'],'DEFAULT_LOCALE')
        self.assertNotIn('timeZone',cols['JoinDate']['columnMeta'])
        self.assertEqual((cols['Active']['columnMeta']['checkedValue'],cols['Active']['columnMeta']['unCheckedValue']),('1','0'))
        self.assertTrue(cols['Code']['columnMeta']['dbMeta']['isUnique'])
        self.assertEqual(cols['Code']['columnMeta']['dbMeta']['maxLength'],20)
        self.assertEqual((cols['Salary']['columnMeta']['dbMeta']['numericPrecision'],cols['Salary']['columnMeta']['dbMeta']['numericScale']),(18,2))
        self.assertTrue(all(r['status'].startswith('passed') for r in schema_report(raw)))

    def test_single_select_lookup_and_hide_are_explicit_overrides(self):
        overrides={'Department':{'kind':'text-options'},'Salary':{'hide':True,'decimals':0},
                   'LastLogin':{'time_zone':'user-local'},'Code':{'display_name':'Employee code'}}
        _,raw,_=table_from_request(request(columns=overrides))
        cols={c['columnName']:c for c in columns_of(raw)}
        self.assertEqual((cols['Department']['columnType'],cols['Department']['columnMeta']['selectionMethod']),(2,'DISTINCT_VALUES'))
        self.assertEqual((cols['Salary']['hideColumn'],cols['Salary']['columnMeta']['noOfDecimals']),(1,0))
        self.assertEqual(cols['LastLogin']['columnMeta']['timeZone'],'user-local')
        self.assertEqual(cols['Code']['displayName'],'Employee code')
        with self.assertRaisesRegex(ValueError,'unknown column'):table_from_request(request(columns={'Missing':{'hide':True}}))
        with self.assertRaisesRegex(ValueError,'Unsupported column override'):table_from_request(request(columns={'Code':{'width':3}}))

    def test_kind_and_type_compatibility(self):
        date={'name':'D','dbMeta':{'type':'date','isIdentity':False,'isNullable':True,'isPrimaryKey':False,'isUnique':False,'isCompositeUnique':False}}
        with self.assertRaisesRegex(ValueError,'incompatible'):column_config(date,'datetime')
        with self.assertRaisesRegex(ValueError,'time_zone'):column_config(date,'date',time_zone='user-local')
        stamp=copy.deepcopy(date);stamp['dbMeta']['type']='datetime'
        self.assertEqual(column_config(stamp)['columnType'],12)
        self.assertEqual(column_config(stamp,'date')['columnType'],4)
        with self.assertRaisesRegex(ValueError,'time_zone must be'):column_config(stamp,time_zone='UTC')

    def test_computed_columns_stay_read_only(self):
        data=rows()+[row(9,'Tenure','int',4,10,0,computed=1)]
        table=catalog_table(data,UNIQUE,schema='dbo',table='Employee')
        cols={c['columnName']:c for c in table_column_configs(table)}
        self.assertEqual((cols['Tenure']['allowEdit'],cols['Tenure']['mandatory']),(0,1))
        with self.assertRaisesRegex(ValueError,'Computed'):table_column_configs(table,{'Tenure':{'allow_edit':True}})

class CatalogAndParser(unittest.TestCase):
    def test_catalog_flags_accept_text_and_reject_foreign_rows(self):
        data=[{k:(str(v) if k.startswith('is_') else v) for k,v in r.items()} for r in rows()]
        table=catalog_table(data,[],schema='dbo',table='Employee')
        self.assertEqual(table['primaryKey'],['EmployeeID'])
        self.assertTrue(table['columns'][0]['dbMeta']['isIdentity'])
        other=rows();other[1]['table_name']='Other'
        with self.assertRaisesRegex(ValueError,'different table'):catalog_table(other,[],schema='dbo',table='Employee')
        with self.assertRaisesRegex(ValueError,'Unique-index rows required'):catalog_table(rows(),None,schema='dbo',table='Employee')
        nokey=[dict(r,is_primary_key=0) for r in rows()]
        with self.assertRaisesRegex(ValueError,'primary key'):catalog_table(nokey,[],schema='dbo',table='Employee')

    def test_composite_unique_from_index_rows(self):
        unique=[{'index_name':'UQ_Pair','is_primary_key':0,'column_name':'Code','key_ordinal':1},
                {'index_name':'UQ_Pair','is_primary_key':0,'column_name':'Department','key_ordinal':2},
                {'index_name':'PK','is_primary_key':1,'column_name':'EmployeeID','key_ordinal':1}]
        cols={c['name']:c['dbMeta'] for c in catalog_table(rows(),unique,schema='dbo',table='Employee')['columns']}
        self.assertEqual((cols['Code']['isUnique'],cols['Code']['isCompositeUnique']),(False,True))
        self.assertFalse(cols['EmployeeID']['isUnique'])

    def test_sqlproj_parser_reads_varchar_datetime_bit_and_max(self):
        sql="""CREATE TABLE [dbo].[Employee] (
    [EmployeeID] BIGINT IDENTITY (1, 1) NOT NULL,
    [Code] VARCHAR (20) NOT NULL,
    [Notes] NVARCHAR (MAX) NULL,
    [LastLogin] DATETIME2 (7) NULL,
    [Active] BIT NOT NULL,
    [Rate] NUMERIC (10) NULL,
    CONSTRAINT [PK] PRIMARY KEY CLUSTERED ([EmployeeID] ASC)
);"""
        cols={c['name']:c['dbMeta'] for c in physical_table(sql,'dbo','Employee')['columns']}
        self.assertEqual(cols['Code']['maxLength'],20)
        self.assertEqual(cols['Notes']['maxLength'],-1)
        self.assertEqual(cols['LastLogin']['type'],'datetime2')
        self.assertEqual((cols['Rate']['numericPrecision'],cols['Rate']['numericScale']),(10,0))
        self.assertEqual(default_kind(cols['Active']['type']),'checkbox')

class FormsAndAutomations(unittest.TestCase):
    def setUp(self):
        _,self.raw,_=table_from_request(request())
        self.columns=columns_of(self.raw)
        self.guids={c['columnName']:c['recordGuid'] for c in self.columns}

    def test_form_references_column_record_guids(self):
        form=form_record('New employee',[{'column':'Code'},{'column':'FullName'},{'column':'JoinDate'},
                                         {'column':'Active','defaultValue':True},{'column':'Department','description':'Team'}],self.columns)
        self.assertEqual([f['columnConfigId'] for f in form['formFields']],[self.guids[n] for n in ('Code','FullName','JoinDate','Active','Department')])
        self.assertTrue(all(f['formId']==form['recordGuid'] for f in form['formFields']))
        children=form['layoutMeta']['children']
        self.assertEqual([c['dataKey'] for c in children],[f['columnConfigId'] for f in form['formFields']])
        self.assertEqual((form['layoutMeta']['type'],form['layoutMeta']['status']),('form',10))
        self.assertEqual([f['required'] for f in form['formFields']],[1,1,1,1,0])
        self.assertEqual([f['defaultValue'] for f in form['formFields']],['','','','true',''])

    def test_form_requires_mandatory_and_editable_columns(self):
        with self.assertRaisesRegex(ValueError,'every mandatory column: FullName, JoinDate, Active'):
            form_record('Partial',[{'column':'Code'}],self.columns)
        with self.assertRaisesRegex(ValueError,'read-only'):
            form_record('Key',[{'column':'EmployeeID'}],self.columns)
        with self.assertRaisesRegex(ValueError,'cannot be optional'):
            form_record('Loose',[{'column':c,'mandatory':0} for c in ('Code','FullName','JoinDate','Active')],self.columns)

    def test_automation_is_a_linked_action_block(self):
        record=automation_record('Notify HR',ROW_UPDATED,[mail(),mail('{{trigger.record.Email}}')],self.columns,
                                 watch_columns=['Active'],conditions={'combinator':'and','rules':[{'field':'Active','operator':'equals','value':True}]})
        config=record['config'];group=config['groups'][config['entryGroupId']]
        first=group['actions'][group['entryActionId']];second=group['actions'][first['nextActionId']]
        self.assertEqual((record['triggerType'],config['trigger']['triggerType'],group['groupType'],first['actionType']),(2,'2','1','5'))
        self.assertEqual((second['previousActionId'],second['nextActionId']),(first['actionId'],None))
        self.assertEqual(config['trigger']['triggerConfig']['watchColumns'],['Active'])
        self.assertEqual(config['trigger']['triggerConfig']['conditions']['rules'][0]['fieldDataType'],'boolean')
        with self.assertRaisesRegex(ValueError,'only to ROW_UPDATED'):
            automation_record('Bad',ROW_CREATED,[mail()],self.columns,watch_columns=['Active'])
        with self.assertRaisesRegex(ValueError,'Conditions support'):
            automation_record('Bad',ROW_CREATED,[mail()],self.columns,conditions={'combinator':'and','rules':[{'field':'JoinDate','operator':'empty'}]})
        with self.assertRaisesRegex(ValueError,'email address'):automation_record('Bad',ROW_CREATED,[mail('nobody')],self.columns)
        with self.assertRaisesRegex(ValueError,'Trigger must be'):automation_record('Bad','SCHEDULED',[mail()],self.columns)

    def test_features_added_to_export_keep_other_parts(self):
        model=load(ROOT/'assets/fixtures/model.json');spec=load(ROOT/'assets/fixtures/capacity-spec.json')
        base=build(model,spec)['raw'];sheet,new,ids=table_from_request(request())
        envelope=add_table_to_definition(pack(base),sheet,new)
        before=parts(envelope)
        self.assertEqual(validate_plan(unpack(envelope))['sheets'],2)
        fields=[{'column':c} for c in ('Code','FullName','JoinDate','Active')]
        candidate,manifest=add_features(envelope,sheet_guid=ids['sheetGuid'],forms=[{'title':'New employee','fields':fields}],
                                        automations=[{'name':'Notify HR','trigger':'ROW_CREATED','actions':[mail()]}])
        after=parts(candidate)
        self.assertEqual(sorted(p.rsplit('/',1)[-1] for p in manifest['addedParts']),['automations.json','forms.json'])
        self.assertTrue(all(after[p]==b for p,b in before.items()))
        again,manifest=add_features(candidate,sheet_guid=ids['sheetGuid'],forms=[{'title':'Second form','fields':fields}])
        self.assertEqual([p.rsplit('/',1)[-1] for p in manifest['changedParts']],['forms.json'])
        forms=next(v for k,v in unpack(again).items() if k.endswith('/forms.json'))['forms']
        self.assertEqual([f['title'] for f in forms],['New employee','Second form'])
        with self.assertRaisesRegex(ValueError,'already exists'):
            add_features(again,sheet_guid=ids['sheetGuid'],forms=[{'title':'new EMPLOYEE','fields':fields}])
        self.assertEqual(validate_plan(unpack(again))['sheets'],2)

    def test_form_warns_when_rows_cannot_be_added(self):
        model=load(ROOT/'assets/fixtures/model.json');spec=load(ROOT/'assets/fixtures/capacity-spec.json')
        sheet,new,ids=table_from_request(request(allow_add=False))
        envelope=add_table_to_definition(pack(build(model,spec)['raw']),sheet,new)
        fields=[{'column':c} for c in ('Code','FullName','JoinDate','Active')]
        _,manifest=add_features(envelope,sheet_guid=ids['sheetGuid'],forms=[{'title':'Intake','fields':fields}])
        self.assertIn('ROW_ADD',manifest['warnings'][0])

    def test_validation_of_existing_feature_parts(self):
        raw=copy.deepcopy(self.raw);prefix=prefix_of(raw)
        raw[prefix+'approvals.json']={'$schema':'x','approvals':{'recordGuid':'a','approvalLevels':[]}}
        with self.assertRaisesRegex(ValueError,'approvalLevels and approvalFilter'):check_powertable_parts(raw,prefix)
        raw[prefix+'approvals.json']['approvals']['approvalFilter']=[]
        self.assertEqual(check_powertable_parts(raw,prefix)['approvals'],1)
        form=form_record('F',[{'column':c} for c in ('Code','FullName','JoinDate','Active')],self.columns)
        form['formFields'][0]['columnConfigId']='stale'
        raw[prefix+'forms.json']={'forms':[form]}
        with self.assertRaisesRegex(ValueError,'unknown column'):check_powertable_parts(raw,prefix)

    def test_product_export_shapes_validate_and_can_be_extended(self):
        # Shapes emitted by the product's ALM export: string configs, an empty layout,
        # a field whose column was deleted, and automations without recordGuid.
        model=load(ROOT/'assets/fixtures/model.json');spec=load(ROOT/'assets/fixtures/capacity-spec.json')
        sheet,new,ids=table_from_request(request());prefix=prefix_of(new);source=ids['sourceGuid']
        legacy=automation_record('Legacy',ROW_CREATED,[mail()],self.columns)
        new[prefix+'automations.json']={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/PowerTable/Automations/1.0.0/schema.json',
            'automations':[{'name':'Legacy','triggerType':1,'config':json.dumps(legacy['config']),'sourceId':source}]}
        new[prefix+'forms.json']={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/PowerTable/Forms/1.0.0/schema.json',
            'forms':[{'sourceId':source,'recordGuid':'form-1','title':'Old form','description':'','restrictMultipleEntry':0,'logo':None,
                      'layoutMeta':{},'config':'{"showTitle":true}',
                      'formFields':[{'recordGuid':'field-1','columnConfigId':new[prefix+'columnConfigs.json']['columnConfigs'][1]['recordGuid'],
                                     'description':'','required':1,'defaultValue':'','formId':'form-1'},
                                    {'recordGuid':'field-2','description':'','required':0,'defaultValue':'','formId':'form-1'}]}]}
        raw=build(model,spec)['raw'];raw['definition.json']['sheets'].append(sheet);raw.update(new)
        self.assertEqual(validate_plan(raw)['sheets'],2)
        envelope=pack(raw)
        fields=[{'column':c} for c in ('Code','FullName','JoinDate','Active')]
        candidate,manifest=add_features(envelope,sheet_guid=ids['sheetGuid'],forms=[{'title':'New form','fields':fields}],
                                        automations=[{'name':'Second','trigger':'ROW_DELETED','actions':[mail()]}])
        self.assertEqual(sorted(p.rsplit('/',1)[-1] for p in manifest['changedParts']),['automations.json','forms.json'])
        self.assertTrue(any('recordGuid' in w and 'Legacy' in w for w in manifest['warnings']))
        merged=unpack(candidate)
        self.assertEqual(merged[prefix+'forms.json']['forms'][0],new[prefix+'forms.json']['forms'][0])
        self.assertEqual([a['name'] for a in merged[prefix+'automations.json']['automations']],['Legacy','Second'])
        self.assertEqual(validate_plan(merged)['sheets'],2)
        _,manifest=backfill_row_access(candidate)
        self.assertTrue(manifest['warnings'])

ROW_CREATED,ROW_UPDATED='ROW_CREATED','ROW_UPDATED'

class RowAccess(unittest.TestCase):
    def test_backfill_only_enabled_actions_without_selection(self):
        model=load(ROOT/'assets/fixtures/model.json');spec=load(ROOT/'assets/fixtures/capacity-spec.json')
        sheet,new,ids=table_from_request(request(allow_delete=True))
        prefix=prefix_of(new);settings=new[prefix+'sourceSettings.json']['sourceSettings']
        for setting in settings:
            if setting['name'] in ('ROW_ADD','ROW_DELETE'):setting.pop('filters')
        kept=copy.deepcopy(next(s for s in settings if s['name']=='ROW_UPDATE'))
        raw=build(model,spec)['raw'];raw['definition.json']['sheets'].append(sheet);raw.update(new)
        envelope=pack(raw)
        candidate,manifest=backfill_row_access(envelope)
        self.assertEqual(sorted(f['setting'] for f in manifest['filled']),['ROW_ADD','ROW_DELETE'])
        result=unpack(candidate)[prefix+'sourceSettings.json']['sourceSettings']
        for setting in result:
            self.assertEqual([(f['name'],f['filterType'],f['filter']) for f in setting['filters']],[('all_users',1,{})])
        self.assertEqual(next(s for s in result if s['name']=='ROW_UPDATE'),kept)
        self.assertEqual([p for p in parts(envelope) if parts(envelope)[p]!=parts(candidate)[p]],[prefix+'sourceSettings.json'])
        again,manifest=backfill_row_access(candidate)
        self.assertEqual((manifest['filled'],again),([],candidate))

class CommandLine(unittest.TestCase):
    def test_powertable_table_command_appends_to_baseline(self):
        model=load(ROOT/'assets/fixtures/model.json');spec=load(ROOT/'assets/fixtures/capacity-spec.json')
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);(tmp/'request.json').write_text(json.dumps(request()),encoding='utf-8')
            (tmp/'baseline.json').write_text(json.dumps(pack(build(model,spec)['raw'])),encoding='utf-8')
            result=subprocess.run([sys.executable,str(ROOT/'scripts/plan.py'),'powertable-table','--input',str(tmp/'request.json'),
                                   '--baseline',str(tmp/'baseline.json'),'--out',str(tmp/'out')],capture_output=True,text=True,cwd=ROOT,
                                  env={**os.environ,'FABRIC_SKILL_OFFLINE_TEST':'1'})
            self.assertEqual(result.returncode,0,result.stderr)
            candidate=unpack(load(tmp/'out/definition.json'))
            self.assertEqual(validate_plan(candidate)['sheets'],2)
            self.assertEqual(load(tmp/'out/changes.json')['columnTypes']['LastLogin'],12)

if __name__=='__main__':unittest.main()
