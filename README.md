# Blender LocalLLM Tester

An isolated, evidence-driven test of whether `gemma4-agent:26b` can use BlenderMCP to build a game-ready asset from staged Markdown requirements.

The first challenge is one deliberately simple low-poly go-kart. The test is successful only when the agent produces the Blender file, GLB export, four review renders, and a validation report without silently relaxing the specification.

## Start here

1. Open Blender and connect the BlenderMCP add-on.
2. From this repository, run `opencode mcp list` and confirm `blenderMCP connected`.
3. Confirm your global OpenCode config already defines the `ollama` provider and `gemma4-agent:26b`. The repository deliberately does not publish machine-specific host addresses or filesystem paths.
4. Confirm `uvx` is available on your shell `PATH` with `command -v uvx`.
5. Start OpenCode in this repository. The project config selects `ollama/gemma4-agent:26b`, enables only Ollama, and exposes only BlenderMCP plus minimal local file/git operations.
6. Run `/kart-start` in OpenCode.
7. Review `BUILD_STATUS.md` and the evidence under `artifacts/` after every stage.

Do not run OpenCode `/init`; this repository already contains a deliberate `AGENTS.md`.

## Repository map

- `AGENTS.md` — always-loaded operating contract.
- `opencode.json` — project-only model, MCP, context, and permission configuration.
- `.opencode/commands/kart-start.md` — short kickoff command.
- `spec/kart-01/` — ordered build requirements; only the active stage should be read in detail.
- `BUILD_STATUS.md` — durable checkpoint and test ledger.
- `artifacts/` — generated `.blend`, `.glb`, renders, reports, and scripts.

## Design intent

This is a capability test, not an Aiden Kart Racing production asset. Keep it isolated and disposable. If a stage fails, stop there, record evidence, and resume from that checkpoint after the requirement or workflow is corrected.
