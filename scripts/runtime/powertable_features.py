"""PowerTable Forms, Automations and Approvals as public Plan definition parts.

The Plan import reads ``forms.json``, ``automations.json`` and ``approvals.json``
from the PowerTable visual folder, beside ``source.json`` and
``columnConfigs.json``, so they travel through the public definition APIs. Form
fields and layout nodes reference a column by its columnConfigs ``recordGuid``;
import maps it to the runtime ID.

``approvals.json`` carries one approval workflow record (rule type, persist flag,
multi-level flag, levels and routing filters). Approver users are not definition
content and have no supported public route.

An update that omits an existing ``forms.json``, ``automations.json`` or
``approvals.json`` deletes those records on import, so always start from a fresh
export.
"""
import copy,json,re,uuid
from .construct import guid,schema
from .codec import parts,unpack,patch,pack,sha

FORM_ENABLED=10
TRIGGERS={'ROW_CREATED':1,'ROW_UPDATED':2,'ROW_DELETED':3}
ACTIONS={'CREATE_RECORD':(1,'createRecord'),'UPDATE_RECORD':(2,'updateRecord'),
         'SEND_MAIL':(5,'sendEmail'),'MS_TEAMS':(7,'teams')}
ACTION_BLOCK=1
OPERATORS={'equals','notEqual','lessThan','greaterThan','lessThanOrEquals','greaterThanOrEquals','empty','notEmpty',
           'is','isNot','isOneof','isNotOneof','contains','doesNotContain','beginsWith','doesNotBeginWith','endsWith','doesNotEndWith'}
CONDITION_TYPES={1:'string',2:'string',6:'number',13:'number',11:'boolean'}
AUTOMATION_NAME=re.compile(r'[A-Za-z][A-Za-z0-9\-_() ]*')
EMAIL=re.compile(r'[^@\s]+@[^@\s]+\.[^@\s]+')
FORM_CONFIG={'showTitle':bool,'showLogo':bool,'submissionMessage':str,'fieldLabel':str}
APPROVAL_RULES={'DEFAULT':10,'MANUAL':20,'LOOKUP':30}
PERSIST_FLAGS={'SAVE_AFTER_REVIEW':10,'SAVE_BEFORE_REVIEW':20}
APPROVAL_REQUEST={'rule_type','persist_flag','multi_level_enabled','levels','filters','lookup_config'}

def _text(value,label,limit=255,*,allow_empty=False):
    if not isinstance(value,str) or len(value)>limit or (not allow_empty and not value.strip()):
        raise ValueError(label+' must be text of at most '+str(limit)+' characters')
    return value.strip() if not allow_empty else value

def _rule_id(prefix):return prefix+'-'+uuid.uuid4().hex[:21]

def _by_name(columns):
    names=[c.get('columnName') for c in columns]
    if any(not isinstance(n,str) for n in names) or len(set(names))!=len(names):raise ValueError('Unique PowerTable column names required')
    if any(not isinstance(c.get('recordGuid'),str) or not c['recordGuid'] for c in columns):
        raise ValueError('Column recordGuid required; Forms reference columns by recordGuid')
    return {c['columnName']:c for c in columns}

def _json_default(value):
    # The product stores JSON.stringify(defaultValue) for JavaScript-truthy values and '' otherwise.
    if value is None or value is False or value=='' or (isinstance(value,(int,float)) and not isinstance(value,bool) and value==0):return ''
    if isinstance(value,float) and value!=value:return ''
    return json.dumps(value,ensure_ascii=False,separators=(',',':'))

