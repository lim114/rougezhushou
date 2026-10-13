This directory contains isolated public temporary-file checks of the section261
diagnostic-name archive adjustment. No production source, private state, game
capture, game action or chat request was changed by these probes.

`archive-interleave-current-linux.json` is the actual pre-lock helper result:
two writes were completed before the first publication. Both initial and
replacement publication used writer B's bytes when called through writer A's
returned path. Writer A's bytes remained in the preserved diagnostic entry.
The receipt binds the helper SHA256 before and after the real IO; it does not
claim the experiment used actual GUI threads or native Windows.

Root then added `record_save_lock` around each producer's write through publish.
`run-save-interleave-after-lock-linux.json` uses two actual `RunState.save`
calls and a scheduling barrier only around the real helper return. The second
save is rejected before its write phase, with the normal sticky save issue;
the first returns True and publishes its own state in both initial and existing
destination cases. Actual exit0 and unchanged source hashes were recorded.

The original run-save probe assumed both calls could reach the write phase and
failed that precondition after the lock was added during preparation. Its
script and explanatory stderr are retained separately; that probe-precondition
failure is not called a product failure. The independent after result is Linux
only. The earlier actual Wine mkdir-collision proof is retained one directory
above and supports the lock's atomic directory-claim boundary.
