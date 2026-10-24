# Workflow hardening and authorized relaunch evidence

## Verified before relaunch

- `python -m unittest discover -s tests`: **79 tests passed**.
- Targeted Pyright on workflow/preflight/MCP/export/checkpoint/controller/resume/
  relaunch preparation: **0 errors, 0 warnings**.
- Fresh `scripts/preflight_blender52.py`: **passed**; all17 MCP tools discovered,
  actual Blender **5.2.3 LTS**, CPU-only queue, Qwen3.6 native262144 context,
  automatic compaction/pruning with16384 reserved tokens and no step cap.
- Fresh `opencode debug agent bowling-coder`: primary Qwen3.6 agent; Bash/Task
  disabled, image generation denied, managed state/validator/config edits denied.
- `python3 scripts/run_bowling.py --check-continuation`: **passed**; current source,
  canonical native hash, immutable validator hash, report hash, guard-row hash and
  reset epoch2 match `continuation.json`. This plan requires a fresh coding session.
- Real MCP execution and restart proof: `mcp-acceptance.json`. Common invalid
  render/API author requests made no submissions; a durable view ID selected the
  camera, queued a real CPU render and published verified bytes without replacing
  the current asset source. A new MCP process recovered the same view/state.

## Preserved accounting and asset state

- Reset epoch2 starts after row64. **0 current failures**, **26 historical failed
  jobs preserved**, unchanged limits **6/source,20 total**. No attempt/fingerprint
  rows were deleted. `attempts.before.json`, `attempts.after.json` and
  `reset-receipt.json` preserve the reconciliation and accounting evidence.
- Current asset source: `756846c5415e4c5e92f159389a87eeb0`.
- Canonical native SHA-256:
  `6b352b5ba0c22b8b69e124ce602133b771fb84e821ed68075f5a5821d6a98810`.
- Measured stages00–03 PASS,04 UNRESOLVED,05–07 FAIL. Geometry was not repaired by
  this infrastructure work. The queued overview qualification image was visually
  inspected and is blank/obstructed; it is execution evidence, not asset acceptance.
- Fixed presentation-review and selected-export/reimport delivery paths have
  unit/type-check coverage but have **not** been live-qualified as successful asset
  delivery. Their current acceptance gates remain enforced.

## Recovery and publication boundaries

`before/`, `failed-model-scripts/`, controller/checkpoint copies and the local SQLite
backup preserve prior state. Binary native/SQLite backups remain local and ignored
by Git. Model-authored scripts are preserved as evaluation history. No references
were regenerated and no primary model/runtime or GPU policy was changed.

Use `python3 scripts/run_bowling.py --status` for current controller/session state.
Do not launch another controller while its lock is held. An interrupted workflow
must inspect the durable accepted IDs and guard before explicit resumption; do not
rerun the one-shot reset installer or replay uncertain submissions. For rollback,
stop the controller first and retain its accepted jobs/guard history; inspect the
archived state before restoring any checkpoint or selecting a new continuation.

The detached launch opens a fresh OpenCode process and loads the new configuration.
Existing interactive OpenCode processes need a quit/restart to load these changes.
