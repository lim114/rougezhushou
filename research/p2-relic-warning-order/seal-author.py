import gzip
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

OUT = Path(__file__).parent
sha = lambda data: hashlib.sha256(data).hexdigest()
test = OUT / 'draft/tests/test_relic_warning_order.py'
test_diff = subprocess.run(['git', 'diff', '--no-index', '--', '/dev/null', str(test)], stdout=subprocess.PIPE)
assert test_diff.returncode == 1
engine_patch = (OUT / 'relic-warning-order-081.patch').read_bytes()
test_patch = test_diff.stdout.replace(str(test).encode(), b'tests/test_relic_warning_order.py')
patch = engine_patch + test_patch
(OUT / 'relic-warning-order-081.patch').write_bytes(patch)
compression = {}
for tree in ('baseline', 'draft'):
    for seed in (0, 1, 42, 314159):
        original = OUT / f'public-{tree}-seed-{seed}.json'
        data = original.read_bytes()
        buffer = io.BytesIO()
        with gzip.GzipFile(filename='', mode='wb', fileobj=buffer, compresslevel=9, mtime=0) as f:
            f.write(data)
        compressed = buffer.getvalue()
        assert gzip.decompress(compressed) == data
        destination = original.with_suffix('.json.gz')
        with destination.open('xb') as f:
            f.write(compressed)
        compression[original.name] = {'original_bytes': len(data), 'original_sha256': sha(data),
                                      'gzip_path': destination.name, 'gzip_bytes': len(compressed),
                                      'gzip_sha256': sha(compressed), 'decompressed_original_exact': True}
with (OUT / 'compressed-matrix-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(compression, f, ensure_ascii=False, indent=2)
    f.write('\n')
new_log = (OUT / 'new-tests.log').read_text()
old_log = (OUT / 'related-tests.log').read_text()
assert 'Ran 8 tests ' in new_log and new_log.rstrip().endswith('OK')
assert 'Ran 58 tests ' in old_log and old_log.rstrip().endswith('OK (skipped=10)')
test_receipt = {'passed': True, 'new_tests_run': 8, 'new_tests_passed': 8,
                'related_run': 58, 'related_passed': 48, 'related_historical_skipped': 10,
                'failures': 0, 'errors': 0,
                'historical_skip_lines': [line for line in old_log.splitlines() if ' ... skipped ' in line],
                'new_tests_sha256': sha(test.read_bytes()),
                'source_prepare_probes': 3, 'calculate_damage_matrix_calls': 280,
                'test_public_calls_separate_from_matrix': True,
                'probe_scope': 'Three read-only prepare probes inspected actual source paths for deepcl/81+82+5, mechanist/81+82+104+fight21, and gnosis/80+hand1. Their results select guards, not native mechanism assertions.'}
with (OUT / 'test-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(test_receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
freeze = json.loads((OUT / 'freeze-receipt.json').read_text())
for name, proof in freeze['fixed_files'].items():
    baseline = OUT / 'baseline' / name
    assert baseline.stat().st_size == proof['bytes'] and sha(baseline.read_bytes()) == proof['sha256']
    draft = OUT / 'draft' / name
    if name == 'rouge/relics.py':
        assert sha(draft.read_bytes()) == freeze['new_sha256']
    else:
        assert draft.read_bytes() == baseline.read_bytes(), name
receipt = {'status': 'author_source_tests_matrix_frozen_independent_review_pending',
           'passed': True, 'baseline_commit': freeze['baseline_commit'],
           'patch_sha256': sha(patch), 'draft_relics_sha256': sha((OUT / 'draft/rouge/relics.py').read_bytes()),
           'new_test_sha256': sha(test.read_bytes()),
           'note_draft_sha256': sha((OUT / 'NOTE.draft.md').read_bytes()),
           'source_receipt_sha256': sha((OUT / 'source-receipt.json').read_bytes()),
           'comparison_receipt_sha256': sha((OUT / 'comparison-receipt.json').read_bytes()),
           'test_receipt_sha256': sha((OUT / 'test-receipt.json').read_bytes()),
           'compressed_matrix_receipt_sha256': sha((OUT / 'compressed-matrix-receipt.json').read_bytes()),
           'original_717_source_files_unchanged': True, 'only_one_product_statement_changed': True,
           'crlf_preserved': True, 'tracked_edits': False, 'gui_executed': False, 'wine_executed': False}
with (OUT / 'author-frozen-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps(receipt, ensure_ascii=False))
