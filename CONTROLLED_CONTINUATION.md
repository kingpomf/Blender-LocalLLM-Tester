# Current Turbo continuation — context recovery and error reset

The user authorized fixing context overflow/automatic recovery, archiving and
resetting active errors, committing/pushing all changes and a new detached run.
Read testing/context-recovery-reset-20261025/HANDOFF.md. This continues the same
Qwen3.8 Turbo trial and asset; it does not restart references or scene construction.

- Model: z6-llama/qwen38-turbo; native139264 context/16384 output retained.
- Compaction/pruning enabled, **32768 reserve**, no step cap. Tool output cap:
  **160 lines/12000 bytes**. Earlier compaction leaves room for the next response.
- Trial: bowling52-qwen38-turbo-20261025-r1; Blender5.2.3 LTS CPU queue.
- Starting source: **c3e6eb270cce4cdd82671452900849bc**. Use current MCP source if it
  advances. Canonical hash at authorization:
  **38411b0cf6add697e68d6f1ef9a507ab5c6dd230cd4b6f7fcc31c4a6fb7f496b**.
- Reference phase is verified **READY**. Do not regenerate completed images.
- Epoch1 starts with **0 hard failures,0 API corrections,empty active streak**;
  all39 accepted attempts and5 historical failed jobs remain. No further reset.

The current validation is138 PASS/79 FAIL/4 unresolved. **No asset stage has fully
passed.** Prior prose claiming Stage00 PASS is wrong; S00_hierarchy still fails.
Start with that concrete failure, then work through earlier-stage findings rather
than repeatedly rebuilding pins. One small criterion/object group per revision.

Use blender_workflow_status, **blender_scene_summary(names=[...])** and
**blender_validation_details(stage="00")**. Follow next_offset for a small page.
Do not load whole scene.json/validation files into context. Consult installed API
lookup before unfamiliar calls. Poll every accepted native ID and auto-validator.
Actual measurements, not a report's passed flag, determine acceptance.

A confirmed context-only overflow can now reconcile accepted jobs/checkpoint and
continue in a fresh context automatically. It never resets counters or replays
jobs. Mixed transport/API errors, hard STOPs, uncertainty, explicit user stops and
repeated overflow without a new verified checkpoint remain bounded stops. The
reference phase also requires saved image acknowledgements before context rotation.

Coding agent has no Bash/delegation. No inline render, output subdirectories,
validator changes, managed-file edits or manual PASS. Use queued named views, fixed
pixel review and selected export/reimport tools for later acceptance/delivery.
Resume from machine state after compaction; never trust stale summaries.

Monitor: `python3 scripts/run_bowling.py --status` or the read-only Blender trial
report at http://z6-llm:8088/blender-trial/. Do not launch a duplicate controller.
