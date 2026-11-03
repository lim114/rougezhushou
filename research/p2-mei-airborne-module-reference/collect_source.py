"""Re-read exact pinned original records; do not promote tables to native proof."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT.parent / 'p2-after-070-source-audit'
BASELINE = AUDIT / 'baseline070'
GAME_COMMIT = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
paths = {
    'character_table': Path('/workspace/rougezhushou/.cache/p2-s1-binding/character_table.json'),
    'battle_equip_table': AUDIT / 'originals/battle_equip_table.json',
    'uniequip_table': AUDIT / 'originals/uniequip_table.json'}
expected = {
    'character_table': '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697',
    'battle_equip_table': '006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460',
    'uniequip_table': 'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9'}
tables, sources = {}, {}
for name, path in paths.items():
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == expected[name]
    tables[name] = json.loads(raw)
    sources[name] = {'path': str(path), 'sha256': digest, 'bytes': len(raw),
                     'url': 'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/'
                            + GAME_COMMIT + '/zh_CN/gamedata/excel/' + name + '.json',
                     'fresh_pinned_https_download': name != 'character_table',
                     'tls_verification_preserved': True,
                     'hash_rechecked': True}
char = tables['character_table']['char_133_mm']
meta = tables['uniequip_table']['equipDict']['uniequip_002_mm']
battle = tables['battle_equip_table']['uniequip_002_mm']
profile = json.loads((BASELINE / 'rouge/data/catalog.json').read_text())['operators']['char_133_mm']
module = next(m for m in profile['modules'] if m['id'] == 'uniequip_002_mm')
assert meta['charId'] == 'char_133_mm'
assert (meta['unlockEvolvePhase'], meta['unlockLevel']) == ('PHASE_2', 40)
assert (module['unlock_elite'], module['unlock_level']) == (2, 40)
assert tables['uniequip_table']['charEquip']['char_133_mm'] == ['uniequip_001_mm', 'uniequip_002_mm']
for native, selected in zip(char['skills'], profile['skills']):
    assert selected['id'] == native['skillId']
    assert selected['unlock_elite'] == int(native['unlockCond']['phase'][-1])
assert [p['maxLevel'] for p in char['phases']] == [p['max_level'] for p in profile['phases']]
records = []
for index, phase in enumerate(battle['phases']):
    assert phase['equipLevel'] == index + 1
    assert module['levels'][index]['parts'] == phase['parts']
    assert module['levels'][index]['attributes'] == {b['key']: b['value'] for b in phase['attributeBlackboard']}
    part = phase['parts'][0]
    assert (part['target'], part['isToken'], part['validInGameTag'], part['validInMapTag']) == ('TRAIT', False, None, None)
    assert part['resKey'] == 'mm_equip_1_' + str(index + 1) + '_p1'
    candidate = part['overrideTraitDataBundle']['candidates'][0]
    assert candidate['unlockCondition'] == {'phase': 'PHASE_2', 'level': 40}
    assert candidate['requiredPotentialRank'] == 0
    assert candidate['additionalDescription'] == '攻击空中单位时攻击力提升至<@ba.kw>{atk_scale:0%}</>'
    assert candidate['blackboard'] == [{'key': 'atk_scale', 'value': 1.1, 'valueStr': None}]
    records.append({'selector': 'battle_equip_table.uniequip_002_mm.phases[' + str(index) + ']', 'record': phase})
for native in char['talents'][0]['candidates']:
    normalized = {'phase': int(native['unlockCondition']['phase'][-1]),
                  'level': native['unlockCondition']['level'], 'potential_rank': native['requiredPotentialRank'],
                  'name': native['name'], 'description': native['description'],
                  'values': {b['key']: b['value'] for b in native['blackboard']}}
    assert normalized in profile['talents'][0]
native_files = sorted(p for p in Path('/workspace/rougezhushou/.cache/research').rglob('*')
                      if p.is_file() and p.suffix in ('.json', '.txt', '.md', '.py'))
needle = ('mm_equip_1_', 'uniequip_002_mm', 'char_133_mm', 'skchr_mm_')
searched = {str(p): {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                    'bytes': p.stat().st_size,
                    'matching_needles': [s for s in needle if s in p.read_text(errors='replace')]}
            for p in native_files}
receipt = {
    'baseline_commit': '552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9',
    'game_commit': GAME_COMMIT, 'source_files': sources,
    'exact_owner_binding': {'character_selector': 'character_table.char_133_mm',
                            'charEquip_selector': 'uniequip_table.charEquip.char_133_mm',
                            'metadata_selector': 'uniequip_table.equipDict.uniequip_002_mm',
                            'metadata_record': meta},
    'character_records': {'name': char['name'], 'profession': char['profession'],
                          'skills': char['skills'], 'talents': char['talents']},
    'all_three_module_records': records, 'catalog_full_module_parts_and_attribute_match': True,
    'existing_numeric_talent_source_match': True,
    'native_evidence_search': {'scope': 'Retained .cache/research text exports only, not a complete game installation',
                               'needles': list(needle), 'files': searched,
                               'exact_matches': [p for p, v in searched.items() if v['matching_needles']]},
    'conclusions': {
        'table_conditional_attack_scale_parameter': 1.1,
        'actual_target_airborne': None, 'native_attachment_verified': False,
        'damage_composition_verified': False, 'live_state_verified': False,
        'numeric_multiplier_authorized_by_this_evidence': False,
        'implementation_scope': 'Qualified source-only reference; no checkbox, target inference, damage formula or clock change'}}
(ROOT / 'source-receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'raw_files_verified': len(sources), 'module_levels': len(records),
                  'retained_native_files_searched': len(searched),
                  'exact_native_matches': receipt['native_evidence_search']['exact_matches']}, ensure_ascii=False))
