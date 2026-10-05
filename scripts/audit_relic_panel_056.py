"""Read-only public-data/native audit, independent arithmetic, no live state."""
import argparse
import hashlib
import json
import math
import re
import struct
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / '.cache/research/relic-panel-056'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_cultivation(character, elite, level, trust, potential, module=None):
    """Oracle over original character/equip table; no derived profile values."""
    frames = character['phases'][elite]['attributesKeyFrames']
    low, high = frames[0], frames[-1]
    fraction = ((level - low['level']) / (high['level'] - low['level'])
                if high['level'] != low['level'] else 0)
    result = {key: low['data'][key] + fraction * (high['data'][key] - low['data'][key])
              for key in ('maxHp', 'atk', 'def')}
    favor = character['favorKeyFrames'][-1]['data']
    for key in result:
        result[key] = math.floor(result[key] + .5) + math.floor(favor[key] * trust / 100 + .5)
    names = {'MAX_HP': 'maxHp', 'ATK': 'atk', 'DEF': 'def'}
    for rank in character['potentialRanks'][:potential - 1]:
        for change in ((rank.get('buff') or {}).get('attributes') or {}).get('attributeModifiers') or []:
            if change['attributeType'] in names:
                assert change['formulaItem'] == 'ADDITION'
                result[names[change['attributeType']]] += change['value']
    if module:
        names = {'max_hp': 'maxHp', 'atk': 'atk', 'def': 'def'}
        for change in module['attributeBlackboard']:
            if change['key'] in names:
                result[names[change['key']]] += change['value']
    return result


