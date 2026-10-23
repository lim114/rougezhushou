"""Exact current recruitment/stashed ticket directory; no inventory or recruiting."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import re

from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-recruit-tickets-354'
DATA = 'rouge/data/current-recruit-tickets.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '1484ceb44fc0582323ebc742d52cd5d409307c7d7f63a98708d68a34b3f3d2bb'
PROFESSIONS = (
    ('PIONEER', '先锋'), ('WARRIOR', '近卫'), ('TANK', '重装'),
    ('SNIPER', '狙击'), ('CASTER', '术师'), ('MEDIC', '医疗'),
    ('SUPPORT', '辅助'), ('SPECIAL', '特种'),
)
FAMILIES = (
    ('profession', '单职业招募券'), ('protocol', '双职业招募券'),
    ('coordination', '四职业招募券'), ('dispatch', '人事调度函'),
    ('limited', '限定星级与随机临时券'),
)
LINKS = {
    'exit': ('choice_ro6_final1_2', '险路尽头：召集同伴'),
    'rest': ('choice_ro6_rest_7', '安全的角落：尝试发出求援信号'),
}
UNAVAILABLE = '招募券的来源暂时无法核对，旧券种、说明和原文入口已清除；恢复后请重新选择。'
NOTICE = '47种招募券的资料目录，不是本局持有券或奖励池；实际库存、人选、希望费用与领取情况尚未读取。'


def family(ticket_id, ticket):
    if '_temp_' in ticket_id or '_5star_double_' in ticket_id:
        return 'limited'
    size = len(ticket['professionList'])
    return {1: 'profession', 2: 'protocol', 4: 'coordination', 8: 'dispatch'}[size]


def source_rows(current):
    """Every explicitly mapped pair, never infer a candle suffix or ticket pool."""
    pairs = current['stashableTickets']
    if len(pairs) != 47 or len(current['recruitTickets']) != 94:
        raise ValueError('The pinned47 pairs and94 recruitment records are required')
    rows = []
    used = set()
    professions = dict(PROFESSIONS)
    for key, pair in pairs.items():
        original, stashed = pair['ticketId'], pair['stashedTicketId']
        if key != original or original == stashed or original in used or stashed in used:
            raise ValueError('Distinct exact original/stashed identities required')
        used.update((original, stashed))
        a, b = current['recruitTickets'][original], current['recruitTickets'][stashed]
        ia, ib = current['items'][original], current['items'][stashed]
        if a['id'] != original or b['id'] != stashed or ia['id'] != original or ib['id'] != stashed:
            raise ValueError('Full record identities differ')
        if ia['type'] != 'RECRUIT_TICKET' or ib['type'] != 'RECRUIT_TICKET':
            raise ValueError('Recruitment ticket items required')
        if {k: v for k, v in a.items() if k != 'id'} != {k: v for k, v in b.items() if k != 'id'}:
            raise ValueError('Original/stashed recruitment parameters differ')
        if ia['name'] != ib['name'] or ia['usage'] != ib['usage']:
            raise ValueError('Exact full item names and uses must agree')
        if not a['professionList'] or any(p not in professions for p in a['professionList']):
            raise ValueError('Unknown profession is not silently translated')
        stars = []
        for tier in a['rarityList']:
            if type(tier) is not str or not re.fullmatch(r'TIER_[1-6]', tier):
                raise ValueError('Unknown rarity is not silently translated')
            stars.append(int(tier[-1]))
        if len(set(stars)) != len(stars) or not stars:
            raise ValueError('Distinct explicit star ranges required')
        rows.append({
            'id': original, 'stashed_id': stashed, 'name': ia['name'],
            'family': family(original, a),
            'professions': deepcopy(a['professionList']), 'stars': stars,
            'original_item': deepcopy(ia), 'stashed_item': deepcopy(ib),
            'original_ticket': deepcopy(a), 'stashed_ticket': deepcopy(b),
            'pair': deepcopy(pair), 'actual_owned': None, 'actual_recruit': None,
        })
    if used != set(current['recruitTickets']):
        raise ValueError('All pinned recruitment records must be covered exactly once')
    return rows


def _read_public(name):
    if type(name) is not str:
        raise ValueError('Public relative path required')
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or rel.as_posix() != name:
        raise ValueError('Unsafe public path')
    path = ROOT.joinpath(*rel.parts)
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Linked public source refused')
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Linked public source parent refused')
    return path.read_bytes()


def packet():
    try:
        raw = _read_public(MANIFEST)
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        expected = {
            DATA, PACK + '/source-notes.json', PACK + '/source-download.json',
            PACK + '/documented-stashing.html', PACK + '/topic-page.html',
            'research/p3-expansion-313/current-topic.json',
            'rouge/data/current-exit.json', 'rouge/data/current-rest-travel.json',
            'research/p3-current-exit-339/runtime-manifest.json',
            'research/p3-current-rest-travel-331/runtime-manifest.json',
        }
        if manifest['schema'] != 'current_recruit_tickets_354_manifest_v1' or manifest['game_commit'] != version.NEW_COMMIT or set(manifest['files']) != expected:
            return None
        values = {}
        for name, pin in manifest['files'].items():
            content = _read_public(name)
            if type(pin['bytes']) is not int or len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']:
                return None
            values[name] = content
        data = json.loads(values[DATA])
        current = version.packet()
        if current is None or data['schema'] != 'current_recruit_tickets_354_v1' or data['game_commit'] != version.NEW_COMMIT:
            return None
        if data['complete_reward_pool'] is not False or data['rows'] != source_rows(current['current']['details']):
            return None
        constants = current['current']['details']['gameConst']
        if data['configuration_bounds'] != {k: constants[k] for k in ('recruitStashMinNum', 'recruitStashMaxNum')}:
            return None
        from . import current_exit as exit_model, current_rest_travel as rest_model
        source = {'exit': exit_model, 'rest': rest_model}
        for key, (cid, _) in LINKS.items():
            provider = source[key]
            source_packet = provider.packet()
            if source_packet is None:
                return None
            link = data['links'][key]
            if link['original_choice_id'] != cid or link['original_choice'] != current['current']['details']['choices'][cid]:
                return None
            if link['target'] != provider.locate('choices', cid):
                return None
            if link['source_identity'] != json.loads(json.dumps(source_packet['source_identity'])):
                return None
        if set(data['links']) != set(LINKS):
            return None
        return {
            'data': data, 'source_identity': (MANIFEST_SHA256, current['source_identity']),
            'actual_inventory': None, 'actual_owned': None, 'actual_recruited': None,
            'actual_cost': None, 'actual_random_result': None, 'run_updated': False,
        }
    except (OSError, ValueError, KeyError, TypeError, AttributeError, UnicodeError, RecursionError):
        return None


def reference(ticket_id=None, *, profession=None, ticket_family=None, query=''):
    if ticket_id is not None and type(ticket_id) is not str:
        return None
    if profession is not None and (type(profession) is not str or profession not in dict(PROFESSIONS)):
        return None
    if ticket_family is not None and (type(ticket_family) is not str or ticket_family not in dict(FAMILIES)):
        return None
    if type(query) is not str:
        return None
    result = packet()
    if result is None:
        return None
    rows = [deepcopy(row) for row in result['data']['rows']
            if (profession is None or profession in row['professions'])
            and (ticket_family is None or row['family'] == ticket_family)
            and (not query.strip() or query.strip() in row['name'])]
    selected = next((row for row in rows if row['id'] == ticket_id or row['stashed_id'] == ticket_id), None)
    if ticket_id is not None and selected is None:
        return None
    return {**result, 'rows': rows, 'selected': selected,
            'filters': {'profession': profession, 'family': ticket_family, 'query': query}}


def destination(kind):
    if type(kind) is not str or kind not in LINKS:
        return None
    result = packet()
    return deepcopy(result['data']['links'][kind]) if result else None


def player_text(result):
    lines = ['【招募券资料】', NOTICE, '',
             '【怎样看这份目录】',
             '按职业和券种分别筛选；多职业券会同时符合多个职业筛选，并不代表持有多张券。',
             '目录中的47项各有一份原券和一份明确对应的留存券；不是94种可同时领取的奖励。']
    row = result['selected']
    if row:
        stars = '、'.join(str(star) + '★' for star in row['stars'])
        names = dict(PROFESSIONS)
        lines += ['', '【'+row['name']+'】',
                  '可选职业：' + '、'.join(names[p] for p in row['professions']),
                  '资料列出的星级：' + stars,
                  '完整用途：' + version._plain(row['original_item']['usage']),
                  '', '【原券与留存券】',
                  '名称和用途相同，但它们是两份不同的原始条目；配对由资料明确给出。',
                  '两份招募参数一致，并不表示随机人选、直升或临时招募状态被保存。',
                  '本局持有张数、是否已取出、具体干员、希望花费及最终培养：未知。']
        if '直升' in row['original_item']['usage'] or '直升' in row['name']:
            lines += ['“直升”表示初次招募即相当于已经进阶；本页不据此填写具体等级或技能培养。']
    else:
        lines += ['', '请选择一张券，查看它自己的职业、星级和完整用途。']
    lines += ['', '【留存与取出规则】',
              '初始招募阶段不能留存招募券。留存后的券可在险路尽头取出；安全的角落还需要点亮生命游戏的“血管”。',
              '初始留存上限为3张；满额时不能继续留存，也不能用新券替换旧券。',
              '取出后的招募券不能再次存入。券中的随机效果在取出时重新判定，包括随机直升、人选和临时招募出现状态。',
              '当前配置另外记有1与15的数值边界；它们不是本局容量，也不能把15解释成初始上限。实际容量仍受本局条件影响。',
              '', '【查看实际节点的原文】',
              '可分别打开“召集同伴”和“尝试发出求援信号”的准确选项。它们是使用已有留存券，不是领取新券。',
              '安全的角落中该项是否占用随机菜单名额、完整服务器资格、实际库存与发放过程尚未核实。',
              '', '【资料范围】',
              '券种来自固定bee3国服资料；留存规则另由PRTS固定修订442954核对。文献说明不证明当前服务器已执行。',
              '本页只供局外查阅，不招募、不花费希望、不保存或清空本局；不提供路线推荐、候选出现概率或随机结果预测。']
    return '\n'.join(lines)
