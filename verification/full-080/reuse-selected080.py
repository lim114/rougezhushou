import hashlib,json,shutil
from pathlib import Path
local=Path('/workspace/.continuation');ctx=json.loads(Path('/workspace/.compat/wine-validation-080-context.json').read_text());r=json.loads((local/'root-selected-source-snapshot080.json').read_text())
assert ctx['source_sha256']==r['source_sha256_after_completed_selected_checks']
log=local/'root-selected-080.log';assert hashlib.sha256(log.read_bytes()).hexdigest()==r['selected_log_sha256'];assert r['selected_checks_completed']['passed'];assert not (local/'selected-080.log').exists()
shutil.copyfile(log,local/'selected-080.log')
proof={'passed':True,'source_files_verified':len(ctx['source_sha256']),'full_frozen_commit':ctx['commit'],'reused_completed_root_section80_selected_log_sha256':r['selected_log_sha256'],'fresh_selected_tests_executed_for_full080':False,'reason':'Every maintained product/test/script source byte matches the completed section80 selected-check snapshot; subsequent section commit only records metadata/evidence.'}
(local/'linux-selected-080-byte-identity.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(json.dumps(proof))
