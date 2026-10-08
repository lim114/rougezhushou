"""Append-only registry/source-file proposal; author review freeze stays intact."""
from pathlib import Path
import difflib,hashlib,json,subprocess
OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
REV='6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0'
sha=lambda data:hashlib.sha256(data).hexdigest()
old=subprocess.check_output(['git','show',REV+':scripts/verify_cloud.py'],cwd=REPO)
assert (REPO/'scripts/verify_cloud.py').read_bytes()==old
assert b'\r' not in old
entry=b'    "tests.test_continuous_attacks_text_input",\n'
anchor=b'MODULES = (\n'
assert old.count(anchor)==1 and entry not in old
new=old.replace(anchor,anchor+entry)
assert new.replace(entry,b'')==old
patch=b''.join(difflib.diff_bytes(difflib.unified_diff,old.splitlines(keepends=True),new.splitlines(keepends=True),
    fromfile=b'a/scripts/verify_cloud.py',tofile=b'b/scripts/verify_cloud.py'))
(OUT/'registryproposal088.patch').write_bytes(patch)
check=subprocess.run(['git','apply','--check',str(OUT/'registryproposal088.patch')],cwd=REPO,capture_output=True,text=True)
assert check.returncode==0
proposal={'status':'SINGLE_ENTRY_PROPOSAL_ONLY_NOT_APPLIED','prior_revision':REV,'path':'scripts/verify_cloud.py',
    'entry':'tests.test_continuous_attacks_text_input','exact_inserted_bytes_hex':entry.hex(),
    'anchor_hex':anchor.hex(),'line_endings':'LF','old_bytes':len(old),'old_sha256':sha(old),
    'new_bytes':len(new),'new_sha256':sha(new),'inverse_exact':True,
    'patch_sha256':sha(patch),'readonly_apply_check':{'returncode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},
    'root_apply':False,'new_project_calls':0}
(OUT/'registryproposal088.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n')
products=json.loads((OUT/'patch-and-source-after088.json').read_text())['product_and_test_files']
rows=[]
for name,record in products.items():
    prior=(OUT/'baseline'/name).read_bytes() if (OUT/'baseline'/name).exists() else None
    current=(OUT/'test_continuous_attacks_text_input.py').read_bytes() if name.startswith('tests/') else (OUT/'draft'/name).read_bytes()
    assert (len(current),sha(current))==(record['bytes'],record['sha256'])
    rows.append({'path':name,'old_sha256':sha(prior) if prior is not None else None,
                 'old_bytes':len(prior) if prior is not None else None,'new_sha256':record['sha256'],'new_bytes':record['bytes'],
                 'line_endings':'CRLF' if b'\r\n' in current else 'LF','new_file':prior is None})
rows.append({'path':proposal['path'],'old_sha256':sha(old),'old_bytes':len(old),'new_sha256':sha(new),
    'new_bytes':len(new),'line_endings':'LF','new_file':False,'transport':'registryproposal088.patch'})
(OUT/'named-source-files088.json').write_text(json.dumps({'format_version':1,'status':'EXPLICIT_ROOT_TRANSPORT_FILE_PROPOSAL',
    'files':rows,'root_apply':False,'frozen_product_patch_unchanged':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'registry_old_sha256':sha(old),'registry_new_sha256':sha(new),
    'registry_patch_sha256':sha(patch),'files':len(rows),'new_project_calls':0}))
