# Anti-patterns

<!-- Design topic for the `fabric-plan-skill` skill. -->

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Wall of KPI cards (8+) | No hierarchy; nothing stands out | 3–6 cards, each with a comparison |
| KPI card repeating the adjacent chart total | Redundant | Replace with a variance, rank, or threshold |
| Pie with 9 slices | Angles unreadable | Sorted bar or Top N + Others |
| Unsorted bars | Reader must scan | Sort by value (or natural order for time) |
| Dual axis without labels | Misleading scale | Multi-measure chart with labelled axes, or small multiples |
| Tile slicer on 300 members | Unusable | Dropdown with search and its own title / hierarchy slicer |
| Every filter in the same style | Repetitive; rejected in review | Mix tile, toggle, checkbox, tree, date and dropdown controls by cardinality |
| Pop-up mode used without asking | The user rejected unrequested pop-ups | Ask first; otherwise a titled dropdown facet |
| Unlabelled pop-up launchers | A bare search box hides the field | Text label beside each approved launcher |
| Dropdown in a short filter band | Open list cropped | Enough height for the open list |
| Day-level calendar on an executive sheet | Too fine | Month range / presets |
| Matrix with 40 columns visible | Horizontal scroll fatigue | Measures in rows, column hierarchy collapsed, pagination |
| Summed ratios in totals | Wrong numbers | Ratio aggregation settings / calculated totals |
| CF on every column | Noise | CF only on the decision column |
| Raw field names (`Sum of amt_lc`) | Unreadable | Rename headers, axes, legends |
| Slicer overlapping a chart | Clipped controls | Reserved filter band |
| Embedded Planning grid squeezed into a corner | Unusable input | Largest region, bounded default scope |
| Unbounded default scope on a large grid | Cell limit / slow load | Default one region and one year |
| IBCS colours used without IBCS request | Confuses readers expecting brand | Use design-system colours unless IBCS requested |
| Red/green only | Colour-blind readers miss it | Add ▲/▼ or signed labels |
| Inventing JSON for a feature from its UI label | Broken definition | Native sample workflow |

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Choosing visuals from field names before studying the model | Wrong grain, sign or scenario | Read expressions, grain, units, signs, date and scenario context first |
| Text box repeating a visual's native title | Two titles compete; looks unfinished | Title on the visual; standalone text only for the header, group labels or distinct callouts (visual craft) |
| Visual boundaries lost against the canvas | Grouping and focus collapse | Separate with the session's container style: fill, hairline, elevation or spacing |
| Generic or copied caption, or a period word the calculation does not support | Misstates the content | Content-bound titles |
| Single-value KPI card in the hero slot | Wastes the lead region | Lead chart or Matrix in the hero |
| Callout repeating a value already on the sheet | Noise | Remove it or state something new |
| Copying a historical canvas or donor styling as a new standard | Drifts from the session design | Apply the session layout; record approved exceptions |
| Treating notes, annotations, markers, shapes and text as one component | Wrong owner; context lost | Choose the native owner first |
| Static text standing in for a selector | Filters nothing | Native Super Filter with binding, registration and selection |

**Optional (companion default):** the companion also treats a visual without
its own container fill, border and radius, or a borderless KPI card, as a
defect (companion framing); this
applies only when the user or session design selects it and never overrides
the session theme, supplied designs, report-inspiration guidance or IBCS
opt-in.