def form_record(title,fields,columns,*,description='',restrict_multiple_entry=0,config=None,source_guid=None):
    """One forms.json entry for a configured PowerTable.

    ``fields`` is an ordered list of ``{"column": <columnName>, "mandatory": 0|1,
    "description": "", "defaultValue": ...}``. Every mandatory column must be on
    the form; the product blocks submission otherwise.
    """
    title=_text(title,'Form title');description=_text(description or '','Form description',allow_empty=True)
    if restrict_multiple_entry not in (0,1) or isinstance(restrict_multiple_entry,bool):raise ValueError('restrict_multiple_entry must be 0 or 1')
    by_name=_by_name(columns)
    if not isinstance(fields,list) or not fields:raise ValueError('At least one form field is required')
    form_guid=guid();children=[];records=[];seen=set()
    for field in fields:
        if not isinstance(field,dict) or set(field)-{'column','mandatory','description','defaultValue'}:
            raise ValueError('Form field must name a column with optional mandatory, description and defaultValue')
        column=by_name.get(field.get('column'))
        if column is None:raise ValueError('Form field column not configured: '+str(field.get('column')))
        if column['columnName'] in seen:raise ValueError('Duplicate form field: '+column['columnName'])
        seen.add(column['columnName'])
        if column.get('allowEdit')!=1:raise ValueError('Form field column is read-only: '+column['columnName'])
        required=field.get('mandatory',1 if column.get('mandatory')==1 else 0)
        if required not in (0,1) or isinstance(required,bool):raise ValueError('Form field mandatory must be 0 or 1')
        if column.get('mandatory')==1 and required!=1:raise ValueError('Mandatory column cannot be optional on a form: '+column['columnName'])
        label=column.get('displayName') or column['columnName']
        children.append({'type':'field','id':column['recordGuid'],'dataKey':column['recordGuid'],'name':label,
                         'mandatory':required,'allowEdit':1,'props':{'name':label}})
        records.append({'recordGuid':guid(),'columnConfigId':column['recordGuid'],
                        'description':_text(field.get('description',''),'Form field description',allow_empty=True),
                        'required':required,'defaultValue':_json_default(field.get('defaultValue')),'formId':form_guid})
    missing=[n for n,c in by_name.items() if c.get('mandatory')==1 and c.get('allowEdit')==1 and n not in seen]
    if missing:raise ValueError('Form must include every mandatory column: '+', '.join(missing))
    # The product's new-form defaults: logo shown, multiple entries allowed.
    settings={'showTitle':True,'showLogo':True,'submissionMessage':'','fieldLabel':'stacked'}
    if config is not None:
        if not isinstance(config,dict) or set(config)-set(FORM_CONFIG):raise ValueError('Form config supports only '+', '.join(FORM_CONFIG))
        for key,value in config.items():
            if not isinstance(value,FORM_CONFIG[key]):raise ValueError('Invalid form config '+key)
        settings.update(config)
    if settings['fieldLabel'] not in ('stacked','inline'):raise ValueError('fieldLabel must be stacked or inline')
    record={'recordGuid':form_guid,'title':title,'description':description,'restrictMultipleEntry':restrict_multiple_entry,
            'logo':None,'layoutMeta':{'id':guid(),'type':'form','status':FORM_ENABLED,'layoutType':'default','children':children},
            'config':settings,'formFields':records}
    if source_guid is not None:record['sourceId']=source_guid
    return record

def _conditions(group,by_name,*,depth=0):
    if not isinstance(group,dict) or set(group)-{'combinator','rules','not'} or group.get('combinator') not in ('and','or'):
        raise ValueError('Condition group needs combinator and/or with rules')
    rules=group.get('rules')
    if not isinstance(rules,list) or not rules:raise ValueError('Condition group needs at least one rule')
    if 'not' in group and not isinstance(group['not'],bool):raise ValueError('Condition not must be Boolean')
    if depth>3:raise ValueError('Condition groups are limited to three nested levels')
    out={'id':_rule_id('g'),'combinator':group['combinator'],'rules':[]}
    if group.get('not'):out['not']=True
    for rule in rules:
        if isinstance(rule,dict) and 'combinator' in rule:
            out['rules'].append(_conditions(rule,by_name,depth=depth+1));continue
        if not isinstance(rule,dict) or set(rule)-{'field','operator','value'}:raise ValueError('Condition rule needs field, operator and value')
        column=by_name.get(rule.get('field'))
        if column is None:raise ValueError('Condition column not configured: '+str(rule.get('field')))
        data_type=CONDITION_TYPES.get(column.get('columnType'))
        if data_type is None:raise ValueError('Conditions support text, number, decimal and checkbox columns only: '+column['columnName'])
        if rule.get('operator') not in OPERATORS:raise ValueError('Unsupported condition operator: '+str(rule.get('operator')))
        if rule['operator'] not in ('empty','notEmpty') and 'value' not in rule:raise ValueError('Condition value required')
        out['rules'].append({'id':_rule_id('r'),'field':column['columnName'],'operator':rule['operator'],
                             'value':copy.deepcopy(rule.get('value')),'fieldDataType':data_type})
    return out

