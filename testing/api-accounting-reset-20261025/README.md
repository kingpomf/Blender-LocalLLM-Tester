# Reviewed API return types, consistent accounting and authorized epoch3 reset

## Defects found and fixed

1. The catalog listed Object.children but omitted its concrete Python return type.
   The actual installed5.2.3 runtime now records children/users_collection as
   tuples and children_recursive as a list, plus element types and permitted
   members. These are included in MCP lookup and checked through aliases, helper
   scopes and known collection iteration. Shadowed/rebound/conditionally changed
   receivers lose stale type assumptions instead of causing speculative rejection.
2. Runtime fallback ignored builtin return-type misuse. A soft correction now
   requires the accepted script fingerprint, exact traceback line, and API-derived
   receiver/type/member proof. Generic tuple errors remain hard. Supported keyword
   validation similarly requires source/catalog/terminal-exception agreement.
3. Diagnostics could return an API error without its soft classification. Status
   and diagnostics now share one classifier/accounting path and cached evidence.
   The controller cannot recharge a soft error merely because diagnostics were read.
4. Historical failure polls could restart a streak after reset. Terminal responses
   now identify their accounting epoch/historical status. The controller excludes
   pre-reset failures and late-confirmed API errors from its active hard streak.
5. Earlier log exceptions could mask a later actual error. Classification now uses
   the final worker exception, preferring blender.log over stale Python output.
6. A legacy catalog capture could silently replace the richer API catalog. Version2
   return-type evidence is now required; older captures cannot downgrade admission.

No blanket AttributeError/TypeError exemption was introduced. Geometry rejection,
removed-object errors, cancellations and unproven Python mistakes remain hard.
API/preflight errors allow genuine changed-code corrections, not identical replay.
Static checks remain conservative, not proof of all dynamic Python or geometry.

## Actual runtime and regression evidence

- Read-only catalog refresh job **003523a3675043c79d5a48d0ee388f36** completed on
  Blender5.2.3 LTS. No asset datablocks were modified; the original asset source
  remains2b37b77ce016462c943a217f67fb9418.4,011 types/2,497 operators retained.
- **110 tests passed**, targeted Pyright **0 errors/warnings**.
- `mcp-acceptance.json`: a fresh MCP process rejects the actual latest failing
  script at line29 before submission; lookup exposes Object.children's tuple
  result; status and diagnostics both classify its runtime failure as soft.
  The prior degenerate-gutter failure remains hard. No new attempt rows were added.
- `mcp-after-reset.json`: a second fresh MCP process observes0 active hard errors,
  0 API corrections, epoch3, and31 preserved historical failed jobs. Polling old
  hard/API outcomes does not charge the controller or mutate guard attempt rows.
- The current continuation passes source/native/report/validator/guard hash checks.
  No asset acceptance threshold or validator was changed.

## Authorized reset and relaunch

The user explicitly authorized archiving and resetting failures to zero, commit/
push and a detached run. The reset verified the remote terminal status of all
**106 accepted attempts** before advancing the accounting cutoff to epoch3.
Active hard failures, API corrections and the controller streak are zero; all
31 original failed jobs, fingerprints and API classifications remain intact.
Limits are unchanged:6 hard failures/source20 total.

`reset-receipt.json`, `attempts.before.json`, `api-corrections.before.json`,
`continuation.json` and `before/` preserve the reset evidence. The local SQLite
backup, native checkpoint and nested runtime backups remain ignored by Git.
Do not rerun the one-shot reset script. If interrupted, inspect saved accepted IDs
and receipts rather than replaying submissions or resetting again.

The new session receives the concise current CONTROLLED_CONTINUATION.md and this
folder's HANDOFF.md. It is instructed to fix one criterion/object group at a time,
query the installed API, validate each edit, and preserve passing visual gutters.
No new model, reference generation, GPU policy or automatic counter reset is added.

Monitor using `python3 scripts/run_bowling.py --status`. The launch is process-
detached, with existing controller locking and automatic stop protections. Asset
completion remains unverified; these tests qualify workflow/accounting behavior.
