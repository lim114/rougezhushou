"""Nine exact current enemy references to four existing guarded document readers.

This is a qualified documentary migration, not a new numeric/phase model. The
legacy readers retain their genuine old identities and complete source guards.
"""
from copy import deepcopy
from hashlib import sha256
import json
from . import current_battle_reference as battle

PACK = 'research/p3-current-boss-documents-369'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '519c8238a1ecacfba4d20014af31616a6320e6056e3c68deefdb43fd1b442bda'
TARGETS = (
    ('ro6_b_6', '0', 'enemy_2150_shchmr', 0, 'phase'),
    ('ro6_b_5', '0', 'enemy_2147_shophm', 0, 'cycle'),
    ('ro6_b_5', '1', 'enemy_2148_shorbb', 0, 'cycle'),
    ('ro6_b_4', '0', 'enemy_2145_cadejo', 0, 'hunt'),
    ('ro6_b_4', '1', 'enemy_2146_cadesd', 0, 'hunt'),
    ('ro6_b_4', '2', 'enemy_2137_shsdgo', 0, 'hunt'),
    ('ro6_b_2', '1', 'enemy_2140_shsgzd', 0, 'gold'),
    ('ro6_b_2', '2', 'enemy_2142_shsggd', 0, 'gold'),
    ('ro6_b_2_b', '0', 'enemy_2141_shsgz2', 0, 'gold'),
)
STAGES = tuple(dict.fromkeys(t[0] for t in TARGETS))
LABELS = {'phase': '形态、招式与转换条件', 'cycle': '交替激活、模块与退场条件',
          'hunt': '围猎、休整与后续来敌条件', 'gold': '起飞、劫掠与退场条件'}
SOURCE_FILES = {
    'phase': ('research/p3-boss-phase-309/selected-original-records.json', 'research/p3-boss-phase-309/source-manifest.json'),
    'cycle': ('research/p3-boss-cycle-310/selected-original-records.json', 'research/p3-boss-cycle-310/source-manifest.json'),
    'hunt': ('research/p3-boss-hunt-311/selected-original-records.json', 'research/p3-boss-hunt-311/source-manifest.json'),
    'gold': ('research/p3-gold-boss-312/selected-original-authority.json', 'research/p3-gold-boss-312/source-manifest.json'),
}
NOTICE = ('查看这关敌人的形态、招式、特殊循环与退场条件。'
          '文献中的时长和比例供查阅；不表示本局状态、实际倒计时或已经算出的面板。')
UNAVAILABLE = '当前敌人的完整机制资料无法核对，旧选择、说明、图片与入口已清除；资料恢复后请手动重新选择。'


def _same(a, b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if type(a) in (tuple, list): return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def _legacy(family):
    if family == 'phase':
        from . import boss_phase_reference as module
        return module.phase_reference, module.reference_text
    if family == 'cycle':
        from . import boss_cycle_reference as module
        return module.cycle_reference, module.reference_text
    if family == 'hunt':
        from . import boss_hunt_reference as module
        return module.hunt_reference, module.reference_text
    if family == 'gold':
        from . import gold_boss_reference as module
        return module.gold_reference, module.reference_text
    raise ValueError('Unsupported documentary family')


def packet():
    try:
        raw = battle.version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {PACK + '/' + n for n in ('qualified-current-records.json', 'source-notes.json', 'web-check-record.json')}
        expected.update(n for pair in SOURCE_FILES.values() for n in pair)
        if (manifest['schema'] != 'current_boss_documents_369_manifest_v1'
                or manifest['game_commit'] != battle.version.NEW_COMMIT
                or set(manifest['files']) != expected): return None
        blobs = {}
        for name, pin in manifest['files'].items():
            content = battle.version._file(name).read_bytes()
            if (type(pin['bytes']) is not int or len(content) != pin['bytes']
                    or sha256(content).hexdigest() != pin['sha256']): return None
            blobs[name] = content
        data = json.loads(blobs[PACK + '/qualified-current-records.json'])
        current = battle.packet()
        if (current is None or data['schema'] != 'current_boss_documents_369_v1'
                or data['current_commit'] != battle.version.NEW_COMMIT
                or set(data['families']) != set(LABELS)): return None
        declared = tuple((r['stage_id'], r['enemy_key'], r['enemy_id'], r['level'], r['family']) for r in data['targets'])
        if not _same(declared, TARGETS): return None
        stages = current['version']['current']['details']['stages']; inputs = current['inputs']
        if any(not _same(v, stages.get(k)) for k, v in data['originals']['stages'].items()): return None
        for table in ('levels', 'enemy_definitions', 'handbook'):
            if any(not _same(v, inputs[table].get(k)) for k, v in data['originals'][table].items()): return None
        for family, spec in data['families'].items():
            for row in spec['level_qualification']:
                old = data['old_levels'][row['stage_id']]; new = inputs['levels'][row['level_key']]
                changed = sorted(k for k in set(old) | set(new) if not _same(old.get(k), new.get(k)))
                permitted = ['runes'] if row['stage_id'] == 'ro6_b_2_b' else []
                if changed != permitted or row['changed_top_fields'] != permitted: return None
                if permitted and (new['runes'] is not None or not _same(
                        row['differences'], [{'field': 'runes', 'previous': old['runes'], 'current': None}])): return None
                if row['whole_level_equal'] is not (not permitted): return None
        for target in data['targets']:
            sid = target['stage_id']; key = 'levels/' + stages[sid]['levelId'].lower() + '.json'
            binding = inputs['levels'][key]['enemyDbRefs'][int(target['enemy_key'])]
            if (not _same(binding, target['raw_binding']) or binding['id'] != target['enemy_id']
                    or type(binding['level']) is not int or binding['level'] != target['level']
                    or not _same(target['legacy_identity'], [sid, binding['id'], binding['level']])): return None
        return {'data': data, 'current': current,
                'source_identity': (MANIFEST_SHA256, current['identity']),
                'actual_phase': None, 'actual_skill_time': None, 'expected_stats': None,
                'actual_server_verified': False, 'numeric_model_added': False, 'run_updated': False}
    except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError, UnicodeError, RecursionError):
        return None


