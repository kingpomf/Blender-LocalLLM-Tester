# Fresh bowling trial — Flash-Next on Z6, Blender5.2/CUDA on EliteDesk

## Current operator-authorized continuation

References are READY and the native Stage00 checkpoint is
`cf9e9c33d60a4f99ae69e149236e0acf`. Query blender_workflow_status before editing;
this current checkpoint supersedes the historical fresh-start description below.
The user increased native hard-failure limits fivefold:10 without a published
asset advance,30/source,100 total. Existing failures remain counted; no reset.
OpenCode MCP execution timeout is120 seconds in a fresh process.

Two diagnosed failures: initial fixed validation on the empty Stage00 scene raised
`ValueError: min() iterable argument is empty`; the first lane edit raised
`IndexError: bpy_prop_collection[index]: index168 out of range,size168`.
The slab's +Y wall repeated its -Y wall indices; mesh.validate removed duplicate
faces, leaving fewer polygons than material slots. Repair the actual boundary
indices and verify slots match real polygons. Use a changed lane script from the
completed Stage00 source. Do not replay the failed request, rerun unchanged empty
validation, weaken the validator, regenerate references or reset counters.
Inspect cached diagnostics via the workflow tools if more detail is needed.

## Original trial setup (historical)

The user authorized Qwen3.8 Flash-Next/Strata to attempt the bowling asset and
selected EliteDesk GPU rendering with the existing qualified Blender5.2.3 runtime.

- Model z6-llama/qwen38-flash-next,262144 context/32768 output,49152 compaction
  reserve,160-line/12000-byte tool output cap. No model/backend tuning change.
- Trial bowling52-flash-next-elitedesk-20261025-r1, clean linked worktree
  /Users/start/Development/Blender-Bowling-FlashNext. No starting asset or accepted
  stages. Generate fresh references, then author original Stage00 geometry.
- All Blender scene/checkpoint/job IDs stay on EliteDesk. CPU authoring and
  validation share its existing worker; renders use its serialized RTX3060 CUDA
  queue. The Z6 GPUs remain managed by Strata's existing gateway. Never release
  leases or mix Z6 CPU scene IDs with EliteDesk IDs.
- Local guard starts empty. Prior Turbo bowling and completed kart packages are
  preserved in their original checkouts. Their stage passes are not current proof.
- The installed API catalog and unchanged validator are tooling, not old assets.
  Small CPU-author/CUDA qualification fixtures are separate evidence, not this asset.

Apply AGENTS.md/specification exactly. Read compact scene_summary and paged
validation_details instead of whole JSON files. Poll the auto-validator after
every small criterion/object-group change. PinDeck_L/R and Pit_Catch are contract
names; confirm an object exists before declaring a rename/move successful. Decks
must cover full pin footprints, not just pin center coordinates. Preserve valid
geometry and avoid repeated no-op renames. Make real lane markings and materials.

API corrections remain soft; invalid geometry remains hard. Eight successive
validated asset revisions with identical remaining statuses/stage acceptance stop
authoring for diagnosis without charging a native error. Context-only failures
may reconcile accepted work and resume in a fresh context; uncertainty/transport
failures and genuine hard STOPs still halt. Never replay an accepted request.

Reference generation and CUDA renders share the EliteDesk GPU queue: wait on its
existing IDs, do not create extra GPU daemons or steal GPU work. Use named render
tools, fixed pixel review and selected export/reimport delivery. No inline render,
managed-state edits, validator weakening or manual PASS. Continue only with
measured progress. Monitor via scripts/run_bowling.py --status; no duplicate launch.
