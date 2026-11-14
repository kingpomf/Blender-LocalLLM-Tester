# BowlingPair01 Build Report

## Summary

BowlingPair01 was completed in Blender 5.2.3 LTS through the bowling-blender52 MCP workflow. The final measured validation passes all required stages:

- Stage 00: PASS
- Stage 01: PASS
- Stage 02: PASS
- Stage 03: PASS
- Stage 04: PASS
- Stage 05: PASS
- Stage 06: PASS
- Stage 07: PASS

Final validation job: `28609257a4d1406ba1c1445c449adfee`
Final validation report SHA-256: `5a186e56c870d1c885ff15bf1cd8ab7311531da26116fa92d4c1e447e782c72a`

## Final source and checkpoint

Current accepted source job: `17ade96359e8480cbe0472d26e87e495`

Native scene checkpoint:

- Path: `artifacts/blend/BowlingPair01.blend`
- SHA-256: `2aa9f9e56f838e30ccc5ae74ee98ecbfc6ba9860c6c1796a6e59f1656dadbc2f`
- Bytes: `209857`

The checkpoint contains the two-lane pair, gutters, decks, pit, pins, balls, return rack, dressing, screens, labels, collision proxies, cameras, and lights.

## Export and round-trip evidence

The fixed delivery export job `262114a05e1445eea3280b70b5ea9b6b` completed with measured round-trip pass.

Exported GLB files:

- `artifacts/exports/BowlingPair01.glb`
  - SHA-256: `d8e9140ef8cbbc863969882e79ebe828ceae50acb5975e296cb7a6db44282931`
- `artifacts/exports/BowlingPin01.glb`
  - SHA-256: `f88a7cade2937a2cd6eae1f5d72da44daa8f84eb1927a63cc2046262d3627fbe`
- `artifacts/exports/BowlingBall01.glb`
  - SHA-256: `cf8418b72ac6c9a6b0752ca689691228a5fd747ca81c4a9a0bd6f98195411bed`
- `artifacts/exports/BowlingBall02.glb`
  - SHA-256: `f5ecc095efdb20b4e7a1b0507388cb2fabf496ab6493cb2a7b4fa179a49eae4a`
- `artifacts/exports/BowlingBall03.glb`
  - SHA-256: `d9ca4b289f8b1c332a505e41fcd01eac9d8a5b55fcfbaf42304f4d6ea105ac35`
- `artifacts/exports/BowlingPair01_Collision.glb`
  - SHA-256: `1bbc8defa3e96f7b71755c7569a66f6e2d33b79e37196489dcc6c09e5b81be32`

The round-trip path is tool-owned and measured. The report does not claim gameplay physics or engine runtime validation.

## Renders and visual review

Four required Blender renders were produced from the final source through queued CUDA render views:

- `overview`: render job `gpu-603d20aa750345cdaa56408c9dcb1691`, view job `view-03668dfbd96c4ff8918531015bcd4063`
- `player`: render job `gpu-047857c754754ea8b7f3b3e830e64609`, view job `view-9483f5f0e4eb4de0b537adf18b619b5f`
- `pindeck`: render job `gpu-480e1a79642242cbac23fac50284b2c5`, view job `view-04ba507a5acc43b4bdfcdb9956fcb731`
- `props`: render job `gpu-84a24949173f4e558c08557f37feee9a`, view job `view-424d16cad9814315b36ea4f2a27592b7`

Final fixed presentation review: `review-74642b17abf146979110773ecd7792e8`

The review reported that overview, player, pindeck, and props views pass. The helper observed visible grip sockets on all three balls, readable scoreboard and masking labels, return opening visibility, and acceptable normals/static-origin facts.

## Geometry and naming decisions

Key accepted decisions:

- Lane markings use validator names `ArrowTri_L/R`, `Dot_L/R`, and `Foul_L/R`.
- Gutters, divider, rails, decks, and pit use Stage 02 required names and bounds.
- Pins are twenty separate objects named `Pin_L_01` through `Pin_L_10` and `Pin_R_01` through `Pin_R_10`.
- Balls are three separate objects named `Ball_01`, `Ball_02`, and `Ball_03`.
- The return rack, benches, screens, score grids, lane digits, masking digits, and masking wall are present as intended visual assets.
- Collision-only proxies are limited to `BP01_COLLISION` and hidden from render.
- Presentation cameras are `CAM_BowlingPair01_Overview`, `CAM_BowlingPair01_Player`, `CAM_BowlingPair01_PinDeck`, and `CAM_BowlingPair01_Props`.

## Interventions and hard failures

This continuation required several corrections:

- Fixed lane marking geometry and validator-required names after initial lane failures.
- Fixed gutter/deck/pit acceptance after measured failures.
- Fixed pin geometry and pin loop-index reporting bug.
- Fixed collision proxy membership and render visibility.
- Fixed camera orientation: Blender cameras view along local `-Z`, so `to_track_quat('-Z', 'Y')` was required for correct frustum containment.
- Fixed ball visibility: an initial boolean attempt produced degenerate faces and was rejected. The final accepted ball revision used valid non-Boolean recessed grip geometry and rotated the grips toward the props camera.

The final guard state reported:

- Hard failures: 10
- API correction count: 1
- Historical failed count: 11
- Per-source hard limit: 30
- Total hard limit: 100

No budget was bypassed, reset, or reinterpreted. No stage was manually marked PASS.

## Limitations

- The primary coding model did not directly view image attachments; visual evidence came from the fixed pixel/geometry helper.
- Gameplay behavior, pin dynamics, ball physics, and engine collision response are not tested.
- Collision GLB is static-proxy data only. Dynamic pin/ball colliders are recommended but not proven.
- The asset is geometry and presentation validated, not a complete game system.