def _recipients(values,label,*,required):
    if values is None and not required:return None
    if not isinstance(values,list) or (required and not values):raise ValueError(label+' recipients required')
    out=[]
    for value in values:
        email=value.get('email') if isinstance(value,dict) else value
        if not isinstance(email,str) or not (EMAIL.fullmatch(email) or ('{{' in email and '}}' in email)):
            raise ValueError(label+' recipient must be an email address or a {{...}} reference')
        if isinstance(value,dict) and set(value)-{'email','name'}:raise ValueError(label+' recipient supports email and name')
        out.append(copy.deepcopy(value))
    return out

def _action_config(kind,config):
    if not isinstance(config,dict):raise ValueError(kind+' action config must be an object')
    if kind=='SEND_MAIL':
        if set(config)-{'subject','body','to','cc','bcc','description'}:raise ValueError('SEND_MAIL supports subject, body, to, cc, bcc, description')
        result={'description':_text(config.get('description',''),'Email description',allow_empty=True),
                'subject':_text(config.get('subject'),'Email subject',998),'body':_text(config.get('body'),'Email body',100000),
                'to':_recipients(config.get('to'),'to',required=True)}
        for key in ('cc','bcc'):
            if config.get(key) is not None:result[key]=_recipients(config[key],key,required=False)
        return result
    if kind=='MS_TEAMS':
        if set(config)-{'message','channelDetails'}:raise ValueError('MS_TEAMS supports message and channelDetails')
        channels=config.get('channelDetails')
        if not isinstance(channels,list) or not channels:raise ValueError('MS_TEAMS needs channelDetails')
        keys={'webhookUrl','channelName','teamName','teamId','channelId'}
        for channel in channels:
            if not isinstance(channel,dict) or set(channel)!=keys or any(not isinstance(channel[k],str) or not channel[k] for k in keys):
                raise ValueError('Teams channel needs '+', '.join(sorted(keys)))
            if not channel['webhookUrl'].startswith('https://'):raise ValueError('Teams webhookUrl must use https')
        return {'message':_text(config.get('message'),'Teams message',28000),'channelDetails':copy.deepcopy(channels)}
    allowed={'connectionId','schema','table','fields'}|({'uniqueColumn'} if kind=='CREATE_RECORD' else {'conditions'})
    if set(config)-allowed or not {'connectionId','schema','table','fields'}<=config.keys():
        raise ValueError(kind+' needs connectionId, schema, table and fields')
    for key in ('connectionId','schema','table'):
        if not isinstance(config[key],(str,int)) or isinstance(config[key],bool) or not str(config[key]).strip():raise ValueError(kind+' '+key+' required')
    if not isinstance(config['fields'],dict) or not config['fields']:raise ValueError(kind+' fields must map target columns to values')
    if kind=='UPDATE_RECORD':
        group=config.get('conditions')
        if not isinstance(group,dict) or group.get('combinator') not in ('and','or') or not isinstance(group.get('rules'),list) or not group['rules']:
            raise ValueError('UPDATE_RECORD needs a conditions group selecting the target rows')
    return copy.deepcopy(config)

