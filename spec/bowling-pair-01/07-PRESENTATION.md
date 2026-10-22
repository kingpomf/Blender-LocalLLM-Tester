# Stage 07 — Presentation cameras and lighting

Create these cameras and render four genuinely distinct PNGs, each at least
1280×720, from the actual authored Blender scene:

| Camera | Local PNG | Required visible evidence |
| --- | --- | --- |
| CAM_BowlingPair01_Overview | artifacts/renders/BowlingPair01_overview.png | Full pair, both racks, approaches, seating, return and scoreboards |
| CAM_BowlingPair01_Player | artifacts/renders/BowlingPair01_player.png | From the left approach toward the left pins; lane markings, gutter depth and alley atmosphere |
| CAM_BowlingPair01_PinDeck | artifacts/renders/BowlingPair01_pindeck.png | Both complete ten-pin racks, red bands, decks and pits |
| CAM_BowlingPair01_Props | artifacts/renders/BowlingPair01_props.png | All three balls on the return; finger recesses clearly readable |

Use balanced alley lighting with readable silhouettes and nonblown-out polished
surfaces. Camera markers or separate render-only revisions may select views;
rendering four timeline frames without selecting four cameras is insufficient.
Use the worker render queue; do not substitute generated images or AI video.

Inspect the rendered images. With a text-only model, use available local image
inspection plus measured framing/occlusion checks; record the vision limitation
and any operator review still needed rather than claiming unseen visual approval.
The required geometric/framing checks must still pass. Presentation objects are
not children of the visual root and never enter GLB exports.
