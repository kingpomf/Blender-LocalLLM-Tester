# BowlingPair01 Agent Test

## Goal

Build a modular, game-ready bowling alley pair, `BowlingPair01`, using `spec/bowling-pair-01/00-CONTRACT.md` through `09-DELIVERY.md`. Include two lanes, twenty pins, three bowling balls, gutters, a shared ball return, and alley dressing. The specifications define acceptance; do not weaken them to obtain a pass. This is a fresh bowling assignment authorized by the operator; the kart trial is historical evidence only.

Start by reading `BUILD_STATUS.md`, `HANDOFF.md`, `WORKER_GUIDE.md`, and the specifications needed to plan the work. Run `python3 scripts/check_resume.py` before submitting work. If it flags stale/contradictory progress, reconcile the saved artifacts and accepted jobs before continuing; do not start over or delete them. You may inspect any relevant project files, consult Blender API documentation, use applicable skills, and ask clarification questions. Keep work focused on this asset.

**Current trial:** use one fresh 262,144-token session with project automatic
compaction and tool-output pruning disabled. Do not manually compact or change
those settings mid-run. If context is exhausted, save the checkpoints and report
that outcome; a new session is a separate trial, not uninterrupted continuation.

## Blender workflow

- Use `z6-blender-worker` for Blender operations. Check connectivity and `authoring.available=true` before submitting work.
- Start a fresh run with an isolated empty scene, omitting `source_job`. For later stages, revise the previous completed same-host authoring job. Inspect the scene before and after changes.
- Fresh means **zero objects**: no default Cube, Camera, or Light exists to delete. Use `scene = bpy.context.scene` and `scene.unit_settings.system`, not `bpy.scene` or `scene.unit_system`. Omit `source_job` or use JSON null for a fresh scene; never send the string `"None"`.
- Author code runs with `__name__="__blender_author__"`. Execute stage functions with an unconditional top-level call; a `__main__`-only guard skips them. Fetch and read `scene.json` and `report.json`: `result.json.passed` means execution succeeded, not that stage requirements passed.
- Save each submitted authoring script under `artifacts/scripts/`. Record accepted job IDs and source IDs in `BUILD_STATUS.md` before polling. Poll existing jobs; never replay an uncertain submission.
- Worker Python runs inside `/job`, without access to Mac paths. Write extra outputs as flat files there, fetch verified artifacts, and record their actual paths. Use `blender_render` for queued GPU renders.
- Keep a hash-verified current checkpoint at `artifacts/blend/BowlingPair01.blend`. Update it after every passed stage, including later corrections. Deliver renders, reports, and exports at the specification paths.

## Durable progress and session handoff

- Immediately after each accepted submission, update **both** `BUILD_STATUS.md` and `HANDOFF.md` with the stage, job ID, source ID, and pending state **before polling**. The source remains the last verified completed scene, not the newest unverified job.
- After every terminal result, record PASS/FAIL/BLOCKED evidence, verified artifact paths/hashes, last verified source, and the exact next action in both files. Mark pending job `none` only once that job has been reconciled.
- Saving these checkpoints is part of finishing a stage: do it before beginning the next stage, reporting completion, or ending the session. Do not defer documentation until the full build finishes or a compaction warning appears.
- After compaction or in a new session, reread both checkpoints and rerun the consistency check. Poll a recorded pending job; otherwise inspect/resume the verified source. If artifacts exist but the ledger says NOT_STARTED, reconstruct progress from actual jobs/scenes/reports instead of submitting a new empty scene. Script filenames alone do not prove a stage passed.
- Run `python3 scripts/check_resume.py` after updating stage progress. This checks handoff consistency, not scene correctness; the normal measured acceptance checks still apply.

## Diagnose and verify

- Python LSP is explicitly enabled with Blender 4.5 typing support; see `LSP_SETUP.md`. After writing/editing a saved authoring script, inspect its LSP diagnostics or run `.venv/bin/pyright artifacts/scripts/STAGE_FILE.py` before submitting it. Fix syntax and confirmed API/signature errors; verify generated-stub false positives against the actual worker API rather than guessing replacements.
- Local Python, image/GLB inspection, checksums, and other relevant diagnostic tools are permitted. Read-only supporting files outside the repository may be consulted when relevant; keep generated work in this repository.
- Ordinary API errors or failed checks may be diagnosed, fixed, and rechecked. Keep the stage FAIL until its checks pass; do not advance dependent stages with unresolved failures. After three unsuccessful repair attempts on the same issue, report the evidence and ask for help.
- Failed CPU jobs are terminal: call `blender_job_diagnostics(job_id)` once for the traceback. Do not cycle through `artifact_fetch` filenames for a failed job; that endpoint only serves completed jobs. If diagnostics is missing from the tool catalog, report BLOCKED and request an OpenCode restart.
- Validate actual evaluated geometry, dimensions, transforms, hierarchy, materials, and triangle counts rather than intended parameters. Save machine-readable validation at `artifacts/reports/validation.json`.
- Validate reusable pin/ball exports and their pivots, the full pair, and static collision proxies independently. Use the same final revision for all deliveries. Do not build game code, simulation, or unrelated assets for this assignment.
- Inspect the rendered images and camera framing. File existence alone is not proof that a render shows the asset. If image viewing is unavailable, use geometric framing checks and report any remaining visual-review limitation.
- Revalidate affected stages after corrections. The delivered `.blend`, GLB, PNGs, and reports must correspond to the same final asset revision.
- Update `BUILD_STATUS.md` and `artifacts/reports/BUILD_REPORT.md` with objective PASS/FAIL/BLOCKED evidence. Mark COMPLETE only when every Stage 00–09 requirement passes; any failed required check means FAIL.

## Boundaries

- Preserve user-created content and `artifacts/archive/`. Historical artifacts are evidence, not starting assets for a fresh test.
- Keep Blender's X/Y ground plane and Z-up convention. Follow the specifications' asset-import restrictions.
- Keep the workflow on Z6. Do not release leases, change gateway ownership, or interrupt protected workloads.
- Ask before installing dependencies or making unrelated changes outside the project.
- Do not commit or push without explicit user approval.

Keep chat updates concise; put detailed evidence in the project reports. Record the model actually used and any operator intervention so the evaluation remains attributable.
