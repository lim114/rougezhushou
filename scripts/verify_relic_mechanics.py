"""Public-entry conformance sweep and full primary-data audit; no accuracy inflation."""
import hashlib,json,math,sys,time,unittest
import tomllib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.offline_scope import partition,scope_counts

def main():
    version=tomllib.loads((ROOT/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    data=mechanics();assert len(data['relics'])==272
    counts=Counter();by_item={};cases=0
    context={'gold':25,'parts_count':3,'current_hp_ratio':.65,'deployed_casters':2,
        'adjacent_allies':2,'skill_cast_stacks':3,'empty_slots':4,'deployed_seconds':80,
        'near_protection_point':1,'grudge_stacks':100,'enemy_first_damage_unused':1,
        'entered_zone_count':2,'active_other_aura_sources':1,'mercenary_recipient':1,'mercenary_stacks':1,
        'probe_stacks':2,'fire_rod_stacks':3}
    for rid,proof in data['relics'].items():
        assert proof['source'] and 'raw_buffs' in proof and 'bound_char_buffs' in proof
        statuses=Counter()
        for op,p in catalog()['operators'].items():
            result=calculate_damage({'operator':op,'skill':len(p['skills']),
                'relic_ids':[rid],'relic_context':context,'recruitment_kind':'emergency_hire'})
            for value in result['estimate']['base_stats'].values():assert math.isfinite(value) and value>=0,(rid,op)
            for key in ('initial_seconds','recharge_seconds','cycle_seconds','total_damage','total_healing'):
                value=result['estimate']['skill'][key]
                assert value is None or math.isfinite(value) and value>=0,(rid,op,key,value)
            record=result['relic_resolution']['records'][0]
            assert record['id']==rid
            if record['pending'] or record['missing_conditions']:
                assert not result['relic_resolution']['complete'],(rid,op)
            statuses[record['status']]+=1;cases+=1
        counts[proof['status']]+=1
        by_item[rid]={'data_status':proof['status'],'runtime_probe_statuses':dict(statuses)}
    assert counts==Counter(data['counts'])
    bound_cases=0;forbidden_cases=0
    for bid,buff in data['char_buffs'].items():
        for op,p in catalog()['operators'].items():
            if buff['required_profession'] and p['profession'] not in buff['required_profession'].split('|'):continue
            for skill in range(1,len(p['skills'])+1):
                try:r=calculate_damage({'operator':op,'skill':skill,'char_buff_ids':[bid]})
                except ValueError as error:
                    assert bid=='rogue_6_from_relic_10' and '禁止开启技能' in str(error),(bid,op,error)
                    forbidden_cases+=1;continue
                record=r['relic_resolution']['records'][0]
                assert record['recipient']==op and record['source_relic_id']==buff['relic_id']
                assert not r['relic_resolution']['token_effects'],(bid,op)
                for v in r['estimate']['base_stats'].values():assert math.isfinite(v) and v>=0,(bid,op,v)
                if record['pending']:assert not r['relic_resolution']['complete'],(bid,op)
                bound_cases+=1
    icon_receipt=json.loads((ROOT/'rouge/data/relic-icon-receipt.json').read_text(encoding='utf-8'))
    icons={i['id']:i for i in icon_receipt['icons']}
    icon_proof=[]
    for bid,buff in data['char_buffs'].items():
        icon=icons[buff['raw']['iconId']];path=ROOT/'rouge/data'/icon['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==icon['sha256'],bid
        icon_proof.append({'char_buff_id':bid,'icon_id':buff['raw']['iconId'],**icon})
    (ROOT/'TARGET_ICON_VERIFICATION.json').write_text(json.dumps({'verified_at':time.time(),
        'game_commit':data['commit'],'resource_commit':icon_receipt['commit'],'count':len(icon_proof),
        'icons':icon_proof,'recipient_capture_layout_verified':False},ensure_ascii=False,indent=2),encoding='utf-8')
    rows=[f'# 黑流树海藏品逐条核验与计算范围（{version}）','',
        '272 件均保留原始黑板、选择器、强化绑定数据和来源。下表是规则覆盖，不代表所有条件、组合或实战均已校准。',
        f'{counts["numeric"]} 件有不需额外数值输入的规则（含限定技能时序路径）；{counts["conditional"]} 件有条件规则；{counts["partial"]} 件仅覆盖部分机制；{counts["pending"]} 件战斗机制尚未接入；{counts["non_output"]} 件不提供干员输出加成。',
        '0.30按用户要求仅作局外计算：击倒/受击/实时生命、屏障与站位触发只保留资料，不属于计算待办；原始规则数量是历史机制解析量，不能当作当前计算覆盖量。',
        '当前范围：'+json.dumps(scope_counts(data),ensure_ascii=False)+'。reference_only为仅资料，mixed为稳定部分仍可算，offline含无数值加成的条目。',
        '定向强化不能因持有即套给全队；缺失条件及未核验叠加组合不套用。时序参考仍有模板和取值时刻待实测。',
        '数值规则含敌方参考参数，不等于完整伤害机制。幸运饼干持有条目仍pending；已确认绑定的charBuff另支持自然技力+0.8/秒，不作用攻击/受击回复。',
        '',f'固定来源：[{data["commit"]}]({data["source_url"]})。详细原始证据见 `rouge/data/relic-mechanics.json`。','',
        '| 藏品 | 原始解析 / 当前范围 | 当前计算效果 | 局外必需条件 / 未覆盖项 |','| --- | --- | --- | --- |']
    labels={'numeric':'数值规则，需匹配适用技能/单位','conditional':'条件规则','partial':'部分机制','pending':'待接入','non_output':'无干员输出加成'}
    for rid,p in data['relics'].items():
        active,reference,pending,reference_pending=partition(p,rid)
        scope='稳定部分计算，战斗部分仅资料' if (reference or reference_pending) and (active or pending) else '仅作效果资料' if reference or reference_pending else '局外计算范围'
        effects=', '.join(sorted({e['kind'] for e in active})) or '—'
        gaps=', '.join(sorted({e[k] for e in active for k in ('condition','recipient_condition','loss_pending_condition') if e.get(k)}))+('；' if pending else '')+'、'.join(pending)
        if any(e.get('eligible_stage_ids') for e in p['effects']):gaps+='；必须选择固定关卡敌人；居民HP仅8个已核验关卡，复合HP藏品组合未知'
        if any(e['kind']=='temporary_attack' for e in p['effects']):gaps+='；当前仅机械师/凛御银灰S3逐帧本体路径'
        if any(e['kind']=='temporary_ammo_speed' for e in p['effects']):gaps+='；已接入的常规攻击弹药路径，冷却中途变速仍待校准'
        if any(e['kind']=='enemy_weight_delta' for e in p['effects']):gaps+='；需要选定关卡敌人及已知重量；允许负值，不推算位移或伤害'
        if any(e['kind']=='enemy_spawn_hp_branch' for e in p['effects']):gaps+='；单件出生生命分支3%触发/2倍生命，当前分支未观测；其他生命藏品组合未知，不推算整关概率或击杀时间'
        if any(e['kind']=='neural_burst_scale' for e in p['effects']):gaps+='；当前神经积累路径只计瞬时爆发×2，附带元素不翻倍；额外1000/秒未排程，受影响完整总伤/周期DPS未知，另列已建模小计；其他元素分支待接入'
        if p.get('pending_scopes') and pending:gaps+='；未完成项仅在所需联动藏品持有且选择器适用时提示'
        if rid=='rogue_6_relic_assign_15':gaps+='；已确认绑定rogue_6_from_relic_15可单独计算自然技力+0.8/秒'
        if reference or reference_pending:gaps+='；排除部分仅保留原始说明，不要求事件输入'
        rows.append('| '+p['name'].replace('|',' / ')+' | '+labels[p['status']]+' / '+scope+' | '+effects+' | '+(gaps or '按职业/分支/位置选择器；隐藏脚本实测仍待验证').replace('|',' / ')+' |')
    (ROOT/'RELIC_COVERAGE.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    receipt={'verified_at':time.time(),'version':version,'audit_count':272,'data_rule_counts':dict(counts),
        'offline_scope':scope_counts(data),
        'counts_meaning':'data-rule coverage; not all-runtime or stacking accuracy',
        'public_entry_cases':cases,'operator_profiles':32,'relic_regression_tests':unittest.TestLoader().loadTestsFromNames(['tests.test_relics','tests.test_relic_extension','tests.test_relic_conditions_022','tests.test_relic_events_022']).countTestCases(),
        'bound_recipient_cases':bound_cases,'forbidden_skill_cases':forbidden_cases,'bound_icon_references_verified':15,
        'source_commit':data['commit'],'source_sha256':data['source_sha256'],
        'latest_snapshot':json.loads((ROOT/'.cache/research/relics/receipt.json').read_text(encoding='utf-8'))['latest_snapshot'],
        'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ('rouge/offline_scope.py','rouge/relics.py','rouge/deployment.py','rouge/run_modifiers.py','rouge/timing.py','rouge/sp_events.py','rouge/damage.py','rouge/operator_engine.py','rouge/estimate.py',
             'rouge/reporting.py','rouge/catalog.py','rouge/run_state.py','rouge/run_recognition.py',
             'rouge/resource_recognition.py','rouge/app.py','rouge/relic_events.py','rouge/relic_recognition.py','rouge/data/relic-reference-equivalence.json','rouge/data/relic-mechanics.json','tests/test_relics.py','tests/test_relic_extension.py','tests/test_relic_conditions_022.py','tests/test_relic_events_022.py')},
        'chat_requests':0,'new_live_combat_measurements':0,'per_item':by_item,
        'limits':['数据黑板核验不代表隐藏脚本实战核验。','酒类已提供假设下相位范围；隐藏阻回脚本、稳定强化领取者自动读取等局外机制仍待核验。战斗触发不属于当前计算待办。',
            '未知同键叠加组合不套用。','源石锭/零件是最近确认值，当前看不见不能证明未发生变化。',
            '短时攻击目前仅机械师和凛御银灰S3本体参考，未排程冲锋不套用；弹体取值脚本仍待校准。']}
    (ROOT/'RELIC_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('audit_count','data_rule_counts','public_entry_cases')},ensure_ascii=False))
if __name__=='__main__':main()
