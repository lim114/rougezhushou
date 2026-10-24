"""Current exact Sun-boss form references, without battle-state prediction."""
from copy import deepcopy
from hashlib import sha256
import json
import re
from . import current_battle_reference as battle

PACK = 'research/p3-current-sun-boss-368'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '4ea4999cd58af402e689acd9ccd5fd2c6b08f05367fdb14256e3a65b85dfec10'
STAGES = ('ro6_b_7', 'ro6_b_7_b')
FORMS = {'enemy_2157_shadvr': 'normal', 'enemy_2157_shadvr_1': 'sun', 'enemy_2157_shadvr_2': 'eclipse'}
TOPICS = (('overview', '先看形态与两个阶段'), ('faith', '信仰、转变与异常状态'),
          ('skills', '本形态的完整招式说明'), ('terrain', '二阶段与固定地形'), ('altar', '陨石与祭台'))
NOTICE = ('这是同一首领的三种形态资料，不是三名同时出场的敌人。'
          '只读这份固定关卡与完整文献，不认定本局形态、信仰进度、地形变化或技能实际发动时刻。')
UNAVAILABLE = '熄日首领资料无法核对，旧形态、招式、图片和地形入口已清除；恢复后请重新选择。'


def _same(a, b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if type(a) in (tuple, list): return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def packet():
    try:
        raw = battle.version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {PACK + '/' + name for name in ('reference-data.json', 'source-materials.json',
            'source-notes.json', 'related-id-absence-proof.json', 'sun-boss-complete.html',
            'altar-complete.html', 'http-source-record.json', 'altar-source-record.json')}
        if (manifest['schema'] != 'current_sun_boss_368_manifest_v1'
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
        if current is None or data['schema'] != 'current_sun_boss_368_v1': return None
        if tuple(data['bindings']) != STAGES or set(data['originals']['enemy_definitions']) != set(FORMS): return None
        stages = current['version']['current']['details']['stages']; inputs = current['inputs']
        if any(not _same(row, stages.get(key)) for key, row in data['originals']['stages'].items()): return None
        for table in ('levels', 'enemy_definitions', 'handbook'):
            if any(not _same(row, inputs[table].get(key)) for key, row in data['originals'][table].items()): return None
        if set(materials['forms']) != set(FORMS.values()): return None
        for sid in STAGES:
            selected = data['bindings'][sid]; level = inputs['levels'][selected['level_key']]
            refs = [{'key': str(i), 'reference_index': i, 'entity_id': row['id'], 'level': row['level'],
                     'form': FORMS[row['id']], 'raw_binding': row,
                     'source_selector': '$.enemyDbRefs[' + str(i) + ']'}
                    for i, row in enumerate(level['enemyDbRefs']) if row['id'] in FORMS]
            if not _same(refs, selected['rows']) or len(refs) != 3: return None
        return {'data': data, 'materials': materials, 'current': current,
                'source_identity': (MANIFEST_SHA256, current['identity']),
                'actual_form': None, 'actual_phase': None, 'actual_faith': None,
                'actual_skill_time': None, 'actual_terrain': None, 'actual_altar_cells': None,
                'current_server_verified': False, 'numeric_model_added': False, 'run_updated': False}
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError):
        return None


def reference(stage_id, enemy_key=None):
    if type(stage_id) is not str or stage_id not in STAGES: return None
    if enemy_key is not None and type(enemy_key) is not str: return None
    result = packet()
    if result is None: return None
    stage = battle.stage_reference(stage_id)
    if (stage is None or stage['source_identity'] != result['current']['identity']
            or not _same(stage['stage'], result['data']['originals']['stages'][stage_id])
            or not _same(stage['level'], result['data']['originals']['levels'][stage['level_key']])): return None
    rows = []
    for binding in result['data']['bindings'][stage_id]['rows']:
        enemy = next((r for r in stage['enemies'] if r['key'] == binding['key']), None)
        if (enemy is None or not _same(enemy['raw_binding'], binding['raw_binding'])
                or enemy['id'] != binding['entity_id'] or type(enemy['level']) is not int
                or enemy['level'] != binding['level']): return None
        rows.append({**deepcopy(binding), 'enemy': deepcopy(enemy), 'actual_form_active': None})
    if enemy_key is not None and enemy_key not in {r['key'] for r in rows}: return None
    appearances = [deepcopy(action) for action in stage['actions']
                   if action['raw'].get('actionType') == 'SPAWN' and action['raw'].get('key') in FORMS]
    return {'stage_id': stage_id, 'stage_name': stage['name'], 'selected_key': enemy_key,
            'rows': rows, 'data': result['data'], 'materials': result['materials'],
            'source_identity': result['source_identity'], 'battle_source_identity': stage['source_identity'],
            'level_key': stage['level_key'], 'source': deepcopy(stage['source']),
            'declared_appearances': appearances,
            'actual_form': None, 'actual_phase': None, 'actual_faith': None,
            'actual_skill_time': None, 'actual_terrain': None, 'actual_altar_cells': None,
            'current_server_verified': False, 'numeric_model_added': False, 'run_updated': False}


def target_available(stage_id, enemy_key):
    return type(enemy_key) is str and reference(stage_id, enemy_key) is not None


def entity(result, enemy_key):
    if result is None or type(enemy_key) is not str: return None
    return next((deepcopy(row) for row in result['rows'] if row['key'] == enemy_key), None)


def cards(result, enemy_key):
    row = entity(result, enemy_key)
    if row is None: return []
    return deepcopy(result['materials']['forms'][row['form']]['cards'])


def card(result, enemy_key, index):
    if type(index) is not int: return None
    return next((r for r in cards(result, enemy_key) if r['index'] == index), None)


def related_forms(result, enemy_key):
    if entity(result, enemy_key) is None: return []
    return [{'key': row['key'], 'entity_id': row['entity_id'], 'level': row['level'],
             'name': row['enemy']['name']} for row in result['rows'] if row['key'] != enemy_key]


def resolve_form(result, enemy_key, request):
    if type(result) is not dict or type(request) is not dict: return None
    fresh = reference(result.get('stage_id'), result.get('selected_key'))
    if fresh is None or not _same(fresh, result): return None
    match = next((r for r in related_forms(fresh, enemy_key) if _same(r, request)), None)
    if match is None: return None
    return {'stage_id': fresh['stage_id'], 'enemy_key': match['key'],
            'source_identity': deepcopy(fresh['source_identity']), 'actual_form': None, 'run_updated': False}


def map_reference(result):
    if type(result) is not dict: return None
    fresh = reference(result.get('stage_id'), result.get('selected_key'))
    if fresh is None or not _same(fresh, result): return None
    from . import current_map_position as maps
    mapped = maps.stage_reference(fresh['stage_id'])
    original = fresh['data']['originals']['levels'][fresh['level_key']]
    if (type(mapped) is not dict or mapped.get('stage_id') != fresh['stage_id']
            or mapped.get('current_level_key') != fresh['level_key']
            or not _same((mapped.get('complete_current_geometry') or {}).get('mapData'), original['mapData'])): return None
    return {'stage_id': fresh['stage_id'], 'source_identity': deepcopy(fresh['source_identity']),
            'map_source_identity': deepcopy(mapped['source_identity']), 'map': mapped,
            'actual_second_phase_terrain': None, 'actual_altar_cells': None, 'run_updated': False}


def _player(value):
    value = re.sub(r'(\d+(?:\.\d+)?)s\b', r'\1秒', value)
    return value.replace('物理普通伤害', '物理伤害').replace('法术普通伤害', '法术伤害').replace('Buff', '效果')


def player_text(result, enemy_key=None, topic='overview', card_index=None):
    if result is None: return UNAVAILABLE
    if type(topic) is not str or topic not in dict(TOPICS): return UNAVAILABLE
    row = entity(result, enemy_key)
    lines = ['【' + result['stage_name'] + ' · 沉沦之人】', NOTICE,
             '“形态”与“阶段”是两回事：形态有沉沦之人、日照与日蚀三种；击倒后重生才进入第二阶段。',
             '这两份同名熄日配置独立保存，不按名称、图像或编号互借参数。']
    if row is None:
        return '\n'.join(lines + ['', '请手动选择一份准确形态资料。选择只是查阅，不表示本局已转成它。'])
    form = result['materials']['forms'][row['form']]
    talent = next(c for c in form['cards'] if c['kind'] == 'talent')
    lines += ['', '【当前查阅的形态资料】' + row['enemy']['name'],
              '本关没有单独改写这份敌人资料；本页未把形态、关卡特殊条件和当前保密等级的修正折算成预计面板。']
    if topic == 'overview':
        lines += ['', '【怎样变化】',
                  '起始为沉沦之人。日照信仰满溢转为艾穆拉伊；日蚀信仰满溢转为托斯卡特尔。',
                  '第一阶段中，同一种信仰在对应形态再次满溢，会进入该形态的强化状态；文献分别记载其持续40秒及之后的信仰消逝。',
                  '第二阶段则停止积累信仰并始终保持强化形态，不能把第一阶段的40秒结束规则直接套到第二阶段。',
                  '两种信仰同时满溢时，文献说明优先转为托斯卡特尔；不能把它当成两种形态同时生效。',
                  '第一阶段与第二阶段的转换、招式和地形说明分开查阅，不据当前选择推实际状态。',
                  '', '【游戏图鉴原文】', *row['enemy']['abilities'],
                  '', '【容易看错】',
                  '文献明确：另两份非常规档案用于显示形态图鉴，实战不是额外出现两名首领。',
                  '本关出场声明也只写沉沦之人本体；声明数量不是实际出现或总敌人数的证明。']
    elif topic == 'faith':
        lines += ['', '【文献中的信仰、状态与阶段】',
                  '受到特定异常后，它会对相同异常逐步产生更强抵抗；每种异常分开记录，重复附加会刷新相应记录。',
                  '以下为固定文献的完整天赋与能力卡。增益数值是机制说明，不是已算出的本局面板。',
                  _player(talent['body']),
                  '', '【仍须区分】',
                  '文献要求伤害成功造成生命实际降低才增加对应受击信仰；不能按命中次数或弹道数量直接累计。',
                  '六种异常分别叠层与刷新，不能把某一种叠满推广为所有异常免疫；原数据库初始字段也不能代替动态状态。']
    elif topic == 'skills':
        selected = card(result, enemy_key, card_index)
        if selected is None:
            lines += ['', '请从本形态原项中选择一条招式或天赋；同名招式在不同形态仍保留为独立原项。']
        else:
            lines += ['', '【完整文献原项 · ' + selected['title'] + '】',
                      '下面保留该形态自身的触发条件与效果；不是本局预测数值或开场绝对时刻。',
                      _player(selected['body'])]
            if any('/' in cost and cost != '/' for cost in selected['cost_header_raw']):
                lines += ['文献的时间栏合并了不同模式的数值；原栏完整保留在来源页，本页不猜对应关系或据此推连续时间轴。']
            if row['form'] == 'eclipse' and selected['title'] == '熄日的祭坛':
                lines += ['命名差别：当前游戏图鉴写“熄日的祭仪”，这份文献标题写“熄日的祭坛”。两原文分别保留，不擅自改名或按名称建立技能脚本对应。']
    elif topic == 'terrain':
        phase = talent['body'].split('二阶段', 1)
        lines += ['', '【第二阶段】', _player(phase[1]) if len(phase) == 2 else '这份原文未明确列出二阶段段落。',
                  '', '【怎样看地图】',
                  '下方入口只打开这份准确关卡的固定原图与格图。它没有模拟首领位置、下个检查点或祭台位置。',
                  '文献说隐藏带指定标记的地块，同时保留所述路段与祭台所在格；这些条件依赖当时状态，固定地图不能给出唯一剩余地形。',
                  '原表的标记参数在来源页保留，不按英文参数名认定哪些格必然消失，不把地块列表替换为第二阶段结果。']
    elif topic == 'altar':
        meteor = next(c for c in form['cards'] if c['title'] == '陨石召唤')
        lines += ['', '【陨石与祭台 · 首领文献原项】', _player(meteor['body']),
                  '', '【祭台独立文献】',
                  '祭台装置页的技能说明为“会被沉沦之人攻击”，并记载不能手动撤退；该页标为机制尚待补充。',
                  '首领文献与祭台装置页分别保存。当前固定关卡没有祭台预置原项，不能生成固定祭台编号、位置或预计面板。',
                  '完整祭台机制、动态生成/替换与实际所在格仍未核验；固定地形入口不会画出虚构祭台。']
    lines += ['', '【来源与未知】',
              '首领文献修订442955、祭台文献修订442887，均与国服10月16日固定原件分别保存；首领文献仍标注编辑中。',
              '本局信仰、形态、阶段、实际召唤与时钟、祭台及变化后地形均未知。本页不提供白值替代预测，不改计算或本局记忆。']
    return '\n'.join(lines)
