"""Root-only integration of the frozen, independently reviewed maintenance tool."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess

repo = Path('/workspace/rougezhushou')
packet = Path('/workspace/.continuation/p2-animation-provenance-portability-090-draft')
out = repo / 'research/p2-animation-provenance-portability'
prior = '3a59aa0c3d09199caea14de3c5fe89781225a8d6'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=repo)

assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('rev-parse', 'HEAD').decode().strip() == prior
assert git('rev-parse', 'p2-section-089^{commit}').decode().strip() == prior
assert git('status', '--porcelain') == b''
assert not out.exists()
mf = packet / 'archivable-public-manifest-final090.json'
hand = packet / 'final-handoff090.json'
assert sha(mf.read_bytes()) == '00da4b9e91f7c7df701c62a246dcdbac337d25187a6d4f8ef7204d92a080603a'
assert sha(hand.read_bytes()) == '835b60126a4b2453ad8cd3310f1707f657a2d861a594d4f796c9146c656d9be5'
rows = json.loads(mf.read_bytes())['files']
assert len(rows) == 109 and sum(row['bytes'] for row in rows) == 4412868
seen = set()
for row in rows:
    name = PurePosixPath(row['archive_path'])
    assert not name.is_absolute() and '..' not in name.parts and str(name) == row['archive_path']
    assert str(name) not in ('', '.') and str(name) not in seen
    seen.add(str(name))
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], str(name)
freeze = json.loads((packet / 'review-freeze090.json').read_bytes())
assert sha((packet / 'review-freeze090.json').read_bytes()) == 'e0f5fd4f72a1fafbca959d06365e3eaab842713e3b76112bba56c65a4542b4a2'
transport = json.loads((packet / 'root89-transport090.json').read_bytes())
assert transport['root_baseline_commit'] == prior
patch = packet / 'product090.patch'
assert sha(patch.read_bytes()) == freeze['patch_sha256'] == 'b1ee652d8a60c69cfbd48ddeaf7c01b6b399b00fb11bcc6d2b691230b8a90660'
targets = {row['path']: row for row in freeze['product_files']}
assert set(targets) == {'README.md', 'scripts/verify_original_animation_provenance.py', 'tests/test_original_animation_provenance.py'}
old = {}
for name in git('ls-files', '-z', '--', 'rouge', 'tests', 'scripts').decode().split('\0'):
    if name and Path(name).suffix in ('.py', '.json') and '__pycache__' not in Path(name).parts:
        original = git('show', prior + ':' + name)
        assert (repo / name).read_bytes() == original, name
        old[name] = original
assert len(old) == 728
registry_name = 'scripts/verify_cloud.py'
registry_new = (packet / 'registered-verify_cloud090-root89.py').read_bytes()
assert sha(registry_new) == 'cdff7ab731bde134c3c7921cba0d5825983b446cbbbecf133a754f3e68c9e871'
literal = b'    "tests.test_original_animation_provenance",\n'
assert registry_new.count(literal) == 1 and registry_new.replace(literal, b'', 1) == old[registry_name]
for n in ['tests.test_continuous_attacks_text_input', 'tests.test_run_crew_count_boolean_input']:
    assert registry_new.count(('    "' + n + '",\n').encode()) == 1
assert (repo / 'README.md').read_bytes() == (packet / 'baseline/README.md').read_bytes() == git('show', prior + ':README.md')
for name, row in targets.items():
    raw = (packet / 'draft' / name).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
    if name != 'README.md':
        assert not (repo / name).exists() and name not in old and b'\r\n' not in raw
subprocess.run(['git', 'apply', '--check', str(patch)], cwd=repo, check=True)
subprocess.run(['git', 'apply', str(patch)], cwd=repo, check=True)
(repo / registry_name).write_bytes(registry_new)
for name, row in targets.items():
    raw = (repo / name).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name
for name in set(old) - {registry_name}:
    assert (repo / name).read_bytes() == old[name], name
assert set(git('diff', '--name-only').decode().splitlines()) == {'README.md', registry_name}
out.mkdir()
for row in rows:
    target = out / row['archive_path']
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(row['source_path'], target)
    raw = target.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
for file in [mf, hand]:
    if file.name in seen:
        assert (out / file.name).read_bytes() == file.read_bytes()
    else:
        shutil.copyfile(file, out / file.name)
receipt = {'passed': True, 'section': 90, 'actual_prior_commit': prior,
           'public_packet_files': 109, 'public_packet_bytes': 4412868,
           'all_public_source_destination_bytes_hashes_verified': True,
           'old_maintained_py_json': 728, 'unchanged_old_maintained_py_json': 727,
           'production_data_and_all_existing_gameplay_code_unchanged': True,
           'frozen_stdlib_CLI_new6_and_README_exact': True,
           'registry_one_module_inverse_exact_preserves88_89': True,
           'root_current_source_and_fresh_tests_pending': True,
           'new_CLI_verifier_API_helper_formatter_parser_network_Qt_Wine_calls': 0}
with (out / 'root-integration090.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
shutil.copyfile(__file__, out / Path(__file__).name)
shutil.copyfile('/workspace/.continuation/root-related-090.py', out / 'root-related-090.py')
print(json.dumps(receipt, ensure_ascii=False))
