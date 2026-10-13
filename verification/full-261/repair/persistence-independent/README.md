These are independent actual observations of the section261 persistence repair,
using public temporary files only. The manifest records every original execution
path, archive path, byte count and SHA256. No environment, pyc or full before tree
was copied.

* The f4a0b964 before receipt contains all12 cases and actual original/after byte
  values. All12 unrelated targets were overwritten or created; first-install
  destination collision protection still held. The loaded isolated source hashes
  were checked against the original Git revision.
* The two Linux exclusive-open after receipts are preserved candidate stages.
  Their historical `final` filenames do not claim final cross-platform acceptance.
  The root's later Wine x-only4 failures superseded those candidates. The old
  summaries remain raw historical records with this explicit stage qualification.
* The actual Wine11 mkdir probe passed all4 forced existing-name cases, preserving
  regular files, directories, and live/dangling directory symlinks, then allocating
  a fresh private directory. Only candidate names were forced; actual IO was used.
* The archive helper before-lock probe exposed two write/publication interleavings
  that published another writer's bytes. The current actual `RunState.save` after
  lock probe blocks the second writer before write, and the first successfully
  publishes its own state in both initial and replacement cases. Its receipt is
  Linux-only; final root Linux/Wine suites provide separate wider acceptance.

The original scheduling probe assumption failed after root introduced the lock;
its script and explanatory stderr are retained, without calling that invalid
precondition a product failure. Original probe scripts remain byte-exact evidence;
their relative-root assumptions refer to the manifest's original work paths.
`persistence_tmp_probe.py` also accepts an explicit `--source-root` for replay.
No private-state access, native Windows verification, game action or chat request
is inferred from these checks.
