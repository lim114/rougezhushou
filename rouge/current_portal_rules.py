"""Nine documentary portal rules, without choosing a region or changing a run."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-portal-rules-358'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = 'ca804fa40e1373a023ec5e79cb72dfed1a260d4425d27a1dd4945746cc75a5f3'
NOTICE = ('乌托邦是误入奇境后的区域规则。本页查阅固定资料和社区补充，不代表本局已进入、'
          '已刷新或已获奖励；不读取战斗站位，不推荐路线，不修改本局或计算。')
UNAVAILABLE = '秘境规则资料无法核对；旧雾色、规则、原区域表和资料入口已清除，请在恢复后重新选择。'
FOGS = ('红雾', '蓝雾', '绿雾', '金雾', '橙雾', '紫雾')


def _same(left, right):
    if type(left) is not type(right): return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(_same(left[k], right[k]) for k in left)
    if type(left) in (list, tuple):
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    return left == right


def packet():
    try:
        raw = version._file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {PACK + '/' + name for name in (
            'reference-data.json', 'source-notes.json', 'source-reuse.json',
            'database-utopia-section.html', 'main-portal-section.html')}
        if (manifest['schema'] != 'current_portal_rules_358_manifest_v1'
                or manifest['game_commit'] != version.NEW_COMMIT
                or set(manifest['files']) != expected): return None
        blobs = {}
        for name, pin in manifest['files'].items():
            content = version._file(name).read_bytes()
            if type(pin['bytes']) is not int or len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']:
                return None
            blobs[name] = content
        data = json.loads(blobs[PACK + '/reference-data.json'])
        current = version.packet()
        if current is None or data['schema'] != 'current_portal_rules_358_v1': return None
        source = current['current']['details']
        if set(data['rules']) != set(source['variationData']) or len(data['rules']) != 9: return None
        if tuple(data['fogs']) != FOGS: return None
        if any(not _same(row['original'], source['variationData'][key]) for key, row in data['rules'].items()): return None
        if not _same(data['original_roll_node_data'], source['rollNodeData']): return None
        if not _same(data['original_nodes'], source['nodeTypeData']): return None
        if any(not _same(value, source['zones'].get(key)) for key, value in data['original_portal_zones'].items()): return None
        if any(not _same(value, source['items'].get(key)) for key, value in data['original_items'].items()): return None
        if any(not _same(value['original'], source['choiceScenes'].get(key))
               for key, value in data['original_enter_scenes'].items()): return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, current['source_identity']),
                'actual_current_rule': None, 'actual_refreshed_nodes': None,
                'actual_rewards': None, 'actual_zone_to_fog_mapping': None,
                'current_server_verified': False, 'run_updated': False,
                'calculation_applied': False}
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError):
        return None


def reference():
    return packet()


def rows(result, fog=None):
    if result is None or (fog is not None and (type(fog) is not str or fog not in FOGS)):
        return []
    ids = result['data']['fogs'][fog]['rule_ids'] if fog else list(result['data']['rules'])
    return [deepcopy(result['data']['rules'][key]) for key in ids]


def listed_floor_condition(rule, main_floor=None):
    if type(rule) is not dict: return None
    if main_floor is not None and (type(main_floor) is not int or not 1 <= main_floor <= 5): return None
    listed = rule.get('documented_main_floors')
    return {'declared_main_floor': main_floor, 'documented_main_floors': deepcopy(listed),
            'matches_listed_floor': None if main_floor is None or listed is None else main_floor in listed,
            'actual_server_eligible': None, 'run_updated': False}


def refresh_condition(result, node_type=None, *, moved=None, passed=None, completed_shop=None):
    """Compare only the stated movement/pass/shop conditions; never refresh a node."""
    if result is None: return None
    if node_type is not None and (type(node_type) is not str or node_type not in result['data']['original_nodes']): return None
    if any(value is not None and type(value) is not bool for value in (moved, passed, completed_shop)): return None
    if node_type != 'BATTLE_SHOP' and completed_shop is not None: return None
    if node_type == 'BATTLE_SHOP' and completed_shop is True:
        status = 'documented_completed_shop_exception'
        text = '按所填声明，这是已完成的诡意行商；社区文献明确它不参加这条刷新规则。'
    elif passed is True:
        status = 'outside_unpassed_wording'
        text = '按所填声明，这个节点已经过，不属于原文所说的“其余未经过节点”。'
    elif moved is False:
        status = 'movement_trigger_not_declared'
        text = '尚未完成一次移动，不能按这条“每次移动后”的文字条件判定已经触发；其它变化机制仍未核对。'
    elif moved is None or passed is None or node_type is None or (node_type == 'BATTLE_SHOP' and completed_shop is None):
        status = 'unknown'
        text = '移动、是否经过或商店完成状态仍有必要信息未知，不能确定已列条件是否相符。'
    else:
        status = 'matches_listed_conditions_only'
        text = '按所填声明，符合“移动后、未经过”的文字条件，且没有声明已完成商店例外；不表示本次一定刷新。'
    return {'status': status, 'text': text, 'declared_node_type': node_type,
            'declared_moved': moved, 'declared_passed': passed,
            'declared_completed_shop': completed_shop,
            'actual_will_refresh': None, 'actual_node_type_after': None,
            'actual_event_after': None, 'nodes_changed': False,
            'complete_refresh_type_scope_verified': False}


def locate(category, key):
    if type(category) is not str or type(key) is not str: return None
    result = packet()
    if result is None: return None
    data = result['data']
    base = {'branch': 'rules', 'fog': None, 'rule_id': None, 'zone_id': None,
            'source_request': {'category': category, 'key': key}}
    if category == 'scenes' and key in data['original_enter_scenes']:
        base['fog'] = data['original_enter_scenes'][key]['fog']
        # A red entry remains four candidates; the scene suffix is not decoded.
        return base
    if category == 'variations' and key in data['rules']:
        base['rule_id'] = key; base['fog'] = data['rules'][key]['fog']; return base
    if category == 'regions' and key in data['original_portal_zones']:
        base['branch'] = 'refresh'; base['zone_id'] = key; return base
    if category in ('items', 'relics') and key == 'rogue_6_bubble_01':
        base['rule_id'] = 'variation_6'; base['fog'] = '绿雾'; return base
    if category == 'node_types' and key == 'PORTAL': return base
    return None


def links(result, rule_id=None, zone_id=None):
    if result is None: return []
    if any(value is not None and type(value) is not str for value in (rule_id, zone_id)): return []
    data = result['data']; output = []
    if rule_id in data['rules']:
        row = data['rules'][rule_id]
        output.append({'kind': 'portal_fog', 'key': row['fog'],
                       'label': '查看' + row['fog'] + '的溯源对话资料'})
        for key in row['node_links']:
            output.append({'kind': 'node_type', 'key': key,
                           'label': '查看' + data['original_nodes'][key]['name'] + '的原节点说明'})
        for key in row['item_links']:
            output.append({'kind': 'item', 'key': key,
                           'label': '查看' + data['original_items'][key]['name'] + '的原标志说明'})
    if zone_id in data['original_portal_zones']:
        output.append({'kind': 'region', 'key': zone_id, 'label': '查看这份准确原区域资料'})
        group = data['original_roll_node_data'].get(zone_id, {}).get('groups', {})
        for key in group:
            output.append({'kind': 'node_type', 'key': key,
                           'label': '查看' + data['original_nodes'][key]['name'] + '的原节点说明'})
    return output


def resolve_link(result, request, *, rule_id=None, zone_id=None):
    if type(result) is not dict or type(request) is not dict: return None
    fresh = packet()
    if fresh is None or not _same(fresh, result): return None
    valid = next((link for link in links(fresh, rule_id, zone_id) if _same(link, request)), None)
    if valid is None: return None
    data = fresh['data']; kind = valid['kind']; key = valid['key']
    original = (data['original_nodes'].get(key) if kind == 'node_type' else
                data['original_items'].get(key) if kind == 'item' else
                data['original_portal_zones'].get(key) if kind == 'region' else None)
    return {'request': deepcopy(valid), 'source_identity': deepcopy(fresh['source_identity']),
            'original': deepcopy(original), 'reference_only': True,
            'actual_node_affected': None, 'actual_held': None, 'run_updated': False}


def player_text(result, rule_id=None, *, fog=None, main_floor=None, condition=None):
    if type(rule_id) not in (str, type(None)) or type(fog) not in (str, type(None)): return UNAVAILABLE
    lines = ['【秘境乌托邦】', NOTICE]
    data = result['data']; row = data['rules'].get(rule_id)
    if fog in data['fogs']:
        entry = data['fogs'][fog]
        lines += ['', '【' + fog + '的资料对应】', entry['principle'], '布局资料：' + entry['layout'],
                  '对应规则：' + '、'.join(data['rules'][key]['name'] for key in entry['rule_ids'])]
        if fog == '红雾':
            lines.append('红雾对应四种候选之一，尚未确认是哪种；不按对话或区域编号替你选定。')
    if row is None:
        return '\n'.join(lines + ['', '请手动选择一条规则。九条是规则目录，不是本次同时生效的九项加成。',
            '本区域规则无法被消除；文献记载本层行动力耗尽后返回原进入节点。实际触发与返回时刻仍未知。',
            '原区域刷新表是另一分支；没有根据区域后缀绑定雾色、规则、主层或完整布局。'])
    lines += ['', '【' + row['name'] + ' · 游戏原说明】', row['original']['functionDesc'],
              '', '【怎样理解与适用限制】', *row['player_notes']]
    if row['documented_main_floors'] is not None:
        comparison = listed_floor_condition(row, main_floor)
        if comparison is None:
            lines += ['层数输入无效；只接受进入前的常规第Ⅰ至Ⅴ层，特殊区域不由名字或编号折算。']
        elif comparison['matches_listed_floor'] is None:
            lines += ['进入前的常规层未声明，不能核对文献层数条件。']
        elif comparison['matches_listed_floor']:
            lines += ['仅本页声明与文献列出的常规层条件相符；不代表本局已获得入口或完整资格。']
        else:
            lines += ['仅本页声明不在文献列出的常规层范围内；原文仍可查阅，不据此删除本局已读内容。']
    if rule_id == 'variation_5':
        lines += ['', '【仅本页节点条件对照】', condition['text'] if condition else '尚未填写对照条件。',
                  '这里只对照文字条件与商店例外；实际可刷新节点类别、刷新后的事件和实际执行均未知，不改变节点历史。']
    if rule_id == 'variation_8':
        lines += ['', '【原文与补充的差别】',
                  '“获胜的”“正式”两处来自社区为原文歧义增加的解释，不改写上方游戏原说明，也不声称已核对服务器当前执行。']
    lines += ['', '【仍需核对】',
              '本局是否进入这份规则、确切区域变体、实际受影响节点或干员、发放与扣除时刻及完整服务器条件仍未确认。',
              '九条区域规则不是九件藏品。没有取得准确藏品对应的规则，不制造藏品入口；相关居民标志会明确标为标志。']
    return '\n'.join(lines)


def refresh_table_text(result, zone_id=None):
    data = result['data']; tables = data['original_roll_node_data']
    lines = ['【原区域的节点刷新表】', NOTICE,
             '三份准确原区域分别保留；它们同名不表示同一布局，也没有据编号推断蓝雾、主层或当前进入的是哪一份。']
    if zone_id is None:
        return '\n'.join(lines + ['', '请选择一份原区域。原表只给节点类型，不给具体事件、权重、刷新次数或完整地图。'])
    if zone_id not in data['original_portal_zones']:
        return '\n'.join(lines + ['', '这份区域没有准确对应，旧表不能借给其它同名区域。'])
    zone = data['original_portal_zones'][zone_id]
    lines += ['', '【当前查看】' + zone['name'], zone['description']]
    if zone_id not in tables:
        return '\n'.join(lines + ['此准确原区域未列独立刷新表；未知不等于不会刷新，也不借用三份有表区域的内容。'])
    names = [data['original_nodes'][key]['name'] for key in tables[zone_id]['groups']]
    lines += ['', '【这份原表列出的节点类型】', *('• ' + name for name in names),
              '', '【边界】', '这是这份区域原表里的类型集合，不是所有乌托邦的通用节点池。',
              '同一不期而遇或其它节点类型可能有不同事件；本表未列具体事件成员，不能把同类全部事件视为一定可发生。',
              '没有显示或计算生成概率，不预测实际刷新结果，不清除已完成或历史节点记录。']
    return '\n'.join(lines)
