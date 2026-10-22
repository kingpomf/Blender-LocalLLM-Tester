# Stuck 100K attempt — archived for fresh 256K trial

User requested another fresh run to evaluate whether compaction contributed to
the failure. This archive preserves the original active directories and document
snapshots before reset, including the inconsistent stage ledger, handoff, native
checkpoint, downloaded renders/metadata, validation script, and independent review.

- Session reviewed: `ses_e9c18d959ffem6YPRJCfSlIb7w`.
- Its run used the 100K client profile; model metadata in the snapshots reflects
  the subsequent 256K setup, which did not repair the attempt.
- Stage 07 source: `af5a5f32725047799da134617e2841bc`; claimed PASS is unsupported.
- Multiple identical-code validation jobs failed; the review records the evidence.
- The original project configuration had automatic compaction/pruning enabled.
- The new trial retains native 262,144 context, disables automatic compaction and
  pruning, and starts with no historical source or PASS claims.
- This reset adds no LSP/stub dependencies, submits no new Blender/inference jobs,
  and makes no worker/model-service change. No queued/running CPU jobs were found.

The new test is distinct from this archived session. Preserve this evidence and
do not reuse its asset or compaction summary as the new trial's starting state.