def reference(stage_id, enemy_key=None):
    if type(stage_id) is not str or stage_id not in STAGES: return None
    if enemy_key is not None and (type(enemy_key) is not str
            or (stage_id, enemy_key) not in {(t[0], t[1]) for t in TARGETS}): return None
    result = packet()
    if result is None: return None
    stage = battle.stage_reference(stage_id)
    if (stage is None or stage['source_identity'] != result['current']['identity']
            or not _same(stage['stage'], result['data']['originals']['stages'][stage_id])
            or not _same(stage['level'], result['data']['originals']['levels'][stage['level_key']])): return None
    targets = [r for r in result['data']['targets'] if r['stage_id'] == stage_id]
    rows = []
    for target in targets:
        enemy = next((e for e in stage['enemies'] if e['key'] == target['enemy_key']), None)
        if (enemy is None or not _same(enemy['raw_binding'], target['raw_binding'])
                or enemy['id'] != target['enemy_id'] or type(enemy['level']) is not int
                or enemy['level'] != target['level']): return None
        reader, _ = _legacy(target['family'])
        old = reader(*target['legacy_identity'])
        if (type(old) is not dict or old.get('source_valid') is not True
                or old.get('stage_id') != target['stage_id'] or old.get('enemy_id') != target['enemy_id']
                or type(old.get('level')) is not int or old['level'] != target['level']
                or type(old.get('reference')) is not dict): return None
        rows.append({**deepcopy(target), 'enemy': deepcopy(enemy), 'legacy_document': old,
                     'actual_phase': None, 'expected_stats': None})
    family = targets[0]['family']; spec = result['data']['families'][family]
    related = [deepcopy(e) for e in stage['enemies'] if e['id'] in spec['related_ids']]
    qualification = next(r for r in spec['level_qualification'] if r['stage_id'] == stage_id)
    return {'stage_id': stage_id, 'stage_name': stage['name'], 'selected_key': enemy_key,
            'family': family, 'rows': rows, 'related': related, 'qualification': deepcopy(qualification),
            'documents': deepcopy(spec['document_sources']),
            'source_identity': (*result['source_identity'], tuple((r['enemy_key'],
                r['legacy_document']['source_identity']['manifest_sha256'],
                r['legacy_document']['source_identity']['data_sha256']) for r in rows)),
            'battle_source_identity': stage['source_identity'], 'level_key': stage['level_key'],
            'source': deepcopy(stage['source']), 'complete_current_level': deepcopy(stage['level']),
            'actual_phase': None, 'actual_skill_time': None, 'expected_stats': None,
            'actual_server_verified': False, 'numeric_model_added': False, 'run_updated': False}


def target_available(stage_id, enemy_key):
    return type(enemy_key) is str and reference(stage_id, enemy_key) is not None


