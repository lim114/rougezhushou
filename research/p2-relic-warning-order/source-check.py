import hashlib
import json
from pathlib import Path

OUT = Path(__file__).parent
source = Path('/workspace/.continuation/p2-after-055-audit/relic-scope/roguelike_topic_table.json')
data = source.read_bytes()
assert hashlib.sha256(data).hexdigest() == 'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
raw = json.loads(data)['details']['rogue_6']
mechanics_path = OUT / 'baseline/rouge/data/relic-mechanics.json'
mechanics = json.loads(mechanics_path.read_bytes())
assert (OUT / 'draft/rouge/data/relic-mechanics.json').read_bytes() == mechanics_path.read_bytes()
selectors = {}
for number in (81, 82, 83):
    key = 'rogue_6_relic_legacy_' + str(number)
    current = mechanics['relics'][key]
    assert current['raw_buffs'] == raw['relics'][key]['buffs']
    assert current['relic_params'] == raw['relicParams'][key]
    assert all(e['stacking'] == 'unverified' for e in current['effects'])
    selectors[key] = {'relic_source_selector': 'details.rogue_6.relics.' + key,
                      'params_source_selector': 'details.rogue_6.relicParams.' + key,
                      'raw_relic': raw['relics'][key], 'raw_params': raw['relicParams'][key],
                      'existing_model_effects': current['effects']}
old = (OUT / 'baseline/rouge/relics.py').read_bytes()
new = (OUT / 'draft/rouge/relics.py').read_bytes()
old_statement = b"    for group in {r.get('group') for r in candidates if r.get('stacking')=='unverified'}:\r\n"
new_statement = b"    for group in dict.fromkeys(r.get('group') for r in candidates if r.get('stacking')=='unverified'):\r\n"
assert old.count(old_statement) == 1
assert new == old.replace(old_statement, new_statement)
receipt = {'passed': True, 'source_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
           'baseline_commit': '9b7cfba08319d64175a7f51a94f339ce225bc76c',
           'original_source': {'path': str(source), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()},
           'existing_mechanics_sha256': hashlib.sha256(mechanics_path.read_bytes()).hexdigest(),
           'prior_evidence_reused': ['research/p2-healing-subtotal-scaling/NOTE.md',
                                     'research/p2-amiya-phase-reference/NOTE.md',
                                     'tests/test_relic_mechanisms_053.py',
                                     '/workspace/.continuation/p2-amiya-trait-scale-080/preparation-diagnostics80.json'],
           'selectors': selectors, 'numeric_model_changed': False,
           'native_stacking_verified': False, 'native_attachment_verified': False,
           'code_scope': {'original_set_iteration_line': 254,
                          'candidate_assembly': 'rules+effects+token_effects',
                          'warning_append_line': 259, 'record_pending_append_line': 266,
                          'replacement': 'dict.fromkeys preserves first declared candidate group order and deduplicates groups',
                          'whole_byte_difference_is_one_crlf_statement': True},
           'order_semantics': 'Each candidate has one group value. Fixed candidates define disjoint groups; enumeration order can change presentation order but does not change group membership, numeric exclusions, ammo flag or unresolved HP membership.',
           'limits': ['The original buffers are reused to preserve the existing unknown-stacking model; no stacking mechanism is newly inferred.',
                      'First declaration order is software data order, not combat activation or relic acquisition order.',
                      'Wine/native Windows/game verification is not executed by this author.']}
with (OUT / 'source-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'passed': True, 'sha256': hashlib.sha256((OUT / 'source-receipt.json').read_bytes()).hexdigest()}))
