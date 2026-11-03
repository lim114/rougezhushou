"""Apply the sole frozen old-test adaptation; retain initial095 failure evidence."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
PACKET = LOCAL / 'p2-report095-token-duration-test-adaptation-v1'
MF = PACKET / 'public-artifacts-manifest-token-duration-adaptation095.json'
TEST = 'tests/test_token_duration_reference.py'
INITIAL_SHA = '57e80f30aa67384225c49fd16b58bd3289fe9df41e018feca242ce132d105b82'
MF_SHA = '6a580bed1e8e60a1782fb53495996b4f841626a77eea9292f10952acdd194fcc'
BEFORE = 'cea16b4243c949fd1749c1cab4f323b2f5ea7267ad69928e715ea570ab27e199'
AFTER = 'ad4a6381e6ec6f1a6db08cb1df0339b614883c960a1db3865d019ac08b12b554'
HEAD = 'f509d186e501bfcfd042e45b46e398ec756840ec'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def maintained():
    return {p.relative_to(ROOT).as_posix(): sha(p)
            for name in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / name).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json')
            and '__pycache__' not in p.parts}


review_path, review_sha = Path(sys.argv[1]), sys.argv[2]
assert review_path.resolve().is_relative_to(LOCAL / 'token-duration-test-adaptation095-formal-review')
assert sha(review_path) == review_sha
formal = json.loads(review_path.read_bytes())
assert formal['source_gate_passed'] is True and formal['runtime_pass'] is False
assert formal['test_manifest_sha256'] == MF_SHA
assert formal['before_test_sha256'] == BEFORE and formal['after_test_sha256'] == AFTER
assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT,
                               text=True).strip() == 'codex/p2-development'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                               text=True).strip() == HEAD
assert json.loads((ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes())['completed_sections'] == 94
initial_path = LOCAL / 'root-source-095.json'
assert sha(initial_path) == INITIAL_SHA
initial = json.loads(initial_path.read_bytes())
assert initial['passed'] is True and initial['section095_completed'] is False
assert maintained() == initial['source_sha256_after']
assert len(initial['source_sha256_after']) == 735
assert sha(MF) == MF_SHA
mf = json.loads(MF.read_bytes())
assert len(mf['files']) == 8 and len(mf['code_files']) == 1
for row in mf['files']:
    path = Path(row['source_path'])
    assert path.resolve().is_relative_to(PACKET)
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
row = mf['code_files'][0]
assert row['destination_repo_path'] == TEST
assert row['before_sha256'] == BEFORE and row['sha256'] == AFTER
old = (ROOT / TEST).read_bytes()
new = Path(row['source_path']).read_bytes()
assert hashlib.sha256(old).hexdigest() == BEFORE
inverse_path = PACKET / 'exact-inverse-token-duration095.json'
assert sha(inverse_path) == '2d1eb27fa3f4067beb813815c547acaa94f23084ff37290f354aae1e06f0fa5d'
inverse = json.loads(inverse_path.read_bytes())
assert len(inverse['edits']) == 2 and inverse['new_test_methods'] == 0
restored = new
for edit in reversed(inverse['edits']):
    before, after = edit['old'].encode(), edit['new'].encode()
    assert restored.count(after) == 1
    restored = restored.replace(after, before, 1)
assert restored == old
old_methods = [node for node in ast.walk(ast.parse(old))
               if isinstance(node, ast.FunctionDef)]
new_methods = [node for node in ast.walk(ast.parse(new))
               if isinstance(node, ast.FunctionDef)]
assert [node.name for node in old_methods] == [node.name for node in new_methods]
changed = [a.name for a, b in zip(old_methods, new_methods)
           if ast.dump(a) != ast.dump(b)]
assert changed == ['test_all_public_numeric_stats_damage_and_clocks_are_unchanged']
failure_binding = json.loads((PACKET / 'root-failure-source-binding095.json').read_bytes())
for key in ('root_original_guard', 'root_original_failed_log', 'root_captured_primary_rc'):
    evidence = failure_binding[key]
    assert sha(Path(evidence['path'])) == evidence['sha256']
assert Path(failure_binding['root_captured_primary_rc']['path']).read_bytes() == b'1\n'
assert failure_binding['failed_subtests'] == 52
core_mf = LOCAL / 'p2-report095-candidate-v1/public-code-artifacts-manifest095.json'
assert sha(core_mf) == '216d5c31a9bc89dbc51f0b875db073a4fe8ea8b85fb5c9b624f5d9d6f56a461a'
core_rows = json.loads(core_mf.read_bytes())['files']
assert len(core_rows) == 5
for core in core_rows:
    assert sha(ROOT / core['destination_repo_path']) == core['sha256']
    assert sha(Path(core['source_path'])) == core['sha256']
guard_path = LOCAL / 'root-source-095-v2.json'
receipt_path = LOCAL / 'root-token-duration-test-applied095.json'
assert not guard_path.exists() and not receipt_path.exists()
expected = dict(initial['source_sha256_after'])
expected[TEST] = AFTER
(ROOT / TEST).write_bytes(new)
actual = maintained()
assert actual == expected and len(actual) == 735
base = json.loads((LOCAL / 'root-source-094.json').read_bytes())['source_sha256_after']
old_changes = sorted(name for name in base if base[name] != actual[name])
assert old_changes == ['rouge/reporting.py', 'scripts/verify_cloud.py', TEST]
assert sorted(set(actual) - set(base)) == sorted(initial['new_maintained'])
guard = copy.deepcopy(initial)
guard.update(source_sha256_after=actual, unchanged_maintained=729,
             changed_maintained=old_changes,
             original_initial095_source_guard={'path': str(initial_path), 'sha256': INITIAL_SHA},
             exact_single_old_test_adaptation={'manifest_path': str(MF), 'manifest_sha256': MF_SHA,
                 'formal_review_path': str(review_path), 'formal_review_sha256': review_sha,
                 'destination_repo_path': TEST, 'before_sha256': BEFORE, 'after_sha256': AFTER,
                 'new_test_methods': 0, 'whole_file_inverse_exact': True},
             original_failed_selected_evidence_preserved=failure_binding,
             root_fresh_selected_after_adaptation_pass=False)
save(guard_path, guard)
save(receipt_path, {'format_version': 1, 'passed': True, 'root_only_apply': True,
     'applied_paths': [TEST], 'core_five_unchanged': True,
     'current_maintained': 735, 'unchanged_relative_actual94': 729,
     'source_guard_path': str(guard_path), 'source_guard_sha256': sha(guard_path),
     'formal_review_path': str(review_path), 'formal_review_sha256': review_sha,
     'project_calls': 0, 'section095_completed': False, 'full095_runtime_PASS': False})
print(json.dumps({'applied': [TEST], 'core_five_unchanged': True,
                  'current_maintained': 735, 'unchanged_relative_actual94': 729,
                  'source_guard_sha256': sha(guard_path), 'section095_completed': False}))
