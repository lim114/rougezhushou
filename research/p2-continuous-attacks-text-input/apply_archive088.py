"""Sole root integration after the sealed independent section-088 review."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys

repo = Path('/workspace/rougezhushou')
packet = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')
out = repo / 'research/p2-continuous-attacks-text-input'
spec = json.loads(Path(sys.argv[1]).read_bytes())
prior = '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=repo)

assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('rev-parse', 'HEAD').decode().strip() == prior
assert git('status', '--porcelain') == b''
assert not out.exists()
mf, hand = (packet / spec[key] for key in ('manifest_name', 'handoff_name'))
assert digest(mf.read_bytes()) == spec['manifest_sha256']
assert digest(hand.read_bytes()) == spec['handoff_sha256']
rows = json.loads(mf.read_bytes())['files']
assert len(rows) == spec['files'] and sum(row['bytes'] for row in rows) == spec['bytes']
seen = set()
for row in rows:
    name = PurePosixPath(row['archive_path'])
    assert not name.is_absolute() and '..' not in name.parts and str(name) == row['archive_path']
    assert str(name) not in seen
    seen.add(str(name))
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], str(name)
freeze = json.loads((packet / 'review-freeze088.json').read_bytes())
assert digest((packet / 'review-freeze088.json').read_bytes()) == '10e5e8bcbc3e6a8a74e838d5ddd12638a3574230385a876a0c6d03a7c98baf99'
patch = packet / 'section88.patch'
assert digest(patch.read_bytes()) == freeze['patch_sha256'] == '6cad7ce79a0458e494cb975d3670b404c98f004227f97bb975e87b14fffd9627'
targets = freeze['product_and_test_files']
old = {}
for name in git('ls-files', '-z', '--', 'rouge', 'tests', 'scripts').decode().split('\0'):
    if name and Path(name).suffix in ('.py', '.json') and '__pycache__' not in Path(name).parts:
        original = git('show', prior + ':' + name)
        assert (repo / name).read_bytes() == original, name
        old[name] = original
assert len(old) == 725
registry_name = 'scripts/verify_cloud.py'
registry_old = old[registry_name]
literal = b'    "tests.test_continuous_attacks_text_input",\n'
assert literal not in registry_old and registry_old.count(b'MODULES = (\n') == 1
registry_new = registry_old.replace(b'MODULES = (\n', b'MODULES = (\n' + literal, 1)
assert registry_new.replace(literal, b'', 1) == registry_old
assert digest(registry_new) == '87a00479deba7406b7355348cd9721ef810d042b76c10cc46983939de01e7034'
named = json.loads((packet / 'named-source-files088.json').read_bytes())['files']
assert {row['path'] for row in named} == set(targets) | {registry_name}
for row in named:
    name = row['path']
    original = old.get(name)
    assert (original is None) == row['new_file']
    assert (None if original is None else len(original)) == row['old_bytes']
    assert (None if original is None else digest(original)) == row['old_sha256']
for name, row in targets.items():
    source = packet / 'test_continuous_attacks_text_input.py' if name == 'tests/test_continuous_attacks_text_input.py' else packet / 'draft' / name
    raw = source.read_bytes()
    assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], name
    if name not in old:
        assert not (repo / name).exists(), name
subprocess.run(['git', 'apply', '--check', str(patch)], cwd=repo, check=True)
subprocess.run(['git', 'apply', str(patch)], cwd=repo, check=True)
(repo / registry_name).write_bytes(registry_new)
for name, row in targets.items():
    raw = (repo / name).read_bytes()
    assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], name
    if name in old and b'\r\n' in old[name]:
        assert b'\r\n' in raw and b'\n' not in raw.replace(b'\r\n', b''), name
for row in named:
    raw = (repo / row['path']).read_bytes()
    assert len(raw) == row['new_bytes'] and digest(raw) == row['new_sha256']
    if row['line_endings'] == 'LF':
        assert b'\r\n' not in raw
unchanged = set(old) - set(targets) - {registry_name}
for name in unchanged:
    assert (repo / name).read_bytes() == old[name], name
assert set(git('diff', '--name-only').decode().splitlines()) == (set(targets) & set(old)) | {registry_name}
out.mkdir()
for row in rows:
    target = out / row['archive_path']
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(row['source_path'], target)
    raw = target.read_bytes()
    assert len(raw) == row['bytes'] and digest(raw) == row['sha256']
for file in (mf, hand):
    if file.name in seen:
        assert (out / file.name).read_bytes() == file.read_bytes()
    else:
        shutil.copyfile(file, out / file.name)
receipt = {'passed': True, 'section': 88, 'actual_prior_commit': prior,
           'public_packet_files': len(rows), 'public_packet_bytes': sum(row['bytes'] for row in rows),
           'all_public_source_destination_bytes_hashes_verified': True,
           'old_maintained_py_json': len(old), 'unchanged_old_maintained_py_json': len(unchanged),
           'six_old_product_files_plus_registry_only': True, 'new_leaf_and_test_exact': True,
           'registry_single_entry_inverse_exact': True, 'old_CRLF_preserved': True,
           'root_current_source_and_fresh_tests_pending': True,
           'new_API_helper_formatter_parser_download_Qt_Wine_calls': 0}
with (out / 'root-integration088.json').open('x') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
shutil.copyfile(__file__, out / Path(__file__).name)
shutil.copyfile('/workspace/.continuation/root-related-088.py', out / 'root-related-088.py')
shutil.copyfile('/workspace/.continuation/root-related-preparation088-089.json', out / 'root-related-preparation088-089.json')
print(json.dumps(receipt, ensure_ascii=False))
