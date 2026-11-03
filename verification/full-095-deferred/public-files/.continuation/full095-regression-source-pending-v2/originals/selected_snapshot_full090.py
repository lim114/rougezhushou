"""Record and reuse completed root selected checks only at identical source bytes."""
import hashlib,json,shutil,sys
from pathlib import Path
phase=sys.argv[1];number=int(sys.argv[2]);suffix=f'{number:03d}'
root=Path('/workspace/rougezhushou');local=Path('/workspace/.continuation')
snapshot=local/f'root-selected-source-snapshot{suffix}.json';log=local/f'root-selected-{suffix}.log'
sha=lambda b:hashlib.sha256(b).hexdigest()
if phase=='snapshot':
 r=json.loads(log.read_text().strip().splitlines()[-1]);assert r['passed'] and r['failures']==r['errors']==0
 files={p.relative_to(root).as_posix():sha(p.read_bytes()) for folder in ('rouge','tests','scripts') for p in sorted((root/folder).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
 receipt={'section':number,'selected_checks_completed':r,'selected_log_sha256':sha(log.read_bytes()),'source_sha256_after_completed_selected_checks':files,'new_selected_execution_in_this_snapshot':False}
 with snapshot.open('x') as f:f.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'passed':True,'source_files':len(files),'selected_tests':r['tests_run'],'no_new_selected_execution':True}))
elif phase=='reuse':
 ctx=json.loads(Path(f'/workspace/.compat/wine-validation-{suffix}-context.json').read_text());r=json.loads(snapshot.read_text())
 assert ctx['source_sha256']==r['source_sha256_after_completed_selected_checks']
 assert sha(log.read_bytes())==r['selected_log_sha256'];assert r['selected_checks_completed']['passed'];assert not (local/f'selected-{suffix}.log').exists()
 shutil.copyfile(log,local/f'selected-{suffix}.log')
 proof={'passed':True,'source_files_verified':len(ctx['source_sha256']),'full_frozen_commit':ctx['commit'],'reused_completed_root_selected_section':number,'reused_selected_log_sha256':r['selected_log_sha256'],'fresh_selected_tests_executed_for_full':False,'reason':'Every maintained product/test/script source byte matches completed selected-check snapshot; subsequent section commit only records metadata/evidence.'}
 with (local/f'linux-selected-{suffix}-byte-identity.json').open('x') as f:f.write(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(proof))
else:raise ValueError(phase)
