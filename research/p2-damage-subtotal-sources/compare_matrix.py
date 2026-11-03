"""Require every whole-output difference to be an allowed subtotal source note."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
base_path = ROOT / 'baseline-matrix.json'
draft_path = ROOT / 'draft-matrix.json'
base = json.loads(base_path.read_text())
draft = json.loads(draft_path.read_text())
assert base['cases'].keys() == draft['cases'].keys()
assert base['skill_identities'] == draft['skill_identities']
RIVER = 'rogue_6_relic_fight_22'

def notes(result):
    return next((s['notes'] for s in result['report']['sections']
                 if s['id'] == 'known_damage_subtotals'), None)

changed = {}
for name, before in base['cases'].items():
    after = draft['cases'][name]
    assert before['scenario'] == after['scenario'], name
    b, d = deepcopy(before['result']), deepcopy(after['result'])
    bnotes, dnotes = notes(b), notes(d)
    if bnotes != dnotes:
        assert bnotes is not None and dnotes is not None, name
        changed[name] = {'scenario': after['scenario'],
                         'before': bnotes, 'after': dnotes}
        for value in (b, d):
            for s in value['report']['sections']:
                if s['id'] == 'known_damage_subtotals':
                    s['notes'] = []
    assert b == d, name
    result = after['result']
    if dnotes is not None:
        joined = '\n'.join(dnotes)
        river_present = bool(result.get('neural_relic_reference'))
        assert river_present or '河谷' not in joined, name
        assert '不能当作完整' in joined, name
        if result.get('neural_s1_reference'):
            assert '暗夜回声' in joined and '刷新顺序' in joined, name
        if result.get('neural_incoming_reference'):
            assert '堕梦' in joined and '没有事件时刻' in joined, name
        if result.get('neural_relic_reference'):
            assert '河谷祭祈' in joined, name
    if before['formatted_report'] != after['formatted_report']:
        assert name in changed, name
    if name not in changed:
        assert before == after, name

payload = {'passed': True, 'baseline_head': base['baseline_head'],
           'public_pairs': len(base['cases']), 'public_calls': 2*len(base['cases']),
           'changed_notes_only': len(changed),
           'unchanged_whole_outputs': len(base['cases'])-len(changed),
           'changed_cases': changed,
           'numeric_scope_complete_phase_sp_and_actual_fields_identical': True,
           'all_other_report_fields_identical': True,
           'baseline_matrix_sha256': hashlib.sha256(base_path.read_bytes()).hexdigest(),
           'draft_matrix_sha256': hashlib.sha256(draft_path.read_bytes()).hexdigest()}
(ROOT / 'matrix-comparison.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k: v for k, v in payload.items() if k != 'changed_cases'}, ensure_ascii=False))
