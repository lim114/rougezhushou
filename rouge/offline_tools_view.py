"""Small offline query surface over public calibration and fixed-stage tools.

This widget owns only editable copies. It never loads run state, sends a chat,
captures a game, or promotes a declaration into native verification.
"""
from copy import deepcopy
import html
import json
import math

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QPlainTextEdit, QTextBrowser, QGroupBox, QSplitter)
from PySide6.QtCore import Qt
from . import calibration, battle_planning
from .catalog import catalog
from .battle_preview import battle_data


CALIBRATION_QUERIES = (
    ('panel', '面板属性分层'), ('pair', '同条件面板对照'),
    ('skills', '首批三名全部技能'), ('cultivation', '等级与培养贡献'),
    ('modules', '模组阶段与门槛'), ('talents', '天赋与在场时间'),
    ('animations', '原动作事件与帧数'), ('recipient-events', '银灰二技能受益包'),
    ('packets', '单包伤害与治疗算式'), ('worksheets', '公开培养公式算例'),
)
BATTLE_QUERIES = (
    ('actions', '完整关卡动作清单'), ('activations', '预置实体激活对应'),
    ('candidates', '候选组与伴随包'), ('window', '各片段局部时间窗'),
    ('enemy-sources', '敌人全部入口来源'), ('branches', '条件分支与阶段'),
    ('route', '固定路线分段与等待'), ('cell', '地图格反向查询'),
    ('mechanism', '敌人机制原始来源差异'), ('compare', '两组敌人环境对照'),
)
QUERIES = {'calibration': CALIBRATION_QUERIES, 'battle': BATTLE_QUERIES}
BATTLE_COMMANDS = {
    'actions': battle_planning.action_catalog,
    'activations': battle_planning.predefined_activations,
    'candidates': battle_planning.candidate_groups,
    'window': battle_planning.local_time_window,
    'enemy-sources': battle_planning.enemy_entry_sources,
    'branches': battle_planning.branch_phase_catalog,
    'route': battle_planning.route_segments,
    'cell': battle_planning.cell_planning_references,
    'mechanism': battle_planning.mechanism_provenance,
    'compare': battle_planning.enemy_scenario_comparison,
}
EVIDENCE_NAMES = {'game_panel': '调用方声明的游戏面板',
    'public_case': '调用方声明的公开算例', 'formula_reference': '公式参考算例'}
