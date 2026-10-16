from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
CANDIDATE = BASE / 'candidate'
DEST = BASE / 'backend-first'
DEST.mkdir(exist_ok=False)
source = {p.relative_to(CANDIDATE).as_posix(): sha256(p.read_bytes()).hexdigest()
          for p in CANDIDATE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
for name in ('rouge/spawn_candidates.py', 'tests/test_spawn_candidates_299.py',
             'scripts/build_spawn_candidates_299.py', 'research/p3-spawn-candidates-299/source-manifest.json'):
    target = DEST / 'original-source' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((CANDIDATE / name).read_bytes())
argv = [sys.executable, '-B', '-X', 'utf8', str(CANDIDATE / 'tests/test_spawn_candidates_299.py'),
        '--module-file', str(CANDIDATE / 'rouge/spawn_candidates.py'), '-v']
start = time.time()
try:
    completed = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
    stdout, stderr, code, timed_out = completed.stdout, completed.stderr, completed.returncode, False
except subprocess.TimeoutExpired as error:
    stdout, stderr, code, timed_out = error.stdout or b'', error.stderr or b'', 124, True
after = {p.relative_to(CANDIDATE).as_posix(): sha256(p.read_bytes()).hexdigest()
         for p in CANDIDATE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
(DEST / 'stdout.txt').write_bytes(stdout)
(DEST / 'stderr.txt').write_bytes(stderr)
(DEST / 'process.exit').write_bytes((str(code) + '\n').encode())
receipt = {'kind': 'CACHE_CANDIDATE_PURE_BACKEND_TESTS_NOT_PRODUCT_ACCEPTANCE', 'argv': argv,
           'exit_code': code, 'timed_out': timed_out, 'elapsed_seconds': time.time() - start,
           'source_sha256_before': source, 'source_sha256_after': after,
           'source_unchanged': source == after, 'Qt_or_game_or_chat_executed': False,
           'production_modified': False}
(DEST / 'process.json').write_bytes((json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({k: v for k, v in receipt.items() if not k.startswith('source_sha256')}, ensure_ascii=False))
print(stderr.decode('utf8', errors='replace'))
sys.exit(code)
