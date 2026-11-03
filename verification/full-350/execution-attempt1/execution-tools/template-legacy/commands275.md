# Inactive preparation handoff

Both bundles are INACTIVE_DRAFT, not frozen and not executed. `--prepare` has already run; do not rerun or overwrite this phase. Current production source is still owned by root.

After root has declared and written its final275 `verification/full-275/source-freeze.json` (with `parent_commit` and complete `source_sha256`), bind both reviewed bundles:

```powershell
$taskRoot=(Get-Location).Path
$taskPython=Join-Path $taskRoot '.venv/Scripts/python.exe'
$taskParent=(git rev-parse HEAD).Trim()
& $taskPython -X utf8 .cache/full275-legacy-bundle/prepare275.py --activate --root-declared-freeze verification/full-275/source-freeze.json --expected-parent-commit $taskParent
```

Activation verifies the root declaration and exact source bytes, maintained source scope and branch/parent, all reviewed draft-tool bytes,17 original-proof archive mappings, complete862 assert AST/order, original552 maintry source, full guard coverage and unchanged root source. It does not run tests or create a source freeze itself. Re-activation/overwriting a used phase is refused.

Use a fresh temporary output namespace outside the repository; do not create each `actual` directory first. Supervision creates its own parent status/log directory, while each original fixture creates `actual` itself.

```powershell
$taskOut=Join-Path $env:TEMP ('rouge-full275-'+[guid]::NewGuid().ToString('N'))
$taskSupervisor=Join-Path $taskRoot '.cache/full275-legacy-bundle/supervisor275.py'
$taskLegacyLauncher=Join-Path $taskRoot '.cache/full275-legacy-bundle/launcher275.py'
$taskCurrentLauncher=Join-Path $taskRoot '.cache/full275-current-window/launcher275.py'

# Run sequentially, and preserve the real exit of every command.
& $taskPython -X utf8 $taskSupervisor --status (Join-Path $taskOut 'legacy/supervisor.json') --timeout 1200 -- $taskPython -X utf8 $taskLegacyLauncher --root $taskRoot --out (Join-Path $taskOut 'legacy/actual') --mode legacy
& $taskPython -X utf8 $taskSupervisor --status (Join-Path $taskOut 'current30/supervisor.json') --timeout 1200 -- $taskPython -X utf8 $taskCurrentLauncher --root $taskRoot --out (Join-Path $taskOut 'current30/actual') --mode current30
& $taskPython -X utf8 $taskSupervisor --status (Join-Path $taskOut 'current29/supervisor.json') --timeout 1200 -- $taskPython -X utf8 $taskCurrentLauncher --root $taskRoot --out (Join-Path $taskOut 'current29/actual') --mode current29
```

`current30` retains all original30 checks, including real symlink creation. Its1314 failure is expected from the native capability proof but must be actually observed and archived; no exception is converted to PASS. `current29` retains all29 previous workflows and precisely omits only the proven unavailable261 symlink specialization, with an explicit unavailable record. It is a separate result and cannot be called a complete30 PASS. Do not skip running `current30` based on the preflight result.

The supervisor retains a real Popen child handle and assigns it to a newly created owned Windows job. Its1200s deadline is the maximum; it writes true child/supervisor exits, stdout/stderr, timeout and owned-job closure. A transient observation timeout is not a terminal signal: poll the same supervisor/Popen tool session or inspect its actual PID/retained handle; never start a duplicate fixture because a poll expired. A live owned job is terminated only on its own deadline or verified supervisor failure. Do not globally kill Python/Codex/game/window processes. The private original project window remains outside the job.

Before broad execution, small non-GUI supervisor capability probes ran only owned `python -c import time;time.sleep(...)` children: normal completion child0/supervisor0 and deadline child124/supervisor124, both job assigned and no live owned execution. The first preparation probe found pywin32 `CreateJobObject(None,None)` rejection before child launch; original source/record retained, corrected to the actual supported unnamed-job empty string. These are process API probes only, not GUI, source-freeze or full-test passes.

After each genuine execution, inspect both raw fixture output and `native275-launcher-closure.json`; true process exits from `supervisor.json` are necessary. Root must additionally inspect the full52 typed state archive/4283 records/42 projections/exact10 admissions, complete current29/30 records, PNGs and freeze/source coverage. The old legacy filename/receipt scope labels are preserved with original maintry bytes; authoritative current platform/constructor/cleanup information is in the native275 supplemental ledgers. Never infer Linux/Wine or original historicalWindows/game/chat verification from this new native fixture.
