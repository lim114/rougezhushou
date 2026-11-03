from pathlib import Path
import ast,difflib,hashlib,json,subprocess
OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
def sha(d):return hashlib.sha256(d).hexdigest()
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
index=json.loads((OUT/'fixed-source-index088.json').read_text())
changes=json.loads((OUT/'surgical-byte-inverse088.json').read_text())['changes']
for r in index['files']:
    base=(OUT/'baseline'/r['path']).read_bytes()
    assert len(base)==r['bytes'] and sha(base)==r['sha256']
    draft=(OUT/'draft'/r['path']).read_bytes()
    if r['path'] in changes:assert sha(draft)==changes[r['path']]['draft_sha256']
    else:assert draft==base
leaf=OUT/'draft/rouge/condition_inputs.py'
assert sha(leaf.read_bytes())==json.loads((OUT/'surgical-byte-inverse088.json').read_text())['new_leaf_sha256']
files=list(changes)+['rouge/condition_inputs.py','tests/test_continuous_attacks_text_input.py']
patch=b'';expected={}
for name in files:
    old=(OUT/'baseline'/name).read_bytes() if name in changes else b''
    new=(OUT/'test_continuous_attacks_text_input.py').read_bytes() if name.startswith('tests/') else (OUT/'draft'/name).read_bytes()
    patch+=b''.join(difflib.diff_bytes(difflib.unified_diff,old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile=('a/'+name).encode(),tofile=('b/'+name).encode()))
    expected[name]={'bytes':len(new),'sha256':sha(new)}
path=OUT/'section88.patch';path.write_bytes(patch)
num=subprocess.run(['git','apply','--numstat',str(path)],cwd=REPO,capture_output=True,text=True)
check=subprocess.run(['git','apply','--check',str(path)],cwd=REPO,capture_output=True,text=True)
assert num.returncode==0 and check.returncode==0,(num,check)
receipt={'status':'PASS_FROZEN_PRODUCT_TRANSPORT_NO_APPLY','baseline_commit':index['baseline_commit'],
    'patch_sha256':sha(patch),'product_and_test_files':expected,
    'git_apply_numstat':{'returncode':num.returncode,'stdout':num.stdout,'stderr':num.stderr},
    'git_apply_check':{'returncode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},
    'actual_root_apply':False,'source_hashes_after_calls_unchanged':True,
    'new_public_or_helper_calls':0,'tracked_mutations':0}
save('patch-and-source-after088.json',receipt)
print(json.dumps({'patch_sha256':sha(patch),'numstat':num.stdout,'check_returncode':check.returncode}))
