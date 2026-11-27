"""Planning-source field lineage for portable ALM and native source selectors.

No report IDs, cached data, filesystem reads or network calls. Field type here
is the InfoBridge source code, not the consumer assignment's Column/Measure.
"""
import copy

SOURCE_TYPES={'DataInput':'DI','Native':'DI','Forecast':'DI','Formula':'FORMULA'}

def _string(value,label):
    if not isinstance(value,str) or not value.strip():
        raise ValueError(label+' must be a nonempty lossless string')
    return value

def _typed(field):
    _string(field.get('id'),'Planning source field id')
    _string(field.get('measureGuid'),'Planning source measureGuid')
    if field.get('columnType') not in ('DI','FORMULA'):
        raise ValueError('Planning source columnType requires DI or FORMULA from owner records')
    if field.get('isHierarchyColumn') is not False:
        raise ValueError('Planning measure isHierarchyColumn must be false')

def planning_catalog(catalog,owner_columns=None,*,identity_mode='portable'):
    """Enrich source measures by exact owner identity, never by display name.

    Portable id = measureGuid. Native id = the current source selector/record id;
    keep its separate measureGuid. Without owner_columns, require a complete
    catalog from the chosen writer. Never guess a Formula from label or SQL type.
    """
    if identity_mode not in ('portable','native'):raise ValueError('Unknown Planning identity_mode')
    records={};native={}
    if owner_columns is not None:
        if not isinstance(owner_columns,list):raise ValueError('owner_columns must be an array')
        for record in owner_columns:
            mid=_string(record.get('measureGuid'),'Owner measureGuid')
            if mid in records:raise ValueError('Duplicate owner measureGuid')
            records[mid]=record
            rid=record.get('id')
            if rid is not None:
                if isinstance(rid,bool) or not isinstance(rid,(int,str)):raise ValueError('Invalid native owner id')
                key=str(rid)
                if key in native:raise ValueError('Duplicate native owner id')
                native[key]=record
    out=copy.deepcopy(catalog);seen=set()
    for field in out.get('measures',[]):
        fid=_string(field.get('id'),'Planning source field id')
        if fid in seen:raise ValueError('Duplicate Planning source measure id')
        seen.add(fid)
        if owner_columns is not None:
            record=records.get(fid) if identity_mode=='portable' else native.get(fid)
            if record is None:raise ValueError('Missing owner identity for Planning measure '+fid)
            mid=record['measureGuid']
            if field.get('measureGuid',mid)!=mid:raise ValueError('Conflicting source measureGuid')
            if field.get('name')!=record.get('name'):raise ValueError('Source identity/name conflicts with owner; use alias for captions')
            kind=record.get('columnMeta',{}).get('measure_type')
            if not isinstance(kind,dict) or len(kind)!=1 or next(iter(kind)) not in SOURCE_TYPES:
                raise ValueError('Unsupported owner measure_type; resolve its source writer')
            typ=SOURCE_TYPES[next(iter(kind))]
            if field.get('columnType',typ)!=typ:raise ValueError('Conflicting source columnType')
            if field.get('isHierarchyColumn',False) is not False:raise ValueError('Owner measure cannot be a hierarchy column')
            field.update(measureGuid=mid,columnType=typ,isHierarchyColumn=False)
        else:
            # False is derivable from membership in the source measures array.
            field.setdefault('isHierarchyColumn',False)
        _typed(field)
        if identity_mode=='portable' and field['id']!=field['measureGuid']:
            raise ValueError('Portable source id must equal measureGuid; native selectors require identity_mode=native')
    return out

def include_measures(selection,catalog):
    """Complete selected owner descriptors without converting ID domains."""
    fields={f['id']:f for f in catalog.get('measures',[])};out=[];seen=set()
    for selected in selection:
        item=copy.deepcopy(selected);fid=_string(item.get('id'),'includeMeasures id')
        if fid in seen or fid not in fields:raise ValueError('Duplicate/missing includeMeasures source identity')
        seen.add(fid);field=fields[fid]
        if item.get('name')!=field['name']:raise ValueError('includeMeasures name/identity mismatch')
        for key in ('measureGuid','columnType','isHierarchyColumn'):
            if key in item and item[key]!=field[key]:raise ValueError('Conflicting includeMeasures '+key)
            item[key]=field[key]
        out.append(item)
    return out

def check_planning_graph(graph):
    """Reject missing lineage even when callers assemble the portable JSON by hand.

    Check every copy of a known owner measure through source/query metadata and
    transformation descriptors. Derived-query outputs and non-Planning sources
    have separate contracts and are not stamped with owner metadata.
    """
    count=0
    for source in graph.get('sources',[]):
        if source.get('type')!='PLANNING':continue
        fields={};meta=source['meta']
        for field in meta.get('measures',[]):
            _typed(field)
            if field['id'] in fields:raise ValueError('Duplicate Planning source measure id')
            fields[field['id']]=field
        for field in meta.get('selectedMeasures',[])+meta.get('includeMeasures',[]):
            if field.get('id') not in fields:raise ValueError('Selected Planning measure missing from base catalog')
        for query in source.get('queries',[]):
            for field in query.get('meta',{}).get('measures',[]):
                if field.get('id') not in fields:raise ValueError('Planning query base measure missing from source catalog')
        def visit(x):
            nonlocal count
            if isinstance(x,dict):
                fid=x.get('id')
                if isinstance(fid,str) and fid in fields and 'name' in x:
                    field=fields[fid];_typed(x)
                    if any(x[k]!=field[k] for k in ('name','measureGuid','columnType','isHierarchyColumn')):
                        raise ValueError('Inconsistent Planning lineage in source/query/transformation: '+fid)
                    count+=1
                for value in x.values():visit(value)
            elif isinstance(x,list):
                for value in x:visit(value)
        visit(source)
    return {'planningMeasureDescriptors':count,'runtime':'not-run'}

