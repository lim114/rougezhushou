"""Archive the actual first necessary correction test run, never old28 credit."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = BASE / 'first-real-correction'
OUT.mkdir(exist_ok=False)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
core = BASE / 'rouge/panel_native_finalization.py'
test = BASE / 'verify_correction_283.py'
for src in (core, test, Path(__file__)):
    shutil.copyfile(src, OUT / src.name)
before = sha(core)
started = time.time()
argv = [str(ROOT / '.venv/Scripts/python.exe'), '-X', 'utf8', str(test)]
result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=90)
(OUT / 'stdout.txt').write_bytes(result.stdout)
(OUT / 'stderr.txt').write_bytes(result.stderr)
report = {'argv': argv, 'actual_exit': result.returncode, 'elapsed_seconds': time.time() - started,
          'core_sha256_before': before, 'core_sha256_after': sha(core), 'test_sha256': sha(test),
          'stdout_sha256': sha(OUT / 'stdout.txt'), 'stderr_sha256': sha(OUT / 'stderr.txt'),
          'old28_not_rerun_or_credited_to_new_core': True,
          'game_or_chat_accessed': False, 'production_modified': False}
(OUT / 'process.json').write_bytes((json.dumps(report, indent=2) + '\n').encode('utf8'))
print(json.dumps(report))
print(result.stderr.decode('utf8'))
raise SystemExit(result.returncode)
