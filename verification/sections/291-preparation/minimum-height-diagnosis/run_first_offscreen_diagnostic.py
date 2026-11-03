"""Own/capture the isolated offscreen diagnostic; never start native validation."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[1]
source = here / 'diagnose_tab_minimums.py'
paths = {suffix: here / ('first-offscreen' + suffix)
         for suffix in ('.source.py', '.stdout.txt', '.stderr.txt', '.run.json')}
if any(path.exists() for path in paths.values()):
    raise FileExistsError('Keep first actual diagnostic evidence.')
raw = source.read_bytes(); paths['.source.py'].write_bytes(raw)
argv = [sys.executable, '-B', '-X', 'utf8', str(source)]
env = dict(os.environ); env['QT_QPA_PLATFORM'] = 'offscreen'
started = datetime.now(timezone.utc).isoformat()
timeout = None
try:
    result = subprocess.run(argv, cwd=root, env=env, capture_output=True, check=False, timeout=60)
    out, err, code = result.stdout, result.stderr, result.returncode
except subprocess.TimeoutExpired as error:
    out, err, code = error.stdout or b'', error.stderr or b'', None
    timeout = {'type': type(error).__name__, 'message': str(error)}
paths['.stdout.txt'].write_bytes(out); paths['.stderr.txt'].write_bytes(err)
report = {'kind': 'REAL_OFFSCREEN_PUBLIC_DIAGNOSTIC_PROCESS_NOT_NATIVE_ACCEPTANCE',
          'argv': argv, 'cwd': str(root), 'QT_QPA_PLATFORM': 'offscreen',
          'started_at': started, 'ended_at': datetime.now(timezone.utc).isoformat(),
          'actual_exit_code': code, 'timeout': timeout,
          'source_sha256': hashlib.sha256(raw).hexdigest(), 'source_unchanged': source.read_bytes() == raw,
          'actual_unittest_runs': 0, 'native_window_launched': False,
          'outputs': {suffix: {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                              'bytes': path.stat().st_size} for suffix, path in paths.items() if path.exists()}}
paths['.run.json'].write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(out.decode('utf-8', errors='replace'), end='')
print(err.decode('utf-8', errors='replace'), end='', file=sys.stderr)
raise SystemExit(code if code is not None else 124)
