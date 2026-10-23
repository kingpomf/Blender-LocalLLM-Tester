# Fresh Nemotron trial reset — 2026-10-23

Explicitly authorized reset after retiring the Blender-specialist model.

## Preserved evidence

- Final old-model session: `ses_e9ab8bc15ffewRCFYXmdOPs5mK`.
- Previous Z6 queue `var/bowling52-guarded-20261022`: 4 completed, 6 failed;
  zero queued/running jobs at reset inspection. No remote job deleted/replayed.
- Old scripts, native checkpoint, downloaded artifacts, original ledgers,
  configuration snapshots and exhausted guard database archived under
  `artifacts/archive/blender52-specialist-final-2026-10-23/`.
- Archive manifest records byte counts and SHA-256 for all 30 files. Native/job
  metadata/database files may remain Git-ignored but are preserved locally.
- The database is archived rather than its failure history being rewritten.
- Historical Stage 01–03 PASS claims are unsupported and are not reused.

## Fresh trial

- Model: `z6-llama/nemotron35-bolt-e4b`, context 65,536, output budget 16,384.
- Actual runtime: Blender 5.2.3 LTS on Z6, CPU-only rendering in this toolchain.
- New queue: `var/bowling52-nemotron-20261023` (lazily created at first job).
- Active local guard: `.runtime/blender52/submissions.sqlite`, empty attempt table.
- All ten stages NOT_STARTED; no source, pending job or native checkpoint.
- No model-authored implementation in active artifacts/scripts; only the existing
  discovery utility/placeholder remains.
- Infrastructure qualification still uses its original separate queue and local
  state, and contributes no jobs/failures to the new trial.

## Checks

- Fresh OpenCode merged config: Nemotron main/helper model, correct 64K metadata,
  old worker disabled, guarded worker connected, Build limit 60 iterations.
- Real fresh MCP capabilities: runtime_verified=true, actual_version=Blender
  5.2.3 LTS, expected new queue, zero accepted/uncertain jobs and zero failures.
- `python3 scripts/check_resume.py`: PASS, NOT_STARTED / Stage 00,
  active_file_count=0, no consistency issues.
- Resume/guard tests: 19 passed; runtime identity tests: 5 passed.
- Workspace `.venv/bin/pyright`: zero errors/warnings/information.
- Existing Nemotron installed API and OpenCode tool-call qualification is recorded
  in MODEL_SETUP.md. No bowling scene was generated during reset verification.

Fully restart OpenCode and open a fresh Nemotron session before `/bowling-start`.
Proceed one stage per invocation. Guard limits and one-stage workflow remain
unchanged. Shared inference services and the prepared EliteDesk runtime were not
changed by this reset.
