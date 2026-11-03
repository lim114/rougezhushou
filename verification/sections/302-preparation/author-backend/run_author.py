"""Owned isolated cache source build or pure API tests; preserve exact first result."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE = HERE / 'candidate'
parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=('build', 'verify', 'tests'))
parser.add_argument('--name', required=True)
args = parser.parse_args()
out = HERE / args.name
out.mkdir(exist_ok=False)
inputs = [p for p in CANDIDATE.rglob('*') if p.is_file() and p.suffix not in ('.pyc',)]
before = {p.relative_to(CANDIDATE).as_posix(): sha256(p.read_bytes()).hexdigest() for p in inputs}
if args.mode == 'tests':
    argv = [sys.executable, '-B', '-X', 'utf8', str(CANDIDATE / 'tests/test_ritual_weakening_302.py'), '-v']
else:
    argv = [sys.executable, '-B', '-X', 'utf8', str(CANDIDATE / 'scripts/build_ritual_weakening_302.py')]
    if args.mode == 'build': argv.append('--write')
env = os.environ.copy()
env['ROUGE_RITUAL_WEAKENING_MODULE'] = str(CANDIDATE / 'rouge/ritual_weakening.py')
env['PYTHONPATH'] = str(ROOT)
started = datetime.now(timezone.utc).isoformat()
result = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, timeout=180, check=False)
(out / 'stdout.txt').write_bytes(result.stdout)
(out / 'stderr.txt').write_bytes(result.stderr)
(out / 'process.exit').write_bytes((str(result.returncode) + '\n').encode('ascii'))
after = {p.relative_to(CANDIDATE).as_posix(): sha256(p.read_bytes()).hexdigest()
         for p in CANDIDATE.rglob('*') if p.is_file() and p.suffix not in ('.pyc',)}
record = {'kind': 'CACHE_AUTHOR_SOURCE_BUILD_OR_PURE_API_NOT_FORMAL_PRODUCT_ACCEPTANCE',
          'mode': args.mode, 'argv': argv, 'started_utc': started,
          'finished_utc': datetime.now(timezone.utc).isoformat(), 'exit_code': result.returncode,
          'source_sha256_before': before, 'source_sha256_after': after,
          'all_preexisting_inputs_unchanged': all(after.get(n) == v for n, v in before.items()),
          'Qt_game_chat_Git_live_private_operations': False}
(out / 'process.json').write_bytes((json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
