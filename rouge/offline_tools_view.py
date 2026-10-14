"""Small offline query surface over public calibration and fixed-stage tools.

This widget owns only editable copies. It never loads run state, sends a chat,
captures a game, or promotes a declaration into native verification.
"""
from copy import deepcopy
import html
import json
import math
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QPlainTextEdit, QTextBrowser, QGroupBox, QSplitter)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from . import calibration, battle_planning, exploration_planning
from urllib.parse import quote, unquote
from .catalog import catalog
from .battle_preview import battle_data
from .base_settlement_planning import gold_reference_text
from .node_arrival import arrival_lines
from .information_scope import HISTORICAL_ROUTE_QUERIES,require_query_scope


CALIBRATION_QUERIES = (
    ('panel', '面板属性分层'), ('pair', '同条件面板对照'),
    ('skills', '首批三名全部技能'), ('cultivation', '等级与培养贡献'),
    ('modules', '模组阶段与门槛'), ('talents', '天赋与在场时间'),
    ('animations', '原动作事件与帧数'), ('recipient-events', '银灰二技能受益包'),
    ('relic-panels', '藏品组合与面板差值诊断'),
    ('packets', '单包伤害与治疗算式'), ('worksheets', '公开培养公式算例'),
    ('barrier-ledger', '机械师二技能 · 入伤与屏障账本'),
    ('shield-grants', '机械师二技能 · 初始屏障与藏品'),
    ('shield-inventory', '机械师二技能 · 按来源汇总屏障'),
    ('explosion-values', '机械师二技能 · 爆炸双分支定点计算'),
    ('modifier-values', '藏品逐包定点修饰与顺序差异'),
    ('regen-clock', '常态生命回复 · 逐点周期与改速'),
    ('regen-attributes', '常态生命回复 · 属性缓存与藏品求值'),
)
BATTLE_QUERIES = (
    ('actions', '完整关卡动作清单'), ('activations', '预置实体激活对应'),
    ('candidates', '候选组与伴随包'), ('window', '各片段局部时间窗'),
    ('enemy-sources', '敌人全部入口来源'), ('branches', '条件分支与阶段'),
    ('route', '固定路线分段与等待'), ('cell', '地图格反向查询'),
    ('mechanism', '敌人机制原始来源差异'), ('compare', '两组敌人环境对照'),
)
EXPLORATION_QUERIES = (
    ('items','全部零件与原始参数'),('targets','加工品全部目的地候选'),
    ('effects','移动资源与概念体条件'),('zones','主层和秘境目标'),
    ('budget','行动力付款与耗尽边界'),('valuation','自然物估价与损坏账本'),
    ('options','步行与加工品方案比较'),('itinerary','多步次数与资源账本'),
    ('transition','主层与秘境转移条件'),('residents','居民位置与路线风险候选'),
    ('settlements','战斗基础奖励与路线分项'),
    ('compare-routes','多路线费用与战斗收益比较'),
    ('search-routes','有限声明图的路线候选构造'),
)
QUERIES = {'calibration': CALIBRATION_QUERIES, 'battle': BATTLE_QUERIES,'exploration':EXPLORATION_QUERIES}
PRODUCT_QUERIES={family:tuple(row for row in rows if family!='exploration' or row[0] not in HISTORICAL_ROUTE_QUERIES)
                 for family,rows in QUERIES.items()}
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
    'regen-attributes':'attributes逐次声明属性13/19读取。未脏直接独立decoded cache；脏值按有序完整注册库存、各getter正常/纳入资格与四桶FP重算，清脏先于raw/范围/缓存写入。名义三花值须独立确认黑板仍为来源参数，失败读取仅正常TryFP后回默认0。每个时钟链接使用独立读取ID，数值未变不替代下一次正常返回；库存不全仅列所提供项，不推完整总量或下界。',
    'regen-clock':'recovery独立声明Precise定时器与FP读点；update按声明delta推进，dirty仅13/19，先结旧定时器，再分别读取能否回复与新周期的快照。每次HP读点独立，不由上次请求推后续HP；正常返回资格、周期与剩余数值不证明实际时钟或最终回血。属性13/19来自独立读取，不借既有double藏品倍率推定。',
    'modifier-values':'packet声明一种family的固定藏品、独立入链值与实际包类型/目标/方向/不可改值标记。base_one先合并成一个模块，normal逐模块乘；预处理与修饰顺序分开，留空列有限声明组合，不赋概率。BB对象缺失与数字失败分开，成功0/负值不夹正。接爆炸返回须独立声明修饰器存在及入链值未变；不是实际命中或生命结算。',
    'shield-grants':'仅机械师二技能。scenario为当前等级、模组、藏品等培养条件；snapshots逐受益对象声明创建时MAX_HP或本体模型小计。结构性原理不得借本体HP。分别列倍率、FP乘积、单精度写入与读回；null为未知，成功读取0不改用默认1。仅数值参考，不证明新盾已建立。',
    'shield-inventory':'仅机械师二技能。inventory逐实例声明读取点、身份、结束/来源/hasShield资格与独立FP值或黑板float32。自动计算本体来源及受击者自身来源总原值与双筛选门；mask不参与。未读全、黑板对象缺失或读值未知则完整总量未知。已证分项不是下界，不操作游戏、不自动建立或删除盾。',
    'explosion-values':'仅机械师二技能。两次来源攻击读取、两次前置事件后的AttackInfo/法抗及晚期originAtk快照独立声明。计算FP攻击加项门、穿透法抗、0.01f顺序和5%下限；技能倍率和ONE基准分列。快照与无变化条件互斥；不是实际modifier接受、命中或生命损失。',
    'barrier-ledger':'仅机械师二技能。按声明顺序计算本体和结构性原理的吸收、破屏及共享耗弹参考。原值单位2^32；各门条件true/false/null分别表示声明成立/不成立/未知。两次主buff门独立；后续屏障须独立声明，不凭补盾请求推定已建立。输入为公共条件算例，不能代替实机观察。',
    'relic-panels':'scenario声明当前培养、技能和藏品。relic_ids选择其中1–12件审计，留空审计全部；未选来源作为共同背景。并列移除单件/仅保留单件的模型差值，定向强化独立保留。零差值与非相加残差不证明实际机制或偏差原因。',
    'search-routes':'goal为声明终点，逐边步行并列举加工品候选；max_steps/max_results/max_transitions控制有限搜索。battle_declarations按节点声明独立关卡和胜利。随机落点、未知资格和AP到零保留停止前沿，不补完整收益或真实最优。',
    'compare-routes':'routes为1–20条带唯一id的明确路线，每条steps只含mode/target和可选battle。battle独立声明精确关卡/入口/胜利；不是胜利预测。共同graph、行动力和库存不随自动刷新覆盖。只比较同终点的已证净AP及基础战斗收益，不穷举概率或替代真实最优。',
    'settlements':'steps每项使用精确stage_id/stage_ids，或graph中的target。battle_floor是战斗所属主层，秘境编号不代替；entry_context需要unknown/map_battle/event_battle/pursuit。仅声明胜利后的基础分项，实际胜利和完整奖励未知。steps留空（null）只列图中当前战斗身份参考；不读取本局库存。',
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
    'mechanism': 'stage_id、enemy_id、level 选择关卡敌人。resource_plan 是基础共享技力请求账本；prefab_gate_plan 可声明scope=gated_baseline_skill_starts与requests启动序列，另受具体次数门约束；每项可为招式标识（声明启动成功）或{skill,ability_start_success}明确失败。starting_counts、starting_sp或starting_sp_raw仅为指定参考。数值门通过后先扣费，启动成功才增加次数，失败分支不在本函数立即退费。不加回复或时间，不证明实际施放。具体预制体、原等级及覆盖分别保留；实际附着、脚本、热更新与时钟未知。',
    'compare': 'left_stage/right_stage 与 left_level/right_level 分别指定两组条件；run_config/right_run_config 为局外环境。比较已支持环境小计，完整有效面板仍未知。',
}
INPUT_GUIDANCE.update({
    'items':'列固定原件全部30零件。kind可选MOVE、GOODS、PASSIVE；目录不代表实际持有。',
    'targets':'graph为声明地图，item_id为加工品；remaining_uses可声明余次数。未知资格仍保留候选，无生成概率。',
    'effects':'明确target后逐项显示移动资源与passive_items概念体条件。结果不更新实际持有或战斗数值。',
    'zones':'列全部26个原区域ID；同名秘境分别保留。区域目标、主层追猎和秘境返回不同。',
    'budget':'zone_id选择区域；声明action_points和walking_steps或item_id。付款到零与后续奖励分别显示，真实顺序未知。',
    'valuation':'item_id选择自然物；events逐项声明独立触发次数和完美作战状态。随机变化、损坏和实际售价分别保留。',
    'options':'graph、target与inventory声明图和独立加工品实例。羽瞰点需node.light_arrival_declaration明确first_entry与reward_received；历史访问不补状态。difficulty和split_unlocked只为揭示数量参数；不猜几何。返还不能透支付款。',
    'itinerary':'steps每步使用mode（walking或库存实例ID）和target。首次羽瞰点组件只在临时账本记领；AP到零或到达AP未知会截断可续行推导，尾链保留独立声明参考。实际结果与领取不自动取得。',
    'transition':'transition选择主层前进、秘境进入或返回。主层需exit_node_type；暂存品、剩余AP、FINAL等量希望参考与其他出口未知比率分开。',
    'residents':'声明graph与可选据点/居民位置，moves为1–10。连通距离5以内初始候选、每步候选和路线交集不等于实际占领。',
})
LABELS = {**calibration.LABELS, 'maxHp': '生命上限', 'atk': '攻击力',
    'def': '防御力', 'magicResistance': '法术抗性', 'attackSpeed': '攻速属性',
    'baseAttackTime': '基础攻击间隔', 'moveSpeed': '移动速度',
    'massLevel': '重量', 'hpRecoveryPerSec': '每秒生命回复',
    'epResistance': '元素抗性', 'epDamageResistance': '元素伤害抗性'}
