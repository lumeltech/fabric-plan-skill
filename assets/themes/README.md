# Theme assets

Optional, user-supplied theme presets for Intelligence Sheets. Nothing here is
a default: use a preset only when the user or the session design selects it.
A preset never overrides the session theme, supplied designs,
report-inspiration guidance or IBCS opt-in.

- [Default 1 — Fabric Quiet](default-1-fabric-quiet.user-theme.json): the
  exact global theme preset (label `Default 1`) that a user of the companion
  Intelligence authoring library supplied as the reference for later updates,
  copied unchanged. A saved global theme registration matched its supplied
  fields, but its native rendering, accessibility and inheritance by every
  visual were not tested.
  - It is a theme-preset object, not a Plan definition part and not a direct
    replacement for the Plan properties theme. Native registration needs a
    same-build native readback; see the
    [themes feature](../../references/intelligence/features/canvas/themes.md)
    and the [native-sample workflow](../../references/intelligence/core/native-samples.md).
  - Design notes, contrast cautions and how it fits the session design:
    [design families](../../references/intelligence/design/design-families.md#fabric-quiet-preset-default-1).

Keep presets free of names, tenant identifiers, credentials and business data.
Record each preset's provenance and validation status here.
