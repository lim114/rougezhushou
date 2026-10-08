"""Seal reviewed independent source/saved/fresh evidence without rerunning calls."""
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-relic-warning-order-081')
scope = {'__file__': str(OUT / 'independent_saved_compare081.py')}
exec((OUT / 'independent_saved_compare081.py').read_text().split("receipt = {'status'", 1)[0], scope)
canonical, normalize, groups_for, warning = [scope[k] for k in ('canonical', 'normalize', 'groups_for', 'warning')]
input_hashes = {}
summaries = []
draft_bytes = []
for seed in (7, 101):
    matrices = []
    for tree in ('baseline', 'draft'):
        path = OUT / f'independent-public-{tree}-seed-{seed}.json.gz'
        raw = path.read_bytes()
        uncompressed = gzip.decompress(raw)
        matrices.append(json.loads(uncompressed))
        input_hashes[path.name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        if tree == 'draft':
            draft_bytes.append(uncompressed)
    assert len(matrices[0]) == len(matrices[1]) == 8
    counts = Counter()
    for before, after in zip(*matrices, strict=True):
        assert canonical(normalize(before)) == canonical(normalize(after)), (seed, before['label'])
        if 'error' in before:
            assert canonical(before) == canonical(after)
            counts['exact_old_errors'] += 1
        else:
            groups = groups_for(after)
            actual = [w for w in after['result']['relic_resolution']['warnings'] if w in {warning(g) for g in groups}]
            assert actual == [warning(g) for g in groups]
            if canonical(before) == canonical(after):
                counts['whole_accepted_same'] += 1
            else:
                counts['only_group_warning_pending_order'] += 1
    summaries.append({'seed': seed, 'pairs': 8, 'counts': dict(counts)})
assert draft_bytes[0] == draft_bytes[1]
source = json.loads((OUT / 'independent-source-static081.json').read_text())
saved = json.loads((OUT / 'independent-saved-comparison081.json').read_text())
assert source['status'] == saved['status'] == 'PASS'
sealed = json.loads((AUTHOR / 'author-frozen-receipt.json').read_text())
for name, key in [('relic-warning-order-081.patch', 'patch_sha256'),
                  ('draft/rouge/relics.py', 'draft_relics_sha256'),
                  ('source-receipt.json', 'source_receipt_sha256'),
                  ('comparison-receipt.json', 'comparison_receipt_sha256'),
                  ('draft/tests/test_relic_warning_order.py', 'new_test_sha256')]:
    assert hashlib.sha256((AUTHOR / name).read_bytes()).hexdigest() == sealed[key]
log = (OUT / 'independent-new-tests081.log').read_text()
assert 'Ran 8 tests' in log and log.rstrip().endswith('OK')
diagnostic = json.loads((OUT / 'preparation-diagnostics081.json').read_text())
diagnostic['comparison_preparation']['closure'] = 'Only reviewer whitelist corrected using existing frozen pure formatter phrase; saved 140 pairs strict canonical review then passed, no API matrix rerun.'
diagnostic['author_patch_transport'] = {'attempt': 1, 'failure': 'Missing a/b slash in test headers produced root-level new-test path.',
    'closure': 'Author preserved original patch/freeze/diagnostic and corrected transport paths; independent exact numstat and git apply --check pass, frozen product/test/matrix unchanged.',
    'corrected_patch_sha256': sealed['patch_sha256']}
(OUT / 'preparation-diagnostics081.json').write_text(json.dumps(diagnostic, ensure_ascii=False, indent=2) + '\n')
receipt = {'status': 'PASS_FINAL_FROZEN', 'section': 81,
           'baseline_commit': sealed['baseline_commit'], 'author_directory': str(AUTHOR),
           'patched_statement': 'Set enumeration to first occurrence in fixed rules+effects+token_effects using dict.fromkeys.',
           'frozen_source_static': source,
           'saved_pairs_strictly_recompared': 140, 'saved_author_calls_not_repeated': 280,
           'saved_seed_counts': saved['seed_summaries'],
           'saved_draft_four_seed_bytes_equal_without_normalization': True,
           'saved_draft_raw_json_sha256': saved['draft_raw_json_sha256'],
           'fresh_unique_review_scenarios': 8, 'fresh_seeds': [7, 101], 'fresh_pairs': 16,
           'fresh_calculate_calls': 32, 'fresh_counts': summaries,
           'fresh_draft_two_seed_bytes_equal_without_normalization': True,
           'fresh_draft_uncompressed_sha256': hashlib.sha256(draft_bytes[0]).hexdigest(),
           'fresh_input_artifacts': input_hashes,
           'new_tests_passed': 8, 'author_related_58_tests_not_repeated': True,
           'related_historical_skips_remain_author_10_not_passed': True,
           'original_words_fields_numbers_errors_and_unknowns_preserved': True,
           'normalization_is_comparison_only': saved['normalization'],
           'pure_phrase_scope': saved['formatted_exact_warning_phrases'],
           'candidate_trace': 'Real public call local trace, no injected rule or fake native marker.',
           'tracked_author_source_or_080_matrices_mutated': False,
           'GUI_Wine_native_Windows_game_run': False,
           'required_root_action': 'Integrate surgical patch and register new tests only after section080 full cadence; root current checks still required.',
           'frozen_artifact_hashes': {key: sealed[key] for key in ('patch_sha256', 'draft_relics_sha256', 'new_test_sha256', 'source_receipt_sha256', 'comparison_receipt_sha256')},
           'preparation_diagnostics': 'All initial read/whitelist and author patch transport evidence preserved; product failures zero.'}
(OUT / 'independent-review-final081.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
files = []
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path.name != 'independent-public-manifest081.json' and '__pycache__' not in path.parts:
        raw = path.read_bytes()
        files.append({'source_path': str(path), 'archive_path': str(path.relative_to(OUT)),
                      'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
manifest = {'format_version': 1, 'section': 81, 'status': 'FINAL_SEALED', 'file_count': len(files),
            'files': files, 'total_bytes': sum(row['bytes'] for row in files),
            'manifest_self_excluded': True, 'public_artifacts_only': True, 'whole_source_trees_excluded': True}
(OUT / 'independent-public-manifest081.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'fresh_counts': summaries,
    'file_count': len(files), 'manifest_sha256': hashlib.sha256((OUT / 'independent-public-manifest081.json').read_bytes()).hexdigest(),
    'review_final_sha256': hashlib.sha256((OUT / 'independent-review-final081.json').read_bytes()).hexdigest()}, ensure_ascii=False))
