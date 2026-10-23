"""Current exact-region entry grants and conditional exhaustion references."""
from copy import deepcopy
from hashlib import sha256
from html import unescape
from pathlib import Path, PurePosixPath
import json
import re

from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-regions-359'
DATA = 'rouge/data/current-region-reference.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = 'b939a8cf21544439a0a4566badb113a7923cef01e4b6290157452569705e9af8'
TOPIC = 'research/p3-expansion-313/current-topic.json'
DOCUMENT = 'research/p3-stage-context/community-main.html'
DOCUMENT_RECEIPT = 'research/p3-stage-context/source-receipt.json'
EXCERPTS = PACK + '/region-document-433770-excerpts.json'
NOTES = PACK + '/source-notes.json'
AP_FEATURE = 'rogue_6_feature_ap_1'
WINGS = 'rogue_6_outbuff_37'
GROUPS = ((None, '全部区域资料'), ('exit', '目标：抵达险路尽头'),
          ('boss', '目标：击败险路恶敌'), ('return', '秘境：耗尽后返回'))
NOTICE = ('选择准确区域，查看资料列示的入区行动力分项与离开条件。'
          '这些不是当前剩余行动力，也不是包含所有加成的最终值。')
UNAVAILABLE = '区域资料暂时无法核对，旧内容和条件结果已清除；恢复后请重新选择区域。'
DOCUMENT_AREAS = {
    '玻利瓦尔肤层': 5, '甜美的伤口': 6, '血色空脉': 7,
    '受害者腐殖': 8, '卡德霍之颅': 8, '源流交汇处': 5,
}


def _plain_html(value):
    return ' '.join(unescape(re.sub('<[^>]+>', '', value)).split())


def document_excerpts(html):
    """Keep contiguous original HTML slices with unambiguous Chinese headings."""
    areas = {}
    for name, amount in DOCUMENT_AREAS.items():
        starts = list(re.finditer(r'<div class="AKCollapse-title"[^>]*>[^<]*' + re.escape(name) + r'</div>', html))
        if len(starts) != 1:
            raise ValueError('Unique documented region heading required: ' + name)
        start = starts[0].start()
        pstart = html.index('<p>初始行动力：', start)
        next_heading = html.find('<div class="AKCollapse-title"', starts[0].end())
        if next_heading >= 0 and pstart >= next_heading:
            raise ValueError('Initial amount escaped the selected region')
        end = html.index('</p>', pstart) + len('</p>')
        paragraph = _plain_html(html[pstart:end])
        if not paragraph.startswith('初始行动力：' + str(amount)):
            raise ValueError('Documented initial amount changed')
        areas[name] = {'html': html[start:end], 'initial_ap_paragraph': paragraph,
                       'documented_base_ap': amount}
    needle = '进入后会获得一定量<b>本层专用</b>的行动力，行动力耗尽后会返回进入该层时所在节点的位置。'
    if html.count(needle) != 1:
        raise ValueError('Unique explicit special-region return paragraph required')
    start = html.rfind('<p>', 0, html.index(needle) + 1)
    end = html.index('</p>', html.index(needle)) + len('</p>')
    return {'areas': areas, 'portal_return_html': html[start:end],
            'portal_return_text': _plain_html(html[start:end])}


def _same(actual, expected):
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return actual.keys() == expected.keys() and all(_same(actual[k], v) for k, v in expected.items())
    if type(expected) is list:
        return len(actual) == len(expected) and all(_same(a, b) for a, b in zip(actual, expected))
    return actual == expected


