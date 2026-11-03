import hashlib
import json
import sys
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).parent
sys.path.insert(0, str(OUT / 'baseline'))
from rouge.catalog import catalog

def digest(p):
    b = p.read_bytes(); return {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}

token_path = ROOT / 'research/p2-token-duration/source-receipt.json'
susuro_path = ROOT / 'research/p2-susuro-recipient-factor/source-receipt.json'
token = json.loads(token_path.read_text())
susuro = json.loads(susuro_path.read_text())
selector = 'uniequip_table.equipDict.uniequip_002_mcnist'
mechanist = token['selectors'][selector]
susuro_selector = 'uniequip_table.equipDict.uniequip_002_susuro'
susuro_module = susuro['selectors'][susuro_selector]
selected = {selector: mechanist, susuro_selector: susuro_module}
for source, op in [(mechanist, 'mechanist'), (susuro_module, 'char_298_susuro')]:
    module_id = source.get('uniEquipId', 'uniequip_002_susuro')
    current = next(m for m in catalog()['operators'][op]['modules'] if m['id'] == module_id)
    assert current['unlock_elite'] == int(source['unlockEvolvePhase'].split('_')[1])
    assert current['unlock_level'] == source['unlockLevel']
    selected['current_catalog.' + op + '.' + module_id] = current

raw_path = ROOT / '.cache/p2-s1-binding/character_table.json'
raw = json.loads(raw_path.read_text())
raw_selected = {}
talent_gate_records = []
candidate_gate_records = []
raw_candidates_omitted_by_existing_catalog = []
for op, profile in catalog()['operators'].items():
    native = {'kaltsit': 'char_1052_kalts2', 'silverash': 'char_1045_svash2', 'mechanist': 'char_4230_mcnist'}.get(op, op)
    if native not in raw: continue
    raw_selected['character_table.' + native + '.talents'] = raw[native]['talents']
    original_talents = raw[native]['talents'] or []
    assert len(profile['talents']) == len(original_talents)
    for slot, (candidates, original_slot) in enumerate(zip(profile['talents'], original_talents)):
        original_candidates = [(index, item) for index, item in enumerate(original_slot['candidates']) if item['name']]
        raw_candidates_omitted_by_existing_catalog.extend(
            f'character_table.{native}.talents[{slot}].candidates[{index}]'
            for index, item in enumerate(original_slot['candidates']) if not item['name'])
        assert len(candidates) == len(original_candidates)
        for candidate, (index, original) in zip(candidates, original_candidates):
            assert candidate['name'] == original['name']
            assert candidate['phase'] == int(original['unlockCondition']['phase'].split('_')[1])
            assert candidate['level'] == original['unlockCondition']['level']
            assert candidate['potential_rank'] == original['requiredPotentialRank']
            candidate_gate_records.append({
                'operator': op,
                'selector': f'character_table.{native}.talents[{slot}].candidates[{index}]',
                'unlockCondition': original['unlockCondition'],
                'requiredPotentialRank': original['requiredPotentialRank'],
                'normalized_gate_exactly_matches_raw': True})
    from rouge.operator_engine import selected_talents
    for elite, phase in enumerate(profile['phases']):
        for level in (1, phase['max_level']):
            for potential in range(1, 7):
                scenario = {'elite': elite, 'level': level, 'potential': potential}
                chosen, parts = selected_talents(profile, scenario)
                expected = []
                for candidates in profile['talents']:
                    eligible = [t for t in candidates if t['phase'] <= elite and (t['phase'] < elite or t['level'] <= level) and t['potential_rank'] <= potential - 1]
                    if eligible: expected.append(eligible[-1])
                assert chosen == expected and parts == []
                talent_gate_records.append({'operator': op, 'elite': elite, 'level': level, 'potential': potential,
                                            'selected_names': [t['name'] for t in chosen], 'selected_candidates_eligible': True})
obj = {'game_commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
       'qualification_sources': {'mechanist_receipt': {'path': str(token_path), **digest(token_path), 'original_table_sha256': token['sources']['uniequip_table']['sha256']},
                                 'susuro_receipt': {'path': str(susuro_path), **digest(susuro_path), 'original_table_sha256': susuro['sources']['uniequip_table']['sha256']}},
       'reused_original_selectors': selected, 'raw_uniequip_file_rehashed_now': False,
       'current_character_raw': {'path': str(raw_path), **digest(raw_path)},
       'base_talent_selectors': raw_selected, 'base_talent_gate_cases': len(talent_gate_records),
       'normalized_base_candidate_gate_count': len(candidate_gate_records),
       'normalized_base_candidate_gate_records': candidate_gate_records,
       'raw_candidate_selectors_omitted_by_existing_catalog': raw_candidates_omitted_by_existing_catalog,
       'omitted_raw_candidate_scope': 'Existing normalized catalog excludes null-name candidates; this audit neither changes that selection nor establishes their native attachment rules.',
       'base_talent_gate_records': talent_gate_records,
       'base_talent_gate_scope': '30 non-patch forms; E0/E1/E2, min/cap level, P1..P6; current normalized candidate selection checked against phase/level/potential predicates.',
       'raw_hidden_module_attachment_rule_added': False,
       'new_native_validation': False}
(OUT / 'source-receipt.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'mechanist_unlock': [mechanist['unlockEvolvePhase'],mechanist['unlockLevel']], 'susuro_unlock': [susuro_module['unlockEvolvePhase'],susuro_module['unlockLevel']], 'base_talent_gate_cases': len(talent_gate_records)}))
