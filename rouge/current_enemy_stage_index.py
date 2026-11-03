"""Exact current enemy-reference -> stage lookup; no spawn or stat prediction."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

from . import current_battle_reference as battle
from . import current_stage_directory as directory

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-enemy-stage-index-370'
DATA = 'rouge/data/current-enemy-stage-index.json'
NOTES = PACK + '/source-notes.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = 'f7efb28d86690cab46786de63f2b8e10ddbc1fa76aa1d98d6956ca7f1b96bceb'
TIERS = ((None, '总览（全部记录）'), ('NORMAL', '普通'), ('ELITE', '精英'),
         ('BOSS', '领袖'), ('UNKNOWN', '类别未确认'))
SCOPES = ((None, '全部关联记录'), ('not_counted', '原设置不计入敌人数'))
NOTICE = '按敌人中文名查找关联关卡。这里列的是关卡资料中的记录，含随机候选和特殊实体；不表示每局必出，也不是实际敌人数。'
UNAVAILABLE = '敌人与关卡的对应资料无法核对；旧结果和关联窗口已清除。资料恢复后请重新选择。'


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) in (list, tuple):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf8')).hexdigest()


def _file(name):
    if type(name) is not str:
        raise ValueError('Public relative path required')
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or rel.as_posix() != name:
        raise ValueError('Unsafe public source')
    path = ROOT.joinpath(*rel.parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Regular public source required')
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Linked source refused')
    return path


def enabled_paths(value, prefix=''):
    """List only enabled wrappers; placeholders are not overrides."""
    found = []
    if type(value) is dict:
        if value.get('m_defined') is True and 'm_value' in value:
            return [prefix]
        for key, child in value.items():
            if type(child) is dict:
                found.extend(enabled_paths(child, prefix + '.' + key if prefix else key))
    return found


def derive(current, stage_directory):
    stages, rows = {}, []
    original_stages = current['version']['current']['details']['stages']
    if set(original_stages) != set(stage_directory['data']['rows']):
        raise ValueError('All exact current stages required')
    for sid in sorted(original_stages):
        stage = original_stages[sid]
        info = directory.detail(sid, reference=stage_directory)
        key = 'levels/' + stage['levelId'].lower() + '.json'
        level = current['inputs']['levels'][key]
        enemies = battle.enemy_records(level, current)
        if len(enemies) != len(level['enemyDbRefs']):
            raise ValueError('Every original reference required')
        stages[sid] = {'name': stage['name'], 'label': directory.label(info),
                       'floor': info['row']['floor'], 'play_kind': info['row']['play_kind'],
                       'region': info['row']['region'], 'variant_index': info['variant_index'],
                       'variant_count': info['variant_count'], 'level_key': key,
                       'original_stage_sha256': digest(stage), 'original_level_sha256': digest(level),
                       'reference_count': len(enemies)}
        for e in enemies:
            if e['key'] != str(e['reference_index']) or e['raw_binding'] != level['enemyDbRefs'][e['reference_index']]:
                raise ValueError('Exact reference position required')
            rows.append({'stage_id': sid, 'enemy_key': e['key'], 'name': e['name'],
                         'enemy_id': e['id'], 'database_level': e['level'],
                         'tier': e['tier'], 'use_db': e['use_db'],
                         'reference_index': e['reference_index'],
                         'exact_database_level_present': e['exact_database_level_present'],
                         'binding_sha256': digest(e['raw_binding']),
                         'enabled_override_paths': enabled_paths(e['raw_binding'].get('overwrittenData') or {}),
                         'not_counted': e['declared_traits']['values'].get('notCountInTotal'),
                         'portrait': deepcopy(e['portrait']),
                         'portrait_prefab_key': e['prefab_key']})
    return {'schema': 'current_enemy_stage_index_370_v1', 'stages': stages, 'rows': rows,
            'actual_spawn_list': None, 'actual_enemy_count': None, 'actual_server_verified': False}


def packet():
    try:
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        if manifest['schema'] != 'current_enemy_stage_index_370_manifest_v1' or set(manifest['files']) != {DATA, NOTES}:
            return None
        blobs = {}
        for name, pin in manifest['files'].items():
            body = _file(name).read_bytes()
            if type(pin['bytes']) is not int or len(body) != pin['bytes'] or sha256(body).hexdigest() != pin['sha256']:
                return None
            blobs[name] = body
        current, stage_directory = battle.packet(), directory.packet()
        if current is None or stage_directory is None:
            return None
        source_ids = {'battle': current['identity'], 'stage_directory': stage_directory['source_identity'],
                      'version': current['version']['source_identity']}
        if not same(manifest['source_identities'], source_ids):
            return None
        data = json.loads(blobs[DATA])
        if not same(data, derive(current, stage_directory)):
            return None
        return {'data': data, 'source_notes': json.loads(blobs[NOTES]),
                'source_identity': (MANIFEST_SHA256, *source_ids.values()),
                'actual_spawn_list': None, 'actual_enemy_count': None,
                'actual_server_verified': False, 'run_updated': False}
    except (OSError, ValueError, KeyError, TypeError, IndexError):
        return None


def rows(query='', tier=None, scope=None, floor=None, kind=None, *, reference=None):
    ref = reference if reference is not None else packet()
    if ref is None or type(query) is not str or tier not in dict(TIERS) or scope not in dict(SCOPES):
        return []
    if floor not in dict(directory.FLOORS) or kind not in dict(directory.KINDS):
        return []
    query = query.strip().casefold()
    result = []
    for row in ref['data']['rows']:
        stage = ref['data']['stages'][row['stage_id']]
        if query and query not in row['name'].casefold():
            continue
        if tier is not None and (row['tier'] or 'UNKNOWN') != tier:
            continue
        if scope == 'not_counted' and row['not_counted'] is not True:
            continue
        if floor is not None and stage['floor'] != floor:
            continue
        if kind is not None and stage['play_kind'] != kind:
            continue
        result.append(deepcopy(row))
    return result


def locate(stage_id, enemy_key, *, reference=None):
    if type(stage_id) is not str or type(enemy_key) is not str:
        return None
    ref = reference if reference is not None else packet()
    if ref is None:
        return None
    row = next((r for r in ref['data']['rows'] if r['stage_id'] == stage_id and r['enemy_key'] == enemy_key), None)
    return deepcopy(row) if row is not None else None


def detail(stage_id, enemy_key, *, reference=None):
    ref = reference if reference is not None else packet()
    if ref is None:
        return None
    row = locate(stage_id, enemy_key, reference=ref)
    if row is None:
        return None
    stage = ref['data']['stages'][stage_id]
    return {'row': row, 'stage': deepcopy(stage), 'source_identity': ref['source_identity'],
            'same_name_references': sum(r['name'] == row['name'] for r in ref['data']['rows']),
            'same_name_in_this_stage': sum(r['name'] == row['name'] and r['stage_id'] == stage_id for r in ref['data']['rows']),
            'actual_spawned': None, 'actual_count': None, 'expected_stats': None,
            'actual_server_verified': False, 'run_updated': False}


def exact_target(info):
    """Requalify a public row against a fresh complete source chain before opening."""
    if type(info) is not dict or type(info.get('row')) is not dict:
        return None
    row = info['row']
    fresh = detail(row.get('stage_id'), row.get('enemy_key'))
    if fresh is None or not same(fresh, info):
        return None
    target = battle.stage_reference(row['stage_id'])
    if target is None:
        return None
    enemy = next((e for e in target['enemies'] if e['key'] == row['enemy_key']), None)
    if enemy is None or digest(enemy['raw_binding']) != row['binding_sha256'] or enemy['name'] != row['name'] or not same(enemy['portrait'], row['portrait']):
        return None
    return {'stage_id': row['stage_id'], 'enemy_key': row['enemy_key'],
            'binding_sha256': row['binding_sha256'], 'battle': target, 'enemy': enemy}


def label(row, reference):
    stage = reference['data']['stages'][row['stage_id']]
    return row['name'] + ' · ' + stage['label'] + ' · 本关记录' + str(row['reference_index'] + 1)


def player_text(info):
    if info is None:
        return '先搜索敌人中文名或选择分类，再选择一条对应关卡。'
    row, stage = info['row'], info['stage']
    floor = dict(directory.FLOORS).get(stage['floor'], '层数未确认')
    kind = dict(directory.KINDS).get(stage['play_kind'], '来源分类未确认')
    lines = [row['name'], '', '【在哪里查到】', '关卡：' + stage['label'],
             '层数：' + floor, '作战来源：' + kind,
             '资料类别：' + battle.TIERS.get(row['tier'], '尚未确认，不按普通敌人归类'),
             '', '【这条资料能说明什么】',
             '本关固定资料明确引用了这条记录。可打开对应关卡，直接查看它的图片、已有机制、固定地图和出怪条件。',
             '资料引用不等于实际出场：随机候选、分支触发和特殊实体仍需分别核对，不能把检索结果数当敌人数。']
    if row['not_counted'] is True:
        lines += ['此关联记录明确设为“不计入总敌人数”。保留原类别；这不证明它一定是辅助单位，也不证明本局会出现。']
    if info['same_name_references'] > 1:
        lines += ['', '【同名资料的区别】', '相同名称在多份关卡或多个引用中出现；这里始终打开当前选中的那一条，不合并等级、技能或最终面板。']
    if info['same_name_in_this_stage'] > 1:
        lines += ['本关也有多个同名记录，请用“本关记录”编号区分；编号是阅读资料用的顺序，不是出场顺序。']
    if row['enabled_override_paths']:
        lines += ['本关含明确的局部专用设置，不能直接用同名图鉴条目代替本关结果。']
    if row['use_db'] is False:
        lines += ['这条记录使用本关独立配置，不套用同名敌人的图鉴数据。']
    if row['portrait'] is None:
        lines += ['', '图片：此精确引用没有可核对的图片，保留空缺，不借用同名图。']
    lines += ['', '【仍需注意】', '这里只做资料检索，不读取战斗、不计算新面板、不推荐路线。当前实际出现条件、数量和本局结果仍未知。']
    return '\n'.join(lines)
