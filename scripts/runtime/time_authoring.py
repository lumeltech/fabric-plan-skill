"""Resolved non-composite calendar axes and scoped native as-of Visual Columns.

Only local candidates are produced. No report cache, source checkout or live token.
"""
import copy,re
from datetime import datetime
from .identity import native_id,xxh3
from .codec import unpack,parts,patch,sha
from .forecast import forecast_time_axis,resolve_time_levels
from .formula_syntax import check_formula

ALIASES={'Year':['year','yr'],'Quarter':['quarter','qtr'],
 'Month':['monthname','month','monthnumber','monthno'],'Week':['week','weeknumber']}
COMPOSITES={'yearmonth':'Month','yearquarter':'Quarter','yearweek':'Week'}

def preferred_calendar_axis(model,calendar_table,grain='Month',fields=None,week_parentage_valid=False):
    """Choose actual model fields; an explicit role map resolves custom/fiscal names."""
    selected={};fields=fields or {}
    if grain not in ('Year','Quarter','Month','Week'):raise ValueError('Supported calendar grain required')
    available=[f for f in model['fields'] if f['tableName']==calendar_table and f['columnType']=='Column']
    for role,aliases in ALIASES.items():
        if role in fields:
            hits=[f for f in available if f['id']==fields[role]]
            if not hits:raise ValueError('Explicit calendar role does not resolve: '+role)
        else:
            hits=[]
            for alias in aliases:
                hits=[f for f in available if re.sub(r'[ _-]','',f['columnName']).lower()==alias]
                if hits:break
        if len(hits)>1:raise ValueError('Ambiguous calendar role '+role)
        if hits:selected[role]=hits[0]['id']
    required={'Year':['Year'],'Quarter':['Year','Quarter'],'Month':['Year','Quarter','Month'],
              'Week':['Year','Quarter','Month','Week'] if week_parentage_valid else ['Year','Week']}[grain]
    # A calendar with no Quarter can still have a valid Year/Month hierarchy.
    if grain=='Month' and 'Quarter' not in selected:required=['Year','Month']
    if any(r not in selected for r in required):raise ValueError('Resolve missing calendar roles: '+', '.join(r for r in required if r not in selected))
    columns=[selected[r] for r in required]
    levels={selected[r]:{'level':r,'timeIntervalUnit':r,**({'parentageValidated':True} if r=='Week' and week_parentage_valid else {})} for r in required}
    return {'columns':columns,'columnTimeLevels':levels,'grain':grain}

def prefer_forecast_axis(model,spec):
    """New-sheet authoring only. Existing-report repairs must be explicitly scoped."""
    out=copy.deepcopy(spec)
    if not any(m.get('kind')=='Forecast' for m in out.get('measures',[])):return out
    columns=out.get('columns',[]);found=[]
    for key in columns:
        field=next((f for f in model['fields'] if f['id']==key),None)
        if field and re.sub(r'[ _-]','',field['columnName']).lower() in COMPOSITES:found.append(field)
    if not found:return out
    if out.get('allowCompositeTimeAxis'):
        if not out.get('compositeTimeAxisReason') or not out.get('columnTimeLevels'):
            raise ValueError('Composite exception needs a reason and resolved native time levels')
        return out
    if len(found)!=1:raise ValueError('Resolve composite calendar axis through preferred_calendar_axis')
    composite=found[0];grain=COMPOSITES[re.sub(r'[ _-]','',composite['columnName']).lower()]
    chosen=preferred_calendar_axis(model,composite['tableName'],grain,
        out.get('calendarRoleFields'),out.get('weekParentageValidated',False))
    # Do not silently remove a product/scenario or a separately requested axis.
    known=set(chosen['columns'])|{composite['id']}
    if set(columns)-known:raise ValueError('Forecast Columns must contain only the resolved date hierarchy')
    out.update(columns=chosen['columns'],columnTimeLevels=chosen['columnTimeLevels'])
    return out

