"""Scoped ALM Forecast repair from a user-designated working reference."""
import copy
from .codec import parts,loads,patch,sha
from .forecast import forecast_time_axis

def repair_definition(envelope,target_sheet,reference_sheet,target_forecast,reference_forecast):
    raw=parts(envelope);definition=loads(raw['definition.json'].decode('utf-8-sig'))
    def selected(sheet_name,measure_name):
        sheets=[s for s in definition['sheets'] if s['displayName']==sheet_name]
        if len(sheets)!=1:raise ValueError('Missing/ambiguous sheet '+sheet_name)
        hits=[]
        for v in sheets[0]['workloadItemEntityVisuals']:
            if v.get('isEmbedded') or v['visualType']!='PLANNING':continue
            prefix=f'sheets/{sheets[0]["recordGuid"]}/visuals/{v["visualId"]}/'
            data=loads(raw[prefix+'dataInput.json'].decode('utf-8-sig'))
            cs=[c for c in data['columns'] if c['name'].casefold()==measure_name.casefold() and 'Forecast' in c['columnMeta']['measure_type']]
            for c in cs:hits.append((prefix,data,c))
        if len(hits)!=1:raise ValueError('Missing/ambiguous native Forecast '+measure_name)
        return hits[0]
    prefix,data,target=selected(target_sheet,target_forecast);rp,rd,reference=selected(reference_sheet,reference_forecast)
    old=target['columnMeta']['measure_type']['Forecast'];ref=reference['columnMeta']['measure_type']['Forecast']
    # Copy behavior/settings, preserve consumer identity and its resolved methods.
    for k in ('forecast_version','closed_period_till','auto_close_forecast_settings','forecast_value_display',
              'forecast_allowed_user_permissions','disable_write_access','bound_to_filter_context','edit_config'):
        if k in ref:old[k]=copy.deepcopy(ref[k])
    if all(old['forecast_period'][k][:10]==ref['forecast_period'][k][:10] for k in ('start','end')):
        old['forecast_period']=copy.deepcopy(ref['forecast_period'])
    else:raise ValueError('Reference horizon differs; construct bounds for the requested dates instead')
    # Do not import reference-specific formulas/defaults with unremapped IDs.
    edit=old['edit_config'];num=edit['number_column_metadata']
    if edit.get('on_change_formula') or any(isinstance(num.get(k),dict) and 'Measure' in num[k] for k in ('default_value','min_value','max_value')):
        raise ValueError('Reference-specific edit dependencies require explicit remapping')
    props=loads(raw[prefix+'properties.json'].decode('utf-8-sig'));state=props['properties']['visualState']
    mid=target['measureGuid'];rs=loads(raw[rp+'properties.json'].decode('utf-8-sig'))['properties']['visualState']
    known_roles={d['externalKey']:{'level':d['timeIntervalUnit'],'timeIntervalUnit':d['timeIntervalUnit']}
        for d in rs.get('columnDimensions',[]) if d.get('timeIntervalUnit') in ('Year','Quarter','Month','HalfYear','Week','Day')}
    forecast_time_axis(state['columnDimensions'],{d['externalKey']:known_roles[d['externalKey']] for d in state['columnDimensions'] if d['externalKey'] in known_roles})
    source_agg=rs.get('aggregation_config',{}).get('measure_aggregation',{}).get(reference['measureGuid'],{'row':'Sum','column':'Sum'})
    state.setdefault('aggregation_config',{}).setdefault('measure_aggregation',{})[mid]=copy.deepcopy(source_agg)
    members=state.setdefault('manage_measures',[]);member=next((m for m in members if m['id']==mid),None)
    if member:member['visible']=True
    else:members.append({'id':mid,'label':target['name'],'order':len(members),'visible':True})
    changed={prefix+'dataInput.json':data,prefix+'properties.json':props}
    changed={k:v for k,v in changed.items() if v!=loads(raw[k].decode('utf-8-sig'))}
    return patch(envelope,changed,{k:sha(raw[k]) for k in changed}),{'changedParts':list(changed),
        'measureGuid':mid,'referenceSheet':reference_sheet,'settings':copy.deepcopy(old),'postSaveValidation':'not-run'}
