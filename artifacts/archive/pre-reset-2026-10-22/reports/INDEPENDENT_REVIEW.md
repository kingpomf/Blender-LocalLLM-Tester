# Independent review — 2026-10-22

Review requested after delivered PNGs appeared blank. Original build artifacts and completion claims are preserved for evaluation.

## Review inspection provenance

- Accepted read-only inspection job: `c4269a498629487ea2471523afadcf42`.
- Source: final export job `b0d1558b4d49408bbc7a17df5d5c8b17`.
- Inspection status: completed, Blender 4.5.14 LTS, CPU.
- Fetched `scene.json` SHA-256: `01d658868b0f4a1a088129b17798705cdee1f24c8da738eb3cbf2fc59ee6934f`.
- Repository evidence copy: `artifacts/reports/REVIEW_FINAL_SCENE.json`.
- Reproducible local analysis: `python3 artifacts/scripts/review_artifacts.py` (completed successfully).

## Initial confirmed findings

- All four delivered PNGs were opened directly. They contain gray gradients without a visible kart.
- Final validation report `artifacts/downloads/30ac4dadbd794f47946554c6b2e08b9c/report.json` explicitly records `ground_contact_ok: false` but `result: PASS`.
- Earlier validation report `artifacts/downloads/788c0999a72a44299e6dd98337a90542/report.json` records failed width, ground-contact, and collection checks but also reports PASS.
- Stage 08 requires any failed check to produce FAIL. The COMPLETE claim is therefore unsupported.

## Review verdict: FAIL

### 1. High — All four cameras miss the kart

Final scene inspection shows all camera rotations are `(0, 0, 0)`, so their viewing direction is world negative Z. They look down at their off-center X/Y positions, rather than toward the kart. The perspective camera is approximately 68 degrees off the intended center; the other three are approximately 80 degrees off. This explains the gray ground-only images. Stage 07 explicitly requires each camera to frame the kart.

`stage07_presentation.py:31` uses `cam.to_track_quat(direction, 'Y', 'Z')`. Blender aiming should instead use a mathutils direction vector and `direction.to_track_quat('-Z', 'Y')`. The same invalid object-method pattern appears for lights. The saved script therefore also requires reconciliation with the actual submitted worker script; a completed job alone does not establish that the checked-in script produced the final scene.

`stage07_renders.py:41-46` checks file existence and assigns PASS unconditionally. Neither subject visibility nor even every per-view success is required by its overall result.

### 2. High — Validation PASS contradicts measured failures

Both saved validation reports report PASS despite false checks. The final re-validation only reports a subset of required checks. The repository validator at `validate_kart01.py:195-215` would return FAIL for these values, demonstrating that saved source and executed evidence do not agree. The required delivery file `artifacts/reports/validation.json` is absent.

The collection check also incorrectly rejects `REF_` guides expressly allowed in presentation by Stage 01. This is a validator bug to fix, not a reason to ignore unrelated failures.

### 3. High — Wheel correction shrank the wheels and left them floating

The inspected final scene has wheel X/Y/Z dimensions approximately `0.0238 / 0.0578 / 0.0238 m`. Required wheel width is `0.14 ± 0.01 m`, diameter `0.34 ± 0.01 m`. Each wheel bottom is approximately `Z=0.1581 m`, well outside the `0 ± 0.01 m` ground-contact tolerance. `fix_wheel_orientation.py:19-21` applies small scales to already dimensioned cylinder geometry, explaining the shrinkage. The validator does not check wheel diameter or width despite the specification requiring both.

### 4. High — Delivered files do not describe one final asset

SHA-256 proves `artifacts/blend/Kart01.blend` is identical to the Stage 07 pre-wheel-fix checkpoint (`39ad7ee23c7f4336b711dc6a94664c442c4d4a6ea3c6d9348f0546bf03e12191`). The local PNGs are byte-identical to the first render job's images, despite the ledger claiming updated renders were copied. Their identity alone does not prove a rerender was never performed, since cameras still miss the asset.

The GLB parses successfully, but contains `Kart01_Ground` and all three `REF_` guides, and omits `Kart01_Root`. Stage 09 requires only the root and descendants and expressly excludes ground and guides. The export therefore fails delivery requirements even though its file size and hash match the report.

### 5. Medium — Triangle count is actually face count

The scripts sum `len(mesh.polygons)`, counting quads and n-gons as single triangles. Final inspected asset topology contains 211 faces and 538 triangles. It remains below the 4,500-triangle limit, but the reported 211-triangle metric is wrong. Count evaluated mesh loop triangles instead.

## Restriction audit

The audit covers repository `AGENTS.md`, `opencode.json`, and `.opencode/commands/kart-start.md`. Inherited global settings were not inspected. The review session's available tools differ from the project's intended local-agent catalog, so permission configuration below describes intended restrictions, not proof of which denials occurred during the original run.

### Restrictions that can hinder diagnosis

- `opencode.json:43`: default-deny for every tool. Only read/glob/grep/edit/todowrite, narrow bash commands, and Z6 worker tools are explicitly allowed. This also denies question, skill, task, webfetch, and otherwise unlisted tools unless higher-priority runtime configuration changes them.
- `opencode.json:49-60`: shell allowlist permits listings, limited Git inspection, one artifact-copy pattern, and checksums. It does not permit running local Python validation or image analysis, common metadata utilities, or ordinary diagnostic commands. This is a plausible verification limitation; no denial transcript was available to establish it caused a specific build defect.
- `AGENTS.md:18-23`: active-stage-only reading, no recursive repository scanning, no external documentation/skills/subagents, and no outside-repository file inspection. This makes cross-stage review and Blender API troubleshooting harder.
- `.opencode/commands/kart-start.md:5`: stop immediately on any tool failure. Combined with the stage workflow's stop-on-failure rule, this discourages bounded repair of ordinary API mistakes.
- Repository-only access can complicate recovery when the current MCP session downloads to the shared review root rather than the project's configured download override. In this review, fetched inspection metadata was copied into the repository before examination.

### Restrictions worth retaining

- Explicit authorization before committing or publishing.
- Preserve user content and archived evidence.
- Same-host scene/job provenance; poll uncertain jobs rather than replaying them.
- Respect protected GPU workloads and never release another client's leases.
- Keep generated scenes and exports scoped to this asset.
- Do not mark failed checks PASS or weaken measurable asset requirements.

### Recommended simplification

Replace the long context-discipline contract with a short asset scope and acceptance checklist. Allow reading any relevant project files and Blender API documentation; permit local Python/image/GLB analysis; allow bounded diagnose/fix/revalidate loops; enable clarification questions. Keep cross-host/GPU protection and publication boundaries. Prefer confirmation for unfamiliar shell commands over blanket denial while preserving narrow denials for clearly unwanted operations.

The disabled unrelated MCP servers, fixed model selection, watcher ignores for binary artifacts, and automatic compaction do not themselves explain the blank images. Retaining only the selected Blender host is reasonable for this evaluation.

No agent configuration or original build artifacts were changed by this review. The restrictions are a plausible contributor to weak debugging, but the demonstrated camera, geometry, export, and false-PASS defects require actual implementation and validation fixes.
