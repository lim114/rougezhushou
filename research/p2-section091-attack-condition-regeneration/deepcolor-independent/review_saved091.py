"""Read-only independent review of the exact frozen271 files and six saved outcomes."""
import json
from pathlib import Path, PurePosixPath
from review_common091 import canonical, decode, inverse, native, sha, QUALIFICATION

AUTHOR = Path('/workspace/.continuation/p2-section091-deepcolor-regeneration-notes-author')
OUT = Path(__file__).resolve().parent
manifest_path = AUTHOR / 'public-artifacts-manifest-final.json'
raw_manifest = manifest_path.read_bytes()
assert sha(raw_manifest) == 'cfedb0ab204f413d77fe695c614f6667df92886320abc23d5a6d99c9963ece73'
manifest = json.loads(raw_manifest)
assert manifest['schema_version'] == 1 and len(manifest['artifacts']) == manifest['artifact_count'] == 271
assert manifest['artifact_bytes'] == 44566566
names = set(); normalized = []
for row in manifest['artifacts']:
    path = PurePosixPath(row['path'])
    assert not path.is_absolute() and '..' not in path.parts and path.as_posix() == row['path']
    assert row['path'] not in names; names.add(row['path'])
    source = AUTHOR / row['path']; raw = source.read_bytes()
    assert not source.is_symlink() and len(raw) == row['bytes'] and sha(raw) == row['sha256']
    normalized.append({'source_path': str(source), 'archive_path': row['path'],
                       'bytes': len(raw), 'sha256': sha(raw)})
assert sum(row['bytes'] for row in normalized) == manifest['artifact_bytes']
handoff_raw = (AUTHOR / 'final-handoff.json').read_bytes()
assert sha(handoff_raw) == '7c7dcd0dedd5f712ed69c142272c327d0b284e0a6dec28060b63c6c214010aeb'
pre = json.loads((AUTHOR / 'pre-execution-freeze.json').read_text())
assert sha((AUTHOR / 'pre-execution-freeze.json').read_bytes()) == 'f5a4d3a13a4e7e63e55be0f0831dbce77ee24c8d179849ee7afe003fd729b4b3'
for row in pre['artifacts']:
    raw = (AUTHOR / row['path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
base_raw = (AUTHOR / 'public-baseline.json').read_bytes()
draft_raw = (AUTHOR / 'public-draft.json').read_bytes()
assert sha(base_raw) == '5eeaa93f31182abb35744d527711d053aa2681ac0d4c3921b8de2045d02f3741'
assert sha(draft_raw) == 'd36a16e02fa830671e4394e16dbf3940e00e3f25d9ef1d71783b15a9e4265259'
base, draft = json.loads(base_raw), json.loads(draft_raw)
for group in (base, draft):
    assert group['status'] == 'THREE_PUBLIC_ENTRIES_COMPLETE' and group['public_API_entries'] == 3
    assert group['source_before'] == group['source_after'] and group['source_unchanged']
    tree = AUTHOR / (group['tree'] + '-tree')
    current = {p.relative_to(tree).as_posix(): sha(p.read_bytes()) for p in sorted(tree.rglob('*'))
               if p.is_file() and p.suffix in ('.py', '.json')}
    assert current == group['source_before']
assert base['explicit_formatter_entries'] == 0 and draft['explicit_formatter_entries'] == 3
checks = []
for left, right in zip(base['records'], draft['records'], strict=True):
    assert left['id'] == right['id'] and left['input'] == right['input']
    for row in (left, right):
        assert row['status'] == 'returned'
        decoded = decode(row['result_native'])
        assert canonical(decoded) == row['result_json'] == canonical(row['result'])
        assert row['input_json_before'] == row['input_json_after'] == canonical(row['input'])
        assert row['input_native_before'] == row['input_native_after'] == native(row['input'])
        assert row['caller_json_unchanged'] and row['caller_native_unchanged']
    changed = decode(right['result_native'])
    restored, substitutions, qualification_count = inverse(changed)
    assert native(restored) == left['result_native'] and canonical(restored) == left['result_json']
    s1 = right['input']['skill'] == 1
    assert bool(substitutions) == s1 and qualification_count == (1 if s1 else 0)
    if s1:
        assert len(substitutions) == 2
        block = next(b for b in changed['report']['sections'] if b['id'] == 'regeneration')
        assert {metric['key']: metric['value'] for metric in block['metrics']} == {
            'per_token_rate': 84.0, 'all_tokens_rate': 168.0}
        assert changed['relic_regeneration_multiplier'] == 1.2
        assert QUALIFICATION in right['formatted_text']
        assert all(item['new'] in right['formatted_text'] for item in substitutions)
    else:
        assert changed == restored and QUALIFICATION not in right['formatted_text']
    archived_text = AUTHOR / right['formatted_text_archive_path']
    text_raw = archived_text.read_bytes()
    assert sha(text_raw) == right['formatted_text_file_sha256']
    assert text_raw.decode() == right['formatted_text'] + '\n'
    assert native(right['formatted_text']) == right['formatted_native']
    assert right['formatter_preserved_result_native'] and right['formatter_preserved_result_json']
    checks.append({'id': right['id'], 'whole_preencoding_native_and_JSON_inverse_exact': True,
                   'caller_native_JSON_unchanged': True, 'structured_report_all_numeric_fields_exact': True,
                   'only_allowed_changes': ['estimate.notes', 'report.sections[id=regeneration].notes'] if s1 else [],
                   'saved_default_text_verified_without_new_formatter_request': True,
                   'note_inversions': substitutions})
receipt = {'status': 'SAVED_SIX_PUBLIC_OUTCOMES_STRICT_INDEPENDENT_PASS',
           'author_manifest_sha256': sha(raw_manifest), 'author_files_verified': len(normalized),
           'author_bytes_verified': manifest['artifact_bytes'], 'preexecution263_files_hash_verified': True,
           'author_public_entries': 6, 'author_explicit_formatter_requests': 3,
           'author_formatter_modes': 'One default format_report for each of three draft cases; zero baseline formatter requests. Not three modes for every case.',
           'checks': checks, 'new_independent_API_projecthelper_formatter_test_Qt_Wine_calls': 0,
           'old389_source23_or_full90_replays': 0,
           'native_tick_lifetime_hotupdate_actual_regeneration_total_certified': False,
           'caller_and_tree_scope': 'Saved caller before/after and both126 tree hashes verified. Author did not independently store raw in-memory catalog before/after; no such assertion is inferred from source hashes.'}
with (OUT / 'saved-independent-receipt091.json').open('x') as handle:
    handle.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
with (OUT / 'author-manifest-normalized-v1.json').open('x') as handle:
    handle.write(json.dumps({'format_version': 1, 'original_manifest_sha256': sha(raw_manifest),
                             'original_schema': 'Explicit schema_version1/artifacts/path; no generic shape autodetection',
                             'files': normalized}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'saved_pairs': len(checks), 'author_files_verified': len(normalized),
                  'new_product_calls': 0, 'receipt_sha256': sha((OUT / 'saved-independent-receipt091.json').read_bytes())}))
