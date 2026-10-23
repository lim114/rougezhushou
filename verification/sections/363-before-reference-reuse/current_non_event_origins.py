"""Exact non-event named-item sources; not an inventory, actual grant or reward pool."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-non-event-origins-363'
DATA = 'rouge/data/current-non-event-origins.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '51f9c115de15206344dc1c535ea0fbb6c20a5bac3e5c7fb0798478679b936804'
SQUADS = tuple('rogue_6_band_'+str(n) for n in (5,7,14,21,23,24,26,27))
RELICS = ('rogue_6_relic_legacy_132', 'rogue_6_relic_legacy_133')
KINDS = (('squad', '分队的初始具名物品'), ('relic', '收藏品对应的招募券'))
TIMES = (('initial', '原文明确：初始携带'), ('unspecified', '具体发放时点未核验'))
UNAVAILABLE = '非事件取得来源暂时无法核对，旧清单、原文和关联窗口已清除；恢复后请重新选择。'
NOTICE = '10条已核对的非事件取得资料；与事件领取分开，不代表完整获取池、当前已生效分队或已经获得物品。'


def source_rows(current):
    rows = []
    for source_id in (*SQUADS, *RELICS):
        source_item = current['items'][source_id]
        effect = current['relics'][source_id]
        matches = []
        for index, buff in enumerate(effect['buffs']):
            if buff['key'] != 'immediate_reward': continue
            board = {v['key']: v['valueStr'] if v['valueStr'] is not None else v['value']
                     for v in buff['blackboard']}
            identity = board.get('id'); item = current['items'].get(identity)
            if item is None or item['type'] not in ('RELIC', 'SCRAP', 'RECRUIT_TICKET'): continue
            count = board.get('count')
            if type(count) not in (int,float) or isinstance(count,bool) or int(count) != count or count <= 0:
                raise ValueError('Exact positive integer source count required')
            matches.append((index, identity, item, int(count)))
        if len(matches) != 1: raise ValueError('One exact named item pointer per selected source required')
        index, identity, item, count = matches[0]
        squad = source_id in SQUADS
        if squad != (source_item['type'] == 'BAND'):
            raise ValueError('Exact source kind differs')
        if not squad and (source_item['type'] != 'RELIC' or item['type'] != 'RECRUIT_TICKET'):
            raise ValueError('Exact recruitment-voucher source required')
        if identity in current['upgradeTickets'] or source_id.startswith('rogue_6_legacy_'):
            raise ValueError('360 upgrade and361 cross-run scopes excluded')
        configs = [deepcopy(row) for row in current['init'] if source_id in row['initialBandRelic']] if squad else []
        if squad and not configs: raise ValueError('Exact squad must have a current initial-configuration reference')
        rows.append({'id': source_id+':'+identity, 'kind': 'squad' if squad else 'relic',
                     'source_id': source_id, 'source_name': source_item['name'],
                     'source_item': deepcopy(source_item), 'source_effect': deepcopy(effect),
                     'source_buff_index': index, 'source_buff': deepcopy(effect['buffs'][index]),
                     'source_category': 'squads' if squad else 'relics',
                     'band_reference': deepcopy(current['bandRef'][source_id]) if squad else None,
                     'initial_configuration_references': configs,
                     'item_id': identity, 'item_name': item['name'], 'item': deepcopy(item),
                     'item_category': {'RELIC':'relics','SCRAP':'scrap','RECRUIT_TICKET':'recruit_tickets'}[item['type']],
                     'reference_quantity': count, 'time': 'initial' if squad else 'unspecified',
                     'quantity_basis': 'explicit_full_immediate_reward_id_and_count_not_timing_proof',
                     'actual_eligible': None, 'actual_source_active': None,
                     'actual_quantity': None, 'actual_received': None})
    if len(rows) != 10 or len({r['item_id'] for r in rows}) != 10:
        raise ValueError('Ten distinct named references required')
    return rows


def _read_public(name):
    if type(name) is not str: raise ValueError('Public source path required')
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or rel.as_posix() != name:
        raise ValueError('Unsafe public source path')
    path = ROOT.joinpath(*rel.parts)
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()): raise ValueError('Linked source refused')
    for parent in path.parents:
        if parent == ROOT: break
        if parent.is_symlink(): raise ValueError('Linked source parent refused')
    return path.read_bytes()


def packet():
    try:
        raw = _read_public(MANIFEST)
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {DATA, PACK+'/source-notes.json', PACK+'/documented-source-rows.json',
                    PACK+'/web-observations.json', PACK+'/failed-downloads.json',
                    'research/p3-current-recruit-tickets-354/topic-page.html',
                    'research/p3-current-recruit-tickets-354/source-download.json',
                    'research/p3-expansion-313/current-topic.json',
                    'rouge/data/current-recruit-tickets.json',
                    'research/p3-current-recruit-tickets-354/runtime-manifest.json'}
        if manifest['schema'] != 'current_non_event_origins_363_manifest_v1' or manifest['game_commit'] != version.NEW_COMMIT or set(manifest['files']) != expected:
            return None
        values = {}
        for name,pin in manifest['files'].items():
            content = _read_public(name)
            if type(pin['bytes']) is not int or len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']: return None
            values[name] = content
        data = json.loads(values[DATA]); current = version.packet()
        if current is None or data['schema'] != 'current_non_event_origins_363_v1' or data['game_commit'] != version.NEW_COMMIT:
            return None
        if data['rows'] != source_rows(current['current']['details']) or data['complete_acquisition_pool'] is not False: return None
        from . import current_recruit_tickets as recruits
        recruit_packet = recruits.packet()
        if recruit_packet is None or data['recruit_source_identity'] != json.loads(json.dumps(recruit_packet['source_identity'])): return None
        for row in data['rows']:
            docs = data['documents'][row['source_id']]
            if row['kind'] == 'squad':
                if docs['timing'] != 'initial' or row['item_name'].strip('“”') not in docs['visible_text'] or '初始携带' not in docs['visible_text']: return None
            else:
                ref = recruits.reference(row['item_id'])
                if docs['timing'] != 'unspecified' or ref is None or ref['selected']['original_item'] != row['item']: return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256,current['source_identity']),
                'actual_eligible': None, 'actual_source_active': None, 'actual_received': None,
                'actual_quantity': None, 'actual_candidate': None, 'actual_cultivation': None,
                'actual_cost': None, 'run_updated': False, 'calculation_applied': False}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, UnicodeError, RecursionError):
        return None


def reference(identity=None, *, kind=None, timing=None, query=''):
    if identity is not None and type(identity) is not str: return None
    if kind is not None and (type(kind) is not str or kind not in dict(KINDS)): return None
    if timing is not None and (type(timing) is not str or timing not in dict(TIMES)): return None
    if type(query) is not str: return None
    result = packet()
    if result is None: return None
    rows = [deepcopy(row) for row in result['data']['rows']
            if (kind is None or row['kind'] == kind) and (timing is None or row['time'] == timing)
            and (not query.strip() or query.strip() in row['source_name'] or query.strip() in row['item_name'])]
    selected = next((row for row in rows if row['id'] == identity), None)
    if identity is not None and selected is None: return None
    return {**result, 'rows': rows, 'selected': selected, 'filters': {'kind':kind,'timing':timing,'query':query}}


def locate(category, identity):
    if type(category) is not str or type(identity) is not str: return None
    result = reference()
    if result is None: return None
    matching = []
    for row in result['rows']:
        if (category == row['source_category'] and identity == row['source_id']
            or category in ('items',row['item_category']) and identity == row['item_id']):
            matching.append(row)
    return {'identity':matching[0]['id'],'source_request':{'category':category,'key':identity}} if len(matching)==1 else None


def destination(identity, side):
    if type(side) is not str or side not in ('source','item'): return None
    result = reference(identity)
    if result is None or result['selected'] is None: return None
    row = result['selected']; prefix = 'source_' if side == 'source' else 'item_'
    return {'category':row[prefix+'category'],'key':row[prefix+'id'],
            'name':row[prefix+'name'], 'actual_active':None, 'actual_received':None}


def player_text(result):
    lines = ['【非事件取得来源】',NOTICE,'','【怎样查阅】',
             '按来源和有证据的时点分别查看。每条单独显示，不把不同分队、不同档位或收藏品的奖励相加。']
    row = result['selected']
    if row:
        lines += ['','【可取得什么】'+row['item_name'],
                  '资料中的发放数量：'+str(row['reference_quantity'])+('张招募券' if row['item_category']=='recruit_tickets' else '件'),
                  '【对应来源】'+row['source_name'],'完整来源说明：'+version._plain(row['source_item']['usage']),
                  '物品完整用途：'+version._plain(row['item']['usage'])]
        if row['kind'] == 'squad':
            band = row['band_reference']; ordinary = band['bandLevel'] == 0
            lines += ['','【何时获得】文献明确：初始携带。',
                      '时点依据是对应分队的完整中文文献行；发放编号与数量另由固定原始效果记录核对。',
                      '分队档位：'+('原记录的基础档' if ordinary else '原记录的强化档位'+str(band['bandLevel']))+'。同名的其它档位不能自动继承这项奖励。']
            if row['source_id'] == 'rogue_6_band_21':
                lines += ['地质调查的原效果文字未写“初始携带”；这是当前主题文献的补充说明，原效果记录另有准确物品指针，两个依据分开保留。']
            configs = row['initial_configuration_references']
            grades = sorted(c['modeGrade'] for c in configs if c['modeId']=='NORMAL')
            monthly = [c['predefinedId'] for c in configs if c['modeId']=='MONTH_TEAM']
            lines += ['','【初始配置中的适用范围】',
                      '常规行动原表列有该准确档位的保密等级：'+('、'.join(map(str,grades)) if grades else '未列出')+'。',
                      '这只是原始配置收录情况；不等于相应等级下必然选择此档位，也不证明账户已点亮科技或已经解锁。']
            if monthly: lines += ['另有'+str(len(monthly))+'份实践者列表配置列出此档位；不借此解释所有月份或其它模式都适用。']
            unlock = row['source_item']['unlockCondDesc']
            lines += ['原项解锁说明：'+(version._plain(unlock) if unlock else '此原项没有提供独立的解锁说明；不能当作无条件解锁。')]
            if row['source_id'] == 'rogue_6_band_27':
                lines += ['','【三件与一件不要混在一起】本条是初始3个枯苔藓球；同一分队文字中的“每次进入行商时获得1个”是另一个时点，不在这里再加1。']
            if row['source_id'] == 'rogue_6_band_26':
                lines += ['','【具名物品与随机池分开】本条是旅行绒。初始稀有加工品和进入新区域的随机物品是其它分项；完整名单与实际结果未知，不加到旅行绒数量里。']
        else:
            stars = 5 if row['source_id'] == RELICS[0] else 6
            lines += ['','【何时发放】具体时点尚未核验。',
                      '原物品文字说明随机临时招募效果，原效果记录准确指向这张券并写明数量1；但变量名称不足以证明获取当帧、结算时或其它实际发放时刻。',
                      '博士银印文献中“获得收藏品时给予招募券”的备注列在水月主题下，不能未经核验就移到黑流树海。',
                      '这张券的说明为'+str(stars)+'星随机直升临时招募。不是任选一名已拥有干员，也不证明实际人选、职业、培养、领取或处理时刻。',
                      '“直升”表示首次招募即相当于已进阶，不将它当作进阶券或具体满级培养证明。']
        lines += ['','【继续查看】两侧分别打开准确来源原文与对应物品/招募券；不在程序中执行领取。']
    else:
        lines += ['','请选择一条资料，查看具体物品、数量、来源档位和时点依据。']
    lines += ['','【范围与未知】',
              '这里列出2026年10月16日固定国服资料中的8条分队具名物品与2条收藏品对应招募券。资源、随机池、新典训进阶券和跨局助力可在各自说明中继续查阅。',
              '完整获取池、账户实际解锁、分队实际生效、物品实际持有、发放时刻、领取及当前服务器执行仍未知。缺少条目不表示无法获得。',
              '只作局外资料查阅，不发放物品、不招募、不改变计算、培养或本局记忆，不推荐路线、不提供生成概率。']
    return '\n'.join(lines)