def _file(relative):
    if type(relative) is not str:
        raise ValueError('Public source path required')
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or '\\' in relative or ':' in relative or rel.as_posix() != relative:
        raise ValueError('Unsafe path')
    path = ROOT.joinpath(*rel.parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Regular public source required')
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Linked source parent refused')
    return path


def derive_data(current, excerpts, receipt):
    details = current['details']
    grid = current['modules']['gridZone']
    zones = details['zones']
    missions = grid['zoneMissionBannerData']
    exhaustion = grid['scrapSideBarStepZeroHintBannerData']
    if len(zones) != 27 or set(zones) != set(missions) or set(zones) != set(exhaustion):
        raise ValueError('Complete 27-region three-table binding required')
    feature = details['relics'][AP_FEATURE]
    feature_item = details['items'][AP_FEATURE]
    if feature_item['usage'] != '机制道具，发放每层的步数':
        raise ValueError('Explicit Chinese entry-grant purpose required')
    grants = {}
    for buff in feature['buffs']:
        if buff['key'] not in ('zone_into_reward', 'secret_into_reward'):
            raise ValueError('Unreviewed grant type')
        board = {v['key']: v for v in buff['blackboard']}
        if len(board) != len(buff['blackboard']) or set(board) != {'id', 'count', 'zone'}:
            raise ValueError('Exact independent grant fields required')
        zone = board['zone']['valueStr']
        amount = board['count']['value']
        if (zone not in zones or zone in grants or board['id']['valueStr'] != 'rogue_6_ap'
                or type(amount) not in (int, float) or amount < 0 or int(amount) != amount):
            raise ValueError('Exact zone, resource and nonnegative integral grant required')
        grants[zone] = {'amount': int(amount), 'original': deepcopy(buff),
                        'runtime_attached_verified': False, 'actual_granted': None}
    if set(grants) != set(zones):
        raise ValueError('Each original region needs exactly one grant record')
    wings = current['customizeData']['commonDevelopment']['developments'][WINGS]
    if wings['buffName'] != '翅膀' or wings['rawDesc'] != ['进入第一层时，行动力+1']:
        raise ValueError('Exact current first-region technology description required')
    portals = details['gameConst']['portalZones']
    if len(portals) != len(set(portals)) or len(portals) != 19:
        raise ValueError('Explicit current portal-zone membership required')
    if receipt['community_revision'] != 433770 or receipt['community_file'] != DOCUMENT:
        raise ValueError('Pinned document provenance required')
    counts = {}
    for zone in zones.values():
        counts[zone['name']] = counts.get(zone['name'], 0) + 1
    positions = {}
    rows = []
    for zid, zone in zones.items():
        mission = version._plain(missions[zid]['bannerText'])
        hint = version._plain(exhaustion[zid]['hintText'])
        if missions[zid]['zoneId'] != zid or exhaustion[zid]['zoneId'] != zid:
            raise ValueError('Cross-region banner prohibited')
        if zid in portals:
            if mission != '自由探索，行动力耗尽后，将返回林间' or hint != '行动力耗尽后\n将返回原先的区域':
                raise ValueError('Portal return wording changed')
            group = 'return'
            if grants[zid]['original']['key'] != 'secret_into_reward':
                raise ValueError('Portal grant must retain its distinct original kind')
        elif mission == '目标：找到险路尽头节点进入下一区域' and '未抵达险路尽头' in hint and '追猎' in hint:
            group = 'exit'
        elif mission == '目标：找到险路恶敌节点并取得胜利' and '未击败险路恶敌' in hint and '追猎' in hint:
            group = 'boss'
        else:
            raise ValueError('Unreviewed exact goal/exhaustion combination')
        if group != 'return' and grants[zid]['original']['key'] != 'zone_into_reward':
            raise ValueError('Main-region grant must retain its distinct original kind')
        name = zone['name']
        positions[name] = positions.get(name, 0) + 1
        doc = excerpts['areas'].get(name)
        if doc and doc['documented_base_ap'] != grants[zid]['amount']:
            raise ValueError('Document and exact region parameter disagree')
        evidence = ('name_shared_not_variant_specific' if doc and counts[name] > 1 else
                    'unique_name_document_corroboration' if doc else 'parameter_only')
        rows.append({'id': zid, 'name': name, 'name_variant_index': positions[name],
                     'name_variant_count': counts[name], 'group': group,
                     'zone': deepcopy(zone), 'mission': deepcopy(missions[zid]),
                     'exhaustion': deepcopy(exhaustion[zid]), 'entry_grant': grants[zid],
                     'document_ap_evidence': evidence, 'document_ap': deepcopy(doc),
                     'wings_applicable_reference': zid == 'zone_1',
                     'actual_destination_zone': None, 'actual_return_node': None,
                     'actual_exhaustion_triggered': None, 'actual_final_ap': None})
    if sum(r['group'] == 'return' for r in rows) != 19 or sum(r['group'] == 'exit' for r in rows) != 4:
        raise ValueError('Current reviewed region families changed')
    if not any(r['id'] == 'zone_7' and r['name'] == '盲目者所见' for r in rows):
        raise ValueError('Current additional region required')
    return {'schema': 'current_region_reference_359_v1', 'game_commit': version.NEW_COMMIT,
            'rows': rows, 'entry_feature_item': deepcopy(feature_item),
            'wings_original': deepcopy(wings), 'portal_zone_ids': deepcopy(portals),
            'document': {'url': receipt['community_pinned_url'], 'revision': 433770,
                         'portal_return_text': excerpts['portal_return_text']},
            'old_budget_replaced': False, 'complete_action_point_calculation': False,
            'actual_gameplay_verified': False, 'run_updated': False}


def packet():
    try:
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        names = {DATA, TOPIC, DOCUMENT, DOCUMENT_RECEIPT, EXCERPTS, NOTES}
        if (manifest['schema'] != 'current_region_359_manifest_v1'
                or manifest['game_commit'] != version.NEW_COMMIT or set(manifest['files']) != names):
            return None
        blobs = {}
        for name, pin in manifest['files'].items():
            content = _file(name).read_bytes()
            if type(pin['bytes']) is not int or len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']:
                return None
            blobs[name] = content
        source = version.packet()
        if source is None:
            return None
        current = json.loads(blobs[TOPIC])
        if not _same(current, source['current']):
            return None
        receipt = json.loads(blobs[DOCUMENT_RECEIPT])
        if (receipt['community_sha256'] != sha256(blobs[DOCUMENT]).hexdigest()
                or receipt['community_bytes'] != len(blobs[DOCUMENT])):
            return None
        excerpts = document_excerpts(blobs[DOCUMENT].decode('utf8'))
        if not _same(excerpts, json.loads(blobs[EXCERPTS])):
            return None
        data = json.loads(blobs[DATA])
        if not _same(data, derive_data(current, excerpts, receipt)):
            return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, source['source_identity']),
                'run_updated': False, 'actual_gameplay_verified': False}
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, AttributeError, IndexError):
        return None


