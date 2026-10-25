# Fresh references first; Qwen3.8 Turbo asset coding second

The current trial is **bowling52-qwen38-turbo-20261025-r1**. Qwen3.8 Turbo remains
the planner/coder throughout. Old reference images, receipts and design guides are
archived and must not be reused as the current trial's work.

The automatic entry point is `python3 scripts/run_bowling.py --detach` or
/bowling-run. The controller runs /bowling-references in build/Qwen3.8 Turbo,
then a separate fresh /bowling-start session in bowling-coder/Qwen3.8 Turbo.
Do not launch a second controller or code asset meshes during reference planning.

## Execution and provenance

- Concepts: imageMCP, backend **elitedesk**, model **qwen-image-2.1-q4**,
  width512/height512,25 steps, one candidate, distinct recorded seeds.
- Roles: **overview** (three-quarter pair from approach), **layout** (top/elevated
  lanes/approach/gutters/decks/return), **details** (pins, balls, return, materials).
- Use cohesive original stylized-realistic modular game art. Follow the bowling
  specifications, not unrelated mesh packs. Concepts are design inputs, never
  final evidence for a Blender render or completed asset.
- Discover live capabilities/models. Preserve stable request IDs before submitting;
  EliteDesk supports exact-request lookup. Record accepted edimg- IDs immediately,
  poll those IDs, and never replay an uncertain request or silently change hosts.
- Fetch completed verified bytes and receipt.json under this project's
  artifacts/references. Do not claim a prompt-only description is visual review.
- Do not release coding leases or evict other workloads. Preserve an accepted
  authorization_required job and report the required handoff instead of replaying.

## Manifest and actual pixel review

Create artifacts/references/manifest.json with current trial and one completed
entry per role. Each entry must include exact fields:
`role`, `tool="imageMCP"`, `provider`, `model`, `request_id`, `job_id`, `state`,
`prompt`, `seed`, `width`, `height`, `path`, `receipt`, `bytes`, `sha256`.
Paths are project-relative paths beneath artifacts/references and must match
the actual receipt's verified local_path, dimensions, hash, byte count and job.
Use the backend's returned provenance; never invent hashes, IDs or observations.

Then run `python3 scripts/review_reference_images.py`. This fixed image-only
helper sends actual saved image pixels to the installed qwen38-27b vision profile
and writes hash-bound observations/receipts. It is not the primary coding model.
Read the output and write artifacts/references/DESIGN_GUIDE.md yourself, discussing
every image by filename, reusable construction features and corrections to errors.
The helper records inspection_method="visual", reviewer_model and visual_review.
Do not send images to a text-only session or invent a claim of seeing pixels.

Run `python3 scripts/check_references.py`; only after it passes set Reference
phase READY and Pending reference job none in both BUILD_STATUS.md and HANDOFF.md.
The reference planner may edit those fields and record accepted image IDs, but
must leave scene source none, asset stages NOT_STARTED and acceptance unchanged.
Run `python3 scripts/check_resume.py`, then return. The detached controller starts
Stage00 coding automatically. Save reference inputs/receipts/guide for delivery.
