"""Current cross-exploration references and separate failure/start declarations."""
from copy import deepcopy
from hashlib import sha256
import json
from . import expansion_reference as version

PACK = 'research/p3-current-legacy-361'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '19e7c9e531cdb4276a74f711aa1da9ab17b52c2e7b6a4defc06bad54703e2515'
HIDDEN = 'rogue_6_legacy_10'
TARGET = 'rogue_6_relic_fight_29'
NOTICE = ('这些助力留待下次探索，不给本局添加资源或增益。失败局与下次开始的条件分开核对；'
          '本页声明不证明已继承、已领取或服务器实际资格。')
UNAVAILABLE = '跨局助力资料无法核对，旧条目、条件结果与资料入口已清除；恢复后请重新选择。'
GROUPS = (('all', '总览'), ('cat', '襁褓中的猫'), ('dog', '襁褓中的狗'),
          ('cerberus', '襁褓三头犬'), ('feather', '襁褓羽蛇'), ('hidden', '开局助力'))


def _same(a, b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if type(a) in (tuple, list): return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def packet():
    try:
        raw = version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {PACK + '/' + name for name in ('reference-data.json', 'source-notes.json',
                    'relic-film-page.html', 'download-receipt.json', 'film-acquisition-excerpt.txt')}
        if (manifest['schema'] != 'current_legacy_361_manifest_v1'
                or manifest['game_commit'] != version.NEW_COMMIT
                or set(manifest['files']) != expected): return None
        blobs = {}
        for name, pin in manifest['files'].items():
            content = version._file(name).read_bytes()
            if (type(pin['bytes']) is not int or len(content) != pin['bytes']
                    or sha256(content).hexdigest() != pin['sha256']): return None
            blobs[name] = content
        data = json.loads(blobs[PACK + '/reference-data.json'])
        current = version.packet()
        if current is None or data['schema'] != 'current_legacy_361_reference_v1': return None
        d = current['current']['details']; old = current['baseline']['details']
        if len(data['rows']) != 14 or not _same(data['originals']['legacyItems'], d['legacyItems']): return None
        for table in ('items', 'relics', 'choices', 'choiceScenes'):
            if any(not _same(row, d[table].get(key)) for key, row in data['originals'][table].items()): return None
        if not _same(data['originals']['difficulties'], d['difficulties']): return None
        if set(data['rows']) != set(d['legacyItems']): return None
        for key, row in data['rows'].items():
            if not all(_same(row[field], d[table].get(key)) for field, table in
                       (('original_legacy', 'legacyItems'), ('item', 'items'), ('relic', 'relics'))): return None
            unchanged = all(_same(old[table].get(key), d[table][key])
                            for table in ('legacyItems', 'items', 'relics'))
            if row['source_unchanged_from_previous_fixed_snapshot'] is not unchanged: return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, current['source_identity']),
                'actual_held': None, 'actual_inherited': None, 'actual_claim_consumed': None,
                'actual_next_received': None, 'current_server_verified': False,
                'run_updated': False, 'next_run_created': False, 'calculation_applied': False}
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError):
        return None


def reference():
    return packet()


def rows(result, group='all'):
    if result is None or type(group) is not str or group not in dict(GROUPS): return []
    return [deepcopy(row) for row in result['data']['rows'].values()
            if group == 'all' or row['group'] == group]


def _status(checks):
    values = [check['matches'] for check in checks]
    return False if any(value is False for value in values) else None if None in values else True


