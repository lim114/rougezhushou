"""Pure source-only post-apply checker; root supplies its actual pre89 commit.

Derived maintained py/json checker. The sealed original template is unchanged.
No project imports, constructors, helpers, APIs, tests, GUI or Wine calls.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--pre89-commit', required=True)
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
REPO = Path('/workspace/rougezhushou')
DRAFT = Path('/workspace/.continuation/p2-crew-count-boolean-089-draft')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


commit = git('rev-parse', '--verify', args.pre89_commit + '^{commit}').decode().strip()
assert commit == args.pre89_commit, 'Use an exact actual pre89 commit, not a moving ref.'
assert git('rev-parse', '--verify', 'refs/tags/p2-section-088^{commit}').decode().strip() == commit
assert git('rev-parse', 'HEAD').decode().strip() == commit
assert not args.receipt.exists()
freeze_path = DRAFT / 'draft-freeze089.json'
assert sha(freeze_path.read_bytes()) == '04c9567954f2b7bcd34c2abe1b2b616988400d4193943e94ec4e46e32a8cc248'
freeze = json.loads(freeze_path.read_bytes())
for item in freeze['files']:
    data = Path(item['source_path']).read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256']
product = 'rouge/run_state.py'
new_test = 'tests/test_run_crew_count_boolean_input.py'
registry = 'scripts/verify_cloud.py'
baseline_paths = set(git('ls-tree', '-r', '--name-only', '-z', commit).decode().split('\0')) - {''}
def maintained(path):
    return path.split('/', 1)[0] in ('rouge', 'tests', 'scripts') and Path(path).suffix in ('.py', '.json') and '__pycache__' not in path.split('/')
baseline_maintained = {p for p in baseline_paths if maintained(p)}
assert new_test not in baseline_paths
current_paths = set(git('ls-files', '-z', '--', 'rouge', 'tests', 'scripts').decode().split('\0')) - {''}
current_maintained = {p for p in current_paths if maintained(p)}
assert current_maintained == baseline_maintained | {new_test}, 'Unexpected maintained py/json source path change.'
old = git('show', commit + ':' + product)
assert sha(old) == freeze['source_run_state_old_sha256']
actual = (REPO / product).read_bytes()
assert actual == Path(freeze['files'][0]['source_path']).read_bytes()
line = b'        if isinstance(crew,bool):crew=None\r\n'
assert actual.count(line) == 1 and actual.replace(line, b'', 1) == old
assert b'\n' not in actual.replace(b'\r\n', b'')
test = (REPO / new_test).read_bytes()
assert test == Path(freeze['files'][1]['source_path']).read_bytes()
assert b'\r\n' not in test
old_registry = git('show', commit + ':' + registry)
token = b'MODULES = (\n'
module = b'    "tests.test_run_crew_count_boolean_input",\n'
assert old_registry.count(token) == 1 and module not in old_registry
module88 = b'    \"tests.test_continuous_attacks_text_input\",\n'
assert old_registry.count(module88) == 1
expected_registry = old_registry.replace(token, token + module, 1)
actual_registry = (REPO / registry).read_bytes()
assert actual_registry == expected_registry
assert actual_registry.count(module88) == 1
unchanged = []
for relative in sorted(baseline_maintained - {product, registry}):
    expected = git('show', commit + ':' + relative)
    data = (REPO / relative).read_bytes()
    assert data == expected, relative
    unchanged.append({'path': relative, 'bytes': len(data), 'sha256': sha(data)})
record = {
    'status': 'PASS_ROOT_CURRENT_SOURCE_ONLY', 'actual_pre89_commit': commit,
    'baseline_maintained_py_json': len(baseline_maintained), 'current_tracked_maintained_py_json': len(current_maintained),
    'other_baseline_maintained_py_json_unchanged': len(unchanged), 'unchanged_files': unchanged,
    'source38_original_run_state_sha256': freeze['source_run_state_old_sha256'],
    'product': {'path': product, 'bytes': len(actual), 'sha256': sha(actual),
                'inverse_exact_actual_pre89': True, 'CRLF': True},
    'new_test': {'path': new_test, 'bytes': len(test), 'sha256': sha(test), 'LF': True},
    'registry': {'path': registry, 'baseline_sha256': sha(old_registry),
                 'current_sha256': sha(actual_registry), 'exact_one_literal_insertion': True, 'actual88_module_preserved': True},
    'checker_sha256': sha(Path(__file__).read_bytes()), 'new_project_calls': 0,
    'scope': 'All maintained rouge/tests/scripts .py/.json source bytes relative to actual88. Research archive is separately hash/index-blob checked. No tests executed.'}
args.receipt.parent.mkdir(parents=True, exist_ok=True)
with args.receipt.open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({k: record[k] for k in ('status', 'actual_pre89_commit', 'baseline_maintained_py_json',
                                        'other_baseline_maintained_py_json_unchanged', 'new_project_calls')}))