VALUE_NAMES = {'physical': '物理', 'magic': '法术', 'true': '真实',
    'main_floor_normal':'主层普通作战','main_floor_emergency':'主层紧急作战','main_floor_boss':'主层险路恶敌',
    'portal_normal':'秘境普通作战','portal_emergency':'秘境紧急作战','portal_boss':'秘境险路恶敌参考',
    'named_special_battle':'具名事件/特殊战斗','ordinary_pursuit':'普通追猎','boss_pursuit':'首领追猎',
    'main_floor_boss_pursuit':'主层首领追猎','portal_boss_pursuit':'秘境首领追猎数值未知',
    'matched':'已列条件相符','unknown':'资格未确认','excluded':'已列条件不符',
    'no_exact_current_or_declared_stage_identity':'没有精确当前或声明关卡ID',
    'unresolved_current_stage_identity':'当前关卡身份不相符或尚未收录',
    'entry_or_origin_floor_or_variant_unresolved':'入口、战斗所属主层或同名变体未确认',
    'victory_not_declared':'未独立声明胜利条件','base_experience_not_documented':'基础指挥经验未证',
    'base_gold_not_documented':'基础源石锭未证','no_current_battle_identity_in_declared_graph':'声明图没有提供当前战斗身份',
    'healing': '治疗', 'Front': '正面', 'Back': '背面', 'WALK': '地面',
    'FLY': '飞行', 'start': '起点', 'end': '终点', 'move': '移动检查点',
    'appear': '再出现', 'disappear': '消失', 'main_queue': '主队列',
    'conditional_branch': '条件分支', 'initial_record': '初始记录',
    'database_level': '敌人数据库', 'stage_override': '关卡覆盖记录',
    'exact_alias': '唯一别名对应', 'empty_key': '空键，未绑定',
    'ambiguous_alias': '同名多个实体，未确认', 'unresolved_alias': '未找到对应实体',
    'elapsed_fragment_time': '当前片段计时条件', 'arrival_local_wait': '到达后的局部等待',
    'OnAttack': '攻击事件（命中未核验）','MOVE':'加工品','GOODS':'自然物','PASSIVE':'概念体',
    'hope':'希望','gold':'源石锭','ap':'行动力','shield':'护盾',
    'battle_attack_speed_reference':'战斗攻速资料','random_relic':'随机藏品',
    'main_region_advance':'进入下一主区域','portal_enter':'进入秘境','portal_return':'返回原区域',
    'processed_item':'加工品','walking':'步行','same_position_reentry_reference':'同格再进入参考',
    'conditional_reference_step':'声明条件下参考步骤','blocked':'已列条件阻断',
    'unresolved':'条件未知，停止依赖链','not_evaluated_after_stop':'前序停止，尚未求值',
    'zero_ap_callback_order_unverified':'付款到零，耗尽与返还顺序未证',
    'node_arrival_ap_condition_unknown':'到达节点AP条件未明确'}
VALUE_NAMES.update({'transition_limit':'分支检查上限','result_limit':'结果数量上限','depth_limit':'步数上限','action_points_unknown':'起始行动力未明确','known_condition_or_ap_failed':'已列资格不符或AP不足','eligibility_or_inventory_condition_unknown':'资格、次数或随机目的地未证'})
VALUE_NAMES.update({'arrival_chain_unresolved_or_blocked':'到达依赖链未知或被已列条件阻断','repeated_battle_reward_eligibility_unknown':'同节点再次作战奖励资格未证','declared_battle_not_won':'声明战斗未胜利，不证明后续成功路线','different_declared_goal':'声明终点不同，不作分项支配比较','component_conditions_not_closed':'声明分项条件未全部闭合'})



def exploration_examples():
    return json.loads((Path(__file__).with_name('data')/'exploration-examples.json').read_text(encoding='utf8'))


def exploration_presets(command):
    return [{'id':'default','label':'基本公开声明示例','payload':exploration_examples()['examples'][command]},
            *exploration_examples().get('variants',{}).get(command,[])]


def _finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError('输入不能包含无穷或非数值。')
    if isinstance(value, dict):
        for item in value.values(): _finite_tree(item)
    elif isinstance(value, list):
        for item in value: _finite_tree(item)


def run_offline_query(family, command, payload, *, include_historical_route_diagnostics=False):
    require_query_scope(family,command,include_historical_route_diagnostics)
    """Public synchronous entry point used by a worker and public-fixture tests."""
    if not isinstance(payload, dict): raise ValueError('条件必须是 JSON 对象。')
    _finite_tree(payload)
    commands = calibration.COMMANDS if family == 'calibration' else BATTLE_COMMANDS if family == 'battle' else exploration_planning.COMMANDS if family=='exploration' else {}
    if command not in commands: raise ValueError('没有这个离线查询。')
    try:
        return commands[command](**deepcopy(payload))
    except TypeError as error:
        raise ValueError('条件字段缺失、类型不正确或含有此查询不支持的字段。技术原因：'+str(error)) from None


def public_payload(family, command):
    """No private state: defaults come from the pinned public data only."""
    if family=='exploration':return deepcopy(exploration_examples()['examples'][command])
    if family == 'calibration':
        if command == 'regen-attributes':
            from .recovery_attributes import public_example
            return {'attributes':public_example()}
        if command == 'regen-clock':
            from .regeneration_clock import public_example
            return {'recovery':public_example()}
        if command == 'modifier-values':
            from .modifier_packet_reference import public_example
            return {'packet':public_example()}
        if command == 'explosion-values':
            from .mechanist_explosion_math import public_example
            return {'explosion':public_example()}
        if command == 'shield-inventory':
            from .shield_source_inventory import public_example
            return {'inventory': public_example()}
        if command == 'shield-grants':
            from .mechanist_shield_grants import public_snapshots
            return {'scenario':{'operator':'mechanist','skill':2,'relic_ids':['rogue_6_relic_legacy_27']},'snapshots':public_snapshots(),
                'ordinary_native_path':True,'float_rounding':'nearest_even'}
        if command == 'barrier-ledger':
            from .mechanist_barrier_ledger import public_example
            return {'ledger': public_example()}
        scenario = {'operator': 'mechanist', 'skill': 3, 'charge_count': 0}
        payload = {'scenario': scenario}
        if command == 'worksheets': return {}
        if command == 'relic-panels':
            payload['scenario']['relic_ids']=['rogue_6_relic_legacy_27','rogue_6_relic_legacy_29','rogue_6_relic_legacy_12']
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


def _fp_amount(raw, digits=None):
    from decimal import Decimal, localcontext
    if raw is None:return '未知'
    with localcontext() as ctx:
        ctx.prec=80
        number=Decimal(raw)/Decimal(1<<32)
        text=format(number,'f' if digits is None else '.'+str(digits)+'f')
        approximate=Decimal(text)!=number
    text=text.rstrip('0').rstrip('.') if '.' in text else text
    return ('≈' if approximate else '')+text


def _explosion_tables(data):
    def amount(raw):return _fp_amount(raw,8)
    parts=[_p('技能等级：'+str(data['skill_rank'])+'；倍率参考：'+amount(data['scale_raw_reference'])+
        '；半径读取参考：'+_text(data['radius_float32_reference'])),
        _p('两次来源攻击读取均在首个回调前。基准分支仍触发目标事件；下列都是独立声明。')]
    for row in data['rows']:
        parts += [_h(row['id']+' · 两次计算分列'),
            _table(['分支','攻击乘积','采用加项','最终攻击','有效法抗','最低伤害','计算返回参考'],
                [('技能倍率分支' if key=='scaled' else 'ONE基准分支',
                  *[amount((branch['numeric_reference'] or {}).get(field)) for field in
                    ('atk_product_raw_reference','used_addition_raw_reference','final_atk_raw_reference',
                     'effective_res_raw_reference','minimum_damage_raw_reference','calculate_damage_raw_reference')])
                 for key,branch in row['branches'].items()]),
            _p('晚期来源攻击参考：'+amount(row['origin_atk_raw_reference'])+'；实际伤害修改器值、命中及生命损失：未知。')]
    parts += [_p('已证技能分支小计：'+amount(data['known_scaled_damage_raw_subtotal'])+
        '；所声明调用总参考：'+amount(data['declared_calls_scaled_damage_raw_total'])),
        _p('≈表示仅显示到8位小数；完整定点原值保留在技术详情。'),
        _p('采用原值定点顺序与单精度常量；这些数值不代表全爆炸伤害、实际目标数或实机时钟。')]
    return parts