def automation_record(name,trigger,actions,columns,*,watch_columns=None,conditions=None,description='',source_guid=None):
    """One automations.json entry: a row-event trigger and an ordered action block.

    ``trigger`` is ROW_CREATED, ROW_UPDATED or ROW_DELETED. ``actions`` is an
    ordered list of ``{"type": SEND_MAIL|MS_TEAMS|CREATE_RECORD|UPDATE_RECORD,
    "config": {...}}``. Values may use the product's ``{{...}}`` references;
    those expressions are passed through, not evaluated here.
    """
    if not isinstance(name,str) or len(name)>255 or not AUTOMATION_NAME.fullmatch(name.strip()):
        raise ValueError('Automation name must start with a letter and use letters, digits, spaces, -, _ or ()')
    name=name.strip()
    if trigger not in TRIGGERS:raise ValueError('Trigger must be ROW_CREATED, ROW_UPDATED or ROW_DELETED')
    by_name=_by_name(columns)
    trigger_config={'conditions':None if conditions is None else _conditions(conditions,by_name)}
    if watch_columns is not None:
        if trigger!='ROW_UPDATED':raise ValueError('watch_columns apply only to ROW_UPDATED')
        if not isinstance(watch_columns,list) or not watch_columns or len(set(watch_columns))!=len(watch_columns) or any(c not in by_name for c in watch_columns):
            raise ValueError('watch_columns must list distinct configured columns')
        trigger_config['watchColumns']=list(watch_columns)
    if not isinstance(actions,list) or not actions:raise ValueError('At least one automation action is required')
    group_id=guid();ids=[guid() for _ in actions];steps={}
    for index,(action,action_id) in enumerate(zip(actions,ids)):
        if not isinstance(action,dict) or set(action)!={'type','config'} or action['type'] not in ACTIONS:
            raise ValueError('Automation action needs type ('+', '.join(ACTIONS)+') and config')
        code,key=ACTIONS[action['type']]
        steps[action_id]={'actionId':action_id,'actionType':str(code),'previousActionId':ids[index-1] if index else None,
                          'nextActionId':ids[index+1] if index+1<len(ids) else None,'config':{key:_action_config(action['type'],action['config'])}}
    config={'id':guid(),'name':name,
            'trigger':{'id':guid(),'triggerType':str(TRIGGERS[trigger]),'description':_text(description or '','Trigger description',allow_empty=True),
                       'triggerConfig':trigger_config},
            'entryGroupId':group_id,
            'groups':{group_id:{'groupId':group_id,'groupType':str(ACTION_BLOCK),'previousGroupId':None,'nextGroupId':None,
                                'entryActionId':ids[0],'actions':steps,'position':0}},
            'variables':{}}
    record={'recordGuid':guid(),'name':name,'triggerType':TRIGGERS[trigger],'config':config}
    if source_guid is not None:record['sourceId']=source_guid
    return record

def _lookup_config(value):
    """A LOOKUP rule's approver table, copied as given: tableName, approverColumn and conditionalColumn pairs."""
    if not isinstance(value,dict) or set(value)!={'tableName','approverColumn','conditionalColumn'}:
        raise ValueError('lookup_config needs tableName, approverColumn and conditionalColumn')
    for key in ('tableName','approverColumn'):_text(value[key],'lookup_config '+key)
    pairs=value['conditionalColumn']
    if (not isinstance(pairs,list) or not pairs or any(not isinstance(p,dict) or set(p)!={'columnName','lookupColumnName'} for p in pairs)):
        raise ValueError('lookup_config conditionalColumn must list columnName and lookupColumnName pairs')
    for pair in pairs:
        for key in ('columnName','lookupColumnName'):_text(pair[key],'lookup_config '+key)
    return copy.deepcopy(value)

