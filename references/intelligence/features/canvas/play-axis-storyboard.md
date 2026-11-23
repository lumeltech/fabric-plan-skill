---
id: CV-NAV-01
name: Storyboard play axis
area: canvas
category: Elements
status: IS-Confirmed
encoding: unverified
visual: Canvas
sources:
---

# Storyboard play axis

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Animates the whole board through a dimension. A play axis navigator applies
each member of its dimension as a filter in turn, so charts, cards and tables
update automatically. Options: axis type (tabs, progress bar, ticks or
labels), sort order, loop, autoplay, play interval in seconds, play-button
style and position (left or right) and a counter of viewed and remaining members.

## When to use

- Time-lapse dashboards.
- Hands-free walk-throughs of regions, products or periods on a shared screen.
- Continuously cycling displays (loop with autoplay).

## UI path

Navigation › Play axis. Insert the Play Axis navigator on the canvas, assign
the driving dimension in its data (pivot) configuration, style it (border,
margin, shadow, background), then set the play options.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.(capture sample)
Evidence: none yet
```

Not yet captured. Run `core/native-samples.md` before writing this feature into a definition.

## Constraints

- The driving dimension must come from the bound semantic model; each step
  filters the board's charts, cards and tables to one member.
- Autoplay starts playback when the sheet loads and Loop repeats it without
  end; avoid both where readers need a stable view.
- Sort sets the play order (ascending, descending or native); check that
  period members play chronologically.
- Set the play interval long enough for each step to render and be read.

## Related features

- `SF-PLAY-01`
