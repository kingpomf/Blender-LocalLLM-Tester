# Latest validation/checkpoint reconciliation — 2026-10-24

User authorized repairing validation/checkpoints and increasing trial-wide failures
to20. The per-source limit remains6. No failure rows were deleted, new trial created
or asset geometry repaired. The controller remains stopped for user invocation.

## Recovered actual artifacts

All37 pre-audit jobs were reconciled against terminal remote state:25 completed,
12 failed. The common completed asset source is **6b947366ef42484291a8ee70a19c32e6**.
Its native checksum is **26ba8ed54bb6af9f9b9d0c8ce6007b459230491f09c5b0f81b7e2c52bcd10e07**;
the canonical checkpoint now contains that revision rather than the older pin scene.
The previous checkpoint and ledgers/controller/guard snapshot are preserved.

Four1280×720 PNGs were fetched by manifest and SHA-256 verified from completed
camera/render branches: overview acd151e9599448a4964426ff5b1f03be, player
5c9d98141f8748f585f3e7fd981b1060, pin-deck b61e77cd38b944e0b5c3f2f3c3dca0b9,
props b99e756159724e659b8735c24f26ea0b. Their camera revisions derive from the same
asset source. Original jobs/images are retained, not regenerated for this audit.

Actual visual review failed all four: overview is nearly featureless gray;
pin-deck is almost uniformly dark; player/props show large occluding surfaces.
File existence and successful render execution do not satisfy Stage07.

## Fixed validator and checkpoint workflow

- Replaced the crash-prone validation script with an explicitly read-only measured
  implementation. The original model script is preserved in
  reconciliation-v2-20261024/model-validation-before.tar and original session logs.
- Evaluated meshes are released on their **evaluated objects**, including finally
  blocks. Loop triangles are calculated before every count.
- Lane surface Z uses **world-space maximum Z**, not mesh thickness. All20 pin
  names/positions/dimensions/topology/material bands and all3 balls are measured.
- Recess depth/connected-region findings remain distinct from actual visible grip
  confirmation. Unresolved qualitative criteria are explicit, not hardcoded PASS.
- Checks include gutters/decks/pits, rack support, dressing bounds, material
  assignments, collision alignment/exclusion, camera framing and local render proof.
- A complete before/after fingerprint verifies mesh geometry, transforms, material
  assignments and hierarchy were unchanged by validation. Geometry FAIL does not
  crash the audit or consume a failed-job slot; it produces an honest failed report.
- Local verification fully decodes images, checks dimensions/hashes/same-asset
  provenance and records actual visual review. Four image files alone never PASS.
- `checkpoint_bowling.py` publishes manifest-verified native/render artifacts,
  retains old checkpoint versions, deduplicates metadata and produces exactly ten
  ordered stage rows. Both ledgers are synchronized from actual validation results.
- The continuation plan now binds current guard rows, scene checksum, validator
  checksum and measured report checksum. Old source/plan metadata is not reused.

## Native installed validation results

Final read-only job **32be847b02094a34a655f571cf1a9cba** completed successfully
against the saved source. It did not repair geometry. Combined measured report:
**312 PASS,63 FAIL,7 unresolved**. Earlier audit d2788f6b844b47d4bb25e5a8500891eb
is retained too; neither added a failed-job count.

| Stage | Reconciled result | Important findings |
|---|---|---|
|00|PASS|Metric foundation/root/collections/hierarchy checks pass.|
|01|PASS|Lane/approach extents and30 markings now satisfy measured checks.|
|02|FAIL|Inner gutters still extend onto playable lane regions rather than adjoining their correct outer side.|
|03|FAIL|Positions and basic dimensions improved, but the shared pin mesh still has24 boundary edges; red assignments do not form two separated neck bands.|
|04|UNRESOLVED|Three balls meet measured radius/spacing and have deep regions; actual visible socket/grip evidence is absent because props render is obstructed.|
|05|FAIL|AlleyFloor dimensions are approximately78×0.65×338m—a vertical slab, not a floor beneath the assembly. Return hood is1.0m wide, outside±0.40; rack geometry intersects the spherical exterior; masking-wall clearance fails. Label/opening evidence unresolved.|
|06|FAIL|Gutter collision proxies are flat shallow pieces, lane proxies are too wide, collision meshes remain render-visible. Static normals/pivot-documentation review remains unresolved.|
|07|FAIL|Framing checks fail and all four recovered images fail visual acceptance.|
|08|FAIL|Validation now executes and reports honest defects; asset acceptance is not complete.|
|09|NOT_STARTED|No qualified final export and round-trip delivery.|

The exact criteria/observations are in **artifacts/reports/validation.json**;
render hashes/review are in **artifacts/reports/render-manifest.json**. Inspect
these before changing geometry—do not treat this summary as replacement evidence.

## Continuation

Preserve measured Stage00/01 passes and the latest source. Repair02 onward and
revalidate dependent stages; do not repeat the already corrected ball API failure.
All12 failed jobs remain counted: **8 failures remain globally** and **4 on the
current source**, under6/source20/total. Use `/bowling-continue` after restarting
OpenCode or the explicit terminal command in CONTROLLED_CONTINUATION.md. This
operator reconciliation did not start the agent continuation.
