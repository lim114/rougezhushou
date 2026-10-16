"""Reproduce fixed main-queue memberships. Default is read-only; --write is explicit."""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'research/p3-spawn-candidates-299'
DATA = 'rouge/data/spawn-candidates.json'
BATTLE = 'rouge/data/battle-previews.json'
BATTLE_SHA = 'f0155647af8766eb2f01e84295f85b7300264fc49b40ffc82e89800837d274f3'
CHARACTER_SHA = '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'
CHARACTER_RECORDS_SHA = '5c5c51cd627c611258d9d545090387ca72e1d1f74cdbb73f06d7a799822d3030'
LABELS = {'SPAWN': '生成敌人', 'ACTIVATE_PREDEFINED': '激活预置实体',
          'EMPTY': '空动作', 'PREVIEW_CURSOR': '路线预览标记',
          'DISPLAY_ENEMY_INFO': '敌人资料显示', 'PLAY_OPERA': '演出配置'}

def sha(raw): return sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
def identity(value): return sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())

def cell(position, nr, nc):
    if type(position) is not dict: return None
    r, c = position.get('row'), position.get('col')
    if type(r) is not int or type(c) is not int or not 0 <= r < nr or not 0 <= c < nc: return None
    return {'row': nr - 1 - r, 'col': c}

def collect_aliases(level):
    result = defaultdict(list)
    for container in ('predefines', 'hardPredefines'):
        for field in ('characterInsts', 'tokenInsts'):
            for i, obj in enumerate((level.get(container) or {}).get(field) or []):
                if obj.get('alias'):
                    result[obj['alias']].append((container, f'$.{container}.{field}[{i}]', obj))
    return result

def collect_actions(stage):
    rows = []
    for wave in stage['waves']:
        for fragment in wave['fragments']:
            wi, fi = wave['index'], fragment['index']
            for i, row in enumerate(fragment['actions']):
                rows.append({'action_id': row['id'], 'queue_id': f'w{wi}.f{fi}',
                             'wave': wi, 'fragment': fi, 'raw_action': row['action'],
                             'source_selector': f'$.waves[{wi-1}].fragments[{fi-1}].actions[{i}]'})
    return rows

