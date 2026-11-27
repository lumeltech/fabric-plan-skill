# Saved views, parameters, Home and PowerTable inspection

Use this guide when a user supplies a working Plan as evidence for bookmarks,
navigators, shared Planning embeds, parameters or an existing SQL PowerTable.
Discover **SAVED-VIEW-REFERENCE**. A reference is evidence for a contract; it is
not a template to clone or a source of IDs for another application.

## Contents

- [Read the complete current configuration](#read-the-complete-current-configuration)
- [What a reference proves](#what-a-reference-proves)
- [Number parameter construction](#number-parameter-construction)
- [PowerTable identity and source boundaries](#powertable-identity-and-source-boundaries)

## Read the complete current configuration

1. Export the current Plan using the bundled `api export` and finish its operation.
   Decode the returned parts. If the user edits the reference during inspection,
   export again after that change; retain the captures separately.
2. Resolve pages and visuals from the decoded parts. Use actual visual IDs, not
   membership/association IDs. An embedded Planning visual retains its real
   owner's identity and inputs.
3. Read bookmarks from the exported parts. Live bookmark reads and writes have no
   public route in this package, and exported snapshots are a different
   representation from live ones.
4. The export carries Home visibility. Role-specific Home metadata and content have
   no public read route here. Empty exported `homeLayout.roles` and an omitted
   `show` property do not prove Home is absent or disabled; report role content as
   not inspected unless the user supplies it.
5. For PowerTable, read the exported source, column configuration and source
   settings parts. Read the SQL schema from the database definition (the SQL
   definition discovery guide); a schema readback through the PowerTable service
   has no public route here. None of this certifies source connection health or
   row saves.

`python scripts/plan.py inspect-reference-views --input inspection.json --out audit.json`
accepts `{"raw": <decoded parts>, "home_roles": <optional role metadata>,
"home_contents": {"<role ID>": <optional role content response>}}`.
It resolves owner/embed membership, bookmark page/visual references, navigator
kinds, current page parameters, exported PowerTable configuration and any Home
content the user supplies. It flags parameters missing from bookmark snapshots. It
does not apply a bookmark, open a dashboard, refresh queries or write any business
data.

## What a reference proves

A reference profile records hashes and checks; it never bundles a customer's
whole report or becomes a prerequisite for future builds.

- Exported bookmarks carry `cloudMeta.bookmarkMeta` and `bookmarkVisualMeta`, with
  record-GUID page and visual references. Live references use runtime IDs; never
  mix the two domains.
- Planning `manage_measures` snapshot entries retain IDs, but the exporter converts
  them to labels, order and visibility. Never treat that label-only fragment as an
  ID-bearing snapshot or guess IDs by position.
  `reference_views.audit_native_capture(capture, current_page)` detects this error.
- A bookmark keeps its page as `activePageId`, with `includeCurrentPage`,
  `includeData` and `includeDisplay`. Its snapshots cover only the visuals present
  when it was captured: a navigator added later is not in them. Names and order are
  independent of array order.
- A page parameter added after a bookmark was captured is absent from that
  bookmark's `entityLevelVariables`. Page parameter storage does not prove that
  bookmarks capture or restore it. Capture the intended context explicitly; do not
  claim every current control is saved.
- Generating new restorable pivot snapshots (full detail, region or specialist
  views) and validating apply/restore have no implemented contract here. Keep an
  agreed deferral until that requirement is implemented; navigator tabs are not a
  substitute.

## Number parameter construction

`python scripts/plan.py construct-native number-parameter --input number.json --out bundle.json`
uses `runtime.page_parameters.number_parameter`:

```json
{"label":"Planning assumption","technical_name":"planning_assumption","value":4}
```

The output contains `entityVariable`, `visualGlobalVariable` and
`calculatedVariable`, all with one new `CALC_VARIABLE_...` ID. The page variable
belongs in `sheet.json.properties.entityLevelVariables`; the corresponding
selected Planning owner mirrors belong in `visualState.globalVariables` and
`visualState.calculatedVariables[id]`. These are separate stores; don't replace
unrelated parameters or duplicate the input visual. Resolve the consumers and
page scope intentionally, especially when one Planning owner is embedded on more
than one dashboard. A parameter creates neither an input permission nor a formula
dependency automatically. Add the records to a fresh export, publish with
`api update`, then export again and verify the three stores. `allow_decimal` and
`visible` are optional booleans; the supported profile is an ordinary number
input-box with no percentage display or slider. Dates keep their separate existing
constructor. The supplied value is literal; 4 remains 4. Do not invent a `/100`
dependency unless the requested formula uses whole percentage points.

## PowerTable identity and source boundaries

An existing-table PowerTable uses creation mode 2, Fabric SQL artifact type
`SQLDbNative` and an authenticated FabricSql connection. Identity primary keys stay
noneditable and lookup columns preserve their keys. Saved row add, update and
delete settings are configuration, not verification of a successful SQL row write.

Portable `source.json.source.recordGuid`, native visual `dataSourceId`, visual ID,
and page membership ID are different identities. Preserve runtime source IDs as
opaque strings, including nonnumeric compact identifiers. Resolve new source IDs
from the current application; don't reuse the reference's source. Discover the
actual target table schema/keys and configure through the bundled PowerTable
constructors. Don't import the reference's other table, rows, database, lookups or
permission settings as an automatic replacement.

Treat schema reads, source registration, connection resolution and physical
writeback as separate results: one can succeed while another fails, and reusing a
working connection ID does not by itself fix a source-creation error. Don't request
an unrelated SQL token, change database schema, recreate the Plan, or replay the
same failed mutation merely because one reader failed. Preserve the current
artifact and the precise gap.

All application defaults still apply: Arial, enabled Home, a visible Page
Navigator with complete padding on every dashboard, hidden Planning owners,
shared embeds, complete inputs/formulas/CF imports, correct OneLake query identity,
and optional initial InfoBridge refresh. The reference's own colors/fonts and
visible source sheets do not override those requested application defaults.