def approval_record(rule_type=None,levels=None,*,source_guid,persist_flag=None,multi_level_enabled=None,filters=None,lookup_config=None):
    """The one approvals.json record of a PowerTable: rule type, persist flag, multi-level flag, levels and routing filters.

    ``levels`` is an ordered list of ``{"name", "description"}``, numbered from 1.
    ``filters`` is a list of ``{"name", "filter": object|null, "order"}``. The
    import reads both lists from this record, so both are always written.
    ``multi_level_enabled`` is optional: written as stated, left out when the
    request omits it, and never inferred from the levels. ``approvalLevel`` is the
    number of levels, as the product's own workflow API stores it; multi-level
    approval finishes only at that level. A LOOKUP rule needs ``lookup_config``,
    which is stored as ``settings.lookupConfig``.
    """
    from .validate import Schemas
    if rule_type is None:raise ValueError('rule_type required; it has no default')
    if not isinstance(rule_type,str) or rule_type not in APPROVAL_RULES:raise ValueError('rule_type must be DEFAULT, MANUAL or LOOKUP')
    if persist_flag is None:raise ValueError('persist_flag required; it has no default')
    if not isinstance(persist_flag,str) or persist_flag not in PERSIST_FLAGS:
        raise ValueError('persist_flag must be SAVE_AFTER_REVIEW or SAVE_BEFORE_REVIEW')
    if multi_level_enabled is not None and not isinstance(multi_level_enabled,bool):raise ValueError('multi_level_enabled must be Boolean')
    if rule_type=='LOOKUP':
        if lookup_config is None:raise ValueError('A LOOKUP rule needs lookup_config: tableName, approverColumn and conditionalColumn')
        settings={'lookupConfig':_lookup_config(lookup_config)}
    elif lookup_config is not None:raise ValueError('lookup_config applies only to a LOOKUP rule')
    else:settings=None
    if not isinstance(levels,list) or not levels:raise ValueError('Name at least one approval level')
    approval_levels=[];names=set()
    for number,level in enumerate(levels,1):
        if not isinstance(level,dict) or set(level)!={'name','description'}:raise ValueError('Approval level supports name and description only')
        name=_text(level['name'],'Approval level name')
        if name.casefold() in names:raise ValueError('Duplicate approval level: '+name)
        names.add(name.casefold())
        approval_levels.append({'name':name,'description':_text(level['description'],'Approval level description',allow_empty=True),'level':number})
    filters=[] if filters is None else filters
    if not isinstance(filters,list) or any(not isinstance(f,dict) for f in filters):raise ValueError('filters must be a list of objects')
    routing=[];names=set();orders=set()
    for item in filters:
        if not {'name','filter'}<=set(item) or set(item)-{'name','filter','order'}:raise ValueError('Approval filter needs name, filter and order')
        name=_text(item['name'],'Approval filter name')
        if item['filter'] is not None and not isinstance(item['filter'],dict):raise ValueError('Approval filter must be an object or null')
        order=item.get('order')
        if order is None:raise ValueError('Approval filter order required; it has no default')
        if isinstance(order,bool) or not isinstance(order,int) or order<0:raise ValueError('Approval filter order must be a nonnegative integer')
        if order in orders:raise ValueError('Approval filter order '+str(order)+' is taken')
        if name.casefold() in names:raise ValueError('Duplicate approval filter: '+name)
        names.add(name.casefold());orders.add(order)
        routing.append({'name':name,'filter':copy.deepcopy(item['filter']),'order':order})
    record={'recordGuid':guid(),'sourceId':source_guid,'ruleType':APPROVAL_RULES[rule_type],'persistFlag':PERSIST_FLAGS[persist_flag],
            'approvalLevel':len(approval_levels),**({'settings':settings} if settings else {}),
            **({} if multi_level_enabled is None else {'multiLevelEnabled':1 if multi_level_enabled else 0}),
            'approvalLevels':approval_levels,'approvalFilter':routing}
    # The published schema types these members at the top level; check the record's values against those definitions.
    url=schema('PowerTable/Approvals')
    Schemas().check({'$schema':url,**{k:v for k,v in record.items() if k not in ('recordGuid','sourceId')}},url)
    return record

def feature_parts(prefix,raw,*,forms=None,automations=None,approvals=None):
    """New or extended forms.json/automations.json and a new approvals.json for one PowerTable visual folder."""
    columns=raw[prefix+'columnConfigs.json']['columnConfigs'];source_guid=raw[prefix+'source.json']['source']['recordGuid']
    changes={};summary={'forms':[],'automations':[],'approvals':None}
    for leaf,key,items,build,label,schema_name,allowed in (
        ('forms.json','forms',forms,lambda spec:form_record(columns=columns,source_guid=source_guid,**spec),'title','PowerTable/Forms',
         {'title','fields','description','restrict_multiple_entry','config'}),
        ('automations.json','automations',automations,lambda spec:automation_record(columns=columns,source_guid=source_guid,**spec),'name','PowerTable/Automations',
         {'name','trigger','actions','watch_columns','conditions','description'})):
        if not items:continue
        if not isinstance(items,list) or any(not isinstance(i,dict) for i in items):raise ValueError(key+' must be a list of objects')
        for spec in items:
            if set(spec)-allowed:raise ValueError('Unsupported '+key[:-1]+' field: '+', '.join(sorted(set(spec)-allowed)))
        current=copy.deepcopy(raw.get(prefix+leaf) or {'$schema':schema(schema_name),key:[]})
        existing=current.get(key)
        if not isinstance(existing,list):raise ValueError('Existing '+leaf+' has no '+key+' list')
        names={str(i.get(label,'')).strip().casefold() for i in existing if isinstance(i,dict)}
        for spec in items:
            record=build(spec)
            if record[label].casefold() in names:raise ValueError('A '+key[:-1]+' with this '+label+' already exists: '+record[label])
            names.add(record[label].casefold());existing.append(record);summary[key].append(record[label])
        changes[prefix+leaf]=current
    if approvals is not None:
        path=prefix+'approvals.json'
        if path in raw:raise ValueError('approvals.json already exists; change the exported workflow instead of rebuilding it')
        if not isinstance(approvals,dict) or set(approvals)-APPROVAL_REQUEST:
            raise ValueError('Unsupported approval field: '+(', '.join(sorted(set(approvals)-APPROVAL_REQUEST)) if isinstance(approvals,dict) else 'object required'))
        record=approval_record(source_guid=source_guid,**approvals)
        changes[path]={'$schema':schema('PowerTable/Approvals'),'approvals':record}
        summary['approvals']={'ruleType':{v:k for k,v in APPROVAL_RULES.items()}[record['ruleType']],
                              'levels':[level['name'] for level in record['approvalLevels']]}
    if not changes:raise ValueError('Request at least one form, automation or approval workflow')
    return changes,summary

