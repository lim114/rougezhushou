# Attempt2 import-order adapter repair

Do not run the copied `prepare275.py` or its copied first-attempt commands: those original files are preserved as evidence. This attempt has a dedicated `prepare_attempt2.py` and remains INACTIVE_DRAFT until root explicitly binds it to the exact same freeze and parent.

Attempt1 actually ended child1/supervisor1 with source drift empty and normal Qt cleanup. The final raw receipt has4213 appended records;4192 was only its last progress checkpoint. Actual failure was the strict section90 same-call `calculate_damage` entry-delta==1 assertion. Source and88 original output/tool/freeze artifacts are sealed in `attempt1-original-seal/seal.json` with original SHA/byte length; originals remain untouched.

The first-attempt adapter imported `rouge.app` before the unchanged narrow observers were installed. `app.py` binds its calculator/formatter names with `from ... import ...`. Two fresh-process real calculator probes executing the four original observer functions' unchanged AST prove:

- Early app import: all3 application aliases remain unobserved, actual calculator delta0.
- Original order: observers installed before app import, all3 aliases match, actual delta1.
- Both return the exact same real result SHA256 `9d59c2f453c59e7019b23d5f219978bb28be603335fecd3f80224150e9d13d3a`, from the same public mechanical operator input. No QApplication, window, game action, chat or private state access.

Attempt2 only delegates the original observer installer first, preserves its return/exceptions, then runs the existing normal constructor bootstrap. It never manually patches app damage aliases, fabricates counter values, changes a calculator return, removes/assert-softens a check, or installs a global profiler. Original862 assert AST/order, original552 maintry source bytes, and original observer installer function bytes remain unchanged. Native historical constructor admission,52 typed states/4283 records/42 projections/exact10 comparisons are still required.

Root may bind after inspecting the inactive adapter and original/probe evidence. The copied first-attempt activation records are replaced only inside the new attempt2 namespace, never in the used original folder.

```powershell
$taskRoot=(Get-Location).Path
$taskPython=Join-Path $taskRoot '.venv/Scripts/python.exe'
$taskParent=(git rev-parse HEAD).Trim()
# Use the exact freeze path already recorded in attempt1 activation275.json.
& $taskPython -X utf8 .cache/full275-legacy-attempt2-bundle/prepare_attempt2.py --activate --same-root-freeze verification/full-275/source-freeze.json --expected-parent-commit $taskParent

$taskOut=Join-Path $env:TEMP ('rouge-full275-legacy-attempt2-'+[guid]::NewGuid().ToString('N'))
$taskSupervisor=Join-Path $taskRoot '.cache/full275-legacy-attempt2-bundle/supervisor275.py'
$taskLauncher=Join-Path $taskRoot '.cache/full275-legacy-attempt2-bundle/launcher275.py'
# Root alone starts this after explicit same-frozen-source binding; not started by worker.
& $taskPython -X utf8 $taskSupervisor --status (Join-Path $taskOut 'supervisor.json') --timeout 1200 -- $taskPython -X utf8 $taskLauncher --root $taskRoot --out (Join-Path $taskOut 'actual') --mode legacy
```

Activation requires exactly the same parent/branch/freeze SHA as actual attempt1, rechecks every root/maintained/source supplemental SHA, remaps only the candidate cache paths, validates all sealed originals, and records new executed-tool/window/guard SHA. It does not create a new root freeze, touch production/tests, or automatically run any UI. Subsequent runtime observations must poll the same owned live Popen/job handle and preserve true terminal exits. A passing non-GUI alias probe does not certify the legacy window.