def writer_oracle(base, factor):
    # All audit factors are exactly representable selected small rational values;
    # this is independent of production's Q32/card helpers and catches its boundary.
    return round(struct.unpack('<f', struct.pack('<f', base * factor))[0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch-web', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    from rouge.catalog import catalog, operator_attributes
    from rouge.damage import calculate_damage
    from rouge.relics import mechanics
    receipt = json.loads((ROOT / '.cache/game-data/receipt.json').read_text('utf-8'))
    sources = {}
    for name in ('character_table', 'skill_table', 'battle_equip_table', 'roguelike_topic_table'):
        path = ROOT / '.cache/game-data' / (name + '.json')
        assert sha(path) == receipt['files'][name]['sha256']
        sources[name] = {**receipt['files'][name], 'local_path': str(path.relative_to(ROOT))}
    raw = json.loads((ROOT / '.cache/game-data/character_table.json').read_text('utf-8'))
    patch_path = ROOT / '.cache/game-data/char_patch_table.json'
    patch_receipt = json.loads((ROOT / 'rouge/data/operator-profiles.json').read_text('utf-8'))['source']['files']['char_patch_table']
    assert sha(patch_path) == patch_receipt['sha256']
    sources['char_patch_table'] = patch_receipt
    raw.update(json.loads(patch_path.read_text('utf-8'))['patchChars'])
    equips = json.loads((ROOT / '.cache/game-data/battle_equip_table.json').read_text('utf-8'))
    topic = json.loads((ROOT / '.cache/game-data/roguelike_topic_table.json').read_text('utf-8'))['details']['rogue_6']
    template_path = ROOT / '.cache/research/p1-rules-050/buff_template_data.json'
    assert sha(template_path) == 'b119917318c464f92d28fc5eb40b2069e3644674d26cace165f17bf9044e00ff'
    template = json.loads(template_path.read_text('utf-8'))
    sources['buff_template'] = {'sha256': sha(template_path),
        'url': 'https://raw.githubusercontent.com/fexli/ArknightsResource/d0b5af0b004b044d322397ce5ae79632b6d9fcdd/gamedata/battle/buff_template_data.json'}
    web = []
    urls = [('attribute', 'https://prts.wiki/w/游戏数据基础'),
            ('relics', 'https://prts.wiki/w/沉沦者的黑流树海/拟造物质编目')]
    if args.fetch_web:
        for name, url in urls:
            encoded = urllib.parse.quote(url, safe=':/')
            request = urllib.request.Request(encoded, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read()
            html = content.decode('utf-8')
            revision = re.search(r'"wgRevisionId"\s*:\s*(\d+)', html)
            path = OUT / (name + '-web.html')
            path.write_bytes(content)
            web.append({'url': url, 'fetched_unix': time.time(), 'sha256': sha(path),
                'revision': int(revision.group(1)) if revision else None,
                'bytes': len(content)})
        (OUT / 'web-receipt.json').write_text(json.dumps(web, ensure_ascii=False, indent=2), 'utf-8')
    elif (OUT / 'web-receipt.json').exists():
        web = json.loads((OUT / 'web-receipt.json').read_text('utf-8'))
    checked = []
    for op, profile in catalog()['operators'].items():
        character = raw[profile['id']]
        for elite, phase in enumerate(character['phases']):
            for level in sorted({1, phase['maxLevel'], max(1, phase['maxLevel'] // 2)}):
                for trust in (0, 50, 100):
                    for potential in (1, 3, 6):
                        expected = raw_cultivation(character, elite, level, trust, potential)
                        actual = operator_attributes(op, elite, level, trust, potential)
                        for game, public in (('maxHp', 'hp'), ('atk', 'attack'), ('def', 'defense')):
                            assert actual[public] == expected[game], (op, elite, level, trust, potential, public)
                        checked.append([op, elite, level, trust, potential])
        for module in profile['modules']:
            elite, level = module['unlock_elite'], module['unlock_level']
            for stage in range(1, len(module['levels']) + 1):
                expected = raw_cultivation(character, elite, level, 100, 1,
                    equips[module['id']]['phases'][stage - 1])
                actual = operator_attributes(op, elite, level, 100, 1, module['id'], stage)
                for game, public in (('maxHp', 'hp'), ('atk', 'attack'), ('def', 'defense')):
                    assert actual[public] == expected[game], (op, module['id'], stage, public)
                checked.append([op, 'module', module['id'], stage])
    m = mechanics()
    rune_sources = []
    for owner_kind in ('relics', 'char_buffs'):
        for identity, entry in m[owner_kind].items():
            raw_buffs = entry['raw_buffs'] if owner_kind == 'relics' else entry['raw']['buffs']
            original = topic['relics'][identity]['buffs'] if owner_kind == 'relics' else topic['charBuffData'][identity]['buffs']
            assert raw_buffs == original, (owner_kind, identity, 'exact pinned source')
            for effect in entry['effects']:
                if effect.get('attribute_layer') != 'relic_rune':
                    continue
                source = raw_buffs[effect['source_buff_index']]
                assert source['key'] == effect['source_buff_key']
                allowed = {'char_attribute_mul': 'MULTIPLIER', 'char_attribute_add': 'ADDITION',
                    'char_attribute_final_scaler': 'FINAL_SCALER',
                    'layer_char_attribute_mul': 'MULTIPLIER', 'layer_char_attribute_add': 'ADDITION',
                    'char_random_target_attribute': 'MULTIPLIER',
                    'layer_char_random_target_attribute': 'MULTIPLIER'}
                assert allowed[source['key']] == effect['formula_item']
                bb = {b['key']: b['valueStr'] if b.get('valueStr') is not None else b['value']
                      for b in source['blackboard']}
                attribute = {'attack_pct': 'atk', 'hp_pct': 'max_hp', 'defense_pct': 'def',
                    'attack_speed': 'attack_speed', 'resistance_flat': 'magic_resistance',
                    'redeploy_delta': 'respawn_time', 'deployment_cost_add': 'cost',
                    'deployment_cost_pct': 'cost', 'regeneration': 'hp_recovery_per_sec',
                    'regeneration_hp_ratio': 'hp_recovery_per_sec_by_max_hp_ratio',
                    'defense_penetration': 'def_penetrate'}[effect['kind']]
                if source['key'] in ('char_random_target_attribute', 'layer_char_random_target_attribute'):
                    attribute = 'multiplier@' + attribute
                assert bb[attribute] == effect['value'], (owner_kind, identity, attribute)
                for selector, public in [('selector.profession', 'profession'),
                        ('selector.buildable', 'position'), ('selector.sub_profession', 'subprofession')]:
                    assert str(bb.get(selector, '')).lower() == effect[public], (identity, selector)
                rune_sources.append({'owner': owner_kind, 'id': identity,
                    'source_index': effect['source_buff_index'], 'source_key': source['key'],
                    'kind': effect['kind'], 'formula': effect['formula_item'],
                    'raw_attribute_key': attribute, 'raw_value': bb[attribute],
                    'selectors': {public: effect[public] for public in ('profession', 'position', 'subprofession')}})
    grudge = template['rogue6_relic_fight_63']['eventToActions']['ON_BUFF_START'][0]['_buff']
    assert grudge['attributes']['attributeModifiers'][0]['formulaItem'] == 'MULTIPLIER'
    # Differential scope checks preserve the existing self-talent model while
    # independently testing whether each of 87 skills applies rune integer fields
    # before its normal multipliers/final additions. This is not an oracle for
    # every operator's unknown talent/module/combat scripts.
    skill_cases = []
    for op, profile in catalog()['operators'].items():
        cultivated = operator_attributes(op)
        for skill in range(1, len(profile['skills']) + 1):
            base = calculate_damage({'operator': op, 'skill': skill})
            for field, rid, factor in [('hp', 'rogue_6_relic_legacy_90', 1.5),
                    ('defense', 'rogue_6_relic_legacy_14', 1.5),
                    ('attack', 'rogue_6_relic_legacy_142', 1.5)]:
                buffed = calculate_damage({'operator': op, 'skill': skill, 'relic_ids': [rid]})
                previous = base['estimate']['base_stats'][field]
                flat = 90 if op == 'char_4087_ines' and field == 'attack' else (
                    previous - cultivated[field] if op == 'silverash' and field == 'defense' else 0)
                expected = (previous - flat) / cultivated[field] * writer_oracle(cultivated[field], factor) + flat
                actual = buffed['estimate']['base_stats'][field]
                assert abs(expected - actual) < 1e-7, (op, skill, field, expected, actual)
                skill_cases.append({'operator': op, 'skill': skill, 'field': field,
                                    'expected': expected, 'actual': actual})
    result = {'passed': True, 'sources': sources, 'web': web,
        'cultivation_cases': len(checked), 'rune_source_entries': len(rune_sources),
        'rune_source_matrix': rune_sources, 'skill_stat_cases': skill_cases,
        'skill_stat_case_count': len(skill_cases), 'all_priority_1_complete': False,
        'game_operated': False, 'private_run_state_read': False, 'chat_sent': False,
        'scope': 'verified source-layer and integer-writer correction; unchanged unknown scripts remain unknown'}
    path = OUT / ('audit-' + str(time.time_ns()) + '.json')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf-8')
    print(json.dumps({'path': str(path.relative_to(ROOT)), 'passed': True,
        'cultivation_cases': len(checked), 'rune_source_entries': len(rune_sources),
        'skill_stat_case_count': len(skill_cases)}))


if __name__ == '__main__':
    main()
