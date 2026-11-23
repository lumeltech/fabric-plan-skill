## Contents

- [Critical notes](#critical-notes)
- [Companion references](#companion-references)
- [Tool stack and authentication](#tool-stack-and-authentication)
- [Resolve a plan by name](#resolve-a-plan-by-name)
- [Operations](#operations)
  - [List plans](#list-plans)
  - [Get plan](#get-plan)
  - [Get definition](#get-definition)
  - [Create plan](#create-plan)
  - [Update definition](#update-definition)
  - [Update properties](#update-properties)
  - [Delete plan](#delete-plan)
- [Additional details](#additional-details)

<!-- Mode reference for the `fabric-plan-skill` skill. Loaded on demand from `SKILL.md` when the request matches the `management` mode. Structure adapted from microsoft/skills-for-fabric powerbi-report-cli (MIT). -->

# fabric-plan-skill management mode — Plan item transport and management

> **Required continuation.** After this file, open
> [management-part-02.md](management-part-02.md) (workflows, rebind,
> readback verification, troubleshooting).

Management moves Plan definitions to and from Fabric and manages the Plan
item in a workspace. The product runs on the web; there is no local project
format. It does not author definition content.

## Critical notes

- **Never create, overwrite, or delete without explicit user permission in this
  conversation.** Confirm the workspace, plan name, and operation first.
- `updateDefinition` is documented to replace **all** parts; always send the
  full set (packed from the full decoded folder). Observed service behavior
  differs for omissions: a visual left out of the payload, including its
  `definition.json` registration, was **not deleted**, and omitted
  server-managed parts (per-visual `writeback.json`/`dataInput.json`, cube,
  InfoBridge, `datasetRelations`) were restored. Never rely on omission to
  remove a visual; see [removing visuals](core/invariants.md#removing-visuals).
- **Never re-POST a create after a 202 or timeout.** List by name first.
- Resolve every ID by list + JMESPath; never guess.
- One workspace per operation unless the user names more.
- Download/readback before every definition update of an existing plan, so unrelated
  parts (Planning sheets, InfoBridge, cube) are preserved.
- Save untouched metadata and the rollback envelope outside the decoded folder
  being packed. Keep the target closed or in Reading mode during definition
  changes; reconcile any remote changes since the snapshot before writing.
- Skip writes with no intended delta. After an ambiguous write, inspect the
  known operation and live state instead of resubmitting.
- **Data pane field check before report-definition creation or update**: refresh the
  registry from the live model and run `plan_def.py validate --registry …`.
  A missing field blocks the call. For metadata-only changes, fetch current
  metadata and validate only the requested fields; do not export/rewrite the
  definition. An explicitly empty creation has no report bindings to validate.
- Follow [module boundaries](core/module-boundaries.md). Current validation
  covers model-backed reporting, not blended source provenance. If mixed-source
  bindings prevent validation, block the update; never drop foreign parts or
  disable checks to publish. Shared Plan settings must not restyle other modules.

## Companion references

- `core/rest-and-lro.md` — `az rest`, LRO polling, paging, run-state record.
- `core/definition-structure.md` — parts and envelope.
- [Upstream contracts and provenance](core/upstream-references.md).
- `scripts/plan_def.py` — unpack / pack / validate.

## Tool stack and authentication

```bash
az login
az account show -o table
```

All Fabric calls: `az rest --resource "https://api.fabric.microsoft.com"`
with `--headers "x-ms-fabric-skill=fabric-planning-api"`, including polls,
pagination and result requests. Permissions/scopes are listed in
[REST and LRO patterns](core/rest-and-lro.md#public-operations-and-permissions).

## Resolve a plan by name

```bash
az rest --method get --resource "https://api.fabric.microsoft.com" \
  --headers "x-ms-fabric-skill=fabric-planning-api" \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/plans" \
  --query "value[?displayName=='$PLAN_NAME'].{id:id,name:displayName}" -o json
```

Collect exact matches across every page before setting `PLAN_ID`. Stop on
ambiguity; do not silently select the first item or reuse an existing name.
If the type-specific route is unavailable in the tenant, use the generic one:
`/v1/workspaces/$WS_ID/items?type=Plan`. Follow `continuationToken`.

## Operations

For generic item creation, use `/items` with `type: "Plan"`; generic listing
uses `/items?type=Plan`. Item-specific metadata/definition routes use
`/items/{itemId}`. Do not blindly substitute paths or omit the type on create.

### List plans

```bash
az rest --method get --resource "https://api.fabric.microsoft.com" \
  --headers "x-ms-fabric-skill=fabric-planning-api" \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/plans" \
  --query "value[].{name:displayName, id:id}" -o table
```

### Get plan

```bash
az rest --method get --resource "https://api.fabric.microsoft.com" \
  --headers "x-ms-fabric-skill=fabric-planning-api" \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/plans/$PLAN_ID"
```

### Get definition

LRO. Follow `core/rest-and-lro.md`, save the result, then unpack:

```bash
az rest --method post --resource "https://api.fabric.microsoft.com" \
  --headers "x-ms-fabric-skill=fabric-planning-api" \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/plans/$PLAN_ID/getDefinition" \
  --output-file _build/getdef-response.json
# Capture response status/headers safely; handle 200 or poll 202 per core/rest-and-lro.md.
# poll → GET /v1/operations/$OP_ID/result --output-file _build/source.json
python -I scripts/plan_def.py unpack _build/source.json _build/def
python -I scripts/plan_def.py unpack _build/source.json _build/readback   # untouched baseline
python -I scripts/plan_def.py fields _build/def --registry _build/info-columns.json --registry _build/info-measures.json
```

Report any field the existing plan uses that the model no longer has.

`format=PlanV1` is an optional documented query parameter, not a requirement.
If export fails
for a plan that exists, report it; export failures were observed even when
create succeeded.

### Create plan

Body: `{ "displayName", "description", "definition": { "parts": [...] } }`.

```bash
python -I scripts/plan_def.py pack _build/def _build/payload.json \
  --display-name "$PLAN_NAME" --description "$DESC"
az rest --method post --resource "https://api.fabric.microsoft.com" \
  --headers "x-ms-fabric-skill=fabric-planning-api" \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/plans" \
  --body @_build/payload.json --output-file _build/create-response.json
# poll until Succeeded; result contains the new item id
```

Before create: list by `displayName` (`ItemDisplayNameAlreadyInUse` otherwise).
After create: record the plan ID; do not retry the POST.
Prefer a complete definition in the initial create request for report building.
An explicitly requested empty Plan may omit the definition; do not use empty
creation as a shortcut around the report approval/validation workflow.

### Update definition

```bash
python -I scripts/plan_def.py validate _build/def \
  --registry _build/info-columns.json --registry _build/info-measures.json \
  --baseline _build/readback   # live model, this task; readback of this plan
python -I scripts/plan_def.py pack _build/def _build/payload.json
az rest --method post --resource "https://api.fabric.microsoft.com" \
  --headers "x-ms-fabric-skill=fabric-planning-api" \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/plans/$PLAN_ID/updateDefinition" \
  --body @_build/payload.json --output-file _build/update-response.json
# poll until Succeeded
```

- `pack` without `--display-name` produces `{ "definition": { "parts": [...] } }`.
- When `.platform` metadata must be applied, review the entire metadata and
  obtain explicit intent, then use the **Core Items** endpoint
  `/workspaces/$WS_ID/items/$PLAN_ID/updateDefinition?updateMetadata=true`
  with the same full envelope. Do not append that parameter to the Plan route.

### Update properties

Rename or change the description without touching the definition:

```bash
az rest --method patch --resource "https://api.fabric.microsoft.com" \
  --headers "x-ms-fabric-skill=fabric-planning-api" \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/plans/$PLAN_ID" \
  --body '{"displayName":"<new name>","description":"<text>"}'
```

### Delete plan

Only after the user confirms the exact plan name and workspace in this
conversation.

```bash
az rest --method delete --resource "https://api.fabric.microsoft.com" \
  --headers "x-ms-fabric-skill=fabric-planning-api" \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WS_ID/plans/$PLAN_ID"
```

Use the documented DELETE operation; do not invent hard-delete parameters
or promise recovery behavior not established by the public contract.
Verify absence by listing the resolved workspace; an access failure does not
prove that deletion succeeded.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Export inventory.** Before editing, record every part's path, payload
  type, decoded byte length and hash, and keep the raw decoded JSON; do not
  assume a fixed part subset. Exports can contain business commentary and
  identifiers, so keep raw evidence local.
- **Write evidence set.** For each write keep the raw decoded snapshot, the
  packed request and the validation report together, saved before packing.
- **Inspection copies are not payloads.** Recursively expanded JSON strings
  are for analysis only; pack from decoded parts with native string/object
  boundaries intact.
- **Root keys.** Preserve root keys you do not use, such as
  `appDBconnection` where present [saved].
- **Capacity gate.** Before create or update, apply the per-item sheet and
  visual count in validation layers,
  including non-chart visuals.
- **Item existence.** A successful `GET` of the plan item does not prove that
  every sheet loads.
- **Donor identities.** Report IDs, workspace IDs and permissions found in
  evidence or earlier sessions are not current deployment targets; resolve
  targets again.
- **Parsing and hosts.** See REST and LRO
  for response parsing, redirect hosts and resultless operations.
