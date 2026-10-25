# Reviewed API/accounting repair and authorized zero-counter continuation

The user authorized reviewing/fixing API checks and hard/soft accounting, archiving
and resetting active failures to zero, committing/pushing, and another detached run.
Use bowling-coder / Qwen3.6 with the same Blender5.2.3 LTS CPU-only queue.

Start with blender_workflow_status and blender_api_lookup. The verified asset
source remains **2b37b77ce016462c943a217f67fb9418**. Do not start empty or use any
failed revision. Stage00–03 remain verified; other acceptance is still incomplete.

## Correct the actual problem with one small edit

`Object.children` is a **tuple**, not an editable collection. Never call
`root.children.unlink(obj)`. For reparenting use `obj.parent`; for deleting an
object use `bpy.data.objects.remove(obj, do_unlink=True)`. Save any mesh reference
before deletion; only remove the saved mesh after its users count is zero. Do not
access removed objects or delete their data first.

The installed API catalog now includes real return types for Object.children,
children_recursive and users_collection. Look up unfamiliar APIs and keep edits
small: **one failed acceptance criterion or one object group per revision**, then
poll automatic validation and compare measured results before another change.
The previous agent ignored small-edit instructions and submitted another broad
collision/geometry/camera rewrite. Do not replay that script. Preserve the valid
visual gutters and inspect the collision-only objects before modifying them.

## Accounting contract

- This authorized reset starts epoch3 with **0 hard failures,0 API corrections**
  and an empty active controller streak. All31 historical failed jobs and their
  fingerprints remain. The prior classifications are archived, not deleted.
- Confirmed missing Blender members/operators, unsupported declared keywords and
  source-proven misuse of Blender-returned tuples are recoverable API corrections.
  Preflight rejection submits no job. Runtime-confirmed API errors do not consume
  the hard budget; diagnostics and status use the same classification.
- Arbitrary Python tuple/dict errors, invalid/degenerate geometry, removed-object
  references and cancellations remain hard unless actual evidence proves an API
  mismatch. Current limits stay6/source20/total. Two distinct current hard failures
  without a new published asset edit stop the client.
- Status/diagnostics for pre-reset jobs do not recharge the new epoch or streak.
  Identical failed submissions are still blocked from replay. Make genuine changes.

The earlier image review is completed and negative, not permission-denied/stuck.
Automatic review reconciliation remains installed. Fix actual framing/occluders,
render changed real images and use the fixed review/validation/export tools.
Do not render inline, weaken validators, regenerate references, edit managed
ledgers/counters or claim acceptance from execution success. No shell/delegation.
Write delivery docs under artifacts/reports. Continue only with measured progress.
