import hashlib,json
from pathlib import Path
root=Path('/workspace/rougezhushou');log=Path('/workspace/.continuation/root-selected-080.log');r=json.loads(log.read_text().strip().splitlines()[-1]);assert r['passed'] and r['failures']==r['errors']==0
files={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('rouge','tests','scripts') for p in sorted((root/folder).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
receipt={'section':80,'selected_checks_completed':r,'selected_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'source_sha256_after_completed_selected_checks':files,'new_selected_execution_in_this_snapshot':False}
out=Path('/workspace/.continuation/root-selected-source-snapshot080.json')
with out.open('x') as f:f.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':True,'source_files':len(files),'selected_tests':r['tests_run']}))
