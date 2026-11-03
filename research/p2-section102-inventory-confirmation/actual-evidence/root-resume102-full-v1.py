"""Root real maintained full217 entrypoint with independent746+CORE guard."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root=Path('/workspace/rougezhushou');base=Path('/workspace/.continuation')
sys.path.insert(0,str(base/'section102-window-source-v2'))
from native_evidence import source_map
guard_raw=(base/'resume102-applied-source-v1.json').read_bytes();guard=json.loads(guard_raw)
before=source_map(root);assert before==guard['source_sha256'] and len(before)==746
extra=guard['source_additional_sha256']
for name,want in extra.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==want
receipt_path=base/'resume102-full-linux-v1.json'
result=subprocess.run([sys.executable,str(root/'scripts/verify_full_available.py'),'--output',str(receipt_path)],cwd=root)
with (base/'resume102-full-linux-v1.child-exit-code').open('x') as stream:stream.write(str(result.returncode)+'\n')
after=source_map(root);after_extra={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in extra}
receipt={'source_before':before,'source_after':after,'source_guard_sha256':hashlib.sha256(guard_raw).hexdigest(),
         'source_additional_before':extra,'source_additional_after':after_extra,'child_primary_exit':result.returncode,
         'source_drift':[key for key in set(before)|set(after) if before.get(key)!=after.get(key)],
         'source_files':746,'maintained_full_entrypoint':True}
with (base/'resume102-full-linux-guard-v1.json').open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
assert not receipt['source_drift'] and after_extra==extra
if result.returncode==0:
    actual=json.loads(receipt_path.read_bytes());assert actual['available_checks_passed'] is True and len(actual['selectors'])==217
sys.exit(result.returncode)
