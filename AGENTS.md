# BowlingPair01 — fresh Qwen3.8 Turbo trial

Build the original modular two-lane bowling asset defined by all ten files under
spec/bowling-pair-01/. Specifications are acceptance requirements. No mesh packs,
old trial assets or unrelated game code. The previous trial is archived.

## Selected model and scope

- Primary planner/coder: **z6-llama/qwen38-turbo**,139264 context/16384 output.
  Automatic compaction/pruning,32768 reserve, no configured step cap. Tool outputs
  are capped at160 lines/12000 bytes to leave context headroom.
- Trial: **bowling52-qwen38-turbo-20261025-r1**. Use only bowling-blender52:
  Blender5.2.3 LTS, CPU rendering, its new isolated trial queue.
- Start from **no scene and no accepted stages**. New references come first, then
  a fresh Stage00 scene. Do not reuse the archived native file, meshes or scripts.
- Keep the selected primary model. Fixed pixel-only helpers may use the installed
  vision model; they supply evidence, not asset code. Never release coding leases.

## Phases

1. Reference planner (build/Qwen3.8 Turbo): follow REFERENCE_IMAGES.md. Generate
   three fresh imageMCP concepts on EliteDesk, save accepted IDs/receipts, use the
   fixed pixel helper and write DESIGN_GUIDE.md. Only reference-phase metadata may
   be updated directly. Run fixed reference/resume checks. No Blender jobs yet.
2. Coding agent (bowling-coder/Qwen3.8 Turbo): **no Bash or Task tools**. Read
   CONTROLLED_CONTINUATION.md and call blender_workflow_status before editing.
   Use current machine state after compaction; remembered summaries are not proof.

## Required coding flow

- Consult **blender_api_lookup** before unfamiliar APIs; query an exact type,
  member or operator. The catalog comes from the actual installed5.2.3 runtime.
  Do not load the full large catalog into context. Follow confirmed LSP diagnostics.
- Use **blender_scene_summary** for up to6 exact object names and
  **blender_validation_details** for selected stages/check IDs. Follow next_offset
  for a small next page. Never load whole scene/validation JSON files into context.
- Save code in artifacts/scripts. Make **one criterion/object-group change per
  revision**, submit blender_scene_author and poll the accepted ID. The first
  authoring starts empty; every later edit uses the current completed asset source.
- Authoring entry functions must execute unconditionally under
  __name__='__blender_author__'. Assign a JSON-compatible report. Use
  bpy.context.scene, metric units, X/Y ground and Z up.
- Completed edits automatically publish the verified native checkpoint and queue
  fixed read-only validation. Poll validation_job and correct actual measured
  failures. Execution success or a self-reported passed flag is not acceptance.
- Configure cameras/lights in authoring, then use blender_render_view for
  overview/player/pindeck/props and poll its view- ID. Never render inline or
  create output directories; extra author artifacts are flat /job files.
- Write artifacts/reports/ASSET_GUIDE.md, then use blender_review_presentation.
  Poll review- IDs. Actual images must show the required objects. Short criterion
  observations stay unresolved; never fabricate evidence or substitute generated
  concepts for real Blender renders. Review reconciliation is automatic.
- Refresh blender_validate. After current acceptance passes, use the fixed
  blender_export_delivery/reimport path, write BUILD_REPORT.md and ASSET_GUIDE.md,
  then blender_finish_delivery. Only verified complete delivery sets COMPLETE.

## Lessons that must be applied

- Object.children/users_collection are tuples, not editable collections. Use
  obj.parent for parenting or bpy.data.objects.remove(obj, do_unlink=True) to
  delete. Save mesh data first and remove it only after the object and only if
  data.users is zero. Never access a removed object or delete its data first.
- Profile sampling must contain each endpoint **once**. Repeating a final curve
  endpoint creates zero-area faces. Check every face area and valid connectivity;
  worker rejection of degenerate geometry is a real hard failure.
- Choose local coordinates plus object transform consistently. Do not encode a
  gutter center in its vertices and add the same center again as object location.
  Keep collision-only objects in BP01_COLLISION, not the scene root collection.
- Correct actual normals/topology with supported APIs; similarly named methods
  are not necessarily equivalent. Never invent Mesh methods or weaken validation.
- Verify camera orientation and actual pixels; walls/ceilings can obscure a view
  even if a camera exists. Small previews and measured framing beat broad rewrites.

## State, errors and recovery

- Coding ledgers, receipts, validators, configuration and runtime are tool-owned.
  Do not edit them, mark stages PASS manually or change counters. Ordinary asset
  scripts and delivery documentation are editable; source snapshots are immutable.
- Static API/preflight feedback is recoverable with no native submission. A
  runtime mismatch is soft only with installed API evidence and, for builtin
  return types, accepted-source/traceback proof. Correct code and continue.
- Soft API errors remain audited but do not count toward hard budgets or the
  two-hard-failure streak. Identical failed requests are never replayed. Arbitrary
  Python mistakes, geometry failures, cancellations and uncertainty remain hard.
- Limits6 hard failures/source20 total. Two current hard failures without a new
  published asset edit stop the client. Never bypass a STOP or reset counters.
  Read cached diagnostics and fix the cause; failed jobs never become sources.
- Old trial history stays archived. A reset requires explicit operator authority.
  A confirmed context-only overflow may automatically reconcile pending accepted
  IDs and verify the checkpoint before continuing in a fresh coding session. It
  does not reset counters or replay jobs; uncertainty/transport errors still stop.
  Continue automatically while making verified progress; checkpoint after each
  edit, use the same accepted IDs, and never launch a duplicate worker or commit/
  push from the asset agent. Report real blockers and unresolved evidence honestly.