def _recovery_attribute_tables(data):
    amount=lambda raw:_fp_amount(raw,8)
    statuses={'unqualified_source_or_instance':'来源/实例资格未核准','unknown_instance':'实例存在未知',
        'independent_decoded_cache':'独立已解密缓存','unknown_dirty_branch':'缓存与重算分支未确认',
        'unqualified_calculation':'重算条件未完整声明','unqualified_enumeration':'枚举/修饰器访问未证正常',
        'unqualified_raw_read':'原值读取未证正常','unqualified_range_read':'范围读取未证正常',
        'recomputed':'声明条件下重算','unqualified_cache_store':'缓存编码/写入未证正常'}
    buckets=('addition','multiplier_delta','final_addition','final_scaler')
    headings=['前置加值','基准1+倍率增量','后置加值','末尾乘算']
    parts=[_p('来源核验：'+_text(data['source_valid'])+'；属性13/19独立读点，不凭藏品持有推注册、缓存脏标或实际属性。'),
        _p('实际属性、后续缓存/脏标状态、实际时钟与完整生命结算：未知。')]
    for row in data['rows']:
        parts += [_h(row['id']+' · '+('固定生命回复' if row['attribute']==13 else '最大生命比例回复')),
            _p(statuses[row['status']]+'；正常返回：'+_text(row['normal_return_reference'])+'；本次清脏步骤执行：'+_text(row['dirty_cleared_reference'])),
            _table(['最终getter参考','精确原值','缓存写入值参数（参考）'],
                [(amount(row['getter_raw_reference']),_text(row['getter_raw_reference']),amount(row['cache_write_value_argument_raw_reference']))])]
        if row.get('listed_buckets_reference') is not None:
            parts += [_table(['聚合范围',*headings],[(label,*[amount(values[k]) for k in buckets]) for label,values in
                [('所列项',row['listed_buckets_reference']),('完整库存',row['buckets_reference'])] if values is not None]),
                _p('完整范围限制前值：'+amount(row.get('pre_clamp_raw_reference'))+'；缓存写入前数值参考：'+amount(row.get('computed_clamped_raw_reference'))+'。所列项不是下界。')]
        loads=[s['flower_load'] for s in row.get('steps',[]) if s.get('flower_load') is not None]
        if loads:parts += [_table(['藏品来源','buff索引','加载正常','倍率增量FP参考','与当前缓存关联已确认'],
            [(s['name'],s['source_buff_index'],s['load_normal_reference'],amount(s['loaded_multiplier_raw_reference']),s['cache_link_qualified']) for s in loads])]
    if data['clock_reference'] is not None:
        parts += [_h('两个独立读点接入周期参考'),_p('每次getter调用分别声明正常返回；不会覆盖已有快照或复用同一读取ID。')]
        parts += _regeneration_tables(data['clock_reference'])
    return parts


def _regeneration_tables(data):
    amount=lambda raw:_fp_amount(raw,8)
    statuses={'invalid_timer_skipped':'旧定时器无效，保留状态','unknown_timer_validity':'定时器有效性未知',
        'declared_timer_reference':'声明条件下的定时器参考','unknown_ready_gate':'到期门未知',
        'missing_independent_hp_access':'缺独立HP读取/返回资格，未补造后续请求',
        'unqualified_hp_access':'HP访问未证正常返回，停止后续链','marked_invalid':'资格不成立，标记无效',
        'reset_keep_past':'保留已过时间后改速','unqualified_period_read_or_division_domain':'周期读点或除法域未核准',
        'unknown_can_recover_gate':'回复资格未知','unqualified_attribute_reads':'属性读取未证正常返回',
        'not_called_after_unqualified_chain':'前序或来源资格未核准，未继续'}
    parts=[_p('来源核验：'+_text(data['source_valid'])+'；定时器使用Precise类型，保留逾期量，逐点请求HP+1。'),
        _p('声明链完整：'+_text(data['declared_chain_complete'])+'；声明范围请求次数：'+_text(data['declared_complete_request_count'])),
        _p('最终周期参考：'+amount(data['final_period_raw_reference'])+'秒；最终剩余参考：'+amount(data['final_remaining_raw_reference'])+'秒。实际生命值、实际回复总量及实机时钟：未知。')]
    for row in data['rows']:
        parts += [_h(row['id']),_p(statuses[row['status']]+'；正常返回：'+_text(row['normal_return_reference'])),
            _table(['定时器','周期（秒）','剩余（秒）'],[(label,amount(row[p]),amount(row[r])) for label,p,r in
                [('操作前','period_before_raw_reference','remaining_before_raw_reference'),('操作后','period_after_raw_reference','remaining_after_raw_reference')]])]
        if row['can_recover'] is not None:
            parts += [_table(['独立读取用途','每秒回复FP参考','最大生命比例分项','正常返回'],
                [(label,amount(ref['rate_raw_reference']),amount(ref['ratio_part_raw_reference']),ref['normal_return_reference'])
                 for label,ref in [('能否回复',row['can_recover']),('新周期',row['period_rate'])] if ref is not None]),
                _p('能否回复：'+_text(row['can_recover_hp_reference'])+'；第二次读取不借用第一次数值。')]
        reset=row['reset_keep_past_reference']
        if reset is not None:parts += [_p('旧周期已过时间：'+amount(reset['past_raw_reference'])+'秒；新剩余先减后夹零：'+amount(reset['clamped_remaining_raw_reference'])+'秒。')]
        drain=row['drain']
        if drain is not None:
            parts += [_table(['读点','独立HP读值','HP+1请求参数','请求参数精确原值','Next后剩余秒','HP访问正常返回'],
                [(s['index']+1,amount(s['hp_read_raw_reference']),amount(s['setter_value_argument_raw_reference']),
                  _text(s['setter_value_argument_raw_reference']),amount(s['remaining_after_next_raw_reference']),s['hp_access_normal_return_reference']) for s in drain['requests']]),
                _p('本操作完整请求次数：'+_text(drain['declared_complete_request_count'])+'；请求参数不是最终HP。')]
    parts += [_p('仅属性13/19脏标分支；其它属性、藏品实际FP组合、运行实例/热更新及实际HP接受仍未知。未安排事件或操作游戏。')]
    return parts


def _modifier_tables(data):
    families={'healing':'受治疗修饰','physical':'物理承伤修饰','magic':'法术承伤修饰','true':'真实承伤修饰','elemental':'元素伤害修饰'}
    source_names={r['relic_id']:r['name'] for r in data['selected_sources']}
    definitions=data['module_definitions']
    amount=lambda raw:_fp_amount(raw,8)
    statuses={'skipped':'未执行修饰','missing_blackboard_exception':'黑板对象缺失，异常路径',
        'unknown_execution_or_blackboard':'执行资格或黑板未确认','conditional_reference':'声明条件下的数值',
        'unknown_numeric_or_setter':'数字或写入门未确认','unqualified_float_conversion':'浮点转换正常返回未核验',
        'not_called_after_unqualified_chain':'前序未证正常返回，未继续'}
    known=data['known_discrete_raw_references'];low=known[0] if known else None
    parts=[_p('类型：'+families[data['family']]+'；来源核验：'+_text(data['source_valid'])),
        _p('独立修饰模块：'+str(len(definitions))+'；有限声明顺序组合：'+str(data['declared_order_combination_count'])+'。组合数量不是概率，也不证明实际顺序可达。'),
        _h('离散数值参考'),_table(['定点原值','显示值（8位）','距最小候选的原值差'],
            [(raw,amount(raw),raw-low) for raw in known]),
        _p('所有声明组合数值齐全：'+_text(data['all_declared_cases_numeric'])+'；所声明链的唯一参考：'+amount(data['single_declared_chain_raw_reference'])),
        _p('1个定点原值单位为2⁻³²；≈仅为显示舍入。候选之间不补中间值、不取平均，实际伤害/治疗及生命结算未知。')]
    for index,case in enumerate(data['cases'],1):
        acquisition=' → '.join(source_names.get(k,'来源未核验') for k in case['preprocessing_order'])
        application=' → '.join(definitions[k]['name'] for k in case['application_order'])
        parts += [_h('声明组合'+str(index)),_p('黑板预处理：'+acquisition+'；修饰应用：'+application),
            _table(['模块','进入值','倍率','尝试写入','保留值','正常返回','状态'],
                [(s['name'],amount(s.get('input_raw_reference')),amount(s.get('factor_raw_reference')),
                  amount(s.get('attempted_raw_reference')),amount(s.get('stored_raw_reference')),
                  s['normal_return_reference'],statuses[s['status']]) for s in case['steps']]),
            _p('链正常返回：'+_text(case['normal_return_reference'])+'；声明范围链值：'+amount(case['declared_chain_raw_reference']))]
    return parts


