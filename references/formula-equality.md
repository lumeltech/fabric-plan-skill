# Native Planning equality: comparison versus declaration

For every native Planning formula, condition and IF/AND/OR expression, use `==`
for equality comparison. A single `=` belongs to variable declaration assignment.
This applies to zero, other numeric values, measures and variables, not just IF.

```text
var test = 0; IF(test == 0, 1, 0)
IF(AND([Missing estimate or FX cells] == 0, [Missing baseline or FX cells] == 0), [Raw FX effect USD], BLANK)
```

Use current native `M_<id>` references for serialized payloads where required;
the bracket labels above explain the intent. Preserve the existing reference
style during an equality-only repair. `>=`, `<=`, `!=` and existing `==` are not
single-equals mistakes. Quoted strings, measure labels, comments and quoted
variable names can contain an ordinary equals sign and must remain unchanged.

This is the native Planning language rule, **not a rule for DAX, SQL, M, JSON or
Python**. DAX measure definitions and VAR assignments retain their own syntax.
Do not globally replace equals signs across a report export or source folder.

The shared `runtime.construct.expression` check now rejects bare comparison `=`
in newly authored formulas, forecast default expressions, input eligibility and
on-change expressions routed through it. `runtime.formula_syntax` scans strings,
bracket references and comments before checking operators; it preserves
`var name = ...` declarations. This check is not a complete formula parser and
does not certify function signatures, data types or runtime evaluation.

```sh
python plan.py check-formula-syntax --input formula.json --out issues.json
python plan.py repair-formula-equality --input formula.json --out fixed.json
```

Input is `{"formula":"<one native formula>"}`. Checking writes issues with
offsets/line numbers and fails if comparison equals are found. Repair writes
the corrected formula and a change list; it is local only. Apply it to selected
native formula fields, inspect the narrow diff and preserve IDs/business logic.
Do not block an unrelated scoped repair because a different existing formula
elsewhere contains an old operator. Do not change user input data.