def build(primary_root=None):
    battle_raw = (ROOT / BATTLE).read_bytes()
    if sha(battle_raw) != BATTLE_SHA: raise ValueError('Fixed full battle source differs.')
    battle = json.loads(battle_raw)
    selected = {}
    originals = {}
    needed_characters = set()
    for sid, stage in battle['stages'].items():
        actions = collect_actions(stage)
        if not any(row['raw_action'].get('randomSpawnGroupKey') or row['raw_action'].get('randomSpawnGroupPackKey') for row in actions): continue
        source = stage['level_source']
        name = f'{PACKAGE}/levels/{source["sha256"]}.json'
        path = ((primary_root / '.cache/game-data/levels' / urlsplit(source['url']).path.split('/gamedata/levels/', 1)[1])
                if primary_root is not None else ROOT / name)
        raw = path.read_bytes()
        if sha(raw) != source['sha256'] or len(raw) != source['bytes']: raise ValueError('Original level differs: ' + sid)
        level = json.loads(raw)
        if len(level['waves']) != len(stage['waves']): raise ValueError('Wave projection differs: ' + sid)
        for ow, bw in zip(level['waves'], stage['waves']):
            if len(ow['fragments']) != len(bw['fragments']): raise ValueError('Fragment projection differs: ' + sid)
            for of, bf in zip(ow['fragments'], bw['fragments']):
                if of['actions'] != [r['action'] for r in bf['actions']]: raise ValueError('Original action differs: ' + sid)
        if (level['mapData']['map'] != stage['map'] or level['mapData']['tiles'] != stage['tiles']
                or (level.get('routes') or []) != stage['routes']
                or ((level.get('predefines') or {}).get('tokenInsts') or []) != stage['predefined_objects']):
            raise ValueError('Fixed map/routes/token declarations differ: ' + sid)
        if [(r['id'], r['level']) for r in level['enemyDbRefs']] != [(r['id'], r['level']) for r in stage['enemies']]:
            raise ValueError('Original enemy identities differ: ' + sid)
        aliases = collect_aliases(level)
        for action in actions:
            raw_action = action['raw_action']
            if raw_action['actionType'] == 'ACTIVATE_PREDEFINED' and (raw_action.get('randomSpawnGroupKey') or raw_action.get('randomSpawnGroupPackKey')):
                for _, _, obj in aliases.get(raw_action.get('key'), []):
                    needed_characters.add((obj.get('inst') or {}).get('characterKey'))
        originals[name] = raw
        selected[sid] = (stage, level, actions, aliases, name)
    character_file = f'{PACKAGE}/character-records.json'
    if primary_root is not None:
        character_raw = (primary_root / '.cache/game-data/character_table.json').read_bytes()
        if sha(character_raw) != CHARACTER_SHA: raise ValueError('Primary character table differs.')
        all_characters = json.loads(character_raw)
        names = {'primary_source': {'url': f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{battle["source"]["game_commit"]}/zh_CN/gamedata/excel/character_table.json',
                                    'sha256': CHARACTER_SHA, 'bytes': len(character_raw)},
                 'records': {key: all_characters[key] for key in sorted(needed_characters)}}
        name_raw = encoded(names)
    else:
        name_raw = (ROOT / character_file).read_bytes()
        if sha(name_raw) != CHARACTER_RECORDS_SHA: raise ValueError('Selected primary character records differ.')
        names = json.loads(name_raw)
        if names['primary_source']['sha256'] != CHARACTER_SHA or set(names['records']) != needed_characters:
            raise ValueError('Selected primary character identity differs.')

    stages = {}
    group_total = package_total = 0
    for sid, (stage, level, actions, aliases, level_file) in selected.items():
        nr, nc = len(stage['map']), len(stage['map'][0])
        groups, packages = defaultdict(list), defaultdict(list)
        for action in actions:
            raw = action['raw_action']
            if raw.get('randomSpawnGroupKey'): groups[(action['queue_id'], raw['randomSpawnGroupKey'])].append(action)
            if raw.get('randomSpawnGroupPackKey'): packages[(action['queue_id'], raw['randomSpawnGroupPackKey'])].append(action)
        result = {'stage_id': sid, 'stage_name': stage['name'], 'difficulty': stage['difficulty'],
                  'original_level': stage['level_source'], 'original_level_file': level_file,
                  'groups': [], 'packages': []}
        for kind, grouped in (('group', groups), ('package', packages)):
            ordinals = defaultdict(int)
            for (queue, key), raw_members in grouped.items():
                ordinals[queue] += 1
                wi, fi = raw_members[0]['wave'], raw_members[0]['fragment']
                rid = 'spawn-relation:' + identity([sid, stage['level_source']['sha256'], queue, kind, key])
                relation = {'reference_id': rid, 'kind': kind, 'queue_id': queue, 'wave': wi, 'fragment': fi,
                            'ordinal': ordinals[queue], 'display_label': f'第{wi}波 · 第{fi}段 · 第{ordinals[queue]}组' + ('候选资料' if kind == 'group' else '关联包资料'),
                            'group_key': key if kind == 'group' else None,
                            'package_key': key if kind == 'package' else None,
                            'members': [], 'actual_selection': None}
                for row in raw_members:
                    raw = row['raw_action']; typ = raw['actionType']; key = raw.get('key')
                    refs = [{**{k: e[k] for k in ('id', 'level', 'name', 'level_type')}, 'source_role': 'fixed_stage_enemy_reference'}
                            for e in stage['enemies'] if typ == 'SPAWN' and e['id'] == key]
                    predefined = None
                    spawn = None
                    if typ == 'ACTIVATE_PREDEFINED':
                        matched = aliases.get(key, []) if key else []
                        objects = [{'entity_id': (obj.get('inst') or {}).get('characterKey'),
                                    'name': names['records'].get((obj.get('inst') or {}).get('characterKey'), {}).get('name'),
                                    'raw': obj, 'source_selector': selector,
                                    'display_cell': cell(obj.get('position'), nr, nc), 'container': container}
                                   for container, selector, obj in matched]
                        state = 'empty_key' if not key else 'exact_alias' if len(objects) == 1 else 'ambiguous_alias' if objects else 'unresolved_alias'
                        predefined = {'status': state, 'alias': key, 'objects': objects, 'position_is_actual': False}
                        title = ('未指定激活目标' if not key else objects[0]['name'] if len(objects) == 1 and objects[0]['name'] else '预置实体名称未确认')
                    elif typ == 'SPAWN':
                        title = ' / '.join(dict.fromkeys(e['name'] for e in refs)) or '敌人名称未确认'
                        route_index = raw.get('routeIndex')
                        if len(refs) == 1 and type(route_index) is int and 0 <= route_index < len(stage['routes']):
                            route = stage['routes'][route_index]
                            if route.get('motionMode') in ('WALK', 'FLY') and cell(route.get('startPosition'), nr, nc) is not None:
                                spawn = {'stage_id': sid, 'action_id': row['action_id'], 'enemy_id': refs[0]['id'],
                                         'level': refs[0]['level'], 'route_index_reference': route_index,
                                         'level_source_sha256': stage['level_source']['sha256']}
                    else:
                        title = '空动作（不生成敌人）' if typ == 'EMPTY' else LABELS.get(typ, '尚未确认的动作')
                    member = {'reference_id': 'spawn-member:' + identity([rid, row['action_id']]),
                              'action_id': row['action_id'], 'action_type': typ, 'type_label': LABELS.get(typ, '未确认动作类型'),
                              'display_name': title, 'display_label': title + ' · 第' + row['action_id'].rsplit('.a', 1)[1] + '条资料',
                              'queue_id': queue, 'wave': wi, 'fragment': fi, 'declared_count': raw.get('count'),
                              'raw_action': raw, 'source_selector': row['source_selector'], 'enemy_references': refs,
                              'predefined_reference': predefined, 'spawn_reference': spawn, 'actual_selected': None}
                    relation['members'].append(member)
                result['groups' if kind == 'group' else 'packages'].append(relation)
        group_total += len(result['groups']); package_total += len(result['packages'])
        stages[sid] = result
    counts = {'stages': len(stages), 'original_levels': len(originals), 'groups': group_total, 'packages': package_total}
    if counts != {'stages': 69, 'original_levels': 38, 'groups': 285, 'packages': 215}: raise ValueError('Fixed membership scope differs: ' + str(counts))
    data = {'schema_version': 1, 'reference_kind': 'fixed_main_queue_group_and_package_membership',
            'counts': counts, 'game_commit': battle['source']['game_commit'],
            'battle_source': {'file': BATTLE, 'sha256': BATTLE_SHA, 'bytes': len(battle_raw)},
            'character_records': character_file, 'stages': stages,
            'actual_selection': None, 'probabilities': None,
            'limitations': ['只含主队列固定成员关系；分支不借同名键。', '同组或同包不证明实际选择、唯一入选、互斥、共同出现或次数。',
                            '原权重不是概率；单条数量不能相加为实际敌人数。', '固定版本不证明当前服务器、实际激活、全局时间或实际路径。']}
    outputs = {DATA: encoded(data), character_file: name_raw, **originals}
    for name in ('README.md', 'SCHEMA.md'):
        outputs[f'{PACKAGE}/{name}'] = (ROOT / PACKAGE / name).read_bytes()
    manifest = {'schema': 'spawn_candidates_source_manifest_v1', 'data_file': DATA,
                'data_sha256': sha(outputs[DATA]), 'runtime_reads_primary_character_table': False,
                'global_files': sorted([DATA, BATTLE, character_file, f'{PACKAGE}/README.md', f'{PACKAGE}/SCHEMA.md']),
                'stage_files': {sid: row['original_level_file'] for sid, row in stages.items()},
                'files': {name: {'sha256': sha(raw), 'bytes': len(raw)} for name, raw in sorted({**outputs, BATTLE: battle_raw}.items())}}
    outputs[f'{PACKAGE}/source-manifest.json'] = encoded(manifest)
    return outputs, counts, tuple(stages)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--primary-root', type=Path, help='Optional fixed original game-data cache root for initial capture; no private state.')
    parser.add_argument('--write', action='store_true', help='Explicitly write generated public files and literal pins; default writes nothing.')
    args = parser.parse_args()
    outputs, counts, stages = build(args.primary_root.resolve() if args.primary_root else None)
    result = {'kind': 'SPAWN_CANDIDATES299_SOURCE_BUILD', 'write': args.write, 'counts': counts,
              'generated_files': {name: {'sha256': sha(raw), 'bytes': len(raw)} for name, raw in outputs.items()}}
    if args.write:
        for name, raw in outputs.items():
            target = ROOT / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
        core = ROOT / 'rouge/spawn_candidates.py'
        text = core.read_bytes().decode('utf8')
        text = re.sub(r"^MANIFEST_SHA256 = '[^']*'", "MANIFEST_SHA256 = '" + sha(outputs[f'{PACKAGE}/source-manifest.json']) + "'", text, flags=re.M)
        text = re.sub(r"^DATA_SHA256 = '[^']*'", "DATA_SHA256 = '" + sha(outputs[DATA]) + "'", text, flags=re.M)
        text = re.sub(r'^STAGE_IDS = .*$', 'STAGE_IDS = ' + repr(stages), text, flags=re.M)
        core.write_bytes(text.encode('utf8'))
        text = Path(__file__).read_bytes().decode('utf8')
        text = re.sub(r"^CHARACTER_RECORDS_SHA = '[^']*'", "CHARACTER_RECORDS_SHA = '" + sha(outputs[f'{PACKAGE}/character-records.json']) + "'", text, flags=re.M)
        Path(__file__).write_bytes(text.encode('utf8'))
    else:
        result['existing_outputs_match'] = all((ROOT / name).is_file() and (ROOT / name).read_bytes() == raw for name, raw in outputs.items())
        if not result['existing_outputs_match']: raise ValueError('Read-only reconstruction differs from current public outputs.')
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__': main()