def catalog(group=None):
    if (group is not None and type(group) is not str) or group not in dict(GROUPS):
        return None
    source = packet()
    if source is None:
        return None
    return {**source, 'rows': [deepcopy(row) for row in source['data']['rows']
                              if group is None or row['group'] == group]}


def locate(category, key):
    if type(category) is not str or type(key) is not str or category != 'regions':
        return None
    source = packet()
    if source is None or not any(row['id'] == key for row in source['data']['rows']):
        return None
    return {'zone_id': key}


def reference(zone_id, action_points=None, goal_completed=None, wings=None):
    if (type(zone_id) is not str or (action_points is not None and
            (type(action_points) is not int or not 0 <= action_points <= 2147483647))
            or (goal_completed is not None and type(goal_completed) is not bool)
            or (wings is not None and type(wings) is not bool)):
        return None
    source = packet()
    if source is None:
        return None
    row = next((r for r in source['data']['rows'] if r['id'] == zone_id), None)
    if row is None or (row['group'] == 'return' and goal_completed is not None):
        return None
    if not row['wings_applicable_reference'] and wings is not None:
        return None
    depleted = None if action_points is None else action_points == 0
    matches = (depleted if row['group'] == 'return' else False if depleted is False or goal_completed is True
               else True if depleted is True and goal_completed is False else None)
    wing_amount = (None if wings is None else 1 if wings else 0) if row['wings_applicable_reference'] else None
    subtotal = (row['entry_grant']['amount'] + wing_amount
                if row['wings_applicable_reference'] and wing_amount is not None else None)
    return {**source, 'row': deepcopy(row),
            'declared': {'action_points': action_points, 'goal_completed': goal_completed, 'wings': wings},
            'exhaustion_description_conditions_match': matches,
            'wings_reference_addition': wing_amount, 'base_and_wings_reference_subtotal': subtotal,
            'actual_final_entry_ap': None, 'actual_exhaustion_triggered': None,
            'actual_destination_zone': None, 'actual_return_node': None,
            'route_recommended': False, 'old_budget_replaced': False}