def _shield_inventory_tables(data):
    amount=_fp_amount
    status_names = {'declared_getter_result':'独立getter返回声明', 'unknown_getter_result':'getter结果未知',
        'unknown_blackboard_read':'黑板读取未知', 'unqualified_data_path':'直接分支未核准',
        'missing_blackboard_exception_path':'黑板对象缺失，异常路径',
        'explicit_failed_numeric_lookup_default_zero':'明确数字读取失败，采用0',
        'numeric_reference':'单精度数值转FP', 'unqualified_or_missing_float32_value':'单精度值缺失或超出支持域'}
    filters = data['source_filters']
    parts = [_p('快照：'+data['snapshot_id']+'；读取点：受击处理后的来源筛选；声明读全：'+_text(data['inventory_complete_declaration'])),
        _h('按来源汇总与双筛选门'),
        _table(['筛选来源','完整屏障值','已证分项（回绕后）','完整总原值对照','发生回绕','小于零阈值','正常返回'],
            [('机械师来源' if role=='caster' else '受击者自身来源', amount(row['total_raw_reference']),
              amount(row['known_wrapped_raw_subtotal']),row['total_raw_reference'],row['signed_wrap_occurred'],
              row['filter_le_zero_reference'],row['normal_return_reference']) for role,row in filters.items()]),
        _p('双筛选通过参考：'+_text(data['both_filters_pass_reference'])+'；零阈值FP原值42950，严格小于才通过。'),
        _p('第二道筛选被调用：'+_text(data['recipient_filter_called_reference'])+'；筛选链正常返回：'+_text(data['ordered_filters_returned_reference'])),
        _p('已证分项不是下界；库存不完整或贡献未知时，完整总量保留未知。')]
    for role, row in filters.items():
        parts += [_h(('机械师来源' if role=='caster' else '受击者自身来源')+' · 逐实例资格与贡献'),
            _table(['实例','来源相同','实例存在','结束或禁用','屏障标志','计入资格','独立屏障值','本项贡献','读取说明'],
                [(r['id'],r['source_matches'],r['buff_reference_present'],r['finished_or_disabled'],r['has_shield'],
                  r['eligible_reference'],amount(r['value_reference']['raw_reference']),amount(r['contribution_raw_reference']),
                  status_names[r['value_reference']['status']]) for r in row['rows']])]
    parts += [_p('伤害类型mask不参与来源筛选；补盾与结束请求不改变本库存。实际库存、取消结果与时钟：未知。')]
    return parts


def _node_label(graph,node_id):
    node=next((n for n in (graph or {}).get('nodes',[]) if isinstance(n,dict) and n.get('id')==node_id),None)
    if node is None:return str(node_id)+'（位置未绑定）'
    row,col=node.get('row'),node.get('col')
    position=f'第{row+1}行、第{col+1}列' if type(row) is int and type(col) is int else '位置未明确'
    raw=node.get('base_node_type') or node.get('node_type_raw')
    if not isinstance(raw,str):raw=None
    name=node.get('observed_type') or exploration_planning.reference_data()['node_types'].get(raw,{}).get('name') or '类型未知'
    return f'{position} · {name} · {node_id}'


def result_node_ids(command,data):
    if command=='search-routes':
        keys={data.get('start'),data.get('goal_node')}
        for row in data['plans']+data['frontier']:
            keys.update(step['target'] for step in row['steps'])
        if data['comparison']:keys.update(result_node_ids('compare-routes',data['comparison']))
        return {key for key in keys if isinstance(key,str)}
    keys={data.get('start'),data.get('target'),data.get('nominal_position'),data.get('post_node')}
    for row in data.get('targets',[])+data.get('excluded',[])+data.get('spawn_candidates',[]):keys.add(row.get('node_id'))
    for row in data.get('steps',[]):keys.update((row.get('start'),row.get('target')))
    if command=='settlements':keys.update(row.get('node_id') for row in data['rows'])
    if command=='compare-routes':
        for route in data['routes']:
            keys.add(route['goal_node'])
            for row in route['movement_reference']['steps']:
                keys.update((row.get('start'),row.get('assumed_start_from_declared_plan'),row.get('target')))
                keys.update((row.get('option') or {}).get('path',[]))
    for resident in data.get('movement_candidates',[]):
        keys.add(resident.get('initial_position_declared'))
        for step in resident.get('steps',[]):keys.update(step['candidate_positions'])
    for path in (data.get('walking_paths') or {}).values():
        if path:keys.update(path['path'])
    return {key for key in keys if isinstance(key,str)}


