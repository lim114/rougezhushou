"""Read-only public report audit, pinned to archived section-055 source."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
FROZEN = ROOT / 'frozen'
sys.path.insert(0, str(FROZEN))
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

HEAD = '15e0fa455aad05d27303428299d24d15db4c572c'
RIVER = 'rogue_6_relic_fight_22'
ROSE = 'rogue_6_relic_legacy_81'
BASE = {'operator': 'char_1042_phatm2', 'base_attack': 1000}
CASES = {
    'wine_s1_default_no_river': {**BASE, 'skill': 1},
    'wine_s1_explicit_empty_relics': {**BASE, 'skill': 1, 'relic_ids': []},
    'wine_s1_magic_taken_twice': {**BASE, 'skill': 1, 'relic_ids': [],
        'effects': [{'kind': 'damage_taken', 'damage_type': 'magic', 'value': 1}]},
    'wine_s1_with_river': {**BASE, 'skill': 1, 'relic_ids': [RIVER]},
    'wine_s2_incoming_no_river': {**BASE, 'skill': 2, 'enemy_attack_count': 20,
        'relic_ids': []},
    'wine_s2_incoming_with_river': {**BASE, 'skill': 2, 'enemy_attack_count': 20,
        'relic_ids': [RIVER]},
    'wine_s2_zero_incoming_control': {**BASE, 'skill': 2, 'enemy_attack_count': 0,
        'relic_ids': []},
    'wine_s3_no_river_control': {**BASE, 'skill': 3, 'relic_ids': []},
    'medical_amiya_s2_rose_control': {'operator': 'char_1037_amiya3', 'skill': 2,
        'base_attack': 1000, 'relic_ids': [ROSE]},
    'hsgma2_s2_rose_control': {'operator': 'char_1044_hsgma2', 'skill': 2,
        'base_attack': 1000, 'relic_ids': [ROSE]},
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

results = {}
for name, scenario in CASES.items():
    before = deepcopy(scenario)
    result = calculate_damage(scenario)
    assert scenario == before, name
    sections = {section['id']: section for section in result['report']['sections']}
    results[name] = {'public_input': scenario, 'public_result': result,
        'formatted_report': format_estimate(result),
        'subtotal_section': sections.get('known_damage_subtotals')}

for name in ('wine_s1_default_no_river', 'wine_s1_explicit_empty_relics',
             'wine_s1_magic_taken_twice', 'wine_s2_incoming_no_river'):
    result = results[name]['public_result']
    assert 'neural_relic_reference' not in result, name
    assert not any(record['id'] == RIVER for record in
        result.get('relic_resolution', {}).get('records', [])), name
    assert result['total_damage'] is None, name
    assert any('河谷祭祈' in note for note in
        results[name]['subtotal_section']['notes']), name

assert results['wine_s1_default_no_river']['public_result'] == \
    results['wine_s1_explicit_empty_relics']['public_result']
assert results['wine_s1_default_no_river']['public_result'][
    'known_damage_subtotals']['window_damage'] == 3000
assert results['wine_s1_magic_taken_twice']['public_result'][
    'known_damage_subtotals']['window_damage'] == 6000
assert results['wine_s1_magic_taken_twice']['public_result'][
    'neural_s1_reference']['direct_buildup_raw'] == 300
assert 'known_damage_subtotals' not in results[
    'wine_s2_zero_incoming_control']['public_result']
assert not any('河谷祭祈' in note for note in
    results['wine_s3_no_river_control']['subtotal_section']['notes'])
medical = results['medical_amiya_s2_rose_control']['public_result']
assert medical['total_healing'] is None
assert medical['known_healing_subtotals']['window_healing'] == 1200
healing = next(c for c in medical['components']
    if c.get('damage_healing') is not None)
assert healing['actual_total'] is None
assert sum(c['total'] for c in healing['known_healing_sources']) == 1200

payload = {'head': HEAD, 'freeze_directory': str(FROZEN),
    'runtime_python': sys.version, 'results': results}
(ROOT / 'public-results.json').write_text(json.dumps(payload,
    ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
manifest = {str(path.relative_to(FROZEN)): sha(path)
    for path in FROZEN.rglob('*') if path.is_file()}
(ROOT / 'freeze-manifest.json').write_text(json.dumps({'head': HEAD,
    'files': manifest}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'head': HEAD, 'public_cases': len(results),
    'numeric_counterexamples': 0, 'report_wrong_source_cases': 4,
    'artifacts': ['public-results.json', 'freeze-manifest.json']},
    ensure_ascii=False))
