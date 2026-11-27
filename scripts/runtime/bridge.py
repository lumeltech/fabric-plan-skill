"""Planning bridge constructors and schema algebra; no cached rows/job state."""
import copy, re, math
from decimal import Decimal
from .construct import guid, schema, acyclic
from .bridge_identity import planning_catalog,include_measures as mapped_include_measures,check_planning_graph
GROUPS={'dimensions':'selectedDimensions','columns':'selectedColumns','measures':'selectedMeasures','dateColumns':'selectedDateColumns','hierarchyColumns':'selectedHierarchyColumns'}
BUSINESS_GROUPS=('dimensions','columns','measures')
def catalog_meta(catalog):
    out={}
    for group,selected in GROUPS.items():
        out[group]=copy.deepcopy(catalog.get(group,[])); out[selected]=copy.deepcopy(out[group])
    names=[f.get('alias',f['name']) for g in BUSINESS_GROUPS for f in out[g]]
    if len(names)!=len(set(names)): raise ValueError('Ambiguous output names')
    for group in GROUPS:
        for f in out[group]:
            if 'name' not in f:raise ValueError('Unnamed source descriptor')
            if group in BUSINESS_GROUPS:
                if 'id' not in f:raise ValueError('Incomplete actual source field')
                field_family(f)  # Auxiliary date/hierarchy records can omit ID/type.
    return out
def field_family(field):
    """Compare logical types without inventing or overwriting saved metadata."""
    typ=str(field.get('type','')).upper(); dt=str(field.get('dataType','')).upper()
    if typ.startswith(('DECIMAL','NUMERIC')) or typ in ('DOUBLE','FLOAT','REAL','INTEGER','BIGINT','SMALLINT','TINYINT','HUGEINT','INT','UBIGINT'): return 'number'
    if typ in ('VARCHAR','TEXT','STRING') or dt in ('TEXT_COLUMN','STRING'): return 'text'
    if typ in ('DATE','TIMESTAMP','TIMESTAMP WITH TIME ZONE') or dt in ('DATE','DATETIME'): return 'date'
    if typ=='BOOLEAN':return 'boolean'
    if dt in ('NUMERIC','INTEGER'):return 'number'
    raise ValueError('Unknown output field type: '+str(field.get('name')))
def signature(meta,semantics):
    fields=[]
    for g in BUSINESS_GROUPS:
        fields.extend((g,f.get('alias',f['name']),f.get('type',field_family(f)),f.get('dataType',field_family(f))) for f in meta.get(GROUPS[g],[]))
    return {'fields':fields,'semantics':copy.deepcopy(semantics)}
def append_check(inputs):
    if len(inputs)<2: raise ValueError('Append needs two or more inputs')
    expected=signature(inputs[0]['meta'],inputs[0]['semantics'])
    for q in inputs:
        if not q.get('aggregatedToGrain'): raise ValueError('Explicit reporting-grain aggregation required')
        if signature(q['meta'],q['semantics'])!=expected: raise ValueError('Append dimensionality/type/context mismatch: '+q['name'])
    return expected