def render_offline_result(family, command, data, *, graph=None, map_link_nodes=None, input_source=None):
    """Readable main output; technical fields stay available in a collapsed pane."""
    title = dict(QUERIES[family])[command]
    parts = ['<html><body>', '<h2>'+_esc(title)+'</h2>',
        _p('局外声明条件 / 固定公开配置参考。尚未验证当前客户端实机；未知不等于0。')]
    if data.get('operator'): parts.append(_p('干员：'+data['operator']))
    if data.get('stage_name'): parts.append(_p('关卡：'+data['stage_name']))
    if input_source:parts.append(_p('此次输入来源：'+input_source))
    if family == 'calibration':
        if command == 'regen-attributes':
            parts += _recovery_attribute_tables(data)
        elif command == 'regen-clock':
            parts += _regeneration_tables(data)
        elif command == 'modifier-values':
            parts += _modifier_tables(data)
        elif command == 'explosion-values':
            parts += _explosion_tables(data)
        elif command == 'shield-inventory':
            parts += _shield_inventory_tables(data)
        elif command == 'barrier-ledger':
            from .mechanist_barrier_ledger import ONE
            def amount(value):return '未知' if value is None else format(value / ONE, '.10g')
            parts += [_p('来源核验：'+_text(data['source_valid'])+'；各数值为声明条件下的参考。'),
                _h('即时吸收算式'),
                _table(['序号 / 入伤','受击对象','声明入伤','盾前值','吸收','盾后值','修改器中间值','耗尽门'],
                    [(f"{r['ordinal']} · {r['id']}",r['recipient_name'],amount(r['input_raw']),
                      amount(r['barrier_before_raw']),amount(r['absorbed_raw']),amount(r['barrier_after_block_raw']),
                      amount(r['modifier_after_block_raw']),r['depletion_gate']) for r in data['rows']]),
                _h('后续请求与共享弹匣'),
                _table(['入伤','溢出取消请求','爆炸请求','补盾请求','参考耗弹','参考剩余','旧盾结束请求'],
                    [(r['id'],r['overflow_cancel_requested'],r['explosion_requested'],r['replenishment_requested'],
                      r['ammunition_consumed_reference'],r['ammunition_remaining_reference'],r['finish_old_barrier_requested']) for r in data['rows']]),
                _p('已证吸收分项：'+amount(data['known_absorbed_raw_subtotal'])+'；全部吸收参考：'+amount(data['absorbed_raw_total'])),
                _p('实际生命损失、爆炸命中、新盾创建与技能结束时刻：未知。')]
            for row in data['rows']:
                if row['source_shield_inventory_reference'] is not None:
                    parts += [_h(row['id']+' · 独立受击后库存')] + _shield_inventory_tables(row['source_shield_inventory_reference'])
                if row['explosion_fp_reference'] is not None:
                    parts += [_h(row['id']+' · 已请求爆炸的独立数值')] + _explosion_tables(row['explosion_fp_reference'])
        elif command == 'shield-grants':
            from .barrier_blackboard import ONE
            def amount(value):return '未知' if value is None else format(value/ONE,'.12g')
            parts += [_p('来源核验：'+_text(data['source_valid'])+'；技能等级：'+str(data['skill_rank'])),
                _h('创建节点数值参考'),
                _table(['快照','受益对象','生命输入依据','MAX_HP参考','倍率参考','FP即时乘积','黑板读回屏障'],
                    [(r['id'],r['recipient_name'],'本体已覆盖模型小计' if r['basis']=='owner_model_known_subtotal' else '独立FP快照声明',
                      amount(r['max_hp_snapshot_raw_reference']),amount(r['ratio_raw_reference']),
                      amount((r['numeric_reference'] or {}).get('product_raw')),amount(r['shield_readback_raw_reference'])) for r in data['rows']]),
                _h('单精度写回与资格'),
                _table(['快照','初始化门','明确读取失败采用1','单精度写入值','读回减即时乘积（FP原值）'],
                    [(r['id'],r['initialization_gate'],r['default_one_used_reference'],
                      (((r['numeric_reference'] or {}).get('storage') or {}).get('stored_float32')),
                      (((r['numeric_reference'] or {}).get('storage') or {}).get('readback_minus_math_raw'))) for r in data['rows']]),
                _p('实际创建屏障、实例初始化完成与创建时刻：未知。')]
        elif command == 'panel':
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
        elif command == 'relic-panels':
            parts += [_p('干员：'+data['operator']),_p('共同背景藏品：'+_text(data['background_relic_ids'])),
                _p('独立保留的定向强化：'+_text(data['preserved_targeted_buff_ids'])),
                _p('下面均为当前模型差值；实际加成、实际偏差原因及完整实机面板仍未知。'),
                _table(['面板层','属性','组合模型值','共同背景值','组合差值','单件背景增量之和','非相加模型残差'],
                    [(r['panel'],r['label'],r['combined_model_reference'],r['background_model_reference'],r['combined_model_difference'],
                        r['sum_single_background_model_differences'],r['nonadditive_model_residual']) for r in data['combination_rows'] if r['panel']!='培养与模组'])]
            for source in data['source_rows']:
                parts += [_h(source['name']),_p('固定机制记录：'+_text(source['fixed_mechanic_record_available'])),
                    _table(['面板层','属性','组合值','移除后值','移除单件边际差值','共同背景加单件值','单件背景增量'],
                        [(r['panel'],r['label'],r['combined_model_reference'],r['without_source_model_reference'],r['marginal_model_difference'],
                            r['single_source_background_model_reference'],r['single_background_model_difference']) for r in source['fields'] if r['panel']!='培养与模组']),
                    _p('移除单件后的警告：'+_text(source['without_source_warnings'])),
                    _p('共同背景加单件的警告：'+_text(source['single_source_warnings']))]
            parts += [_p('当前组合警告：'+_text(data['full_warnings'])),_p('共同背景警告：'+_text(data['background_warnings']))]
        elif command == 'worksheets':
            parts += [_p(f"公式参考算例 {data['case_count']} 组；相符 {data['matching_reference_cases']} 组。不是公开实机成对验收。"),
                _table(['算例','干员','比较属性','预测','公式参考','差值','在声明容差内'],
                    [(row['id'],row['comparison']['operator'],r['label'],r['predicted'],r['observed'],r['difference'],r['matches_declared_tolerance']) for row in data['rows'] for r in row['comparison']['rows']])]
    elif family=='exploration':
        label=lambda key:_node_label(graph,key)
        if command=='search-routes':
            parts += [_p('明确终点：'+label(data['goal_node'])),
                _p('仅构造声明图中的不重复节点计划；每条步行连线分别核算，不以跨中途节点的捷径漏掉节点组件。'),
                _table(['已检查分支','所得终点候选','深度截断前缀','上限停止原因','等待前缀'],
                    [(data['examined_transitions'],len(data['plans']),data['depth_limited_prefixes'],data['limit_reason'] or '未触发上限',data['pending_prefixes_at_limit'])]),
                _table(['停止位置','声明路径','未证或受阻原因','实际能否续行'],
                    [(label(row['node_id']),[label(step['target']) for step in row['steps']],row['reason'],row['actual_continuation']) for row in data['frontier']]),
                _p('实际终点可达性与最优路线：未知。没有候选不证明没有实际路线；上限与未知前沿会遗漏后续方案。')]
            if data['comparison']:
                parts.append(render_offline_result('exploration','compare-routes',data['comparison'],graph=graph))
        elif command=='compare-routes':
            parts += [_p('每条路线独立使用共同声明的地图、行动力和库存；不更新本局。'),
                _p('分项支配仅比较同终点的净行动力消耗、基础战斗经验和源石锭范围；范围只作保守端点比较，不取平均或赋概率。'),
                _table(['路线','声明终点','净行动力消耗参考','已知基础经验小计','已知基础源石锭范围','声明分项齐全','分项支配来源'],
                    [(r['name'],label(r['goal_node']),r['net_ap_consumption_reference'],r['known_base_subtotal']['experience'],
                        gold_reference_text(r['known_base_subtotal']['gold']),r['closed_declared_component_reference'],r['component_dominated_by'])
                        for r in data['routes']])]
            for route in data['routes']:
                movement=route['movement_reference'];rewards={r['step']:r for r in route['battle_reward_rows']}
                rows=[]
                for step in movement['steps']:
                    reward=rewards.get(step['step']);ref=reward['base_reward_reference'] if reward else {}
                    rows.append((step['step'],label(step.get('start') or step.get('assumed_start_from_declared_plan') or movement['start']),
                        label(step['target']),step['status'],step.get('base_ap_cost'),step.get('stated_node_arrival_ap_grant'),
                        ref.get('victory_declared') if reward else '没有独立战斗声明',
                        ref.get('conditional_base_experience') if reward else '此项不列战斗收益',
                        gold_reference_text(ref.get('conditional_base_gold')) if reward else '此项不列战斗收益',
                        reward['admitted_to_known_base_subtotal'] if reward else '不适用'))
                parts += [_h(route['name']),_table(['步骤','声明起点','声明目标','移动参考状态','基础AP费用','首次到达返还','胜利条件','基础经验参考','源石锭范围','纳入已知战斗小计'],rows),
                    _p('移动停止边界：'+_text(movement['stopped_reason'])),
                    _p('声明基础分项总量：'+('仍有未知或失败条件' if route['conditional_base_total'] is None else '仅此声明范围的基础分项齐全'))]
                for gap in route['unknown_or_failed_conditions']:
                    parts.append(_p(f"步骤{gap['step']} · {label(gap['node_id'])}："+_text(gap['reasons'])))
            parts += [_p('实际最佳路线、当前服务器资格、完整奖励总量与真实成功率：未知。'),
                _p('未知或阻断后的尾链只保留独立奖励资料，不加入已知小计；同节点再次奖励未证。')]
        elif command=='settlements':
            parts += [_p('基础分项来自独立公开表，满级科技列只作参考；实际胜利、额外奖励和完整总量均未知。'),
                _p('已列条件相符仅针对声明的入口和战斗所属层，不证明服务器资格或实际会领取。'),
                _p('各声明战斗独立列分项；未评估路线可达性或失败后的续行条件。秘境表仅普通/紧急继承主层，首领/首领追猎空列数值未知。'),
                _table(['步骤/声明图节点','关卡候选','胜利声明','条件基础指挥经验','条件基础源石锭范围','未知边界'],
                    [(label(row['node_id']) if row['node_id'] else row['step'],row['stage_candidates'],row['victory_declared'],
                      row['conditional_base_experience'],gold_reference_text(row['conditional_base_gold']),row['unknown_components']) for row in data['rows']])]
            if data['automatic_graph_reference_only']:
                parts.append(_p('当前图战斗身份清单仅为并列参考；节点数组次序不表示路线、进入先后或胜利。'))
            for row in data['rows']:
                for reference in row['battle_references']:
                    parts += [_h(reference['stage_name']+' · '+reference['stage_id']),
                        _table(['来源入口','战斗所属主层','资料条件','基础经验','基础源石锭','满级科技经验参考'],
                            [(r['rule_kind'],r['source_battle_floor'],r['status'],r['base_experience_reference'],
                              gold_reference_text(r['base_gold_reference']),r['full_technology_experience_reference']) for r in reference['rows']])]
            parts += [_h('已闭合且声明胜利的基础分项小计'),
                _table(['分项','数量参考'],[('基础指挥经验',data['known_base_subtotal']['experience']),
                    ('基础源石锭',gold_reference_text(data['known_base_subtotal']['gold']))]),
                _p('基础分项仍有未知：'+_text(data['unknown_components'])),
                _p('实际完整奖励总量：未知；不将上述小计写入本局资源。')]
        elif command=='items':
            parts.append(_table(['零件','类别','原文用途','初始估价参数','加工品初始次数'],
                [(r['name'],r['kind'],r['usage'],r['raw']['sellPrice'],r['raw'].get('count')) for r in data['items']]))
        elif command=='targets':
            parts += [_p('起点：'+label(data['start'])),
                _table(['目的地','基础AP','类型条件相符','声明余次','次数可用','随机落点'],
                    [(label(r['node_id']),r['base_ap_cost'],r['node_type_matches'],r['remaining_uses_declared'],r['uses_available'],r['is_random_destination']) for r in data['targets']]),
                _p('已排除目的地：'+_text([label(r['node_id']) for r in data['excluded']]))]
        elif command=='effects':
            parts += [_p('目的地：'+label(data['target'])),
                _table(['移动资源','描述数量','声明条件相符','实际领取'],
                    [(r['resource'],r['amount'],r['condition_matches'],r['actual_granted']) for r in data['movement_grants']]),
                _table(['概念体','节点条件','次数可用','全部条件','效果资料','实际触发'],
                    [(r['name'],r['node_type_matches'],r['activation_available_declared'],r['condition_matches'],r['effects'],r['actual_activation']) for r in data['passives']]),
                _p('攻速只列战斗参考；实际新资源与完整随机池未知。')]
        elif command=='zones':
            parts.append(_table(['原区域ID','名称','目标','行动力耗尽提示'],
                [(r['zone_id'],r['name'],r['mission_text'],r['exhaustion_text']) for r in data['zones']]))
        elif command=='budget':
            parts += [_p(data['zone']['name']+' · '+data['zone']['mission_text']),
                _table(['AP参考项','数值'],[('声明AP',data['action_points_declared']),('基础付款',data['base_ap_cost']),
                    ('基础成本可负担',data['base_cost_affordable']),('付款后小计',data['nominal_ap_after_payment']),
                    ('描述移动AP奖励',data['source_stated_movement_ap_grant']),('奖励后小计',data['nominal_ap_after_stated_grant']),
                    ('付款到零边界',data['payment_zero_boundary']),('实际最终AP',data['actual_final_ap'])]),
                _table(['条件后果','适用条件','目标条件相符'],[(r['outcome'],r['condition'],r['goal_condition_matches']) for r in data['conditional_outcomes']])]
        elif command=='valuation':
            parts += [_p('自然物：'+data['item']['name']),
                _table(['事件次序','事件','独立次数','已证描述增量','事件状态','未知影响前小计'],
                    [(r['event_ordinal'],r['kind'],r['count_declared'],r['known_description_delta'],r['status'],r['subtotal_before_unknown_effects']) for r in data['events']]),
                _table(['估价项','参考'],[('原始/声明估价',data['initial_estimate_reference']),('算术小计',data['arithmetic_subtotal']),
                    ('条件估价',data['nominal_estimate']),('已声明损坏',data['destroyed_in_declared_ledger']),('实际售价',data['actual_sell_value'])]),
                _table(['尚未知事件','原因'],[(r['event_ordinal'],r['reason']) for r in data['unknown_effects']])]
        elif command=='options':
            parts += [_p('目的地：'+label(data['target'])),
                _table(['方案','移动方式','基础AP','声明条件相符','基础AP可负担','实际进入'],
                    [(r.get('name',r['id']),r['mode'],r['base_ap_cost'],r['known_conditions_match'],r['base_cost_affordable'],r['actual_entry_eligible']) for r in data['options']]),
                _p('最低基础AP候选：'+_text(data['minimum_base_cost_candidates'])+'；数值：'+_text(data['minimum_base_ap_cost_reference'])+'；实际最优路线未知。')]
            for mode,path in (data.get('walking_paths') or {}).items():
                if path:parts.append(_p('步行路径参考 '+mode+'：'+' → '.join(label(key) for key in path['path'])))
            parts += [_table(['方案','加工品AP参考','羽瞰点AP参考','付款后','列示奖励后','付款到零'],
                [(r.get('name',r['id']),r.get('item_ap_grant_reference'),r.get('node_arrival_reference',{}).get('node_arrival_ap_reference'),
                  r.get('nominal_ap_after_payment_reference'),r.get('nominal_ap_after_combined_grants_reference'),r.get('payment_zero_boundary_reference')) for r in data['options']])]
            if data.get('node_arrival_reference'):parts.extend(_p(line) for line in arrival_lines(data['node_arrival_reference']))
        elif command=='itinerary':
            parts += [_table(['步骤','目的地','状态','基础AP','移动AP奖励','付款后小计','奖励后小计'],
                [(r['step'],label(r['target']),r['status'],r.get('base_ap_cost'),r.get('stated_ap_grant'),r.get('nominal_ap_after_payment'),r.get('nominal_ap_after_stated_grant')) for r in data['steps']]),
                _p('名义最终位置：'+label(data['nominal_position'])+'；名义最终AP：'+_text(data['nominal_final_ap'])),
                _p('依赖链停止原因：'+_text(data['stopped_reason'])+'；实际最终库存未知。')]
            for row in data['steps']:
                arrival=row.get('node_arrival_reference')
                if arrival and arrival['original_type_matches_light'] is not False:
                    parts.append(_h('步骤 '+str(row['step'])+' · 节点到达AP'))
                    parts.extend(_p(line) for line in arrival_lines(arrival))
                    parts.append(_p('已证分项算术小计（不是完整终值）：'+_text(row.get('nominal_ap_after_known_grants_subtotal'))))
            tails=[r for r in data['steps'] if r['status']=='not_evaluated_after_stop']
            if tails:
                parts += [_h('保留的尾链独立声明参考'),
                    _p('这些行只假设前一个计划目标已到达；AP、库存与实际继续均未知，不表示已经续行或必然结束。'),
                    _table(['后续步骤','设想起点','目的地','声明mode','独立基础AP','实际继续'],
                        [(r['step'],label(r.get('assumed_start_from_declared_plan')),label(r['target']),
                          r.get('declared_step',{}).get('mode'),(r.get('independent_declared_option_reference') or {}).get('base_ap_cost'),r.get('actual_continuation')) for r in tails])]
        elif command=='transition':
            parts += [_p('转移：'+_text(data['transition'])),
                _table(['零件','主层成功后过期','秘境例外保留','已声明耗尽','实际保留'],
                    [(r['name'],r['expires_if_transition_succeeds'],r['preserved_by_portal_exception'],r['already_depleted_declared'],r['actual_retained']) for r in data['inventory_conditions']]),
                _table(['资源项','参考'],[('用于希望转换的剩余AP',data['resources']['source_rule_ap_conversion']),
                    ('携带到下一区域的AP',data['resources']['source_rule_carried_ap']),('希望数量',data['resources']['hope_gain']),
                    ('已证转换比率参考',data['resources'].get('hope_conversion_ratio')),('希望增量参考',data['resources'].get('hope_gain_reference')),
                    ('下一区域总AP',data['resources']['next_region_total_ap'])])]
        elif command=='residents':
            parts += [_table(['初始生成位置候选','连通距离','空地类型条件','据点门槛','实际生成'],
                [(label(r['node_id']),r['connected_distance'],r['initial_clearing_type_matches'],r['known_post_gate_matches'],r['actual_spawn']) for r in data['spawn_candidates']]),
                _p('来源人数上限3；候选数量上界：'+_text(data['initial_count_upper_bound'])+'；实际人数未知。')]
            for resident in data['movement_candidates']:
                parts += [_h('居民 '+resident['resident_id']),_table(['第几次移动后','位置候选','未证回退数','实际位置'],
                    [(r['movement_step'],[label(key) for key in r['candidate_positions']],len(r['unresolved_fallbacks']),r['actual_position']) for r in resident['steps']])]
            parts.append(_table(['移动次序','与声明玩家位置候选重合','实际碰撞/阻断'],
                [(r['movement_step'],r['source_candidate_overlap'],r['actual_collision_or_blockage']) for r in data['player_route_risk']]))
        if map_link_nodes:
            parts += [_h('定位已绑定来源图节点'),'<p>'+ '　'.join(
                '<a href="rouge-map-node:'+quote(key,safe='')+'">'+html.escape(label(key))+'</a>' for key in map_link_nodes)+'</p>']
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
            compiled=data.get('compiled_configuration')
            if compiled:
                from .enemy_configuration import construction_text
                parts += [_h('基包配置分项'),_p(construction_text(compiled))]
            resources=data.get('initial_skill_resources')
            if resources:
                from .enemy_skill_resources import skill_resource_text
                content=skill_resource_text(resources)
                if content:parts += [_h('共享技力数值门与声明预算'),_p(content)]
            prefab=data.get('prefab_skill_gates')
            if prefab:
                from .enemy_prefab_skill_gates import prefab_skill_text
                content=prefab_skill_text(prefab)
                if content:parts += [_h('具体预制体技能门与启动预算'),_p(content)]
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
    parts.extend(_p(n) for n in data.get('notes',[])+data.get('limits',[])+data.get('warnings',[])+data.get('additional_limits',[]))
    parts.append(_p('完整原始结果与来源记录保留在下方“技术详情”。'))
    parts.append('</body></html>')
    return ''.join(parts)


