# Blender LocalLLM Tester — simplified kart

This branch tests an agent constructing a low-poly kart with supplied primitive helpers, independent numeric validation, and a fixed presentation rig. The agent still designs and authors the kart. No complete kart generator is supplied.

## Start when other testing has stopped

Use a clean checkout of `project/kart-simplified`, restart OpenCode, start a new session, select your model, and run `/kart-start`. Do not switch a checkout with an active agent or uncommitted outputs. This is a branch of the same repository, not a separate repository.

Read `AGENTS.md`, `spec/KART_SIMPLIFIED.md`, and `WORKER_GUIDE.md`. Existing `spec/kart-01/` files and historical reviews are legacy evidence, not the active challenge on this branch. The three active phases are BUILD, REVIEW, DELIVER.

`RUN_STATE.json` is the sole authoritative progress record. `BUILD_STATUS.md` and `HANDOFF.md` are retired pointers. Start a new isolated scene only when the state is fresh and no current outputs exist. Preserve archives. No Blender jobs were run to prepare this branch.

`support/kart/helpers.py` supplies primitives and a shared dimension block; `presentation.py` supplies cameras and lighting; `validate.py` measures the scene without repairing it. Assemble their actual text into worker submissions: repository imports and Mac paths do not work inside `/job`. Details are in the worker guide.

The existing model and Z6 connection configuration is retained. Machine-local paths in `opencode.json` may need adjustment for another checkout. Support code has local syntax/unit checks; Blender execution and remote rendering must be verified on Z6 during the first run.
