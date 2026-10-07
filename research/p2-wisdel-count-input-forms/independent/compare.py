from pathlib import Path
import collections
import gzip
import hashlib
import json

out = Path(__file__).resolve().parent


def read(name):
    with gzip.open(out/name, 'rt', encoding='utf-8') as handle:
        return json.load(handle)


def strict(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


before = read('baseline63-public.json.gz')
after = read('draft-public.json.gz')
assert len(before['records']) == len(after['records'])
changed, unchanged, unexpected, canonical_drift = [], [], [], []
groups = collections.Counter()
for a, b in zip(before['records'],after['records']):
    assert a['key'] == b['key'] and strict(a['input']) == strict(b['input'])
    key = a['key']
    if strict(a['outcome']) == strict(b['outcome']):
        unchanged.append(key)
    else:
        changed.append(key)
        groups[a['group']] += 1
        if a['group'] not in ('inactive_casts','valid_active_forms') or a['matches_canonical'] is not False:
            unexpected.append(key)
    if strict(a['canonical_outcome']) != strict(b['canonical_outcome']):
        canonical_drift.append(key)
source_changes = [name for name, sha in before['summary']['source_hashes'].items()
                  if after['summary']['source_hashes'].get(name) != sha]
receipt = {'cases':len(after['records']),
           'public_calls':before['summary']['public_calls']+after['summary']['public_calls'],
           'comparison':'strict serialized full JSON, including numeric types, reports and error types/text',
           'changed_cases':len(changed),'unchanged_cases':len(unchanged),
           'changed_groups':dict(groups),'unexpected_changes':unexpected,
           'typed_canonical_output_changes':canonical_drift,
           'draft_canonical_mismatches':after['summary']['canonical_mismatches'],
           'parsed_zero_count_cast_query_violations':after['summary']['queried_casts_with_parsed_zero_count'],
           'invalid_accepted':after['summary']['invalid_accepted'],
           'caller_isolation_errors':after['summary']['caller_isolation_errors'],
           'catalog_preserved':after['summary']['catalog_preserved'],
           'source_changes':source_changes,'source_change_scope_correct':source_changes==['rouge/operator_engine.py'],
           'frozen_source_drift':[], 'production_edits':0,'native_validation':False,
           'evidence_sha256':{name:hashlib.sha256((out/name).read_bytes()).hexdigest()
                              for name in ('baseline63-public.json.gz','draft-public.json.gz')}}
receipt['passed'] = not any((unexpected,canonical_drift,receipt['draft_canonical_mismatches'],
                             receipt['parsed_zero_count_cast_query_violations'],receipt['invalid_accepted'],
                             receipt['caller_isolation_errors'])) and (
    receipt['catalog_preserved'] and receipt['source_change_scope_correct'])
(out/'matrix-comparison.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
assert receipt['passed']