def apply_time_axis(properties,model,columns,time_levels=None):
    """Property-only candidate. Keep period-window filters and storage-key rules."""
    from .construct import field
    out=copy.deepcopy(properties);state=out['visualState']
    new=[field(model,k,'columns',i) for i,k in enumerate(columns)]
    resolve_time_levels(columns,time_levels)
    oldkeys={a['id'] for a in out['pivotAssignments'] if a['bucketId']=='columns'}
    olddims={d['externalKey']:d for d in state.get('columnDimensions',[])}
    dims=[{'externalKey':k,'id':olddims[k]['id'] if k in olddims else str(xxh3(k)),
           'label':a['name']} for k,a in zip(columns,new)]
    state['columnDimensions']=forecast_time_axis(dims,time_levels)
    out['pivotAssignments']=[a for a in out['pivotAssignments'] if a['bucketId']!='columns']+new
    for f in out.get('superFilterAssignments',[]):
        if f.get('isDaxMeasure'):
            f['pivotAssignments']=[a for a in f['pivotAssignments'] if a['bucketId']!='columns']+copy.deepcopy(new)
        elif any(a.get('id') in oldkeys-set(columns) for a in f.get('pivotAssignments',[])):
            f['isDefault']=False # Retain filters on removed composite fields as scope filters.
    mapping=state.get('dimension_id_mapping',{})
    if mapping.get('pivot'):
        templates=[a for a in mapping['pivot'] if a['bucket_type']=='Column']
        if templates:
            rebuilt=[]
            for a in new:
                t=copy.deepcopy(next((t for t in templates if t['id']==a['id']),templates[-1]))
                t.update(id=a['id'],name=a['name'],column_name=a['columnName'],order=a['order'],external_data_type=a['dataType'])
                rebuilt.append(t)
            mapping['pivot']=[a for a in mapping['pivot'] if a['bucket_type']!='Column']+rebuilt
    table=state.setdefault('tableState',{});levels=table.get('columnHierarchyLevel',{})
    table['columnHierarchyLevel']={d['id']:copy.deepcopy(levels.get(d['id'],{'collapsed':'Expanded'})) for d in dims}
    state['columnExpandCollapse']={'columnExpandCollapse':{},'expandColumnToLastLevel':True}
    from .filters import ensure_axis_filters
    ensure_axis_filters(out)
    return out

def date_parameter_bundle(parameter_id,label,field,selected_value,technical_name):
    if not re.fullmatch(r'CALC_VARIABLE_[A-Za-z0-9_]+',parameter_id):raise ValueError('Native parameter ID required')
    if not all(isinstance(s,str) and s for s in (label,field,selected_value,technical_name)):raise ValueError('Complete date parameter binding required')
    datetime.fromisoformat(selected_value.replace('Z','+00:00'))
    return {'sheetVariable':{'allowDecimalValues':False,'assignValues':False,'datasetId':'','defaultValue':None,
       'description':'As-of calculation control; does not filter the date hierarchy.','displayMode':'single-select',
       'id':parameter_id,'label':label,'labelColumn':'','numericValue':False,'options':[],
       'radioDirection':'horizontal','scope':'entity','selectedDimension':field,'showInViewMode':True,
       'sourceType':'dataset','technicalName':technical_name,'type':'list',
       'value':{'label':selected_value,'value':selected_value},'valueColumn':''},
     'engineVariable':{'assignValues':False,'description':'','id':parameter_id,'label':label,'options':[],
       'showVariable':True,'title':technical_name,'valueType':'singleSelect'},
     'calculatedVariable':{'id':parameter_id,'value':selected_value}}

def time_expression(source_id,period,cutoff_expression,offset=0,missing_id=None):
    native_id(source_id)
    if period not in ('QTD','MTD','YTD'):raise ValueError('Use QTD, MTD or YTD')
    if isinstance(offset,bool) or not isinstance(offset,int):raise ValueError('Offset must be an integer')
    if not isinstance(cutoff_expression,str) or not cutoff_expression.strip():raise ValueError('Resolved native cutoff expression required')
    check_formula(cutoff_expression)
    total=f'SUM({period}(M_{source_id}, {offset}, {cutoff_expression}))'
    if missing_id:
        native_id(missing_id)
        total=f'IF(SUM({period}(M_{missing_id}, {offset}, {cutoff_expression})) > 0, BLANK, {total})'
    return check_formula(total)

