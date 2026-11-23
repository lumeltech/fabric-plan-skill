---
id: SF-PLAY-01
name: Play axis
area: slicers
category: Animation
status: IS-Confirmed
encoding: observed
visual: Super Filter
sources:
---

# Play axis

<!-- Feature reference for the `fabric-plan-skill` skill. Loaded on demand from the SKILL.md reference index. -->

## What it does

Animates selection through members (e.g. months) with play/pause, loop, cumulative and multi-level selection.

## When to use

- Time-lapse stories.

## UI path

Filter type › Play axis.

## Definition encoding

```text
Path: sheets/{sheetId}/visuals/{visualId}/properties.json → properties.visualState.playAxisSettings (enablePlayAxis, autoPlay, loop, playInterval, cumulativeSelection)
Evidence: decoded native readback (REPORTING sheet, facet Super Filter, embedded Planning grid)
```

The settings group exists in a native export, but the values for this feature are not isolated. Copy the whole group from a working visual or run `core/native-samples.md` before writing it.

## Constraints

- Play buttons and member chips do not identify the animated dimension; a
  category axis may sit beside a time-based chart. Capture the animated
  dimension instead of assuming time.
- Screenshots do not capture playback. Test order, interval, pause/stop,
  restoration and target interactions. Loop/cumulative and multilevel
  behavior need separate capture despite user-confirmed availability.
- Keep autoplay user-controlled and respect reduced-motion needs.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

```text
Partial: /properties/visualState/playAxisSettings = {enablePlayAxis:true,
  playAxisType:"label" | "tabs", autoPlay:false, cumulativeSelection:false,
  loop:false, displayStopButton:true, playInterval:<number>} [saved]
Binding: every enabled owner bound its play-axis category field [saved]
```

- The `playInterval` unit and playback timing are untested [open].
- Rendering of `"tabs"` versus `"label"` is unconfirmed [open].

## Related features

- `CV-NAV-01`
