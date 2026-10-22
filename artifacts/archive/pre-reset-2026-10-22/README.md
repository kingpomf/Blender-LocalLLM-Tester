# Blender LocalLLM Tester

An isolated, evidence-driven test of whether a local model can build a game-ready asset from staged Markdown requirements. The fresh run selects **Qwen3.8 27B Dense on the Z6**, with **Z6 Blender execution**.

The challenge remains one low-poly go-kart: a Blender file, GLB export, four review renders, and a validation report, without silently relaxing the specification.

## Current state: reset, ready for a fresh model run

The authoring upgrade and all three review repairs are installed and verified
on Z6. Topology inspection is accurate, supported texture dependencies survive
scene revisions, and deployment cleanup/rollback regressions pass. The review
hold is cleared. Details: `artifacts/reports/Z6_RESET.md`.

The previous checkpoint and `.blend` are preserved in `artifacts/archive/pre-z6-2026-10-21/`. All build stages have been reset; no old PASS is reused.

The upgraded Z6 worker now exposes `blender_scene_author` for general Blender Python. Custom meshes, collections/units, hierarchy, node materials, cameras/lights, native reopen, render/export and inspection were verified through real MCP jobs; a queued CUDA render also passed. The initial recovery state is cleared and the gateway is healthy. See `artifacts/reports/Z6_RESET.md`. The specifications have not been weakened, and no Kart01 build has been submitted.

## Start here

1. Keep the global OpenCode `z6-llama` provider and `z6-blender-worker` server configured. This project inherits the provider endpoint/credentials and remote worker configuration; it declares the local launcher so its download override is applied. Its machine-local `BLENDER_DOWNLOADS` places verified worker artifacts under this repository's `artifacts/downloads/` so checkpoints can be copied to the required delivery paths. Update those local paths if you move the checkout.
2. Quit and restart OpenCode in this repository to load the changed configuration.
3. Run `opencode mcp list` and confirm `z6-blender-worker` connects.
4. Run `/kart-start`. It checks the authoring capability and begins a fresh isolated Stage 00 scene.
5. Review `BUILD_STATUS.md` and `artifacts/` after each stage. The agent records remote job IDs and copies hash-verified artifacts into the required local checkpoint/delivery paths.

`z6-llama/qwen38-turbo` is an experimental configured alternative; Dense is the selected baseline. Do not run OpenCode `/init`; the repository already has a deliberate `AGENTS.md`.

## Repository map

- `AGENTS.md` — operating contract and Z6 compatibility gate.
- `opencode.json` — project-only model, MCP isolation, context, and permissions.
- `.opencode/commands/kart-start.md` — kickoff/resume command.
- `spec/kart-01/` — unchanged, ordered build requirements; read only the active stage.
- `BUILD_STATUS.md` — current checkpoint and test ledger.
- `artifacts/archive/` — preserved previous runs.
- `artifacts/` — generated assets, renders, reports, and scripts.

This is a capability test, not an Aiden Kart Racing production asset. Stop on failure and record objective evidence before resuming.