INPUT_GUIDANCE = {
    'panel': '编辑 scenario 培养、藏品和技能条件。operator：kaltsit=凯尔希·思衡托，silverash=凛御银灰，mechanist=机械师；trust 为加成进度0–100。结果分层诊断，不是实机认证。',
    'pair': 'scenario 为预测条件；observation 为独立观察记录。先查询“面板属性分层”取得同条件标识。注明观察面板、来源类别、来源与数值，不能将模型输出冒充游戏观察。',
    'skills': 'scenario 为声明培养条件；默认列首批三名的9个技能，可用 operators 限定干员。完整总量缺证时保持未知，模型条件总量另列参考。',
    'cultivation': 'scenario 为培养条件；levels 是要对照的等级列表，均须在声明精英阶段内。信赖为加成进度0–100；不含藏品、部署天赋或技能。',
    'modules': 'scenario 为干员与培养条件。列固定资料中的各模组阶段、资格门槛与属性增量；列出候选不等于证实隐藏脚本附着。',
    'talents': 'scenario 为声明条件；elapsed_seconds 可填写在场秒数列表。天赋回复速度与技能治疗分开；实际受益时间、损血和治疗总量未自动取得。',
    'animations': 'scenario 选择干员；animation_contains 可筛选动画名，orientation 可为 Front（正面）或 Back（背面）。原事件与帧数不自动代表实际命中。',
    'recipient-events': '仅凛御银灰二技能。recipients 声明每次受益部署：部署秒数、叠层和每次触发时受益人攻击；enemy_defense 为目标防御。缺少攻击快照时只列已知包。',
    'packets': 'scenario 为培养、藏品、技能与目标减伤条件。只求单包算式；不猜实际攻击次数、完整技能总量或实际有效治疗。',
    'worksheets': '无需输入即可运行10组公共培养公式算例。空白或 {} 使用公共算例；自定义 cases 时须注明来源。算式交叉核对不能代替实机成对校准。',
    'actions': 'stage_id 为固定关卡标识。列主队列所有动作与数量参数；配置延迟不是已验证的全局执行时间。',
    'activations': 'stage_id 为固定关卡标识。按精确别名对应预置实体；空键、多个匹配、未找到均保持未确认。',
    'candidates': 'stage_id 为固定关卡标识。列各片段全部候选组与伴随包；不求生成概率，也不把候选数量相加为实际数量。',
    'window': 'start_seconds/end_seconds 是每个片段动作队列起点之后的局部秒数窗口；limit 为输出上限。各队列彼此独立，不是全局出怪轴。',
    'enemy-sources': 'stage_id、enemy_id、level 为关卡、敌人标识和资料等级。列主队列、条件分支和初始记录来源；不确认实际选中哪条入口。',
    'branches': 'stage_id 为关卡；branch_id 可选，用于筛选分支。列各阶段完整动作；触发机制、实际阶段选择、分支路线作用域缺证时未知。',
    'route': 'route_index 为固定路线序号（从0计）。折线分段、消失、再出现和等待分别列出；名义格不是实测寻路或实际到达时间。',
    'cell': 'row、col 是显示地图从上到下的行列（从0计）。反查明确配置点、主队列关联和预置实体；不声称实际占用或必经。',
    'mechanism': 'stage_id、enemy_id、level 选择关卡敌人。原数据库等级与关卡覆盖差异分别保留，缺字段、null、空表与0不同；不猜继承或脚本合并。',
    'compare': 'left_stage/right_stage 与 left_level/right_level 分别指定两组条件；run_config/right_run_config 为局外环境。比较已支持环境小计，完整有效面板仍未知。',
}
LABELS = {**calibration.LABELS, 'maxHp': '生命上限', 'atk': '攻击力',
    'def': '防御力', 'magicResistance': '法术抗性', 'attackSpeed': '攻速属性',
    'baseAttackTime': '基础攻击间隔', 'moveSpeed': '移动速度',
    'massLevel': '重量', 'hpRecoveryPerSec': '每秒生命回复',
    'epResistance': '元素抗性', 'epDamageResistance': '元素伤害抗性'}
VALUE_NAMES = {'physical': '物理', 'magic': '法术', 'true': '真实',
    'healing': '治疗', 'Front': '正面', 'Back': '背面', 'WALK': '地面',
    'FLY': '飞行', 'start': '起点', 'end': '终点', 'move': '移动检查点',
    'appear': '再出现', 'disappear': '消失', 'main_queue': '主队列',
    'conditional_branch': '条件分支', 'initial_record': '初始记录',
    'database_level': '敌人数据库', 'stage_override': '关卡覆盖记录',
    'exact_alias': '唯一别名对应', 'empty_key': '空键，未绑定',
    'ambiguous_alias': '同名多个实体，未确认', 'unresolved_alias': '未找到对应实体',
    'elapsed_fragment_time': '当前片段计时条件', 'arrival_local_wait': '到达后的局部等待',
    'OnAttack': '攻击事件（命中未核验）'}


def _finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('输入不能包含无穷或非数值。')
    if isinstance(value, dict):
        for item in value.values(): _finite_tree(item)
    elif isinstance(value, list):
        for item in value: _finite_tree(item)


def run_offline_query(family, command, payload):
    """Public synchronous entry point used by a worker and public-fixture tests."""
    if not isinstance(payload, dict): raise ValueError('条件必须是 JSON 对象。')
    _finite_tree(payload)
    commands = calibration.COMMANDS if family == 'calibration' else BATTLE_COMMANDS if family == 'battle' else {}
    if command not in commands: raise ValueError('没有这个离线查询。')
    try:
        return commands[command](**deepcopy(payload))
    except TypeError as error:
        raise ValueError('条件字段缺失、类型不正确或含有此查询不支持的字段。技术原因：'+str(error)) from None


