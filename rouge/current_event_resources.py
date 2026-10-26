"""Find explicit documented resource changes without computing a whole-run result."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json, re
from . import current_event_directory as directory
ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-event-resources-374'; DATA = 'rouge/data/current-event-resources.json'
NOTES = PACK + '/source-notes.json'; MANIFEST = PACK + '/runtime-manifest.json'; MANIFEST_SHA256 = 'fba199d073730919c677e6a359ebe2ad2ef07d801db2d6b1b10885d764be7a2c'
RESOURCES = (('gold', '源石锭'), ('hope', '希望'), ('life', '目标生命值'), ('max_life', '目标生命值上限'),
             ('shield', '护盾'), ('ap', '行动力'), ('carry', '可携带干员数'), ('weight', '零件箱容量'),
             ('relic', '收藏品'), ('processed', '加工品'), ('concept', '概念体'), ('natural', '自然物'), ('part', '零件'))
KINDS = (('gain', '获得或回复'), ('cost', '需要付出的代价'), ('item', '数量明确的物品奖励'))
NOTICE = '按已核对的事件原文查资源变化；不同选项、对话阶段和随机结果分别保留，不合计成总收益。'
UNAVAILABLE = '事件资源变化的资料暂时无法核对，旧条目、原文和所属流程已清除；恢复后请重新选择。'
_NAMES = {'源石锭': 'gold', '希望': 'hope', '目标生命值': 'life', '目标生命': 'life', '目标生命值上限': 'max_life',
          '目标生命上限': 'max_life', '护盾': 'shield', '行动力': 'ap', '收藏品': 'relic', '加工品': 'processed',
          '概念体': 'concept', '自然物': 'natural', '零件': 'part'}


def extract(text):
    effects = []; occupied = []
    scalar = r'(源石锭|希望|目标生命值上限|目标生命上限|目标生命值|目标生命|护盾|行动力)'
    for match in re.finditer(r'(获得|回复|消耗|失去|扣除)(\d+|一半|全部)(?:的)?' + scalar, text):
        verb, raw, name = match.groups(); kind = 'gain' if verb in ('获得', '回复') else 'cost'
        effects.append({'kind': kind, 'resource': _NAMES[name], 'quantity': int(raw) if raw.isdecimal() else None,
                        'amount_rule': 'fixed' if raw.isdecimal() else 'half' if raw == '一半' else 'all',
                        'original_verb': verb, 'literal': match.group(0), 'quality': None, 'complete_pool': None})
        occupied.append(match.span())
    for match in re.finditer(r'(可携带干员|零件箱容量)([+＋-－])(\d+)', text):
        noun, sign, raw = match.groups()
        effects.append({'kind': 'gain' if sign in ('+', '＋') else 'cost', 'resource': 'carry' if noun == '可携带干员' else 'weight',
                        'quantity': int(raw), 'amount_rule': 'fixed', 'original_verb': '增加' if sign in ('+', '＋') else '减少',
                        'literal': match.group(0), 'quality': None, 'complete_pool': None})
    for match in re.finditer(r'获得(\d+)件(珍贵的|珍贵|随机)?(收藏品|加工品|概念体|自然物|零件)', text):
        raw, modifier, noun = match.groups()
        effects.append({'kind': 'item', 'resource': _NAMES[noun], 'quantity': int(raw), 'amount_rule': 'fixed',
                        'original_verb': '获得', 'literal': match.group(0), 'quality': '珍贵' if modifier and '珍贵' in modifier else None,
                        'complete_pool': None})
    if '消耗全部行动力，转化为等量希望' in text:
        effects.append({'kind': 'gain', 'resource': 'hope', 'quantity': None, 'amount_rule': 'equal_spent_ap',
                        'original_verb': '转化', 'literal': '消耗全部行动力，转化为等量希望', 'quality': None, 'complete_pool': None})
    return effects


def derive(reference):
    rows = []
    for event in reference['data']['rows']:
        for entry in event['entries']:
            effects = extract(entry['description'])
            if not effects: continue
            rows.append({'id': entry['key'], 'event_id': event['id'], 'event_title': event['title'],
                         'reader': event['reader'], 'entry': deepcopy(entry), 'effects': effects,
                         'actual_eligible': None, 'actual_received': None, 'actual_consumed': None})
    return {'schema': 'current_event_resources_374_v1', 'rows': rows, 'source_event_count': len(reference['data']['rows']),
            'source_occurrence_count': sum(len(r['entries']) for r in reference['data']['rows']),
            'directory_source_identity': json.loads(json.dumps(reference['source_identity'])),
            'complete_reward_pool_known': False, 'actual_net_change': None, 'run_updated': False}


def packet():
    try:
        raw = (ROOT / MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {DATA, NOTES, directory.DATA, directory.MANIFEST, 'rouge/current_event_directory.py'}
        if manifest['schema'] != 'current_event_resources_374_manifest_v1' or set(manifest['files']) != expected: return None
        blobs = {}
        for name, pin in manifest['files'].items():
            rel = Path(name); path = ROOT / name
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()): return None
            if any(parent.is_symlink() for parent in path.parents if parent != ROOT and ROOT in parent.parents): return None
            data = path.read_bytes()
            if type(pin['bytes']) is not int or len(data) != pin['bytes'] or sha256(data).hexdigest() != pin['sha256']: return None
            blobs[name] = data
        base = directory.packet()
        if base is None: return None
        data = json.loads(blobs[DATA])
        if not directory.same(data, derive(base)): return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, base['source_identity']),
                'version_source_identity': base['version_source_identity'], 'actual_eligible': None,
                'actual_net_change': None, 'run_updated': False}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, UnicodeError, RecursionError): return None


def reference(identity=None, *, resource=None, kind=None, query=''):
    if identity is not None and type(identity) is not str: return None
    if resource is not None and (type(resource) is not str or resource not in dict(RESOURCES)): return None
    if kind is not None and (type(kind) is not str or kind not in dict(KINDS)): return None
    if type(query) is not str or len(query) > 160: return None
    p = packet()
    if p is None: return None
    rows = []; needle = query.strip().casefold()
    for original in p['data']['rows']:
        relevant = [e for e in original['effects'] if (resource is None or e['resource'] == resource) and (kind is None or e['kind'] == kind)]
        if not relevant: continue
        text = original['event_title'] + '\n' + original['entry']['title'] + '\n' + original['entry']['description']
        if needle and needle not in text.casefold(): continue
        row = deepcopy(original); row['matching_effects'] = deepcopy(relevant); rows.append(row)
    selected = next((r for r in rows if r['id'] == identity), None)
    if identity is not None and selected is None: return None
    return {**p, 'rows': rows, 'selected': selected, 'filters': {'resource': resource, 'kind': kind, 'query': query}}


def destination(result):
    if type(result) is not dict or result.get('selected') is None: return None
    row = result['selected']; fresh = reference(row['id'], **result['filters'])
    if fresh is None or not directory.same(fresh, result): return None
    base = directory.reference(row['event_id'])
    if base is None or not directory.same(json.loads(json.dumps(base['source_identity'])), result['data']['directory_source_identity']): return None
    return directory.resolve(base, row['entry']['key'])


def _amount(effect):
    rule = effect['amount_rule']
    if rule == 'half': return '原文为一半；取整和实际底限未核验'
    if rule == 'all': return '原文为全部；实际数量未确认'
    if rule == 'equal_spent_ap': return '与本次消耗的全部行动力等量；实际数量未确认'
    unit = '件' if effect['kind'] == 'item' else '人' if effect['resource'] == 'carry' else '点容量' if effect['resource'] == 'weight' else ''
    return str(effect['quantity']) + unit


def player_text(result):
    lines = [NOTICE, '筛选只帮助找资料，选中一项后仍显示它全部有证据的代价和奖励。']
    row = result['selected']
    if row is None:
        lines += ['', '已从' + str(result['data']['source_event_count']) + '份事件文献中的' + str(result['data']['source_occurrence_count']) + '处选项/结果里核对原文明示数值。',
                  '没有明确数字的具名物品、只写在叙述中的结果和完整随机池不补算。',
                  '先选需要查找的资源和获得/代价方向，再选一条准确记录。']
        return '\n'.join(lines)
    lines += ['', '【事件】' + row['event_title'], '【查阅位置】' + row['entry']['scene_label'],
              '【选项或结果】' + row['entry']['title'], row['entry']['description'], '', '【本条文献中的变化】']
    for effect in row['effects']:
        label = '代价' if effect['kind'] == 'cost' else '物品奖励' if effect['kind'] == 'item' else '获得或回复'
        lines += [label + ' · ' + dict(RESOURCES)[effect['resource']] + '：' + _amount(effect) + ('；品质注明珍贵' if effect['quality'] else '') + '。']
        if effect['kind'] == 'cost' and effect['resource'] == 'life' and '至少保留1目标生命值' in row['entry']['description']:
            lines += ['这项同时注明至少保留1目标生命值；上面是原文名义代价，不当作生命不足时仍无条件扣满。']
        if effect['kind'] == 'item': lines += ['只确认原文数量和类别；具体名单、品质分布和实际领取未知。']
    if row['entry']['presentation'] == 'outcome_reference' or row['entry']['actual_game_button'] is False:
        lines += ['', '这条是文献记载的结果参考，不能当成玩家可以挑选的游戏按钮。']
    lines += ['', '【不要混算】目标生命值、生命上限和护盾分开；它们不会互相折算。',
              '同名选项、不同阶段和互斥奖励不相加；未列出的修正不当作零，也不输出猜测净收益。',
              '这里的数值是原文变化，不是已经结算后的本局面板。完整出现前置、实际支付、随机池和服务器执行仍需核对。',
              '可打开准确的原事件对话，继续核对已列条件；不操作游戏、不领奖、不扣资源、不改本局或推荐路线。']
    return '\n'.join(lines)

