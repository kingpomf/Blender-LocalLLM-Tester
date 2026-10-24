# BowlingPair01 Agent Test

## Goal

Build a modular, game-ready bowling alley pair, `BowlingPair01`, using `spec/bowling-pair-01/00-CONTRACT.md` through `09-DELIVERY.md`. Include two lanes, twenty pins, three bowling balls, gutters, a shared ball return, and alley dressing. The specifications define acceptance; do not weaken them to obtain a pass. This is a fresh bowling assignment authorized by the operator; the kart trial is historical evidence only.

Start by reading `BUILD_STATUS.md`, `HANDOFF.md`, `WORKER_GUIDE.md`, and the specifications needed to plan the work. Run `python3 scripts/check_resume.py` before submitting work. If it flags stale/contradictory progress, reconcile the saved artifacts and accepted jobs before continuing; do not start over or delete them. You may inspect any relevant project files, consult Blender API documentation, use applicable skills, and ask clarification questions. Keep work focused on this asset.

**Selected model:** `z6-llama/qwen36-35b-a3b-mtp-q8` (262,144-token context, reduced to native 256K by operator request on 2026-10-23).
This is the **Blender coding** model. `/bowling-references` separately selects
vision-capable `z6-llama/qwen38-27b` to plan, generate and inspect images first;
its input window is 139,264 tokens. Reference planning is recorded separately
and is not a result from the MTP coding trial.
The operator authorized a fresh Qwen3.6 MTP UD-Q8_K_XL trial on 2026-10-23;
all prior Nemotron scenes, scripts and guard state are archived.
No previous source or PASS is reused. Read the checkpoints before submitting.

**Continuous execution:** complete all remaining stages 00–09 in succession.
After each verified stage, save both checkpoints, run the consistency check and
immediately continue to the next stage without asking the user to say “next”.
Automatic compaction and tool-output pruning are enabled, with a16,384-token
compaction reserve. The previous60-step cap is removed. Compact as needed,
preserve durable evidence, then reread both ledgers and resume the same verified
source. A stage boundary or compaction is not a reason to end the run.
Stop only at verified COMPLETE, an explicit user stop, a genuine unresolved
blocker/required approval, or the existing tool failure limit. Never bypass a STOP.

## Blender workflow

- Before ANY Blender authoring, complete the imageMCP reference phase in `REFERENCE_IMAGES.md`: overview, layout and detail sheet, verified local images and a construction guide. Record accepted image jobs in both ledgers before polling. The wrapper enforces `scripts/check_references.py`; missing references are a STOP. Use the reference guide throughout construction. Image references are concepts, not final Blender renders or stage acceptance.
- Use ONLY `bowling-blender52` tools. Read `RUNTIME_52.md`; capabilities must show `runtime_verified=true`, `actual_version="Blender 5.2.3 LTS"`, and root ending `var/bowling52-qwen36-mtp-q8-20261023`. If that connection is absent, STOP and request an OpenCode restart. Never substitute the disabled `z6-blender-worker`. Use `device="CPU"` for renders.
- Start a fresh run with an isolated empty scene, omitting `source_job`. For later stages, revise the previous completed same-host authoring job. Inspect the scene before and after changes.
- Fresh means **zero objects**: no default Cube, Camera, or Light exists to delete. Use `scene = bpy.context.scene` and `scene.unit_settings.system`, not `bpy.scene` or `scene.unit_system`. Omit `source_job` or use JSON null for a fresh scene; never send the string `"None"`.
- Author code runs with `__name__="__blender_author__"`. Execute stage functions with an unconditional top-level call; a `__main__`-only guard skips them. Fetch and read `scene.json` and `report.json`: `result.json.passed` means execution succeeded, not that stage requirements passed.
- Save each submitted authoring script under `artifacts/scripts/`. Record accepted job IDs and source IDs in `BUILD_STATUS.md` before polling. Poll existing jobs; never replay an uncertain submission.
- Worker Python runs inside `/job`, without access to Mac paths. Write extra outputs as flat files there, fetch verified artifacts, and record their actual paths. Use `blender_render` for CPU renders in this trial.
- Keep a hash-verified current checkpoint at `artifacts/blend/BowlingPair01.blend`. Update it after every passed stage, including later corrections. Deliver renders, reports, and exports at the specification paths.

## Durable progress and session handoff

