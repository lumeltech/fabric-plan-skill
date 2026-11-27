"""Native Home authoring checks; these are not a browser rendering certificate.

Widths are pixel dimensions, not percentages or Intelligence grid units. The
240px rejection floor and 320px preferred text width are authoring heuristics,
not server schema limits. Unknown viewport => full-width stacked text.
"""
import copy, math

TEXT_TYPES = {'text', 'header-image-text'}

def positive_number(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value > 0

def audit_home_fit(layout, content_width_px=None, gap_px=24):
    if content_width_px is not None and not positive_number(content_width_px):
        raise ValueError('Home content_width_px must be a finite positive pixel width')
    if not positive_number(gap_px):
        raise ValueError('Home gap_px must be a finite positive pixel width')
    items = {item['id']: item for item in layout.get('items', [])}
    issues = []
    def issue(row, code, message, severity='error'):
        issues.append({'rowId': row.get('id'), 'code': code, 'severity': severity, 'message': message})
    for row in layout.get('rows', []):
        seq = row.get('itemIds', [])
        widths = row.get('widths', [None] * len(seq))
        if len(widths) != len(seq) or any(i not in items for i in seq):
            issue(row, 'row-references', 'Keep itemIds and widths positionally aligned with existing items.')
            continue
        if any(w is not None and not positive_number(w) for w in widths):
            issue(row, 'invalid-width', 'Widths must be null or finite positive pixel numbers, never strings, booleans or percentages.')
            continue
        height = row.get('height')
        ratio = row.get('defaultHeightRatio')
        if any(v is not None and not positive_number(v) for v in (height, ratio)):
            issue(row, 'invalid-height', 'Height and relative sizing hint must be null or finite positive numbers.')
        text_positions = [n for n, item_id in enumerate(seq) if items[item_id]['type'] in TEXT_TYPES]
        for n in text_positions:
            if widths[n] is not None and widths[n] < 240:
                issue(row, 'narrow-text', 'Home widths are pixels: use null for flexible text; values such as 60/40 do not mean percentages. Stack text if space is uncertain.')
        if text_positions and (height is not None or row.get('isHeightManual') is True or ratio is not None):
            issue(row, 'fixed-text-height', 'Text may clip or leave excess whitespace. Prefer height:null, defaultHeightRatio:null and no manual-height flag; otherwise check actual wrapping.', 'warning')
        if content_width_px is not None and seq:
            fixed = sum(w for w in widths if w is not None)
            remaining = content_width_px - gap_px * (len(seq) - 1) - fixed
            flexible = widths.count(None)
            if remaining < 0:
                issue(row, 'row-overflow', 'Fixed widths plus gutters exceed the available Home content width.')
            elif flexible and any(widths[n] is None for n in text_positions) and remaining / flexible < 240:
                issue(row, 'narrow-flex-text', 'Available space leaves text too narrow; stack the blocks into full-width rows.')
        elif len(seq) > 1 and text_positions:
            issue(row, 'unknown-content-width', 'Side-by-side text has no fit evidence. Use stacked full-width rows or check the available content width.', 'warning')
    return {'passed': not any(x['severity'] == 'error' for x in issues), 'issues': issues,
            'validation': 'static-authoring-only', 'rendering': 'not-tested'}

def assert_home_fit(layout, content_width_px=None):
    result = audit_home_fit(layout, content_width_px)
    errors = [x['message'] for x in result['issues'] if x['severity'] == 'error']
    if errors:
        raise ValueError('Home layout: ' + '; '.join(dict.fromkeys(errors)))
    return result

def readable_home_layout(items, rows=None, content_width_px=None):
    """Construct new Home content with flexible, content-sized text/card rows.

    This is an explicit authoring normalization, not a lossless edit of an
    existing Home. Use audit_home_fit on saved layouts before scoped edits.
    """
    from .construct import guid
    from .surfaces import home_layout
    if content_width_px is not None and not positive_number(content_width_px):
        raise ValueError('Home content_width_px must be a finite positive pixel width')
    by_id = {item['id']: item for item in items}
    rows = copy.deepcopy(rows) if rows is not None else [{'itemIds': [item['id']]} for item in items]
    output = []
    for row in rows:
        seq = row['itemIds']
        if not seq or any(i not in by_id for i in seq):
            raise ValueError('Unknown/empty Home row')
        text_only = all(by_id[i]['type'] in TEXT_TYPES for i in seq)
        if text_only:
            # A two-column composition is an opt-in with known content width.
            count = 2 if content_width_px is not None and content_width_px >= 664 else 1
            for start in range(0, len(seq), count):
                ids = seq[start:start+count]
                output.append({'id': row.get('id') if start == 0 else guid(), 'itemIds': ids,
                               'widths': [None] * len(ids), 'height': None})
        elif len(seq) == 1 and by_id[seq[0]]['type'] == 'preview-cards':
            output.append({'id': row.get('id'), 'itemIds': seq, 'widths': [None], 'height': None})
        else:
            output.append(row)
    result = home_layout(items, output)
    assert_home_fit(result, content_width_px)
    return result
