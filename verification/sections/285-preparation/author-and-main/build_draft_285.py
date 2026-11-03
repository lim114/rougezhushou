"""Prepare public adapter drafts only; never replace the working source."""
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
EXPECTED={
 'rouge/calibration.py':'72fa76dcb8592b7eb539ddc4d9440cb84e92449d30795b3de9bf9b81f0006691',
 'rouge/offline_tools_view.py':'05de5293607b57114b20f9a228882ec2a771cd0b1606e4d215518c4680e2d3e4',
}

def replace_once(text,old,new):
    assert text.count(old)==1,(old[:100],text.count(old))
    return text.replace(old,new,1)

def calibration_draft(text):
    text=replace_once(text,'"""Read-only, source-qualified calibration worksheets for the first three operators.',
        '"""Read-only calibration: all-operator panels/skills and scoped legacy worksheets.')
    text=replace_once(text,'def _scenario(scenario):','def _scenario(scenario, *, all_operators=False):')
    text=replace_once(text,"    if out.get('operator') not in OPERATORS:raise ValueError('校准工具仅支持首批三名干员。')",
        "    allowed=catalog()['operators'] if all_operators else OPERATORS\n"
        "    if out.get('operator') not in allowed:raise ValueError('此查询仅支持固定资料中已适配干员。' if all_operators else '校准工具仅支持首批三名干员。')")
    text=replace_once(text,"    s=_scenario(scenario);cult=_cultivated(s)",
        "    s=_scenario(scenario,all_operators=True);cult=_cultivated(s)")
    text=replace_once(text,"    return {'operator':catalog()['operators'][s['operator']]['name'],'context':ctx,",
        "    profile=catalog()['operators'][s['operator']]\n"
        "    return {'operator':profile['name'],'operator_key':s['operator'],'operator_id':profile['id'],\n"
        "            'selected_operator':{'key':s['operator'],'id':profile['id'],'name':profile['name']},'context':ctx,")
    start=text.index('def skill_matrix(scenario, operators=None):')
    end=text.index("\nCOMMANDS['skills']=skill_matrix",start)
    text=text[:start]+'''def skill_matrix(scenario, operators=None):
    """Reuse each skill's main result without crossing extended owner conditions."""
    base=_scenario(scenario,all_operators=True);_cultivated(base)
    rank=_integer(base['skill_rank'],'技能等级',10)
    if rank<1:raise ValueError('技能等级需要为1–10。')
    if operators is None:
        ops=list(OPERATORS) if base['operator'] in OPERATORS else [base['operator']]
        selection_mode='legacy_first_three' if base['operator'] in OPERATORS else 'current_operator'
    else:
        if not isinstance(operators,list) or not operators or any(not isinstance(op,str) for op in operators):
            raise ValueError('operators需要非空干员标识列表。')
        ops=list(dict.fromkeys(operators))
        if base['operator'] in OPERATORS and all(op in OPERATORS for op in ops) and len(ops)<=3:
            selection_mode='explicit_first_three'
        elif ops==[base['operator']]:selection_mode='explicit_current_operator'
        else:raise ValueError('扩展干员条件只能用于当前干员；不能跨干员复制培养、模组或专属条件。')
    rows=[]
    for op in ops:
        profile=catalog()['operators'][op]
        for number,entry in enumerate(profile['skills'],1):
            s={**deepcopy(base),'operator':op,'skill':number}
            # Historical first-three comparison retains its existing owner isolation.
            if op!=base['operator']:
                for key in ('module_id','module_level','base_attack','activation_count','deployment_stacks',
                            'companion_attack','shield_break_count','charge_count','cooperative','preexisting_fragile'):
                    s.pop(key,None)
            reasons=[]
            if s['elite']<entry['unlock_elite']:
                reasons.append('需要精英'+str(entry['unlock_elite'])+'，当前精英'+str(s['elite'])+'。')
            if s['elite']<2 and rank>7:
                reasons.append('专精技能等级需要精英2；当前声明技能等级为'+str(rank)+'。')
            row={'operator':profile['name'],'operator_key':op,'operator_id':profile['id'],
                 'skill':number,'skill_id':entry['id'],'name':entry['levels'][rank-1]['name'],
                 'identity':{'operator_key':op,'operator_id':profile['id'],'skill':number,'skill_id':entry['id']},
                 'unlocked':not reasons,'unlock_reasons':reasons,
                 'native_verified':False,'native_clock_verified':False}
            if reasons:
                row.update(status='培养条件未开放',full_skill_damage=None,full_skill_healing=None,
                           native_panel_reference=None,declared_components=[])
            else:
                result=calculate_damage(s);skill=result['estimate']['skill']
                complete=bool(result['estimate'].get('complete',False))
                row.update(name=skill['name'],status='条件模型参考' if complete else '存在未核验项',
                    initial_seconds_reference=skill.get('initial_seconds'),recharge_seconds_reference=skill.get('recharge_seconds'),
                    cycle_seconds_reference=skill.get('cycle_seconds'),model_complete=complete,
                    model_complete_definition=result.get('complete_definition'),
                    conditional_total_reference={'damage':skill.get('total_damage'),'healing':skill.get('total_healing')},
                    full_skill_damage=0 if (op=='kaltsit' and number in (1,3)) or (op=='silverash' and number==1) else None,
                    full_skill_healing=0 if op in ('mechanist','silverash') else None,
                    declared_components=deepcopy(result.get('components',[])),
                    native_panel_reference=deepcopy(result['panel_native_finalization']),
                    window_damage_reference=skill.get('window_damage'),window_healing_reference=skill.get('window_healing'),
                    missing_or_conditional_notes=deepcopy(result['estimate']['notes']))
            rows.append(row)
    selected=catalog()['operators'][base['operator']]
    return {'selected_operator':{'key':base['operator'],'id':selected['id'],'name':selected['name']},
        'selection_mode':selection_mode,'rows':rows,'source':_source(),'native_verified':False,'notes':[BOUNDARY,
        '公共默认条件仍列首批三名的9个技能；扩展干员默认仅列自身全部技能。显式导入当前条件时只列当前干员。',
        '模型complete不是原生动作时钟核验；非零完整总量保持未知，原模型总量独立标为条件参考。',
        '各技能原生算式参考复制对应主计算结果，不另外重算；未开放技能不执行计算。',
        '调用方所选模组和专属事件条件只用于原干员；扩展干员不允许跨人复制条件。']}
''' +text[end:]
    return text

