# Stage 00 pre-change inspection recovery — 2026-10-21

## Failed model attempt (preserved)

- Job: `cb743bfa380d43a98cfe895514e5356a`, no source, terminal `failed`.
- Original model script: `artifacts/scripts/stage00_inspect_fresh.py` (unchanged).
- Operator SSH inspection of the retained Z6 `blender.log` identified:

```text
Blender 4.5.14 LTS
File "/job/author.py", line 35
    "length": us.length,
AttributeError: 'UnitSettings' object has no attribute 'length'
```

Blender uses `UnitSettings.length_unit`. The original script also asserts
`system == 'METRIC'` during pre-change inspection, before Stage 00 setup. That
assertion was not reached in the failed job. A fresh scene's initial units must
be observed; Stage 00 then configures and validates METRIC at scale 1.0.
The always-true `assert not ... or True` provided no validation and is omitted
from the corrected script.

This was a model-authored script error, not evidence of GPU failure or a worker
startup failure. The model correctly stopped, recorded the accepted ID, and did
not replay it. Failed-job logs currently require operator access because the MCP
artifact endpoint only serves completed manifests. No worker/API change is made
as part of this recovery.

## Assisted recovery

The corrected inspection is saved separately as
`artifacts/scripts/stage00_inspect_fresh_corrected.py`. It changes no scene data,
records the initial units and contents, and checks for unexpected user objects.
Any new submission is a distinct, explicitly corrected attempt, not a replay of
the failed job. Record its ID in `BUILD_STATUS.md` before polling.

This run must be reported as **assisted**, not an autonomous Qwen Stage 00 pass.
Successful inspection alone does not complete Stage 00: required collections,
Metric units, native checkpoint and validation remain to be performed.

## Verified recovery result

- New job: `63e47cd8a09f4ff591c5629d191198e8`, completed on Blender 4.5.14 LTS.
- Inspection result PASS: no objects, no child collections, no cleanup needed.
- Actual initial units: `METRIC`, `METERS`, scale `1.0`. The old Metric assertion
  was not reached in the failed job and would not have failed for this observed
  state. Removing it keeps observation separate from setup validation; it is not
  evidence of a second runtime failure.
- The scene remains unchanged and Stage 00 itself is PENDING. Required Kart01
  collections and the `artifacts/blend/Kart01.blend` delivery checkpoint have
  not been created by the assisting agent.
- Artifacts were fetched through MCP, copied into the repository's
  `artifacts/downloads/63e47cd8a09f4ff591c5629d191198e8/`, and their hashes matched
  the completed manifest:

| Artifact | SHA-256 |
| --- | --- |
| report.json | `a08edf81e8541a5314a26007ddc4e880d776a5abc8e6e42f289173d91a259255` |
| scene.json | `c8f1f0b42e366b4098765f7c209e9a4aca05ca8e5f710aaaefc710b0f054936b` |
| scene.blend | `2369ced903728e07dcc8c605fb28b8560b138036a6f2b61e90fcac83b16973be` |

The saved corrected script also matches the remote `author.py` hash:
`f8a21d630f48b7fcac709aa79b2dd6bc687340fed459eb6afabe53a8101e536a`.
Resume setup from this completed source ID instead of submitting another fresh
inspection. Preserve the original failure in the model evaluation record.
