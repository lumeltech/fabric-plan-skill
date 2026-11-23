## Contents

- [Tool stack](#tool-stack)
- [Authentication](#authentication)
- [Base URLs](#base-urls)
- [Public operations and permissions](#public-operations-and-permissions)
- [Long-running operations](#long-running-operations)
- [Paging](#paging)
- [Run-state record](#run-state-record)
- [Additional details](#additional-details)

<!-- Core reference for the `fabric-plan-skill` skill. Shared by discovery (read calls) and management (all Plan item calls). -->

# REST and LRO patterns

## Tool stack

- `az` CLI (`az rest`) for every HTTP call. It handles tokens; nothing is
  stored on disk.
- `python -I scripts/plan_def.py` for pack/unpack/validate (standard library,
  no network).
- Bash examples are shown; on Windows PowerShell use the same `az rest`
  arguments and `ConvertFrom-Json`.

## Authentication

```bash
az login                     # interactive, once per session
az account show -o table     # confirm tenant
```

| Resource (`--resource`) | Used for |
|---|---|
| `https://api.fabric.microsoft.com` | Fabric workspaces, items, Plan definitions, operations |
| `https://analysis.windows.net/powerbi/api` | Power BI `executeQueries` on the semantic model |

Never print, save, or paste tokens. On 401, verify the token resource and
current identity; stop if reauthentication does not resolve it.
Every Fabric request, including pagination, polls and result retrieval, needs
`--headers "x-ms-fabric-skill=fabric-planning-api"`. Do not log authorization
headers when capturing HTTP diagnostics.

## Base URLs

- Fabric: `https://api.fabric.microsoft.com/v1`
- Plan items: `/workspaces/{workspaceId}/plans` (type-specific).
  Generic fallback: `/workspaces/{workspaceId}/items?type=Plan` and
  `/workspaces/{workspaceId}/items/{itemId}/getDefinition|updateDefinition`.
- Power BI: `https://api.powerbi.com/v1.0/myorg`

## Public operations and permissions

Sources: [Plan API](https://learn.microsoft.com/en-us/rest/api/fabric/plan/items),
[reviewed upstream API reference](https://github.com/tmdaidevs/fabric-planning-skill/blob/ce129e8bce4663f3f6f8fff154df3c253c3fc377/references/api-reference.md).
Paths below are relative to `/workspaces/{workspaceId}/plans`.

| Operation | Method/path | Permission and delegated scope |
|---|---|---|
| Create | `POST` collection | Contributor; `Item.ReadWrite.All` |
| List | `GET` collection | Viewer; `Workspace.Read.All` or `Workspace.ReadWrite.All` |
| Get | `GET /{planId}` | Read; `Item.Read.All` or `Item.ReadWrite.All` |
| Update metadata | `PATCH /{planId}` | Read/write; `Item.ReadWrite.All` |
| Delete | `DELETE /{planId}` | Write; `Item.ReadWrite.All`; explicit target confirmation |
| Get definition | `POST /{planId}/getDefinition` | Read/write; `Item.ReadWrite.All`; optional `format=PlanV1` |
| Update definition | `POST /{planId}/updateDefinition` | Read/write; `Item.ReadWrite.All`; complete definition |

All seven operations support user, service-principal and managed identities;
OAuth scopes do not replace workspace/item permission. Creation also needs
supported Fabric capacity. An encrypted sensitivity label can restrict definition
retrieval; do not remove the label as a workaround.

Use PATCH for ordinary name/description changes (description maximum 256
characters). Applying `.platform` metadata is a distinct, explicitly authorized
Core operation:
`POST /workspaces/{workspaceId}/items/{itemId}/updateDefinition?updateMetadata=true`.
Send the full definition envelope. Do not put `updateMetadata` on the
Plan-specific route. There is no separate public clone or blend-execution API.

## Long-running operations

`create`, `getDefinition`, and `updateDefinition` may return `202 Accepted`
with headers `Location`, `x-ms-operation-id`, and `Retry-After`. The location
may redirect to a regional Power BI host; follow it as given.

Rules:

1. Submit once and capture status plus `Location`, `x-ms-operation-id` and
   `Retry-After` without retaining credentials.
2. Wait for the initial `Retry-After`, then poll the exact returned `Location`.
   Honor subsequent `Retry-After` values without capping a server-requested
   wait. When absent, use bounded backoff (5 seconds, doubling to 30 seconds).
3. Keep authorization and telemetry on every poll. Stop on `Failed` or
   `Cancelled`; a polling budget exhausted after 60 attempts is unresolved,
   not success. Save the operation URL/ID to resume instead of resubmitting.
4. On `Succeeded`, create/get-definition require a result: follow the returned
   result location or use the operation URL plus `/result` if none is supplied.
   A failed result request is an error. Update-definition has no required
   result body; do not fetch a nonexistent result or suppress its 404.
5. Synchronous `200`/`201` skip polling. A 429 requires waiting for
   `Retry-After` before retrying the same request. Other polling failures must
   be reported, not converted into success or a restarted write.
6. Never resubmit an ambiguous create/update after a timeout or 202. Inspect
   the known operation and live state first; check all matching items before
   considering another write.
7. A save in the Fabric Plan editor took about 45–90 seconds to appear in
   `getDefinition`. Wait before exporting a UI capture, and re-export if the
   expected change is missing rather than concluding the save failed.
8. Run snapshot → concurrency check → validate → pack → update as separate
   steps and stop on any non-zero exit code. A chained shell command (`;`)
   once kept going after the concurrency check failed and overwrote a user's
   saved edits.

## Paging

List calls return `continuationToken` / `continuationUri`. Loop until absent
before concluding that an item does not exist; prefer the returned
`continuationUri`. Plan listing supports `rootFolderId`, `recursive` (default
true), and `continuationToken`. Match exact names across all pages and stop on
multiple matches instead of selecting the first ID.

## Run-state record

Keep one compact record in `_build/run-state.json` and update it after each step:

```json
{ "workspaceId": "", "workspaceName": "", "modelId": "", "modelName": "",
  "planId": "", "planName": "", "definitionPath": "_build/def/",
  "lastOperation": { "kind": "updateDefinition", "operationId": "", "status": "" },
  "validated": false, "published": false, "readbackVerified": false,
  "modelMeasurePermission": "none", "modelMeasuresCreated": [] }
```

No tokens, no headers, no personal data.

## Additional details

Merged from the companion Intelligence authoring library. Additive only:
the sections above and the frontmatter `encoding` take precedence. Tags:
[saved] saved exports, [confirmed] user-confirmed, [open] unresolved.

- **Endpoints and hosts.** A portal URL is not necessarily the REST API base
  URL. Confirm the base from known configuration and trusted responses, never
  by text substitution in a portal URL. Follow operation and result redirects
  only to verified service hosts of the intended environment, and never
  forward credentials to an arbitrary URL found in a payload.
- **Resultless operations.** A `/result` request for a succeeded operation
  without a result body returned `OperationHasNoResult` in the companion work
  [open]. Rule 4 still applies: do not fetch it for update-definition, and
  never treat that code as a failed mutation or a reason to resubmit; confirm
  the terminal state and read back instead.
- **Visible polling.** Report stage, elapsed time, next retry and the last
  useful service status while polling; avoid one long silent wait.
- **Diagnostics.** Add the service error code and request or correlation ID
  to `lastOperation` in the run state when available; still no headers or
  tokens.
- **Idempotency.** Retrying an idempotent status `GET` differs from retrying a
  create `POST`; only the first is safe after a timeout.
- **Response parsing.** Normalize the response type before parsing: parse a
  JSON string once, use an already parsed object directly and handle an empty
  response explicitly.
- **Readiness gates.** An accepted create, a terminal operation, a persisted
  definition and loaded sheets are separate gates. Wait for the gate the next
  step needs instead of adding a fixed delay and assuming success.
