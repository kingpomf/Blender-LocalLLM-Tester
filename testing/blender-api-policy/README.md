# Installed Blender API guidance and recoverable API corrections

## User-authorized behavior

The user requested an installed5.2 API whitelist/reference, assistance for the
smaller coding model, and self-correction without treating wrong APIs as hard
errors. Asset execution was paused during implementation; no budget reset was
requested. The subsequent commit/relaunch authorization is recorded under
testing/api-aware-relaunch/. The Qwen3.6 model/context configuration is unchanged.

## Actual runtime evidence

Read-only catalog job **4a43658f17b748429a92b399530e8d9d** inspected the installed
**Blender5.2.3 LTS** runtime: **4,011 RNA types,2,497 operators**, zero introspection
errors, plus datablock-collection members, BMesh operators/types and mathutils
members. It did not execute any operators or change scene datablocks. The asset
source remains **2b37b77ce016462c943a217f67fb9418**.

The full9,418,935-byte catalog and verified artifact receipt are local:
`artifacts/reports/blender-api-catalog.json` and
`artifacts/reports/blender-api-catalog-receipt.json`. They are ignored by Git and
edit-denied for the coding agent. `scripts/capture_blender_api.py` checkpoints the
accepted job and polls/reuses it; an uncertain submission is never replayed.

## Model-facing API reference

New MCP tool **blender_api_lookup(query)** supports:

- `Mesh`: supported members, RNA properties and function parameters.
- `Mesh.update`: exact availability and supported RNA parameters.
- `Mesh.calc_normals_use_fit_sharp`: confirmed absent, with close-name suggestions.
- `bpy.ops.mesh.primitive_cube_add`: operator keywords and parameter types.
- `bpy.data.meshes`, `mathutils.Vector`, or substring searches for discovery.

AGENTS.md and bowling-start instruct small validated edits and targeted API
queries instead of loading the entire catalog into the model's context.
Suggestions are discovery hints, not assertions that methods are equivalent.
Fresh OpenCode/MCP processes load the new tool/configuration; existing interactive
processes need a quit/restart. The API catalog is required for author admission.

## Preflight boundaries

The checker rejects absent operators, known typed members, datablock-collection
members, BMesh operator names, and unsupported explicit RNA keyword arguments.
It follows common imports/factory aliases, typed annotations, and explicit mesh/
camera/light data narrowing. Python helpers and unknown/polymorphic receiver
types are not rejected speculatively. Operator poll/get_rna_type remain valid.

This is deliberately **not a whitelist of every Python call**. Dynamic code,
operator context, enum values, arbitrary Python values, some collection element
types and geometry correctness cannot all be proven statically. Static admission
is not runtime or asset acceptance. Catalog fingerprints/runtime version are
verified; missing/tampered catalogs cannot silently disable the new checks.

## Error accounting and loop protection

- Static API mismatches: recoverable tool feedback, **zero native submissions**.
- Runtime errors: cache diagnostics once. Only a terminal AttributeError proving
  that a member of a known Blender type or an operator is absent from the actual
  catalog is classified as an API correction. Generic AttributeErrors/TypeErrors,
  geometry failures, removed-object references and cancellations remain hard.
- API corrections remain original failed attempt rows with original fingerprints;
  separate evidence records exclude them from hard budgets. Identical failed API
  requests receive recoverable guidance without replay. Changed code may proceed.
- The controller ignores confirmed API corrections for its two-hard-failure stop;
  retained streaks are filtered under the same policy on explicit restart, while
  old state is archived if reclassified. Genuine hard failures still stop it.
- No budget-reset row, attempt deletion, source change or validator weakening.

## Verification

**101 tests passed**; targeted Pyright **0 errors/warnings**. Coverage includes
unsupported members/operators/keywords, valid aliases and operator polling,
explicit type narrowing, unknown Python helpers, strict terminal-exception
classification, required catalog admission, controller hard-error exclusion,
durable audit/accounting and corrected-code admission with identical replay denied.

Fresh real MCP proof is in `mcp-acceptance.json`:
- New tool exposed and exact supported/unsupported API lookups verified.
- Actual failed submitted script rejected without any added attempt row.
- Prior job6a3c128b6ab54880b0f6449b85e2fab0 classified as recoverable API mismatch.
- Prior job82d3d39a52f34fce88177515528a1998 remains a hard geometry failure.
- Guard attempt rows and canonical asset source unchanged through qualification.
- Current epoch2: **3 hard failures +1 API correction**,30 historical failed jobs
  preserved, limits6/source20/total unchanged. No reset performed.

The API catalog capture itself was one successful operator-owned read-only native
job. The MCP policy qualification added no native jobs. No end-to-end completion
of a newly corrected asset has been claimed; geometry/presentation defects remain.
