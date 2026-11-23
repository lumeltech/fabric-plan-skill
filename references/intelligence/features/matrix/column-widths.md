---
id: MX-COLW-01
name: Column widths
area: matrix
category: Layout and hierarchies
status: IS-Confirmed
encoding: observed
visual: Matrix
sources:
---

# Column widths

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Sets fixed or auto-fit column widths. Drag a column header edge, or use Auto
fit: Fit to header, Fit to content, Best fit (adjusts rows and columns
together) or Manual column width in pixels. Lock size protects the chosen
widths; Auto wrap column wraps header and cell text.

## When to use

- Fit a wide Matrix into its region.
- Show long row labels in full (Fit to content or Auto wrap column).
- Give statement columns exact, consistent pixel widths.
- Lock an approved layout against accidental resizing.

## UI path

Matrix toolbar: Home › Auto fit › Fit to header, Fit to content, Best fit or
Manual column width; the same drop-down holds the Lock size and Auto wrap
column toggles. Or drag the column header edge.

## Definition encoding

```text
Pointer: /properties/visualState/columnMeta/row_label/width (row-header column, px)
Pointer: /properties/visualState/columnMeta/<rowDimensionId>/width (each level column in Table layout, px)
Pointer: /properties/visualState/measureAttributes/<measureId>/width (each measure column, px)
Evidence: user-finalized saved reporting matrices (INFORIVER/10) [saved];
          not round-tripped by this skill
```

Widths are integer pixels keyed by the owner's own `rowDimensions[].id` and
measure ids, which the engine can re-key on an edit-mode load; read them from
the newest readback. Prefer setting widths in the UI or copying a complete
owner; follow `core/native-samples.md` before writing them.

## Constraints

- Auto fit options do not resize columns that contain in-cell charts.
- Best fit also changes the row height to optimise space.
- While Lock size is on, the four auto-fit options are disabled; turn it off
  before resizing again.
- Manual column width takes pixel values for the selected columns.
- Auto wrap applies to row, column and measure headers and to row, column and
  cell text.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- Saved Table and Matrix owners carry a `columnMeta` object, and saved
  matrices also a layout-sizes group (`layoutSizes`, see `MX-LAY-01`)
  [saved]. User-finalized matrices stored widths as pixels in `columnMeta`
  and `measureAttributes` (pointers above) [saved].
- Size columns so the row-label, level and measure widths sum to about the
  visual's inner width: no unused band on the right and no horizontal scroll
  at normal zoom [confirmed]. Re-check after adding or hiding measures.

## Related features

- `MX-PIN-01`
