"""Exact current upgrade-voucher ranges and documented sources, without recruitment."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import re

from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-upgrade-tickets-360'
DATA = 'rouge/data/current-upgrade-tickets.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '34a4cf3d64f67f4fc2a95db6cb74c9717d7322d11a95fb3e2744a8fcb1cec3b7'
PROFESSIONS = (('PIONEER', '先锋'), ('WARRIOR', '近卫'), ('TANK', '重装'),
               ('SNIPER', '狙击'), ('CASTER', '术师'), ('MEDIC', '医疗'),
               ('SUPPORT', '辅助'), ('SPECIAL', '特种'))
KINDS = (('general', '跨职业物资券'), ('profession', '职业进阶券'),
         ('relic', '新典训所附进阶券'))
REST_CHOICE = 'choice_ro6_rest_4'
UNAVAILABLE = '进阶券资料暂时无法核对，旧券种、说明和来源入口已清除；恢复后请重新选择。'
NOTICE = '18份进阶券资料，按券本身的职业与星级范围查询；不是本局持有券、可选干员或完整取得池。'


def source_rows(current):
    tickets, items = current['upgradeTickets'], current['items']
    if len(tickets) != 18:
        raise ValueError('The complete pinned18 upgrade records are required')
    origins = {}
    for relic_id, relic in current['relics'].items():
        for buff in relic['buffs']:
            if buff['key'] != 'immediate_reward':
                continue
            values = {v['key']: v['valueStr'] if v['valueStr'] is not None else v['value']
                      for v in buff['blackboard']}
            identity = values.get('id')
            if identity in tickets:
                if identity in origins or values.get('count') != 1:
                    raise ValueError('One exact immediate reward binding required')
                item = items[relic_id]
                if item['type'] != 'RELIC' or '新典训' not in item['name']:
                    raise ValueError('Source type and exact full name required')
                origins[identity] = {'id': relic_id, 'item': deepcopy(item),
                                     'relic': deepcopy(relic), 'reference_count': 1,
                                     'actual_obtained': None, 'actual_recipient': None}
    if len(origins) != 8:
        raise ValueError('All eight explicit new-training source pointers required')
    rows = []
    for identity, ticket in tickets.items():
        item = items[identity]
        if ticket['id'] != identity or item['id'] != identity or item['type'] != 'UPGRADE_TICKET':
            raise ValueError('Exact full upgrade records required')
        professions = ticket['professionList']
        if not professions or len(set(professions)) != len(professions) or any(p not in dict(PROFESSIONS) for p in professions):
            raise ValueError('Unknown professions cannot be silently translated')
        stars = []
        for rarity in ticket['rarityList']:
            if type(rarity) is not str or not re.fullmatch(r'TIER_[1-6]', rarity):
                raise ValueError('Explicit named star ranges required')
            stars.append(int(rarity[-1]))
        if not stars or len(set(stars)) != len(stars) or '不消耗希望' not in item['usage']:
            raise ValueError('Complete star list and explicit free-upgrade usage required')
        origin = origins.get(identity)
        kind = 'relic' if origin else 'profession' if len(professions) == 1 else 'general'
        label = item['name'] + (' · ' + origin['item']['name'] + '所附' if origin else '')
        rows.append({'id': identity, 'name': item['name'], 'label': label, 'kind': kind,
                     'professions': deepcopy(professions), 'stars': stars,
                     'item': deepcopy(item), 'ticket': deepcopy(ticket),
                     'relic_origin': deepcopy(origin), 'actual_owned': None,
                     'actual_candidates': None, 'actual_upgraded': None})
    if {r['kind']: sum(s['kind'] == r['kind'] for s in rows) for r in rows} != {'general': 2, 'profession': 8, 'relic': 8}:
        raise ValueError('Exact two general/eight profession/eight sourced records required')
    return rows


def _read_public(name):
    if type(name) is not str:
        raise ValueError('Public relative path required')
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or rel.as_posix() != name:
        raise ValueError('Unsafe public source')
    path = ROOT.joinpath(*rel.parts)
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Linked public source refused')
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Linked public parent refused')
    return path.read_bytes()


def packet():
    try:
        raw = _read_public(MANIFEST)
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        expected = {DATA, PACK+'/source-notes.json', PACK+'/general-w-page.html',
                    PACK+'/general-w-download.json', PACK+'/tools-w-page.html',
                    PACK+'/tools-w-download.json', PACK+'/documented-recruitment.html',
                    PACK+'/documented-tools.html', 'research/p3-expansion-313/current-topic.json',
                    'rouge/data/current-rest-travel.json',
                    'research/p3-current-rest-travel-331/runtime-manifest.json'}
        if manifest['schema'] != 'current_upgrade_tickets_360_manifest_v1' or manifest['game_commit'] != version.NEW_COMMIT or set(manifest['files']) != expected:
            return None
        values = {}
        for name, pin in manifest['files'].items():
            content = _read_public(name)
            if type(pin['bytes']) is not int or len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']:
                return None
            values[name] = content
        data = json.loads(values[DATA])
        source = version.packet()
        if source is None or data['schema'] != 'current_upgrade_tickets_360_v1' or data['game_commit'] != version.NEW_COMMIT:
            return None
        if data['rows'] != source_rows(source['current']['details']) or data['complete_acquisition_pool'] is not False:
            return None
        from . import current_rest_travel as rest
        rest_packet = rest.packet()
        link = data['rest_source']
        if rest_packet is None or link['target'] != rest.locate('choices', REST_CHOICE) or link['choice'] != source['current']['details']['choices'][REST_CHOICE]:
            return None
        if link['source_identity'] != json.loads(json.dumps(rest_packet['source_identity'])):
            return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, source['source_identity']),
                'actual_owned': None, 'actual_candidates': None, 'actual_eligible': None,
                'actual_cost': None, 'actual_upgraded': None, 'actual_cultivation': None,
                'run_updated': False, 'calculation_applied': False}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, UnicodeError, RecursionError):
        return None


def reference(ticket_id=None, *, profession=None, kind=None, star=None, query=''):
    if ticket_id is not None and type(ticket_id) is not str:
        return None
    if profession is not None and (type(profession) is not str or profession not in dict(PROFESSIONS)):
        return None
    if kind is not None and (type(kind) is not str or kind not in dict(KINDS)):
        return None
    if star is not None and (type(star) is not int or star not in range(1, 7)):
        return None
    if type(query) is not str:
        return None
    result = packet()
    if result is None:
        return None
    rows = [deepcopy(row) for row in result['data']['rows']
            if (profession is None or profession in row['professions'])
            and (kind is None or row['kind'] == kind)
            and (star is None or star in row['stars'])
            and (not query.strip() or query.strip() in row['label'])]
    selected = next((row for row in rows if row['id'] == ticket_id), None)
    if ticket_id is not None and selected is None:
        return None
    return {**result, 'rows': rows, 'selected': selected,
            'filters': {'profession': profession, 'kind': kind, 'star': star, 'query': query}}


def destination(ticket_id):
    result = reference(ticket_id)
    if result is None or result['selected'] is None:
        return None
    row = result['selected']
    if row['relic_origin'] is not None:
        return {'reader': 'relic', 'category': 'relics', 'key': row['relic_origin']['id'],
                'name': row['relic_origin']['item']['name'], 'actual_owned': None}
    if ticket_id == 'rogue_6_upgrade_ticket_all':
        return {'reader': 'rest', **deepcopy(result['data']['rest_source']), 'actual_owned': None}
    return None


def locate(category, identity):
    if type(category) is not str or type(identity) is not str:
        return None
    result = reference()
    if result is None:
        return None
    if category == 'items':
        row = next((r for r in result['rows'] if r['id'] == identity), None)
    elif category == 'relics':
        row = next((r for r in result['rows'] if r['relic_origin'] and r['relic_origin']['id'] == identity), None)
    elif category == 'choices' and identity == REST_CHOICE:
        row = next((r for r in result['rows'] if r['id'] == 'rogue_6_upgrade_ticket_all'), None)
    else:
        row = None
    return {'ticket_id': row['id'], 'source_request': {'category': category, 'key': identity}} if row else None


def player_text(result):
    lines = ['【进阶券资料】', NOTICE, '', '【怎样查询】',
             '按职业、券种和资料中的星级范围分别筛选。同名券保留各自来源；多职业筛选会重合，不是拥有多张券。',
             '星级筛选只对照券的原始范围，不证明对应星级或具体干员能够进阶。']
    row = result['selected']
    if row:
        lines += ['', '【' + row['label'] + '】',
                  '适用职业：' + '、'.join(dict(PROFESSIONS)[p] for p in row['professions']),
                  '券种列出的星级：' + '、'.join(str(s)+'★' for s in row['stars']),
                  '完整用途：' + version._plain(row['item']['usage']),
                  '希望说明：原文明确写“不消耗希望”，这是此券的进阶用途；不推广为其它招募免费。']
        if row['relic_origin']:
            origin = row['relic_origin']
            lines += ['', '【明确对应的新典训】' + origin['item']['name'],
                      '该收藏品的发放记录明确指向这一份进阶券，记录数量为1。不是凭券名或编号猜来源，也不证明本局已经领取。',
                      '收藏品的完整用途：' + version._plain(origin['item']['usage']),
                      '定向强化归属、实际进阶、培养数值与战斗内触发仍需独立证据，本页不代入计算。']
        elif row['id'] == 'rogue_6_upgrade_ticket_all':
            lines += ['', '【已核对的一处取得说明】安全的角落 → 查看无人机',
                      '准确原文：“获得高级物资配给券”。该选项未单列张数，不能把新典训的1张或1人套到这里。',
                      '事件页面列出的是文献选项目录，不是本次完整菜单；可以打开准确原文继续查看。']
        else:
            lines += ['', '【取得方式】' + version._plain(row['item']['obtainApproach']),
                      '当前证据没有把这份券唯一绑定到具体事件或收藏品；不自动借用同名券的来源。']
    else:
        lines += ['', '请选择一份券，查看它自己的完整用途、职业与星级范围，以及有原件支持的取得说明。']
    lines += ['', '【进阶、招募和直升有什么不同】',
              '招募券用来招募干员；通常招募中，再次招募同一名干员可解除本局能力限制。进阶券写明的是进阶用途，不据此添加一名新干员。',
              '“直升”是首次招募时就处于已进阶状态，不能把它当成这18份进阶券资料的另一种名称。',
              '通常干员进阶只解除限制，不会超过账号已有培养。临时招募和助战等有各自规则，不能统一套用账号满级或同一套培养。',
              '券本身列出的职业和星级只是其中一部分条件。是否已经招募、是否已进阶、培养情况、特殊升变职业以及当前可选名单都须另行核对。',
              '资料中的八份职业券与八份新典训所附券名称相同，但原记录不同。这些进阶券不属于已核对的招募券留存配对，不能据此认定可以留存。',
              '', '【范围与未知】',
              '18份原项来自2026年10月16日固定国服资料；术语另由集成战略说明核对，两种物资券用途另核对道具一览。具体来源可在完整原值与来源页查阅。',
              '本局实际持有、完整取得池、可选人选、是否实际进阶、最终培养、其它费用与当前服务器资格仍未知。',
              '本页只供局外查阅，不招募、不进阶、不花费希望、不修改培养或本局记忆；不提供路线推荐或概率。']
    return '\n'.join(lines)