class _WorkerSignals(QObject):
    finished = Signal(int, str, str, object, str)


class _QueryWorker(QRunnable):
    def __init__(self, serial, family, command, payload, *, include_historical_route_diagnostics=False):
        super().__init__()
        self.serial,self.family,self.command,self.payload=serial,family,command,payload
        self.include_historical_route_diagnostics=include_historical_route_diagnostics
        self.signals = _WorkerSignals()

    def run(self):
        try:
            result=run_offline_query(self.family,self.command,self.payload,
                include_historical_route_diagnostics=self.include_historical_route_diagnostics);error=''
        except Exception as exc: result=None;error='离线查询失败：'+str(exc)
        self.signals.finished.emit(self.serial,self.family,self.command,result,error)


class OfflineToolsPanel(QWidget):
    """Qt panel with explicit imports; automatic context refresh is nondestructive."""
    resultChanged = Signal(object)
    mapNodeSelected = Signal(str,object)

    def __init__(self, parent=None, *, include_historical_route_diagnostics=False):
        super().__init__(parent)
        require_query_scope('exploration',None,include_historical_route_diagnostics)
        self.include_historical_route_diagnostics=include_historical_route_diagnostics
        self.queries=QUERIES if include_historical_route_diagnostics else PRODUCT_QUERIES
        self._scenario=None; self._stage=None; self._buffers={};self._views={};self._active_key=None;self._family_queries={}
        self._serial=0; self._workers={}; self._result=None; self._rendered=''
        self._graph_cache=None;self._graph_import=None;self._origin='公开声明示例；不是本局状态'
        self._result_graph=None;self._result_links={};self._worker_context={}
        self._changing=False
        layout=QVBoxLayout(self)
        row=QHBoxLayout()
        self.family=QComboBox();self.family.addItem('干员校准','calibration');self.family.addItem('固定关卡规划','battle');self.family.addItem('探索节点信息','exploration')
        self.query=QComboBox();row.addWidget(self.family);row.addWidget(self.query,1)
        layout.addLayout(row)
        row=QHBoxLayout();self.preset=QComboBox();self.preset.setAccessibleName('探索公开场景预置')
        self.import_graph=QPushButton('导入缓存地图声明')
        self.graph_node=QComboBox();self.graph_node.setAccessibleName('声明图目标或起点')
        self.fill_node=QPushButton('填写所选节点')
        for control in (self.preset,self.import_graph,self.graph_node,self.fill_node):row.addWidget(control)
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
        self.result_view=QTextBrowser();self.result_view.setOpenExternalLinks(False);self.result_view.setOpenLinks(False)
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
        self.import_graph.clicked.connect(self._import_graph)
        self.fill_node.clicked.connect(self._fill_node)
        self.graph_node.currentIndexChanged.connect(self._update_buttons)
        self.result_view.anchorClicked.connect(self._map_anchor)
        self.run_button.clicked.connect(self._run)
        self._family_changed()

    def current_query(self): return self.family.currentData(),self.query.currentData()

    def select_query(self, family, command):
        """Select a public query, preserving each declaration and reading state."""
        require_query_scope(family,command,self.include_historical_route_diagnostics)
        index=self.family.findData(family)
        if index<0 or command not in dict(self.queries[family]):raise ValueError('没有这个查询。')
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

    def set_graph(self,graph,*,epoch=None,historical=True):
        """Deep-copy cache only. Capture timestamps never replace the input/result."""
        self._graph_cache={'graph':deepcopy(graph),'epoch':epoch,'historical':bool(historical)} if isinstance(graph,dict) else None
        self._update_context()

    def _update_context(self):
        name=catalog()['operators'].get((self._scenario or {}).get('operator'),{}).get('name')
        stage=battle_data()['stages'].get(self._stage,{})
        graph=(self._graph_cache or {}).get('graph') or {}
        graph_name=(str(graph.get('template_id') or '模板未确认')+' / '+str(graph.get('zone_id') or '区域未确认')) if graph else '尚无可用地图'
        history='历史记录' if self._graph_cache and self._graph_cache['historical'] else '当前匹配记录'
        self.context_label.setText(f"可显式导入：干员 {name or '尚无可用条件'}；关卡 {stage.get('name','尚无可用关卡')}；地图 {graph_name}（{history}）。自动刷新保留编辑、选择和结果。")
        self._update_buttons()

    def _update_buttons(self):
        family,command=self.current_query()
        self.import_scenario.setEnabled(family=='calibration' and command not in ('worksheets','barrier-ledger','shield-inventory','explosion-values','modifier-values','regen-clock','regen-attributes') and self._scenario is not None)
        self.import_stage.setEnabled((family=='battle' or family=='exploration' and command=='settlements') and self._stage is not None)
        exploring=family=='exploration';graph_query=command in ('targets','effects','options','itinerary','residents','settlements','compare-routes','search-routes')
        self.import_graph.setVisible(exploring);self.preset.setVisible(exploring)
        self.graph_node.setVisible(exploring and graph_query);self.fill_node.setVisible(exploring and graph_query)
        self.import_graph.setText('导入缓存区域声明' if command=='budget' else '导入缓存地图声明')
        self.import_graph.setEnabled(exploring and (graph_query or command=='budget') and self._graph_cache is not None)
        self.fill_node.setEnabled(exploring and command in ('targets','effects','options','residents','settlements','search-routes') and self.graph_node.currentData() is not None)
        self.fill_node.setText('追加战斗节点参考' if command=='settlements' else '填写声明起点' if command=='targets' else '填写居民据点' if command=='residents' else '填写声明目标')

    def _family_changed(self):
        self._changing=True
        self.query.clear()
        for command,label in self.queries[self.family.currentData()]:self.query.addItem(label,command)
        remembered=self._family_queries.get(self.family.currentData())
        if remembered:self.query.setCurrentIndex(self.query.findData(remembered))
        self._changing=False
        self._query_changed()

    def _query_changed(self):
        if self._changing or not self.query.currentData():return
        self._save_view()
        key=self.current_query();self._changing=True
        try:
            text=self._buffers.get(key)
            if text is None:text=json.dumps(public_payload(*key),ensure_ascii=False,indent=2)
            self.editor.setPlainText(text);self._buffers[key]=text;self._active_key=key
            self.preset.clear()
            if key[0]=='exploration':
                for row in exploration_presets(key[1]):self.preset.addItem(row['label'],row['id'])
            view=self._views.get(key)
            self._origin=(view or {}).get('origin','公开声明示例；不是本局状态')
            self._graph_import=deepcopy((view or {}).get('graph_import'))
            self._refresh_graph_choices((view or {}).get('graph_node'))
            self._serial+=1;self._restore_view(view)
        finally:
            self._changing=False
        self.scope.setText(INPUT_GUIDANCE[key[1]])
        self._update_buttons()

    def _save_view(self):
        if self._active_key is None:return
        self._family_queries[self._active_key[0]]=self._active_key[1]
        cursor=self.editor.textCursor()
        self._views[self._active_key]={'cursor':[cursor.anchor(),cursor.position()],
            'result_cursor':[self.result_view.textCursor().anchor(),self.result_view.textCursor().position()],
            'raw_cursor':[self.raw_result.textCursor().anchor(),self.raw_result.textCursor().position()],
            'editor_scroll':self.editor.verticalScrollBar().value(),'result_scroll':self.result_view.verticalScrollBar().value(),
            'raw_scroll':self.raw_result.verticalScrollBar().value(),'technical':self.technical.isChecked(),
            'horizontal_scroll':[w.horizontalScrollBar().value() for w in (self.editor,self.result_view,self.raw_result)],
            'result':deepcopy(self._result),'rendered':self._rendered,'raw':self.raw_result.toPlainText(),
            'status':self.status.text(),'origin':self._origin,'graph_import':deepcopy(self._graph_import),
            'result_graph':deepcopy(self._result_graph),'result_links':deepcopy(self._result_links),
            'preset':self.preset.currentData(),'graph_node':self.graph_node.currentData()}

    def _restore_view(self,view):
        self.run_button.setEnabled(True)
        self._result=deepcopy((view or {}).get('result'));self._rendered=(view or {}).get('rendered','')
        self._result_graph=deepcopy((view or {}).get('result_graph'));self._result_links=deepcopy((view or {}).get('result_links',{}))
        message=(view or {}).get('status','查询已切换，请检查声明条件后运行。')
        if message=='正在运行局外查询……':message='先前查询未保留结果，请重新运行。'
        self.status.setText(message);self.result_view.setHtml(self._rendered or _p(message))
        self.raw_result.setPlainText((view or {}).get('raw',''));self.technical.setChecked((view or {}).get('technical',False))
        if view:
            cursor=self.editor.textCursor();cursor.setPosition(view['cursor'][0]);cursor.setPosition(view['cursor'][1],QTextCursor.MoveMode.KeepAnchor)
            self.editor.setTextCursor(cursor);self.editor.verticalScrollBar().setValue(view['editor_scroll'])
            for widget,field in ((self.result_view,'result_cursor'),(self.raw_result,'raw_cursor')):
                cursor=widget.textCursor();cursor.setPosition(view[field][0]);cursor.setPosition(view[field][1],QTextCursor.MoveMode.KeepAnchor)
                widget.setTextCursor(cursor)
            self.result_view.verticalScrollBar().setValue(view['result_scroll']);self.raw_result.verticalScrollBar().setValue(view['raw_scroll'])
            for widget,value in zip((self.editor,self.result_view,self.raw_result),view['horizontal_scroll']):widget.horizontalScrollBar().setValue(value)
            self.preset.setCurrentIndex(self.preset.findData(view['preset']))
        self.resultChanged.emit(deepcopy(self._result))

    def _input_changed(self):
        if self._changing:return
        self._buffers[self.current_query()]=self.editor.toPlainText()
        self._origin='用户编辑的局外声明；不是实际执行结果'
        self._invalidate('条件已修改，旧结果已失效，请重新运行。')

    def _invalidate(self, text):
        self._serial+=1;self._result=None;self._rendered=''
        self._result_graph=None;self._result_links={}
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
        family,command=self.current_query();payload=public_payload(family,command)
        if family=='exploration':payload=next(row['payload'] for row in exploration_presets(command) if row['id']==self.preset.currentData())
        self._graph_import=None
        self.editor.setPlainText(json.dumps(payload,ensure_ascii=False,indent=2))
        self._origin='公开场景预置：'+(self.preset.currentText() if family=='exploration' else '基本示例')+'；所有持有/AP/状态均为说明声明'
        self._refresh_graph_choices()
        self.status.setText('已载入公共示例；请检查条件。公式算例不是实机观察。')

    def _import_scenario(self):
        try:
            family,command=self.current_query()
            if family!='calibration' or command in ('worksheets','barrier-ledger','shield-inventory','explosion-values','modifier-values','regen-clock','regen-attributes') or self._scenario is None:raise ValueError('此查询没有可导入的干员条件。')
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
            if self._stage is None or not (family=='battle' or family=='exploration' and command=='settlements'):
                raise ValueError('没有可导入的关卡。')
            payload=self._payload()
            if family=='exploration':
                steps=payload.get('steps') or []
                if not isinstance(steps,list):raise ValueError('steps需要列表或null。')
                payload['steps']=[*steps,{'stage_id':self._stage}]
                self.editor.setPlainText(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False))
                self._origin='固定关卡选择的显式参考；胜利、层数和入口仍为独立声明'
                self.status.setText('已追加固定原ID参考；未声明胜利或入口，未写入本局资源。');return
            if command=='compare':payload['left_stage']=self._stage
            else:payload['stage_id']=self._stage
            self.editor.setPlainText(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False))
            self.status.setText('已显式导入关卡；敌人、等级、路线和格子仍保留原声明，请核对。两组对照只替换左关卡。')
        except Exception as exc:self.status.setText('未导入：'+str(exc))

    def _refresh_graph_choices(self,selected=None):
        self.graph_node.blockSignals(True);self.graph_node.clear()
        self.graph_node.addItem('请选择声明图节点',None)
        try:graph=self._payload().get('graph') or {}
        except ValueError:graph={}
        nodes=graph.get('nodes') if isinstance(graph,dict) else None
        for node in nodes if isinstance(nodes,list) else []:
            if isinstance(node,dict) and isinstance(node.get('id'),str):
                self.graph_node.addItem(_node_label(graph,node['id']),node['id'])
        if selected is not None:self.graph_node.setCurrentIndex(max(0,self.graph_node.findData(selected)))
        self.graph_node.blockSignals(False)

    def _import_graph(self):
        try:
            family,command=self.current_query()
            if family!='exploration' or self._graph_cache is None:raise ValueError('没有可导入的地图缓存。')
            if command not in ('targets','effects','options','itinerary','residents','budget','settlements','compare-routes','search-routes'):
                raise ValueError('此查询不接受地图或区域声明。')
            payload=self._payload();cached=deepcopy(self._graph_cache);graph=cached['graph']
            if command=='budget':
                zone=graph.get('zone_id')
                if zone not in exploration_planning.reference_data()['zones']:raise ValueError('缓存区域ID尚未确认。')
                payload['zone_id']=zone;graph_import=None
            else:
                payload['graph']=graph;graph_import=cached
            text=json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False)
            self.editor.setPlainText(text);self._graph_import=graph_import
            self._origin=('历史' if cached['historical'] else '当前匹配')+'缓存图的显式副本；AP/次数/完成/阻碍仍是独立声明'
            self._refresh_graph_choices();self._update_buttons()
            self.status.setText('已显式导入地图/区域副本；目标、起点、库存和资源保留原声明，请核对。未写入本局。')
        except Exception as exc:self.status.setText('未导入：'+str(exc))

    def _fill_node(self):
        try:
            family,command=self.current_query();node_id=self.graph_node.currentData();payload=self._payload()
            if family!='exploration' or command not in ('targets','effects','options','residents','settlements','search-routes'):
                raise ValueError('此查询不接受单个节点字段。')
            if not any(n.get('id')==node_id for n in payload.get('graph',{}).get('nodes',[])):
                raise ValueError('所选节点不在当前编辑的声明图中；请重新载入/导入声明图。')
            if self.graph_node.currentText()!=_node_label(payload['graph'],node_id):
                self._refresh_graph_choices();self._update_buttons()
                raise ValueError('节点的位置或类型声明已修改；清单已同步，请重新选择后填写。')
            if command=='settlements':
                steps=payload.get('steps') or []
                if not isinstance(steps,list):raise ValueError('steps需要列表或null。')
                payload['steps']=[*steps,{'target':node_id}]
                self.editor.setPlainText(json.dumps(payload,ensure_ascii=False,indent=2))
                self.status.setText('已追加声明图节点参考；身份、层数、入口与胜利未知仍保留。');return
            field='start' if command=='targets' else 'post_node' if command=='residents' else 'goal' if command=='search-routes' else 'target'
            payload[field]=node_id;self.editor.setPlainText(json.dumps(payload,ensure_ascii=False,indent=2))
            self.status.setText('已填写声明'+('起点' if field=='start' else '据点' if field=='post_node' else '目标')+'；不改变助手或游戏中的实际位置。')
        except Exception as exc:self.status.setText('未填写：'+str(exc))

    @staticmethod
    def _graph_layout(graph):
        if not isinstance(graph,dict):return None
        if not isinstance(graph.get('nodes'),list):return None
        rows=[]
        for node in graph.get('nodes',[]):
            if (not isinstance(node,dict) or not isinstance(node.get('id'),str)
                or type(node.get('row')) is not int or type(node.get('col')) is not int):return None
            rows.append((node['id'],node['row'],node['col']))
        return (graph.get('zone_id'),graph.get('template_id'),tuple(sorted(rows)))

    def _bindings_for_payload(self,payload):
        imported=self._graph_import;graph=payload.get('graph')
        layout=self._graph_layout(graph)
        if not imported or imported.get('epoch') is None or layout is None or layout!=self._graph_layout(imported['graph']):return {}
        if not graph.get('zone_id') or not graph.get('template_id'):return {}
        return {node['id']:{'epoch':imported['epoch'],'zone_id':graph['zone_id'],'template_id':graph['template_id'],
                'node_id':node['id'],'row':node['row'],'col':node['col']} for node in graph['nodes']}

    def _map_anchor(self,url):
        if url.scheme()!='rouge-map-node':return
        key=unquote(url.path());binding=self._result_links.get(key);cached=self._graph_cache
        current=(cached or {}).get('graph') or {}
        nodes=current.get('nodes')
        node=next((n for n in nodes if isinstance(n,dict) and n.get('id')==key),None) if isinstance(nodes,list) else None
        if (not binding or not cached or cached['epoch']!=binding['epoch'] or not node
            or current.get('zone_id')!=binding['zone_id'] or current.get('template_id')!=binding['template_id']
            or type(node.get('row')) is not int or type(node.get('col')) is not int
            or node['row']!=binding['row'] or node['col']!=binding['col']):
            self.status.setText('地图链接已过期或来源未绑定；保留旧结果，请显式导入本局图后重新运行。');return
        self.mapNodeSelected.emit(key,deepcopy(binding))

    def _run(self):
        try:
            require_query_scope(*self.current_query(),self.include_historical_route_diagnostics)
            payload=self._payload()
        except Exception as exc:
            self._invalidate('不能运行：'+str(exc));return
        self._invalidate('正在运行局外查询……')
        serial=self._serial;family,command=self.current_query()
        if family=='exploration':self._refresh_graph_choices(self.graph_node.currentData());self._update_buttons()
        worker=_QueryWorker(serial,family,command,payload,
            include_historical_route_diagnostics=self.include_historical_route_diagnostics)
        self._worker_context[serial]={'payload':deepcopy(payload),'origin':self._origin,'bindings':self._bindings_for_payload(payload) if family=='exploration' else {}}
        worker.signals.finished.connect(self._finished)
        self._workers[serial]=worker;self.run_button.setEnabled(False)
        QThreadPool.globalInstance().start(worker)

    def _finished(self, serial, family, command, result, error):
        self._workers.pop(serial,None)
        context=self._worker_context.pop(serial,{})
        if serial!=self._serial or (family,command)!=self.current_query():return
        self.run_button.setEnabled(True)
        if error:self._invalidate(error);return
        try:
            graph=context.get('payload',{}).get('graph');bindings=context.get('bindings',{})
            links={key:binding for key,binding in bindings.items() if key in result_node_ids(command,result)}
            rendered=render_offline_result(family,command,result,graph=graph,map_link_nodes=links,input_source=context.get('origin'))
            raw=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)
        except Exception as exc:self._invalidate('结果结构无法显示：'+str(exc));return
        self._result=deepcopy(result)
        self._result_graph=deepcopy(graph);self._result_links=deepcopy(links)
        if rendered!=self._rendered:
            self.result_view.setHtml(rendered);self._rendered=rendered
        self.raw_result.setPlainText(raw)
        self.status.setText('离线查询完成。请按各分项的证据范围使用；未核验项保持未知。')
        self.resultChanged.emit(deepcopy(result))

    def result_snapshot(self):return deepcopy(self._result)
