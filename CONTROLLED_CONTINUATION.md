# Enforced-workflow continuation — Qwen3.6 remains the asset agent

## Active API-aware retry

The user authorized committing the installed-API/self-correction changes and
another detached run. Read `testing/api-aware-relaunch/HANDOFF.md` first. Use
blender_api_lookup, then make small verified edits from the authoritative MCP
source. Current accounting is **3 hard failures +1 recoverable API correction**,
epoch2 unchanged; historical30 failed jobs remain preserved. Earlier retry notes
below are historical. Wrong API calls now receive recoverable guidance, not a
hard-error charge, when confirmed against the installed catalog.

## Active retry after automatic review recovery

Read `testing/review-recovery-relaunch/HANDOFF.md` for the current retry. The
latest source is **2b37b77ce016462c943a217f67fb9418**, not the earlier sources
below. The saved negative image review has been recovered without regeneration;
status/admission now reconciles completed/invalid/expired reviews automatically.
The two counted failures and epoch2 remain unchanged. Earlier starting points
and retry notes below are historical; MCP workflow state is authoritative.

## Previous retry after reviewed native-failure fixes

The user authorized another detached run after commit `bfa62a6`. Read
`testing/native-failure-relaunch/HANDOFF.md` for the active retry instructions.
The checkpoint below is unchanged, but **2 failures are now counted** and **28
historical failed jobs are preserved** in epoch2. No additional budget reset was
authorized. The zero-failure starting point below describes the earlier launch.
Begin with one small scene correction, then poll its automatic validation before
another edit. Do not resubmit the earlier multi-stage correction scripts.

The user authorized the workflow repair, another archived error-counter reset,
commit/push and detached relaunch. This is the same assisted r2 asset trial.

## Starting point

- Agent **bowling-coder**, model **z6-llama/qwen36-35b-a3b-mtp-q8**, retuned native256K.
- Current common asset source: **756846c5415e4c5e92f159389a87eeb0**.
- Canonical native hash:
  **6b352b5ba0c22b8b69e124ce602133b771fb84e821ed68075f5a5821d6a98810**.
- The canonical file has been recovered from that actual completed native job,
  replacing the stale older pin checkpoint. New fixed validation measured this
  current scene; do not infer acceptance from the earlier Stage04–06 reports.
- Budget epoch2: **0 current failures**,6/source20/total. All26 historical failed
  jobs and their fingerprints are preserved. No further reset is authorized.
- Source/counter/history/old state backups are in testing/workflow-hardening-20261024/.
  References remain READY; do not regenerate images or restart from an empty scene.

## New operating contract

Call **blender_workflow_status** first. It provides authoritative current source,
compact failed/unresolved checks, budget and accepted pending IDs. It restores
managed stage mirrors from verified measured evidence. Do not read stale claims
from a previous compaction summary as truth.

The coding agent has **no Bash or Task tools**. Critical work no longer depends
on running shell helpers or editing Markdown. Do not edit managed status/source/
hash files, validators, runtime state or acceptance specifications.

### Scene repair

Use blender_scene_author for actual changed scene/camera code. Save your script
and inspect LSP diagnostics; do not blanket-ignore API errors. Inline render
calls, output subdirectories and known wrong APIs return recoverable preflight
guidance before consuming a submission attempt. Repair the code/use next_tool.

Poll accepted job IDs. Completed asset authoring automatically:
1. downloads/verifies and publishes the native checkpoint;
2. queues the fixed read-only validator;
3. returns its validation_job for polling;
4. derives stage results and both ledgers from actual measurements.

No new authoring can overlap an accepted pending job. A completed execution does
not mean a stage passed. Inspect the returned remaining check IDs and correct
actual geometry/evidence; no hand-written PASS or threshold changes.

### Presentation

Prepare only cameras/lights in authoring. Never render inside it.
Use **blender_render_view(role)**, one role at a time, and poll its **view- ID**.
The tool selects the camera, queues one CPU render and publishes its actual bytes
with same-asset lineage/hash proof. It does not replace the asset source with a
camera-only branch. Use8 samples initially. The initial tool qualification already
rendered one overview preview from the current source; it is blank/obstructed and
not accepted. Correct actual occluders/framing before producing final views.

When four useful current views exist, write ASSET_GUIDE.md with measured pivot/
axis/material/import information and call **blender_review_presentation**. Poll
its **review- ID**. The bounded fixed helper observes actual pixels and supplied
geometry facts; it is not a primary coding model. False/unresolved review must
not be converted into a pass. Refresh **blender_validate** after evidence changes.

### Delivery

After current measured/visual acceptance passes, call **blender_export_delivery**.
Its fixed artifact-only job exports six proper selections, imports each GLB and
checks bounds, mesh counts/roles, pivots and materials, restoring the source scene.
Poll it for automatic publication. Write BUILD_REPORT.md and ASSET_GUIDE.md, then
**blender_finish_delivery** verifies the complete current package and generates
the delivery hash manifest. Only it marks COMPLETE.

## Repair scope and continuation

Use the current MCP findings. Stage00–03 previously measured pass and should not
be rebuilt. Current ball work, floor/return support, collision and presentation
need current evidence/repairs—do not repeat legacy Clearcoat/extrusion mistakes.
The model's earlier OOM/"parser failed" diagnoses were not established: two jobs
were killed with137; another rendered inline and created a directory the worker
correctly rejected. The enforced queue/path checks prevent that route now.

Continue automatically with compaction as needed, re-querying machine state after
compaction. The fresh coding session avoids old false PASS/"all Bash rejected"
summaries. True STOP, exhausted budgets, uncertainty and explicit user stop still
halt; recoverable preflight/pending responses do not. Never replay an uncertain
request or change sources solely to evade a failure limit.

User authorized the assistant to launch detached after verification/publication.
Monitor with `python3 scripts/run_bowling.py --status`; the runtime process and
workflow event paths are reported there. Do not launch a second controller.
