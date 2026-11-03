"""Capture actual isolated source-build/API-test processes, never Qt or live writes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE = HERE / 'candidate'
mode, label = sys.argv[1:]
receipt_dir = HERE / label
receipt_dir.mkdir(exist_ok=False)
if mode == 'build':
    source = CANDIDATE / 'scripts/build_event_node_requirements_298.py'
    shutil.copyfile(source, receipt_dir / source.name)
    argv = [sys.executable,'-B','-X','utf8',str(source),'--root',str(ROOT),
        '--original-topic',str(ROOT/'.cache/p3-287-event-research/fixed-game-topic.json'),
        '--output-root',str(CANDIDATE)]
    cwd = ROOT
elif mode == 'tests':
    source = CANDIDATE / 'tests/test_event_node_requirements_298.py'
    shutil.copyfile(source, receipt_dir / source.name)
    shutil.copyfile(CANDIDATE/'rouge/event_node_requirements.py',receipt_dir/'event_node_requirements.py')
    argv = [sys.executable,'-B','-X','utf8','-m','unittest','discover','-s','tests','-p',source.name,'-v']
    cwd = CANDIDATE
else:
    raise ValueError('Only isolated build or pure API tests are supported.')
start = time.time()
result = subprocess.run(argv,cwd=cwd,capture_output=True)
(receipt_dir/'stdout').write_bytes(result.stdout)
(receipt_dir/'stderr').write_bytes(result.stderr)
receipt = {'kind':'cache-candidate-process-not-product-acceptance','argv':argv,'cwd':str(cwd),
    'exit_code':result.returncode,'started_unix':start,'elapsed_seconds':time.time()-start,
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(result.stderr).hexdigest(),
    'Qt_GUI_game_chat_private_state_Git_mutation':False}
(receipt_dir/'process.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(receipt,ensure_ascii=False))
print(result.stdout.decode('utf8'));print(result.stderr.decode('utf8'))
sys.exit(result.returncode)