def public_payload(family, command):
    """No private state: defaults come from the pinned public data only."""
    if family == 'calibration':
        scenario = {'operator': 'mechanist', 'skill': 3, 'charge_count': 0}
        payload = {'scenario': scenario}
        if command == 'worksheets': return {}
        if command == 'pair':
            payload['observation'] = {
                'context_token': calibration.panel_layers(scenario)['context_token'],
                'panel': '培养与模组', 'values': {'attack': 573, 'defense': 765},
                'evidence_kind': 'formula_reference', 'source': '固定培养表公式参考：机械师精二90、满信赖加成、潜能1、无模组',
            }
        elif command == 'cultivation': payload['levels'] = [59, 60, 90]
        elif command == 'talents': payload['scenario'] = {'operator': 'silverash', 'skill': 2}
        elif command == 'animations': payload['animation_contains'] = 'Attack'
        elif command == 'recipient-events':
            payload = {'scenario': {'operator': 'silverash', 'skill': 2},
                'recipients': [{'id': '声明受益人A', 'deployment_seconds': 8, 'stacks': 2,
                    'attack_at_triggers': [500, 600]}], 'enemy_defense': 200}
        return payload
    stage_id = 'ro6_n_1_2'
    stage = battle_data()['stages'][stage_id]
    enemy = next((e for e in stage['enemies'] if e['id'] == 'enemy_1093_ccsbr'), stage['enemies'][0])
    payload = {'stage_id': stage_id}
    if command == 'window': payload.update(start_seconds=0, end_seconds=60, limit=256)
    elif command in ('enemy-sources', 'mechanism'): payload.update(enemy_id=enemy['id'], level=enemy['level'])
    elif command == 'route': payload['route_index'] = 0
    elif command == 'cell': payload.update(row=0, col=0)
    elif command == 'compare':
        payload = {'left_stage': stage_id, 'right_stage': stage_id, 'enemy_id': enemy['id'],
            'left_level': enemy['level'], 'right_level': enemy['level'],
            'run_config': {'difficulty': 0}, 'right_run_config': {'difficulty': 1}}
    return payload


def _text(value):
    if value is None: return '未知'
    if value is True: return '是'
    if value is False: return '否'
    if isinstance(value, float): return format(value, '.10g')
    if isinstance(value, dict):
        if set(value) == {'row', 'col'}: return f"显示格：第{value['row']}行、第{value['col']}列（从0计）"
        return '；'.join(f'{LABELS.get(str(k), k)}：{_text(v)}' for k,v in value.items()) or '空记录'
    if isinstance(value, (list, tuple)): return '、'.join(_text(v) for v in value) or '无记录'
    return VALUE_NAMES.get(str(value), str(value))


