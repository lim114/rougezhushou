"""Player wording for one explicitly supplied fixed map tile, never battle state.

Names and parameter meanings are bound to the public evidence recorded in
research/p3-current-terrain-353/source-notes.json.  This pure decoder does not
read another tile, use a stage default, pair passages, or apply an effect.
"""
from decimal import Decimal
from math import isfinite
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='research/p3-current-terrain-353/runtime-manifest.json'
MANIFEST_SHA256='afcf5b6c0d1669d01e83f4819887aa4fa2aaadef644e3e83b7e03402ada3ada4'


def evidence_identity():
    """Fail closed on actual evidence loss, including after a warm read."""
    try:
        path=ROOT/MANIFEST
        if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
        raw=path.read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        packet=json.loads(raw)
        if packet['schema']!='current_terrain_353_evidence_v1':return None
        for name,pin in packet['files'].items():
            path=ROOT/name
            if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
            if any(parent.is_symlink()for parent in path.parents if parent!=ROOT and ROOT in parent.parents):return None
            data=path.read_bytes()
            if len(data)!=pin['bytes']or sha256(data).hexdigest()!=pin['sha256']:return None
        return MANIFEST_SHA256
    except(OSError,ValueError,KeyError,TypeError,UnicodeError):return None


BWIKI = 'https://wiki.biligame.com/arknights/地形?oldid=352021'
BASIC = 'https://prts.wiki/index.php?title=基本地形&oldid=428351'
WALL = 'https://prts.wiki/index.php?title=围墙&oldid=428434'
FORMAT = 'https://prts.wiki/w/特殊地形/trapper/tilesformat.json'
NOTES = 'research/p3-current-terrain-353/source-notes.json'

# A legend's colors are presentation choices, not measured colors in the game.
_TYPES = {
    'tile_forbidden': ('禁入区', '禁', '#353a43', 'blocked'),
    'tile_road': ('平地', '地', '#a1a7b0', 'ground'),
    'tile_wall': ('高台', '高', '#8e88ae', 'highland'),
    'tile_floor': ('不可放置位', '禁放', '#747b84', 'ground'),
    'tile_start': ('侵入点', '入口', '#d56161', 'entry'),
    'tile_end': ('保护目标', '目标', '#638ed5', 'goal'),
    'tile_hole': ('地穴', '穴', '#39324b', 'hazard'),
    'tile_fence_bound': ('围墙', '围墙', '#9f8c77', 'blocked'),
    'tile_telin': ('通道入口', '通入', '#a078c4', 'passage'),
    'tile_telout': ('通道出口', '通出', '#bc91d8', 'passage'),
    'tile_volcano': ('热泵通道', '热泵', '#d48d61', 'hazard'),
    'tile_empty': ('占位地块', '占位', '#424953', 'placeholder'),
    'tile_flystart': ('空袭侵入点', '空入', '#d68c88', 'entry'),
    'tile_grass': ('草丛', '草', '#73a878', 'cover'),
    'tile_ftstart': ('假侵入点', '假入', '#cba06c', 'entry'),
    'tile_infection': ('活性源石', '源石', '#bb646f', 'hazard'),
    'tile_bigforce': ('特种战术点', '战术', '#8ba5ba', 'tactical'),
    'tile_healing': ('医疗符文', '医疗', '#67ac9e', 'healing'),
    # The exact suffix is not documented by either retained name table.
    'tile_pollution_roadf': ('特殊地形（名称未核实）', '未证', '#85858e', 'unknown'),
}
KNOWN_TILE_KEYS = tuple(_TYPES)

