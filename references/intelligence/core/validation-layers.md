<!-- Core reference for the `fabric-plan-skill` skill. Used by authoring and management (and the discovery hand-off) to state completion claims layer by layer. Merged from a companion Intelligence authoring library. -->

# Validation layers and completion claims

Merged from the companion Intelligence authoring library. Additive only:
mode guides, the other core references and feature-file `encoding` values take
precedence. Tags: [saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

## Contents

- [Claim layers](#claim-layers)
- [What each evidence class does not establish](#what-each-evidence-class-does-not-establish)
- [Before submission](#before-submission)
- [After an authorized write](#after-an-authorized-write)
- [Persistence completeness](#persistence-completeness)
- [Scope of testing](#scope-of-testing)
- [Additional details](#additional-details)

## Claim layers

Each layer is a separate claim. Passing one never implies the next.

| Layer | Required evidence | In this release |
|---|---|---|
| Local static audit | `plan_def.py validate --registry` plus the checks under [Before submission](#before-submission) | Always |
| API acceptance | Sanitized request status and operation identity | Every write |
| Terminal outcome | Completed poll and any required result, not just an accepted submission | Every write |
| Definition readback | Fresh export that matches the intended change | Every write |
| Native rendering | 100% zoom; readable controls, cards and axes; no clipping or scrollbars in authored content or opened controls; intended canvas and normal side-panel/viewing states | Only when observed or user-confirmed |
| Queries and interactions | Correct data; filter change and reset; drill and navigation; no unintended targets | When access permits |
| Business correctness | Reconciled leaf and totals; correct actual/reference, sign and time semantics (metric contract) | Business-critical values |
| Security | Separately authorized restricted-identity (RLS) and edit-permission checks | Separate test |
| Planning save and refresh | Input save, reopen and downstream refresh | `not_applicable`: module integration pending |

Record each check as `passed`, `failed`, `blocked`, `not_run` or
`not_applicable`, with its evidence location. A missing tool, identity or
approved expected value makes a check `blocked`, never `passed`.

- Do not issue an overall end-to-end pass while a required layer or metric
  case is blocked. State the narrower layer that passed, the unresolved case
  and the evidence needed.
- Saved-only donor evidence is not a rendering test. If authenticated UI or a
  required identity is unavailable, list each unverified check with its next
  action.

## What each evidence class does not establish

Complements the evidence classes. Never
replace an unperformed test with a stronger-sounding claim.

| Evidence | Does not establish |
|---|---|
| User requirement | Current implementation or product support |
| User-confirmed result | That other sheets, environments or later deployments work |
| Saved native configuration | A universal schema across product versions |
| Local static check | Importer behavior or rendering |
| API success | Correct data, visible measures or working interactions |
| Persisted readback | Runtime calculations and user workflows |
| Runtime/UI check | Full business reconciliation or RLS coverage |
| Hypothesis | A confirmed diagnosis |

## Before submission

- **Per-item capacity.** Before approving a sheet plan and before any create
  or update, count sheets and every registered visual (Text, Shape, Super
  Filter, navigation and hidden visuals included) against the current
  documented per-item limits in the Plan known-limitations article on
  Microsoft Learn. The companion library recorded 25 sheets and 50 visuals per
  item; the article revision updated 2026-11-11 lists no sheet or visual count
  limit, and a 214-owner Plan published successfully [confirmed]. Recheck the
  article before relying on any number [open].
  Reject an oversized new item or expansion and propose separately approved
  items. Never silently delete existing work to fit; if an existing baseline
  already exceeds a limit, obtain an explicit recovery scope. API acceptance
  does not prove that an oversized definition is supported.
- **Approved scope only.** Diff the package against the snapshot. Every change
  must map to an approved spec item or focused edit; an unapproved model,
  connection or page change blocks submission.
- **Round-trip packaging.** Unpack the packed payload into a scratch folder and
  run `plan_def.py diff` against `_build/def`. Compare part paths, counts and
  byte lengths, and hash untouched parts against the readback. Scan the
  payload for credentials separately from JSON validity: valid JSON can still
  contain secrets.
- **Period and title truth.** Period labels must name real period calculations
  over the same metric (period semantics).
  Recheck titles and subtitles after binding or filter edits, and under changed
  selections and no-data states [confirmed].
- **Resources.** A base64 image or background value can hold a resource
  locator rather than image bytes [saved]. Check that each referenced asset is
  available to the target item; export success does not prove asset retrieval
  or cross-report portability.
- **Notes that fetch values.** Validate attachment, presentation and each
  fetched item separately, then reconcile every fetched value with the
  sentence that describes it: a correctly resolved token can sit in prose that
  names a different metric [saved]. Static prose, dates and percentages must
  stay truthful when filters change. See chart notes
  and Matrix notes.
- **Layout.** Run the geometry checks and the optional layout-manifest audit in
  invariants. A static pass is one layer,
  not rendering proof.

## After an authorized write

Enumerate the fresh readback, not the submission. Return the target identity
and link, the operation outcome, package and readback locations, the exact
layers checked with their statuses, and the remaining gaps.

## Persistence completeness

- For multi-sheet creates and updates, enumerate every intended sheet and every
  registered visual in the readback, including headings, footers and other
  non-data visuals. Require the sheet part, each visual's properties envelope,
  visible layer state and complete reference closure. A sheet-name or
  chart-count check is insufficient.
- In the companion work, the readback of a large multi-sheet create lacked
  several submitted sheets and held text visuals without properties parts,
  although the local package contained them [saved]. Local package validation
  never establishes persistence.
- Report missing sheets or parts and changed content separately. Ask whether
  the user deleted something before restoring it, and keep the original
  operation receipt if its status URL expires.
- Keep the root inventory (`sheets[]`, `workloadItemEntityVisuals`) separate
  from the parts actually available. Record the literal type of an entry
  without parts (for example a `BI_REPORTING` sheet or an unknown visual type)
  instead of relabeling it [saved]. Opening Explore Model in the editor
  produced exactly such an entry (`CV-EXPL-01`) [saved].
- A visual folder that holds only `writeback.json` does not establish fields,
  geometry, styling or template [saved]; never reconstruct a donor from it.
- A sheet can export without canvas settings, as seen on an empty hidden sheet
  [saved]. Record the missing geometry instead of supplying a default.

## Scope of testing

Run checks proportionate to the change. A cosmetic resize does not need every
business test; a new filter-context or calculation design needs behavioral
validation. Stop once the required layers pass and no unresolved concern
remains. Querying the same expression twice is a consistency check, not an
independent business validation.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### More evidence limits

| Evidence | Does not establish |
|---|---|
| Observed symptom (screenshot, error text or user report) | Its root cause; describe the failure without asserting one |
| Proposed pattern | Native configuration or runtime behavior; both still need checks |

### More checks before submission

- Visual-measure formulas resolve (`M_<id>` and captured `R_<id>` operands)
  and their dependencies contain no cycles.
- Placing additions on a new sheet creates no capacity headroom: the visual
  limit applies to the whole item, existing owners included.
