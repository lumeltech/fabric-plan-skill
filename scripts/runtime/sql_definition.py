"""Read physical SQL table definitions through the authorized Fabric item API.

This is metadata export only: no SQL token, connection creation, DDL or row write.
The official API requires SQL database read/write permission. A successful SQL
project export establishes schema, not PowerTable credential or row-save access.
"""
import base64,re
from pathlib import PurePosixPath

def read_sql_project(client,workspace,database,label):
    response=client.request('POST',f'/workspaces/{workspace}/sqlDatabases/{database}/getDefinition?format=sqlproj',label=label)
    envelope=client.finish(response,label)['body']
    parts=envelope.get('definition',envelope).get('parts',[]);decoded={}
    if not parts:raise ValueError('SQL project definition is empty')
    for part in parts:
        path=PurePosixPath(part['path'])
        if path.is_absolute() or '..' in path.parts or '\\' in str(path) or ':' in str(path):raise ValueError('Unsafe SQL project path')
        if part.get('payloadType')!='InlineBase64':raise ValueError('Unsupported SQL project payload')
        if str(path) in decoded:raise ValueError('Duplicate SQL project part')
        decoded[str(path)]=base64.b64decode(part['payload'],validate=True).decode('utf-8-sig')
    return envelope,decoded

SQL_TYPES=r'BIGINT|SMALLINT|TINYINT|INT|BIT|DATETIME2|SMALLDATETIME|DATETIME|DATE|NVARCHAR|VARCHAR|NCHAR|CHAR|DECIMAL|NUMERIC|FLOAT|REAL|SMALLMONEY|MONEY'
TEXT_BYTES={'NVARCHAR':2,'NCHAR':2,'VARCHAR':1,'CHAR':1}

def physical_table(sql,schema,table):
    """Conservative parser for ordinary INT/BIT/DATE/DATETIME/text/decimal tables.

    Additional SQL syntax fails instead of inventing key/identity/null metadata.
    Constraints remain database-owned and are retained in the exported SQL text.
    Text ``maxLength`` is in bytes, as in ``sys.columns``: twice the declared
    length for NVARCHAR/NCHAR, the declared length for VARCHAR/CHAR, -1 for MAX.
    """
    prefix=f'CREATE TABLE [{schema}].[{table}]'
    if not sql.lstrip().startswith(prefix):raise ValueError('Expected physical CREATE TABLE definition')
    pk_match=re.search(r'PRIMARY KEY (?:CLUSTERED|NONCLUSTERED) \(([^)]+)\)',sql)
    if not pk_match:raise ValueError('Explicit primary key required')
    pk=re.findall(r'\[([^]]+)\]',pk_match[1]);unique=[re.findall(r'\[([^]]+)\]',g) for g in re.findall(r'UNIQUE (?:CLUSTERED|NONCLUSTERED) \(([^)]+)\)',sql)]
    lines=[s for s in sql.splitlines() if re.match(r'^\s+\[[^]]+\]\s+',s)]
    columns=[]
    for line in lines:
        match=re.match(r'^\s+\[([^]]+)\]\s+('+SQL_TYPES+r')\b\s*(\([^)]*\))?(.*)',line,re.IGNORECASE)
        if not match:raise ValueError('Unsupported physical SQL column syntax')
        name,typ,size,tail=match.groups();typ=typ.upper()
        if not re.fullmatch(r'\s*(?:IDENTITY\s*\(\d+,\s*\d+\)\s*)?(?:NOT NULL|NULL),?\s*',tail,re.IGNORECASE):raise ValueError('Unparsed physical SQL column attributes')
        meta={'type':typ.lower(),'isIdentity':'IDENTITY' in tail.upper(),'isNullable':'NOT NULL' not in tail.upper(),
          'isPrimaryKey':name in pk,'isUnique':any(g==[name] for g in unique),'isCompositeUnique':any(name in g and len(g)>1 for g in unique)}
        if typ in ('DECIMAL','NUMERIC'):
            values=[int(x) for x in re.findall(r'\d+',size or '')]
            if len(values) not in (1,2):raise ValueError('Decimal precision and scale required')
            meta.update(numericPrecision=values[0],numericScale=values[1] if len(values)==2 else 0)
        if typ in TEXT_BYTES:
            if size and re.fullmatch(r'\(\s*MAX\s*\)',size,re.IGNORECASE):meta['maxLength']=-1
            elif size and re.fullmatch(r'\(\d+\)',size):meta['maxLength']=TEXT_BYTES[typ]*int(size[1:-1])
            else:raise ValueError('Explicit text length or MAX required')
        columns.append({'name':name,'dbMeta':meta})
    names=[x['name'] for x in columns]
    if not columns or len(names)!=len(set(names)) or not set(pk)<=set(names):raise ValueError('Incomplete physical schema')
    return {'schema':schema,'name':table,'physicalType':'U','primaryKey':pk,'columns':columns}

