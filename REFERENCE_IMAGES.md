# Reference images first; MTP Blender coding second

The operator authorized two attributable phases:

**Automatic entry point: `/bowling-run`.** Its controller runs these phases in
order and creates the separate coding session automatically; no manual phase
handoff or next-stage prompts are needed. The individual commands below remain
available for explicit phase-only work.

1. **`/bowling-references`** uses **Qwen3.6 MoE**, exactly like the launcher and
   coding phase. It plans images and calls imageMCP. The fixed
   `scripts/review_reference_images.py` tool supplies actual pixel descriptions
   from the installed vision API; Qwen3.6 then writes the construction guide.
2. Open a fresh **Qwen3.6 MTP Q8** session and run **`/bowling-start`**. This command
   pins `z6-llama/qwen36-35b-a3b-mtp-q8` and builds all remaining Blender stages
   from the completed visual guide. No reference-phase model writes asset geometry.

Reference images are concept inputs, not the final Blender render evidence.
The authoring wrapper rejects missing/incomplete references before reserving a
Blender job. Generation, download hashes, receipts and visual observations must
all be recorded. A prompt-only guide does not satisfy the prerequisite.

## Where work executes

- Image generation: **EliteDesk WSL Linux**, existing shared serialized GPU queue,
  profile **`qwen-image-2.1-q4`**. Windows Comfy Desktop is not launched by imageMCP.
- Trial agent throughout: Qwen3.6 MoE on Z6. Only the fixed pixel-description
  helper invokes the vision API; it is explicitly attributed in vision-helper.json.
- Blender asset authoring/rendering: Z6's guarded5.2.3 CPU queue.
- The general imageMCP routing provider accepts backend `auto`, `elitedesk`, `z6`.
  Auto prefers free EliteDesk; if it is busy, use an already image-owned Z6 or queue
  EliteDesk rather than evict Z6 coding. An explicit model is never substituted.
  This benchmark pins EliteDesk/Q4 for consistent reference provenance.
- Z6 **Turbo** is a separate profile with different step limits. Never label Q4
  output as Turbo or apply Turbo's 8-step settings to the Q4 reference recipe.
- Never release someone else's coding lease. On authorization_required preserve
  the accepted ID and report the handoff. Do not automatically replay an uncertain
  submission or move an accepted job to a different host.

## Reference phase

1. Read the ten bowling specs and both ledgers. Reconcile saved image IDs before
   submitting anything new. The resume checker reports pending reference work;
   that is an instruction to poll/recover, not permission to submit replacements.
2. Discover imageMCP capabilities/models. Generate one original image per role:
   **overview** (approach-side three-quarter pair), **layout** (elevated/top-down
   lanes/approach/gutters/decks/return), **details** (pins, three balls, return and
   material palette). Use a cohesive stylized-realistic modular game-art style.
3. Use `backend="elitedesk"`, `model="qwen-image-2.1-q4"`, width512/height512,
   steps25, one candidate, distinct recorded seeds. Save each role's full prompt
   and a stable request_id before submission. EliteDesk supports exact-request
   deduplication and lookup; a lost acknowledgement must be reconciled with
   image_job_by_request using that ID, not an automatically repeated generate call.
4. Immediately record each accepted `edimg-...` ID and state in
   `artifacts/references/manifest.json` and both ledgers before polling. Keep
   Reference phase IN_PROGRESS and Pending reference job set until reconciled.
5. Call image_job_result for each completed job with
   `output_dir="/Users/start/Development/Blender-LocalLLM-Tester/artifacts/references"`.
   Preserve its returned **receipt_path**, downloaded file path, size, SHA-256 and
   dimensions. imageMCP now writes receipt.json beside verified downloads. The
   manifest must link to that receipt and its actual artifact; do not invent it.
6. Run **`python3 scripts/review_reference_images.py`** after all three image
   entries and receipts are saved. It validates the bytes, sends the actual pixels
   to a fixed image-only vision endpoint and saves observations bound to the hashes.
   It reuses completed reviews and refuses to replay uncertain requests. Read
   vision-helper.json and the updated manifest. Do not send images directly to
   the text-only MTP agent or claim its prompt guesses are visual observations.
7. Write `artifacts/references/DESIGN_GUIDE.md`, discussing every image by filename,
   shared design choices and corrections. Record `inspection_method="visual"`,
   the helper's `reviewer_model` and per-image `visual_review` already saved in
   the manifest. Qwen3.6 owns the design choices and all subsequent Blender code.
8. Run `python3 scripts/check_references.py`. Only after it passes set Reference
   phase READY and Pending reference job none in BOTH ledgers, then run
   `python3 scripts/check_resume.py`. Checkpoint and return without Blender work;
   when launched by `/bowling-run`, the controller starts the coding phase next.

## Manifest example (replace every placeholder with actual evidence)

```json
{
  "trial": "bowling52-qwen36-mtp-q8-20261023-r2",
  "inspection_method": "visual",
  "reviewer_model": "z6-llama/qwen38-27b",
  "images": [
    {
      "role": "overview",
      "tool": "imageMCP",
      "provider": "elitedesk-wsl",
      "model": "qwen-image-2.1-q4",
      "request_id": "SAVED_REQUEST_ID",
      "job_id": "edimg-ACCEPTED_32_HEX_ID",
      "state": "completed",
      "prompt": "FULL_ACTUAL_PROMPT",
      "seed": 36001,
      "width": 512,
      "height": 512,
      "path": "artifacts/references/ACTUAL_DOWNLOADED_PATH.png",
      "receipt": "artifacts/references/ACTUAL_JOB_DIRECTORY/receipt.json",
      "bytes": 123456,
      "sha256": "ACTUAL_SHA256"
    }
  ],
  "visual_review": [
    {"sha256": "ACTUAL_SHA256", "observations": "Actual pixel-derived observations, design choices and required corrections."}
  ]
}
```

Require distinct overview/layout/details jobs and image bytes. Pending entries
may omit artifact fields until downloaded; they deliberately fail authoring
validation. Preserve references, receipts and the guide in final delivery and
list them in DELIVERY_MANIFEST.json. Reference-only work does not establish a
Blender source, checkpoint or stage PASS; the ten asset stages remain NOT_STARTED.
