# Anchor measures: business grain, display and saved configuration



Use this guide when a policy belongs at a broader grain than the detailed plan,
or when a measure is needed by detailed formulas but should not repeat at every
hierarchy level. The user need not say **anchor**. First identify who maintains
independently different values and when those values can change.

## Find the right pattern

| Business request | Anchor decision | Detailed model keeps |
| --- | --- | --- |
| Enter one company-wide annual assumption | No row dimensions; Year | Employee/product/month detail and existing formulas |
| Maintain one regional policy per year | Region; Year | Independent region policies; detail uses its own region's policy |
| Share one product policy across regions | Product; Year | Region detail, without adding Region to the input grain |
| Change a department target quarterly | Department; Year + Quarter | Role/month detail; no implied monthly hiring schedule |
| Use a regional factor with no time variation | Region; no column dimensions | Period calculations; entry at Region × Total |
| Keep an assumption in leaf calculations, hide repeated assumption rows | Its real business grain; `display_at_all_levels: false` | Underlying values, formula dependencies and detailed output measures |
| Show an existing YTD measure once per region | Region; no column dimensions | Existing DAX/time intelligence; no input rights |
| Show a calculated quarterly margin only where meaningful | Region; Year + Quarter | Quarter profit ÷ quarter revenue; not average monthly margins |

An omitted axis means **All rows** or **Total column**. At least one dimension
must be selected across the axes. The dimensions form one joint intersection,
not a set of independent input levels. Product alone and Region × Product are
different decisions. Use unique identities when the same department/product label
appears under different parents. Do not add every parent merely to match the grid.

Recommend anchors when the measure's decision/display grain is coarser than the
sheet grain. Do not apply them to every measure. Keep an ordinary detailed input
when independent values really are required at each leaf. Use storage Context
for independent scenario/version coordinates outside the axes, From Sheets or
InfoBridge for cross-source reuse, and lookup for reference-table retrieval.
Anchoring is not a replacement for those capabilities or for a saved allocation
rule. Preserve explicit user choices.

Before authoring, record: measure identity and type; full sheet grain; independent
row dimensions; calendar cadence; eligible scope; existing aggregation and
distribution; consuming formulas; repeated-instance display preference; input
permissions/locks; and the visible entry intersection. Resolve only meaningful
ambiguities. Rates and amounts require different distribution decisions.

## Visibility without losing formula availability

This is a primary use case, not merely a cosmetic side effect. A region-level
assumption can be visible at Region while the employee/customer/SKU formula
continues to consume the applicable underlying value at its leaf grain. Use
`display_at_all_levels: false` to omit repeated non-anchor **measure instances**
where the layout permits. Do not remove the measure registration, hide the whole
measure via `visible: false`, delete inputs, replace formula references, or
zero/blank the data to achieve that appearance.

Functional examples (illustrative designs; not newly deployed examples):

| Scenario | Visible assumption | Detailed consumer and business reason |
| --- | --- | --- |
| Regional employee benefits | Region × Year: Benefits % | Each employee-month calculates raised salary × (1 + Benefits %). The employee cost remains visible; repeating Benefits % beneath every employee adds clutter. |
| Pharma market rebate policy | Market × Year: Standard Rebate % | Product/customer/month net revenue uses gross sales × (1 − applicable rebate). Keep policy on the market line, detailed revenue below. Tender-specific exceptions need separate business logic/grain. |
| Plant quality loss | Plant × Year × Quarter: Scrap % | SKU-month gross production = ceil(good-unit demand ÷ (1 − Scrap %)). Show the quarterly plant policy and detailed production, without repeated SKU assumption rows. |
| Regional freight uplift | Region × Year: Freight Uplift % | Route/customer/month freight cost uses its own baseline × (1 + regional uplift). Hide repeated policy rows, retain detailed costs. This is not allocation of an absolute freight pool. |
| Product standard price | Product × Year: Price | Store/customer/month revenue uses units × applicable price. Share across omitted Region only if pricing is truly global. Preserve product-specific annual input and detail revenue. |
| Department savings target | Department × Year: Reduction % | Account-month target expense uses baseline × (1 − reduction). Show the department target and account outcomes; detailed initiatives remain a separate plan. |

The policy rate may be copied into eligible leaves by established input behavior;
the anchor itself is not a new dynamic lookup, broadcast or calculation engine.
Existing detailed formulas continue to use those values. Hiding a row does not
prove that a not-yet-populated leaf has a value. Check the existing distribution
and formula path when requested; do not claim runtime propagation from JSON.

