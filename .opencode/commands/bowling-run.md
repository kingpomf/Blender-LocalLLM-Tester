---
description: Launch the full image-reference-to-Blender workflow without per-stage prompts
agent: build
model: z6-llama/qwen38-turbo
---

Start the operator-authorized continuous BowlingPair01 workflow by running
`python3 scripts/run_bowling.py --detach`. The controller uses Qwen3.8 Turbo for
reference preparation and a fresh Qwen3.8 Turbo coding session for all
Blender stages. It checkpoints and handles successful stage-to-stage continuation
automatically. Do not also submit image/Blender work from this launcher session.

If a controller/run already exists, inspect `python3 scripts/run_bowling.py --status`
instead of launching another. Use --resume only when explicitly requested after
reconciling the recorded blocker/interruption. Report the returned controller PID,
log/state paths and how to check status. Do not claim the asset is complete when
only the controller has started. Ordinary incomplete startup/validation gets up
to two diagnostic recovery turns. Actual tool STOP, explicit interruption and
exhausted failure/recovery budgets stop the run; COMPLETE finishes it.
