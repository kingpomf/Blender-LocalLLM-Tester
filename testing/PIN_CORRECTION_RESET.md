# Applied pin correction, checkpoint reconciliation and authorized budget reset

## What was actually wrong

The failed pin lathe supplied `(radius,height)` tuples but unpacked them as
`for z,r in profile`. Its first ring therefore had radius0, generating coincident
ring vertices and zero-area cap triangles. Copying/renaming that mesh could not
repair the geometry. The last explanation blaming automatic shared-mesh deletion
was not established by the diagnostics. Earlier attempts also accessed removed
objects and used object/datablock values in string-only membership checks.

## Concrete operator assistance applied

`artifacts/scripts/stage03_pins_corrected.py` explicitly uses radius,height,
nonzero-radius rings, correctly wound independent cap centers, safe object-only
replacement and two separate red neck bands. It verifies all face areas, manifold
edges, positive volume, all20 actual pin dimensions and rack positions.

Completed native correction: **78c0eaf6afba483694c2ca2c6eec4472**, based on the
completed gutter repair **e8630f4b79ba468ebd18ef53e2f1d51d**. Native report and
independent read-only validation **2e5c733a50d847bf8dd74e9f48aa6116** confirm
**Stages00–03 PASS**. Each corrected pin is0.381m tall,0.121m in maximum diameter,
1056 triangles, with zero nonmanifold edges and separate red intervals
0.270–0.276m /0.288–0.294m. This is explicitly assisted model evaluation.

Canonical checkpoint SHA-256:
**0fce120fa532133520de7b69dcd3a8e2fbd2897ce74fd367aca5f25266801980**.

## User-requested zero error count

The user explicitly authorized zeroing current failures and starting detached work.
Before reset, every48 accepted job was checked against terminal remote status.
Original controller/ledgers/checkpoint, bad pin script and full SQLite backup are
preserved in **testing/pin-correction-reset-20261024/**.

Reset epoch1 records cutoff row48. It does **not** delete or rewrite an attempt:
all18 historical failures, all successful sources and all duplicate fingerprints
remain. Only failures accepted after that reset count against the current6/source,
20-total budget. Identical previously failed code remains blocked, uncertainty
remains blocked, and an empty-scene restart remains blocked.

The corrected-pin and validation jobs both completed without error, so current
failures remain **0**, with the full6/source20/total budget available. This approval
is operator-only; it does not grant the agent a counter-reset capability.

## Remaining work and launch

Current measured report:365 PASS,22 FAIL,7 unresolved. The unresolved ball-grip
evidence depends on fixing Stage05's vertical floor slab, rack/return and Stage07
camera occlusion. Collision proxies also require repair; final exports remain.
Use `python3 scripts/validation_summary.py` rather than shell pipelines to inspect
actual failure IDs. Preserve the solved foundation/lane/gutter/pin stages.

The detached launch uses a **fresh Qwen3.6 coding session** with this checkpoint and
handoff, avoiding stale earlier-session diagnoses. Old session IDs/events stay in
history. Automatic progression/compaction, persistent duplicate protection and
the existing real STOP behavior remain. Do not submit extra concurrent work from
the phone/launcher session. Monitor `python3 scripts/run_bowling.py --status`.
