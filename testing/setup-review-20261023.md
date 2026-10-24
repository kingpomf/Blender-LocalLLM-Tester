# Review: Qwen3.6 setup and image-first Blender trial

Date: 2026-10-23. Scope: review the preceding uncommitted setup changes, verify
installed state observationally, and investigate EliteDesk image generation.
No inference, image generation, worker launch, service restart or lease change
was performed during this review. Findings below are not fixed by this report.

## Findings

### P1 — Images do not yet inform construction through their actual pixels

`opencode.json` selects a text-only MTP model. `REFERENCE_IMAGES.md:45–53`
explicitly permits a prompt-guided guide and `scripts/check_references.py:49–50`
accepts it. Consequently, the workflow can generate images but construct the
asset entirely from their prompts, without observing generated proportions,
forms, colors, omissions or mistakes. This is honest about the limitation, but
is not a complete implementation of image-guided asset creation.

Recommendation: a vision-capable review step (or explicit operator visual review)
must produce an image-derived construction brief tied to the image hashes before
the MTP coding model builds. Keep visual evidence and prompt intent distinct.

### P2 — The reference prerequisite trusts unverifiable/invalid image evidence

`scripts/check_references.py:24–41` trusts manifest claims of completed imageMCP
jobs and checks only a short image signature, not image decoding. It also permits
the same file and job ID to satisfy all three roles. Tests at
`tests/test_references.py:18–27` use fake PNG headers as passing fixtures.

Reproduced outside the checkout with a temporary fixture: one file consisting of
a PNG signature plus arbitrary text, a nonexistent job ID reused for all three
roles, self-consistent byte counts/hashes and repeated guide text returned
`passed: true`. No real job was submitted or project manifest created.

Recommendation: persist actual successful imageMCP result receipts, link their
job/provider/model/artifact metadata to the manifest, decode/verify real images,
validate dimensions, and require distinct requested reference outputs. Test with
real tiny valid images plus corrupt-image and false-receipt negative cases.
This is an acceptance-quality check, not a security boundary against editable files.

### P2 — Reference progress is absent from resume reconciliation

`scripts/check_resume.py:40–85` handles Blender artifacts and the Blender guard,
but neither the new reference manifest nor Reference phase/Pending reference job
fields. A reference-only NOT_STARTED state is legitimate; inconsistent or pending
reference state must nevertheless be reconciled.

Reproduced using copies of the current ledgers: BUILD_STATUS said references READY,
HANDOFF said NOT_STARTED, an image manifest entry remained queued, and the resume
checker still returned `passed: true`, with zero pending work. The author gate can
catch an honestly queued manifest entry later, but the initial resume check gives
no guidance to recover its accepted image ID. Lost/uncertain image submission
handling is currently prose, not a durable project controller.

Recommendation: reconcile both reference ledgers, manifest and saved receipts;
surface pending/uncertain image IDs separately from Blender source IDs; verify READY
against completed reference evidence; never retry an uncertain remote submission.

## Verified positive evidence

- Z6 live registry and observed backend agree on model `qwen36-35b-a3b-mtp-q8`,
  UD-Q8_K_XL path, `n_ctx=1009920`, draft-mtp/max2 and the documented hybrid offload.
- Gateway observed healthy CODING_PROTECTED, no active requests or explicit leases,
  no GPU diagnostic errors. This was read-only inspection, not a model switch.
- Earlier pinned SHA-256/API/SSE/OpenCode qualification evidence is retained.
  Full million-token prefill/retrieval remains untested; no new claim is made.
- The previous trial and guard were archived; current trial remains NOT_STARTED.
- Re-ran project tests: 26 passed. Pyright: zero diagnostics. Registry tests:
  11 passed. Both reviewed repositories pass `git diff --check`.
- These passing suites do not cover the reproduced reference-evidence gaps.

## EliteDesk conclusion and routing recommendation

The earlier statement that no EliteDesk imageMCP backend is configured was correct,
but incomplete: there is an existing native Windows ComfyUI/Qwen Image installation
with weights, workflows, output PNGs and historical GPU execution logs. See
`imageMCP/docs/ELITEDESK-DISCOVERY-2026-10-23.md` for the inspected paths/history.

The current imageMCP has one provider/backend URL. It is not a fleet scheduler.
The Z6 gateway can yield idle, unprotected coding to images, but that reloads the
coding model and loses resident KV cache; an open coding session is not protected
between requests unless an explicit lease exists. The desired policy should prefer
a compatible free EliteDesk worker while keeping Z6 coding resident.

Add the EliteDesk adapter and shared GPU coordination, then durable capability-aware
routing. Do not simply point the existing HTTP adapter at ComfyUI: its API is
different, its standard Qwen Image Q4 profile is not Z6 Turbo, and its native Windows
GPU use is outside the existing WSL render/audio/video queue. Keep accepted job
identity pinned to a host; uncertain submissions must never be failed over/replayed.
