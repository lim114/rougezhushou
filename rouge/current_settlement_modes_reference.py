"""Documented base/full-technology reward modes with explicit entry context."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

from . import current_settlement_reference as prior

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-settlement-modes-362'
DATA = 'rouge/data/current-settlement-modes-reference.json'
HTML = 'research/p3-current-recruit-tickets-354/topic-page.html'
DOWNLOAD = 'research/p3-current-recruit-tickets-354/source-download.json'
EXCERPTS = PACK + '/documented-settlement-442954.json'
NOTES = PACK + '/source-notes.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '132c9a1772267547c59ce0cf27cfb47712cf1294a40fac17676d670ea309bb70'
ENTRIES = prior.ENTRIES
REGIONS = prior.REGIONS
UNAVAILABLE = '结算分项资料暂时无法核对，旧数值已清除；来源恢复后请重新核对入口和区域。'


def _file(name):
    if type(name) is not str:
        raise ValueError('Public path required')
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name or relative.as_posix() != name:
        raise ValueError('Unsafe source path')
    path = ROOT.joinpath(*relative.parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Regular in-root source required')
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Linked source parent refused')
    return path


def packet():
    try:
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        if (manifest['schema'] != 'current_settlement_modes_362_manifest_v1'
                or set(manifest['files']) != {DATA, HTML, DOWNLOAD, EXCERPTS, NOTES}):
            return None
        values = {}
        for name, pin in manifest['files'].items():
            body = _file(name).read_bytes()
            if type(pin['bytes']) is not int or len(body) != pin['bytes'] or sha256(body).hexdigest() != pin['sha256']:
                return None
            values[name] = body
        receipt = json.loads(values[DOWNLOAD])
        if (receipt['http_status'] != 200 or receipt['sha256'] != sha256(values[HTML]).hexdigest()
                or receipt['bytes'] != len(values[HTML]) or receipt['file'] != HTML):
            return None
        previous = prior.packet()
        if previous is None:
            return None
        data = json.loads(values[DATA])
        stages = previous['directory']['data']['rows']
        for row in data['special_battle_table']:
            identities = [key for key, item in stages.items() if item['original_stage']['difficulty'] == row['difficulty']
                          and any(item['original_stage']['code'] == link['code'] and item['original_stage']['name'] == link['name']
                                  for link in row['links'])]
            if identities != row['stage_ids']:
                return None
        return {'data': data, 'directory': previous['directory'],
                'source_identity': (MANIFEST_SHA256, previous['source_identity'], previous['directory']['source_identity']),
                'actual_reward_total': None, 'inventory_updated': False}
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, AttributeError):
        return None


def stage_reference(stage_id, entry='unknown', region='catalog'):
    if type(entry) is not str or type(region) is not str or entry not in dict(ENTRIES) or region not in dict(REGIONS):
        raise ValueError('入口或区域尚未支持。')
    if type(stage_id) is not str:
        return None
    source = packet()
    if source is None:
        return None
    info = prior.directory.detail(stage_id, reference=source['directory'])
    if info is None:
        return None
    stage = info['row']
    original = stage['original_stage']
    data = source['data']
    rows = []

    def add(rule, label, required, region_match=True):
        matches = None if entry == 'unknown' else entry == required
        status = ('not_matched' if matches is False or region_match is False else
                  'unknown' if matches is None or region_match is None else 'listed_matched')
        rows.append({'label': label, 'required_entry': required, 'entry_matches': matches,
                     'region_matches': region_match, 'status': status, 'rule': deepcopy(rule), 'actual_received': None})

    floor = 'source0' if stage['region'] == '源流交汇处' else stage['floor'] if stage['region'] == '主要区域' else None
    if stage['play_kind'] in ('normal', 'emergency', 'boss'):
        for kind in [stage['play_kind']] + (['boss_pursuit'] if stage['play_kind'] == 'boss' else []):
            rule = data['main_floor_table'].get(floor, {}).get(kind)
            if rule is None:
                rule = {'base_gold': None, 'experience_modes': {'base': None, 'full_technology': None},
                        'source_missing_reason': '当前表未列这个区域的对应基础奖励；不能借用同层另一特殊区域。'}
            region_match = True if region == 'catalog' else True if region == 'portal' and kind in ('normal', 'emergency') else None
            label = ('普通或紧急作战的通关基础分项' if kind in ('normal', 'emergency') else
                     '险路恶敌追猎的基础分项' if kind == 'boss_pursuit' else '险路恶敌的通关基础分项')
            add(rule, label, 'boss_pursuit' if kind == 'boss_pursuit' else 'map', region_match)
    for rule in data['special_battle_table']:
        if stage_id in rule['stage_ids']:
            add(rule, '具名特殊入口的通关分项', 'event', True if region == 'catalog' else None)
    if stage['kind'] == 'pursuit' and original['isBoss'] == 0:
        add(data['ordinary_pursuit'], '通常追猎的通关基础分项', 'pursuit', True if region == 'catalog' else None)
    if not rows:
        add({'base_gold': None, 'experience_modes': {'base': None, 'full_technology': None},
             'source_missing_reason': '当前结算表没有这个具名关卡的专门条目，不按同名或共用地图补数。'},
            '基础奖励尚未核实', 'event' if stage['kind'] in ('challenge', 'duck', 'duel', 'resident', 'shop') else 'map', None)
    applicable = [row for row in rows if row['status'] != 'not_matched']
    qualified = bool(applicable) and all(row['status'] == 'listed_matched' for row in applicable)

    def consistent(values):
        return deepcopy(values[0]) if qualified and values and values[0] is not None and all(value == values[0] for value in values) else None

    base = consistent([r['rule']['experience_modes']['base'] for r in applicable])
    full = consistent([r['rule']['experience_modes']['full_technology'] for r in applicable])
    coins = consistent([r['rule']['base_gold'] for r in applicable])
    bonus = deepcopy(data['documented_side_path_bonus']) if region == 'side_path' and entry == 'map' and stage['play_kind'] == 'normal' else None
    return {'stage_id': stage_id, 'stage_name': stage['name'], 'stage_grouping': info,
            'entry_declared': entry, 'region_declared': region, 'rows': rows,
            'conditional_base_gold': coins, 'conditional_base_experience': base,
            'conditional_full_technology_experience': full,
            'conditional_current_experience': None,
            'actual_player_technology': None, 'documented_side_path_bonus': bonus,
            'source_identity': source['source_identity'], 'source': data['source'],
            'covered_document_modes_verified': True, 'all_current_stage_rewards_known': False,
            'actual_reward_total': None, 'complete_reward_pool_known': False, 'inventory_updated': False,
            'actual_victory_verified': False, 'actual_entry_verified': False, 'reward_modifiers_applied': False}


def xp(value):
    return '未知' if value is None else str(value) + ' 点'


def player_text(result):
    labels = {'unknown': '入口或区域尚未确认', 'not_matched': '与声明的入口或区域不符',
              'listed_matched': '已列条件相符；实际通关和结算仍未确认'}
    lines = [result['stage_name'], '', '【符合所选入口与区域时】',
             '基础指挥经验：' + xp(result['conditional_base_experience']) + '。',
             '满级生命游戏的经验参考：' + xp(result['conditional_full_technology_experience']) + '。',
             '基础源石锭：' + prior.amount(result['conditional_base_gold']) + '。',
             '两种经验是分别展示的数值，不能相加；没有假定你的科技已点满。',
             '完整实际奖励：未知。保密等级、分队、收藏品等其它修正尚未合入。']
    for row in result['rows']:
        rule = row['rule']
        values = rule['experience_modes']
        lines += ['', '【' + row['label'] + '】', labels[row['status']],
                  '适用入口：' + dict(ENTRIES)[row['required_entry']],
                  '资料中的经验：基础 ' + xp(values['base']) + '；满级生命游戏 ' + xp(values['full_technology']) + '。',
                  '基础源石锭：' + prior.amount(rule['base_gold']) + '。']
        if rule.get('recruit_ticket_reference') is not None:
            lines += ['通常追猎的资料注明：没有经验、源石锭或收藏品报酬，只掉落1张招募券；券种和实际领取未知。',
                      '不能将这一条套用到同名事件战斗或险路恶敌追猎。']
        if rule.get('links'):
            lines += ['具名文献：' + '、'.join(link['name'] for link in rule['links']) + '。',
                      '同名配置仍各自保留，实际使用哪份配置和能否进入仍未核验。']
        if rule.get('source_missing_reason'):
            lines.append(rule['source_missing_reason'])
    if result['region_declared'] == 'portal':
        lines += ['', '秘境仅沿用文献明确的普通/紧急所属关卡分项；秘境编号不是作战所属主层。']
    if result['region_declared'] == 'side_path':
        lines += ['', '熄日余径的基础结算仍未知，不按下一层或关卡编号套算。']
    if result['documented_side_path_bonus']:
        lines += ['已列额外分项：完成普通作战节点后另有1件随机收藏品；完整候选池和实际领取未知。']
    lines += ['', '【怎么看这两种经验】', '“基础”不计经验加成；“满级生命游戏”是网页单列的参考模式。',
              '这里直接读取各自的原数值，没有从合并数字拆分，也没有推测满科技倍率或实际奖励计算次序。',
              '当前玩家科技、完整额外奖励、无漏怪等条件和服务器实际发放仍需核对。',
              '', '【来源】已保存的PRTS修订442954完整网页，配合固定国服关卡目录；不是本局结算实测。',
              result['source']['fixed_url']]
    return '\n'.join(lines)
