# Planning conditional formatting: new reports and missing rules

Use this guide for CF, Conditional Formatting, Manage Rules, missing rules,
favorable/unfavorable variance, colored numbers, arrows, and comment flags.
The supported constructor is for numeric single-condition Planning/Matrix rules.
This is not a general Charts or PowerTable formatting contract.

## New reports: put rules in the sheet spec

`build`, `build_application`, and `provision` consume each sheet's
`conditionalFormatting` list. `target` and `test` refer to that sheet's stable
measure **keys**, including hidden helper measures. The builder resolves native
IDs after constructing the measures. Do not use display labels or copy IDs from
a reference report. Add `planning.conditional-formatting` to requiredCapabilities
when using `provision`.

```json
{
  "conditionalFormatting": [
    {
      "id": "unfavorable-variance",
      "label": "Unfavorable variance",
      "target": "variance",
      "test": "variance",
      "operator": "<",
      "threshold": 0,
      "rowScope": "both",
      "columnScope": "both",
      "excludeRowTotal": false,
      "excludeColumnTotal": false,
      "appearance": {"textColor": "#A60000", "icon": "down", "iconColor": "#A60000"}
    }
  ]
}
```

Favorable direction is a business decision: higher revenue can be favorable,
while higher cost can be unfavorable. Blank values are excluded; equality uses
`==`. Choose `parent`, `child`, or `both` independently for rows and columns.
Do not put a background in `appearance` when existing input/forecast fills must
remain. An icon-only flag uses `icon` and `iconColor` without `textColor`.

## Existing reports: scoped authoring

Use `format-matrix` / `runtime.matrix_formatting.compile_formatting` against the
current owner's `visualState`. Here `target` and `test` are resolved native
measure IDs from `manage_measures`, kept as strings. The request has a stable
`id`, label, predicate, scopes, total exclusions and appearance as above.

The compiler updates only the requested rules. Unrelated user rules, opaque
extensions, business calculations, input settings and filters survive. A
selected old business-key rule is migrated to its stable native name, rather
than left behind as a duplicate. Repeated application is idempotent. Ambiguous
legacy/current duplicates and complex selected rules require explicit
reconciliation; this helper does not silently flatten them.

The compiler preserves unrelated entries in both `visualState.cfProps` and `visualState.jet_cfProps`. Use resolved IDs and deterministic rule identity; changing a rule count or adding an empty container does not establish that the intended rule exists. Local compilation does not test the UI.