def _flag(value,label):
    if isinstance(value,bool):return value
    if isinstance(value,int) and value in (0,1):return bool(value)
    if isinstance(value,str) and value.strip().lower() in ('0','1','true','false'):return value.strip().lower() in ('1','true')
    raise ValueError('Catalog flag must be 0/1 or Boolean: '+label)

def _number(value,label):
    if isinstance(value,bool):raise ValueError('Catalog number required: '+label)
    if isinstance(value,int):return value
    if isinstance(value,str) and re.fullmatch(r'-?\d+',value.strip()):return int(value)
    raise ValueError('Catalog number required: '+label)

def catalog_table(rows,unique_rows,*,schema,table):
    """Physical table metadata from sqldb-cli catalog results.

    ``rows`` are the result of ``surfaces.PHYSICAL_METADATA_SQL`` and
    ``unique_rows`` the result of ``surfaces.UNIQUE_METADATA_SQL`` for the same
    table (an empty list means the query ran and found no unique index). Both
    are read-only catalog queries; nothing here connects to the database.
    """
    if not isinstance(rows,list) or not rows:raise ValueError('Catalog rows required; run PHYSICAL_METADATA_SQL through sqldb-cli')
    if not isinstance(unique_rows,list):raise ValueError('Unique-index rows required; run UNIQUE_METADATA_SQL (empty list if none)')
    for row in rows:
        if not isinstance(row,dict) or row.get('schema_name')!=schema or row.get('table_name')!=table:
            raise ValueError('Catalog row belongs to a different table')
        if str(row.get('physical_type','')).strip().upper()!='U':raise ValueError('Catalog object is not a user base table')
    ordered=sorted(rows,key=lambda r:_number(r.get('column_id'),'column_id'))
    names=[r.get('column_name') for r in ordered]
    if any(not isinstance(n,str) or not n for n in names) or len(set(names))!=len(names):raise ValueError('Invalid or duplicate catalog column name')
    groups={}
    for row in unique_rows:
        if not isinstance(row,dict) or row.get('column_name') not in names or not isinstance(row.get('index_name'),str):
            raise ValueError('Unique-index row does not match the catalog columns')
        if _flag(row.get('is_primary_key',0),'is_primary_key'):continue
        groups.setdefault(row['index_name'],[]).append(row['column_name'])
    columns=[]
    for row in ordered:
        name=row['column_name'];typ=row.get('type_name')
        if not isinstance(typ,str) or not typ.strip():raise ValueError('Catalog type name required: '+name)
        meta={'type':typ.strip().lower(),'isIdentity':_flag(row.get('is_identity'),'is_identity'),
              'isNullable':_flag(row.get('is_nullable'),'is_nullable'),'isPrimaryKey':_flag(row.get('is_primary_key'),'is_primary_key'),
              'isUnique':any(g==[name] for g in groups.values()),
              'isCompositeUnique':any(name in g and len(g)>1 for g in groups.values())}
        if meta['type'] in ('varchar','nvarchar','char','nchar'):meta['maxLength']=_number(row.get('max_length'),'max_length')
        if meta['type'] in ('decimal','numeric'):
            meta.update(numericPrecision=_number(row.get('precision'),'precision'),numericScale=_number(row.get('scale'),'scale'))
        column={'name':name,'dbMeta':meta}
        if _flag(row.get('is_computed',0),'is_computed'):column['generated']=True
        columns.append(column)
    pk=[c['name'] for c in columns if c['dbMeta']['isPrimaryKey']]
    if not pk:raise ValueError('Explicit primary key required')
    return {'schema':schema,'name':table,'physicalType':'U','primaryKey':pk,'columns':columns}
