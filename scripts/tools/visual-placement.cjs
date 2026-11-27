const assert = require('node:assert/strict');
const fs = require('node:fs');

function validRectangle(rectangle) {
    return rectangle && ['x', 'y', 'width', 'height'].every(key => Number.isFinite(rectangle[key])) &&
        rectangle.x >= 0 && rectangle.y >= 0 && rectangle.width > 0 && rectangle.height > 0;
}

function intersects(first, second, gap = 0) {
    return !(first.x + first.width + gap <= second.x ||
        second.x + second.width + gap <= first.x ||
        first.y + first.height + gap <= second.y ||
        second.y + second.height + gap <= first.y);
}

function inventory(response) {
    if (response.statusCode !== 200 || !Array.isArray(response.payload?.visuals)) {
        throw new Error('Expected a successful complete page-properties response');
    }
    const page = response.payload.properties?.properties;
    if (!page || !page.canvasStyle?.dimension) throw new Error('Missing saved canvas configuration');
    const unit = page.canvasStyle.dimension.elementScalingUnit;
    if (!['pixel', 'percentage'].includes(unit)) throw new Error('Unresolved layout units');
    const embedded = page.reactiveVisualProperties ?? [];
    if (!Array.isArray(embedded)) throw new Error('Malformed embedded placement collection');
    const ids = new Set();
    const rectangles = response.payload.visuals.map(visual => {
        if (typeof visual.id !== 'string' || ids.has(visual.id)) throw new Error('Missing or duplicate visual identity');
        ids.add(visual.id);
        const direct = visual.properties?.properties ?? visual.properties;
        const matches = embedded.filter(entry => entry.visualId === visual.id);
        if (matches.length > 1) throw new Error('Ambiguous embedded placement');
        const geometry = visual.isEmbedded ? matches[0]?.properties : direct;
        const rectangle = {
            id: visual.id,
            x: geometry?.position?.x,
            y: geometry?.position?.y,
            width: geometry?.dimension?.width,
            height: geometry?.dimension?.height,
        };
        if (!validRectangle(rectangle)) throw new Error(`Missing or invalid saved geometry for visual ${visual.id}`);
        return rectangle;
    });
    return { page, unit, rectangles };
}

function findPlacement({ bounds, dimension, occupied, gap, margin = gap }) {
    if (!bounds || !dimension || ![bounds.width, bounds.height, dimension.width, dimension.height]
        .every(value => Number.isFinite(value) && value > 0) ||
        !Number.isFinite(gap) || gap < 0 || !Number.isFinite(margin) || margin < 0 ||
        !Array.isArray(occupied) || !occupied.every(validRectangle)) {
        throw new Error('Invalid bounds, requested dimensions, spacing or occupied areas');
    }
    const maximumX = bounds.width - margin - dimension.width;
    const maximumY = bounds.height - margin - dimension.height;
    const horizontal = new Set([margin, maximumX]);
    const vertical = new Set([margin, maximumY]);
    for (const rectangle of occupied) {
        horizontal.add(rectangle.x + rectangle.width + gap);
        horizontal.add(rectangle.x - dimension.width - gap);
        vertical.add(rectangle.y + rectangle.height + gap);
        vertical.add(rectangle.y - dimension.height - gap);
    }
    const xs = [...horizontal].filter(value => value >= margin && value <= maximumX).sort((first, second) => first - second);
    const ys = [...vertical].filter(value => value >= margin && value <= maximumY).sort((first, second) => first - second);
    for (const y of ys) {
        for (const x of xs) {
            const candidate = { x, y, ...dimension };
            if (!occupied.some(rectangle => intersects(candidate, rectangle, gap))) {
                return { position: { x, y }, dimension: { ...dimension } };
            }
        }
    }
    return null;
}

function verifyPlacement({ response, id, intended, bounds, gap, reservedAreas = [] }) {
    const { rectangles, unit } = inventory(response);
    const actual = rectangles.find(rectangle => rectangle.id === id);
    if (!actual) throw new Error('Created visual missing from fresh readback');
    const expected = { ...intended.position, ...intended.dimension };
    for (const key of ['x', 'y', 'width', 'height']) {
        if (!Number.isFinite(expected[key]) || Math.abs(actual[key] - expected[key]) > 1e-9) {
            throw new Error(`Persisted ${key} differs from intended placement`);
        }
    }
    if (!bounds || ![bounds.width, bounds.height].every(value => Number.isFinite(value) && value > 0) ||
        (unit === 'percentage' && (bounds.width !== 1 || bounds.height !== 1)) ||
        actual.x + actual.width > bounds.width || actual.y + actual.height > bounds.height) {
        throw new Error('Persisted visual exceeds layout bounds');
    }
    if (!Number.isFinite(gap) || gap < 0) throw new Error('Invalid verification spacing');
    if (!Array.isArray(reservedAreas) || !reservedAreas.every(validRectangle)) throw new Error('Invalid reserved areas');
    if ([...rectangles.filter(rectangle => rectangle.id !== id), ...reservedAreas]
        .some(rectangle => intersects(actual, rectangle, gap))) {
        throw new Error('Persisted placement overlaps or violates spacing');
    }
    return { status: 'passed-persisted-geometry', rectangle: actual };
}

