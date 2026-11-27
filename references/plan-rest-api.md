# Fabric Plan REST operations

This guide summarizes the public Fabric REST contract for Plan items and how the
bundled transport applies it. It describes access and failure handling; it is
not permission to call anything. Workspace writes still need the explicit
destination file with `authorizedMutation`.

The only supported base is `https://api.fabric.microsoft.com/v1`. Every request,
operation poll and result read carries `x-ms-fabric-skill: fabric-plan-skill`.

## Contents

- [Operations and access](#operations-and-access)
- [Listing, reading, renaming and deleting](#listing-reading-renaming-and-deleting)
- [Preconditions and request content](#preconditions-and-request-content)
- [Responses and errors](#responses-and-errors)
- [How the bundled transport behaves](#how-the-bundled-transport-behaves)
- [Primary sources](#primary-sources)

## Operations and access

| Operation | Run by this package | Caller permission | Delegated scope | Long-running |
|---|---|---|---|---|
| Get Plan Definition | `api export` | Read and write on the Plan | `Item.ReadWrite.All` | Yes |
| Create Plan | `api create` | Contributor workspace role | `Item.ReadWrite.All` | Yes |
| Update Plan Definition | `api update` | Read and write on the Plan | `Item.ReadWrite.All` | Yes |
| List Plans | `api list` | Viewer workspace role | `Workspace.Read.All` or `Workspace.ReadWrite.All` | No, paged |
| Get Plan | `api get` | Read on the Plan | `Item.Read.All` or `Item.ReadWrite.All` | No |
| Update Plan (name, description) | `api rename` | Read and write on the Plan | `Item.ReadWrite.All` | No |
| Delete Plan | `api delete` | Write on the Plan | `Item.ReadWrite.All` | No |

All seven operations accept users, service principals and managed identities. A
delegated scope and a workspace or item permission are separate requirements: a
token with the right scope still fails without the role, and the reverse.

Applying `.platform` metadata through the generic item update with metadata
enabled is not run here; keep the exported `.platform` part unchanged in an
update.

## Listing, reading, renaming and deleting

These commands use the same destination file as the definition commands. Reads
need no write authorization. `rename` and `delete` need `authorizedMutation`
and are journaled like every other write.

- `api list` returns every Plan in the destination workspace, following
  `continuationUri` to the last page. To find a Plan by name, match
  `displayName` exactly and stop when more than one Plan matches.
- `api get` reads the metadata of the Plan named by `planId`.
- `api rename` sends the destination's `name` as the new display name and its
  `description`, when present, as the new description. An empty name or a
  description longer than 256 characters is refused before any request.
- `api delete` needs three facts that agree: `planId`, `confirmDeletePlanId`
  set to the same ID, and `name` set to the Plan's current display name, which
  is read back first. Any mismatch stops the run before the delete. Afterward
  the command reads the Plan again and records `verifiedAbsent`: true only for
  a 404 with `ItemNotFound`, false if the Plan is still returned, and null for
  any other outcome, including a 404 with another error code. Rerunning with the same `--run` and `--label` replays the
  journaled delete instead of sending another.

```sh
python scripts/plan.py api list --config destination.json --run run --label plans
python scripts/plan.py api delete --config destination.json --run run --label delete
```

## Preconditions and request content

- Creation needs a workspace on a supported Fabric capacity.
- Exporting a Plan protected by an encrypted sensitivity label needs usage
  rights that allow removing the label, as configured in Microsoft Purview.
  Never remove or lower a label to get past this.
- A create request needs `displayName`. `description` is optional and limited to
  256 characters; this package does not send one. The definition is optional in
  the contract; `api create` always sends a complete definition.
- A definition needs only `parts`. Each part needs `path`, `payload` and
  `payloadType` (`InlineBase64`). `format` is optional, and `PlanV1` is its only
  documented value.
- An update replaces the whole definition. Send every retained part, not only
  the changed ones.

## Responses and errors

| Response | Meaning |
|---|---|
| `200`, `201` | Completed; `201` means the Plan was created. |
| `202` | Accepted as a long-running operation. Follow `Location`, or the operation ID in `x-ms-operation-id`. |
| `429` | Throttled. `Retry-After` gives the wait in seconds. |
| `401` | The token was rejected. Check that it was issued for `https://api.fabric.microsoft.com` and has not expired. |
| `403` | The identity lacks the role, permission or scope in the table above. Stop; do not retry with another route. |

Error codes named by the operation contracts:

| Code | Operations | Response |
|---|---|---|
| `CorruptedPayload` | Create, Update Plan Definition | A part failed decoding or validation. Check Base64, UTF-8 JSON, required parts, schemas and references locally before any new attempt. |
| `ItemDisplayNameAlreadyInUse` | Create, Update Plan | The name is taken in the workspace. Resolve which Plan is intended; never rename, reuse or overwrite silently. |
| `WorkspaceItemsLimitExceeded` | Create | The workspace has reached its item limit. |
| `InvalidItemType` | Create, List Plans | The request named the wrong item type. |
| `ItemNotFound` | Get, update, delete and definition operations | Re-resolve the workspace and Plan IDs before concluding the Plan is gone. |

A failed long-running operation reports its code in the operation's `error`
object rather than in the response to the original request.

## How the bundled transport behaves

**Identity and endpoints.** The token comes only from the environment variable
named by the destination's `tokenEnvironment`. An expired token stops the run
with `AUTH_EXPIRED` before any request. Requests go only to
`api.fabric.microsoft.com` over HTTPS, redirects are not followed, and a token
in a URL or in a response stops the run. Responses larger than 64 MiB are
rejected locally; that limit is not a Fabric guarantee.

**Throttling and transient failures.** Reads are retried up to three more times
after `429` or a `5xx` response, waiting for `Retry-After` (seconds or an HTTP
date, 2 seconds when absent), and after a dropped connection. Writes are never
retried automatically, including after `429`: a throttled or interrupted write
becomes an explicit resume or reconciliation step.

**Mutation journal.** Every write needs a `--label`. The transport records the
request intent in the run's `api` folder before sending it, and the response
after. Rerunning the same command with the same `--run` and `--label` replays
the recorded response instead of sending the request again. An intent without a
response means the outcome is unknown: the run stops with
`UNCERTAIN_SUBMISSION`, and the next step is a fresh export to see what the
service holds, never a second create.

**Long-running operations.** On `202` the transport takes `Location`, or builds
the operation address from `x-ms-operation-id`, and writes a
`<label>.operation.json` checkpoint before polling. It never follows another
host. Some tenants return a regional host in `Location`: when the response also
carries the operation ID, the transport polls the public operation address for
that ID instead, and without an operation ID it stops. It honors
`Retry-After` between polls, in slices of at most 30 seconds. Polling stops after
120 polls or 30 minutes with `PENDING: resume same operation checkpoint`; rerun
the same command and label to continue polling the same operation. On
`Succeeded` it reads the result from the completed response's `Location`, or the
operation address plus `/result`. On `Failed` or `Cancelled` it stops with
`Operation <status>: <errorCode>: <message>` and keeps the service `error` object
in the checkpoint, because operation polls are not otherwise journaled.

**Updates against a reviewed baseline.** `api update` exports the Plan again and
compares it with the reviewed baseline hash before submitting. Any difference
stops the update for reconciliation. This is a check, not a server-side lock;
coordinate an exclusive edit window when concurrent edits must not be lost.

For example, to resume an interrupted update or an update whose polling timed
out, repeat it unchanged:

```sh
python scripts/plan.py api update --config destination.json --payload candidate.json --run run --label update
```

## Primary sources

- Plan operation group:
  https://learn.microsoft.com/en-us/rest/api/fabric/plan/items
- Plan REST specification, including the definition contract:
  https://github.com/microsoft/fabric-rest-api-specs/tree/main/plan
- Long-running operations:
  https://learn.microsoft.com/en-us/rest/api/fabric/articles/long-running-operation
- Get Operation State and Get Operation Result:
  https://learn.microsoft.com/en-us/rest/api/fabric/core/long-running-operations/get-operation-state
  and
  https://learn.microsoft.com/en-us/rest/api/fabric/core/long-running-operations/get-operation-result
- Supported identities:
  https://learn.microsoft.com/en-us/rest/api/fabric/articles/identity-support
