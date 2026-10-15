"""Preserve the real first profile process result and exact review sources."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=HERE/'first-real-bench'
OUT.mkdir(exist_ok=False)
files={}
for name in ('before-event-planning.py','candidate-event-planning.py','compare_public_queries.py','prepare_candidate.py'):
    raw=(HERE/name).read_bytes()
    (OUT/name).write_bytes(raw)
    files[name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
command=[sys.executable,'-B','-X','utf8',str(HERE/'compare_public_queries.py')]
try:
    run=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=180)
    stdout,stderr,code,timed_out=run.stdout,run.stderr,run.returncode,False
except subprocess.TimeoutExpired as error:
    stdout,stderr,code,timed_out=error.stdout or b'',error.stderr or b'',None,True
(OUT/'stdout.txt').write_bytes(stdout)
(OUT/'stderr.txt').write_bytes(stderr)
receipt={'scope':'First actual public query/profile process; not GUI/full/OCR speed proof.',
    'command':command,'exit_code':code,'timed_out':timed_out,'timeout_seconds':180,'sources_before':files}
(OUT/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(stdout.decode('utf-8',errors='replace'))
print(stderr.decode('utf-8',errors='replace'))
print(json.dumps({'exit_code':code,'timed_out':timed_out,'receipt':str(OUT/'receipt.json')},ensure_ascii=False))
raise SystemExit(1 if timed_out else code)
