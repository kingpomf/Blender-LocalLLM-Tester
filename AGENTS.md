# Local Blender Technician Contract

## Mission

Build exactly one asset, `Kart01`, by following the ordered files in `spec/kart-01/`. Operate Blender only through `blenderMCP`. This is a requirements-following and tool-use evaluation, not an open-ended art exercise.

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

Use Blender Python through BlenderMCP when it makes deterministic geometry or validation easier. Save reusable scripts under `artifacts/scripts/`; do not execute arbitrary code from outside this repository.

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

