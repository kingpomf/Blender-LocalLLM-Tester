# Blender LocalLLM Tester

An isolated test of whether an agent can build one low-poly go-kart from measurable requirements: a Blender scene, GLB export, four review PNGs, and validation evidence.

## Current state: reset and ready for a fresh test

All build stages are NOT_STARTED and active output directories are empty. The interrupted Defiant Fable attempt is preserved under `artifacts/archive/defiant-fable-2026-10-22/`, including its diagnosis and historical job IDs. Previous work and its independent review remain under `artifacts/archive/pre-reset-2026-10-22/`; the earlier archive is also retained. No historical scene or PASS is reused.

Agent instructions now allow project-wide inspection, Blender documentation, local diagnostic scripts, clarification questions, and bounded repair/revalidation. Unfamiliar shell commands request confirmation rather than being denied outright. Asset specifications are unchanged.

## Run the next test

1. Quit and restart OpenCode in this directory to load the updated configuration.
2. Start a **new session** so the next agent does not inherit the previous run's conversation or loaded instructions.
3. Select the model/agent you want to evaluate. The default remains `z6-llama/qwen38-27b`; this project no longer restricts providers to `z6-llama`.
4. Confirm `z6-blender-worker` connects with `opencode mcp list`.
5. Run `/kart-start`. The agent should read `WORKER_GUIDE.md`, record the actual model used, and start a new empty isolated Stage 00 scene.
6. Review `BUILD_STATUS.md` and the generated artifacts. Completion requires every specification check to pass.

The project inherits provider credentials and remote worker settings from the machine's OpenCode configuration. Its Z6 MCP launcher sets `BLENDER_DOWNLOADS` to this repository's `artifacts/downloads/`. Update machine-local paths if moving the checkout.

## Repository map

- `AGENTS.md` — short workflow, verification, and asset boundaries.
- `WORKER_GUIDE.md` — script entry points, explicit scene chaining, evidence files, local delivery, and rendering semantics.
- `opencode.json` — default model, selected Blender host, and tool permissions.
- `.opencode/commands/kart-start.md` — kickoff/resume command.
- `spec/kart-01/` — unchanged asset requirements, Stages 00–09.
- `BUILD_STATUS.md` — current run's stage ledger and job provenance.
- `artifacts/{blend,exports,renders,downloads,reports,scripts}/` — current run's work; scripts also retains the model-discovery utility.
- `artifacts/archive/` — preserved previous runs and review evidence.

This is a capability test, not a production racing-game asset. Do not run `/init`; the repository already supplies its instructions.
