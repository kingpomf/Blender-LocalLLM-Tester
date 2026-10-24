# BowlingPair01 — enforced Qwen3.6 asset workflow

Build the original modular two-lane bowling asset defined by all ten files under
`spec/bowling-pair-01/`. Specifications are acceptance requirements, not suggestions.
No external mesh packs or unrelated game code. Preserve original artifacts/history.

## Agent, runtime and authority

- Coding agent/model: **bowling-coder / z6-llama/qwen36-35b-a3b-mtp-q8**, retuned
  native262144 context. Compaction/pruning enabled,16K reserve, no step cap.
- Use **bowling-blender52** only: Blender5.2.3 LTS, CPU rendering, same r2 queue
  `var/bowling52-qwen36-mtp-q8-20261023-r2`. Check actual capabilities.
- References are already READY; use their design guide. Qwen3.6 stays the agent;
  fixed pixel-only helpers may use the installed vision model. Do not regenerate
  references or switch primary models.
- **blender_workflow_status is authoritative** for current source, pending IDs,
  budget and measured stage results. A previous narrative/compaction summary or
  a completed job is never sufficient proof of stage acceptance.

## Required tool flow

1. Read workflow_status, CONTROLLED_CONTINUATION.md and the relevant specifications.
2. Save changed geometry/camera Python in artifacts/scripts; use LSP diagnostics.
   Fix confirmed APIs instead of declaring every diagnostic a false positive.
3. blender_scene_author edits scene only. Functions execute with
   `__name__='__blender_author__'`; call them unconditionally and assign report.
   The current source is selected/checked automatically. Do not start empty once
   an authored scene exists. Use bpy.context.scene, metric units, X/Y ground,Z up.
4. Authoring preflight rejects inline rendering, output subdirectories and common
   unsupported APIs before submission. Follow recoverable repair guidance; no
   attempt is consumed. Flat extra outputs belong directly under /job.
5. Poll every accepted job. Completed edits automatically save a hash-verified
   canonical native checkpoint and queue fixed read-only validation. Poll the
   returned validation ID; stage ledgers update from its actual measurements.
6. Use blender_render_view for each of overview/player/pindeck/props; poll the
   returned view- ID. It selects cameras, queues one CPU render and publishes the
   verified image. Do not render inline or build your own output directory.
7. Write ASSET_GUIDE.md, then use blender_review_presentation and poll its review-
   ID for actual image-derived evidence. Blank/obscured images must fail. Do not
   claim this text-only agent saw pixels or replace renders with imageMCP images.
8. Refresh blender_validate. Use blender_export_delivery for fixed selected GLB
   exports and measured reimports. Write BUILD_REPORT/ASSET_GUIDE, then call
   blender_finish_delivery; only verified complete deliverables set COMPLETE.

## Managed state and recovery

- No shell or delegation tools in this coding agent. Critical operations have MCP
  tools, not Bash recipes. Use Read/Glob/Grep/Edit/LSP for asset source work.
- Do not edit BUILD_STATUS, HANDOFF, managed report/receipt JSON, runtime/guard,
  validation code, specifications or OpenCode config. Their mirrors are tool-owned
  and refreshed from verified evidence. Do not handwrite PASS or source metadata.
- Continue stages automatically. Dependency-blocked grip visibility may remain
  unresolved while you repair return/camera prerequisites, then revalidate it.
- After compaction, re-query machine state; do not trust stale remembered IDs.
  Never replay uncertain submissions, rename failed code as a repair, or use a
  failed/camera job as an asset source. Native execution and measured acceptance
  are distinct. Read diagnostics once after a failed job and repair the actual cause.
- Limits:6 failed/cancelled jobs per source and20 per current accounting epoch.
  Only the operator can authorize resets; historical fingerprints/attempts remain.
  A real STOP/exhausted budget/uncertainty requires BLOCKED, not another rejected call.
- Do not release coding leases, change GPU ownership, interrupt unrelated workloads,
  install dependencies, commit or push from the asset evaluation.

Keep updates concise. Preserve source and artifacts; no empty rebuild or unrelated
work. Report objective failures/unresolved evidence honestly rather than weakening
acceptance. This is an explicitly operator-assisted continuation.
