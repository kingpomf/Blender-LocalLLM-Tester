# Post-relaunch repeated-failure diagnosis

The user reported repeated failures in session `ses_e8fd2898dffejP9GEwx0p9wz7y`.
The controller and its client were stopped gracefully and their exit verified.
No pending native jobs remain. Source and canonical checkpoint are unchanged.
Accounting remains epoch2: **2 current failures,28 historical failed jobs**;
no reset or history deletion was performed.

## Actual errors

Both `d647a3b108ae467abe26a4431cc59b4c` and
`4b5ba2cb92d049daad1a9f5af648205e` failed with
`ReferenceError: StructRNA of type Object has been removed`, at submitted
lines114 and119 respectively. Both scripts remove `existing.data` before
removing `existing`. The datablock removal invalidates the dependent object.
The model's proposed fix—collecting names before iterating—kept the destructive
deletion order, so the second submission repeated the underlying defect.

The model also made numerous local edits/LSP corrections before submission.
Those are distinct from the two native failed attempts. No asset acceptance
or measured geometry advance occurred.

## Control gaps repaired

- Authoring preflight rejects direct removal of a live object's mesh/camera/light
  datablock, explains the correct object-first order, and consumes no attempt.
  Both actual accepted failed scripts are now rejected by this check.
- Controller monitoring parses successful MCP responses for failed/cancelled
  **native jobs**, records their IDs in `last_errors`, and immediately terminates
  the client after two distinct failures without a published successful asset
  edit. Repeated polls/diagnostics of the same job count once. Validation success
  alone does not reset the streak. The streak persists across controller phases.
  Named-view failures resolve to their native job IDs. Previously counted failures
  are not counted again after progress, and polling an already-known successful
  asset job cannot reset the streak. A retained two-failure streak blocks client
  startup until operator reconciliation.
- Failed native outcomes update mirrored failure counters when current validation
  is available. Status synchronization preserves BLOCKED for interrupted/blocked
  controllers instead of silently restoring IN_PROGRESS. Explicit validated
  continuation can restore running mirrors after the controller starts.
  Named-view failures update counts on the first terminal poll. Startup ledger-sync
  failures are recorded as BLOCKED, and controller stop state is saved before
  writing Markdown mirrors so a mirror-write failure cannot hide the stop.

## Verification and current disposition

**87 tests pass**; targeted Pyright reports **0 errors/warnings**. Coverage includes
object-first cleanup acceptance, zero-attempt preflight rejection, native failures
inside successful tool responses, duplicate-poll exclusion, and a simulated
controller client being terminated before its third event after two failures.
Review regressions cover named-view/native deduplication, replayed successful
asset status, retained-streak startup rejection, startup-sync failure state, and
first-poll render-failure accounting.
The current ledger synchronization confirms2 failures and0 pending jobs.

Use `python3 scripts/inspect_run_events.py .runtime/autonomous-run/006-coding.jsonl`
for concise saved native outcomes, exception tails and current preflight checks.

The run remains **paused**; the user authorized review and publication of these
bug fixes, not another launch. The asset repair has not been live-qualified.
The old continuation's guard
hash predates these two failed jobs and must not be reused as an authorization
for another launch. The preserved model-authored correction scripts are evidence,
not a verified geometry repair. Workflow-control tests do not establish that
Qwen3.6 can complete this asset autonomously.
