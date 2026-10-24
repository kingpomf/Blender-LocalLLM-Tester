---
description: Launch the full image-reference-to-Blender workflow without per-stage prompts
agent: build
---

Start the operator-authorized continuous BowlingPair01 workflow by running
`python3 scripts/run_bowling.py --detach`. The controller uses the vision model
for reference preparation, then a separate Qwen3.6 MTP session for all remaining
Blender stages. It checkpoints and handles successful stage-to-stage continuation
automatically. Do not also submit image/Blender work from this launcher session.

If a controller/run already exists, inspect `python3 scripts/run_bowling.py --status`
instead of launching another. Use --resume only when explicitly requested after
reconciling the recorded blocker/interruption. Report the returned controller PID,
log/state paths and how to check status. Do not claim the asset is complete when
only the controller has started. The background run stops on actual tool STOP,
failed validation, no verified progress, explicit user interruption or COMPLETE.