class Query:
    def __init__(self,name,source_id,catalog,visual_id=None,kind='PLANNING',query_id=None,*,owner_columns=None,identity_mode='portable'):
        if kind=='PLANNING':catalog=planning_catalog(catalog,owner_columns,identity_mode=identity_mode)
        self.record={'queryId':query_id or 'Q'+guid().replace('-',''),'sourceId':source_id,'name':name,'type':kind,'visualId':visual_id,
                     'meta':catalog_meta(catalog),'transformationSteps':[], 'writebackDestinations':[], 'writebackSettings':None}
        self.trace=[]; self.aggregated=False
    def fields(self):
        items=[(f.get('alias') or f['name'],(g,f)) for g in BUSINESS_GROUPS for f in self.record['meta'][GROUPS[g]]]
        if len({n for n,_ in items})!=len(items): raise ValueError('Ambiguous current output alias')
        return dict(items)
    def step(self,code,name,value):
        self.record['transformationSteps'].append({'queryId':self.record['queryId'],'stepIndex':len(self.record['transformationSteps'])+1,
            'notes':None,'meta':{'type':code,'name':name,'description':'','value':copy.deepcopy(value)}})
        self.trace.append({'step':len(self.trace)+1,'fields':list(self.fields())})
        return self
    def load_planning(self): return self.step(10,'Load Planning columns',{})
    def filter_equals(self, conditions, join='And'):
        """Observed type 180: an array of Where/And/OR clauses, not an object."""
        if join not in ('And','OR') or not isinstance(conditions,list) or not conditions: raise ValueError('Explicit equality conditions required')
        fields=self.fields();clauses=[]
        for index,c in enumerate(conditions):
            if set(c)!={'field','value'} or c['field'] not in fields: raise ValueError('Filter references unavailable output')
            if c['value'] is None or isinstance(c['value'],(dict,list)): raise ValueError('Equality filter requires nonnull scalar')
            field=copy.deepcopy(fields[c['field']][1])
            # Type matching is limited to observed text/numeric source columns.
            numeric=field_family(field)=='number'
            if numeric and (isinstance(c['value'],bool) or not isinstance(c['value'],(int,float,Decimal)) or not math.isfinite(c['value'])): raise ValueError('Finite numeric filter value required')
            if not numeric and (field_family(field)!='text' or not isinstance(c['value'],str)): raise ValueError('Text filter value required')
            clauses.append({'condition':'Where' if index==0 else join,'isValid':True,
                'operator':{'name':'is','value':'='},'sourceColumn':field,'value':c['value']})
        return self.step(180,'Filter Rows',clauses)
    def add(self,name,expression,output_id,kind='measure',requires=(),zero_is_valid=False,*,output_type=None,output_data_type=None):
        """SQL expression and operation role are independent of result type.

        A type-130 Add Measure can return text (for example CASE high/low).
        Explicit output types describe the planned catalog; reconcile the actual
        inferred catalog after execution. Do not parse/rewrite arbitrary SQL here.
        """
        if kind not in ('measure','dimension'):raise ValueError('Unknown derived field role')
        if not isinstance(expression,str) or not expression.strip():raise ValueError('Nonempty SQL expression required')
        f=self.fields()
        if name in f: raise ValueError('Output already exists: '+name)
        if any(x not in f for x in requires): raise ValueError('Expression requires unavailable field')
        if re.fullmatch(r'\s*(?:CAST\()?0(?:\.0)?(?: AS DOUBLE\))?\s*',expression,re.I) and not zero_is_valid:
            raise ValueError('Zero contribution needs explicit business meaning')
        if not isinstance(output_id,str) or not output_id.strip(): raise ValueError('Output identity required by selected writer')
        if any(field['id']==output_id for _,field in f.values()): raise ValueError('Duplicate output field identity')
        group='measures' if kind=='measure' else 'dimensions'
        item={'id':output_id,'name':name,'alias':name,'type':output_type or ('DOUBLE' if kind=='measure' else 'VARCHAR')}
        family=field_family(item)
        # Numeric/text dataType labels are evidenced. Other helper type enums
        # must come from the writer/readback, not from an invented mapping.
        dt=output_data_type or {'number':'NUMERIC','text':'TEXT_COLUMN'}.get(family)
        if dt:item['dataType']=dt
        if kind=='measure' and family=='number': item['aggregationType']='sum'
        self.record['meta'][GROUPS[group]].append(item)
        return self.step(130 if kind=='measure' else 170,'Add Measure' if kind=='measure' else 'Add Dimension',{'columnName':name,'formulaQuery':expression,'isValid':True})
    def find_replace(self,columns,find,replace,*,full_match=True,match_case=False,use_regex=False):
        fields=self.fields()
        if not columns or len(set(columns))!=len(columns) or any(n not in fields for n in columns):raise ValueError('Find/replace needs existing unique columns')
        if not all(isinstance(x,bool) for x in (full_match,match_case,use_regex)):raise ValueError('Explicit Boolean replacement flags required')
        if not isinstance(find,str) or not isinstance(replace,str) or any(field_family(fields[n][1])!='text' for n in columns):raise ValueError('Observed replacement branch requires text fields and strings')
        return self.step(200,'Find and Replace',{'columns':list(columns),'find':find,'replace':replace,'flags':{'fullMatch':full_match,'matchCase':match_case,'useRegex':use_regex},'isValid':True})
    def rename(self,name,new_name,output_id):
        fields=self.fields()
        if name not in fields or not isinstance(new_name,str) or not new_name.strip() or new_name in fields:raise ValueError('Invalid rename')
        if not isinstance(output_id,str) or not output_id or any(f['id']==output_id for _,f in fields.values()):raise ValueError('Fresh renamed output identity required')
        group,field=fields[name]; source={k:copy.deepcopy(field[k]) for k in ('id','name','alias','measureGuid','columnType','isHierarchyColumn') if k in field};source['sourceType']=group
        field.update(id=output_id,name=new_name,alias=new_name)
        # Renamed output has a new query identity; lineage belongs to its input
        # descriptor, not a claim that the new output is the original owner.
        for key in ('measureGuid','columnType','isHierarchyColumn'):field.pop(key,None)
        return self.step(60,'Rename Column',{'columnName':new_name,'sourceColumn':source,'isValid':True})
    def remove(self,names):
        fields=self.fields()
        if any(n not in fields for n in names): raise ValueError('Cannot remove absent field')
        removed=[{**copy.deepcopy(fields[n][1]),'sourceType':fields[n][0]} for n in names]
        for g,s in GROUPS.items(): self.record['meta'][s]=[f for f in self.record['meta'][s] if (f.get('alias') or f['name']) not in names]
        # Dropping a dimension is not aggregation.
        if any(fields[n][0]!='measures' for n in names): self.aggregated=False
        return self.step(310,'Remove Columns',{'sourceColumns':removed,'isValid':True})
    def pivot(self,rows,columns,measures):
        fields=self.fields(); keep=rows+columns+list(measures)
        if len(keep)!=len(set(keep)) or any(n not in fields for n in keep): raise ValueError('Duplicate/missing pivot field (including Year drift)')
        for n in rows:
            if fields[n][0]!='dimensions': raise ValueError('Pivot row role mismatch: '+n)
        for n in columns:
            if fields[n][0]!='columns': raise ValueError('Pivot column role mismatch: '+n)
        for n in measures:
            if fields[n][0]!='measures': raise ValueError('Pivot measure role mismatch: '+n)
        rd=[copy.deepcopy(fields[n][1]) for n in rows]; cd=[copy.deepcopy(fields[n][1]) for n in columns]
        md=[{**copy.deepcopy(fields[n][1]),'aggregationType':agg} for n,agg in measures.items()]
        for m in md:
            if m['aggregationType'] not in ('sum','min','max','avg','count'): raise ValueError('Unverified pivot aggregation')
            if m['aggregationType'] in ('sum','avg') and field_family(m)!='number':raise ValueError('Cannot sum or average a nonnumeric SQL result')
        removed=[copy.deepcopy(f) for n,(_,f) in fields.items() if n not in keep]
        self.record['meta'].update(selectedDimensions=rd,selectedColumns=cd,selectedMeasures=md,selectedDateColumns=[],selectedHierarchyColumns=[])
        self.aggregated=True
        return self.step(50,'Pivot table created',{'sourceDimensions':rd,'sourceColumns':cd,'sourceMeasures':md,'removeColumns':removed,'isValid':True})
    def result(self,semantics):
        return {**copy.deepcopy(self.record),'aggregatedToGrain':self.aggregated,'semantics':copy.deepcopy(semantics)}
