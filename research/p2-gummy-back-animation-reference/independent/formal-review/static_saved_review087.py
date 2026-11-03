"""Formal frozen bytes and saved author JSON comparison, zero product operations."""
from pathlib import Path
from datetime import datetime, timezone
import copy
import gzip
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
PREP = ROOT.parent
AUTHOR = ROOT.parents[1] / 'p2-gummy-back-animation-reference-087-draft'
SNAP = ROOT / 'author-snapshots'
SNAP.mkdir(exist_ok=True)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def typed(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(typed(x, y) for x, y in zip(a, b))
    return a == b

def dump(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def inherited_frame_types(frame):
    # The unchanged original frames() explicitly casts only these two fields.
    # JS saved JSON writes integral doubles without a fractional suffix.
    return {k: float(v) if k in ['seconds', 'raw_frames_30hz'] else v
            for k, v in frame.items() if k != 'field'}

dump('initial-product-patch-path-diagnostic087.json', {
    'version': 1, 'kind': 'Optional local filename discovery preparation', 'failed_attempts': 1,
    'attempted_path': str(AUTHOR / 'draft.patch'),
    'actual_error': 'cat: /workspace/.continuation/p2-gummy-back-animation-reference-087-draft/draft.patch: No such file or directory',
    'resolution': 'Read exact product087.patch path from already available author-freeze087.json',
    'application_API_helper_formatter_tests_parser_network_Qt_Wine_calls': 0})

names = ['author-freeze087.json', 'product087.patch', 'matrix-cases.json',
    'matrix-baseline-results.json', 'matrix-draft-results.json', 'matrix-comparison-receipt.json',
    'initial-public-inspection.json', 'data-generation-receipt.json', 'old-923-record-byte-preservation.json',
    'initial-diff-check-diagnostic.json', 'related-tests-receipt.json', 'new-tests.log', 'related-tests.log',
    'generate_additive_data.py', 'collect_matrix.py', 'compare_matrix.py', 'run_related.py']
bindings = []
for name in names:
    src = AUTHOR / name
    dst = SNAP / name
    shutil.copy2(src, dst)
    assert src.read_bytes() == dst.read_bytes()
    bindings.append({'source_path': str(src), 'archive_path': str(dst.relative_to(ROOT)),
        'bytes': dst.stat().st_size, 'sha256': sha(dst.read_bytes())})
freeze = json.loads((SNAP / 'author-freeze087.json').read_text())
assert freeze['author_baseline_commit'] == '9ef5a469673502754db3be320a8eece9a7fd18d4'
for row in freeze['source_files']:
    src = Path(row['draft_source_path'])
    raw = src.read_bytes()
    assert len(raw) == row['draft_bytes'] and sha(raw) == row['draft_sha256']
    dst = SNAP / 'draft' / row['path']
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(raw)
    assert raw.count(b'\r\n') == raw.count(b'\n') if row['line_endings'] == 'CRLF' else b'\r\n' not in raw
    bindings.append({'source_path': str(src), 'archive_path': str(dst.relative_to(ROOT)),
        'bytes': len(raw), 'sha256': sha(raw)})
for row in freeze['unchanged_author_consumer_sources']:
    draft = AUTHOR / 'draft' / row['path']
    base = AUTHOR / 'baseline' / row['path']
    assert draft.read_bytes() == base.read_bytes()
    assert len(draft.read_bytes()) == row['bytes'] and sha(draft.read_bytes()) == row['sha256']
assert sha((SNAP / 'product087.patch').read_bytes()) == freeze['patch']['sha256']

old_raw = gzip.decompress((PREP / 'source-snapshots/rouge/data/original-animation-references.json.gz').read_bytes())
new_raw = (SNAP / 'draft/rouge/data/original-animation-references.json').read_bytes()
old = json.loads(old_raw)
new = json.loads(new_raw)
expected_counts = {'operators': 32, 'source_skeletons': 64, 'animations': 928,
    'selectable_references': 162, 'unverified_or_transition_references': 766, 'missing_skeletons': 0}
assert typed(new['counts'], expected_counts)
assert list(new['operators']) == list(old['operators'])
restored = copy.deepcopy(new)
addition = restored.pop('source_additions')
restored['counts'] = copy.deepcopy(old['counts'])
restored['operators']['char_196_sunbr']['records'] = restored['operators']['char_196_sunbr']['records'][:9]
restored['operators']['char_196_sunbr']['missing_sources'] = copy.deepcopy(old['operators']['char_196_sunbr']['missing_sources'])
assert typed(restored, old), 'Unexpected original data semantic/type change'
decoder = json.JSONDecoder()
record_index = {}
new_text = new_raw.decode('utf-8')
for match in re.finditer(r'"records": \[', new_text):
    cursor = match.end()
    while True:
        while new_text[cursor].isspace() or new_text[cursor] == ',':
            cursor += 1
        if new_text[cursor] == ']':
            break
        start = cursor
        record, cursor = decoder.raw_decode(new_text, cursor)
        assert record['id'] not in record_index
        piece = new_text[start:cursor].encode('utf-8')
        record_index[record['id']] = {'literal_object_bytes': len(piece), 'literal_object_sha256': sha(piece),
            'strict_JSON_type_value_sha256': sha(json.dumps(record, ensure_ascii=False, sort_keys=True,
                separators=(',', ':')).encode('utf-8'))}
assert len(record_index) == 928
old_index = json.loads((PREP / 'baseline923-record-byte-index087.json').read_text())
for item in old_index['records']:
    assert typed({k: v for k, v in item.items() if k != 'id'}, record_index[item['id']]), item['id']

prep = json.loads((PREP / 'source-preparation-receipt087.json').read_text())
back = json.loads((PREP / 'source-snapshots/source-operation/parse-Back-result.json').read_text())
records = new['operators']['char_196_sunbr']['records']
assert [r['id'] for r in records[:9]] == [r['id'] for r in old['operators']['char_196_sunbr']['records']]
added = records[9:]
assert len(added) == 5
assert new['operators']['char_196_sunbr']['missing_sources'] == []
for record, fact in zip(added, prep['new_saved_source_record_facts']):
    assert list(record) == ['id', 'orientation', 'skin', 'animation', 'spine_version', 'duration', 'events',
        'selectable_as_conventional_reference', 'unverified_reasons', 'runtime_binding_verified', 'source'] + (['preview'] if fact['policy_eligible'] else [])
    assert record['id'] == fact['new_record_id']
    assert record['orientation'] == 'Back' and record['skin'] == 'original' and record['spine_version'] == '3.8.99'
    frame = fact['policy_frame_facts'][0]
    assert typed(record['duration'], inherited_frame_types(frame))
    frames = fact['policy_frame_facts'][1:]
    assert typed(record['events'], [{'name': frame['field'], **inherited_frame_types(frame)} for frame in frames])
    assert record['selectable_as_conventional_reference'] is fact['policy_eligible']
    assert typed(record['unverified_reasons'], fact['policy_unverified_reasons_in_order'])
    assert record['runtime_binding_verified'] is False
    assert typed(record['source'], {'url': back['resource']['source_url'], 'sha256': back['resource']['sha256'],
        'git_blob': back['resource']['git_blob_sha1'], 'bytes': back['resource']['bytes']})
    assert typed(record['preview'], fact['preview_if_eligible']) if fact['policy_eligible'] else 'preview' not in record
assert len(addition) == 1
a = addition[0]
assert a['record_ids'] == [r['id'] for r in added]
assert a['runtime_binding_inferred'] is False
assert a['extraction_sha256'] == sha((PREP / 'source-snapshots/source-operation/parse-Back-result.json').read_bytes())
assert a['source_packet_manifest_sha256'] == sha((PREP / 'source-snapshots/source-operation/public-artifacts-manifest087.json').read_bytes())
assert a['source_sha256'] == back['resource']['sha256'] and a['git_blob'] == back['resource']['git_blob_sha1']
assert a['official_reader_commit'] == '8b4844bd4b193ba9e54487ed397a777993cbad56'
assert a['official_reader_bundle_sha256'] == back['official_bundle_sha256']
assert all(r['runtime_binding_verified'] is False for p in new['operators'].values() for r in p['records'])

before = json.loads((SNAP / 'matrix-baseline-results.json').read_text())
after = json.loads((SNAP / 'matrix-draft-results.json').read_text())
cases = json.loads((SNAP / 'matrix-cases.json').read_text())['cases']
initial = json.loads((SNAP / 'initial-public-inspection.json').read_text())
assert len(before['items']) == len(after['items']) == len(cases) == 35
assert len({json.dumps(case['scenario'], sort_keys=True, ensure_ascii=False) for case in cases}) == 35
counts = {'whole_accepted_and_3_texts_same': 0, 'exact_old_errors': 0, 'new_explicit_Back_successes': 0}
reused = 0
checks = []
for case, b, d in zip(cases, before['items'], after['items']):
    assert typed({k: b[k] for k in case}, case) and typed({k: d[k] for k in case}, case)
    if case['expect'] == 'new_back_success':
        assert b['accepted'] is False and d['accepted'] is True
        assert b['error_type'] == 'ValueError' and b['error'] == '原版动画参考与当前干员/技能不符，或该动作不适合常规逐击参考。'
        result = d['result']
        assert result['timing']['complete'] is False
        assert all(s['exact_binding'] is False for s in result['timing']['streams'])
        if case['scenario']['skill'] == 1:
            assert result['total_healing'] is None
            for key in ['recharge_seconds', 'cycle_seconds', 'cycle_healing', 'cycle_hps']:
                assert result['estimate']['skill'][key] is None
        counts['new_explicit_Back_successes'] += 1
    elif b['accepted']:
        assert d['accepted'] is True and typed(b['result'], d['result']) and typed(b['texts'], d['texts'])
        counts['whole_accepted_and_3_texts_same'] += 1
    else:
        assert d['accepted'] is False and typed((b['error_type'], b['error']), (d['error_type'], d['error']))
        counts['exact_old_errors'] += 1
    for row in [b, d]:
        if row['accepted']:
            assert set(row['texts']) == {'plain', 'technical', 'estimate'}
            assert all(type(value) is str and value for value in row['texts'].values())
            assert row['texts']['estimate'] == row['texts']['plain']
    matching = [row for row in initial['items'] if typed(row['scenario'], d['scenario'])]
    if matching:
        assert len(matching) == 1
        prior = matching[0]
        assert all(typed(prior[k], d[k]) for k in prior if k not in ['label', 'scenario'])
        reused += 1
    checks.append({'label': case['label'], 'expect': case['expect'], 'passed': True})
assert counts == {'whole_accepted_and_3_texts_same': 16, 'exact_old_errors': 9, 'new_explicit_Back_successes': 10}
assert reused == after['reused_initial_API_results'] == 3
assert before['fresh_API_calls'] == 35 and after['fresh_API_calls'] == 32
assert before['formatter_calls'] + after['formatter_calls'] == 126
author_comparison = json.loads((SNAP / 'matrix-comparison-receipt.json').read_text())
assert author_comparison['passed'] is True and author_comparison['unique_pairs'] == 35
dump('static-source-and-saved35-review087.json', {'version': 1, 'status': 'PASS_STATIC_AND_SAVED_0_NEW_API',
    'reviewed_at_utc': datetime.now(timezone.utc).isoformat(), 'input_bindings': bindings,
    'source_files_frozen_exact': 3, 'unchanged_author_consumers_exact': 8,
    'original923_literal_bytes_and_exact_JSON_types_values_preserved': 923,
    'new_Back_record_full_schema_source_and_representation_policy_verified': 5,
    'new_counts': expected_counts, 'original_metadata_and_selection_derivation_preserved': True,
    'source_additions_distinguishes_new_source_from_old_derivation': True,
    'all928_runtime_binding_verified_false': True,
    'author_saved_unique_pairs': 35, 'author_saved_counts_independent': counts,
    'author_saved_rows': checks, 'original_initial_results_reused_exact': 3,
    'author_saved_formatter_requests': 126, 'estimate_plain_text_equality_verified': True,
    'source_metadata_reading_is_not_native_clock_or_UI_option_proof': True,
    'reviewer_application_API_helper_formatter_tests_parser_network_Qt_Wine_calls': 0,
    'root86_integration_boundary': 'Formal API sample trees are author frozen9ef; actual root86 merges only approved three-file patch and one registry line. Old damage/engine must never overwrite root86.'})
print(json.dumps({'status': 'PASS_STATIC_AND_SAVED_0_NEW_API', 'old_records_exact': 923,
    'added_records_verified': 5, 'saved_pairs': 35, 'counts': counts,
    'receipt_sha256': sha((ROOT / 'static-source-and-saved35-review087.json').read_bytes())}))