With display ON, repeated instances are visible but still read-only away from
the anchor. Display OFF does not guarantee every shared non-anchor **cell** is
blank. In Measures in Rows, a surviving region assumption row may still span
monthly columns shared with other measures. In default measures-inside-time
layout, omit that measure's columns in non-anchor time blocks. In Measures in
Columns, restrict that measure's own time block; retain other measures' detail.
Recommend Measures in Rows for a readable mixed-grain assumptions-and-outcomes
story; use Measure Model only when a logical hierarchy adds meaning. Grouping
does not change calculations, aggregation or input identity.

## Entry, totals and independent controls

Annual input is at the **Year subtotal**, not January or the first visible month.
Quarterly input is at the **Quarter subtotal**. No row dimension needs the All
row; no column dimension needs the Total column. Use year-qualified time levels
from the actual calendar. Do not invent Quarter/Month identities or add a
nonexistent Quarter when the actual axis is Year → Month.

Keep the universal defaults: Row GT ON, Row subtotal ON, Column GT ON, Column
subtotal OFF. An anchor needing an intermediate Year/Quarter entry is a scoped
exception: expose the required column subtotal on that sheet. The helper changes
only necessary hidden totals, preserving their existing visible placement.
Do not turn off the entry subtotal to hide repeated measure rows. Expansion and
subtotal/individual-node visibility are separate; ensure the intended intersection
is reachable without changing storage grain. The helper does not synthesize
unobserved per-node visibility or expansion properties.

Inputs and Forecast retain `ReadAndEdit` by default and any formula-based lock.
Anchoring narrows direct entry; display ON does not permit descendant entry.
An anchor-read-only descendant is distinct from an independently locked or
unauthorized cell. Applicable allocation from the anchor can reach eligible
children; independent locks and security remain effective.

For suitable rate/factor inputs, Average (Leaf) plus the existing
distribute-parent-to-children behavior can copy the rate. Do not silently change
aggregation or enable distribution on an existing measure while adding anchors.
Never copy an absolute $1m pool into every employee. Resolve an appropriate
allocation method for amounts. Formula/native measures remain calculated and
read-only; anchoring neither grants write rights nor supplies YTD logic.

Persist here, preserving the entire managed-measure member and its identity:

```text
properties.visualState.manage_measures[*].anchor_config
```

```json
{
  "row_dimensions": ["<current native dimension ID>"],
  "col_dimensions": ["<current native Year ID>"],
  "display_at_all_levels": false,
  "dimension_hash": "<computed hash of all current ordered pivot dimensions>"
}
```

IDs are exact decimal **strings**, including values larger than JavaScript's
safe integer. Resolve them from `rowDimensions`/`columnDimensions` using exact
`externalKey`, not display labels, data-input IDs, storage keys or model IDs.

Bundled `runtime.anchor_measures` provides:

- `capture_context(properties, owner_visual_id)`: computes the native layout hash
  from all current ordered pivot dimensions. Works with no existing anchors and
  rejects conflicting, mismatched or stale saved anchor state.
- `apply_anchors(properties, owner_visual_id, requests, ...)`: resolves selected
  fields, upserts only anchor configuration and necessary entry totals, and returns
  a local candidate/change list. It preserves input/formula records, aggregation,
  bindings, locks, storage mappings and every unrelated property.

**Hash contract:** the portable implementation uses
the existing bundled Python XXH3 engine, with no npm dependency or donor report.
`generate_dimension_id(exact_source_id)` produces an unsigned decimal string;
`generate_dimension_hash(all_ordered_row_ids, all_ordered_column_ids)` hashes
`rows.join("-") + "__" + columns.join("-")` and returns lowercase hexadecimal without leading zeroes.

For offline authoring, pass exact current owner properties plus requests:

```json
{
  "properties": "<replace with the complete current properties object>",
  "owner_visual_id": "<actual owner identity in this JSON's namespace>",
  "requests": [{
    "measure_id": "<current managed measure ID>",
    "row_fields": ["PolicyRegion[Region]"],
    "column_fields": ["Calendar[Year]"],
    "display_at_all_levels": false
  }],
  "expose_entry_totals": true
}
```

```sh
python plan.py construct-native anchor --input anchor-request.json --out anchor-candidate.json
```
