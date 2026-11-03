"""Prepare complete documentary/current-original shop battle reading."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import argparse, importlib.util, json, re, sys

BASE = Path(__file__).resolve().parents[1]
SOURCE_ROOT = BASE if (BASE / 'rouge/expansion_reference.py').is_file() else BASE.parents[1]


def enc(x):
    return (json.dumps(x, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf8')


def build(root, output):
    sys.path.insert(0, str(root))
    from scripts.build_boss_hunt_reference_311 import Document, Node, cls, visible, serial, descendants
    from rouge import current_reward_reference as reward
    spec = importlib.util.spec_from_file_location('rouge.current_cannot_reference', BASE / 'rouge/current_cannot_reference.py')
    model = importlib.util.module_from_spec(spec); spec.loader.exec_module(model)
    p = reward.packet()
    if p is None:
        raise ValueError('Existing current battle/reward source chain required')
    blobs = {name: (root / name).read_bytes() for name in (model.THEME, model.THEME_RECEIPT, model.NODE_SOURCE)}
    for name in ('cannot.html', 'deadbox.html', 'livingwood.html', 'vault.html', 'http-sources.json'):
        blobs[model.PACK + '/' + name] = (output / model.PACK / name).read_bytes()
    records = json.loads(blobs[model.PACK + '/http-sources.json'])
    if len(records) != 4 or {r['key'] for r in records} != {'cannot', 'deadbox', 'livingwood', 'vault'}:
        raise ValueError('Four complete originals required')
    documents = {}
    for r in records:
        raw = blobs[model.PACK + '/' + r['key'] + '.html']
        text = raw.decode('utf8')
        if r['http_status'] != 200 or r['bytes'] != len(raw) or r['sha256'] != sha256(raw).hexdigest() or r['complete_html_obtained'] is not True:
            raise ValueError('Actual complete original response required')
        if len(r['wg_revision']) != 1 or 'oldid=' + r['wg_revision'][0] not in text or not re.search(r'"wgRevisionId":' + r['wg_revision'][0] + r'\b', text):
            raise ValueError('Observed original revision required')
        doc = Document(text)
        cards = [n for n in doc.nodes if cls(n, 'ak-card__body') and cls(n, 'skill_card')]
        tables = [n for n in doc.nodes if n.tag == 'table' and cls(n, 'wikitable')]
        documents[r['key']] = {'source': deepcopy(r), 'cards': [{'complete_DOM': serial(n), 'full_visible': visible(n).strip(),
            'paragraphs': [visible(c).strip() for c in n.children if isinstance(c, Node) and c.tag == 'p'],
            'tooltips': [serial(t) for t in (n, *descendants(n)) if cls(t, 'mc-tooltips')]} for n in cards],
            'tables': [{'complete_DOM': serial(n), 'full_visible': visible(n).strip()} for n in tables]}
    if len(documents['cannot']['cards']) != 2:
        raise ValueError('One complete boss skill and one full ability card required')
    skill, talent = (d['full_visible'] for d in documents['cannot']['cards'])
    for text in ('物归原主', '仅攻击范围内存在', '可受孤立干扰', '强制击杀', '跳过重生'):
        if text not in skill.replace(' ', ''):
            raise ValueError('Complete retrieval skill wording required: ' + text)
    for text in ('不进行普通攻击', '移动速度+0.9', '持续8秒', '重复获得时仅刷新持续时间', '10%×已回收保险柜数', '最多降低50%', '最多5个', '扣除99源石锭'):
        if text not in talent:
            raise ValueError('Complete ability wording required: ' + text)
    vault_mechanisms = [t for t in documents['vault']['tables'] if '装置机制' in t['full_visible']]
    if len(vault_mechanisms) != 1:
        raise ValueError('One complete device mechanism table required')
    vault_text = vault_mechanisms[0]['full_visible']
    for text in ('0.667秒', '100%生命值', '待回收模式', '非无职业', '锁定并撤退', '1个栏位', '2个'):
        if text not in vault_text:
            raise ValueError('Complete vault pickup wording required: ' + text)
    theme_raw = blobs[model.THEME]; meta = json.loads(blobs[model.THEME_RECEIPT])
    if meta['http_status'] != 200 or meta['bytes'] != len(theme_raw) or meta['sha256'] != sha256(theme_raw).hexdigest():
        raise ValueError('354 complete theme original required')
    theme = Document(theme_raw.decode('utf8'))
    sections = [n for n in theme.nodes if n.attrs.get('id') == 'mw-customcollapsible-ro2shopinner']
    shops = [n for n in sections if '试探性碰碰商品' in visible(n) and '原地投降' in visible(n)]
    investments = [n for n in sections if '历史累计投资额' in visible(n) and '余额提取功能' in visible(n)]
    if len(sections) != 2 or len(shops) != 1 or len(investments) != 1:
        raise ValueError('Both same-id sections must retain distinct investment/challenge content')
    shop_text = visible(shops[0]).strip()
    for text in ('最高投资额达到50', '到达第4层前进入死箱', '第4层及之后进入活木', '林间空地', '不再提供任何功能', '原地投降'):
        if text not in shop_text:
            raise ValueError('Full shop condition/cost aftermath required: ' + text)
    documents['theme_shop'] = {'revision': 442954, 'source_path': model.THEME,
                             'complete_DOM': serial(shops[0]), 'full_visible': shop_text}
    documents['theme_investment'] = {'revision': 442954, 'source_path': model.THEME,
                                    'complete_DOM': serial(investments[0]), 'full_visible': visible(investments[0]).strip()}
    originals = model.selected_originals(p['current'], p['selected'])
    definition = originals['enemy_definitions']
    if len(definition) != 1 or definition[0]['level'] != 0:
        raise ValueError('Exact database level0 required')
    base = definition[0]['enemyData']
    if base['talentBlackboard'] != [{'key': 'SpeedUp.move_speed', 'value': 0.9, 'valueStr': None}, {'key': 'SpeedUp.duration', 'value': 8.0, 'valueStr': None}]:
        raise ValueError('Reviewed movement parameters required')
    if len(base['skills']) != 1 or base['skills'][0]['cooldown'] != 1.0 or base['skills'][0]['initCooldown'] != 0.0:
        raise ValueError('Reviewed documented skill timing parameters required')
    if base['skills'][0]['blackboard'] != [{'key': 'cnt_max', 'value': 5.0, 'valueStr': None}, {'key': 'damage_scale', 'value': 0.1, 'valueStr': None}]:
        raise ValueError('Reviewed cap/reduction parameters required')
    rows = {}
    for sid, original in originals['stages'].items():
        level = original['level']
        bound = [(i, r) for i, r in enumerate(level['enemyDbRefs']) if r['id'] == model.BOSS]
        if len(bound) != 1 or bound[0][1]['useDb'] is not True or type(bound[0][1]['level']) is not int or bound[0][1]['level'] != 0:
            raise ValueError('Unique current boss reference required')
        index, binding = bound[0]
        effective = {}
        def collect(value, path=''):
            if isinstance(value, dict):
                if type(value.get('m_defined')) is bool and 'm_value' in value:
                    if value['m_defined']:
                        effective[path] = deepcopy(value['m_value'])
                else:
                    for key, item in value.items():
                        if key in ('skills', 'talentBlackboard', 'spData') and item is not None:
                            effective[path + '.' + key] = deepcopy(item)
                        else:
                            collect(item, path + '.' + key)
        collect(binding['overwrittenData'])
        expected = {'.attributes.maxHp': 60000} if sid == 'ro6_t_6' else {}
        if not model.same(effective, expected):
            raise ValueError('Unreviewed enemy mechanism override')
        vaults = []
        for container in ('predefines', 'hardPredefines'):
            for field in ('characterInsts', 'tokenInsts'):
                for i, raw in enumerate((level.get(container) or {}).get(field) or []):
                    if (raw.get('inst') or {}).get('characterKey') != model.VAULT:
                        continue
                    grade = raw['inst']['level']
                    if type(grade) is not int or grade not in (1, 2) or raw['inst']['phase'] != 'PHASE_0':
                        raise ValueError('Reviewed device grade1/2 required')
                    rule = reward.device_rule(model.VAULT, raw, p)
                    if not rule['quantity_qualified']:
                        raise ValueError('Existing precise device skill qualification required')
                    key = '$.' + container + '.' + field + '[' + str(i) + ']'
                    vaults.append({'key': key, 'label': ('大' if grade == 2 else '小') + '保险柜 · 资料' + str(len(vaults) + 1),
                                   'grade': grade, 'original': deepcopy(raw), 'pickup_free_slots_reference': grade,
                                   'actual_appeared': None, 'actual_picked_up': None, 'actual_free_slots': None})
        if [v['grade'] for v in vaults] != ([2, 1, 2, 1, 2, 1, 1] if sid == 'ro6_t_6' else [1] * 10):
            raise ValueError('Complete exact selected vault sequence required')
        rows[sid] = {'id': sid, 'name': original['stage']['name'], 'floor_description': '到达第4层前' if sid == 'ro6_t_6' else '第4层及之后',
                     'boss': {'key': str(index), 'enemy_id': model.BOSS, 'level': 0, 'original': deepcopy(binding),
                              'hp_override_only': bool(effective), 'effective_override_reference': effective}, 'vaults': vaults}
    function = [f for f in json.loads(blobs[model.NODE_SOURCE])['node_functions'] if f['node_type'] == '诡意行商']
    if len(function) != 1:
        raise ValueError('One original legacy shop-function record required')
    reading = [
        {'id':'entry','title':'商店挑战的入口与后果','paragraphs':[
            '主题文献写明：本主题最高投资额达到50后出现“试探性碰碰商品”；连续点击后，可选择听劝或“请”坎诺特“降价”。这里不核验账户投资记录，也不把这段条件当实际可选资格。',
            '同页投资更新段又写按历史累计投资额解锁奖赏，挑战段仍使用“最高投资额”。两种口径不自行合并；此前投资阅读器已有此类边界，本页不另作账户解锁判断。',
            '听劝不发生后续挑战；选择“降价”进入特殊商店战斗。到达第4层前对应死箱，第4层及之后对应活木。层数未知时两份条件候选都保留，不自动选择。',
            '通关后只有部分商品可免费取得。坎诺特离开，该节点变为林间空地；本次探索后续诡意行商不再提供功能。文献未据此说明秘境行商也失效，不能扩大到另一种商店。'], 'evidence':['theme_shop','theme_investment']},
        {'id':'boss','title':'坎诺特：移动与回收','paragraphs':[
            '文献说明他不可阻挡且不普通攻击。受到伤害时移动速度增加0.9，持续8秒；再次获得只刷新持续时间，不把每次受击当成无限叠加。该数值是文献增量，不是当前关卡的最终速度。',
            '图鉴概述写“被攻击”，详细文献写“受到伤害”。零伤害命中、持续伤害等边界未取得独立执行依据，不据此计算实际触发次数。',
            '“物归原主”仅在攻击范围内存在可选中的坎诺特保险柜时触发；孤立会干扰选中。回收属于强制击杀并跳过保险柜的重生，不能当成我方正常击破后的可拾取状态。',
            '文献给出初始冷却0秒、冷却1秒；触发仍要满足附近保险柜等条件，不能改成每秒保证回收或开场绝对时间表。',
            '文献中回收后物理、法术伤害减免为每柜10%，最多50%；只在对应路径成立时说明。不把它套到真实伤害，也不合成实际减伤后面板或伤害。'], 'evidence':['cannot.cards[0]','cannot.cards[1]','current enemy definition']},
        {'id':'vault','title':'保险柜：击破与干员拾取','paragraphs':[
            '初始保险柜占据的格子不能部署；具有不可阻挡及晕眩、冻结、寒冷、沉睡免疫。正常击倒后经历文献记载的0.667秒重生，回复100%生命，进入待回收模式。',
            '待回收模式可在所在地块部署，并具有无敌、孤立、禁疗。攻击范围内出现非“无职业”的我方干员时，保险柜退场，锁定并撤退该干员；该干员本场不能再次部署。它不是“看到箱子就自动领取”，也不能把任意召唤物当可拾取干员。',
            '小保险柜在成功走完干员拾取路径后，使战后商店1个栏位价格变0；等级2的大保险柜对应2个栏位。等级来自所选本关预置原件，不能只看图标猜等级。',
            '这是装置文献与当前原表共同支持的条件分项。实际击破、复生、拾取、参与干员与商品仍未知；不会操作游戏或把这段说明当实时部署提示。'], 'evidence':['vault mechanism table','current selected vault character/skill','current stage predefines']},
        {'id':'free','title':'两种免费栏位来源：不能直接相加','paragraphs':[
            '路径一是我方击破后由干员拾取保险柜；路径二是坎诺特先回收，再被击倒。两条路径会涉及同一批保险柜，不能把同一个箱子在两处各计一次。',
            '坎诺特详细社区天赋写“每回收一个，使1个栏位变0，最多5个”；游戏图鉴却说明按已回收保险柜的“数量和等级”决定。文献没有完整解释等级2保险柜在这条路径的处理。',
            '因此保留两份原文差异，不以最多5个或大柜2个拼成完整公式。大柜2个的直接拾取证据不能自动套到坎诺特回收后被击倒。实际免费栏位总数和具体商品仍未知。',
            '“价格变为0”表示那个商店栏位可以免费购买，不能直接等同于已领取固定收藏品，也不保证某个指定商品。“1–2个商店物品”的说明没有列出完整商品名单。'], 'evidence':['cannot.cards[1]','current handbook','vault mechanism table']},
        {'id':'exit','title':'逃脱、投降与战后商品','paragraphs':[
            '游戏图鉴记载进入保护目标时偷取99源石锭，详细文献表述为到达自己的路径终点后扣除99源石锭；这里保留原表述，不计算玩家余额或把某个地图格自行绑定为实际终点。',
            '余额不足99时的扣除下限、是否存在其它条件或修正，本包没有独立执行依据。不能显示负余额或宣称已扣除99。',
            '战斗结束后，购买价格未变为0的商品消失。坎诺特带走而未夺回的保险柜中商品不能购买；原地投降会令其回收全部保险柜、带走全部商品。',
            '击倒、逃脱、投降及战后结算是不同条件，不能同时当成已发生，也不能依据预置数量推算玩家最终损益。'], 'evidence':['current handbook','cannot.cards[1]','theme_shop']},
        {'id':'sources','title':'适用范围与来源差异','paragraphs':[
            '这里结合死箱、活木各自的关卡资料，解释坎诺特与保险柜的完整文献说明；“击破后部署偷取1–2个物品”仍需区分箱子等级与是否成功领取。',
            '死箱中的坎诺特有单独生命设定，活木沿用默认设定。两关分别核对，不能因为敌人同名就照搬完整预测面板。',
            '使用国服10月16日固定关卡资料和对应社区文献；文献参考不等于当前服务器实测。完整修订号、原始值和文献页面保存于来源页。',
            '尚未取得商店挑战与不期而遇原选项的一一对应资料。诡意行商、无人商店和秘境行商是不同内容，不能互换入口。'], 'evidence':['all originals']}
    ]
    data = {'schema':'current_cannot_367_v1','originals':originals,'shop_function_original':function[0],'stages':rows,
            'reading':reading,'actual_complete_free_slot_formula':None,'actual_complete_goods_pool':None,'existing_315_reward_model_replaced':False,
            'current_server_verified':False,'run_updated':False}
    notes = {'section_candidate':367,'counts':{'stages':2,'boss_references':2,'vault_records':17,'large_vault_records':3},
             'duplicate_scope':'315 pickup1-2 and existing node shop conditions retained, not claimed new',
             'source_conflict':'native number-and-grade wording versus community one-slot-per-recovered-vault max5; no complete formula inferred',
             'entry_pointer':'No current choice_ro6 pointer; source-bound legacy shop-function record only',
             'source_failures_before_success':['web tool cannot enemy page timed out; raw mobile HTML fetched successfully afterward'],
             'first_build_failure':'Theme original contains two nodes with identical id; first build rejected nonunique id. Final extraction retains both and distinguishes full investment and challenge contents.',
             'license':'PRTS CC BY-NC-SA4.0 except separately owned original game materials',
             'tests_and_gui_executed':False}
    outputs = {model.DATA:enc(data),model.DOCS:enc(documents),model.NOTES:enc(notes)}
    files = {name:{'bytes':len(raw),'sha256':sha256(raw).hexdigest()} for name,raw in {**blobs,**outputs}.items()}
    outputs[model.MANIFEST] = enc({'schema':'current_cannot_367_manifest_v1','files':dict(sorted(files.items()))})
    return model,outputs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root',type=Path,default=SOURCE_ROOT)
    parser.add_argument('--output-root',type=Path,default=BASE)
    parser.add_argument('--check',action='store_true')
    args = parser.parse_args()
    model, outputs = build(args.source_root.resolve(),args.output_root.resolve())
    for name, body in outputs.items():
        path = args.output_root / name
        if args.check:
            if path.read_bytes() != body:raise ValueError('Build differs: '+name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    print(json.dumps({'stages':2,'boss_references':2,'vault_records':17,'manifest_sha256':sha256(outputs[model.MANIFEST]).hexdigest()}))