def planning_source(name,visual_id,catalog,include_measures,include_scenarios,honor_filters=True,source_id=None,*,skip_totals=True,model_reference=None,owner_columns=None,identity_mode='portable'):
    for selection in (include_measures,include_scenarios):
        if not isinstance(selection,list) or any(not isinstance(x,dict) or not {'id','name'}<=x.keys() for x in selection):
            raise ValueError('includeMeasures/includeScenarios require explicit {id,name} arrays')
    if not isinstance(honor_filters,bool) or not isinstance(skip_totals,bool):raise ValueError('Explicit Boolean source flags required')
    catalog=planning_catalog(catalog,owner_columns,identity_mode=identity_mode)
    include_measures=mapped_include_measures(include_measures,catalog)
    out={'sourceGuid':source_id or guid(),'name':name,'type':'PLANNING','visualId':visual_id,
       'meta':{**catalog_meta(catalog),'includeMeasures':copy.deepcopy(include_measures),'includeScenarios':copy.deepcopy(include_scenarios),
               'honorSourceFilter':honor_filters,'isSkipTotals':skip_totals},'queries':[]}
    if model_reference:
        for k in ('datasetId','datasetName','workspaceId','workspaceName'):
            if k not in model_reference:raise ValueError('Complete current source model reference required')
            out['meta'][k]=model_reference[k]
    return out
def append_source(name,inputs):
    append_check(inputs); sid=guid(); qid='Q'+guid().replace('-',''); meta=copy.deepcopy(inputs[0]['meta'])
    # Source/query outputs are selected catalogs; never carry old caches.
    for g,s in GROUPS.items(): meta[g]=copy.deepcopy(meta[s])
    meta['queries']=[q['queryId'] for q in inputs]
    q={'queryId':qid,'sourceId':sid,'name':name,'type':'APPEND','visualId':None,'meta':copy.deepcopy(meta),
       'writebackDestinations':[],'writebackSettings':None,
       'transformationSteps':[{'queryId':qid,'stepIndex':1,'notes':None,'meta':{'type':140,'name':'Append Query','description':'','value':{}}}]}
    src={'sourceGuid':sid,'name':name,'type':'APPEND','visualId':None,'meta':meta,'queries':[q]}
    edges=[{'linkedQueryGuid':guid(),'queryId':x['queryId'],'sourceId':sid,'visualId':x.get('visualId')} for x in inputs]
    return src,edges
