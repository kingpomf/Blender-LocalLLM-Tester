# Operator pin correction and explicit active-failure reset

The user authorized the correction, checkpoint reconciliation, zero active
failure counts and detached launch. This folder preserves the pre-reset database,
48 unchanged attempt rows, controller/ledgers, native checkpoint and original bad
pin script. The native binary/database backups stay local; state/receipts/reports
are versioned. No failed attempt was rewritten or deleted.

Reset receipt records epoch1 at row48:18 failed requests remain historical while
current failure count starts at0. Their fingerprints still reject unchanged
replay. Per-source6 and global20 limits still apply to subsequent failures.

Operator-provided corrected pin job78c0eaf6afba483694c2ca2c6eec4472 completed;
independent read-only validator2e5c733a50d847bf8dd74e9f48aa6116 completed. Stages
00–03 now measure PASS. At launch preparation,50 accepted jobs are terminal:
32 completed,18 failed; zero active-budget failures. Both new jobs succeeded.

Canonical scene hash is
0fce120fa532133520de7b69dcd3a8e2fbd2897ce74fd367aca5f25266801980.
The handoff/plan selects this corrected source and a fresh Qwen3.6 coding session
to avoid stale failed-session diagnoses. It retains old session IDs/history and
the same r2 trial. Current work is remaining04–09, not a rebuilt assignment.

Verification:66 regression tests pass; corrected native script type checks pass;
native pin audit confirms20 pins, correct dimensions, closed nondegenerate
outward mesh and two neck bands. Validation still honestly reports the remaining
scene/presentation defects. See ../PIN_CORRECTION_RESET.md and the active plan.