def label(row):
    return row['name'] + (' · 资料' + str(row['name_variant_index']) + '/' + str(row['name_variant_count'])
                           if row['name_variant_count'] > 1 else '')


def player_text(result):
    row = result['row']
    lines = ['【区域】' + label(row), '', '【本区域的目标】', version._plain(row['mission']['bannerText']),
             '', '【入区行动力分项】',
             '当前固定资料列示：' + str(row['entry_grant']['amount']) + ' 点。',
             '这是对应区域的资料数值；尚未确认这些发放规则本次是否生效，也不是当前剩余行动力。']
    evidence = row['document_ap_evidence']
    if evidence == 'unique_name_document_corroboration':
        lines += ['固定文献也写明该区域的初始数量：' + row['document_ap']['initial_ap_paragraph']]
    elif evidence == 'name_shared_not_variant_specific':
        lines += ['固定文献对“' + row['name'] + '”记载相同数量；但没有区分这两份同名区域，不能把文献当成具体变体的证明。']
    else:
        lines += ['这一原区域的独立数量文献尚未取得，仅列参数，不补成实际初始值。']
    if row['wings_applicable_reference']:
        lines += ['', '【只在第一层对照：翅膀】', '当前科技说明：进入第一层时，行动力+1。']
        if result['wings_reference_addition'] is None:
            lines += ['本页未声明翅膀是否生效，因此不合成这两个分项。']
        else:
            lines += ['仅基础参数与翅膀的对照小计：' + str(result['base_and_wings_reference_subtotal']) + ' 点。',
                      '这仍不是完整实际入区值；其它来源及本次生效情况没有核验。']
    lines += ['', '【行动力耗尽时的原提示】', version._plain(row['exhaustion']['hintText'])]
    if row['group'] == 'return':
        lines += ['文献说明：秘境使用本层专用的行动力，耗尽后返回进入秘境时的节点。',
                  '这不是“进入下一主层”。原先区域与具体节点尚未读取，不指定真实返回坐标，也不预测返回后的行动力。']
    elif row['group'] == 'boss':
        lines += ['原条件要求击败险路恶敌；仅抵达其节点不能算目标完成。']
    else:
        lines += ['抵达险路尽头与实际离开区域不是同一件事；后续选择与执行仍须另行核对。']
    status = result['exhaustion_description_conditions_match']
    lines += ['', '【仅按本页声明对照耗尽条件】',
              ('资料中的条件相符；实际是否触发仍未知。' if status is True else
               '资料中的条件不相符；不据此保证仍能继续行动或已经安全离开。' if status is False else
               '信息不足，暂不能对照。')]
    lines += ['', '【仍未确认】',
              '当前真实行动力、发放与扣除顺序、羽瞰点返还、实际追猎/返回、进入资格和真实目的地均未验证。',
              '完整最终入区行动力：未知。这里不借用旧预算器填补，也不会自动选择路线或改动本局。',
              '', '【来源】当前国服10月16日固定原表；文献为已保存的PRTS修订433770，不冒充新网页或当前服务器执行。',
              result['data']['document']['url']]
    return '\n'.join(lines)