_GENERAL = {
    'tile_start': '敌人侵入点标记；具体来敌与条件应查看本关出怪条目，不能仅凭红门认定必有敌人。',
    'tile_end': '需要保护的目标标记；实际生命扣除还取决于进入的单位与关卡规则。',
    'tile_hole': '危险的凹陷地形；符合坠落条件的敌人可能掉落，特殊单位或关卡机制须另行核对。',
    'tile_telin': '资料中的通道入口；经过通道的敌人会从相应出口再度出现。',
    'tile_telout': '资料中的通道出口；它对应哪个入口，须以准确路线或关卡机制为准。',
    'tile_grass': '部署在草丛中的干员不会成为敌方远程攻击的目标；这不等于免疫范围伤害或所有技能。',
    'tile_ftstart': '资料称作假侵入点；它与对应敌人或装置的关系由关卡机制决定，不能按普通侵入点推定。',
    'tile_empty': '资料中的占位地块；实际部署与通行标注分别查看本格原记录。',
    'tile_healing': '为部署在其上的干员持续回复生命；下列数值只来自这一格的明确参数。',
    'tile_infection': '部署其上的我方单位及经过的敌方单位获得攻速和攻击力变化，同时持续受到真实伤害；数值仅解释本格。',
    'tile_bigforce': '部署在其上的我方单位推动或拉动敌人时，力度发生变化；不代表能推动所有敌人。',
    'tile_volcano': '间隔喷出高温气体，对地块上的单位造成真实伤害；本页不推算首次喷发或实际命中。',
}


def _number(value):
    if type(value) not in (int, float):
        return False
    try:
        return isfinite(value)
    except (OverflowError, TypeError):
        return False


def _text(value, multiplier=1):
    number = Decimal(str(value)) * multiplier
    result = format(number, 'f')
    return result.rstrip('0').rstrip('.') if '.' in result else result


def _change(value, unit='', multiplier=1):
    direction = '增加' if value >= 0 else '减少'
    return direction + _text(abs(value), multiplier) + unit


def _parameters(tile, expected, unknowns):
    """Invalid or duplicate entries never become a default or a numeric effect."""
    raw = tile.get('blackboard')
    if raw is None:
        return {}
    if type(raw) is not list:
        unknowns.append('本格附带参数格式异常，不能解释其中的数值。')
        return {}
    values = {}
    seen = set()
    invalid = set()
    extra = False
    for row in raw:
        if type(row) is not dict or type(row.get('key')) is not str:
            unknowns.append('本格有格式异常的附带参数，未作为效果使用。')
            continue
        key = row['key']
        if key in seen:
            invalid.add(key)
            values.pop(key, None)
        seen.add(key)
        if key not in expected:
            extra = True
            continue
        if key in invalid:
            continue
        value = row.get('value')
        if not _number(value) or row.get('valueStr') not in (None, ''):
            invalid.add(key)
        else:
            values[key] = value
    if invalid.intersection(expected):
        unknowns.append('本格存在重复或异常的相关数值；有歧义的参数保持未知。')
    if extra:
        unknowns.append('本格还列有未解释的附带参数；本页没有把它们套用到已知效果。')
    return values


