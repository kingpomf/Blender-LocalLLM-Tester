# Authorized resumed work after operator pin correction and counter reset

The user authorized a concrete pin correction, checkpoint reconciliation,
zeroing active failures and launching the detached continuation. This is an
explicitly assisted continuation in the same r2 trial, not a fresh unaided result.

## Verified starting point

- Model: **Qwen3.6 MoE**, z6-llama/qwen36-35b-a3b-mtp-q8, native262144 retuned.
- Scene source: **78c0eaf6afba483694c2ca2c6eec4472**.
- Canonical file: artifacts/blend/BowlingPair01.blend, SHA-256
  **0fce120fa532133520de7b69dcd3a8e2fbd2897ce74fd367aca5f25266801980**.
- Operator fixed profile radius/height order, nondegenerate cap topology, outward
  winding and two separate red neck bands. Native execution and independent
  validation confirm **Stages00,01,02,03 PASS**. Do not rebuild these stages.
- The unchanged old stage03_pins_v2.py is historical failed model code; its
  shared-mesh-deletion hypothesis was wrong. The applied correction is
  artifacts/scripts/stage03_pins_corrected.py, not an untested proposed fix.
- Failure accounting reset epoch1: **0 current errors**,6/source20/total available.
  All18 historical failed jobs and all prior successful/source identities remain.
  Duplicate failed code is still rejected. Do not perform another reset.
- Reference images and their visual design guide are already READY. Do not
  regenerate them. Earlier four beauty images are verified files but invalid/
  obstructed presentation evidence from an older scene.

## Remaining work (actual measured report)

Run **`python3 scripts/validation_summary.py`** for a compact failure list. Use
Read/Glob/Grep rather than denied shell grep/head/cat pipelines or subagents.

Stage04's balls exist and measured size/spacing/deep regions pass, but visible
grip evidence depends on Stage05 support/occlusion repairs and Stage07 rerendering.
Keep that dependency explicitly IN_PROGRESS while completing05–07; do not waste
attempts rewriting the corrected pin or ball APIs. After rerender, resolve actual
grip/label evidence and revalidate all required criteria.

Prioritize these measured issues:

1. **Stage05 floor/return/dressing:** AlleyFloor is a vertical slab about338m tall,
   not a floor. Inspect make_box axis order and dimensions; do not blindly scale
   already scaled vertex coordinates again. Return hood width and masking-wall
   clearance fail. Rack geometry intersects the balls rather than supporting them.
   Labels/opening evidence still needs actual inspection.
2. **Stage06 collision:** gutter proxies are shallow flat pieces/bridges, lane
   proxies are too wide, and collision meshes are visible to beauty renders.
   Preserve visual geometry while fixing/remeasuring collision placement.
3. **Stage07 framing:** existing images are blank or obstructed; file existence is
   not PASS. Correct huge occluders before camera/framing/occlusion work. Use the
   CPU render tool, not viewport rendering inside authoring. Obtain four useful
   views from the same final asset revision.
4. **Stages08–09:** run fixed read-only measured validation and image review;
   export and round-trip only after required criteria actually pass.

## Checkpoint and validation commands

After each completed real repair revision:

```sh
python3 scripts/checkpoint_bowling.py --source COMPLETED_JOB_ID
python3 scripts/validate_checkpoint.py --campaign UNIQUE_CAMPAIGN_ID
python3 scripts/checkpoint_bowling.py --sync-ledgers
python3 scripts/check_resume.py
```

Publish render artifacts with:

```sh
python3 scripts/checkpoint_bowling.py --render overview RENDER_JOB_ID --asset-source COMMON_ASSET_SOURCE
```

Repeat for player/pindeck/props. The helper checks bytes, lineage and saved mesh/
material descriptions. It does not approve visual content. Record actual hash-bound
visual review and qualitative evidence, never intended parameters or unconditional
true. Do not weaken the operator-reviewed validator to achieve a pass.

Checkpoints are deterministic; do not hand-insert duplicate stage rows. Use plain
permitted commands without2>&1, shell chains or directory-creation commands. The
directories already exist. Diagnose real API failures rather than dismissing all
Pyright errors as stub false positives. Keep all accepted IDs before polling.

## Execution

The user authorized the assistant to launch the prepared detach command. A fresh
Qwen3.6 coding session will start from the reconciled files to avoid the previous
session's stale diagnoses. Prior session IDs/events remain in history. Continue
automatically until delivery or a real STOP; never restart from an empty scene.

Monitoring:

```sh
python3 scripts/run_bowling.py --status
```

Live status includes current and historical failure counts separately. Limits
remain6/source20/total. New failures count normally; transport uncertainty and
unchanged failed submissions are never automatically replayed.
