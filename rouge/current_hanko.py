"""Exact current Hanko/smoke documentary references; no live or numeric model."""
from copy import deepcopy
from hashlib import sha256
import json
from . import current_battle_reference as battle

PACK = 'research/p3-current-hanko-365'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '46cf1a89113c0ce8abe95bd76f2f6139e46f00eb3eb3f674ff721edfb88f6e8f'
ACTORS = {'enemy_2138_shdbjg': 'hanko', 'enemy_2139_shdbj2': 'president', 'enemy_2156_shsmok': 'smoke'}
STAGES = ('ro6_b_1', 'ro6_b_1_b', 'ro6_t_4', 'ro6_b_1_dlc1', 'ro6_b_1_b_dlc1', 'ro6_e_t_4')
TOPICS = {'blink': '被阻挡时的闪现', 'flare': '照明弹与隐匿的区别',
          'attack': '普通攻击、出场和退场', 'smoke': '烟雾弹的独立效果'}
NOTICE = ('只查阅这份关卡中的准确敌人和完整机制文献。原说明与社区修正分别保留；'
          '通用文献数值不等于本关或本局已生效数值，不读取战斗站位或实际时钟。')
UNAVAILABLE = '汉科与烟雾资料无法核对，旧实体、招式、图片和入口已清除；恢复后请重新选择。'


def _same(a, b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if type(a) in (list, tuple): return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def packet():
    try:
        raw = battle.version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {PACK + '/' + name for name in ('reference-data.json', 'source-materials.json',
                    'source-notes.json', 'http-source-records.json', 'hanko-complete.html',
                    'president-complete.html', 'smoke-complete.html')}
        if (manifest['schema'] != 'current_hanko_365_manifest_v1'
                or manifest['game_commit'] != battle.version.NEW_COMMIT
                or set(manifest['files']) != expected): return None
        blobs = {}
        for name, pin in manifest['files'].items():
            content = battle.version._file(name).read_bytes()
            if (type(pin['bytes']) is not int or len(content) != pin['bytes']
                    or sha256(content).hexdigest() != pin['sha256']): return None
            blobs[name] = content
        data = json.loads(blobs[PACK + '/reference-data.json'])
        materials = json.loads(blobs[PACK + '/source-materials.json'])
        current = battle.packet()
        if current is None or data['schema'] != 'current_hanko_365_v1': return None
        if tuple(data['bindings']) != STAGES or len(data['originals']['levels']) != 5: return None
        stages = current['version']['current']['details']['stages']; inputs = current['inputs']
        if any(not _same(row, stages.get(key)) for key, row in data['originals']['stages'].items()): return None
        for table in ('levels', 'enemy_definitions', 'handbook'):
            if any(not _same(row, inputs[table].get(key)) for key, row in data['originals'][table].items()): return None
        if (set(data['originals']['enemy_definitions']) != set(ACTORS)
                or set(materials['actors']) != {'hanko', 'president', 'smoke'}): return None
        actual = {}
        for sid, stage in stages.items():
            level_key = 'levels/' + stage['levelId'].lower() + '.json'; level = inputs['levels'][level_key]
            found = [{'key': str(i), 'reference_index': i, 'entity_id': row['id'],
                      'level': row['level'], 'actor': ACTORS[row['id']], 'raw_binding': row,
                      'source_selector': '$.enemyDbRefs[' + str(i) + ']'}
                     for i, row in enumerate(level['enemyDbRefs']) if row['id'] in ACTORS]
            if found: actual[sid] = {'level_key': level_key, 'rows': found}
        if not _same(actual, data['bindings']): return None
        return {'data': data, 'materials': materials, 'current': current,
                'source_identity': (MANIFEST_SHA256, current['identity']),
                'actual_present': None, 'actual_skill_time': None, 'actual_smoke_cells': None,
                'actual_status_removed': None, 'current_server_verified': False,
                'numeric_model_added': False, 'run_updated': False}
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError):
        return None


def reference(stage_id, enemy_key=None):
    if type(stage_id) is not str or stage_id not in STAGES: return None
    if enemy_key is not None and type(enemy_key) is not str: return None
    result = packet()
    if result is None: return None
    source = battle.stage_reference(stage_id)
    if (source is None or source['source_identity'] != result['current']['identity']
            or not _same(source['stage'], result['data']['originals']['stages'][stage_id])
            or not _same(source['level'], result['data']['originals']['levels'][source['level_key']])): return None
    rows = []
    for binding in result['data']['bindings'][stage_id]['rows']:
        enemy = next((r for r in source['enemies'] if r['key'] == binding['key']), None)
        if (enemy is None or not _same(enemy['raw_binding'], binding['raw_binding'])
                or enemy['id'] != binding['entity_id'] or type(enemy['level']) is not int
                or enemy['level'] != binding['level']): return None
        row = deepcopy(binding); row['enemy'] = deepcopy(enemy)
        row['has_stage_overwrite'] = binding['raw_binding']['overwrittenData'] is not None
        row['actual_effective_parameters'] = None
        rows.append(row)
    if enemy_key is not None and enemy_key not in {r['key'] for r in rows}: return None
    # Keep the independent smoke reference even when no SPAWN action exists for it.
    return {'stage_id': stage_id, 'stage_name': source['name'], 'rows': rows,
            'selected_key': enemy_key, 'data': result['data'], 'materials': result['materials'],
            'source_identity': result['source_identity'], 'battle_source_identity': source['source_identity'],
            'level_key': source['level_key'], 'source': deepcopy(source['source']),
            'actual_present': None, 'actual_smoke_cells': None, 'actual_status_removed': None,
            'actual_skill_time': None, 'current_server_verified': False,
            'numeric_model_added': False, 'run_updated': False}


