# Blender LocalLLM Tester — BowlingPair01

Test the selected local LLM against **Blender 5.2.3 LTS** with matching
5.2 typing stubs, measured asset specifications and enforced retry limits.
The selected coding model is **Qwen3.6 35B A3B MTP UD-Q8_K_XL (256K)**.
The current run has been reconciled after twelve failed jobs. Its latest completed
scene, four actual renders and reference images are preserved. Measured Stage00/01
checks pass; later stages need repair or unresolved evidence. The fixed validator
now completes without changing geometry. Limits are6/source and20/total, with all
prior failures counted—8 remain globally and4 on the current source at preparation.

## Current controlled continuation — operator starts it

Read `CONTROLLED_CONTINUATION.md` and `testing/BALL_GENERATION_DIAGNOSTICS.md`.
The continuation is prepared but stopped. From this project directory:

```sh
python3 scripts/run_bowling.py --check-continuation
python3 scripts/run_bowling.py --resume --continuation --detach
```

Alternatively restart OpenCode and invoke **`/bowling-continue`**. This validates
the known checkpoint and guard history, then supplies the explicit diagnostic
handoff to the existing Qwen3.6 session. It does not reset the trial or regenerate
references. Status remains available with `python3 scripts/run_bowling.py --status`.

## Fresh-run entry point (only after a separately authorized reset)

1. Fully quit/restart OpenCode in this repository on `project/bowling-alley-pair`.
2. Open a **new Qwen3.6 MoE session** and run **`/bowling-run` once**. Launcher,
   reference planner and coding sessions all select Qwen3.6. Image inspection is
   a fixed helper tool, not a Qwen3.8 agent session.
3. Confirm **bowling-blender52** is connected; the old **z6-blender-worker** is disabled.
4. The coding phase completes/resumes **all remaining stages00–09** continuously,
   checkpointing between them. It compacts when needed; no “next stage” prompts.
5. If the tool reports STOP, review the blocker before continuing. Do not reset
   the guard or blindly rerun. Review final renders, reports and exports.

The former60-step cap is removed. Unchanged failed scripts are
rejected; six failures per source or twenty total exhaust the durable budget.
Automatic compaction/pruning are enabled with a16,384-token reserve within the
native262,144-token coding context. See `RUNTIME_52.md`
for runtime identity, qualification evidence, operator recovery and limitations.
Rendering is CPU-only, on the same 5.2 runtime as authoring.

Status: `python3 scripts/run_bowling.py --status`. Controller logs/session IDs
live in `.runtime/autonomous-run/`. A terminal launch also works:
`python3 scripts/run_bowling.py`. After a genuine interruption/blocker is reconciled,
explicitly use `--resume` (and `--detach` for background operation). The controller
allows two diagnostic repair turns for ordinary startup/validation problems,
then stops rather than looping; it never resets the guard. `/bowling-references` and
`/bowling-start` remain available as individual phase commands.

## Assignment

Build two adjacent lanes with approaches, markings, four gutters, decks and pits;
twenty independently movable pins; three balls with real recessed finger holes;
shared ball return, seating, scoreboards and alley dressing. Follow the ten
files under `spec/bowling-pair-01/`. No implementation is supplied to the model.

Deliver an editable Blender scene, assembled visual GLB, standalone pin and three
ball GLBs, static collision GLB, four PNGs, measured validation, integration notes
and a SHA-256 manifest. Lane/fixture objects stay separate within the full-pair
export. Game logic and playable simulation are outside the assignment.

## Files

- `AGENTS.md`, `.opencode/commands/bowling-start.md` — active workflow.
- `BUILD_STATUS.md`, `HANDOFF.md` — current trial ledger and next action.
- `WORKER_GUIDE.md`, `RUNTIME_52.md`, `LSP_SETUP.md` — tool usage and evidence.
- `scripts/blender52_mcp.py`, `scripts/submission_guard.py` — scoped MCP and circuit breaker.
- `scripts/preflight_blender52.py` — actual runtime/config preflight with no build job.
- `scripts/check_resume.py` — read-only ledger consistency check.
- `REFERENCE_IMAGES.md`, `scripts/check_references.py` — imageMCP-first workflow and enforced authoring prerequisite.
- `testing/blender52-guarded/` — separate runtime/guard qualification evidence.
- `artifacts/{references,blend,exports,renders,downloads,reports,scripts}/` — fresh model outputs.
- `artifacts/archive/nemotron-final-before-qwen36-2026-10-23/` — previous Nemotron trial, original ledger, native artifacts and guard state.
- `.runtime/blender52/` — ignored, durable tool-owned guard state. Do not clear it mid-trial.
- `artifacts/archive/bowling-loop-2026-10-22/` — preserved failed run and pre-reset tooling.
- `artifacts/archive/blender52-specialist-final-2026-10-23/` — final old-model 5.2 attempt and exhausted guard before the Nemotron reset.
- `spec/kart-01/`, older archives and session reviews — historical evidence only.

The previous looping run used 4.5.14, despite its ledger saying 5.2, and submitted
identical failed code 33 times. Its PASS claims are not this trial's evidence.
Do not run `/init`; this repository already provides its instructions.
