---
description: Create fresh reference images and a pixel-reviewed guide before Blender coding
agent: build
model: z6-llama/qwen38-turbo
---

Complete the reference phase using Qwen3.8 Turbo. Read AGENTS.md,
REFERENCE_IMAGES.md, BUILD_STATUS.md, HANDOFF.md and all ten bowling specifications.
This is a new trial: bowling52-qwen38-turbo-20261025-r1. Old references/assets are
archived. Do not import old meshes or submit Blender scene jobs in this phase.

Discover imageMCP capabilities/models. Generate distinct overview/layout/details
concept images using backend elitedesk, model qwen-image-2.1-q4,512x512,25 steps
and distinct recorded seeds. Save stable request IDs before submission; record
accepted IDs immediately, poll those IDs and download verified receipts/artifacts
to this project's artifacts/references. Never replay uncertain submissions.

Create artifacts/references/manifest.json with the current trial ID and the exact
provenance/bytes/hash/receipt fields described in REFERENCE_IMAGES.md. Reference
phase fields in BUILD_STATUS.md and HANDOFF.md may be updated by this reference
planner; stage acceptance/source fields remain untouched. No manual stage PASS.

Run `python3 scripts/review_reference_images.py` once the image entries are saved.
This fixed pixel-only helper supplies real observations; it does not replace the
Qwen3.8 Turbo planner/coder. Read its output and write DESIGN_GUIDE.md referencing
all images, useful construction features and corrections. Do not invent a review.
Run `python3 scripts/check_references.py`; only after it passes set Reference phase
READY/Pending reference job none in both ledgers. Run `python3 scripts/check_resume.py`.

Return after reference acceptance. The detached controller automatically starts
bowling-coder/Qwen3.8 Turbo in a separate fresh coding session at Stage00. Use
Read/Glob/Grep for discovery and only the fixed shell helpers above. Actual STOP,
uncertainty or exhausted budgets halt; optional discovery errors do not justify
repeating denied commands. Never commit/push or release coding leases.

Controller context:
$ARGUMENTS
