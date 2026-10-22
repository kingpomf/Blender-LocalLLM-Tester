# Kart01 Build Status

## Fresh 256K no-compaction trial — 2026-10-22

- Status: COMPLETE
- Final source job: 327d8d69a06f43ae8b61cef1a1be6d9c
- Accepted job IDs: 1aa034e7606a43259bd4c24cc377e33d, 327d8d69a06f43ae8b61cef1a1be6d9c
- Default model: `z6-llama/qwen38-blender-35b` — 262,144-token context, 16,384-token client output budget
- Actual model used: z6-llama/qwen38-blender-35b (from worker heartbeat)
- Execution host: Z6 (`z6-blender-worker`)
- Operator intervention: project-local Pyright and Blender 4.5 typing support enabled after session `ses_e9bd339a2ffeLVDksTNlpUtTYo`; existing stage PASS claims were not revalidated by this tooling change
- Trial mode: automatic compaction OFF; automatic tool-output pruning OFF; do not manually compact this trial
- Active outputs: cleared; no previous PASS or source job is reused

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | Job 1aa034e7606a43259bd4c24cc377e33d; scene.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 c447397fafd5f7365e9ebb5a1399ec0ccaa143765b6441493f2c10dac3413d5f) |
| 01 | Coordinate system and dimensions | PASS | Job 393cf6540b584a88b94261a54f80a7fe; scene.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 cbadc9a0c4543e424664f6a317bb4bd411d31933224dbe7ee177817d7ac630f3) |
| 02 | Chassis and bumpers | PASS | Job 8a2904c2925d41689f507181f1bb2c00; scene.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 1622bb6ce257cbe5fe18511417e6d894dce3cde1d3d9d95bde7101e66e2be5ba) |
| 03 | Axles and wheels | PASS | Job 3ac8df5ae6c3408c9f3bc51c307529e7; scene.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 1f6b8667a6873c0152a83696a6f5bef4d218a9b71f32838b5555e0c0edd70186) |
| 04 | Seat and steering | PASS | Job cab6c650cf5c40d6851d77a45d765e60; scene.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 f7aea79b1b84e47088cc7df568c228ad4720a75c3f23e6d391e8687e936786c0) |
| 05 | Materials | PASS | Job fa3abfe27afc4c38b8450fe91d8db2bb; scene.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 ac34453470b2fbf96a5cd229f82fbc9716ca73a496bb36ed4ded15bc4c2a737b) |
| 06 | Hierarchy and transforms | PASS | Job cec66cd056194629a2887a6e868c6eda; scene.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 9fea1652152a20f91464b9f6a964a985c96a275b634c6fccbe97148629ccba67) |
| 07 | Presentation cameras and lighting | PASS | Job 2a3af8af6381456985668d287a482e0d; scene.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 dd7ed8be04c129b85d6176294b9cac3322cc36527d8b8b63244f39aa43091000) |
| 08 | Final validation | PASS | Job 62cfa913418947e3ae93c6e010d3ca77; scene.json and validation.json verified; local checkpoint artifacts/blend/Kart01.blend (sha256 c6b88a922c3a658321dd5959920c7f6c3cc449ccef44f8440f7b7e85dd066d6a) |
| 09 | Export and delivery | PASS | Job 327d8d69a06f43ae8b61cef1a1be6d9c; GLB export (152,064 bytes, sha256 c2b4d5a6c9fe0b75aeaaebfe4229e65470bf44e0a30dddf871b9f2d8a343eb56); BUILD_REPORT.md (1,177 bytes, sha256 40245f120ff632c5e285a49dfb0fcdb015ba5ac7537d6c3da71df02dbd0a42be) |

## Start instruction

Read HANDOFF.md and WORKER_GUIDE.md, run `python3 scripts/check_resume.py`, check
worker capabilities, and record the actual model. Begin Stage 00 in a new empty
isolated scene with no historical source_job. Save accepted job/source IDs and
verification results immediately in both checkpoints. This trial tests a fresh
256K session without automatic summarization/pruning; do not manually compact or
enable compaction mid-run. If the window is exhausted, checkpoint and report that
outcome rather than compacting. Do not start a new session midway and count it as
the same uninterrupted-context trial.

## Historical evidence

- The stuck 100K session, unverified PASS claims, native checkpoint, validation source,
  downloaded artifacts and review are preserved in `artifacts/archive/blender35b-100k-stalled-2026-10-22/`.
- The earlier 65K build remains in `artifacts/archive/blender35b-65k-build-2026-10-22/`.
- Prior attempts remain in `artifacts/archive/blender35b-attempt-2026-10-22/`,
  `qwen27b-attempt-2026-10-22/`, `defiant-fable-2026-10-22/`,
  `pre-reset-2026-10-22/`, and `pre-z6-2026-10-21/`.
- SESSION_REVIEW_2026-10-22.md describes the previous attempt only; its jobs are not
  this trial's sources or completion evidence.

## Reset verification (not a build PASS)

- All 10 stages are NOT_STARTED, with no active source or pending job.
- Active output/download/report directories are empty; scripts retains only the
  unchanged model-discovery utility and placeholder.
- Model context remains 262,144. The worker/gateway were idle with no active CPU
  jobs, inference requests, or protected leases at reset inspection.
- Specifications, worker implementation and Python LSP tooling are unchanged for
  this reset. Existing worker guidance and durable checkpoints remain in place.
- Start a new OpenCode session after restarting to load the trial configuration.
