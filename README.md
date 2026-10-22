# Blender LocalLLM Tester

An isolated test of whether an agent can build one low-poly go-kart from measurable requirements: a Blender scene, GLB export, four review PNGs, and validation evidence.

## Current state: active attempt requires reconciliation

The 100K attempt reached claimed Stage 07/08 work but has unsupported render/validation passes and contradictory ledger/handoff metadata. Its active files are preserved. Read `SESSION_REVIEW_2026-10-22.md` before resuming; the 256K context upgrade does not certify, repair, or reset this asset. Historical attempts remain under `artifacts/archive/`.

Agent instructions now allow project-wide inspection, Blender documentation, local diagnostic scripts, clarification questions, and bounded repair/revalidation. Unfamiliar shell commands request confirmation rather than being denied outright. Asset specifications are unchanged.

## Run the next test

1. Quit and restart OpenCode in this directory to load the updated configuration.
2. Start a **new session** so the next agent does not inherit the previous run's conversation or loaded instructions.
3. Select the model/agent you want to evaluate. The default is `z6-llama/qwen38-blender-35b` — Qwen3.8 35B A3B Blender v1 with a 262,144-token native context. This project does not restrict providers to `z6-llama`.
4. Confirm `z6-blender-worker` connects with `opencode mcp list` and exposes `blender_job_diagnostics`. The installed diagnostics update requires a fresh MCP process.
5. Run `/kart-start` only after reconciling current progress. It reads `WORKER_GUIDE.md` and the handoff, runs the consistency preflight, and resumes a verified source; it must not create a new empty scene over an existing attempt.
6. Review `BUILD_STATUS.md`, `HANDOFF.md`, and the generated artifacts. On later sessions, `/kart-start` first runs the read-only resume check and reconciles existing work; it is not an unconditional reset. Completion requires every specification check to pass.

The project inherits provider credentials and remote worker settings from the machine's OpenCode configuration. Its Z6 MCP launcher sets `BLENDER_DOWNLOADS` to this repository's `artifacts/downloads/`. Update machine-local paths if moving the checkout.

The Blender specialist is installed with a verified **262,144-token** runtime context. See `MODEL_SETUP.md` for pinned weights, inference/tool-use checks, and the Blender 5.2-training versus 4.5-LTS-worker version distinction. Progress must be checkpointed after each accepted job and result, not only at the end of a session; this avoids depending on when automatic compaction occurs.

## Repository map

- `AGENTS.md` — short workflow, verification, and asset boundaries.
- `WORKER_GUIDE.md` — script entry points, explicit scene chaining, evidence files, local delivery, and rendering semantics.
- `MODEL_SETUP.md` — selected Blender specialist model, runtime context, and installation evidence.
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