def append_visual_column(properties,records,record,row_aggregation='None'):
    out=copy.deepcopy(properties);cols=copy.deepcopy(records);rec=copy.deepcopy(record)
    mid=native_id(rec['measureGuid']);mt=rec['columnMeta']['measure_type']
    if set(mt)!={'VisualColumn'} or set(mt['VisualColumn']) not in ({'Formula'},{'DataInput'}):raise ValueError('Use an explicit Formula or DataInput VisualColumn')
    if row_aggregation not in ('None','Sum','Formula'):raise ValueError('Resolve visual-column row aggregation')
    if any(c['measureGuid']==mid for c in cols):raise ValueError('Visual-column ID already exists; use an explicit update')
    if 'Formula' in mt['VisualColumn']:check_formula(mt['VisualColumn']['Formula']['formula'])
    state=out['visualState'];registry=state['manage_measures']
    if any(m['id']==mid for m in registry):raise ValueError('Visual-column ID already registered')
    cols.append(rec);registry.append({'id':mid,'label':rec['name'],'order':max((m['order'] for m in registry),default=-1)+1,'visible':True})
    state['aggregation_config']['measure_aggregation'][mid]={'column':'None','row':row_aggregation}
    state.setdefault('measureAttributes',{})[mid]={'width':160}
    fmt=state['formatConfig'];order=fmt.get('formatSize',0)
    formula='Formula' in mt['VisualColumn'];style={'4':'Arial','3':'#6B3FA0' if formula else '#8A5700','5':'#F2EAFB' if formula else '#FFF4D6'}
    if rec['columnMeta']['data_type']=='Number':style['13']='auto'
    fmt['measure'][mid]=[{'format':style,'order':order}];fmt['formatSize']=order+1
    return out,cols

def add_time_column(envelope,sheet_id,visual_id,measure_id,label,source_id,parameter,
                    period='QTD',offset=0,month_end=True,missing_id=None,row_aggregation='None'):
    raw=unpack(envelope);prefix=f'sheets/{sheet_id}/visuals/{visual_id}/'
    sp=f'sheets/{sheet_id}/sheet.json';pp=prefix+'properties.json';dp=prefix+'dataInput.json'
    if any(k not in raw for k in (sp,pp,dp)):raise ValueError('Resolve current owning sheet and visual IDs')
    sheet=copy.deepcopy(raw[sp]);props=copy.deepcopy(raw[pp]);data=copy.deepcopy(raw[dp])
    ids={r['measureGuid'] for r in data['columns']}
    if source_id not in ids or (missing_id and missing_id not in ids):raise ValueError('Source/missing-data measure must be registered in this owner')
    if not isinstance(month_end,bool):raise ValueError('month_end must be Boolean')
    bundle=date_parameter_bundle(**parameter);pid=bundle['sheetVariable']['id']
    variables=sheet['properties'].setdefault('entityLevelVariables',[])
    state=props['properties']['visualState']
    if any(v['id']==pid for v in variables+state.get('globalVariables',[])) or pid in state.get('calculatedVariables',{}):raise ValueError('Parameter ID exists; reuse or update it explicitly')
    variables.append(bundle['sheetVariable']);state.setdefault('globalVariables',[]).append(bundle['engineVariable'])
    state.setdefault('calculatedVariables',{})[pid]=bundle['calculatedVariable']
    cutoff=f'DATE(VR_{pid})'
    if month_end:cutoff=f'EOMONTH({cutoff})'
    formula=time_expression(source_id,period,cutoff,offset,missing_id)
    rec={'boundToFilterContext':20,'columnMeta':{'data_type':'Number','description':'','id':native_id(measure_id),
      'label':label,'measure_type':{'VisualColumn':{'Formula':{'formula':formula}}}},
      'dataInputType':6,'description':None,'measureGuid':measure_id,'name':label,'visualId':visual_id}
    props['properties'],data['columns']=append_visual_column(props['properties'],data['columns'],rec,row_aggregation)
    changes={sp:sheet,pp:props,dp:data};old=parts(envelope)
    return patch(envelope,changes,{k:sha(old[k]) for k in changes}),{
       'changedParts':list(changes),'measureId':measure_id,'parameterId':pid,'formula':formula,
       'runtimeValidation':'not run','deployment':'not submitted'}
