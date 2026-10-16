"""One isolated pure-Python author run; preserve first sources and raw result."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE = HERE / 'candidate'
OUT = HERE / 'author-tests-first'
OUT.mkdir(exist_ok=False)
PACK = CANDIDATE / 'research/p3-map-direct-ground-303'
BUILDER = CANDIDATE / 'scripts/extend_direct_landmark_303.py'
TEST = CANDIDATE / 'tests/test_direct_landmark_303.py'
shutil.copyfile(HERE / 'build-first/fixed-landmark-references.json', CANDIDATE / 'rouge/data/fixed-landmark-references.json')
sources = [CANDIDATE / relative for relative in json.loads((PACK / 'source-manifest.json').read_bytes())['files']]
sources += [PACK / 'source-manifest.json', BUILDER, TEST, CANDIDATE / 'rouge/data/fixed-landmark-references.json',
            ROOT / 'rouge/fixed_landmark_mapping.py', ROOT / 'rouge/map_projection.py',
            ROOT / 'scripts/extend_direct_landmark_294.py']


def pins():
    return {str(path.relative_to(ROOT)).replace('\\', '/'):
            {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size} for path in sources}


before = pins()
for path in (BUILDER, TEST):
    shutil.copyfile(path, OUT / path.name)
(OUT / 'source-before.json').write_bytes((json.dumps(before, indent=2) + '\n').encode())
env = dict(os.environ)
env['ROUGE_303_BUILDER_FILE'] = str(BUILDER)
code = 'import sys,runpy;sys.path.insert(0,' + repr(str(ROOT)) + ');runpy.run_path(' + repr(str(TEST)) + ',run_name="__main__")'
command = [sys.executable, '-c', code]
start = time.monotonic()
result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=240)
(OUT / 'stdout.log').write_bytes(result.stdout)
(OUT / 'stderr.log').write_bytes(result.stderr)
(OUT / 'process.exit').write_bytes(str(result.returncode).encode())
after = pins()
(OUT / 'source-after.json').write_bytes((json.dumps(after, indent=2) + '\n').encode())
receipt = {'kind': 'SECTION303_FIRST_ACTUAL_PURE_AUTHOR_TESTS_NOT_PRODUCT_OR_NATIVE_ACCEPTANCE',
           'actual_exit': result.returncode, 'elapsed_seconds': time.monotonic() - start,
           'command': command, 'candidate_builder_explicit_env': str(BUILDER.relative_to(ROOT)).replace('\\', '/'),
           'source_count': len(before), 'source_before_after_equal': before == after,
           'Qt_or_game_or_chat': False, 'production_modified': False}
(OUT / 'process.json').write_bytes((json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode())
print(json.dumps(receipt, ensure_ascii=False))
print(result.stderr.decode('utf8', errors='replace'))
sys.exit(result.returncode if before == after else 3)
