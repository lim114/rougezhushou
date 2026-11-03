"""Strict saved comparison of the two independent risk pairs; zero project imports."""
import json
from pathlib import Path
from review_common091 import canonical, decode, inverse, native, sha, QUALIFICATION

OUT = Path(__file__).resolve().parent
base = json.loads((OUT / 'narrow-baseline091.json').read_text())
draft = json.loads((OUT / 'narrow-draft091.json').read_text())
assert base['status'] == draft['status'] == 'NARROW_INDEPENDENT_EXECUTION_COMPLETE'
assert base['counts']['public_API_requests'] == draft['counts']['public_API_requests'] == 2
def inverse_text(text, substitutions):
    translations = {'• ' + item['new']: '• ' + item['old'] for item in substitutions}
    translated = set(); lines = []
    for line in text.split('\n'):
        if line == '• ' + QUALIFICATION:
            continue
        if line in translations:
            line = translations[line]
            if line in translated:
                continue
            translated.add(line)
        lines.append(line)
    assert len(translated) == len({item['old'] for item in substitutions})
    return '\n'.join(lines)
checks = []
for left, right in zip(base['fresh_records'], draft['fresh_records'], strict=True):
    assert left['id'] == right['id'] and native(left['input']) == native(right['input'])
    assert left['status'] == right['status'] == 'returned'
    for record in (left, right):
        assert native(decode(record['result_native'])) == record['result_native']
        assert canonical(decode(record['result_native'])) == record['result_json'] == canonical(record['result'])
        assert record['caller_preserved'] and record['caller_native_before'] == record['caller_native_after']
        assert record['texts']['estimate'] == record['texts']['default']
    restored, substitutions, count = inverse(decode(right['result_native']))
    assert count == 1 and len(substitutions) == 2
    assert native(restored) == left['result_native'] and canonical(restored) == left['result_json']
    for mode in ('estimate', 'default', 'technical'):
        assert inverse_text(right['texts'][mode], substitutions) == left['texts'][mode]
    assert len({item['old'] for item in substitutions}) == 1
    checks.append({'id': right['id'], 'entire_native_and_JSON_inverse_exact': True,
                   'three_real_report_modes_inverse_exact': True, 'original_ordered_note_dedup_required': True,
                   'clipped_observation_seconds': right['result']['estimate']['skill']['window_seconds'],
                   'per_token_and_all_token_rates': next(s['metrics'] for s in right['result']['report']['sections'] if s['id'] == 'regeneration'),
                   'caller_preserved': True, 'cached_catalog_first_return_vs_after_unchanged': True,
                   'substitutions': substitutions})
for row in draft['saved_formatter_supplement']:
    author_row = next(r for r in json.loads(Path('/workspace/.continuation/p2-section091-deepcolor-regeneration-notes-author/public-draft.json').read_text())['records'] if r['id'] == row['id'])
    _, substitutions, _ = inverse(decode(author_row['result_native']))
    for mode, text in row['texts'].items():
        assert (QUALIFICATION in text) == (author_row['input']['skill'] == 1)
        assert all(item['new'] in text for item in substitutions)
    assert row['result_native_decode_exact'] and row['result_native_preserved']
ledger = {key: base['counts'][key] + draft['counts'][key] for key in base['counts']}
assert ledger['public_API_requests'] == 4 and ledger['explicit_formatter_requests'] == 18
assert ledger['estimate_function_entries'] == 7 and ledger['report_function_entries'] == 18
receipt = {'status': 'TWO_INDEPENDENT_RISK_PAIRS_AND_FORMATTER_SUPPLEMENT_PASS',
           'checks': checks, 'actual_independent_counts': ledger,
           'formatter_request_scope': '12 external three-mode requests for4 fresh results, plus6 estimate/technical requests for3 decoded saved draft results. Saved default3 texts read only; author3 default requests remain historical.',
           'formatter_entry_scope': 'Measured7 estimate entries and18 report entries; report includes7 internal estimate delegations. Total25 actual instrumented entries is distinct from18 external requests.',
           'catalog_scope': 'First original cached helper return versus after native hashes; internal observed entries stored. No explicit extra catalog/profile helper request and no separately archived raw catalog tree.',
           'source_unchanged': base['source_unchanged'] and draft['source_unchanged'],
           'author_six_API_or_old389_source23_full90_rerun': False,
           'native_tick_lifetime_hotupdate_actual_regeneration_total_verified': False}
with (OUT / 'narrow-comparison-receipt091.json').open('x') as handle:
    handle.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'counts': ledger,
                  'receipt_sha256': sha((OUT / 'narrow-comparison-receipt091.json').read_bytes())}))
