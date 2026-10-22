# Blender LocalLLM Tester

## Current project: BowlingPair01

Have the local Blender agent build a modular bowling alley pair for a potential
future game: two full-length lanes, twenty pins, three distinct balls, four
gutters, approaches, pin decks/pits, a shared ball return, seating, overhead
scoreboards and an alley backdrop. The style is clean, readable, low/mid-poly
with polished wood, white/red pins and colorful balls.

This branch prepares the assignment. The bowling build is **NOT_STARTED**.
The local agent should create the geometry, renders and exports.

### Start the local agent

1. Open this checkout on branch `project/bowling-alley-pair`.
2. Quit and restart OpenCode, then start a **new session** to load the bowling instructions and command.
3. Select the intended model; default: `z6-llama/qwen38-blender-35b` (256K).
4. Confirm `z6-blender-worker` connects and provides authoring and job diagnostics.
5. Run **`/bowling-start`**. It checks saved progress and works through Stages 00–09.
6. Review `BUILD_STATUS.md`, `HANDOFF.md`, the validation report and rendered views.

Keep this trial in one session with automatic compaction/pruning off. If context
is exhausted, save the checkpoint and record the outcome. Python LSP/stubs remain
enabled; see `LSP_SETUP.md`. Credentials and worker settings are inherited from
the machine configuration. The MCP download directory is local to this checkout.

### Acceptance and delivery

`spec/bowling-pair-01/00-CONTRACT.md` through `09-DELIVERY.md` are the source of
truth. Deliver an editable `.blend`, full-pair GLB, standalone pin and ball GLBs,
static collision GLB, four review PNGs, measured JSON validation, game-integration
notes and a SHA-256 artifact manifest. Requirements include real scale, useful
pivots, separated movable props, material portability and an export round trip.
Game logic and a playable simulation are outside this asset-building assignment.

### Repository map

- `AGENTS.md` — active bowling workflow and boundaries.
- `.opencode/commands/bowling-start.md` — current kickoff/resume command.
- `spec/bowling-pair-01/` — ten staged bowling specifications.
- `BUILD_STATUS.md`, `HANDOFF.md` — active job/source ledger and next action.
- `WORKER_GUIDE.md` — scene chaining, diagnostics, rendering and delivery semantics.
- `scripts/check_resume.py` — read-only progress consistency preflight.
- `artifacts/{blend,exports,renders,downloads,reports,scripts}/` — active bowling outputs.
- `MODEL_SETUP.md`, `LSP_SETUP.md` — retained model/tooling setup evidence.
- `spec/kart-01/`, `SESSION_REVIEW_2026-10-22.md`, `artifacts/archive/` — historical kart work.

The most recent kart work was preserved verbatim under
`artifacts/archive/kart256k-before-bowling-2026-10-22/`, including local native
assets and a hash manifest. Ignored native/job files remain local; Git is not a
complete binary backup. Historical PASS claims have not been revalidated here.
Use `/bowling-start`; `/kart-start` is retained only as a guarded historical entry.
Do not run `/init`; the repository supplies its own instructions.
