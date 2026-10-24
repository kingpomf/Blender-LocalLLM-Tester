# Reconciliation evidence — 2026-10-24 UTC

User authorized reconciliation, a ball-code diagnostic report, doubling the
failure limits and a continuation command they will invoke themselves.

- Last completed model-authored source: `d1ce998472c349ac9f9fc2775afefdf6`.
- Native artifact checksum verified and copied to `artifacts/blend/BowlingPair01.blend`.
- All original12 guard rows match their terminal remote states;6 failed/6 completed.
- One guarded read-only audit completed: `4f572bf507534fe184d09d7014e0d60c`.
  It queried installed APIs and measured existing geometry without repairing it.
- Current ledger therefore contains13 terminal jobs:7 completed/6 failed.
  No prior failure rows were deleted or changed. Same r2 queue remains selected.
- Limits are6/source and12/total. Current source has3 failed attempts already;
  continuation starts with3 remaining on that source and6 remaining globally.
- Stage00 foundation passes. Actual geometry disproves prior Stage01–03 PASS
  claims; ledgers now record those defects and failed Stage04 honestly.
- `continuation.json` binds source/checkpoint hash, model, queue, guard-row hash
  and approved limits. Its read-only preflight passes.
- Controller remains stopped; no resumed model session or asset repair was launched.

Files: original ledgers/controller state, ignored SQLite backup, remote job
manifests, canonical checkpoint receipt, native audit, measured findings and exact
ball submission snapshots (01–03 failed;04 was rejected before execution).
See `../BALL_GENERATION_DIAGNOSTICS.md` and `../../CONTROLLED_CONTINUATION.md`.

Verification:51 regression tests pass; fresh installed MCP reports6/source12/total
and6 retained failures; reference/resume/continuation checks pass. The original
ball script remains unchanged and has a confirmed invalid API call; its Pyright
diagnostics are reported, not hidden or falsely marked resolved. Actual repairs
belong to the operator-started, explicitly assisted continuation.
