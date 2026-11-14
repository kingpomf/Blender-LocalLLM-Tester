# Simplified kart source preservation — November 13, 2026

This cleanup preserves the existing Flash-Next trial configuration, authoring
scripts, operator helpers, report and `RUN_STATE.json` without changing its
recorded **BLOCKED** visual-acceptance state.

Fresh checks passed: both local unit tests, `scripts/check_resume.py`, and
`scripts/check_delivery.py`. The latter verifies local structure and hashes, not
new visual acceptance or a byte-identical delivered-GLB Blender round trip. The
model-authored report and ledger retain their original bytes and evidence limits.

Runtime/session journals, native files, exports, renders and downloaded receipts
remain local ignored artifacts. Authored Python source and the dated report are
versioned. No Blender job, model switch, controller, publication helper or runtime
deployment was started by this repository cleanup. The shared review package
remains subject to its existing operator-review and provenance limitations.

The setup instructions predate this completed numeric run: consult the retained
ledger before any continuation rather than starting an empty trial. Restart a
trial OpenCode session when intentionally loading its saved configuration.