def entity(result, enemy_key):
    if type(result) is not dict or type(enemy_key) is not str: return None
    return next((deepcopy(row) for row in result['rows'] if row['enemy_key'] == enemy_key), None)


def topics(result, enemy_key):
    row = entity(result, enemy_key)
    if row is None: return []
    doc = row['legacy_document']['reference']
    return [{'id': r['id'], 'name': r['name']} for r in doc['phases' if row['family'] == 'phase' else 'topics']]


def _fresh(result):
    if type(result) is not dict: return None
    fresh = reference(result.get('stage_id'), result.get('selected_key'))
    return fresh if fresh is not None and _same(fresh, result) else None


def related_entities(result, enemy_key):
    if entity(result, enemy_key) is None: return []
    return [{'key': e['key'], 'entity_id': e['id'], 'level': e['level'], 'name': e['name']}
            for e in result['related'] if e['key'] != enemy_key]


def resolve_entity(result, enemy_key, request):
    fresh = _fresh(result)
    if fresh is None or type(request) is not dict: return None
    match = next((r for r in related_entities(fresh, enemy_key) if _same(r, request)), None)
    if match is None: return None
    return {'stage_id': fresh['stage_id'], 'enemy_key': match['key'],
            'source_identity': deepcopy(fresh['source_identity']), 'run_updated': False}


def map_reference(result):
    fresh = _fresh(result)
    if fresh is None: return None
    from . import current_map_position as maps
    mapped = maps.stage_reference(fresh['stage_id'])
    if (type(mapped) is not dict or mapped.get('stage_id') != fresh['stage_id']
            or mapped.get('current_level_key') != fresh['level_key']
            or not _same((mapped.get('complete_current_geometry') or {}).get('mapData'),
                         fresh['complete_current_level']['mapData'])): return None
    return {'stage_id': fresh['stage_id'], 'map_source_identity': deepcopy(mapped['source_identity']),
            'map': mapped, 'actual_phase': None, 'actual_entity_position': None, 'run_updated': False}


def player_text(result, enemy_key=None, topic_id=None):
    fresh = _fresh(result)
    if fresh is None: return UNAVAILABLE
    if topic_id is not None and type(topic_id) is not str: return UNAVAILABLE
    row = entity(fresh, enemy_key)
    lines = ['【' + fresh['stage_name'] + ' · 完整机制文献】', NOTICE,
             '当前固定资料：国服2026年10月16日。关卡、准确敌人条目与文献来源分别核对，不按同名推及其他关卡。']
    if fresh['stage_id'] == 'ro6_b_2_b':
        lines += ['', '【这关的版本差异必须先看】',
                  '旧固定关卡列过两项特殊条件修正，当前固定资料的对应整栏未填写。其余完整关卡内容与此敌人的原始资料相同。',
                  '这里仅保留敌人文献中的起飞、降落、劫掠及退场说明，不沿用旧关卡的修正、旧面板或据此判断当前奖励。',
                  '整栏差异不证明服务器现在完全没有修正；具体原值仅在来源页并列，不参与本页或预计面板计算。']
    else:
        lines += ['已核对这关的完整原始资料和相关敌人原项，与文献原来对应的固定资料相同；仍不能据此保证服务器没有另行调整。']
    if row is None:
        return '\n'.join(lines + ['', '请选择本关有完整文献的准确敌人条目；选择只是阅读，不表示实际出现或处于该形态。',
            *['• ' + r['enemy']['name'] + '：' + LABELS[r['family']] for r in fresh['rows']]])
    if topic_id is not None and topic_id not in {r['id'] for r in topics(fresh, enemy_key)}:
        return '所选机制分支无法核对，请手动重新选择。'
    _, renderer = _legacy(row['family'])
    # Render only the authentic guarded legacy object, never a rewritten current
    # tuple or a legacy battle panel that could carry historical rune calculations.
    body = renderer(row['legacy_document'], topic_id)
    lines += ['', '【正在查阅】' + row['enemy']['name'] + ' · ' + LABELS[row['family']],
              '以下保留完整条件、限定形态、相关招式与来源冲突。文献值不是当前预计结果，也没有产生实际时间轴。', '', body,
              '', '【当前入口的边界】',
              '生命、攻击、防御等预计面板、实际阶段、技能发动时刻和服务器执行情况：未知。',
              '相关条目只跳到本关明确列出的对应敌人；固定地图只展示这关原图，不标记首领的实际脚点或动态位移。',
              '其他同名关卡、追猎变化或同名敌人若未列出对应入口，不能直接套用这份说明。']
    return '\n'.join(lines)
