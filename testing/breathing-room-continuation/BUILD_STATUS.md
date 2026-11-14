# BowlingPair01 — Flash-Next / EliteDesk

- Validation state: pending
- Checkpoint SHA-256: d570cdb362925a57cb33b1a54e080dbd2e35d7763317726463ebcbff08bbf57c
- Active checkpoint: artifacts/blend/BowlingPair01.blend
- Workflow operation: asset
- Status: BLOCKED
- Next stage: 00 — current-source revalidation pending
- Active source job: cf9e9c33d60a4f99ae69e149236e0acf
- Default model: z6-llama/qwen38-flash-next
- Actual model used: not started
- Trial queue: /home/kingpomf/blender-new-llm-setup/var/mcp-worker
- Execution host: elitedesk-3060
- Controller: STOPPED: STOP: two distinct native jobs failed/cancelled without a published asset advance; client stopped immediately for diagnosis, no automatic retry.
- Reference phase: READY (overview edimg-29f0a8afdbb04cbe95d60cfce1e69d77 seed 41001; layout edimg-2404a901d5ad41df8cfcacc32f35b419 seed 41002; details edimg-6df4618278fe4608a80efd3b140e0df7 seed 41003; manifest/receipts/DESIGN_GUIDE verified by check_references)
- Pending reference job: none
- Pending job: none
- Pending source job: none
- Accepted job IDs: cf9e9c33d60a4f99ae69e149236e0acf
- Next action: Inspect machine workflow status and diagnostics; operator reconciliation required before restarting.

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 01 | Lane pair and markings | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 02 | Gutters, decks and pit | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 03 | Reusable bowling pins | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 04 | Reusable bowling balls | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 05 | Return, seating and alley dressing | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 06 | Materials, hierarchy and collision | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 07 | Presentation cameras and lighting | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 08 | Final measured validation | IN_PROGRESS | Current source cf9e9c33d60a4f99ae69e149236e0acf; fixed measured validation pending. |
| 09 | Export and delivery | NOT_STARTED | No verified final delivery yet. |

## Next action

References READY; author Stage00 in a fresh coding session. Strata stays on Z6; Blender5.2/CUDA run on EliteDesk.
