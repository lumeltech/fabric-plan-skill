"""Allocate integer dashboard coordinates across a stack of flexible containers."""

def fit_stack(top, bottom, gap, weights):
    """Return (y, height) pairs. Equal weights give peers equal height within a pixel."""
    if not weights or any(w <= 0 or not isinstance(w, int) for w in weights):
        raise ValueError("Provide one positive integer weight per container")
    if gap < 0 or top < 0:
        raise ValueError("Invalid stack origin or gap")
    usable = bottom - top - gap * (len(weights) - 1)
    total = sum(weights)
    result = []
    cumulative = 0
    previous = 0
    for index, weight in enumerate(weights):
        cumulative += weight
        edge = usable * cumulative // total
        if edge <= previous:
            raise ValueError("Insufficient stack height")
        result.append((top + previous + index * gap, edge - previous))
        previous = edge
    return result

def reading_height(width, viewport):
    """Fit the canvas width to the drawable Reading area. Inputs use the same unit."""
    if not isinstance(viewport, dict) or set(viewport) != {'width', 'height'}:
        raise ValueError('viewport needs drawable width and height')
    if any(type(v) is not int or v <= 0 for v in viewport.values()):
        raise ValueError('viewport dimensions must be positive integer pixels')
    return width * viewport['height'] // viewport['width']


def fill_columns(rectangles, columns, bottom):
    """Distribute surplus height over flexible rows while retaining authored gutters."""
    if not isinstance(columns, list) or not columns:
        raise ValueError('fitColumns needs at least one column')
    seen = set()
    for column in columns:
        rows = column.get('rows') if isinstance(column, dict) else None
        weights = column.get('weights') if isinstance(column, dict) else None
        if not isinstance(rows, list) or not rows or not isinstance(weights, list) or len(rows) != len(weights):
            raise ValueError('Each fit column needs rows and one weight per row')
        if any(type(w) is not int or w < 0 for w in weights) or not sum(weights):
            raise ValueError('Use nonnegative row weights and at least one flexible row')
        groups = []
        last = 0
        for row in rows:
            keys = [row] if isinstance(row, str) else row
            if not isinstance(keys, list) or not keys:
                raise ValueError('Each row needs one or more visual slots')
            for key in keys:
                if not isinstance(key, str) or key not in rectangles or key in seen:
                    raise ValueError('Unknown or repeated fit slot: '+str(key))
                seen.add(key)
            group = [rectangles[k] for k in keys]
            y, height = group[0]['y'], group[0]['height']
            if y < last or any((r['y'], r['height']) != (y, height) for r in group):
                raise ValueError('Fit rows must align horizontally and be ordered vertically')
            groups.append(group)
            last = y + height
        extra = bottom - last
        if extra < 0:
            raise ValueError('Fit baseline would clip the last row')
        previous = cumulative = 0
        total = sum(weights)
        for group, weight in zip(groups, weights):
            cumulative += weight
            edge = extra if cumulative == total else extra * cumulative // total
            for r in group:
                r['y'] += previous
                r['height'] += edge - previous
            previous = edge
