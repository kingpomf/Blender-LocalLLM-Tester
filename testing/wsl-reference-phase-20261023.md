# WSL image references and separate vision reviewer — 2026-10-23

The operator clarified that Qwen3.6 MTP is the Blender coding model, a different
model may handle reference preparation, and image generation should run inside
EliteDesk's Linux WSL subsystem. That workflow is now installed/configured.

## Phases

- `/bowling-references`: vision-capable `z6-llama/qwen38-27b`,139264 context.
  Generates the three references via imageMCP `backend=elitedesk`, Qwen Image2.1
  Q4, then reads actual image pixels and writes hash-bound visual observations.
- `/bowling-start`: pins `z6-llama/qwen36-35b-a3b-mtp-q8`; consumes the guide and
  builds one Blender stage. It does not silently substitute the coding model.
- Open a fresh MTP session at the phase boundary to keep the coding evaluation
  attributable. No reference model contributes Blender implementation scripts.

## Fixed review findings

- References now require full image decode/dimensions, distinct jobs/image bytes,
  actual imageMCP receipt links and matching completed-job/artifact identities.
- Prompt-guided-only review is rejected. Every reference hash requires actual
  pixel-derived observations and an identified vision reviewer.
- Resume validation reconciles reference phase and pending image IDs in both
  ledgers/manifest, including uncertain submissions. It never resubmits jobs.
- imageMCP persists verified-result receipt.json files beside downloads.

## Installed proof

ImageMCP fresh-process generation/download/recovery, shared GPU queue/cancellation,
and controlled simultaneous Z6 coding/EliteDesk image denoising passed. Details:
`../imageMCP/docs/ELITEDESK-WSL-ACCEPTANCE-2026-10-23.md` from the Development parent.

Actual OpenCode vision session `ses_e94b899a8ffePXxGJQx6GoRkKA` read a generated
test image and correctly described red cube left / blue sphere right without
those hints in its prompt. This is infrastructure acceptance, not a bowling
reference or asset-stage PASS. MTP was restored afterward through a normal request.

Fresh merged config confirms both command-level model selections and routing
imageMCP. Real fresh MCP checks confirm EliteDesk Q4, Z6 Turbo and guarded5.2.3
Blender; the trial guard is still empty.32 tests pass; project Pyright clean.

During setup a concurrent configuration change selected native262144 context
for MTP, reflected in both live Z6 and project/global metadata. This task
preserved that newer setting; its earlier1.01M evidence remains historical.

All ten asset stages and the reference phase remain NOT_STARTED. The first user
action after fully restarting OpenCode is `/bowling-references`, then a fresh
MTP session with `/bowling-start`. The previous trial archive is unchanged.
