# Accessibility

<!-- Design topic for the `fabric-plan-skill` skill. -->

## Checklist

- [ ] Text contrast ≥ 4.5:1 (large text ≥ 3:1); chart marks ≥ 3:1 against background.
- [ ] Meaning never by colour alone: ▲/▼, signs, labels, patterns, or icons accompany colour.
- [ ] Red/green pairs also differ in lightness; prefer blue/orange for categorical pairs.
- [ ] Every visual has a plain-language title; KPI cards name the comparison.
- [ ] Every chart has a subtitle or tooltip describing what it shows.
- [ ] Font size ≥ 9 pt everywhere; ≥ 10 pt for Matrix body.
- [ ] Logical reading order: header → filters → KPIs → main → supporting
      (also set layer order so keyboard focus follows it).
- [ ] Slicers have visible titles and support search for long lists.
- [ ] Super Filter keyboard accessibility enabled (`displaySettings`, `SF-DISP-01`).
- [ ] Matrix: header rows pinned, totals labelled, abbreviations explained.
- [ ] Right-to-left support considered for RTL locales (Matrix and Super Filter settings).
- [ ] No flashing animation; play axis (if used) can be paused.

## Fabric Plan specifics

- Matrix keyboard shortcuts and accessibility shortcut keys exist
  (Inforiver docs: accessibility-shortcut-keys).
- Super Filter has a keyboard accessibility option under display settings.
- Notes and annotations can carry explanations for screen-reader users when
  titles are not enough (`MX-NOTE-01`).

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- [ ] Palettes stay distinguishable under colour-vision deficiency: prefer
      Okabe-Ito, Set2, Blues, Viridis or Cividis; take care with YlOrRd
      (deutan), PiYG (protan) and Tableau 10 beyond eight colours
      (palette reference).
- [ ] Contrast is checked against the actual native fill, image or emphasized
      card behind the text, not only the intended background.
- [ ] Bright semantic colours on white (for example a yellow-green positive)
      are paired with signs or labels and tested for small marks.
- [ ] Text is never shrunk below the minimum, and zoom is never reduced, to
      make content fit; reflow or split instead.
- [ ] Where the audience reads red as gain (some East Asian financial
      contexts), semantic colours are confirmed with the user.