- Immediately after each accepted submission, update **both** `BUILD_STATUS.md` and `HANDOFF.md` with the stage, job ID, source ID, and pending state **before polling**. The source remains the last verified completed scene, not the newest unverified job.
- After every terminal result, record PASS/FAIL/BLOCKED evidence, verified artifact paths/hashes, last verified source, and the exact next action in both files. Mark pending job `none` only once that job has been reconciled.
- Saving these checkpoints is part of finishing a stage: do it before beginning the next stage, reporting completion, or ending the session. Do not defer documentation until the full build finishes or a compaction warning appears.
- After compaction or in a new session, reread both checkpoints and rerun the consistency check. Poll a recorded pending job; otherwise inspect/resume the verified source. If artifacts exist but the ledger says NOT_STARTED, reconstruct progress from actual jobs/scenes/reports instead of submitting a new empty scene. Script filenames alone do not prove a stage passed.
- Run `python3 scripts/check_resume.py` after updating stage progress. This checks handoff consistency, not scene correctness; the normal measured acceptance checks still apply.
- Before compaction, ensure the current stage, accepted/pending IDs, verified source, artifact paths/hashes, measurements, failed checks and exact next action are on disk. A summary should preserve these pointers and reference-guide paths. After compaction, rerun both reference and resume checks before continuing; never restart from an empty scene or resubmit an uncertain job because older tool output was pruned.

## Diagnose and verify

- Python LSP is explicitly enabled with Blender 5.2 typing support; see `LSP_SETUP.md`. After writing/editing a saved authoring script, inspect its LSP diagnostics or run `.venv/bin/pyright artifacts/scripts/STAGE_FILE.py` before submitting it. Fix syntax and confirmed API/signature errors; verify generated-stub false positives against the actual worker API rather than guessing replacements. Do not label an entire diagnostic set false positives without checking each distinct API error.
- Local Python, image/GLB inspection, checksums, and other relevant diagnostic tools are permitted. Read-only supporting files outside the repository may be consulted when relevant; keep generated work in this repository.
- Ordinary errors may be diagnosed and repaired. The tools reject unchanged executable code against the same source after failure (comments/formatting are not changes). Three failed/cancelled submissions per source, or six across the trial, block further applicable submissions. Limits persist across MCP restarts. On ANY tool STOP, checkpoint and return BLOCKED immediately; do not keep calling the rejected tool. Never clear state or change source/queue to evade a limit. Read/status/diagnostics remain available.
- Failed CPU jobs are terminal: call `blender_job_diagnostics(job_id)` once for the traceback. Do not cycle through `artifact_fetch` filenames for a failed job; that endpoint only serves completed jobs. If diagnostics is missing from the tool catalog, report BLOCKED and request an OpenCode restart.
- Validate actual evaluated geometry, dimensions, transforms, hierarchy, materials, and triangle counts rather than intended parameters. Save machine-readable validation at `artifacts/reports/validation.json`.
- Validate reusable pin/ball exports and their pivots, the full pair, and static collision proxies independently. Use the same final revision for all deliveries. Do not build game code, simulation, or unrelated assets for this assignment.
- Inspect the rendered images and camera framing. File existence alone is not proof that a render shows the asset. If image viewing is unavailable, use geometric framing checks and report any remaining visual-review limitation.
- Revalidate affected stages after corrections. The delivered `.blend`, GLB, PNGs, and reports must correspond to the same final asset revision.
- Update `BUILD_STATUS.md` and `artifacts/reports/BUILD_REPORT.md` with objective PASS/FAIL/BLOCKED evidence. Mark COMPLETE only when every Stage 00–09 requirement passes; any failed required check means FAIL.

## Boundaries

- Preserve user-created content and `artifacts/archive/`. Historical artifacts are evidence, not starting assets for a fresh test.
- Keep Blender's X/Y ground plane and Z-up convention. Follow the specifications' asset-import restrictions.
- Keep Blender authoring/rendering on Z6. Image generation uses the coordinated EliteDesk WSL imageMCP worker; the reference review uses the installed Z6 vision model before the MTP coding phase. Do not release leases, change gateway ownership, or interrupt protected workloads.
- Ask before installing dependencies or making unrelated changes outside the project.
- Do not commit or push without explicit user approval.
- Do not edit the runtime wrapper, guard, configuration, tests or specifications during the asset evaluation. Those are operator-owned test infrastructure, not model repair targets. Do not use shell commands to bypass the MCP submission guard.

Keep chat updates concise; put detailed evidence in the project reports. Record the model actually used and any operator intervention so the evaluation remains attributable.
