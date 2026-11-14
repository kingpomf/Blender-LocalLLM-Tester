# BowlingPair01 — DESIGN_GUIDE (trial bowling52-flash-next-elitedesk-20261025-r1)

Planner: z6-llama/qwen38-flash-next. Pixel observations supplied by the fixed
image-only helper (`scripts/review_reference_images.py`, reviewer
`z6-llama/qwen38-27b`, hash-bound in `vision-helper.json`). Concepts were
generated with imageMCP on EliteDesk (model `qwen-image-2.1-q4`, 512x512,
25 steps, seeds 41001/41002/41003). These are design inputs only; the written
specification values override anything visible in the images, and the concepts
are never evidence for a Blender render.

## image 1 — overview — `image-c2505b9c9fb4649614ce5ce38a034f6020be04a2422024e12a8d52a4ea3c464a.png`

Job `edimg-29f0a8afdbb04cbe95d60cfce1e69d77`, seed 41001. Helper observed a wide
high-angle view of two parallel light-wood lanes with dark side gutters and a
central divider, plus dark scoring consoles/overhead structures at the far end.

Useful construction features:
- Three-quarter framing from behind the approaches matches the required
  CAM overview composition; both racks, approaches, return and scoreboards read
  as one cohesive module.
- Warm wood lane surfaces with lengthwise board grain, dark recessed gutters and
  a lighter divider cap give the material palette: oiled wood, charcoal gutter,
  teal/dark accent panels.
- Overhead scoreboard housings and rear masking wall confirm the vertical
  silhouette (screen bottoms well above head height).

Corrections against the specs:
- The helper reads "two ball return trays holding white pins": in the concept
  the pins appear associated with the return/deck area ambiguously. Actual
  build must place twenty racked pins on the pin decks (head pin Y=18.288,
  0.3048 m spacing) and keep balls, not pins, on the return rack.
- Perspective hides true proportions; do not derive any measurement from this
  image. Lane width 1.0668 m, centers ±0.95 m and pair envelope X=±1.80 m come
  only from 01-LANES.

## image 2 — layout — `image-fd8cf33bbadf4598dd051c1d8f17c78a15a106e1c319cd31d33e61f0e62b4c65.png`

Job `edimg-2404a901d5ad41df8cfcacc32f35b419`, seed 41002. Helper observed a
top-down symmetrical lane geometry, a prominent central mechanical track
running between the lanes, pin clusters near the far lane ends and dark
rectangular panels along the top edge.

Useful construction features:
- Confirms the plan arrangement we must build: two parallel lanes, four gutters
  with a capped central divider, decks and recessed pits beyond Y=19.20,
  benches and floor fields, rear wall panels.
- The grid-like symmetry supports a mirrored, modular construction approach
  (one lane kit mirrored/reused for the second) with shared central elements.

Corrections against the specs:
- The "central mechanical track between the lanes" is wrong for this asset: the
  shared ball-return hood/rack must sit between the two *approaches*
  (X=-0.40..0.40, Y=-4.30..-0.30, per 05-ALLEY-DRESSING), while the space
  between the lanes is only the capped inner-gutter divider. Do not build a
  machinery trench between the lanes.
- Dark top-edge panels are generic; actual masking wall must carry readable
  `01`/`02` lane IDs with >=0.60 m clearance above standing pin tops.
- Image spacing is not to scale; rack geometry must use the exact triangular
  rows (1/2/3/4, row separation sqrt(3)/2 x 0.3048 m).

## image 3 — details — `image-0381f4c687a190f007109b67de877859e9f2b722326efa2fb09ddf13c3998ab8.png`

Job `edimg-6df4618278fe4608a80efd3b140e0df7`, seed 41003. Helper observed glossy
white pins with red double stripes in a triangular rack on a wooden surface,
with blue/red/green balls in a dark return area behind and a black tray edge in
the foreground.

Useful construction features:
- Pin silhouette to imitate: flat base, broad lower belly, narrow neck, rounded
  head, two red neck bands — matching 03-PINS. Bands sit on the neck and stay
  attached to the body.
- Ball color identity (blue, burgundy/red, green/teal) and glossy polished
  finish match 04-BALLS; balls resting in return cradles is the required final
  placement.
- Dark return mouth and lane/gutter material contrast support the Stage 06
  material list (white pin, red stripe, three ball colors, wood, gutter/metal).

Corrections against the specs:
- The visible finger-hole arrangement is not verifiable at this angle; actual
  balls need three genuinely recessed holes (>=0.015 m deep open/socket
  geometry) with the grip oriented toward the props camera.
- The rack shown is partial/ambiguous; delivery requires twenty distinct pin
  objects with the standard numbered rack and each pin one mesh object.
- Pin/ball proportions in the image are stylized; enforce 0.381 m pin height,
  0.121 m pin diameter, 0.216 m ball diameter from the specs.

## Shared construction takeaways

- Cohesive stylized-realistic low/mid-poly kit: warm wood surfaces, charcoal
  concave gutters, dark accent walls, three saturated ball colors, white/red
  pins. All must survive GLB export as Principled PBR material assignments.
- Composition: pair open at front and one side for review cameras; dressing
  elements (benches, scoreboards, masking wall, stripes/light bars) frame the
  pair without obstructing lane surfaces.
- Concepts are inputs only: all counts, dimensions, budgets and acceptance
  criteria come from spec/bowling-pair-01/; the four Stage 07 PNGs from the
  real Blender scene remain the only visual evidence for the asset.
