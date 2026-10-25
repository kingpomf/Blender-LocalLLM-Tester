# Context-only automatic recovery, compact tools and authorized reset

## Actual incident

The saved coding event reported ContextOverflowError:145862 requested tokens
exceeded native139264 context after full scene/tool output accumulated. OpenCode
compacted but exited1; the prior controller treated any nonzero exit as fatal.
No Blender job was pending and the last checkpoint was valid. This was not a
website outage, media-attachment error or exhausted native-failure circuit breaker.

## Prevention and safe continuation

- Keep actual native context139264/output16384. Increase compaction reserve from
  16384 to32768 and bound tool output to160 lines/12000 bytes. Fresh installed
  OpenCode effective-config validation accepted these settings.
- Add blender_scene_summary (up to6 object names; no new native job) and
  blender_validation_details (bounded4-check pages, selected stage/IDs). Status
  and validation completion return at most12 remaining-check previews and point
  to the details tool. Full immutable local validation is unchanged.
- Only a recognized ContextOverflowError with exit0/1 and no other client/STOP
  error qualifies. The old client exits before reconciliation. Accepted native/
  view/review work is polled to terminal, original IDs reused and fixed validation
  refreshed when necessary. Uncertain IDs, mismatched hashes, missing references,
  hard limits and active two-failure streaks prevent automatic continuation.
- A fresh coding session receives machine-derived checkpoint guidance, not the
  previous erroneous prose summary. Sessions/recovery receipts remain archived;
  native failures/counts are never cleared by context recovery. Three consecutive
  context recoveries without a new verified checkpoint remain a bounded stop.
- Reference-phase recovery also requires all generation acknowledgements already
  recorded in the manifest. Unrecorded/uncertain image submissions halt rather than
  generating replacements. No automatic replay of inference/tool jobs is added.
- Operations report shows context-recovery counts/state while remaining read-only.

## Reset and authorization

The user explicitly authorized active-error reset, all changes commit/push and a
new detached run. The reset verified all39 remote accepted jobs terminal, retained
the same canonical asset/reference inputs, and advanced this trial to epoch1.
Active hard/API counts and controller streak are0. All39 original attempts,5 failed
jobs, classifications, model sessions and fingerprints remain archived/intact.
Limits remain6 hard/source20 total. No further reset is authorized.

`before/`, local ignored SQLite/native/event backups, attempts.before.json,
api-corrections.before.json and reset-receipt.json preserve the prior state.
continuation.json binds model/trial/source, native/report/validator/guard hashes
and the new epoch. Do not rerun the one-shot reset script or use retired plans.

## Verification

122 tests passed; targeted Pyright clean. Regression coverage includes the exact
recorded context overflow, a fresh client after reconciliation, no old session
reuse, mixed/unrelated error refusal, failed reconciliation, bounded repeated
overflow, saved reference-ID proof, source consistency, current hard streaks,
existing pending-result consumption without replay, uncertainty refusal and compact
scene/check queries. Fresh real MCP and checkpoint evidence is recorded alongside
this report. The new model session still needs to repair actual asset geometry;
context recovery success is not asset acceptance.
