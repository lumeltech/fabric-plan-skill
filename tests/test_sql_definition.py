import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import base64,unittest
from runtime.sql_definition import read_sql_project,physical_table

class SQLDefinition(unittest.TestCase):
    def test_primary_key_is_not_always_identity(self):
        sql="""CREATE TABLE [dbo].[Product] (
    [ProductID] INT NOT NULL,
    [Code] NVARCHAR(20) NOT NULL,
    [Price] DECIMAL(19,4) NOT NULL,
    CONSTRAINT [PK] PRIMARY KEY CLUSTERED ([ProductID] ASC),
    CONSTRAINT [UQ] UNIQUE NONCLUSTERED ([Code] ASC)
);"""
        cols={c['name']:c['dbMeta'] for c in physical_table(sql,'dbo','Product')['columns']}
        self.assertTrue(cols['ProductID']['isPrimaryKey'])
        self.assertFalse(cols['ProductID']['isIdentity'])
        self.assertTrue(cols['Code']['isUnique'])
        self.assertEqual(cols['Code']['maxLength'],40)
        self.assertEqual(cols['Price']['numericScale'],4)
        identity=sql.replace('[ProductID] INT NOT NULL','[ProductID] INT IDENTITY (1, 1) NOT NULL')
        self.assertTrue(physical_table(identity,'dbo','Product')['columns'][0]['dbMeta']['isIdentity'])

    def test_unknown_column_definition_fails(self):
        sql="""CREATE TABLE [dbo].[T] (
    [ID] XML NOT NULL,
    CONSTRAINT [PK] PRIMARY KEY CLUSTERED ([ID] ASC)
);"""
        with self.assertRaises(ValueError):physical_table(sql,'dbo','T')
        with self.assertRaises(ValueError):physical_table(sql.replace('XML','INT DEFAULT 1'),'dbo','T')

    def test_definition_endpoint_and_unsafe_part(self):
        class Fake:
            def request(self,*args,**kwargs):self.args=args;return {}
            def finish(self,*args):
                return {'body':{'definition':{'parts':[{'path':self.path,'payloadType':'InlineBase64','payload':base64.b64encode(b'schema').decode()}]}}}
        client=Fake();client.path='dbo/Tables/T.sql'
        _,parts=read_sql_project(client,'workspace','database','schema')
        self.assertEqual(parts[client.path],'schema')
        self.assertEqual(client.args[1],'/workspaces/workspace/sqlDatabases/database/getDefinition?format=sqlproj')
        for path in ['../unsafe','C:/unsafe','/unsafe']:
            client.path=path
            with self.assertRaises(ValueError):read_sql_project(client,'workspace','database','schema')

if __name__=='__main__':unittest.main()
