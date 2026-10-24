---
description: Generate reference images on EliteDesk WSL and visually review them before Blender coding
agent: build
model: z6-llama/qwen36-35b-a3b-mtp-q8
---

Complete only the reference phase for BowlingPair01 using Qwen3.6 MoE.
You remain the trial agent; do not switch the session to Qwen3.8.
Read AGENTS.md, REFERENCE_IMAGES.md, BUILD_STATUS.md, HANDOFF.md and all ten bowling
specifications. Do not submit any Blender author/modify/render jobs in this phase.

Reconcile saved image job IDs first. Through imageMCP discover capabilities/models,
then generate the overview, layout and detail reference images with backend
elitedesk, model qwen-image-2.1-q4, 512x512, 25 steps and recorded distinct seeds.
Record each accepted job immediately in the manifest and both ledgers, then poll
that exact ID. Never automatically repeat an uncertain submission. Fetch completed
results into this project's artifacts/references, preserving receipt.json paths.

The MTP profile is text-only. After saving all three image entries/receipts, run
`python3 scripts/review_reference_images.py`. This fixed image-description helper
sends actual pixels to the installed vision profile and saves hash-bound visual
observations; it is a tool, not a replacement trial agent. Read its saved output
and write DESIGN_GUIDE.md yourself, identifying the helper and image-derived
features/corrections. Never claim you personally saw pixels or invent a review.
Run python3 scripts/check_references.py. Only then set Reference phase READY,
Pending reference job none in both ledgers and run python3 scripts/check_resume.py.

Return with the images and design guide. Under /bowling-run the controller starts
the MTP coding phase automatically. For phase-only use, the next command is
/bowling-start in a fresh Qwen3.6 MTP session. Reference planning is attributable
to Qwen3.6, with the image-only helper separately identified; Blender coding starts at Stage00.

Use Read/Glob/Grep for discovery instead of compound shell listings. A denied
optional discovery command is not a reason to give up: use an allowed tool.
Preserve real STOP/failure limits and never replay uncertain image jobs.

Controller recovery context, when present:
$ARGUMENTS