def compare_failure_support(result, *, origin_mode=None, origin_grade=None, origin_failed=None,
                            next_mode=None, next_grade=None, next_started=None,
                            prior_claim_consumed=None):
    """Compare cited conditions; never turn a declaration into an account claim."""
    if result is None: return None
    if origin_mode not in (None, 'NORMAL', 'OTHER') or next_mode not in (None, 'NORMAL', 'OTHER'): return None
    valid_grades = {r['grade'] for r in result['data']['originals']['difficulties']
                    if r['modeDifficulty'] == 'NORMAL'}
    if any(value is not None and (type(value) is not int or value not in valid_grades)
           for value in (origin_grade, next_grade)): return None
    if any(value is not None and type(value) is not bool
           for value in (origin_failed, next_started, prior_claim_consumed)): return None
    if origin_mode == 'OTHER' and origin_grade is not None: return None
    if next_mode == 'OTHER' and next_grade is not None: return None
    doc = result['data']['failure_support_documentation']
    origin = [
        {'label': '产生助力的那局是常规行动', 'matches': None if origin_mode is None else origin_mode == 'NORMAL'},
        {'label': '那局保密等级为0、1、2或3',
         'matches': None if origin_grade is None else origin_grade in doc['documented_origin_grades']},
        {'label': '那局确实探索失败', 'matches': origin_failed}]
    receipt = [
        {'label': '下次开始的是常规行动', 'matches': None if next_mode is None else next_mode == 'NORMAL'},
        {'label': '下次保密等级仍为0、1、2或3',
         'matches': None if next_grade is None else next_grade in doc['documented_next_grades']},
        {'label': '没有声明这次收取判定已经被消耗',
         'matches': None if prior_claim_consumed is None else not prior_claim_consumed}]
    warning = ('文献特别提醒：产生助力与下次收取都要在0～3级；在其它难度开始时不会收到影像，'
               '仍会消耗这次收取判定。不要把它当成可以无限留到以后领取。')
    status = 'conditions_incomplete'
    if origin_failed is False:
        status = 'failure_not_declared'
    elif _status(origin) is False:
        status = 'origin_conditions_do_not_match'
    elif prior_claim_consumed is True:
        status = 'claim_already_declared_consumed'
    elif next_started is True and next_mode == 'NORMAL' and next_grade is not None and next_grade not in (0, 1, 2, 3):
        status = 'documented_check_consumption_risk'
    elif _status(origin) is True and _status(receipt) is True:
        status = 'listed_conditions_match_only'
    return {'declared': {'origin_mode': origin_mode, 'origin_grade': origin_grade,
            'origin_failed': origin_failed, 'next_mode': next_mode, 'next_grade': next_grade,
            'next_started': next_started, 'prior_claim_consumed': prior_claim_consumed},
            'origin_checks': origin, 'receipt_checks': receipt,
            'listed_origin_match': _status(origin), 'listed_receipt_match': _status(receipt),
            'status': status, 'warning': warning, 'actual_server_eligible': None,
            'actual_claim_exists': None, 'actual_claim_consumed': None,
            'actual_received': None, 'run_updated': False, 'next_run_created': False}


def locate(category, key):
    if type(category) is not str or type(key) is not str: return None
    result = packet()
    if result is None: return None
    data = result['data']; selected = None
    if category in ('items', 'relics'):
        if key in data['rows']: selected = key
        elif key == TARGET: selected = HIDDEN
        elif key == data['seed_item_id']:
            return {'group': 'all', 'legacy_id': None, 'source_request': {'category': category, 'key': key}}
        else:
            matches = [row['id'] for row in data['rows'].values()
                       if row['startup_pointer'] and row['startup_pointer']['reward_item_id'] == key]
            if len(matches) == 1: selected = matches[0]
    elif category == 'choices':
        matches = [row['id'] for row in data['rows'].values()
                   if row['startup_pointer'] and row['startup_pointer']['choice_id'] == key]
        if len(matches) == 1: selected = matches[0]
    elif category == 'difficulty':
        matches = [r for r in data['originals']['difficulties']
                   if key == str(r['modeDifficulty']) + '|' + str(r['grade'])]
        if len(matches) == 1 and matches[0]['modeDifficulty'] == 'NORMAL': selected = HIDDEN
    elif category == 'scenes' and key == 'scene_ro6_startbuff_enter':
        return {'group': 'feather', 'legacy_id': None, 'source_request': {'category': category, 'key': key}}
    if selected is None: return None
    return {'group': data['rows'][selected]['group'], 'legacy_id': selected,
            'source_request': {'category': category, 'key': key}}


def links(result, legacy_id):
    if result is None or type(legacy_id) is not str: return []
    row = result['data']['rows'].get(legacy_id)
    if row is None: return []
    output = [{'kind': 'item', 'key': legacy_id, 'label': '查看这份准确跨局物品原说明'}]
    if row['seed_source_reference']:
        output.append({'kind': 'seed', 'key': legacy_id, 'label': '查看已有种子培育来源与资格边界'})
    if row['startup_pointer']:
        pointer = row['startup_pointer']
        output.append({'kind': 'startup', 'key': pointer['choice_id'],
                       'label': '查看对应下次支援：' + pointer['title']})
    if legacy_id == HIDDEN:
        output.append({'kind': 'item', 'key': TARGET, 'label': '查看特勤任务影像的准确收藏品原说明'})
        for grade in (0, 1, 2, 3, 4):
            output.append({'kind': 'difficulty', 'key': 'NORMAL|' + str(grade),
                           'label': '查看保密等级' + str(grade) + '的原条件说明'})
    return output