def terrain_info(tile):
    """Return fresh player-facing metadata; unknown inputs cannot infer effects.

    ``tile`` is a single original ``mapData.tiles`` declaration.  The caller
    retains responsibility for binding it to the correct stage and grid cell.
    ``source_refs`` names documentary sources, not a claim of live verification.
    """
    key = tile.get('tileKey') if type(tile) is dict else None
    known = type(key) is str and key in _TYPES
    name, short, color, kind = _TYPES[key] if known else (
        '未识别的地形', '未知', '#85858e', 'unknown')
    result = {'name': name, 'short_label': short, 'color': color, 'kind': kind,
              'effects': [], 'unknowns': [], 'source_refs': [NOTES]}
    effects, unknowns = result['effects'], result['unknowns']
    if not known:
        unknowns.append('这份地形名称或格式尚未取得准确对应，不借用相似名称或其它地块的效果。')
        return result
    if key == 'tile_pollution_roadf':
        unknowns.append('已保留这类原始地块，但尚未取得准确中文名称与效果依据；不能仅凭名称片段认定为源石污染区。')
        return result
    result['source_refs'] += [BWIKI]
    if key in ('tile_road', 'tile_wall', 'tile_floor', 'tile_forbidden',
               'tile_start', 'tile_end', 'tile_telin', 'tile_telout',
               'tile_flystart', 'tile_empty'):
        result['source_refs'].append(BASIC)
    if key == 'tile_fence_bound':
        result['source_refs'].append(WALL)
        unknowns.append('固定PRTS资料称围墙，BWIKI总表称围栏；本页保留这项称呼差异，不将它与另一种围栏原件合并。')
    if key in _GENERAL:
        effects.append(_GENERAL[key])
    if key in ('tile_telin', 'tile_telout'):
        unknowns.append('本页未证明本关通道的成对连接、实际通过或出现时刻，不按编号或距离自行连线。')
    if key == 'tile_ftstart':
        unknowns.append('是否释放敌人、转化条件和当前状态没有由单个地块记录证明。')

    expected = {
        'tile_healing': {'HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO'},
        'tile_infection': {'damage', 'duration', 'atk', 'attack_speed'},
        'tile_bigforce': {'base_force_level'},
        'tile_volcano': {'damage', 'cd_min', 'cd_max'},
    }.get(key, set())
    values = _parameters(tile, expected, unknowns)
    if expected:
        result['source_refs'].append(FORMAT)
        def read(parameter, label, *, nonnegative=False):
            value = values.get(parameter)
            if value is None or (nonnegative and value < 0):
                unknowns.append(label + '：本格未给出可用数值，不套用常见默认值。')
                return None
            return value
        if key == 'tile_healing':
            value = read('HP_RECOVERY_PER_SEC_BY_MAX_HP_RATIO', '每秒生命回复比例', nonnegative=True)
            if value is not None:
                effects.append('每秒回复：干员最大生命值的' + _text(value, 100) + '%。')
        elif key == 'tile_infection':
            duration = read('duration', '效果持续时间', nonnegative=True)
            damage = read('damage', '每秒真实伤害', nonnegative=True)
            attack = read('atk', '攻击力变化')
            speed = read('attack_speed', '攻击速度变化')
            if duration is not None:
                effects.append('本格配置的效果持续时间：' + _text(duration) + '秒。')
            if damage is not None:
                effects.append('每秒受到：' + _text(damage) + '点真实伤害。')
            if attack is not None:
                effects.append('攻击力：' + _change(attack, '%', 100) + '。')
            if speed is not None:
                effects.append('攻击速度：' + _change(speed, '（游戏攻速单位）') + '。')
        elif key == 'tile_bigforce':
            value = read('base_force_level', '推拉力度变化')
            if value is not None:
                if int(value) != value:
                    unknowns.append('推拉力度参数不是整数等级，未解释为已确认力度效果。')
                else:
                    effects.append('推动或拉动力度：' + _change(value, '个等级') + '。')
        else:
            damage = read('damage', '每次真实伤害', nonnegative=True)
            lower = read('cd_min', '最短喷发间隔', nonnegative=True)
            upper = read('cd_max', '最长喷发间隔', nonnegative=True)
            if damage is not None:
                effects.append('每次喷发伤害：' + _text(damage) + '点真实伤害。')
            if lower is not None and upper is not None:
                if lower <= upper:
                    interval = _text(lower) if lower == upper else _text(lower) + '至' + _text(upper)
                    effects.append('本格配置的喷发间隔：' + interval + '秒。')
                else:
                    unknowns.append('喷发间隔上下限倒置，不能作为可用间隔。')
        unknowns.append('这是单格固定资料，不代表本局已生效；首次生效、重新触发、结束时刻与最终面板仍须另行核对。')
    if tile.get('effects') not in (None, []):
        unknowns.append('本格另有附加效果声明，本页尚未解释，不能当作已经完整覆盖。')
    return result

