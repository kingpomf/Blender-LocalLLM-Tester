# Blender local-model evaluation — fresh Qwen3.8 Turbo trial

Current checkpoint-bound continuation and context-recovery/error-reset evidence:
`testing/context-recovery-reset-20261025/`. The active asset/references are retained;
the initial clean-trial reset below is historical. Read CONTROLLED_CONTINUATION.md
and inspect status before launching; an existing state requires explicit authorized
resume rather than a duplicate fresh controller.

Build the original modular BowlingPair01 two-lane asset defined under
spec/bowling-pair-01/. The user requested a clean project restart using
**z6-llama/qwen38-turbo** after retiring the previous Qwen3.6 evaluation.

## Run

From the project directory:

```bash
python3 scripts/run_bowling.py --detach
python3 scripts/run_bowling.py --status
```

The controller first generates fresh design references, then launches a separate
fresh asset-coding session and continues stages automatically with measured
checkpoints. Do not launch a duplicate. Explicit resume requires reconciliation
of any interruption/blocker and preservation of pending accepted IDs.

## Current setup

- Primary model: qwen38-turbo;139264 context/16384 output, automatic compaction.
- Isolated trial: bowling52-qwen38-turbo-20261025-r1.
- Blender5.2.3 LTS on Z6; CPU-only authoring/render queue.
- Installed API lookup, source-linked soft API corrections, strict geometry and
  acceptance validation, queued named renders and fixed image-review helpers.
- Fresh asset/reference/state/guard/session history. All prior work preserved at
  artifacts/archive/qwen36-final-before-qwen38-turbo-20261025/.

See AGENTS.md, CONTROLLED_CONTINUATION.md, REFERENCE_IMAGES.md and MODEL_SETUP.md.
BUILD_STATUS.md/HANDOFF.md reflect measured active progress, not historical PASSs.
Native execution success is not asset acceptance. Do not weaken the validator,
invent image evidence, replay uncertain submissions or reset budgets automatically.

Verification:
`/Users/start/Development/blender-new-llm-setup/.venv/bin/python -m unittest discover -s tests`
and `scripts/preflight_blender52.py` through that environment. Current reset and
launch evidence is under testing/qwen38-turbo-fresh-20261025/.
