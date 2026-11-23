"""Protect the requested import contents; never invent a replacement workflow.

Checks are local definition checks, not proof of backend initialization or UI
behavior. The original request must be captured before any scope transformation.
"""
import copy


def require_base_input_contract(measure):
    if measure.get('kind')=='DataInput' and (
            'typed' in measure or measure.get('inputKind','Number')!='Number'):
        raise ValueError('UNSUPPORTED_BASE_INPUT: '+measure.get('key','?')+
            ' needs its documented typed-input phase; do not cast it to Number or strip other measures')
    if 'visualColumn' in measure:
        raise ValueError('Use the documented visual_column option; visualColumn is not a consumed builder field')


def require_import_contract(requested_spec,authored,raw=None):
    """Verify unfiltered base requirements against a construction or candidate.

    Unimplemented phases belong in a recipe's explicit post section, never
    in a rewritten/stripped base specification. Real reference-only requests are
    valid. No dummy input is required or invented.
    """
    raw=authored['raw'] if raw is None else raw
    declarations=raw['definition.json']['sheets']
    identities={i['sheetId']:i for i in authored['identities']}
    checked=rules_checked=0
    for sheet in requested_spec['sheets']:
        matches=[s for s in declarations if s['sheetType']=='PLANNING' and s['displayName']==sheet['name']]
        if len(matches)!=1:raise ValueError('IMPORT_CONTRACT: missing or ambiguous requested sheet '+sheet['name'])
        identity=identities.get(matches[0]['recordGuid'])
        if not identity:raise ValueError('IMPORT_CONTRACT: missing authored identity for '+sheet['name'])
        prefix=f"sheets/{identity['sheetId']}/visuals/{identity['visualId']}/"
        records=raw.get(prefix+'dataInput.json',{}).get('columns',[])
        vs=raw.get(prefix+'properties.json',{}).get('properties',{}).get('visualState',{})
        for m in sheet['measures']:
            require_base_input_contract(m)
            mid=identity['measures'].get(m['key'])
            found=[r for r in records if r['measureGuid']==mid]
            if len(found)!=1:raise ValueError('IMPORT_CONTRACT: missing or duplicate '+sheet['name']+'/'+m['key'])
            meta=found[0]['columnMeta'];kind=meta['measure_type']
            if m.get('visual_column'):
                kind=kind.get('VisualColumn',{})
            if set(kind)!={m['kind']}:
                raise ValueError('IMPORT_CONTRACT: changed measure kind '+sheet['name']+'/'+m['key'])
            if m['kind']=='DataInput' and set(kind['DataInput'].get('column_type',{}))!={'Number'}:
                raise ValueError('IMPORT_CONTRACT: changed Number input '+m['key'])
            if m['kind']=='Formula':
                from .construct import expression
                if kind['Formula'].get('formula')!=expression(m['formula'],identity['measures']):
                    raise ValueError('IMPORT_CONTRACT: changed formula '+m['key'])
            if not any(r['id']==mid for r in vs.get('manage_measures',[])):
                raise ValueError('IMPORT_CONTRACT: unregistered measure '+m['key'])
            checked+=1
        requested_anchors = [dict(m['anchor'], measure_id=identity['measures'][m['key']])
                             for m in sheet['measures'] if 'anchor' in m]
        if requested_anchors:
            from .anchor_measures import apply_anchors
            props = raw[prefix+'properties.json']['properties']
            seed = copy.deepcopy(props)
            for member in seed['visualState']['manage_measures']:
                member.pop('anchor_config', None)
            expected = apply_anchors(seed, identity['visualId'], requested_anchors)['properties']['visualState']
            members = {m['id']:m for m in vs.get('manage_measures', [])}
            for member in expected['manage_measures']:
                if member.get('anchor_config'):
                    actual = members[member['id']].get('anchor_config', {})
                    if any(actual.get(k) != v for k,v in member['anchor_config'].items()):
                        raise ValueError('IMPORT_CONTRACT: missing or altered anchor '+member['id'])
            if expected['totals_config'] != vs.get('totals_config'):
                raise ValueError('IMPORT_CONTRACT: required anchor entry total hidden')
        if sheet.get('conditionalFormatting'):
            from .matrix_formatting import compile_formatting,symbolic_rules
            seed=copy.deepcopy(vs)
            seed.pop('cfProps',None);seed.pop('jet_cfProps',None)
            expected=compile_formatting(seed,{'rules':symbolic_rules(sheet['conditionalFormatting'],identity['measures'])})['state']
            for store in ('cfProps','jet_cfProps'):
                for rule in expected[store]['rules']:
                    found=[r for r in vs.get(store,{}).get('rules',[]) if r.get('name')==rule['name']]
                    if len(found)!=1 or any(found[0].get(k)!=v for k,v in rule.items()):
                        raise ValueError('IMPORT_CONTRACT: missing or altered CF '+sheet['name']+'/'+rule['name'])
            rules_checked+=len(sheet['conditionalFormatting'])
    return {'status':'passed','sheets':len(requested_spec['sheets']),'measures':checked,
            'conditionalFormattingRules':rules_checked,'evidence':'static-definition','runtime':'not-tested'}


def require_authored_flow(authored,requested_spec=None,raw=None):
    request=requested_spec if requested_spec is not None else authored.get('buildRequest')
    if request is None:
        raise ValueError('IMPORT_CONTRACT: original base buildRequest is required; rebuild locally from the requested spec')
    return require_import_contract(request,authored,raw)
