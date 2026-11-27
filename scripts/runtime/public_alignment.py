"""Author dashboard geometry in the public Plan definition."""


def geometry(rectangle):
    return {'position': {k: rectangle[k] for k in ('x', 'y')},
            'dimension': {k: rectangle[k] for k in ('width', 'height')}}


def embedded_placement(sheet_id, visual_id, rectangle):
    return {'visualId': visual_id, 'properties': {
        **geometry(rectangle), 'originEntityId': sheet_id, 'lockAspectRatio': False}}


def fresh_matrix_ids(planning_sheets):
    """Predict the create-time IDs for the builder's Planning-first declaration sequence."""
    result = {}
    visual_index = 0
    for sheet_index, sheet in enumerate(planning_sheets, start=1):
        for member in sheet['workloadItemEntityVisuals']:
            if member.get('isEmbedded'):
                continue
            visual_index += 1
            if member['visualType'] == 'PLANNING':
                result[member['visualId']] = {
                    'originEntityId': str(sheet_index), 'visualId': str(visual_index)}
    return result


def check_placements(raw, dashboard):
    sid = dashboard['sheetGuid']
    sheet = raw[f'sheets/{sid}/sheet.json']['properties']
    declared = raw['definition.json']['sheets']
    owner = dashboard['ownerGuid']
    source, = [s['recordGuid'] for s in declared if any(
        v['visualId'] == owner and not v.get('isEmbedded')
        for v in s['workloadItemEntityVisuals'])]
    placement = dashboard.get('placementIds')
    page, = [s for s in declared if s['recordGuid'] == sid]
    if not any(v['visualId'] == owner and v.get('isEmbedded') for v in page['workloadItemEntityVisuals']):
        raise ValueError('Dashboard does not declare its source matrix')
    local_visual = placement['visualId'] if placement else owner
    origin = placement['originEntityId'] if placement else source
    entry, = [v for v in sheet['reactiveVisualProperties'] if v['visualId'] == local_visual]
    if entry['properties']['originEntityId'] != origin:
        raise ValueError('Embedded visual refers to the wrong source sheet')
    for vid, rect in dashboard['placements'].items():
        p = entry['properties'] if vid == owner else raw[f'sheets/{sid}/visuals/{vid}/properties.json']['properties']
        if any(p.get(k) != value for k, value in geometry(rect).items()):
            raise ValueError('Dashboard rectangle mismatch for ' + vid)
    return {'sheetGuid': sid, 'geometrySource': 'public-create', 'visualCount': len(dashboard['placements']),
            'visibility': {'source': 'public-create'}, 'embeddedPlacement': 'report-local-ids' if placement else 'portable-reference-only',
            'rendering': 'not-tested'}
