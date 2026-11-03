"""Root-only read-only check after applying section88; no project imports/calls."""
from pathlib import Path
import argparse,ast,hashlib,json,subprocess

parser=argparse.ArgumentParser()
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--expected-prior-revision',required=True)
parser.add_argument('--expected-patch-sha',required=True)
args=parser.parse_args()
OUT=Path(__file__).resolve().parent
repo=args.repo.resolve()
sha=lambda data:hashlib.sha256(data).hexdigest()
index=json.loads((OUT/'fixed-source-index088.json').read_text())
inverse=json.loads((OUT/'surgical-byte-inverse088.json').read_text())
transport=json.loads((OUT/'patch-and-source-after088.json').read_text())
assert sha((OUT/'section88.patch').read_bytes())==args.expected_patch_sha==transport['patch_sha256']
changed=inverse['changes']
for row in index['files']:
    name=row['path']
    prior=subprocess.check_output(['git','show',args.expected_prior_revision+':'+name],cwd=repo)
    assert len(prior)==row['bytes'] and sha(prior)==row['sha256'],('prior drift',name)
    current=(repo/name).read_bytes()
    if name in changed:
        assert sha(current)==changed[name]['draft_sha256'],('product drift',name)
        restored=current
        for edit in reversed(changed[name]['edits']):
            before=bytes.fromhex(edit['before_hex']);after=bytes.fromhex(edit['after_hex'])
            assert restored.count(after)==edit['count']
            restored=restored.replace(after,before)
        assert restored==prior,('inverse drift',name)
    else:assert current==prior,('unchanged drift',name)
for name,record in transport['product_and_test_files'].items():
    current=(repo/name).read_bytes()
    assert (len(current),sha(current))==(record['bytes'],record['sha256']),name
    ast.parse(current.decode('utf-8'))
body=ast.parse((repo/'rouge/damage.py').read_text())
core=next(n for n in body.body if isinstance(n,ast.FunctionDef) and n.name=='_evaluate_damage_once')
assert [ast.unparse(d) for d in core.decorator_list]==['validate_continuous_attacks']
assert isinstance(core.body[-1],ast.Return) and isinstance(core.body[-1].value,ast.Name) and core.body[-1].value.id=='result'
leaf=(repo/'rouge/condition_inputs.py').read_text()
assert '_pending.reset(token)' in leaf and "default=None" in leaf
print(json.dumps({'status':'PASS_ROOT_CURRENT_SOURCE_ONLY','expected_prior_revision':args.expected_prior_revision,
    'fixed_prior_files':len(index['files']),'unchanged_prior_files':len(index['files'])-len(changed),
    'six_exact_byte_inverses':True,'new_leaf_and_test_exact':True,'patch_sha256':args.expected_patch_sha,
    'new_project_calls':0,'tracked_mutations':0}))
