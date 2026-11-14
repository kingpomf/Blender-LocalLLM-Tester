# BowlingPair01 — Flash-Next / Strata with EliteDesk Blender5.2 CUDA

The retained completed trial and November repository checks are summarized in
[CLEANUP_REVIEW.md](CLEANUP_REVIEW.md) and [BUILD_REPORT.md](BUILD_REPORT.md).
The setup instructions below describe how this trial began; do not restart it empty.

Fresh trial bowling52-flash-next-elitedesk-20261025-r1, linked worktree branch
trial/bowling-flash-next-elitedesk. The original Turbo bowling trial remains paused
and the completed kart review package remains separate; neither is an input here.

Primary planner/coder: z6-llama/qwen38-flash-next through Strata on Z6,262144 context
and32768 output. Blender5.2.3 runs on EliteDesk: CPU authoring/validation and actual
CUDA rendering on its shared serialized RTX3060 queue. No Z6 model/GPU eviction is
needed for Blender renders. Image reference generation shares the EliteDesk queue.

The asset must satisfy all ten files under spec/bowling-pair-01/. Fresh references
come first, then a new scene. Existing API/return-type lookup, read-only validation,
automatic checkpointing, soft API correction policy, context recovery and fixed
pixel-review/export tools are retained. Eight unchanged validated revisions now
stop new authoring for diagnosis without charging a native error.

Run `python3 scripts/run_bowling.py --detach` once after preflight. Monitor with
`python3 scripts/run_bowling.py --status` and the report at
http://z6-llm:8088/blender-trial/. Do not launch duplicate controllers. Read AGENTS.md,
CONTROLLED_CONTINUATION.md, REFERENCE_IMAGES.md and WORKER_GUIDE.md.

124 unit tests pass; worker CUDA qualification evidence is local under
.runtime/elitedesk-qualification/. The real small fixture confirmed Blender5.2.3,
CUDA RTX3060 execution with cpu_enabled=false, and verified PNG hashes. It is not
a game asset or proof that the bowling deliverable has passed acceptance.
