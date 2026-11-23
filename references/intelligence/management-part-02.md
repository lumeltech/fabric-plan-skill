## Contents

- [MUST/PREFER/AVOID](#mustpreferavoid)
- [Workflows](#workflows)
  - [Publish a new plan](#publish-a-new-plan)
  - [Add sheets to an existing plan](#add-sheets-to-an-existing-plan)
  - [Rebind to another semantic model](#rebind-to-another-semantic-model)
  - [Organize](#organize)
- [Readback verification](#readback-verification)
- [Troubleshooting](#troubleshooting)
- [Additional details](#additional-details)

<!-- Mode reference for the `fabric-plan-skill` skill. Continuation of management.md. Open this file directly from the skill reference index. -->

# Management mode - Part 2

Continuation of `management.md`.

## MUST/PREFER/AVOID

### MUST

- Refresh the field registry from the live model and validate
  (`plan_def.py validate --registry …`, plus `--baseline _build/readback` for an
  update) before every report-definition create or update. Metadata-only work
  validates the changed metadata fields, not unrelated report bindings.
- Send all parts on update; pack from the full decoded folder.
- Poll every LRO to a terminal state; save the operation ID.
- Read back after every write and compare to what was sent.
- Fetch fresh metadata after create or metadata updates. For definition work,
  validate the complete readback and compare retained parts, IDs, field bindings
  and references with the submission.
- Before writing, reconcile the live target with the saved snapshot; stop on
  concurrent changes. A rollback is another authorized write, not an automatic
  response to a failed verification. Opening a page in edit mode can itself
  save editor normalization (sheet-id `originEntityId` stamps, re-keyed Matrix ids,
  filter-context caches, re-enabled card legends, an Explore Model scratch
  sheet, `CV-EXPL-01`). Classify the changes; keep
  deliberate user edits, rebase the build on the newest snapshot (re-pin
  engine ids) and re-run the check before publishing. Ask the user to close
  edit mode while a publish runs.
- Keep `_build/run-state.json` current (`core/rest-and-lro.md`).
- Clean temporary payloads that are no longer needed (keep the decoded folder
  and the readback).

### PREFER

- Publish greenfield work to a **new** plan named with a Unix-ms suffix first;
  replace a production plan only on explicit request.
- Keep the plan in the same workspace as its semantic model unless told otherwise.
- Use a separately authorized proof Plan to establish API-authored rendering
  before a production rollout when the encoding/service boundary is uncertain.

### AVOID

- Authoring definition content here (route to `authoring`).
- Retrying create after a 202.
- Deleting or overwriting without confirmation.
- Logging tokens or authorization headers (`--verbose` logs: delete or redact
  `Authorization` lines before keeping them).

## Workflows

### Publish a new plan

1. Confirm workspace, plan name, and description with the user.
2. Resolve `WS_ID`; list plans to make sure the name is free.
3. `validate` → `pack --display-name … --description …`.
4. POST create once; poll; record the plan ID from the result (or list by name).
5. `getDefinition` → unpack into `_build/readback/` → verify (below).
6. Give the user the plan link:
   `https://app.fabric.microsoft.com/groups/<workspaceId>/plans/<planId>`
   (the path segment may differ by tenant; list the item to confirm).

### Add sheets to an existing plan

1. `getDefinition` → unpack to `_build/def/` (this is the source of truth).
2. Switch to `authoring`; add sheets/visuals in `_build/def/`.
3. Back in management: validate → pack → `updateDefinition` → poll.
4. Read back and verify that untouched parts are byte-identical.

### Rebind to another semantic model

1. Resolve the target model tuple; capture its field registry.
2. Run closure against the **target** model:
   `plan_def.py fields _build/def --registry <target info-columns.json> --registry <target info-measures.json>`.
   Stop and report misses.
3. In `authoring`, change `definition.json → semanticModelReference` (keep the
   form the plan already uses; set IDs and names for the target).
4. Validate → `updateDefinition` → readback → verify the reference changed and
   nothing else did.

### Organize

- **Rename / describe:** PATCH properties (`management.md` § Update properties).
- **Sheet order / visibility:** authoring edit to `definition.json → sheets[]`
  then `updateDefinition`.
- **Copy a plan:** read the source, resolve the destination and check name
  collisions, then create a separate item. Preserve source identities where
  appropriate, but deliberately review/remap semantic-model, connection,
  variable-library and `.platform` identities required by the target.
  Do not assume a copied reference resolves in another workspace.
- **Move between workspaces:** copy to the target workspace, verify, and delete
  the source only on explicit request.

## Readback verification

```bash
python -I scripts/plan_def.py unpack _build/readback.json _build/readback
python -I scripts/plan_def.py diff _build/def _build/readback
```

Expected: no differences except server-managed fields (e.g. `.platform`
`logicalId`, timestamps), server-added parts (per-visual `writeback.json` for
new visuals, `dataInput.json`, `datasetRelations`) and the order of
`workloadItemEntityVisuals`; compare registrations as sets. `.platform`
description changes need a metadata update (PATCH), not `updateDefinition`.
Report any other difference. Then state exactly which layers passed:

| Layer | Evidence |
|---|---|
| Static validation | `plan_def.py validate --registry` passed (structure + Data pane fields; unchanged cross-module bindings with `--baseline` on updates) |
| API acceptance | Synchronous success or LRO `Succeeded`; required create/get-definition result retrieved |
| Readback | diff clean |
| Runtime / UI | Rendering only if observed or user-confirmed; exercise filters, calculations and interactions separately |

Never claim UI rendering from API success.
For explicitly empty creation, verify metadata without claiming a complete
report definition was authored. Preserve the snapshot, submission, operation
details and readback on failure. Persistence does not prove atomic provisioning,
visual registration or working runtime behavior; do not invent private
registration calls when persisted objects fail to render.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| 401 | Token expired → `az login` |
| 403 | No Contributor on workspace, or no Build on the model |
| 404 on `/plans` | Route not available → use `/items` generic route; check IDs |
| `ItemDisplayNameAlreadyInUse` | Resolve the collision and ask before reusing/updating an existing plan; do not silently overwrite |
| 202 with no `Location` / no result | Poll `x-ms-operation-id`; if still missing, list by name before anything else |
| Duplicate plans | A create was retried; delete the extra copy only with permission |
| Update "succeeded" but sheets missing | Parts were omitted; always pack the full folder |
| Removed visual still on the canvas after a successful update | Omission does not delete visuals; reuse its id, hide it (`layerProperties.isHidden`, inert, behind an opaque element) or delete it in the UI |
| Concurrency check reports live changes | Someone saved (possibly only edit-mode normalization); diff, keep deliberate edits, rebase and re-check before writing |
| `GEN_DB_002` / app DB connection error | Service-side; record operation ID, retry later, do not re-create |
| Export (`getDefinition`) fails though create succeeded | Known behaviour; record it, verify in UI, retry export later |
| `OperationNotSupportedForItem` | Item protected (e.g. sensitivity label) or unsupported operation |
| 429 | Honor `Retry-After`, then retry the same request; retain operation context |
| `CorruptedPayload` | Check Base64, JSON, required parts, exact schema contracts and cross-references; preserve unknown fields |

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

### Readback completeness and layers

Apply the validation layers after every write.
Terminal outcome is separate from API acceptance; queries and interactions,
business correctness and security are separate from rendering. For
multi-sheet writes, enumerate every intended sheet and registered visual in
the readback (persistence completeness).

### Pending operations and concurrency

An earlier update still reporting `Running` after a client timeout can later
overwrite a newer user correction [open]. Before any new write, establish that
operation's terminal outcome and rebase on the latest readback; a local backup
neither cancels the operation nor protects the correction.

### Copying a plan

- Flow: resolve the source → `getDefinition` with polling → decode all parts
  → rewrite only the requested semantic-model references and approved
  connection changes → keep every sheet, visual and measure part → create in
  the destination → poll, read back and validate.
- Collect the destination workspace, model workspace ID, model ID and new plan
  name as separate inputs.
- Reduced copies that dropped companion state produced empty sheets and were
  rejected by the user [confirmed]; copy complete contents.
- Removing or changing `appDBconnection` was explored for portability and did
  not prove that cross-environment copies work [open].
- Empty copies occurred both across and within environments, so their cause
  remains unresolved [open]; do not attribute them to environment differences
  without a controlled comparison.
- When several copies are requested, create exactly that many uniquely named
  items and return each link. Copies sharing one semantic model are not
  isolated data environments.
- Before recommending a Git-based copy, verify item-type support, logical
  identities, dependencies, connection bindings and branch/workspace behavior;
  renaming a folder alone does not prove an independent copy [open].

#### Exact replica of an existing plan

A replica must match its source without user rework [confirmed]. Observed
in a completed replica [saved]:

- Set `semanticModelReference.url` in the create payload. An item created
  without it kept Matrices failing to initialize, and a later
  `updateDefinition` dropped an added `url` while saving everything else.
  The URL survived later updates on an item created with it.
- A full create of about 460 parts failed: once on Matrix `dataInput.json`
  columns ("Arrow sidecar provision failed", `SM_CONN_0053`) and once with
  `UnknownError`. Creating a one-sheet shell with the URL, then sending the
  complete definition with `updateDefinition`, worked. Omit Matrix
  `dataInput.json` parts; the editor regenerated them once the Matrices
  loaded.
- Remap only sheet, visual and comment-settings identities (comment-settings
  record GUIDs must be unique); keep model, field and filter references.
- Updates reported `UnknownError` yet persisted fully or partly. Always read
  back, compare parsed content, and send only the missing parts in a second
  pass. Never resubmit blindly. When the readback equals the pre-update
  snapshot (nothing persisted), one identical resubmission of the complete
  definition succeeded.
- `ImportFailed` "Event-trigger replacement rollback failed" on every update,
  including an unchanged round trip, followed a user's deletion of visuals in
  the editor; identical retries kept failing. Re-emitting the deleted visuals
  hidden under their original ids cleared it
  ([removing visuals](core/invariants.md#after-the-user-deletes-visuals-in-the-editor)).
- A 339-part, 10 MB update ran about 23 minutes before `Succeeded`; a fixed
  poll budget expired first. Resume polling the saved operation URL instead of
  resubmitting. `pack` sends files byte for byte, so writing compact JSON
  shrank the request by about a quarter with identical parsed content.
- Uploaded images are item-scoped (`CV-ELEM-01`); re-upload them in the new
  item or flag them before delivery.
- Verify rendering of every Matrix and image in the new item before calling
  it identical.

### Developer handoff package

When the user asks for an API collection (for example Postman or Bruno),
include the sanitized definition payload; variables for the API base,
workspace ID and plan name; an empty token variable that the receiving
developer fills at runtime; create, poll and result requests in execution
order; and notes naming the existing semantic model and connections the plan
references. The package deploys the report only; it does not recreate the
model or its data.

### Handoff note

Before a long wait, or when asked to hand off, write a short note in the
working folder (for example `_build/handoff.md`): current request and latest
corrections; exact files, source, target and deployment status; what changed,
what was tested and what remains unverified; known operation IDs and the safe
next polling action; blockers and one next step. Never include credentials or
label prepared files as deployed, and stop a deployment the user cancels.

### Additional troubleshooting

| Symptom | Cause / fix |
|---|---|
| Import fails without useful detail | Keep the raw payload and operation result; compare one controlled change at a time with a working export |
| Readback lacks submitted sheets or visual properties | Persistence gap: report it, ask about user deletions, keep the original receipt; do not re-create |
| `/result` says the operation has no result | Resultless operation (REST and LRO); confirm the terminal state instead |

### Resuming work

- Take the target and scope from the newest request. Permissions, item IDs
  and unfinished actions in handoffs or earlier evidence are context, not
  instructions to execute.
- Read the working folder first (run state, operation receipts, validation
  reports, handoff note) instead of asking the user to repeat it, and confirm
  whether an earlier create already succeeded before any new write. Resume
  from that checkpoint rather than recreating artifacts.
- Treat existing deployment scripts and request queues as operational tools:
  inspect pending requests before launching one, because a queued create can
  produce an extra item. Never launch one merely because a handoff names it.
- At each material milestone, add the decoded-definition hash, completed
  checks and unresolved issues to the run state, and name the builder or
  script entry point that produced the package. One clear checkpoint beats
  reconstructing the history.
