# Independent OS supervisor v2 — Source only

Use this fresh supervisor with the unchanged GUI runner at `/workspace/.continuation/full100-bounded-validation-source-v1/window.py` (659,988 B, SHA `c2ebf6fe94233fed27fde6abda1d8a27ace1378529c94673d7a271432d195c31`). The earlier supervisor draft and its GUI packet manifest remain byte-identical and must not be treated as an approved launch entry.

The non-author Source review of the first draft found two concrete defects: it could report a negative supervisor exit while actually returning1, and it did not close remaining owned-session descendants after their leader exited. This v2 preserves the genuine child returncode separately and normalizes the supervisor return before storing/printing it. It checks and cleans the launched process group even when its leader has already ended, waits at most5 seconds for closure, and fails if the owned session cannot be verified absent. It also performs this cleanup on exceptions. No global wineserver is terminated.

The actual target argv is passed directly to `subprocess.Popen` with no shell and a new OS session. A monotonic600-second independent supervisor deadline covers the child's Source preflight and actual GUI work; on timeout it sends SIGKILL to the owned process group. Waiting for process/session closure is not extra product execution time. A C extension holding the target's GIL cannot block this separate supervisor process. The child's process exit, supervisor exit, timeout status and closure remain separate recorded facts. A timeout normally produces supervising124; any unresolved closure/error can instead produce supervising1, always with failure/unknown fields retained.

`/proc` session absence only verifies members of that owned Linux session. Root must check that this attempt's Wine/Qt lifecycle has ended before starting another Wine job; it is not proof about a process that escaped that session or the existing shared Wine server.

Launch template (never executed during preparation):

```text
<actual Linux Python> /workspace/.continuation/full100-bounded-supervisor-source-v2/supervisor.py \
  --status <absent fresh Linux status file in a sibling evidence directory> -- \
  /workspace/.compat/run-wine-python.sh \
  <unchanged reviewed GUI window.py Windows path> \
  --root <actual repository Windows path> \
  --guard <actual completed100 guard Windows path> \
  --out <absent fresh GUI output Windows path>
```

The supervisor's parent status directory can be created by this script; status/stdout/stderr files use exclusive creation. The GUI output directory must remain absent until the GUI runner creates it. Root must use real shell-safe argv quoting, bind both packet Sources, require genuine raw completion and inspect all actual GUI assertions,52 state records, four real PNGs and primary/supplemental Source agreement. These future outputs, the actual completed100 guard and runtime success are unknown at Source preparation time.

The v2 Source was compiled without executing its code object (`a875ae`, primary0). No subprocess, project, tests, Qt, Wine, helper codec or Git operation was run. Independent non-author Source review is still required before runtime use.