def resolve_planning_output(query,expected_measure_guid,*,expected_name=None):
    """Resolve post-import output by explicit owner lineage in this exact query.

    Name-only matching and guessing native IDs from an unsigned measureGuid are
    forbidden. Derived/renamed outputs need their own explicit output-ID mapping.
    """
    from .consumer_bindings import output_catalog
    mid=_string(expected_measure_guid,'Expected owner measureGuid');meta=query['meta']
    selected=meta['selectedMeasures'] if 'selectedMeasures' in meta else meta.get('measures',[])
    matches=[f for f in selected if f.get('measureGuid')==mid]
    if len(matches)!=1:raise ValueError('Missing/ambiguous current query output lineage')
    native=matches[0]
    fields=[f for f in output_catalog(query) if f['role']=='measures' and f['outputId']==native['id']]
    if len(fields)!=1:raise ValueError('Lineage not found in current selected output catalog')
    field=fields[0]
    if expected_name is not None and field['columnName']!=expected_name:raise ValueError('Query output label conflicts with intended lineage')
    typ=str(field.get('nativeType','')).upper()
    if typ in ('INTEGER','INT','BIGINT','SMALLINT','TINYINT'):data_type='Int64'
    elif typ in ('DOUBLE','FLOAT','REAL'):data_type='Double'
    elif typ.startswith(('DECIMAL','NUMERIC')):data_type='Decimal'
    else:raise ValueError('Resolve numeric consumer type from actual query output')
    field.update(sourceType='InfoBridge',columnType='Column',dataType=data_type)
    return field

def rebind_planning_outputs(properties,owner_columns,bindings,queries):
    """Scoped post-import candidate, preserving existing internal Native aliases.

    bindings: [{measure_guid, query_guid, source_measure_guid, expected_name?}].
    queries: fresh query metadata keyed by portable query GUID. No API writes.
    """
    from .consumer_bindings import binding_query_id
    out=copy.deepcopy(properties);records={};resolved={};sorts={}
    for c in owner_columns:
        mid=_string(c.get('measureGuid'),'Destination measureGuid')
        if mid in records:raise ValueError('Duplicate destination owner identity')
        records[mid]=c
    for b in bindings:
        mid=_string(b.get('measure_guid'),'Destination measure_guid')
        if mid in resolved:raise ValueError('Duplicate destination binding')
        record=records.get(mid)
        if record is None or set(record.get('columnMeta',{}).get('measure_type',{}))!={'Native'}:
            raise ValueError('Rebinding requires an existing Native companion; inputs and formulas are unchanged')
        matches=[a for a in out.get('pivotAssignments',[]) if a.get('measureGuid')==mid and a.get('dataRoleType')=='Measure']
        if len(matches)!=1 or matches[0].get('sourceType')!='InfoBridge':raise ValueError('Expected one existing InfoBridge measure assignment')
        old=matches[0];q=queries[b['query_guid']]
        if q['id']!=b['query_guid'] or str(old.get('queryId')) not in (q['id'],binding_query_id(q)):
            raise ValueError('Binding must stay within its intended query')
        f=resolve_planning_output(q,b['source_measure_guid'],expected_name=b.get('expected_name'))
        if old.get('columnName')!=f['columnName']:raise ValueError('Output name conflicts with intended binding')
        resolved[mid]=f;key=(str(old['queryId']),old['id'])
        if key in sorts and sorts[key]['id']!=f['id']:raise ValueError('Ambiguous old external reference')
        sorts[key]=f
    def visit(x):
        if isinstance(x,dict):
            mid=x.get('measureGuid')
            if mid in resolved and x.get('sourceType')=='InfoBridge':
                f=resolved[mid]
                for key in ('id','sourceId','queryId','tableName','columnName','columnType','dataType'):x[key]=f[key]
                for key in ('infoBridgeSourceId','infoBridgeSourceGuid','tableId'):x.pop(key,None)
            sort_key=(str(x.get('queryId')),x.get('columnId'))
            if sort_key in sorts and 'columnName' in x:
                f=sorts[sort_key];x.update(columnId=f['id'],columnName=f['columnName'],queryId=f['queryId'])
                if 'id' in x:x['id']=f['id']
            for value in x.values():visit(value)
        elif isinstance(x,list):
            for value in x:visit(value)
    visit(out)
    from .consumer_bindings import audit_visual_consumers
    audit_visual_consumers(out,{binding_query_id(q):q for q in queries.values()})
    return {'properties':out,'resolvedBindings':resolved,'ownerColumnsChanged':False,'runtime':'not-run'}