def portable(sources,edges):
    out={'$schema':schema('ConnectedPlanning/Infobridge'),'sources':copy.deepcopy(sources),'linkedQueries':copy.deepcopy(edges),'queryGroups':[]}
    for s in out['sources']:
        for q in s['queries']:
            q.pop('semantics',None); q.pop('aggregatedToGrain',None)
    validate_graph(out); return out
def validate_graph(graph):
    from .bridge_operations import query_references
    check_planning_graph(graph)
    sources={}; queries={}
    for s in graph['sources']:
        sid=s['sourceGuid']
        if sid in sources: raise ValueError('Duplicate source')
        sources[sid]=s
        for q in s['queries']:
            qid=q['queryId']
            if qid in queries or q['sourceId']!=sid: raise ValueError('Invalid query identity/owner')
            queries[qid]=q
            if q.get('writebackSettings') is not None and not q['writebackSettings'].get('writebackSettingsGuid'): raise ValueError('Empty/incomplete writebackSettings')
            if not q['transformationSteps']: raise ValueError('Query has no source operation')
            for i,t in enumerate(q['transformationSteps'],1):
                if t['stepIndex']!=i or t['queryId']!=qid: raise ValueError('Step order/owner mismatch')
    deps={q:[] for q in queries}; seen=set()
    for e in graph.get('linkedQueries',[]):
        if e['linkedQueryGuid'] in seen: raise ValueError('Duplicate edge identity')
        seen.add(e['linkedQueryGuid'])
        if e['queryId'] not in queries or e['sourceId'] not in sources: raise ValueError('Dangling dependency')
        for q in sources[e['sourceId']]['queries']: deps[q['queryId']].append(e['queryId'])
    for qid,q in queries.items():
        if q['type'] in ('APPEND','MERGE','JOIN','SQL_SOURCE'):
            if set(query_references(q['type'],q['meta']))!=set(deps[qid]): raise ValueError('Query execution references differ from edges')
            smeta=sources[q['sourceId']].get('meta')
            if smeta is not None and set(query_references(q['type'],smeta))!=set(deps[qid]):raise ValueError('Source execution references differ from edges')
    return acyclic(deps)
def reconcile_assignments(assignments,mappings,catalog):
    """Map portable (query, field) to canonical actual catalog identity, never by label."""
    out=copy.deepcopy(assignments)
    keys=['id','sourceId','queryId','tableName','tableId','infoBridgeSourceId','infoBridgeSourceGuid','sourceType']
    for a in out:
        if a.get('sourceType')!='InfoBridge': continue
        lookup=(a['queryId'],a['sourceId'])
        if lookup not in mappings: raise ValueError('Unresolved output-field mapping')
        wanted=mappings[lookup]
        matches=[c for c in catalog if c['queryId']==wanted['queryId'] and c['id']==wanted['id'] and c['sourceType']=='InfoBridge']
        if len(matches)!=1: raise ValueError('Missing or ambiguous destination catalog field')
        c=matches[0]
        for k in keys:
            if k in c: a[k]=copy.deepcopy(c[k])
            elif k in ('tableId','infoBridgeSourceId','infoBridgeSourceGuid'): a.pop(k,None)
    return out
def reconcile_execution(query,query_map):
    """Only SQL tokens and explicit query lists. Does not replace arbitrary GUIDs."""
    out=copy.deepcopy(query)
    from .bridge_operations import reconcile_meta
    out['meta']=reconcile_meta(out.get('type','APPEND'),out['meta'],query_map)
    def tokens(v):
        def sub(m):
            if m.group(1) not in query_map: raise ValueError('Unknown SQL execution query')
            return '{{query_id:'+str(query_map[m.group(1)])+'}}'
        return re.sub(r'\{\{query_id:([^}]+)\}\}',sub,v)
    # Explicit known expression fields only; never a recursive global rewrite.
    for t in out['transformationSteps']:
        v=t['meta'].get('value')
        if isinstance(v,dict):
            for k in ('formulaQuery','sqlQuery'):
                if isinstance(v.get(k),str): v[k]=tokens(v[k])
    return out
