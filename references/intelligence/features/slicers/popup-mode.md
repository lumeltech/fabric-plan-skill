---
id: SF-FEAT-05
name: Pop-up mode
area: slicers
category: Features
status: IS-Confirmed
encoding: verified
visual: Super Filter
sources:
---

# Pop-up mode

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Opens the slicer as a pop-up to save canvas space.

## When to use

- Only after the user has explicitly approved pop-up mode for the report
  [confirmed]. Ask first; choosing a popup/collapsible filter position in the
  design interview counts as approval. Without approval, use a dropdown facet
  that shows its own title (`SF-FACET-01`).
- Dense sheets, once approved.

## UI path

Display › Pop-up (min mode).

## Definition encoding

```text
Part: sheets/{sheetId}/visuals/{visualId}/properties.json
Pointer: /properties/visualState/minModeSettings =
  {enableMinModeFilter:true, popupHeight:<px>, popupWidth:<px>, centerAligned:true,
   actionElements:false, xPosition:0, yPosition:0}
displaySettings.displaydialogbox stayed false in the working pop-up; it is not the switch.
Evidence: native checkbox facet saved with the pop-up on; reused in a report build.
  Runtime: user-confirmed that the pop-ups opened fully where dropdown lists were
  cropped. A hierarchy-mode filter with the same group was published; its rendering
  awaits confirmation.
```

The collapsed launcher is a compact search box at the top of the frame and
shows no filter title or field label, so place a separate text label (native
reports do the same) and keep the frame shallow. In the native sample, search
and bulk paste coexist with the pop-up; saved filters inside a pop-up are not
captured.

## Constraints

- A user replaced unrequested pop-up page filters with dropdown facets
  (`facetViewType: "dropdown"`, `enableMinModeFilter: false`, own title shown)
  and asked to be asked before pop-up mode is used again [confirmed].
- A row of unlabeled launchers was rejected in review ("only a search box with
  no field labels"); label every launcher and mix it with inline controls.
- A launcher with an open-popup instruction is not the opened panel; it does
  not verify activation, size, modality or selection persistence.
- Record trigger/expanded placement in `super_filter_layout`. Capture and test
  open/close, keyboard focus, selected summary and clear/apply behavior;
  do not infer animation or a working drawer from the caption.

## Related features

- `SF-DISP-01`
- `SF-FEAT-02`
- `SF-FEAT-03`
- `SF-HIER-01`
