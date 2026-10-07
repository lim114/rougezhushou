import datetime
import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
PYTHON = '/workspace/rougezhushou/.venv/bin/python'
runs = []
for label, package, tests, pattern, expected in (
        ('baseline-related', 'baseline', 'baseline/tests', 'test_*.py', 0),
        ('baseline-new-regression', 'baseline', 'draft/tests', 'test_module_qualification_notes.py', 1),
        ('draft-related-and-new', 'draft', 'draft/tests', 'test_*.py', 0)):
    command = [PYTHON, '-m', 'unittest', 'discover', '-s', str(ROOT / tests), '-p', pattern]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(ROOT / package))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    completed = subprocess.run(command, cwd=ROOT / package, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log = ROOT / f'{label}.log'
    log.write_text(completed.stdout)
    assert completed.returncode == expected, (label, completed.stdout)
    runs.append({'label': label, 'command': command, 'cwd': str(ROOT / package),
                 'started_utc': started, 'exit_code': completed.returncode,
                 'expected_exit_code': expected, 'log': str(log),
                 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest(),
                 'summary': [line for line in completed.stdout.splitlines()
                             if line.startswith(('Ran ', 'FAILED ', 'OK'))]})
(ROOT / 'test-receipt.json').write_text(json.dumps(runs, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(runs, ensure_ascii=False))
