"""Seal the first immutable author review packet; later transport is additive."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = Path('/workspace/.continuation/p2-animation-provenance-portability-090-source')
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def write(name, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    with (HERE / name).open('xb') as stream:
        stream.write(raw)
    return {'source_path': str(HERE / name), 'archive_path': name,
            'bytes': len(raw), 'sha256': sha(raw)}


files = []
seen = set()


def add(path, archive_path, expected=None):
    pure = PurePosixPath(archive_path)
    assert not pure.is_absolute() and str(pure) == archive_path
    assert '\\' not in archive_path and all(part not in ('.', '..') and ':' not in part for part in pure.parts)
    assert archive_path not in seen
    seen.add(archive_path)
    raw = path.read_bytes()
    if expected:
        assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], archive_path
    files.append({'source_path': str(path), 'archive_path': archive_path,
                  'bytes': len(raw), 'sha256': sha(raw)})


freeze = json.loads((HERE / 'review-freeze090.json').read_bytes())
for item in freeze['product_files']:
    add(HERE / 'draft' / item['path'], 'product/' + item['path'], item)
    if item['path'].endswith('.py'):
        ast.parse((HERE / 'draft' / item['path']).read_bytes())
for path in sorted((HERE / 'draft').rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:
        continue
    rel = path.relative_to(HERE / 'draft').as_posix()
    if rel not in {item['path'] for item in freeze['product_files']}:
        add(path, 'public-inputs/' + rel)
for path in sorted((HERE / 'baseline').rglob('*')):
    if path.is_file():
        add(path, path.relative_to(HERE).as_posix())
for path in sorted(HERE.iterdir()):
    if not path.is_file() or path.name in {'archivable-author-review-manifest090.json', 'author-review-handoff090.json'}:
        continue
    add(path, path.name)
    if path.suffix == '.py':
        ast.parse(path.read_bytes())
source_manifest_path = SOURCE / 'public-artifacts-manifest-source090.json'
source_manifest = json.loads(source_manifest_path.read_bytes())
assert sha(source_manifest_path.read_bytes()) == 'd5d12ae2aaa8d2713a03abb400d4b50cc9973093841b43e91d335d5bba4ecb33'
assert len(source_manifest['files']) == 28
for item in source_manifest['files']:
    add(Path(item['source_path']), 'source-proposal090/' + item['archive_path'], item)
add(source_manifest_path, 'source-proposal090/public-artifacts-manifest-source090.json')
add(SOURCE / 'final-handoff-source090.json', 'source-proposal090/final-handoff-source090.json')
tests = json.loads((HERE / 'new-tests-operation090.json').read_bytes())
assert tests['passed'] and tests['tests_run'] == 6 and tests['author_total_verifier_entries'] == 28
manifest = write('archivable-author-review-manifest090.json', {
    'format_version': 1, 'status': 'FINAL_STABLE_AUTHOR_REVIEW_PACKET_ROOT89_TRANSPORT_PENDING',
    'files': files, 'bytes': sum(item['bytes'] for item in files),
    'immutable_source_proposal_original28_and_original_manifest_handoff_included': True,
    'author_CLI_invocations': 11, 'author_verifier_function_entries': 28,
    'author_tests_first_run': 6, 'author_tests_failures_errors_skips': 0,
    'root89_transport_pending': True, 'formal_independent_review_pending': True,
    'application_API_helper_formatter_source_parser_network_Qt_Wine_calls': 0,
    'tracked_edits': 0,
    'excluded': ['__pycache__', 'temporary corrupted test copies', 'private state']})
handoff = write('author-review-handoff090.json', {
    'format_version': 1, 'status': 'FINAL_STABLE_AUTHOR_REVIEW_PACKET',
    'directory': str(HERE), 'manifest': manifest, 'files': len(files),
    'bytes': sum(item['bytes'] for item in files),
    'review_freeze_sha256': sha((HERE / 'review-freeze090.json').read_bytes()),
    'product_files': freeze['product_files'],
    'patch': {'path': str(HERE / 'product090.patch'), 'bytes': freeze['patch_bytes'], 'sha256': freeze['patch_sha256']},
    'author_verifier_entries': 28, 'author_CLI_invocations': 11,
    'code_test_README_original_note_and_review_packet_will_not_be_modified': True,
    'future_root89_transport_formal_review_and_final_seal_are_additive': True,
    'root_owns_tracked_edits_and_final_validation': True})
print(json.dumps({'manifest': manifest, 'handoff': handoff,
                  'files': len(files), 'bytes': sum(item['bytes'] for item in files)}))
