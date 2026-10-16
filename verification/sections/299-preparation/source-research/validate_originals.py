"""Read pinned original public level files; do not import application code."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def digest(raw):
    return sha256(raw).hexdigest()

inventory_raw = (OUT / 'inventory.json').read_bytes()
inventory = json.loads(inventory_raw)
battle_raw = (ROOT / 'rouge/data/battle-previews.json').read_bytes()
battle = json.loads(battle_raw)
levels = {}
stage_checks = []
alias_entities = Counter()
alias_statuses = Counter()
for sid in sorted({g['stage_id'] for g in inventory['all_group_membership_references']}):
    stage = battle['stages'][sid]
    source = stage['level_source']
    relative = urlsplit(source['url']).path.split('/gamedata/levels/', 1)[1]
    path = ROOT / '.cache/game-data/levels' / relative
    raw = path.read_bytes()
    assert digest(raw) == source['sha256'], sid
    assert len(raw) == source['bytes'], sid
    level = json.loads(raw)
    assert len(level['waves']) == len(stage['waves']), sid
    action_count = 0
    for wi, (original_wave, built_wave) in enumerate(zip(level['waves'], stage['waves'])):
        assert len(original_wave['fragments']) == len(built_wave['fragments']), sid
        for fi, (original_fragment, built_fragment) in enumerate(zip(original_wave['fragments'], built_wave['fragments'])):
            assert original_fragment['actions'] == [r['action'] for r in built_fragment['actions']], (sid, wi, fi)
            action_count += len(original_fragment['actions'])
    assert level['mapData']['map'] == stage['map'], sid
    assert level['mapData']['tiles'] == stage['tiles'], sid
    assert (level.get('routes') or []) == stage['routes'], sid
    assert ((level.get('predefines') or {}).get('tokenInsts') or []) == stage['predefined_objects'], sid
    full_aliases = {}
    for container in ('predefines', 'hardPredefines'):
        for field in ('characterInsts', 'tokenInsts'):
            for oi, obj in enumerate((level.get(container) or {}).get(field) or []):
                if obj.get('alias'):
                    full_aliases.setdefault(obj['alias'], []).append({
                        'source_selector': f'$.{container}.{field}[{oi}]',
                        'entity_id': (obj.get('inst') or {}).get('characterKey'),
                        'raw': obj,
                    })
    for group in (g for g in inventory['all_group_membership_references'] if g['stage_id'] == sid):
        for member in group['members']:
            if member['action_type'] != 'ACTIVATE_PREDEFINED':
                continue
            key = member['entity_key']
            matches = full_aliases.get(key, []) if key else []
            status = 'empty_key' if not key else 'exact_alias' if len(matches) == 1 else 'ambiguous_alias' if matches else 'unresolved_alias'
            alias_statuses[status] += 1
            if len(matches) == 1:
                alias_entities[matches[0]['entity_id']] += 1
    levels[source['sha256']] = {
        'path': path.relative_to(ROOT).as_posix(), 'url': source['url'],
        'sha256': digest(raw), 'bytes': len(raw),
    }
    stage_checks.append({'stage_id': sid, 'stage_name': stage['name'],
                         'level_sha256': source['sha256'], 'main_actions_equal_original': action_count,
                         'map_routes_token_declarations_equal_original': True})

character_path = ROOT / '.cache/game-data/character_table.json'
character_raw = character_path.read_bytes()
reward = json.loads((ROOT / 'rouge/data/battle-reward-reference.json').read_bytes())
character_pin = reward['rules']['trap_321_shnbox']['identity_source']
assert digest(character_raw) == character_pin['sha256']
assert len(character_raw) == character_pin['bytes']
characters = json.loads(character_raw)
names = {key: {'name': characters[key]['name'], 'raw_record': characters[key]}
         for key in sorted(alias_entities) if key in characters}
result = {
    'kind': 'CACHE_ONLY_299_ORIGINAL_LEVEL_AND_NAME_READBACK_NOT_PRODUCT_TESTS',
    'inventory_sha256': digest(inventory_raw),
    'battle_previews_sha256': digest(battle_raw),
    'all_original_level_bytes_sha256_match': True,
    'original_levels': list(levels.values()),
    'unique_original_levels': len(levels),
    'total_original_level_bytes': sum(p['bytes'] for p in levels.values()),
    'stage_readbacks': stage_checks,
    'candidate_activation_alias_statuses': dict(alias_statuses),
    'candidate_activation_entities': dict(alias_entities),
    'full_primary_character_table': {'path': character_path.relative_to(ROOT).as_posix(),
                                     **character_pin},
    'exact_selected_character_names_and_records': names,
    'Qt_tests_game_chat_Git_mutation': False,
    'native_or_game_execution': False,
    'no_new_mechanism_claim': True,
}
for pin in levels.values():
    assert digest((ROOT / pin['path']).read_bytes()) == pin['sha256']
assert digest(character_path.read_bytes()) == character_pin['sha256']
assert digest((OUT / 'inventory.json').read_bytes()) == digest(inventory_raw)
assert digest((ROOT / 'rouge/data/battle-previews.json').read_bytes()) == digest(battle_raw)
path = OUT / 'original-readback.json'
path.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({key: result[key] for key in ('unique_original_levels', 'total_original_level_bytes',
    'candidate_activation_alias_statuses', 'candidate_activation_entities')}, ensure_ascii=False))
print('stages=' + str(len(stage_checks)))
print('output_sha256=' + digest(path.read_bytes()))
