# Blender LocalLLM Tester

An isolated test of whether an agent can build one low-poly go-kart from measurable requirements: a Blender scene, GLB export, four review PNGs, and validation evidence.

## Current state: 256K attempt with Python LSP assistance

An active attempt is preserved in the ledger/handoff and generated artifacts.
Pyright and Blender 4.5 type stubs were enabled after the operator observed the
export script's repeated syntax failures. This is an LSP-assisted continuation;
the existing asset and reported stage results have not been repaired or certified
by enabling the checker. Prior archives remain under `artifacts/archive/`.

For this trial, project automatic compaction and tool-output pruning are **off**.
Do not manually compact. A context-limit stop should be recorded as an outcome,
not worked around by summarizing. The operator subsequently enabled local Python
LSP/stub assistance; record that tooling intervention when comparing test runs.
See `LSP_SETUP.md` for the installed versions, verification, and checker commands.

Agent instructions now allow project-wide inspection, Blender documentation, local diagnostic scripts, clarification questions, and bounded repair/revalidation. Unfamiliar shell commands request confirmation rather than being denied outright. Asset specifications are unchanged.

## Run the next test

1. Quit and restart OpenCode in this directory to load the updated configuration.
2. Start a **new session** so the next agent does not inherit the previous run's conversation or loaded instructions.
3. Select the model/agent you want to evaluate. The default is `z6-llama/qwen38-blender-35b` — Qwen3.8 35B A3B Blender v1 with a 262,144-token native context. This project does not restrict providers to `z6-llama`.
4. Confirm `z6-blender-worker` connects with `opencode mcp list` and exposes `blender_job_diagnostics`. The installed diagnostics update requires a fresh MCP process.
5. Resume the existing checkpoint using `/kart-start` and reconcile its ledger/handoff. Start Stage 00 from a new empty scene only after an explicitly authorized reset. Keep progress recorded without waiting for the end of the run.
6. Review `BUILD_STATUS.md`, `HANDOFF.md`, and the generated artifacts. On later sessions, `/kart-start` first runs the read-only resume check and reconciles existing work; it is not an unconditional reset. Completion requires every specification check to pass.

The project inherits provider credentials and remote worker settings from the machine's OpenCode configuration. Its Z6 MCP launcher sets `BLENDER_DOWNLOADS` to this repository's `artifacts/downloads/`. Update machine-local paths if moving the checkout.

The Blender specialist is installed with a verified **262,144-token** runtime context. See `MODEL_SETUP.md` for pinned weights, inference/tool-use checks, and the Blender 5.2-training versus 4.5-LTS-worker version distinction. Progress must be checkpointed after each accepted job and result, not only at the end of a session; this avoids depending on when automatic compaction occurs.

## Repository map

- `AGENTS.md` — short workflow, verification, and asset boundaries.
- `WORKER_GUIDE.md` — script entry points, explicit scene chaining, evidence files, local delivery, and rendering semantics.
- `MODEL_SETUP.md` — selected Blender specialist model, runtime context, and installation evidence.
- `LSP_SETUP.md` — enabled Pyright server, Blender type stubs, checker commands, and known typing limitations.
- `SESSION_REVIEW_2026-10-22.md` — measured failure causes in the stuck 100K attempt; not a repaired asset or validation PASS.
- `opencode.json` — default model, selected Blender host, and tool permissions.
- `.opencode/commands/kart-start.md` — kickoff/resume command.
- `spec/kart-01/` — unchanged asset requirements, Stages 00–09.
- `BUILD_STATUS.md` — current run's stage ledger and job provenance.
- `HANDOFF.md` — compact pending-job/source/next-action checkpoint for session and compaction handoffs.
- `scripts/check_resume.py` — read-only stale-progress preflight; run with `python3 scripts/check_resume.py`.
- `artifacts/{blend,exports,renders,downloads,reports,scripts}/` — current run's work; scripts also retains the model-discovery utility.
- `artifacts/archive/` — preserved previous runs and review evidence.

This is a capability test, not a production racing-game asset. Do not run `/init`; the repository already supplies its instructions.