function selfTest() {
    const fixture = (unit = 'pixel') => ({ statusCode: 200, payload: {
        properties: { properties: { canvasStyle: { dimension: { type: 'CUSTOM', width: 200, height: 100, elementScalingUnit: unit } },
            reactiveVisualProperties: [{ visualId: 'embed', properties: { position: { x: 100, y: 5 }, dimension: { width: 50, height: 40 } } }] } },
        visuals: [
            { id: 'filter', properties: { properties: { position: { x: 5, y: 5 }, dimension: { width: 40, height: 40 } } } },
            { id: 'embed', isEmbedded: true, properties: { properties: { position: { x: 0, y: 0 }, dimension: { width: 200, height: 100 } } } },
        ],
    } });
    const response = fixture();
    const { rectangles } = inventory(response);
    assert.equal(rectangles[1].x, 100);
    const input = { bounds: { width: 200, height: 100 }, dimension: { width: 40, height: 40 }, occupied: rectangles, gap: 5 };
    const original = JSON.stringify(input);
    const placed = findPlacement(input);
    assert.deepEqual(placed, { position: { x: 50, y: 5 }, dimension: input.dimension });
    assert.equal(JSON.stringify(input), original);
    const next = findPlacement({ ...input, occupied: [...rectangles, { ...placed.position, ...placed.dimension }] });
    assert.deepEqual(next.position, { x: 155, y: 5 });
    assert.equal(findPlacement({ ...input, dimension: { width: 200, height: 100 } }), null);
    assert.equal(findPlacement({ ...input, occupied: [{ x: 0, y: 0, width: 200, height: 100 }] }), null);
    assert.deepEqual(findPlacement({ ...input, occupied: [], dimension: { width: 190, height: 90 } }).position, { x: 5, y: 5 });
    const normalized = findPlacement({ bounds: { width: 1, height: 1 }, dimension: { width: 0.3, height: 0.4 }, occupied: [{ x: 0.005, y: 0.005, width: 0.3, height: 0.4 }], gap: 0.005 });
    assert.equal(normalized.dimension.width, 0.3);
    assert(normalized.position.x >= 0.31 && normalized.position.x < 0.311);
    assert.throws(() => inventory({ statusCode: 200, payload: { visuals: [] } }), /canvas/);
    const missing = fixture(); delete missing.payload.properties.properties.reactiveVisualProperties;
    assert.throws(() => inventory(missing), /geometry/);
    const duplicate = fixture(); duplicate.payload.visuals.push(duplicate.payload.visuals[0]);
    assert.throws(() => inventory(duplicate), /duplicate/);
    assert.throws(() => findPlacement({ ...input, dimension: { width: NaN, height: 40 } }), /Invalid/);
    response.payload.visuals.push({ id: 'new', properties: { properties: placed } });
    const verification = { response, id: 'new', intended: placed, bounds: input.bounds, gap: 5 };
    assert.equal(verifyPlacement(verification).status, 'passed-persisted-geometry');
    assert.throws(() => verifyPlacement({ ...verification, reservedAreas: [{ x: 50, y: 5, width: 1, height: 1 }] }), /overlaps/);
    assert.throws(() => verifyPlacement({ ...verification, bounds: { width: NaN, height: 100 } }), /bounds/);
    assert.throws(() => verifyPlacement({ ...verification, intended: { ...placed, position: { x: 51, y: 5 } } }), /differs/);
    response.payload.visuals[2].properties.properties.position.x = 44;
    assert.throws(() => verifyPlacement({ ...verification, intended: { ...placed, position: { x: 44, y: 5 } } }), /overlaps/);
    console.log('PASS: headless inventory, pixel/fraction placement, sequential placement, exact-fit/no-fit, immutability, invalid input and persisted verification checks.');
}

module.exports = { inventory, findPlacement, verifyPlacement, intersects };
if (require.main === module) {
    if (process.argv.includes('--self-test')) selfTest();
    else {
        const input = JSON.parse(fs.readFileSync(0, 'utf8'));
        if (input.mode === 'verify') console.log(JSON.stringify(verifyPlacement(input)));
        else {
            const snapshot = inventory(input.response);
            if (snapshot.unit === 'percentage' && (input.bounds?.width !== 1 || input.bounds?.height !== 1)) {
                throw new Error('Percentage placement bounds must be 1 by 1');
            }
            const gap = input.gap ?? (snapshot.unit === 'percentage' ? 0.005 : 5);
            const placement = findPlacement({ ...input, gap, occupied: [...snapshot.rectangles, ...(input.reservedAreas ?? [])] });
            console.log(JSON.stringify({ status: placement ? 'placed' : 'no-fit', placement }));
        }
    }
}