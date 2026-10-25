---
description: Complete remaining asset work using enforced MCP state, validation and render queues
agent: bowling-coder
model: z6-llama/qwen36-35b-a3b-mtp-q8
---

Continue BowlingPair01 from **blender_workflow_status**, the authoritative source
and measured results. Read AGENTS.md, CONTROLLED_CONTINUATION.md and the relevant
specifications. Do not assume a previous compaction summary's PASS claims are true.

Your job is asset design/geometry and documentation. Shell/delegation tools are
disabled. Do not edit BUILD_STATUS.md, HANDOFF.md, managed JSON receipts, validator,
guards, specifications or runtime state; the MCP workflow manages them.

1. Call blender_workflow_status and capabilities. Use its current source.
   Before unfamiliar API use, query blender_api_lookup with an exact type/member
   or operator. Keep edits small and validate one change before expanding scope.
2. Save a changed authoring script under artifacts/scripts and inspect LSP
   diagnostics. Call blender_scene_author for geometry, materials, lights/cameras
   only. Never call bpy.ops.render in authoring or create output directories.
3. Poll the accepted native ID. Completion automatically publishes the checkpoint
   and queues a fixed validator. Poll the returned validation_job ID; actual
   failures/unresolved checks—not your own report's passed flag—determine progress.
4. Correct the concrete remaining geometry findings. Recoverable preflight,
   stale-source and pending-work responses consume no attempt; follow their
   next_tool/ID guidance rather than stopping or resubmitting accepted work.
   Confirmed API errors are recoverable: consult blender_api_lookup, change the
   code and continue. They do not consume the hard-error budget. Never replay an
   identical failed request or assume a suggested similarly named API is equivalent.
5. For presentation call blender_render_view(role), one role at a time. Poll its
   **view- ID**, which drives camera selection, queued CPU rendering and verified
   publication. Do not call render operators yourself. Use8 samples initially.
6. Write ASSET_GUIDE.md with measured axes/pivots/materials/import notes before
   blender_review_presentation. That fixed helper reads actual pixels and guide/
   geometry evidence; poll its **review- ID**. It is not another coding agent.
7. Call blender_validate to refresh local evidence after review. When current
   acceptance passes, call blender_export_delivery and poll it for fixed selected
   GLBs and actual reimports. Write substantive BUILD_REPORT.md and ASSET_GUIDE.md,
   then blender_finish_delivery verifies bytes/provenance and alone sets COMPLETE.

Continue successively through delivery; checkpointing is automatic. Compaction is
enabled: afterward reread workflow_status and files, not old guessed source IDs.
On a real STOP, circuit breaker, uncertain submission or explicit operator stop,
return BLOCKED. Never clear budgets, change sources to evade limits, weaken checks
or repeat an unchanged failed request. Do not commit/push from the asset agent.

Explicit operator handoff, when supplied:
$ARGUMENTS