def resolve_link(result, request, *, legacy_id):
    if type(result) is not dict or type(request) is not dict: return None
    fresh = packet()
    if fresh is None or not _same(fresh, result): return None
    request = next((row for row in links(fresh, legacy_id) if _same(row, request)), None)
    if request is None: return None
    data = fresh['data']; row = data['rows'][legacy_id]; kind = request['kind']; key = request['key']
    try:
        if kind == 'seed':
            from . import seed_cultivation_planning as seed
            source = seed.seed_cultivation_reference()
            found = next((r for r in source['rows'] if r['item_id'] == key), None)
            if (found is None or not _same(found['item'], row['item'])
                    or found['legacy_group_id'] != row['legacy_group_id']
                    or not any(_same(found['original_buff'], b) for b in row['relic']['buffs'])
                    or found['documented_source_id'] is not row['seed_source_reference']['documented_source_id']): return None
            target = {'item_id': key}; original = deepcopy(row['seed_source_reference'])
        elif kind == 'startup':
            from . import current_startup as startup
            source = startup.packet(); target = startup.locate('choices', key)
            found = source['data']['choices'].get(key) if source else None
            if (target is None or found is None or found['legacy_id'] != legacy_id
                    or not _same(found['original'], data['originals']['choices'][key])): return None
            original = deepcopy(found)
        elif kind == 'item':
            target = {'category': 'relics', 'key': key}
            original = {'item': deepcopy(data['originals']['items'][key]),
                        'relic': deepcopy(data['originals']['relics'][key])}
        elif kind == 'difficulty':
            target = {'category': 'difficulty', 'key': key}
            original = deepcopy(next(r for r in data['originals']['difficulties']
                                     if key == str(r['modeDifficulty']) + '|' + str(r['grade'])))
        else: return None
        return {'request': deepcopy(request), 'target': target, 'original': original,
                'source_identity': deepcopy(fresh['source_identity']),
                'actual_received': None, 'run_updated': False, 'next_run_created': False}
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, StopIteration):
        return None


def player_text(result, legacy_id=None, condition=None):
    if result is None or type(legacy_id) not in (str, type(None)): return UNAVAILABLE
    data = result['data']; row = data['rows'].get(legacy_id)
    lines = ['【跨局助力】', NOTICE, '',
             '目录包括13份襁褓原记录和1份隐藏开局助力。同名襁褓保留各自来源；目录不是当前持有或下局菜单。',
             '四组襁褓的培育来源与六种后续蓝色支援沿用已有页面；本页补充准确关联和开局助力的双局条件。']
    if row is None:
        return '\n'.join(lines + ['', '请选择一项查看。只有开局助力显示失败局与下次开始的专门条件；其它项不会出现这些输入。'])
    lines += ['', '【' + row['name'] + ' · 原用途】', version._plain(row['item']['usage'])]
    if legacy_id == HIDDEN:
        lines += ['', '【是什么】',
                  '这是原资料标为隐藏的跨局记录，不是种子培育的第五种襁褓，也不表示你当前已经持有。',
                  '它明确指向下次开始时的收藏品“特勤任务影像”；不是六种蓝色支援选项中的一种。',
                  '', '【要分开核对的两局】',
                  '产生助力：常规行动、保密等级0～3，并确实探索失败。',
                  '下次收取：仍是常规行动、保密等级0～3；不能只看失败那一局的难度。',
                  '“主动放弃”“准备阶段退出”是否算同一种失败尚未在本页证明；不要自动勾为已失败。']
        if condition:
            for title, checks in (('产生助力的那局', condition['origin_checks']), ('下次开始', condition['receipt_checks'])):
                lines += ['', '【仅本页声明对照 · ' + title + '】']
                for check in checks:
                    state = '未知' if check['matches'] is None else '相符' if check['matches'] else '不符'
                    lines.append(check['label'] + '：' + state)
            started = condition['declared']['next_started']
            lines.append('下次是否已经开始：' + ('未知' if started is None else '已声明开始' if started else '尚未开始'))
            lines += ['', '【容易忽略的限制】', condition['warning']]
            if condition['status'] == 'documented_check_consumption_risk':
                lines.append('按本页“已开始其它难度”的声明，存在文献所述判定消耗而未领取的风险；本页没有确认实际消耗或发放。')
            if condition['status'] == 'listed_conditions_match_only':
                lines.append('两局已列条件相符；这仍不证明有可收取判定、服务器资格完整或已经领取。')
        lines += ['', '【影像能提供什么】', version._plain(data['originals']['items'][TARGET]['usage']),
                  '上面是收藏品原用途，不是已加到面板的预测值；实际持有、叠加、具体经验结算与最终数值需由相应计算另行核对。',
                  '不能因下一局或账户曾持有这件收藏品，就反推本次收取判定仍在。',
                  '', '【文献补充】', data['failure_support_documentation']['plain_acquisition_and_remark']]
    else:
        source = row['seed_source_reference']
        lines += ['', '【取得来源与后续分别看】',
                  '已有种子页面明确记载这份原ID的黄色襁褓来源。' if source['documented_source_id'] else
                  '这是同组原变体；种子是否会给出这份准确原ID仍未知。相同名字不能代替来源证明。']
        pointer = row['startup_pointer']
        if pointer:
            lines += ['它独立指向的后续支援：' + pointer['title'],
                      '点击下方入口查看已完成的支援说明与条件；不把同名六份羽蛇合并，也不当作已继承。']
        else:
            lines += ['下方回到已有培育页面核对具体来源与下次条件，不把本局通过区域数当成当前层号。']
    lines += ['', '【范围】',
              '这里查阅的是2026年10月16日固定国服资料，不代表当前账户已保留助力或下局已经领取。',
              '当前账户与服务器实际状态未知。本页不领取、不扣除、不创建下一局、不更改本局记忆或计算。']
    return '\n'.join(lines)
