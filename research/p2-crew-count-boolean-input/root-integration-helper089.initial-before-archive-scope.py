"""Root-only section89 integration draft; author must never execute this file.

Usage (after root review, final88 tag, and copying/reviewing the spec):
python root-integration-helper089.py --actual-root88-commit EXACT40 --spec SPEC

Applies/stages approved source and archives. It does not run project code,
tests or the post-apply source checker, and does not commit/tag or edit P1/docs.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--actual-root88-commit', required=True)
parser.add_argument('--spec', type=Path, required=True)
args = parser.parse_args()
repo = Path('/workspace/rougezhushou')
packet = Path('/workspace/.continuation/p2-crew-count-boolean-089-final')
author = Path('/workspace/.continuation/p2-crew-count-boolean-089-draft')
out_relative = 'research/p2-crew-count-boolean-input'
out = repo / out_relative
prior = args.actual_root88_commit
manifest_sha = '9ccc55e525c49e5be057c882b4197bab0e989adced7a1176a08471c566465a33'
handoff_sha = 'd718bb689695fde007efed5a7e00da1e0ac1ca76392f390576008adae842261a'
old_run_sha = '6d36bc955af40aff99ac9079706342b67e6df0bc8d1f93e55e2cc580cabcbdac'
new_run_sha = '20c6a00a72744017ebbc0fcb3b1009dddf8a6702aa01bf273b4b51c344692fd9'
new_test_sha = 'cb76de22153bdb44a223252b5f0bd66c0a03d05eb6fc4daf1e22b0043e198671'
patch_sha = '5f05fa36a07c07e9c1028e0beb2d739a3a98132180388e800f5602f5cd0efa00'
product_name = 'rouge/run_state.py'
test_name = 'tests/test_run_crew_count_boolean_input.py'
registry_name = 'scripts/verify_cloud.py'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*command):
    return subprocess.check_output(['git', *command], cwd=repo)


def write_json(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def staged_blobs():
    result = {}
    for chunk in git('ls-files', '--stage', '-z', '--', out_relative).split(b'\0'):
        if not chunk:
            continue
        header, name = chunk.split(b'\t', 1)
        mode, blob, stage = header.decode().split()
        assert stage == '0' and mode == '100644', name
        result[name.decode()] = blob
    return result


def verify_indexed(paths):
    staged = staged_blobs()
    rows = []
    for path in paths:
        relative = path.relative_to(repo).as_posix()
        raw = path.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        assert staged[relative] == blob, relative
        rows.append({'path': relative, 'bytes': len(raw), 'sha256': digest(raw), 'git_blob': blob})
    return rows


# Complete validation precedes any tracked mutation.
assert re.fullmatch('[0-9a-f]{40}', prior)
assert git('rev-parse', '--show-object-format').decode().strip() == 'sha1'
assert git('rev-parse', '--verify', prior + '^{commit}').decode().strip() == prior
assert git('rev-parse', '--verify', 'refs/tags/p2-section-088^{commit}').decode().strip() == prior
assert git('rev-parse', 'HEAD').decode().strip() == prior
assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('status', '--porcelain') == b''
assert json.loads(git('show', prior + ':DEVELOPMENT_CHECKPOINT.json'))['completed_sections'] == 88
assert not out.exists()
spec_raw = args.spec.read_bytes()
spec = json.loads(spec_raw)
assert spec['number'] == 89
assert spec['verification']['research_archive'] == out_relative
assert set(spec['changed_paths']) == {product_name, test_name, registry_name}
assert 'PROJECT_PROGRESS.md' not in spec['changed_paths']
mf = packet / 'public-manifest-final089.json'
hand = packet / 'handoff-final089.json'
mf_raw, hand_raw = mf.read_bytes(), hand.read_bytes()
assert digest(mf_raw) == manifest_sha and digest(hand_raw) == handoff_sha
manifest, handoff = json.loads(mf_raw), json.loads(hand_raw)
assert manifest['version'] == 1 and manifest['file_count'] == 258
assert manifest['total_bytes'] == 4178513
rows = manifest['files']
assert len(rows) == 258 and sum(row['bytes'] for row in rows) == 4178513
verified_public = {}
for row in rows:
    name = PurePosixPath(row['archive_path'])
    assert not name.is_absolute() and '..' not in name.parts
    assert str(name) == row['archive_path'] and str(name) not in ('', '.')
    assert row['archive_path'] not in verified_public
    source = Path(row['source_path'])
    assert source.is_absolute()
    raw = source.read_bytes()
    assert len(raw) == row['bytes'] and digest(raw) == row['sha256'], str(name)
    verified_public[str(name)] = raw
assert handoff['old_baseline_sha256'] == old_run_sha
patch = Path(handoff['section_patch']['source_path'])
patch_raw = patch.read_bytes()
assert digest(patch_raw) == patch_sha == handoff['section_patch']['sha256']
assert len(patch_raw) == 7155
new_product = Path(handoff['product_and_new_test'][0]['source_path']).read_bytes()
new_test = Path(handoff['product_and_new_test'][1]['source_path']).read_bytes()
assert len(new_product) == 42446 and digest(new_product) == new_run_sha
assert len(new_test) == 6492 and digest(new_test) == new_test_sha
assert b'\n' not in new_product.replace(b'\r\n', b'') and b'\r\n' not in new_test
old = {}
for name in git('ls-files', '-z', '--', 'rouge', 'tests', 'scripts').decode().split('\0'):
    if name and Path(name).suffix in ('.py', '.json') and '__pycache__' not in Path(name).parts:
        original = git('show', prior + ':' + name)
        assert (repo / name).read_bytes() == original, name
        old[name] = original
assert product_name in old and digest(old[product_name]) == old_run_sha
assert test_name not in old and not (repo / test_name).exists()
line = b'        if isinstance(crew,bool):crew=None\r\n'
assert new_product.count(line) == 1 and new_product.replace(line, b'', 1) == old[product_name]
registry_old = old[registry_name]
token = b'MODULES = (\n'
literal = b'    "tests.test_run_crew_count_boolean_input",\n'
literal88 = b'    "tests.test_continuous_attacks_text_input",\n'
assert registry_old.count(token) == 1 and literal not in registry_old
assert registry_old.count(literal88) == 1
registry_new = registry_old.replace(token, token + literal, 1)
assert registry_new.replace(literal, b'', 1) == registry_old
assert registry_new.count(literal88) == 1
template = Path('/workspace/.continuation/p2-crew-count-boolean-089-root-transport/root_current_source089.template.py')
template_raw = template.read_bytes()
assert template_raw == verified_public['root-transport-pending/root_current_source089.template.py']
related = Path('/workspace/.continuation/root-related-089.py')
related_raw = related.read_bytes()
helper_raw = Path(__file__).read_bytes()
extra_public = {mf.name: mf_raw, hand.name: hand_raw,
                'root-integration-helper089.py': helper_raw, 'spec089-at-integration.json': spec_raw,
                'root-current-source-089.py': template_raw, 'root-related-089.py': related_raw}
assert not (set(extra_public) & set(verified_public))
subprocess.run(['git', 'apply', '--check', str(patch)], cwd=repo, check=True)

# Only root's explicit execution may reach these mutation operations.
subprocess.run(['git', 'apply', str(patch)], cwd=repo, check=True)
(repo / registry_name).write_bytes(registry_new)
assert (repo / product_name).read_bytes() == new_product
assert (repo / test_name).read_bytes() == new_test
unchanged = set(old) - {product_name, registry_name}
for name in unchanged:
    assert (repo / name).read_bytes() == old[name], name
assert set(git('diff', '--name-only').decode().splitlines()) == {product_name, registry_name}
out.mkdir()
for name, raw in verified_public.items():
    target = out / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as handle:
        handle.write(raw)
    assert target.read_bytes() == raw
for name, raw in extra_public.items():
    with (out / name).open('xb') as handle:
        handle.write(raw)
receipt = {
    'status': 'PASS_ROOT_SOURCE_PATCH_AND_PUBLIC_ARCHIVE_COPY', 'section': 89,
    'actual_pre89_commit': prior, 'equal_tag': 'p2-section-088',
    'public_packet_files': 258, 'public_packet_bytes': 4178513,
    'public_manifest_sha256': manifest_sha, 'public_handoff_sha256': handoff_sha,
    'all_public_source_and_archive_bytes_hashes_verified': True,
    'old_maintained_py_json': len(old), 'unchanged_old_maintained_py_json': len(unchanged),
    'run_state_added_one_CRLF_line_inverse_exact': True, 'new_test_LF_exact': True,
    'registry_single_module_inverse_exact': True, 'actual88_registry_module_preserved': True,
    'tracked_source_changes': [product_name, test_name, registry_name],
    'P1_and_PROJECT_PROGRESS_modified': False,
    'index_verification_receipt': 'root-indexed-archive089.json',
    'root_current_source_checker_status': 'PENDING_POST_APPLY_AND_STAGE_ROOT_EXECUTION',
    'root_fresh_related_selected_status': 'PENDING', 'commit_and_tag': 'NOT_PERFORMED',
    'new_RunState_damage_app_helper_tests_formatter_Qt_Wine_calls': 0,
    'next_source_command_arguments': ['--pre89-commit', prior, '--receipt', '/workspace/.continuation/root-source-089.json']}
write_json(out / 'root-integration089.json', receipt)
subprocess.run(['git', 'add', '--', product_name, test_name, registry_name], cwd=repo, check=True)
archive_paths = sorted(p for p in out.rglob('*') if p.is_file())
subprocess.run(['git', 'add', '-f', '--', *[p.relative_to(repo).as_posix() for p in archive_paths]], cwd=repo, check=True)
indexed = verify_indexed(archive_paths)
index_receipt = out / 'root-indexed-archive089.json'
write_json(index_receipt, {'status': 'PASS_ALL_INDEXED_ARCHIVE_BYTES', 'actual_pre89_commit': prior,
                           'verified_archive_files_before_this_receipt': len(indexed),
                           'files': indexed, 'source_module_registry_staged': True,
                           'this_receipt_self_excluded_from_rows_but_blob_checked_after_add': True,
                           'new_project_calls': 0, 'commit_performed': False})
subprocess.run(['git', 'add', '-f', '--', index_receipt.relative_to(repo).as_posix()], cwd=repo, check=True)
verify_indexed([index_receipt])
all_archive = archive_paths + [index_receipt]
expected_staged = {product_name, test_name, registry_name} | {p.relative_to(repo).as_posix() for p in all_archive}
assert set(git('diff', '--cached', '--name-only').decode().splitlines()) == expected_staged
assert git('rev-parse', 'HEAD').decode().strip() == prior
for row in rows:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and digest(raw) == row['sha256']
print(json.dumps({'status': 'PASS_ROOT_APPLY_ARCHIVE_AND_FORCE_INDEX',
                  'actual_pre89_commit': prior, 'archive_files_indexed': len(all_archive),
                  'old_maintained_py_json': len(old), 'unchanged_old_maintained_py_json': len(unchanged),
                  'root_source_and_fresh_tests_pending': True, 'new_project_calls': 0}, ensure_ascii=False))
