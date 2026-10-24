# Controlled continuation v2 — measured repair and validation handoff

**Prepared; not started.** The user invokes the continuation when ready.

```sh
python3 scripts/run_bowling.py --check-continuation
python3 scripts/run_bowling.py --resume --continuation --detach
```

Or fully restart OpenCode and invoke `/bowling-continue` once. Do not clear state,
restart the assignment or regenerate reference images.

## Fixed identities and retained history

- Agent: Qwen3.6 MoE, `z6-llama/qwen36-35b-a3b-mtp-q8`, retuned native256K.
- Same trial/guard: `bowling52-qwen36-mtp-q8-20261023-r2`.
- User-authorized limit: **6 failures/source,20 total**, with all12 historical
  failures retained. This is not20 extra attempts. At preparation the source has
  two failures, so4 remain there;8 remain across the trial.
- Starting source: **`6b947366ef42484291a8ee70a19c32e6`**, the last completed
  common asset revision before render-only camera branches. The validator jobs
  did not modify geometry and must not be used as budget-reset sources.
- Canonical file: `artifacts/blend/BowlingPair01.blend`, SHA-256
  `26ba8ed54bb6af9f9b9d0c8ce6007b459230491f09c5b0f81b7e2c52bcd10e07`.
- Reference phase READY. Four actual remote render files are now recovered into
  `artifacts/renders/`, with hashes/provenance and failed visibility reviews.

## First actions

1. Read both ledgers and **`testing/VALIDATION_RECONCILIATION_V2.md`**. Do not reuse
   the previous stage PASS narrative. Stage00/01 measure PASS; later stages have
   actual failures or unresolved evidence. Exports are not complete.
2. Run exact permitted commands without `2>&1`, shell loops or command chains:
   `python3 scripts/check_resume.py`, `python3 scripts/check_references.py`.
   Confirm fresh MCP capabilities show6/source20/total and12 failures retained.
3. Inspect the current native scene; repair earliest failures in order. Particularly
   inspect the inner gutters; pin bands/seam; the enormous vertical floor mesh;
   ball rack contact; return width/masking clearance; visible flat collision
   proxies; and obstructed cameras. Do not undo the successful lane/ball API repairs.
4. Use saved source revisions properly, retain per-source and global limits and
   run LSP/API diagnostics before submitting. Never dismiss all diagnostics as
   stub false positives or rename APIs without checking actual runtime support.

## Required checkpoint/validation tools

After each completed repair authoring job:

```sh
python3 scripts/checkpoint_bowling.py --source COMPLETED_JOB_ID
python3 scripts/validate_checkpoint.py --campaign UNIQUE_CAMPAIGN_ID
python3 scripts/checkpoint_bowling.py --sync-ledgers
python3 scripts/check_resume.py
```

These fixed tools fetch/verify native bytes, publish the canonical file, use
correct evaluated-object cleanup, count actual evaluated triangles, measure
world-space surfaces rather than thickness, and deterministically replace stage
tables and source metadata in both ledgers. They preserve previous checkpoint
bytes under `.runtime/checkpoint-history/`. Do not use brittle oldString guesses
or hand-insert duplicate REPAIRING rows. The validator is operator-reviewed;
repair the asset, not acceptance thresholds or checker code.

A validation job with `passed=false` still produces a completed measured report;
it is not a request to replay a crashed job. Read the failing IDs and fix their
geometry/evidence. Pending or uncertain requests must be reconciled, never repeated.
Reusing a validation campaign reuses its accepted completed job only when the
source and exact validator hash still match. Use a new campaign for a changed scene.

## Render publication and visual evidence

Fix actual asset/camera framing before rendering. Use the CPU render tool, not
`bpy.ops.render` inside authoring or a headless viewport/OpenGL render. After a
completed render-only camera revision:

```sh
python3 scripts/checkpoint_bowling.py --render overview RENDER_JOB_ID --asset-source COMMON_ASSET_SOURCE
```

Repeat with player/pindeck/props. The tool checks lineage, saved mesh/material
description, image hashes and minimum dimensions; it cannot visually approve the
picture. Inspect actual images and record `visual_review` in render-manifest.json,
including reviewer, matching sha256, observations and honest passed true/false.
All four renders must describe the same final asset geometry. Changed geometry
invalidates previous render/visual evidence, even if files still exist.

For qualitative requirements initially marked UNRESOLVED (grip openings, readable
labels, etc.), `artifacts/reports/qualitative-evidence.json` may record actual
image-derived review. It must name asset_source and criteria with id, reviewer,
observations≥80 chars, passed and render_sha256 tied to a verified current image.
Only unresolved criteria may be resolved by such evidence; geometry FAIL checks
cannot be overridden. Do not fabricate review from file existence or prompt intent.

After the required geometry and visual checks pass, complete Stage08, exports,
round-trip checks and Stage09 delivery. Failure limits and every genuine STOP
still apply. This is an assisted continuation, not a fresh unaided model result.
