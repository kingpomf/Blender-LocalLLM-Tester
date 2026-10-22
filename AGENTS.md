# Local Blender Technician Contract

## Mission

Build exactly one asset, `Kart01`, by following the ordered files in `spec/kart-01/`. The fresh Z6 run selects `z6-llama/qwen38-27b` and operates Blender only through `z6-blender-worker`. This is a requirements-following and tool-use evaluation, not an open-ended art exercise.

## Z6 compatibility gate

- Check `BUILD_STATUS.md` and `blender_capabilities` before submitting work. Require `authoring.available=true` and `blender_scene_author` in the current tool catalog. The Z6 authoring extension was installed and verified on 2026-10-21.
- `blender_scene_author(code, source_job?)` supports general Blender Python in the isolated CPU job. Omit the source for a new empty Stage 00 scene; use the previous completed same-host CPU job ID for later stages. It auto-saves `scene.blend` and `scene.json`. Set `report` to JSON-compatible stage evidence and use assertions for required checks.
- Use source revisions to set custom cameras, collection membership, units, hierarchy, mesh geometry, and materials. For queued GPU rendering call `blender_render` explicitly; do not try to access GPUs or the gateway from authoring code.
- If `RECOVERY_REQUIRED` recurs, require operator reconciliation before GPU work. Do not release leases or change gateway ownership.
- Use same-host job IDs throughout. Poll accepted jobs; never replay an uncertain submission. Fetch verified artifacts and record their actual local paths and provenance.
- The archived scene under `artifacts/archive/` belongs to the previous run; do not resume or overwrite it.

## Context discipline

- At session start, read only this file, `BUILD_STATUS.md`, and `spec/kart-01/00-CONTRACT.md`.
- Determine the next incomplete stage from `BUILD_STATUS.md`.
- Read only that stage file plus any file it explicitly names.
- Do not recursively scan the repository or preload every specification.
- Do not use web search, external documentation, unrelated MCP servers, skills, or subagents.
- Do not inspect or modify files outside this repository.

## Required workflow

For each numbered stage:

1. Inspect the current Blender scene before changing it.
2. Compare the scene with the stage's measurable requirements.
3. Make only the focused changes needed for that stage.
4. Re-inspect object names, transforms, dimensions, hierarchy, and materials relevant to that stage.
5. Save `artifacts/blend/Kart01.blend`.
6. Update `BUILD_STATUS.md` with PASS, FAIL, or BLOCKED and objective evidence.
7. Stop on failure or uncertainty. Never mark a stage complete based only on appearance.

Save reusable authoring scripts under `artifacts/scripts/` before submitting their contents to `blender_scene_author`. The worker executes the submitted copy inside `/job`; it cannot see Mac filesystem paths. Do not execute arbitrary code from outside this repository.

## Remote artifacts and local checkpoints

- Record each accepted job ID and its source ID in `BUILD_STATUS.md` immediately, before polling, so interruption cannot lose the resume identity.
- Fetch completed artifacts with `blender_artifact_fetch`. This project's download root is `artifacts/downloads/`; each job gets its own subdirectory.
- Copy verified `artifacts/downloads/JOB_ID/scene.blend` to `artifacts/blend/Kart01.blend` after each passed stage, using the permitted repository-local `cp` command. Verify the destination SHA-256 with `shasum -a 256` against the manifest. Keep the immutable remote source job ID for resuming and re-inspecting.
- Similarly copy verified exports/renders/reports into the exact specification paths under `artifacts/`. Write custom worker outputs as flat files in `/job`, then fetch them. Use authoring Python for GLB export selection/hierarchy when the simple mesh-only export tool is insufficient.
- Local artifact copies are delivery bookkeeping, not Blender operations. Do not copy archived assets into the fresh run or mark a stage passed without its required evidence.

## Hard boundaries

- Preserve Blender's X/Y ground plane and Z-up convention.
- Work only in the isolated `Kart01` scene/file.
- Do not import downloaded assets or textures.
- Do not delete unrelated scene content unless `00-CONTRACT.md` explicitly authorizes initial cleanup.
- Do not change a requirement to make the build pass.
- Do not push Git commits. A commit may be created only after the user explicitly approves it.
- Do not claim completion until every item in `08-VALIDATION.md` passes and `09-DELIVERY.md` is complete.

## Output discipline

Keep chat responses brief. Put detailed evidence in `BUILD_STATUS.md` and `artifacts/reports/BUILD_REPORT.md`. Report the current stage, result, produced files, failed checks, and exact next action.
