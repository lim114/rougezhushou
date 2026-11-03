"""Exact current initial-configuration/recruitment-group associations."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
from pathlib import Path, PurePosixPath
import json
import re

from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-initial-recruit-364'
TOPIC = 'research/p3-expansion-313/current-topic.json'
TOPIC_HTML = 'research/p3-current-recruit-tickets-354/topic-page.html'
TOPIC_DOWNLOAD = 'research/p3-current-recruit-tickets-354/source-download.json'
GENERAL_HTML = PACK + '/general-440806.html'
GENERAL_DOWNLOAD = PACK + '/general-original-download.json'
EXCERPTS = PACK + '/documented-recruitment.json'
DATA = 'rouge/data/current-initial-recruit.json'
NOTES = PACK + '/source-notes.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = 'ae81c67d6365055b68b6818c5daad81a7970a035e7dc00b1d099bec7c5e32c14'
KINDS = (('initial', '按开局配置查看'), ('group', '按招募组合查看'))
SCOPES = (('all', '全部资料'), ('normal', '常规行动'), ('monthly', '实践者列表'), ('unlinked', '尚未关联到初始配置'))
NOTICE = '开局配置与招募组合按原资料明确关联。这里可查内容与条件，不代表当前账户已解锁、实际菜单或已经招募。'
UNAVAILABLE = '开局招募资料暂时无法核对，旧组合、条件和关联入口已清除；恢复后请重新选择。'
RANDOM = 'recruit_group_random'
FIXED = {
    'recruit_group_1': ('先手必胜', ['先锋', '狙击', '特种']),
    'recruit_group_2': ('稳扎稳打', ['重装', '术师', '狙击']),
    'recruit_group_3': ('取长补短', ['近卫', '辅助', '医疗']),
    'recruit_group_4': ('灵活部署', ['先锋', '辅助', '特种']),
    'recruit_group_5': ('坚不可摧', ['重装', '术师', '医疗']),
}


def plain_html(text):
    return ' '.join(unescape(re.sub('<[^>]+>', '', text)).split())


def document_fragments(topic, general):
    if '"wgRevisionId":442954' not in topic or 'oldid=442954' not in topic:
        raise ValueError('Specific current-theme document revision required')
    if '"wgRevisionId":440806' not in general or 'oldid=440806' not in general:
        raise ValueError('Separate generic document revision required')
    marker = '<b>3. 选择招募组合</b>'
    start = topic.rfind('<p>', 0, topic.index(marker))
    end = topic.index('<p><b>4. 进行初始招募</b>', start)
    theme_fragment = topic[start:end]
    start = general.index('<div class="mw-heading mw-heading4"><h4 id="2._选择招募组合">')
    end = general.index('<div class="mw-heading mw-heading4"><h4 id="3._招募干员">', start)
    generic_fragment = general[start:end]
    theme_rows = dict(re.findall(r'<li><b>([^<]+)</b>：(.*?)</li>', theme_fragment, re.S))
    generic_rows = dict(re.findall(r'<li><b>([^<]+)</b>：(.*?)</li>', generic_fragment, re.S))
    names = {'随心所欲', *(name for name, _ in FIXED.values())}
    if set(theme_rows) != names or set(generic_rows) != names:
        raise ValueError('Complete six named recruitment combinations required')
    text = plain_html(theme_rows['随心所欲'])
    for clause in ('不会出现三张相同职业', '包含5星临时招募', '其它招募组合进行一次探索',
                   '第一张为5星临时招募券', '第二张仅可能出现先锋、近卫、重装、特种',
                   '第三张仅可能出现狙击、术师、医疗、辅助'):
        if clause not in text:
            raise ValueError('Specific-theme random guarantees changed: ' + clause)
    if '包含4星临时招募' not in plain_html(generic_rows['随心所欲']):
        raise ValueError('Generic four-star wording must remain separate')
    return {'theme_html': theme_fragment, 'generic_html': generic_fragment,
            'theme_rows_html': theme_rows, 'generic_rows_html': generic_rows}


def initial_key(row):
    return json.dumps([row['modeId'], row['modeGrade'], row.get('predefinedId'), row.get('predefinedStyle')],
                      ensure_ascii=True, separators=(',', ':'))


def derive_data(current, baseline, documents):
    source = current['details']
    groups, configs, months = source['recruitGrps'], source['init'], source['monthSquad']
    if len(groups) != 14 or len(configs) != 21 or len({initial_key(v) for v in configs}) != 21:
        raise ValueError('Four-part identity for all21 configurations and14 groups required')
    reverse = {key: [] for key in groups}
    initial = []
    for config in configs:
        key = initial_key(config)
        ids = config['initialRecruitGroup']
        if len(ids) != len(set(ids)) or not ids or any(g not in groups for g in ids):
            raise ValueError('Every explicit group pointer must resolve once')
        for gid in ids:
            reverse[gid].append(key)
        if config['modeId'] == 'NORMAL':
            if config['predefinedId'] is not None or type(config['modeGrade']) is not int or not 0 <= config['modeGrade'] <= 16:
                raise ValueError('Reviewed normal configuration required')
            scope = 'normal'
            label = '常规行动 · 保密等级' + str(config['modeGrade'])
            monthly = None
        elif config['modeId'] == 'MONTH_TEAM' and config['predefinedId'] in months:
            monthly = deepcopy(months[config['predefinedId']])
            if monthly['id'] != config['predefinedId']:
                raise ValueError('Exact monthly identity required')
            scope = 'monthly'
            label = '实践者列表 · ' + monthly['teamYear'] + '年' + str(int(monthly['teamMonth'])) + '月 · ' + monthly['teamName']
        else:
            raise ValueError('Unreviewed initial mode')
        initial.append({'id': key, 'label': label, 'scope': scope, 'original': deepcopy(config),
                        'monthly_original': monthly, 'group_ids': deepcopy(ids),
                        'actual_menu': None, 'actual_initial_recruits': None, 'actual_initial_resources': None})
    if sorted(r['original']['modeGrade'] for r in initial if r['scope'] == 'normal') != list(range(17)):
        raise ValueError('All current normal grades required separately')
    if len([r for r in initial if r['scope'] == 'monthly']) != 4 or sum(map(len, reverse.values())) != 106:
        raise ValueError('Four monthly configurations and106 exact pointers required')
    rows = []
    for gid, group in groups.items():
        if group['id'] != gid:
            raise ValueError('Exact group identity required')
        linked = [r for r in initial if r['id'] in reverse[gid]]
        kinds = {r['scope'] for r in linked}
        if len(kinds) > 1:
            raise ValueError('Previously unreviewed mixed-mode group')
        scope = next(iter(kinds)) if kinds else 'unlinked'
        if gid in FIXED:
            name, professions = FIXED[gid]
            if group['name'] != name or group['desc'] != '、'.join(professions) + '招募券各一张':
                raise ValueError('Explicit fixed profession description changed')
            if plain_html(documents['theme_rows_html'][name]) != '获得' + group['desc']:
                raise ValueError('Current-theme profession description does not corroborate')
            slots = [{'professions': [p], 'count': 1, 'order_verified': False, 'guaranteed_temporary_rarity': None} for p in professions]
            count, guarantee = 3, None
        elif gid == RANDOM:
            if group['name'] != '随心所欲' or group['desc'] != '三张随机的招募券，其中一张必定出现5星临时招募' or group['unlockDesc'] != '使用其他招募组合进行一次探索':
                raise ValueError('Current five-star guarantee and unlock wording required')
            count, guarantee = 3, 5
            slots = [
                {'position': 1, 'professions': None, 'count': 1, 'guaranteed_temporary_rarity': 5},
                {'position': 2, 'professions': ['先锋', '近卫', '重装', '特种'], 'count': 1, 'guaranteed_temporary_rarity': None},
                {'position': 3, 'professions': ['狙击', '术师', '医疗', '辅助'], 'count': 1, 'guaranteed_temporary_rarity': None}]
        else:
            if group['name'] != '支援作战' or group['desc'] != '两张随机的招募券' or group['unlockDesc'] is not None:
                raise ValueError('Unreviewed support group description')
            count, guarantee, slots = 2, None, []
        label = group['name']
        if label == '支援作战':
            label += ' · ' + (linked[0]['label'].removeprefix('实践者列表 · ') if linked else '未关联资料' + str(len([r for r in rows if r['scope'] == 'unlinked']) + 1))
        rows.append({'id': gid, 'label': label, 'scope': scope, 'original': deepcopy(group),
                     'initial_ids': reverse[gid], 'ticket_count_reference': count,
                     'slots_reference': slots, 'guaranteed_temporary_rarity_reference': guarantee,
                     'random_choice': gid == RANDOM, 'actual_unlocked': None, 'actual_ticket_ids': None,
                     'actual_candidates': None, 'actual_selected': None})
    if len([r for r in rows if r['scope'] == 'unlinked']) != 4:
        raise ValueError('Four unassociated definitions must not be assigned to guessed months')
    return {'schema': 'current_initial_recruit_364_v1', 'game_commit': version.NEW_COMMIT,
            'initial': initial, 'groups': rows, 'explicit_association_count': 106,
            'raw_group_definitions_equal_previous_baseline': groups == baseline['details']['recruitGrps'],
            'source_scope': {'theme_revision': 442954, 'generic_revision': 440806,
                'theme_url': 'https://m.prts.wiki/index.php?title=沉沦者的黑流树海&oldid=442954',
                'generic_url': 'https://m.prts.wiki/index.php?title=集成战略&oldid=440806',
                'generic_four_star_applied_to_current_theme': False, 'current_server_verified': False},
            'actual_account_unlocks': None, 'actual_random_candidates': None, 'run_updated': False}


def _same(a, b):
    return (type(a) is type(b) and (a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a) if type(a) is dict
            else len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b)) if type(a) is list else a == b))


def _file(name):
    if type(name) is not str:
        raise ValueError('Public relative file required')
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or rel.as_posix() != name:
        raise ValueError('Public relative file required')
    path = ROOT.joinpath(*rel.parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Regular in-root source required')
    if any(p.is_symlink() for p in path.parents if p != ROOT and ROOT in p.parents):
        raise ValueError('Linked source parent refused')
    return path


def packet():
    try:
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        names = {TOPIC, TOPIC_HTML, TOPIC_DOWNLOAD, GENERAL_HTML, GENERAL_DOWNLOAD, EXCERPTS, DATA, NOTES}
        if manifest['schema'] != 'current_initial_recruit_364_manifest_v1' or set(manifest['files']) != names:
            return None
        blobs = {}
        for name, pin in manifest['files'].items():
            body = _file(name).read_bytes()
            if type(pin['bytes']) is not int or len(body) != pin['bytes'] or sha256(body).hexdigest() != pin['sha256']:
                return None
            blobs[name] = body
        for html, download in ((TOPIC_HTML, TOPIC_DOWNLOAD), (GENERAL_HTML, GENERAL_DOWNLOAD)):
            receipt = json.loads(blobs[download])
            if receipt['http_status'] != 200 or receipt['bytes'] != len(blobs[html]) or receipt['sha256'] != sha256(blobs[html]).hexdigest():
                return None
        version_packet = version.packet()
        if version_packet is None or not _same(json.loads(blobs[TOPIC]), version_packet['current']):
            return None
        documents = document_fragments(blobs[TOPIC_HTML].decode('utf8'), blobs[GENERAL_HTML].decode('utf8'))
        if not _same(documents, json.loads(blobs[EXCERPTS])):
            return None
        data = json.loads(blobs[DATA])
        if not _same(data, derive_data(version_packet['current'], version_packet['baseline'], documents)):
            return None
        return {'data': data, 'documents': documents, 'source_identity': (MANIFEST_SHA256, version_packet['source_identity']),
                'actual_unlocked': None, 'run_updated': False}
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, AttributeError, IndexError):
        return None


def catalog(kind='initial', scope='all', query=''):
    if (type(kind) is not str or kind not in dict(KINDS) or type(scope) is not str or scope not in dict(SCOPES)
            or (kind == 'initial' and scope == 'unlinked') or type(query) is not str):
        return None
    result = packet()
    if result is None:
        return None
    rows = result['data']['initial' if kind == 'initial' else 'groups']
    return {**result, 'kind': kind, 'scope': scope, 'query': query,
            'rows': [deepcopy(row) for row in rows if (scope == 'all' or row['scope'] == scope)
                     and query.strip() in row['label'] + row['original'].get('desc', '')]}


def locate(category, key):
    if type(category) is not str or category != 'initial' or type(key) is not str:
        return None
    result = packet()
    if result is None or not any(r['id'] == key for r in result['data']['initial']):
        return None
    return {'kind': 'initial', 'key': key}


def detail(kind, key, other_exploration=None):
    if (type(kind) is not str or kind not in dict(KINDS) or type(key) is not str
            or (other_exploration is not None and type(other_exploration) is not bool)):
        return None
    result = packet()
    if result is None:
        return None
    row = next((r for r in result['data']['initial' if kind == 'initial' else 'groups'] if r['id'] == key), None)
    if row is None or (other_exploration is not None and not (kind == 'group' and key == RANDOM)):
        return None
    if kind == 'initial':
        groups = {r['id']: r for r in result['data']['groups']}
        related = [{'target': {'kind': 'group', 'key': key}, 'label': groups[key]['label']} for key in row['group_ids']]
    else:
        related = [{'target': {'kind': 'initial', 'key': r['id']}, 'label': r['label']} for r in result['data']['initial'] if r['id'] in row['initial_ids']]
    return {**result, 'kind': kind, 'row': deepcopy(row), 'target': {'kind': kind, 'key': key}, 'related': related,
            'other_exploration_declared': other_exploration,
            'listed_unlock_description_matches': other_exploration if kind == 'group' and key == RANDOM else None,
            'actual_unlocked': None, 'actual_eligible': None, 'actual_menu': None, 'actual_recruits': None}


def player_text(result):
    row, kind = result['row'], result['kind']
    lines = [row['label'], '', '【这份资料表示什么】']
    if kind == 'initial':
        original = row['original']
        lines += ['该开局配置明确列出' + str(len(row['group_ids'])) + '份招募组合记录，可从下面的关联列表打开。',
                  '原表关联不等于当前账户已解锁、菜单已展示或已经选择。', '', '【原始资源参考】']
        for field, name in (('initialHp', '目标生命'), ('initialMaxHp', '目标生命上限'), ('initialGold', '源石锭'),
                            ('initialPopulation', '希望'), ('initialSquadCapacity', '可携带干员'), ('initialShield', '护盾')):
            lines.append(name + '：' + str(original[field]))
        lines += ['这些是初始配置分项，分队、科技和收藏品仍可影响实际值。']
        if row['scope'] == 'monthly':
            lines += ['同为保密等级0的不同实践者配置各自保留；不因同等级或同名“支援作战”而合并。',
                      '本页未计算理想践行者、完整阵容、领取资格或月份开放状态。']
    else:
        original = row['original']
        lines += [original['desc'], '解锁原文：' + (original['unlockDesc'] or '本条没有单独说明；不能因此认定账户已解锁。')]
        if row['scope'] == 'unlinked':
            lines += ['', '【当前关联缺失】', '当前21份初始配置都没有引用这一记录。无法确定它属于哪个月份或能否选择，不按编号补成未来月份。']
        else:
            lines += ['', '【明确关联】', '原表有' + str(len(row['initial_ids'])) + '份初始配置引用它；可反向打开各份配置。']
        if row['id'] in FIXED:
            lines += ['', '【职业组成】', '、'.join(slot['professions'][0] + '招募券×1' for slot in row['slots_reference']),
                      '这是职业组成，未把列示先后当实际出券顺序。具体干员候选和招募费用仍未知。']
        elif row['random_choice']:
            lines += ['', '【本主题的随机范围】', '固定国服原文和本主题文献均说明：有一张保证出现5星临时招募。',
                      '本主题文献进一步说明：第1张有5星临时招募；第2张来自先锋、近卫、重装、特种；第3张来自狙击、术师、医疗、辅助。',
                      '第一张的完整职业与其它人选范围未从当前组合原文取得，不能借通用页面补全。',
                      '“不会三张同职业”不等于“三张职业都不同”，不要据此排除两张同职业。',
                      '五颗星的保证不代表随机干员已确定，也不代表所有候选都只有五星。',
                      '', '【仅本页对照解锁说明】',
                      '曾使用其它组合进行一次探索：' + ('未知' if result['other_exploration_declared'] is None else '是' if result['other_exploration_declared'] else '否'),
                      '这只对照已写明的说明；实际账户解锁与本次可选资格仍未知。',
                      '', '【为何不采用通用页面的4星说法】',
                      '通用“集成战略”修订440806仍写4星保证；黑流树海原文及主题页442954写5星。适用范围不同，本主题按自己的5星资料展示，通用说法单独保留。']
        else:
            lines += ['', '两张随机招募券不等于常规“随心所欲”。当前这条原文没有保证星级或职业池，不能套入5星保证或三张券的顺序。']
    lines += ['', '【范围】', '固定资料共14份组合定义、21份初始配置；只有10份组合被这些配置引用，另外4份未关联。',
              '组合定义与更新前快照相同，不称为14种新增内容。行动奖励支援、招募组合和最终招募名单是不同事项。',
              '不预测随机人选或概率，不操作游戏、不扣希望，也不改账户与本局记忆。',
              '', '【来源】固定国服10月16日原表；主题文献442954与通用文献440806分别保留，非当前服务器实测。',
              result['data']['source_scope']['theme_url']]
    if kind == 'group' and row['random_choice']:
        lines += ['通用页面（仅作范围对照）：' + result['data']['source_scope']['generic_url']]
    return '\n'.join(lines)
