---
description: Generate reference images on EliteDesk WSL and visually review them before Blender coding
agent: build
model: z6-llama/qwen38-27b
---

Complete only the reference phase for BowlingPair01. This command deliberately
uses the installed vision-capable Qwen3.8 27B profile, not the text-only MTP coder.
Read AGENTS.md, REFERENCE_IMAGES.md, BUILD_STATUS.md, HANDOFF.md and all ten bowling
specifications. Do not submit any Blender author/modify/render jobs in this phase.

Reconcile saved image job IDs first. Through imageMCP discover capabilities/models,
then generate the overview, layout and detail reference images with backend
elitedesk, model qwen-image-2.1-q4, 512x512, 25 steps and recorded distinct seeds.
Record each accepted job immediately in the manifest and both ledgers, then poll
that exact ID. Never automatically repeat an uncertain submission. Fetch completed
results into this project's artifacts/references, preserving receipt.json paths.

Use read on each actual downloaded image. If the model cannot receive/view its
pixels, stop and report the limitation rather than deriving observations from
the prompt. Write image-derived observations bound to every image SHA-256 and a
construction guide with shapes, palette, layout and specification corrections.
Record reviewer_model, inspection_method=visual and visual_review in the manifest.
Run python3 scripts/check_references.py. Only then set Reference phase READY,
Pending reference job none in both ledgers and run python3 scripts/check_resume.py.

Return with the images and design guide. Under /bowling-run the controller starts
the MTP coding phase automatically. For phase-only use, the next command is
/bowling-start in a fresh Qwen3.6 MTP session. Reference planning is attributable
to this vision model; the new model's actual Blender coding trial starts at Stage00.
