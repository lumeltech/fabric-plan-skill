---
id: MX-FMT-03
name: Images in cells (image URLs)
area: matrix
category: Formatting
status: IS-Confirmed
encoding: unverified
visual: Matrix
sources:
---

# Images in cells (image URLs)

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Renders image URLs from the model as images in cells. Used as a cell-level
field it shows an image beside each item's values; bound to the column
dimension it replaces column header text; bound to rows it uses images as the
row categories.

## When to use

- Product or flag images.
- Easier identification of items in long comparisons.
- Logo or flag headers across columns.

## UI path

No separate menu step: bind the model's image URL field to the Matrix rows,
columns or as a cell-level field; images render from the binding.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- Images render only when the model column's data category is Image URL.
- The semantic model is read-only here; ask its owner to set the data category
  instead of changing the model.
- Column-dimension images replace the header text and row-dimension images
  replace the category names.

## Related features

- None.
