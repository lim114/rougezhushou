"""Capture a pure section300 source build or backend test with exact public inputs."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('command',nargs=argparse.REMAINDER)
args=parser.parse_args()
out=HERE/args.name
out.mkdir(exist_ok=False)
root=HERE/'candidate'
paths=sorted(p for p in root.rglob('*') if p.is_file())
before={str(p.relative_to(root)).replace('\\','/'):{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in paths}
for p in paths:
 if p.suffix=='.py':
  dest=out/'source-before'/p.relative_to(root)
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
cmd=[sys.executable,'-B','-X','utf8',*args.command]
start=time.monotonic();stamp=datetime.now(timezone.utc).isoformat()
with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
 result=subprocess.run(cmd,cwd=root,stdout=stdout,stderr=stderr,check=False)
after={str(p.relative_to(root)).replace('\\','/'):{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in root.rglob('*') if p.is_file()}
receipt={'kind':'PURE_PUBLIC_SOURCE_OR_BACKEND_JOB_NOT_PRODUCT_OR_NATIVE_ACCEPTANCE','command':cmd,
 'started_at':stamp,'elapsed_seconds':time.monotonic()-start,'exit_code':result.returncode,
 'source_before':before,'source_after':after,'sources_unchanged':before==after,
 'Qt_game_chat_Git_private_operations':False}
(out/'process.json').write_bytes((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
(out/'process.exit').write_bytes((str(result.returncode)+'\n').encode('ascii'))
print(json.dumps({'directory':str(out),'exit_code':result.returncode,'sources_unchanged':before==after},ensure_ascii=False))
raise SystemExit(result.returncode)