def automation_identity_warnings(raw):
    """Product exports omit automation recordGuid, so import cannot match those records."""
    unmatched=[str(a.get('name','')) for path,value in raw.items() if path.endswith('/automations.json') and isinstance(value,dict)
               for a in (value.get('automations') or []) if isinstance(a,dict) and not a.get('recordGuid')]
    if not unmatched:return []
    return ['Automations without recordGuid ('+', '.join(unmatched)+') cannot be matched on import and may be recreated '
            'or overwritten, losing run history. Verify every automation after publishing.']

def powertable_prefix(raw,sheet_guid):
    sheets=[s for s in raw['definition.json']['sheets'] if s.get('recordGuid')==sheet_guid and s.get('sheetType')=='POWERTABLE']
    if len(sheets)!=1:raise ValueError('Select one current PowerTable sheet GUID')
    owned=[v for v in sheets[0]['workloadItemEntityVisuals'] if v.get('visualType')=='POWERTABLE' and not v.get('isEmbedded',False)]
    if len(owned)!=1:raise ValueError('One directly owned PowerTable visual required; configure the table first')
    prefix=f"sheets/{sheet_guid}/visuals/{owned[0]['visualId']}/"
    if prefix+'source.json' not in raw or prefix+'columnConfigs.json' not in raw:raise ValueError('PowerTable source and columns are not configured')
    return prefix

def add_features(envelope,*,sheet_guid,forms=None,automations=None,approvals=None):
    """Scoped candidate adding Forms, Automations or an approval workflow; every other part keeps its bytes."""
    from .validate import check_powertable_parts
    raw=unpack(envelope);original=parts(envelope);prefix=powertable_prefix(raw,sheet_guid)
    changes,summary=feature_parts(prefix,raw,forms=forms,automations=automations,approvals=approvals)
    check_powertable_parts({**raw,**changes},prefix)
    existing={p:v for p,v in changes.items() if p in original};added={p:v for p,v in changes.items() if p not in original}
    candidate=patch(envelope,existing,{p:sha(original[p]) for p in existing}) if existing else copy.deepcopy(envelope)
    if added:candidate.get('definition',candidate)['parts'].extend(pack(added)['definition']['parts'])
    after=parts(candidate)
    for path,payload in original.items():
        if path not in changes and after[path]!=payload:raise ValueError('Unrelated part changed: '+path)
    row_add=next((s for s in raw[prefix+'sourceSettings.json']['sourceSettings'] if s.get('name')=='ROW_ADD'),None) if prefix+'sourceSettings.json' in raw else None
    warnings=[]
    if summary['forms'] and not (row_add and row_add.get('settings',{}).get('enabled') and row_add.get('filters')):
        warnings.append('Row access does not allow adding rows; form submissions need ROW_ADD access')
    warnings+=automation_identity_warnings({**raw,**changes})
    if summary['approvals']:
        warnings.append('approvals.json nests ruleType, persistFlag, levels and filters in one approvals record, the shape this '
                        'package\'s import check reads; the Plan definition article lists them at the top level. Confirm the '
                        'workflow in the product after publishing, and assign approver users there.')
    return candidate,{'sheetGuid':sheet_guid,'addedForms':summary['forms'],'addedAutomations':summary['automations'],
        'addedApprovals':summary['approvals'],
        'changedParts':sorted(existing),'addedParts':sorted(added),'preservedPartCount':len(original)-len(existing),
        'warnings':warnings,'approvers':'not in definition; no supported public route',
        'deployment':'not run','runtimeValidation':'not run'}
