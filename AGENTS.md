# Simplified kart challenge

Build the asset described in `spec/KART_SIMPLIFIED.md`. This branch intentionally replaces the old ten-stage challenge with BUILD, REVIEW, DELIVER. Legacy specs and session reviews are historical evidence.

Read `RUN_STATE.json` and run `python3 scripts/check_resume.py` before work and after compaction. This is the only progress ledger. Record actual model, accepted job ID/source immediately before polling, result evidence, checkpoint hash, and next action there. Poll recorded pending work; never replay uncertain submissions. Preserve archives and existing user work. Do not start fresh over an existing attempt.

Use the Z6 worker, verify authoring and diagnostics capabilities first. Fresh scenes contain zero objects. Omit source_job initially; later jobs use the last verified completed authoring source. Worker code executes as __blender_author__: invoke code unconditionally and assign a top-level report. Save exact submissions in artifacts/scripts. Fetch scene.json/report.json and hash-verified scene.blend checkpoints. Worker paths are /job; local artifact paths are delivery destinations.

BUILD: author the entire kart in one initial submission, using support/kart/helpers.py if useful. Materials and parenting are created with each part. Save a checkpoint; execution success alone is not acceptance.
REVIEW: use supplied presentation and validator code. Fix measured failures from the last usable source, rerun validation, inspect four actual named camera views. Do not replace failing checks with assumptions or edit acceptance code to pass. Subjective silhouette/support checks require honest visual review. Stop after three unsuccessful repairs of the same issue; diagnose each failed CPU job once. Never resend identical failed code/source.
DELIVER: export only root and descendants, fetch all outputs, run local delivery checks, record evidence and known defects. Mark COMPLETE only after numeric, visual, and delivery checks pass for the same final asset. If visual inspection is unavailable record BLOCKED, not PASS.

Do not interrupt protected GPU work, change gateway ownership, install dependencies, or alter unrelated projects. No model or infrastructure changes are required. Do not commit/push build output without explicit authorization. Supplied helpers/validator/rig are assistance; record that attribution.
