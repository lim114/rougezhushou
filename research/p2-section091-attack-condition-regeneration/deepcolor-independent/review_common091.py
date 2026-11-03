"""Independent strict serialization and note-inverse helpers; standard library only."""
import copy
import hashlib
import json
import re

QUALIFICATION = '以上为所选触手持续在场且技能回复持续覆盖时的速度参考，包含本次采用的生命回复效果倍率；实际在场、回复首跳和结束尚未核验，实际回复总量未知。'
NOTE = re.compile(r'^触手数量 (?P<count>\S+)（局外假设）；(?P<scope>名义技能持续参数 (?P<nominal>\S+) 秒|观察窗口中 (?P<observed>\S+) 秒的名义技能覆盖假设)下，按基础每只 (?P<rate>\S+) 生命/秒连续覆盖的回复参考 (?P<total>\S+)（未计生命回复效果倍率）；实际触手在场、技能回复覆盖及时钟未核验，实际回复总量未知，生命回复不计直接治疗。$')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def native(value):
    if value is None: return ['none']
    if type(value) is bool: return ['bool', value]
    if type(value) is int: return ['int', str(value)]
    if type(value) is float: return ['float', value.hex()]
    if type(value) is str: return ['str', value]
    if type(value) is list: return ['list', [native(v) for v in value]]
    if type(value) is tuple: return ['tuple', [native(v) for v in value]]
    if type(value) is dict: return ['dict', [[native(k), native(v)] for k, v in value.items()]]
    raise TypeError(type(value).__name__)


def decode(tree):
    assert isinstance(tree, list) and tree
    kind = tree[0]
    if kind == 'none':
        assert tree == ['none']; value = None
    elif kind == 'bool':
        assert len(tree) == 2 and type(tree[1]) is bool; value = tree[1]
    elif kind == 'int':
        assert len(tree) == 2 and isinstance(tree[1], str); value = int(tree[1])
    elif kind == 'float':
        assert len(tree) == 2 and isinstance(tree[1], str); value = float.fromhex(tree[1])
    elif kind == 'str':
        assert len(tree) == 2 and isinstance(tree[1], str); value = tree[1]
    elif kind in ('list', 'tuple'):
        assert len(tree) == 2 and isinstance(tree[1], list)
        values = [decode(item) for item in tree[1]]
        value = values if kind == 'list' else tuple(values)
    elif kind == 'dict':
        assert len(tree) == 2 and isinstance(tree[1], list)
        value = {}
        for pair in tree[1]:
            assert isinstance(pair, list) and len(pair) == 2
            key, item = decode(pair[0]), decode(pair[1])
            assert key not in value
            value[key] = item
    else:
        raise ValueError(kind)
    assert native(value) == tree, 'Native decode must preserve exact type, float.hex and dict order'
    return value


def inverse(result):
    result = copy.deepcopy(result)
    substitutions = []
    notes = []
    for note in result['estimate']['notes']:
        match = NOTE.fullmatch(note)
        if match:
            old = f'触手数量 {match["count"]}；技能生命回复 {match["total"]}，生命回复不计直接治疗。'
            substitutions.append({'new': note, 'old': old, 'scope': match['scope'],
                                  'base_rate': match['rate'], 'base_reference_total': match['total']})
            notes.append(old)
        else:
            notes.append(note)
    # Original Combat.calculate line1545 deduplicates identical full/shown notes.
    result['estimate']['notes'] = list(dict.fromkeys(notes))
    report_qualification_count = 0
    for block in result['report']['sections']:
        if block['id'] == 'regeneration':
            report_qualification_count += block['notes'].count(QUALIFICATION)
            block['notes'] = [note for note in block['notes'] if note != QUALIFICATION]
    return result, substitutions, report_qualification_count