def view_draft(text):
    text=replace_once(text,"('skills', '首批三名全部技能')","('skills', '全部技能与条件分项')")
    text=replace_once(text,"    'panel': '编辑 scenario 培养、藏品和技能条件。operator：kaltsit=凯尔希·思衡托，silverash=凛御银灰，mechanist=机械师；trust 为加成进度0–100。结果分层诊断，不是实机认证。',",
        "    'panel': '编辑 scenario 培养、藏品和技能条件；支持固定资料内32名已适配干员，或显式导入当前干员。trust 为加成进度0–100。结果分层诊断，不是实机认证。',")
    text=replace_once(text,"    'skills': 'scenario 为声明培养条件；默认列首批三名的9个技能，可用 operators 限定干员。完整总量缺证时保持未知，模型条件总量另列参考。',",
        "    'skills': 'scenario 为声明培养条件。公共默认列首批三名的9个技能；扩展干员默认仅列自身，导入当前条件时固定仅当前干员。operators不能将扩展干员条件带给其他人。未开放技能只列名称与原因；完整总量缺证时保持未知，条件总量与主结果原生算式分列。',")
    old="""        elif command == 'skills':
            for row in data['rows']:
                parts += [_h(f"{row['operator']} · {row['skill']}技能 {row.get('name','')}"),_p(row['status'])]
                parts.append(_table(['指标','秒数 / 数值'],["""
    new="""        elif command == 'skills':
            selected=data['selected_operator']
            parts += [_p('当前条件归属：'+selected['name']+'；仅作声明条件下的参考。')]
            for row in data['rows']:
                parts += [_h(f"{row['operator']} · {row['skill']}技能 {row['name']}"),_p(row['status'])]
                parts.extend(_p(reason) for reason in row['unlock_reasons'])
                if not row['unlocked']:continue
                parts.append(_table(['指标','秒数 / 数值'],["""
    text=replace_once(text,old,new)
    old="""                parts.extend(_p(n) for n in row.get('missing_or_conditional_notes',[]))
        elif command == 'cultivation':"""
    new="""                native=row['native_panel_reference']
                from .panel_native_bridge import LABELS as NATIVE_LABELS,conditional_value
                parts += [_h('对应主结果 · 技能攻击与攻速'),
                    _p('来源核验：'+_text(native['source_valid'])+'；完整原生面板与实际技能时钟仍未知。'),
                    _table(['属性','现有模型值','条件算式参考','数值条件已闭合','完整原生值'],
                        [(NATIVE_LABELS[r['field']],r['model_value'],conditional_value(r),r['conditional_complete'],None)
                         for r in native['fields'] if r['phase']=='skill'])]
                parts.extend(_p(r['primitive_qualification']['reason']) for r in native['fields']
                    if r['phase']=='skill' and r.get('primitive_qualification',{}).get('reason'))
                parts.extend(_p(n) for n in row.get('missing_or_conditional_notes',[]))
        elif command == 'cultivation':"""
    text=replace_once(text,old,new)
    text=replace_once(text,"            if scenario.get('operator') not in calibration.OPERATORS:raise ValueError('校准工具目前仅支持凯尔希·思衡托、凛御银灰、机械师。')",
        "            allowed=catalog()['operators'] if command in ('panel','pair','skills') else calibration.OPERATORS\n"
        "            if scenario.get('operator') not in allowed:raise ValueError('此查询仅支持已适配干员。' if command in ('panel','pair','skills') else '此查询仅支持凯尔希·思衡托、凛御银灰、机械师。')")
    text=replace_once(text,"            payload['scenario']={k:v for k,v in scenario.items() if not str(k).startswith('_')}",
        "            payload['scenario']={k:v for k,v in scenario.items() if not str(k).startswith('_')}\n"
        "            if command=='skills':payload['operators']=[scenario['operator']]")
    return text

def main():
    manifest={'kind':'SECTION_285_PUBLIC_ADAPTER_DRAFT_NOT_IMPLEMENTED','sources':{},'drafts':{}}
    for rel,expected in EXPECTED.items():
        raw=(ROOT/rel).read_bytes();assert sha256(raw).hexdigest()==expected,rel
        text=raw.decode('utf-8').replace('\r\n','\n')
        modified=(calibration_draft if rel.endswith('/calibration.py') else view_draft)(text)
        output=HERE/'draft'/rel;output.parent.mkdir(parents=True,exist_ok=True)
        result=modified.replace('\n','\r\n').encode('utf-8') if b'\r\n' in raw else modified.encode('utf-8')
        compile(result,str(output),'exec')
        output.write_bytes(result)
        manifest['sources'][rel]=expected;manifest['drafts'][rel]=sha256(result).hexdigest()
    (HERE/'draft-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
