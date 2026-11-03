"""Verify immutable author inputs and freeze the independent execution ledger."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')
CURRENT = Path('/workspace/rougezhushou')
BASELINE = AUTHOR / 'baseline'
DRAFT = AUTHOR / 'draft'
sha = lambda b: hashlib.sha256(b).hexdigest()


def bind(path):
    b = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(b), 'sha256': sha(b)}


mf = AUTHOR / 'author-review-public-manifest088.json'
hf = AUTHOR / 'author-review-handoff088.json'
rf = AUTHOR / 'review-freeze088.json'
assert sha(mf.read_bytes()) == '4772c026843a995921c6013fb435fd547e2cb5a67d8f4f6e73245b7e5dbcc445'
assert sha(hf.read_bytes()) == '7092e9b91019882657f797fc25aa89a2c9337fe1b19e5b40b60b730ae441e7b8'
assert sha(rf.read_bytes()) == '10e5e8bcbc3e6a8a74e838d5ddd12638a3574230385a876a0c6d03a7c98baf99'
author_manifest = json.loads(mf.read_bytes())
assert author_manifest['format_version'] == 1
assert len(author_manifest['files']) == 89
assert sum(x['bytes'] for x in author_manifest['files']) == 1871550
for row in author_manifest['files']:
    path = Path(row['source_path'])
    assert path.is_absolute() and path.is_relative_to(AUTHOR)
    assert row['archive_path'] == str(path.relative_to(AUTHOR))
    assert bind(path) == {k: row[k] for k in ('source_path', 'bytes', 'sha256')}
author = json.loads(rf.read_bytes())
assert author['status'] == 'EXPLICIT_SOURCE_PRODUCT_TEST_MATRIX_FROZEN_FOR_FORMAL_REVIEW'
source_index = json.loads((AUTHOR / 'fixed-source-index088.json').read_bytes())
assert source_index['file_count'] == len(source_index['files']) == 125
baseline_bindings = []
draft_bindings = []
current_bindings = []
for row in source_index['files']:
    relative = row['path']
    old = (BASELINE / relative).read_bytes()
    assert len(old) == row['bytes'] and sha(old) == row['sha256']
    assert (CURRENT / relative).read_bytes() == old
    baseline_bindings.append({k: row[k] for k in ('path', 'bytes', 'sha256')})
    current_bindings.append({k: row[k] for k in ('path', 'bytes', 'sha256')})
    current = (DRAFT / relative).read_bytes()
    if relative in author['product_and_test_files']:
        expected = author['product_and_test_files'][relative]
        assert len(current) == expected['bytes'] and sha(current) == expected['sha256']
    else:
        assert current == old
    draft_bindings.append({'path': relative, 'bytes': len(current), 'sha256': sha(current)})
for relative, expected in author['product_and_test_files'].items():
    data = (DRAFT / relative).read_bytes()
    assert len(data) == expected['bytes'] and sha(data) == expected['sha256']
    if relative not in {r['path'] for r in draft_bindings}:
        draft_bindings.append({'path': relative, **expected})
test = DRAFT / 'tests/test_continuous_attacks_text_input.py'
assert test.read_bytes() == (AUTHOR / 'test_continuous_attacks_text_input.py').read_bytes()
methods = [node.name for node in ast.walk(ast.parse(test.read_bytes()))
           if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
assert len(methods) == 8
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=CURRENT, text=True).strip()
assert head == '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0'
assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=CURRENT, text=True) == ''
patch = AUTHOR / 'section88.patch'
assert sha(patch.read_bytes()) == author['patch_sha256']
checked = subprocess.run(['git', 'apply', '--check', str(patch)], cwd=CURRENT, capture_output=True, text=True)
assert checked.returncode == 0, checked.stderr
plan = OUT / 'formal-risk-plan088.json'
assert sha(plan.read_bytes()) == 'ba462ddef13b9a10866c2c157a2987a138feb71a4e557b3f21dbb6f226d8fa71'
assert sha((OUT / 'formal-risk-plan088-original-before-retirement-check.json').read_bytes()) == 'd854efa8b2e287584b1e9b8c21da42bbc04d85a98e410f786738f766c84869f4'
assert len(json.loads(plan.read_bytes())['cases']) == 8
target = OUT / 'formal-execution-freeze088.json'
assert not target.exists()
receipt = {'format_version': 1, 'status': 'AUTHOR_FINAL_AND_INDEPENDENT_EXECUTION_FROZEN',
           'author_manifest': bind(mf), 'author_handoff': bind(hf), 'author_freeze': bind(rf),
           'author_manifest_verified_files': 89, 'author_manifest_verified_bytes': 1871550,
           'current_root_commit': head, 'baseline_commit': author['baseline_revision'],
           'archive_closure_drift': '125 enumerated maintained rouge source bytes exactly unchanged from1ce at619.',
           'baseline_execution_root': str(BASELINE), 'draft_execution_root': str(DRAFT),
           'baseline_source_bindings': baseline_bindings, 'draft_source_bindings': draft_bindings,
           'current_root_source_bindings': current_bindings, 'plan_sha256': sha(plan.read_bytes()),
           'patch': bind(patch), 'current_root_apply_check': {'returncode': checked.returncode, 'stderr': checked.stderr},
           'new_test_sha256': sha(test.read_bytes()), 'new_test_methods': methods,
           'fresh_public_risk_calls_budget': 16, 'fresh_new_tests_explicit_public_budget': 32,
           'fresh_new_tests_explicit_context_helper_budget': 32,
           'project_calls_before_freeze': 0, 'tests_before_freeze': 0,
           'all_previous_frozen_directories_immutable': True}
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'source_packets': 89,
                  'baseline_sources': len(baseline_bindings), 'draft_sources': len(draft_bindings),
                  'fresh_calls_so_far': 0, 'freeze_sha256': sha(target.read_bytes())}))