def target_available(stage_id, enemy_key):
    return type(enemy_key) is str and reference(stage_id, enemy_key) is not None


def entity(result, enemy_key):
    if result is None or type(enemy_key) is not str: return None
    return next((deepcopy(row) for row in result['rows'] if row['key'] == enemy_key), None)


def topics(result, enemy_key):
    row = entity(result, enemy_key)
    if row is None: return []
    return [(key, TOPICS[key]) for key in result['data']['profiles'][row['actor']]['topics']]


def selected_card(result, enemy_key, topic):
    row = entity(result, enemy_key)
    if row is None or type(topic) is not str or topic not in dict(topics(result, enemy_key)): return None
    index = {'blink': 0, 'flare': 1, 'attack': 2, 'smoke': 0}[topic]
    return deepcopy(result['materials']['actors'][row['actor']]['cards'][index])


def related_entities(result, enemy_key):
    row = entity(result, enemy_key)
    if row is None: return []
    return [{'enemy_key': r['key'], 'name': r['enemy']['name'], 'entity_id': r['entity_id'],
             'level': r['level']} for r in result['rows'] if r['key'] != enemy_key]


def resolve_related(result, enemy_key, request):
    if type(result) is not dict or type(request) is not dict: return None
    fresh = reference(result.get('stage_id'), result.get('selected_key'))
    if fresh is None or not _same(fresh, result): return None
    target = next((r for r in related_entities(fresh, enemy_key) if _same(r, request)), None)
    if target is None: return None
    return {'stage_id': fresh['stage_id'], 'enemy_key': target['enemy_key'],
            'source_identity': deepcopy(fresh['source_identity']), 'actual_present': None,
            'run_updated': False}


def player_text(result, enemy_key=None, topic=None):
    if result is None: return UNAVAILABLE
    row = entity(result, enemy_key)
    lines = ['【' + result['stage_name'] + ' · 汉科与烟雾】', NOTICE,
             '本页仅包含本关的准确引用；没有按相同名字套用其它关卡的面板、招式参数或地图位置。']
    if row is None:
        return '\n'.join(lines + ['', '请先选择本关的首领或独立烟雾弹。烟雾弹是另一实体，不是首领的第二形态。'])
    profile = result['data']['profiles'][row['actor']]
    lines += ['', '【当前查阅】' + row['enemy']['name'],
              '本关记录含专门覆盖配置；通用文献的冷却、持续时间和数值不能直接视为本关实际值。' if row['has_stage_overwrite'] else
              '该引用没有单独覆盖配置；这仍不证明本局的技能实际触发、持续时间或完整修正已核对。']
    if any(r['has_stage_overwrite'] for r in result['rows'] if r['actor'] != 'smoke'):
        lines += ['本关首领还带有专门招式或出场参数。烟雾弹自身没有覆盖，不代表生成过程不会改变它；实际持续时间仍待核对。']
    if row['actor'] == 'smoke':
        lines += ['', '【先看这几点】',
                  '烟雾弹的烟雾会影响我方与敌方，但角色类与敌人类的隐匿条件不同：敌人类还要未被阻挡。',
                  '照明弹暂时关闭的是烟雾弹的“烟雾”天赋，不能据此认定其它来源的隐匿或迷彩也已消失。',
                  '这是独立辅助实体；本关引用不等于实际生成数量，缺少普通出场条目也不表示不会生成。']
    else:
        lines += ['', '【先看这几点】',
                  '被阻挡时才可触发闪现；文献说明目的地还要可通行，不保证每次都能越过阻挡。',
                  '照明弹需要范围内存在我方单位才可触发；冷却就绪不等于立即发射。',
                  '普通攻击在被阻挡和未被阻挡时不同，不能把二连击与近战伤害合成一套攻击。',
                  '', '【图鉴原文与社区修正】']
        lines += row['enemy']['abilities'] or ['当前精确引用没有独立图鉴能力。']
        corrected = next((d['visible_text'] for d in result['materials']['actors'][row['actor']]['descriptions_original_and_corrected']
                          if '不会' in d['visible_text']), None)
        if corrected:
            lines += ['', '社区修正版：', corrected,
                      '社区认为游戏内的反隐表述与实际表现不符：照明弹不会清除其中所有隐匿、迷彩。原文与修正均保留，当前服务器执行没有在本页验证。']
    if topic is not None:
        card = selected_card(result, enemy_key, topic)
        if card is None: return '\n'.join(lines + ['', '所选招式不属于这份准确实体，旧招式内容不显示。'])
        lines += ['', '【完整文献参考 · ' + card['title'] + '】',
                  '以下为通用文献原项，不是本局预测数值；本关覆盖与实际执行仍需单独核对。']
        if 'initial_cooldown_documented' in card:
            lines += ['文献初始冷却：' + str(card['initial_cooldown_documented']) + '秒；后续冷却：' + str(card['cooldown_documented']) + '秒。',
                      '冷却表示准备时间，另有触发条件；不是开场绝对时刻或技能总周期。']
        lines.append(card['body'])
    lines += ['', '【适用边界】',
              '普通汉科、大总统和每份关卡覆盖分别保存。不会用未赋值的备用名称或外观字段替换真实身份。',
              '烟雾出现格、实际覆盖、闪现落脚点、弹道命中与首击时钟未知，不在地图上猜位置，不改预计面板。',
              '文献采用固定修订' + str(profile['source_revision']) + '，与当前固定国服原件分开标明；不操作游戏、不改本局记忆。']
    return '\n'.join(lines)
