# Independent OS supervisor v3 — Source only

This fresh Source candidate corrects the v2 assumption that every remaining owned-session /proc entry means live execution. The saved first full100 attempt retains a terminated Xvfb entry with state Z, parent 1 and its original failure; it is not rewritten or counted as a successful attempt. Linux proc_pid_stat(5) identifies Z as Zombie, and wait(2) explains that a terminated child may retain a process-table entry until it is waited for. The two official pages were downloaded with verified TLS and are bound in source-contract.json.

The real /proc scan now retains each owned PID with its parsed state. Exactly Z may be classified as no live execution. Every other state, any unknown state or any unreadable entry remains blocking until independently observed absent; unknown data cannot grant success. Cleanup still targets only this launch's owned process group, with the existing five-second closure bound, and sends no global Wine-server signal. A group containing only observed zombies receives no pointless new signal.

The closure receipt keeps the original owned PID fields and adds real state rows, potentially live PIDs, zombie PIDs and no_live_owned_execution_verified. owned_session_absence_verified remains false while any zombie or unreadable entry remains. retained_zombies_reaped_by_supervisor is false: this supervisor does not claim to reap somebody else's child or to clear an adopted parent-1 entry. No-live execution permits an otherwise successful zero child result; absence and reaping stay separate recorded facts. A nonzero child, timeout, launch error or unverified live closure never becomes a zero supervisor result. The child's genuine returncode remains separately recorded, including negative signals; supervisor exit normalization remains unchanged.

Use only after independent non-author Source review. Root supplies a freshly reviewed GUI argv, its actual Source bindings, completed100 guard and absent output paths. This packet does not approve the old failed GUI fixtures or select a replacement GUI runner. Launch template (not executed during preparation):

```text
<actual Linux Python> /workspace/.continuation/full100-bounded-supervisor-source-v3/supervisor.py \
  --status <absent fresh Linux status path> -- \
  <exact Root-reviewed Wine wrapper and fresh GUI runner argv>
```

All v2 files and manifests remain byte-identical. The executable diff changes only session state collection, closure classification/recording and its zero-success decision. The original exact argv, shell-free new session, independent 600-second monotonic deadline, exclusive durable status/log files, actual child returncode and scoped cleanup are retained. A closure scan covers the owned Linux session only; it is not proof about escaped descendants, the shared Wine server, or another session. Root separately verifies this attempt's complete Wine/Qt lifecycle before starting further Wine work.

Only standard-library Source reads, SHA/diff/AST/JSON and semantic compile(source, path, 'exec') were used to prepare this candidate. The code object was not executed, no supervisor/helper/project/tests/Wine/Qt/codec/Git operation was run, and no tracked repository file was modified. Actual new GUI results, process states, exits, screenshot views and successful publication remain unknown.