def _esc(value): return html.escape(_text(value))
def _p(value): return '<p>'+_esc(value)+'</p>'
def _h(value): return '<h3>'+_esc(value)+'</h3>'
def _table(headers, rows):
    rows = list(rows)
    if not rows: return _p('公开配置未列出此类记录；不据此推断隐藏逻辑。')
    return ('<table border="1" cellspacing="0" cellpadding="5"><tr>'+''.join('<th>'+_esc(h)+'</th>' for h in headers)+
        '</tr>'+''.join('<tr>'+''.join('<td>'+_esc(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</table>')
def _attributes(stats):
    return _table(['属性', '条件参考值'], [(LABELS.get(k,k),v) for k,v in (stats or {}).items()])


def render_offline_result(family, command, data):
    """Readable main output; technical fields stay available in a collapsed pane."""
    title = dict(QUERIES[family])[command]
    parts = ['<html><body>', '<h2>'+_esc(title)+'</h2>',
        _p('局外声明条件 / 固定公开配置参考。尚未验证当前客户端实机；未知不等于0。')]
    if data.get('operator'): parts.append(_p('干员：'+data['operator']))
    if data.get('stage_name'): parts.append(_p('关卡：'+data['stage_name']))
    if family == 'calibration':
        if command == 'panel':
            parts += [_p('分层差值用于排查，不能把跨层效果再次相加。'),
                _table(['属性','培养与模组','符文写回','常态天赋与效果','技能期间参考'],
                    [(r['label'],*[s['value'] for s in r['stages']]) for r in data['rows']]),
                _h('同条件标识（仅证明声明一致）'),_p(data['context_token'])]
        elif command == 'pair':
            parts += [_p('来源类型：'+EVIDENCE_NAMES.get(data['evidence_kind'],data['evidence_kind'])),
                _p('来源：'+data['source']),_p('比较面板：'+data['panel']),
                _table(['属性','预测','声明观察','观察减预测','在声明容差内','其他层相符线索'],
                    [(r['label'],r['predicted'],r['observed'],r['difference'],r['matches_declared_tolerance'],r['other_stage_matches']) for r in data['rows']]),
                _p('未比较字段：'+_text([LABELS.get(k,k) for k in data['uncompared_fields']]))]
        elif command == 'skills':
            for row in data['rows']:
                parts += [_h(f"{row['operator']} · {row['skill']}技能 {row.get('name','')}"),_p(row['status'])]
                parts.append(_table(['指标','秒数 / 数值'],[
                    ('初动（条件参考）',row.get('initial_seconds_reference')),
                    ('回转（条件参考）',row.get('recharge_seconds_reference')),
                    ('周期（条件参考）',row.get('cycle_seconds_reference')),
                    ('完整技能总伤',row['full_skill_damage']),('完整技能总治疗',row['full_skill_healing'])]))
                reference = row.get('conditional_total_reference', {})
                parts.append(_p(f"原模型条件总伤参考：{_text(reference.get('damage'))}；条件总治疗参考：{_text(reference.get('healing'))}。此项不等于原生完整总量。"))
                parts.append(_table(['已声明分项','伤害类型','包数参考','每包参考','分项参考合计'],
                    [(r.get('name'),r.get('damage_type'),r.get('hits'),r.get('per_hit'),r.get('total')) for r in row.get('declared_components',[])]))
                parts.extend(_p(n) for n in row.get('missing_or_conditional_notes',[]))
        elif command == 'cultivation':
            parts += [_p(data['scope']),_p('信赖字段为加成进度0–100；游戏信赖显示范围0–200。')]
            for row in data['rows']:
                parts += [_h('等级 '+str(row['level'])),_table(['属性','等级基础','信赖贡献','潜能直接贡献','模组贡献','培养参考结果'],
                    [(LABELS.get(k,k),v['level_base'],v['trust_increment'],v['potential_increment'],v['module_increment'],row['cultivated'].get(k)) for k,v in row['contributions'].items()])]
        elif command == 'modules':
            parts.append(_table(['模组','阶段','满足门槛','门槛','当前声明装备','属性增量参考','候选改动数'],
                [(r['name'],r['stage'],r['qualified'],f"精英{r['unlock_elite']} / 等级{r['unlock_level']}",r['requested'],r['attribute_delta'],len(r['parts'])) for r in data['rows']]))
            parts.append(_p('候选天赋/特性并不证明实际脚本附着；原字段可在技术详情查看。'))
        elif command == 'talents':
            for row in data['rows']:
                parts += [_h('声明在场 '+_text(row['deployment_elapsed_seconds'])+' 秒'),_attributes(row['base_stats'])]
                parts.append(_table(['天赋','效果类型','参考回复速度 / 比例','已声明翻倍','实际治疗总量'],
                    [(r['name'],r['kind'],r.get('regeneration_per_second_reference',r.get('recipient_regeneration_rate_reference')),r.get('doubled'),r['actual_healing_total']) for r in row['talent_references']]))
        elif command == 'animations':
            parts.append(_p('参考帧率：'+str(data['reference_fps'])+'；原动作事件不自动绑定实际攻击或命中。'))
            for row in data['records']:
                parts += [_h(_text(row['orientation'])+' / '+row['animation']),
                    _table(['记录','秒数','严格向上取整帧','表示误差归一帧'],[
                        ('动作时长',row['duration'].get('seconds'),row['duration'].get('strict_ceil_frames_30hz'),row['duration'].get('representation_normalized_frames_30hz')),
                        *[(e['name'],e.get('seconds'),e.get('strict_ceil_frames_30hz'),e.get('representation_normalized_frames_30hz')) for e in row['events']]]),
                    _p('可作常规候选参考：'+_text(row['selectable_as_conventional_reference'])+'；运行时绑定：未核验')]
                parts.extend(_p(n) for n in row.get('unverified_reasons',[]))
        elif command == 'recipient-events':
            parts += [_table(['声明受益人','触发次序','参考秒数','当次受益人攻击','攻击倍率','防御前','物理减伤后参考','纳入声明窗口'],
                [(r['recipient_id'],r['trigger_index'],r['time_seconds_reference'],r['recipient_attack_at_trigger'],r['attack_scale'],r['pre_defense_damage'],r['post_defense_damage_reference'],r['included_in_declared_window']) for r in data['events']]),
                _p('已知参考包小计：'+_text(data['known_packet_subtotal_reference'])),
                _p('声明受益包参考合计：'+_text(data['declared_recipient_damage_reference'])),
                _p('完整技能总伤：'+_text(data['full_skill_damage'])+'；缺少攻击快照：'+str(data['missing_attack_snapshots']))]
        elif command == 'packets':
            parts.append(_table(['分项','类型','来源攻击','倍率','减伤前','减伤后','已支持承伤因子','单包条件参考','完整施放合计'],
                [(r['name'],r['damage_type'],r['owner_attack_reference'],r['scale'],r['pre_defense_value'],r['after_defense_value'],r['supported_damage_factor'],r['single_packet_reference'],r['complete_cast_total']) for r in data['rows']]))
        elif command == 'worksheets':
            parts += [_p(f"公式参考算例 {data['case_count']} 组；相符 {data['matching_reference_cases']} 组。不是公开实机成对验收。"),
                _table(['算例','干员','比较属性','预测','公式参考','差值','在声明容差内'],
                    [(row['id'],row['comparison']['operator'],r['label'],r['predicted'],r['observed'],r['difference'],r['matches_declared_tolerance']) for row in data['rows'] for r in row['comparison']['rows']])]
    else:
        if command == 'actions':
            parts.append(_table(['片段队列','次序','动作类型','配置键','声明数量','局部前延迟','间隔参数','全局秒数'],
                [(r['queue_id'],r['action_ordinal'],r['type_label'],r['action'].get('key'),r['action'].get('count'),r['action'].get('preDelay'),r['action'].get('interval'),r['absolute_seconds']) for r in data['actions']]))
        elif command == 'activations':
            parts.append(_table(['动作','队列','配置别名','对应状态','实体名义格','实际激活'],
                [(r['action_id'],r['queue_id'],r['key'],r['binding_status'],[o['display_cell'] for o in r['objects']],r['actual_active']) for r in data['activations']]))
            parts.append(_p('未被激活动作引用的预置实体数：'+str(len(data['unreferenced_objects']))))
        elif command == 'candidates':
            parts.append(_p('列出全部候选与伴随包；权重参数不是已核验概率，候选数量不能相加成实际数量。'))
            for group in data['groups']:
                parts += [_h('队列 '+group['queue_id']+' · 候选组 '+group['group_key']),
                    _table(['动作','类型','配置键','数量参数','权重参数','伴随包','隐藏组'],
                        [(r['action_id'],r['type_label'],r['key'],r['count_parameter'],r['weight_parameter'],r['package_key'],r['hidden_group']) for r in group['candidates']]),
                    _p('实际选择：未知；生成概率：不提供')]
            for pack in data['packages']:
                parts += [_h('队列 '+pack['queue_id']+' · 伴随包 '+pack['package_key']),
                    _table(['动作','所属候选组','类型','配置键'],[(r['action_id'],r.get('group_key'),r['type_label'],r['key']) for r in pack['members']])]
        elif command == 'window':
            parts.append(_p(f"查询各片段队列起点之后 {data['start_seconds']}–{data['end_seconds']} 秒的局部配置窗口；各队列独立，不是全局时间轴。"))
            for q in data['queues']:
                parts += [_h(q['queue_id']),_table(['动作','配置出现次序','类型','配置键','局部偏移秒数','存在条件'],
                    [(r['action_id'],r['ordinal'],r['type_label'],r['key'],r['offset_seconds'],r['conditional']) for r in q['occurrences']]),
                    _p('声明匹配数：'+_text(q['matching_declared_occurrences'])+'；输出截断：'+_text(q['truncated'])),
                    _table(['未纳入动作','待核验原因'],[(r['action_id'],r['reasons']) for r in q['pending']])]
        elif command == 'enemy-sources':
            parts += [_p('敌人：'+data['name']+'；记录等级：'+str(data['level'])),
                _table(['来源类型','动作 / 记录','片段队列','分支','阶段','实际出现时刻'],
                    [(r['kind'],r['id'],r.get('queue_id'),r.get('branch'),r.get('phase'),r.get('actual_entry_seconds')) for r in data['entry_sources']]),
                _p('实际敌人数量：'+_text(data['actual_enemy_count']))]
        elif command == 'branches':
            for branch in data['branches']:
                parts += [_h('分支 '+branch['branch_id']),_p('触发机制：未知；实际阶段选择：未知')]
                for phase in branch['phases']:
                    parts += [_h('阶段 '+str(phase['phase'])),_p('阶段前延迟参数：'+_text(phase['pre_delay_parameter'])),
                        _table(['动作','类型','配置键','数量参数','路线作用域核验'],
                            [(r['id'],r['type_label'],r['action'].get('key'),r['action'].get('count'),r['route_scope_verified']) for r in phase['actions']])]
            if not data['branches']: parts.append(_p('当前固定配置未列出条件分支。'))
        elif command == 'route':
            parts.append(_p('路线序号：'+str(data['route_index'])+'；移动类型：'+_text(data['motion'])))
            for index,segment in enumerate(data['segments'],1):
                parts += [_h('独立配置线段 '+str(index)),_table(['配置点','名义显示格'],[(r['kind'],r['cell']) for r in segment])]
            parts += [_h('等待条件'),_table(['检查点','锚定条件','秒数参数','实际到达秒数'],
                [(r['checkpoint_index'],r['anchor'],r['time_parameter'],r['arrival_seconds']) for r in data['waits']]),
                _h('消失 / 再出现'),_table(['检查点','类型','名义显示格'],[(r['checkpoint_index'],r['kind'],r['display_cell']) for r in data['transitions']]),
                _table(['待核验检查点','原因'],[(r['checkpoint_index'],r['reason']) for r in data['pending']])]
        elif command == 'cell':
            parts += [_p(data['display_cell']),_h('地图格参数'),_p(data['tile']),
                _table(['路线','明确配置点','关联主队列动作'],
                    [(r['route_index'],[p['kind'] for p in r['points']],[a['id'] for a in r['main_spawn_actions']]) for r in data['route_references']]),
                _p('预置实体数：'+str(len(data['predefined_objects']))+'；实际占用：未知')]
        elif command == 'mechanism':
            parts += [_p('敌人：'+data['enemy_id']+'；等级：'+str(data['level'])),
                _p('准确等级记录存在：'+_text(data['exact_level_present'])+'；实际合并机制：未知'),
                _table(['记录来源','等级','原字段数'],[(r['origin'],r['level'],len(r['fields'])) for r in data['records']])]
            for diff in data['comparisons']:
                parts += [_h(_text(diff['left_origin'])+' → '+_text(diff['right_origin'])),
                    _table(['字段位置','左记录状态 / 值','右记录状态 / 值'],
                        [(r['path'],r['left'],r['right']) for r in diff['differences']])]
        elif command == 'compare':
            for key,name in (('left','左条件'),('right','右条件')):
                side=data[key]
                parts += [_h(name+' · '+side['stage_name']+' · 等级'+str(side['level'])),
                    _h('已支持环境小计'),_attributes(side['known_environment_subtotal']),
                    _p('完整有效面板：未知；已支持环境项齐全：'+_text(side['supported_environment_complete']))]
                parts.extend(_p(n) for n in side['pending'])
            parts += [_h('右小计减左小计'),_table(['属性','左条件小计','右条件小计','小计差值','完整有效差值'],
                [(LABELS.get(r['attribute'],r['attribute']),r['left_known_subtotal'],r['right_known_subtotal'],r['subtotal_delta'],r['full_effective_delta']) for r in data['attribute_differences']]),
                _p('免疫字段差异：'+str(len(data['immunity_differences']))+'；机制描述差异：'+str(len(data['ability_differences'])))]
    parts.append(_h('适用范围与未核验项'))
    parts.extend(_p(n) for n in data.get('notes',[])+data.get('limits',[])+data.get('warnings',[]))
    parts.append(_p('完整原始结果与来源记录保留在下方“技术详情”。'))
    parts.append('</body></html>')
    return ''.join(parts)


class _WorkerSignals(QObject):
    finished = Signal(int, str, str, object, str)


class _QueryWorker(QRunnable):
    def __init__(self, serial, family, command, payload):
        super().__init__()
        self.serial,self.family,self.command,self.payload=serial,family,command,payload
        self.signals = _WorkerSignals()

    def run(self):
        try: result=run_offline_query(self.family,self.command,self.payload);error=''
        except Exception as exc: result=None;error='离线查询失败：'+str(exc)
        self.signals.finished.emit(self.serial,self.family,self.command,result,error)


class OfflineToolsPanel(QWidget):
    """Qt panel with explicit imports; automatic context refresh is nondestructive."""
    resultChanged = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scenario=None; self._stage=None; self._buffers={}
        self._serial=0; self._workers={}; self._result=None; self._rendered=''
        self._changing=False
        layout=QVBoxLayout(self)
        row=QHBoxLayout()
        self.family=QComboBox();self.family.addItem('干员校准','calibration');self.family.addItem('固定关卡规划','battle')
        self.query=QComboBox();row.addWidget(self.family);row.addWidget(self.query,1)
        layout.addLayout(row)
        self.scope=QLabel('纯局外查询：公共资料、声明条件、已证分项；不操作游戏，不发送聊天。')
        self.scope.setWordWrap(True);layout.addWidget(self.scope)
        row=QHBoxLayout()
        self.load_example=QPushButton('载入公开示例')
        self.import_scenario=QPushButton('导入当前干员条件')
        self.import_stage=QPushButton('导入当前关卡')
        self.run_button=QPushButton('运行离线查询')
        for button in (self.load_example,self.import_scenario,self.import_stage,self.run_button):row.addWidget(button)
        layout.addLayout(row)
        self.context_label=QLabel('当前干员条件和关卡尚未缓存；公共示例仍可运行。')
        self.context_label.setWordWrap(True);layout.addWidget(self.context_label)
        self.status=QLabel('请检查条件后运行。');self.status.setWordWrap(True);layout.addWidget(self.status)
        splitter=QSplitter(Qt.Orientation.Vertical)
        self.editor=QPlainTextEdit();self.editor.setPlaceholderText('声明条件 JSON；不读取私人配置')
        self.result_view=QTextBrowser();self.result_view.setOpenExternalLinks(False)
        splitter.addWidget(self.editor);splitter.addWidget(self.result_view)
        splitter.setSizes([200,450]);layout.addWidget(splitter,1)
        self.technical=QGroupBox('技术详情（完整 JSON 与来源，仅备查）');self.technical.setCheckable(True);self.technical.setChecked(False)
        technical_layout=QVBoxLayout(self.technical)
        self.raw_result=QPlainTextEdit();self.raw_result.setReadOnly(True);self.raw_result.setMaximumHeight(190)
        technical_layout.addWidget(self.raw_result);self.raw_result.hide()
        self.technical.toggled.connect(self.raw_result.setVisible);layout.addWidget(self.technical)
        self.family.currentIndexChanged.connect(self._family_changed)
        self.query.currentIndexChanged.connect(self._query_changed)
        self.editor.textChanged.connect(self._input_changed)
        self.load_example.clicked.connect(self._load_example)
        self.import_scenario.clicked.connect(self._import_scenario)
        self.import_stage.clicked.connect(self._import_stage)
        self.run_button.clicked.connect(self._run)
        self._family_changed()

    def current_query(self): return self.family.currentData(),self.query.currentData()

    def select_query(self, family, command):
        """Select one of the 20 public queries, preserving each editor buffer."""
        index=self.family.findData(family)
        if index<0 or command not in dict(QUERIES[family]):raise ValueError('没有这个查询。')
        self.family.setCurrentIndex(index)
        self.query.setCurrentIndex(self.query.findData(command))

    def set_scenario(self, scenario):
        incoming=deepcopy(scenario) if isinstance(scenario,dict) else None
        if incoming==self._scenario:return
        self._scenario=incoming;self._update_context()

    def set_stage(self, stage_id):
        incoming=deepcopy(stage_id) if isinstance(stage_id,str) and stage_id in battle_data()['stages'] else None
        if incoming==self._stage:return
        self._stage=incoming;self._update_context()

    def _update_context(self):
        name=catalog()['operators'].get((self._scenario or {}).get('operator'),{}).get('name')
        stage=battle_data()['stages'].get(self._stage,{})
        self.context_label.setText(f"可显式导入：干员 {name or '尚无可用条件'}；关卡 {stage.get('name','尚无可用关卡')}。自动刷新不会改写编辑区或当前结果。")
        self._update_buttons()

    def _update_buttons(self):
        family,command=self.current_query()
        self.import_scenario.setEnabled(family=='calibration' and command!='worksheets' and self._scenario is not None)
        self.import_stage.setEnabled(family=='battle' and self._stage is not None)

    def _family_changed(self):
        self._changing=True
        self.query.clear()
        for command,label in QUERIES[self.family.currentData()]:self.query.addItem(label,command)
        self._changing=False
        self._query_changed()

    def _query_changed(self):
        if self._changing or not self.query.currentData():return
        key=self.current_query();self._changing=True
        text=self._buffers.get(key)
        if text is None:text=json.dumps(public_payload(*key),ensure_ascii=False,indent=2)
        self.editor.setPlainText(text);self._changing=False
        self._buffers[key]=text;self._invalidate('查询已切换，请检查声明条件后运行。')
        self.scope.setText(INPUT_GUIDANCE[key[1]])
        self._update_buttons()

    def _input_changed(self):
        if self._changing:return
        self._buffers[self.current_query()]=self.editor.toPlainText()
        self._invalidate('条件已修改，旧结果已失效，请重新运行。')

    def _invalidate(self, text):
        self._serial+=1;self._result=None;self._rendered=''
        self.status.setText(text);self.result_view.setHtml(_p(text));self.raw_result.clear()
        self.run_button.setEnabled(True)
        self.resultChanged.emit(None)

    def _payload(self):
        text=self.editor.toPlainText()
        if not text.strip() and self.current_query()==('calibration','worksheets'):return {}
        if len(text)>2_000_000:raise ValueError('条件文本过长，请减少声明记录。')
        try:payload=json.loads(text)
        except (ValueError,RecursionError):raise ValueError('JSON 格式不正确；请检查引号、逗号和括号。') from None
        if not isinstance(payload,dict):raise ValueError('条件必须是 JSON 对象，不能是数组或单个值。')
        _finite_tree(payload);return payload

    def _load_example(self):
        self.editor.setPlainText(json.dumps(public_payload(*self.current_query()),ensure_ascii=False,indent=2))
        self.status.setText('已载入公共示例；请检查条件。公式算例不是实机观察。')

    def _import_scenario(self):
        try:
            family,command=self.current_query()
            if family!='calibration' or command=='worksheets' or self._scenario is None:raise ValueError('此查询没有可导入的干员条件。')
            payload=self._payload();scenario=deepcopy(self._scenario)
            if scenario.get('operator') not in calibration.OPERATORS:raise ValueError('校准工具目前仅支持凯尔希·思衡托、凛御银灰、机械师。')
            if command=='recipient-events' and (scenario.get('operator')!='silverash' or scenario.get('skill')!=2):
                raise ValueError('受益包查询需要凛御银灰二技能；请切换原界面后重新计算。')
            # Internal resolved effects are regenerated by the query, never injected.
            payload['scenario']={k:v for k,v in scenario.items() if not str(k).startswith('_')}
            self.editor.setPlainText(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False))
            self.status.setText('已显式导入最后计算的干员条件。原观察值和条件标识未更改；成对对照需独立确认观察条件。')
        except Exception as exc:self.status.setText('未导入：'+str(exc))

    def _import_stage(self):
        try:
            family,command=self.current_query()
            if family!='battle' or self._stage is None:raise ValueError('没有可导入的关卡。')
            payload=self._payload()
            if command=='compare':payload['left_stage']=self._stage
            else:payload['stage_id']=self._stage
            self.editor.setPlainText(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False))
            self.status.setText('已显式导入关卡；敌人、等级、路线和格子仍保留原声明，请核对。两组对照只替换左关卡。')
        except Exception as exc:self.status.setText('未导入：'+str(exc))

    def _run(self):
        try:payload=self._payload()
        except Exception as exc:
            self._invalidate('不能运行：'+str(exc));return
        self._invalidate('正在运行局外查询……')
        serial=self._serial;family,command=self.current_query()
        worker=_QueryWorker(serial,family,command,payload)
        worker.signals.finished.connect(self._finished)
        self._workers[serial]=worker;self.run_button.setEnabled(False)
        QThreadPool.globalInstance().start(worker)

    def _finished(self, serial, family, command, result, error):
        self._workers.pop(serial,None)
        if serial!=self._serial or (family,command)!=self.current_query():return
        self.run_button.setEnabled(True)
        if error:self._invalidate(error);return
        try:
            rendered=render_offline_result(family,command,result)
            raw=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)
        except Exception as exc:self._invalidate('结果结构无法显示：'+str(exc));return
        self._result=deepcopy(result)
        if rendered!=self._rendered:
            self.result_view.setHtml(rendered);self._rendered=rendered
        self.raw_result.setPlainText(raw)
        self.status.setText('离线查询完成。请按各分项的证据范围使用；未核验项保持未知。')
        self.resultChanged.emit(deepcopy(result))

    def result_snapshot(self):return deepcopy(self._result)
