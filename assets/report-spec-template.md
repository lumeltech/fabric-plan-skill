# Report spec — <Plan / report name>

<!-- Template for `_brief/report-spec.md` (fabric-plan-intelligence discovery mode). The YAML block at the end is authoritative. -->

## 1. Report identity
- Plan name:
- New plan or existing plan (name/ID):
- Audience:
- Primary purpose:
- Delivery: local definition only | new plan in workspace | add sheets to existing plan | decide later

## 2. Semantic model binding
- Module: Intelligence
- Source scope: semantic-model-only (cross-module integration pending)
- Entry mode: Live Connected Model | Existing Plan
- Workspace: <name> (<id>)
- Semantic model: <name> (<id>)
- Binding form: legacy (copied from existing plan) | portable

## 3. Field registry
- Path: `_brief/field-registry.md`
- Captured (UTC):
- Metadata completeness and table/column/measure description coverage:
- Description-derived business definitions, grain, units and exclusions:
- Description/expression conflicts, missing metadata and explicit inferences:

## 4. User decisions and constraints
- Scope / sheet count:
- Interactivity:
- Design direction:
- IBCS: no | yes (strict | flexible; IBCS report template or explicit request)
- Publishing permission:
- Model-measure permission: none | ask-per-measure
- Data caveats:

## 5. Narrative
- Core story:
- Key questions answered:

## 6. Design identity
- Session profile ID/revision and resolved snapshot in Design Brief:
- Source: supplied design | design file (<path>) | session reuse | fresh session proposal
- Design choice rationale (user/session preference, not report-type assignment):
- Shared palette, typography, button/navigation style and page-role layouts:
- Help and Info controls (placements, actions, content, close/back or explicit opt-out):
- Tone:
- Signature:

## 7. Sheet plan
### Sheet 1 — <name>
- Chosen example, IBCS report template or Custom / layout name (not inferred from report type):
- Purpose:
- Visuals: (kind — fields — measures — feature IDs)
- Slicers and interactions:
- Super Filter position/regions, sizing, overflow and popup/collapse behavior:

## 8. Measures
- Built in Fabric Plan (visual measures, each with a business description):
- Model measures proposed (name — home table — DAX — description — why not in Fabric Plan), each needs its own approval:
- Gaps this skill will not fix:
- Cross-module measures requested but blocked pending integration:

## 9. Canonical design contract
```yaml
Design Brief:
  generated_by: fabric-plan-intelligence
  contract_version: 1
  # see references/intelligence/design/design-brief.md
```

## 10. Implementation notes
- Native template / sample to start from:
- Feature encodings still unverified (capture plan):
- Validation plan:
- Publishing boundary:
- Risks:
