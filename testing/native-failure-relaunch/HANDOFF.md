# Authorized retry after native-failure review

The user explicitly requested another detached run after review/publication of
commit bfa62a6. Keep bowling-coder and Qwen3.6, same Blender5.2.3 CPU-only queue.
Use current MCP workflow state; preserve the existing asset and reference images.

The asset source remains 756846c5415e4c5e92f159389a87eeb0. Two failed jobs are still
counted in epoch2; all28 failed jobs remain historical evidence. No budget reset,
counter deletion or validator changes are authorized.

Read testing/REPEATED_FAILURE_DIAGNOSIS.md. Both recent failures were caused by
removing obj.data while obj still uses it, followed by accessing/removing obj.
Collecting names first does not fix that order. Prefer editing existing geometry
in place. If deletion is required, save data = obj.data, remove obj with
bpy.data.objects.remove(obj, do_unlink=True), then clean the saved datablock only
when data.users == 0. Never access obj after removal.

Start with ONE small correction, such as the obscuring floor placement, rather
than another several-hundred-line Stage04–07 rewrite. Save it to a new script,
inspect LSP feedback, submit via MCP and poll its automatic checkpoint/validation.
Compare measured checks before proceeding. Correct confirmed unsupported APIs;
do not broadly dismiss diagnostics or skip collision acceptance to evade errors.
Stage04 visibility can wait for useful cameras/props, but must pass final review.

The reviewed controller now recognizes failed native jobs even inside successful
MCP responses, including view jobs. Two distinct failed/cancelled native jobs
without a newly published asset edit stop the client immediately. Old successful
job polls do not clear the streak. Recoverable preflight feedback consumes no
attempt: fix it before submitting. All original budgets/fingerprints still apply.

Use blender_render_view, fixed pixel review, selected export/reimport and delivery
tools as documented. Do not render inline, edit managed ledgers or claim PASS from
job completion. Continue automatically only while making verified progress.
