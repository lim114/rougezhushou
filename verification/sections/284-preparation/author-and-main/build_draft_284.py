"""Cache-only two-file caller draft, bound to exact section283 production bytes."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in (HERE, *HERE.parents) if (p / 'rouge/app.py').is_file())
EXPECTED = {
    'rouge/operator_engine.py': 'ab607af94c536ca214dee880145bc72a7e85acc494a07756c254cc66918ec4bf',
    'rouge/panel_native_bridge.py': '52800ba9d98a58790ec4a77eabd4eb195516f31ad1716a0fc49ee86909e671a6',
}
source = {}
for name, expected in EXPECTED.items():
    raw = (ROOT / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected, name
    source[name] = raw.decode('utf8')


def edit(name, old, new):
    assert source[name].count(old) == 1, (name, old)
    source[name] = source[name].replace(old, new)


bridge = 'rouge/panel_native_bridge.py'
helper = '''EXTENDED_CAPTURE_OPERATORS = frozenset((
    'char_151_myrtle','char_4228_closur','char_1050_chen3','char_4182_oblvns',
    'char_002_amiya','char_1001_amiya2','char_1037_amiya3','char_196_sunbr',
    'char_1044_hsgma2','char_2025_shu','char_1035_wisdel','char_1048_orchd2',
    'char_133_mm','char_1046_sbell2','char_328_cammou','char_1038_whitw2',
    'char_298_susuro','char_1042_phatm2','char_4202_haruka','char_110_deepcl',
    'char_2027_wang','char_1041_angel2','char_1029_yato2','char_4087_ines',
    'char_206_gnosis','char_4107_vrdant','char_1015_aglna2','char_4204_mantra','char_437_mizuki'))


def capture_extended_skill_primitives(scenario, number, attributes, base_attack,
        attack_bonus, attack_flat, attack_speed_bonus, blackboard):
    """Capture the model operands consumed at plan entry, with field scope.

    This does not infer current native activation/normality. A later model
    branch that rewrites an actor value excludes that field from the common
    reference; independent unaffected fields remain useful. No output division
    or re-selection of relics/talents is performed.
    """
    op = scenario['operator']
    reasons = {'attack': None, 'attack_speed': None}
    if op not in EXTENDED_CAPTURE_OPERATORS:
        reasons = dict.fromkeys(reasons, '该干员尚未纳入本体技能输入资格清单。')
    elif op in ('char_110_deepcl','char_4228_closur','char_1001_amiya2',
                 'char_1029_yato2','char_1015_aglna2'):
        reasons['attack'] = {
            'char_110_deepcl': '本体攻击会在召唤分支重置；召唤物技能加攻不能套给本体。',
            'char_4228_closur': '本体攻击重置或援军阻挡特性倍率尚未接入此精度参考。',
            'char_1001_amiya2': '技能天赋增幅及斩击后击倒叠层尚未接入此精度参考。',
            'char_1029_yato2': '技能期间额外天赋攻击项尚未接入此精度参考。',
            'char_1015_aglna2': '起飞状态额外天赋攻击项尚未接入此精度参考。',
        }[op]
    if op == 'char_1050_chen3' and number == 2:
        reasons['attack'] = '斩击后强化改变攻击；前后阶段输入尚未接入此精度参考。'
    if op == 'char_1037_amiya3' and number == 2:
        reasons['attack'] = '开启前攻击重置及按命中叠层尚未接入此精度参考。'
    if op == 'char_4202_haruka' and number == 2:
        reasons['attack'] = '泡影重现分支重新选择攻击增量，尚未接入此精度参考。'
    if op == 'char_2025_shu' and number == 3 and scenario.get('enemy_on_sown_tile'):
        reasons['attack'] = reasons['attack_speed'] = '播种地块的额外攻击与攻速尚未接入此精度参考。'
    if op == 'char_4182_oblvns' and number == 2:
        if scenario.get('organ_mode', False):
            reasons['attack_speed'] = '风琴模式的额外攻速尚未接入此精度参考。'
        else:
            reasons['attack'] = '钢琴模式的额外攻击尚未接入此精度参考。'
    if op == 'char_1041_angel2' and number == 2 and scenario.get('steal_success', True):
        reasons['attack_speed'] = '偷取成功的额外攻速尚未接入此精度参考。'
    terms = {
        'attack': _term(base_attack, multiplier=attack_bonus + blackboard.get('atk', 0),
                        final_addition=attack_flat),
        'attack_speed': _term(attributes['attack_speed'],
                        addition=attack_speed_bonus + blackboard.get('attack_speed', 0)),
    }
    qualifications = {}
    for field, reason in reasons.items():
        if reason is not None:
            terms[field] = _term(None)
        qualifications[field] = {'common_model_primitives_captured': reason is None,
            'reason': reason, 'basis': 'independent_nominal_model_snapshot',
            'actual_activation_or_phase_clock_verified': False}
    return terms, qualifications


'''
edit(bridge, 'def unknown_skill_terms():', helper + 'def unknown_skill_terms():')
edit(bridge, "    estimate=result['estimate'];terms=estimate.pop('_panel_native_terms',{})",
             "    estimate=result['estimate'];terms=estimate.pop('_panel_native_terms',{})\n"
             "    skill_qualifications=estimate.pop('_panel_native_skill_qualification',None)")
edit(bridge, "    result['panel_native_finalization']=evaluated",
             "    if skill_qualifications is not None:\n"
             "        evaluated['skill_primitive_qualification']=deepcopy(skill_qualifications)\n"
             "        evaluated['input_provenance']['extended_skill_input_scope']='Field-qualified common model primitives; special rewrites remain unknown.'\n"
             "        for row in evaluated['fields']:\n"
             "            if row['phase']=='skill' and row['field'] in skill_qualifications:\n"
             "                row['primitive_qualification']=deepcopy(skill_qualifications[row['field']])\n"
             "                if skill_qualifications[row['field']]['reason']:\n"
             "                    row['limitations'].append(skill_qualifications[row['field']]['reason'])\n"
             "    result['panel_native_finalization']=evaluated")
edit(bridge, "        '来源核验：'+('通过' if data['source_valid'] else '未通过，条件参考已隐藏')+'；完整原生面板与实际读值仍未知。'])",
             "        '来源核验：'+('通过' if data['source_valid'] else '未通过，条件参考已隐藏')+'；完整原生面板与实际读值仍未知。',\n"
             "        *['技能'+LABELS[field]+'：'+scope['reason'] for field,scope in data.get('skill_primitive_qualification',{}).items() if scope['reason']]])")

engine = 'rouge/operator_engine.py'
edit(engine, "        speed_reference=self.base_speed_reference+bb.get('attack_speed',0)",
             "        speed_reference=self.base_speed_reference+bb.get('attack_speed',0)\n"
             "        from .panel_native_bridge import capture_extended_skill_primitives\n"
             "        native_skill_terms,native_skill_qualification=(None,None) if normal else capture_extended_skill_primitives(\n"
             "            self.s,self.n,self.a,self.base,self.atk_bonus,self.atk_flat,self.as_bonus,bb)")
edit(engine, "            'attack':attack,'attack_speed':speed,'attack_speed_reference':speed_reference,",
             "            'native_skill_terms':native_skill_terms,'native_skill_qualification':native_skill_qualification,\n"
             "            'attack':attack,'attack_speed':speed,'attack_speed_reference':speed_reference,")
edit(engine, "        from .panel_native_bridge import unknown_skill_terms\n        result['estimate']={'_panel_native_terms':{'normal':self.native_normal_terms,'skill':unknown_skill_terms()},",
             "        result['estimate']={'_panel_native_terms':{'normal':self.native_normal_terms,'skill':full['native_skill_terms']},\n"
             "            '_panel_native_skill_qualification':full['native_skill_qualification'],")

out = HERE / 'draft'
hashes = {}
for name, text in source.items():
    target = out / name
    assert not target.exists(), 'preserve first prepared draft'
    target.parent.mkdir(parents=True, exist_ok=True)
    ast.parse(text)
    target.write_bytes(text.encode('utf8'))
    hashes[name] = hashlib.sha256(target.read_bytes()).hexdigest()
manifest = {'kind': 'SECTION284_TWO_FILE_CACHE_DRAFT_NOT_PRODUCTION',
            'original_source_sha256': EXPECTED, 'draft_sha256': hashes,
            'source_binding_scope': 'nominal model caller capture, reused section283 arithmetic',
            'game_or_chat_actions': 0, 'private_state_used': False, 'production_modified': False}
target = HERE / 'draft-manifest.json'
assert not target.exists()
target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps(manifest, ensure_ascii=False))
