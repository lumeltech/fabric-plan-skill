import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest
from pathlib import Path
from runtime.powertable_factory import configured_table
from runtime.table_columns import column_config
from runtime.validate import Schemas,check_powertable_parts,validate_plan
from runtime.codec import load
from runtime.construct import build

ROOT=Path(__file__).resolve().parents[1]

class PowerTableAlmTests(unittest.TestCase):
    def test_complete_parts_and_source_links_without_foreign_ids(self):
        table={'name':'DimTest','schema':'dbo','physicalType':'U','primaryKey':['Key'],'columns':['Key']}
        conn={'connectionId':'00000000-0000-4000-8000-000000000001','dbHost':'sql.example.invalid',
            'dbName':'Test','artifactId':'00000000-0000-4000-8000-000000000002',
            'workspaceId':'00000000-0000-4000-8000-000000000003',
            'connectionName':'Demo connection','workspaceName':'Demo workspace','dbDisplayName':'Demo SQL'}
        col=column_config({'name':'Key','dbMeta':{'type':'int','isIdentity':False,'isNullable':False,
            'isPrimaryKey':True,'isUnique':True,'isCompositeUnique':False}},'integer')
        sheet,parts,ids=configured_table('Test',table,conn,[col],explicit=True)
        self.assertEqual(len(sheet['workloadItemEntityVisuals']),1)
        self.assertEqual(len(parts),5)
        properties=next(v for k,v in parts.items() if k.endswith('/properties.json'))
        self.assertEqual(properties['properties']['properties']['visualState']['manageMeasures'][0]['id'],'Key')
        self.assertNotIn('originEntityId',properties['properties']['properties'])
        settings=next(v for k,v in parts.items() if k.endswith('/sourceSettings.json'))['sourceSettings']
        self.assertTrue(all(s['sourceId']==ids['sourceGuid'] for s in settings))
        self.assertEqual([s['settings']['enabled'] for s in settings],[True,True,False])
        add=next(s for s in settings if s['name']=='ROW_ADD')
        update=next(s for s in settings if s['name']=='ROW_UPDATE')
        delete=next(s for s in settings if s['name']=='ROW_DELETE')
        for setting in (add,update):
            self.assertEqual(len(setting['filters']),1)
            self.assertEqual(setting['filters'][0]['name'],'all_users')
            self.assertEqual(setting['filters'][0]['filterType'],1)
            self.assertEqual(setting['filters'][0]['filter'],{})
            self.assertTrue(setting['filters'][0]['recordGuid'])
        self.assertNotIn('filters',delete)
        self.assertEqual((col['mandatory'],col['hideColumn'],col['allowEdit']),(1,0,1))
        schema=Schemas()
        for v in parts.values():schema.check(v,v['$schema'])
        prefix=next(k.rsplit('properties.json',1)[0] for k in parts if k.endswith('/properties.json'))
        self.assertEqual(check_powertable_parts(parts,prefix),
            {'sourceId':ids['sourceGuid'],'columns':1,'settings':3})

    def test_from_scratch_origin_is_preserved_after_approved_sql_creation(self):
        table={'name':'Employee','schema':'dbo','physicalType':'U','primaryKey':['EmployeeID'],'columns':['EmployeeID']}
        conn={'connectionId':'00000000-0000-4000-8000-000000000001','dbHost':'sql.example.invalid',
            'dbName':'Test','artifactId':'00000000-0000-4000-8000-000000000002',
            'workspaceId':'00000000-0000-4000-8000-000000000003',
            'connectionName':'Demo connection','workspaceName':'Demo workspace','dbDisplayName':'Demo SQL'}
        col=column_config({'name':'EmployeeID','dbMeta':{'type':'int','isIdentity':True,'isNullable':False,
            'isPrimaryKey':True,'isUnique':True,'isCompositeUnique':False}},'integer')
        _,parts,_=configured_table('Employees',table,conn,[col],explicit=True,creation_mode=1)
        source=next(v['source'] for k,v in parts.items() if k.endswith('/source.json'))
        self.assertEqual(source['creationMode'],1)
        with self.assertRaisesRegex(ValueError,'supported from-scratch'):
            configured_table('Employees',table,conn,[col],explicit=True,creation_mode=3)

    def test_source_and_column_identity_mismatches_are_rejected(self):
        table={'name':'DimTest','schema':'dbo','physicalType':'U','primaryKey':['Key'],'columns':['Key']}
        conn={'connectionId':'00000000-0000-4000-8000-000000000001','dbHost':'sql.example.invalid',
            'dbName':'Test','artifactId':'00000000-0000-4000-8000-000000000002',
            'workspaceId':'00000000-0000-4000-8000-000000000003',
            'connectionName':'Demo connection','workspaceName':'Demo workspace','dbDisplayName':'Demo SQL'}
        col=column_config({'name':'Key','dbMeta':{'type':'int','isIdentity':False,'isNullable':False,
            'isPrimaryKey':True,'isUnique':True,'isCompositeUnique':False}},'integer')
        _,parts,_=configured_table('Test',table,conn,[col],explicit=True)
        prefix=next(k.rsplit('properties.json',1)[0] for k in parts if k.endswith('/properties.json'))
        settings=parts[prefix+'sourceSettings.json']['sourceSettings']
        settings[0]['sourceId']='other'
        with self.assertRaises(ValueError):check_powertable_parts(parts,prefix)
        settings[0]['sourceId']=parts[prefix+'source.json']['source']['recordGuid']
        settings[0].pop('filters')
        with self.assertRaisesRegex(ValueError,'row-access selection'):
            check_powertable_parts(parts,prefix)
        settings[0]['filters']=[{'recordGuid':'filter-guid','name':'all_users','filterType':1,'filter':{}}]
        state=parts[prefix+'properties.json']['properties']['properties']['visualState']
        state['columnMeta']['Other']={'width':150}
        with self.assertRaises(ValueError):check_powertable_parts(parts,prefix)

    def test_full_plan_validation_checks_configured_powertable_companions(self):
        model=load(ROOT/'assets/fixtures/model.json');spec=load(ROOT/'assets/fixtures/capacity-spec.json')
        table={'name':'DimTest','schema':'dbo','physicalType':'U','primaryKey':['Key'],'columns':['Key']}
        conn={'connectionId':'00000000-0000-4000-8000-000000000001','dbHost':'sql.example.invalid',
            'dbName':'Test','artifactId':'00000000-0000-4000-8000-000000000002',
            'workspaceId':'00000000-0000-4000-8000-000000000003',
            'connectionName':'Demo connection','workspaceName':'Demo workspace','dbDisplayName':'Demo SQL'}
        col=column_config({'name':'Key','dbMeta':{'type':'int','isIdentity':False,'isNullable':False,
            'isPrimaryKey':True,'isUnique':True,'isCompositeUnique':False}},'integer')
        sheet,parts,_=configured_table('Test',table,conn,[col],explicit=True)
        built=build(model,spec);raw=built['raw'];raw['definition.json']['sheets'].append(sheet);raw.update(parts)
        self.assertEqual(validate_plan(raw)['sheets'],2)
