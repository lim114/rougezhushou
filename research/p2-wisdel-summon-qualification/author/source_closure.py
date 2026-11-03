import hashlib,json,pathlib,subprocess,sys
sys.dont_write_bytecode=True;p=pathlib.Path(__file__).resolve().parent;root=pathlib.Path('/workspace/rougezhushou');frozen=p/'frozen70';sys.path.insert(0,str(frozen))
from rouge.catalog import catalog
from rouge.operator_options import OPTIONS
from rouge.operator_engine import selected_talents
sha=lambda b:hashlib.sha256(b).hexdigest();freeze=json.loads((p/'freeze70.json').read_text());assert all(sha((frozen/r).read_bytes())==h for r,h in freeze['public_source_hashes'].items())
commit='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add';tables={};sources={}
for name,h in [('character_table','68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),('skill_table','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')]:
 path=root/'.cache/p2-s1-binding'/(name+'.json');b=path.read_bytes();assert sha(b)==h;tables[name]=json.loads(b);sources[name]={'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{commit}/zh_CN/gamedata/excel/{name}.json','bytes':len(b),'sha256':h}
op='char_1035_wisdel';token='token_10035_wisdel_wward';raw=tables['character_table'][op];profile=catalog()['operators'][op];candidates=raw['talents'][1]['candidates'];assert len(candidates)==1;t=candidates[0];entry=raw['skills'][2]
assert t['name']=='死魂灵的余息' and t['tokenKey']==token and t['unlockCondition']=={'phase':'PHASE_2','level':1} and t['requiredPotentialRank']==0 and t['prefabKey']=='2'
assert entry['skillId']=='skchr_wisdel_3' and entry['overrideTokenKey']==token and entry['unlockCond']=={'phase':'PHASE_2','level':1}
n=profile['talents'][1][0];assert (n['name'],n['description'],n['phase'],n['level'],n['potential_rank'])==(t['name'],t['description'],2,1,0);assert 'tokenKey' not in n
assert token in profile['tokens'] and profile['skills'][2]['unlock_elite']==2
levels=tables['skill_table'][entry['skillId']]['levels'];common=['立刻在攻击范围内召唤','个魂灵之影（最多存在3个，技能结束后保留）'];rank_checks=[]
for rank,lvl in enumerate(levels,1):
 bb={b['key']:b['value'] for b in lvl['blackboard']};assert profile['skills'][2]['levels'][rank-1]['values']==bb and profile['skills'][2]['levels'][rank-1]['description']==lvl['description'];assert all(s in lvl['description'] for s in common)
 rank_checks.append({'rank':rank,'description':lvl['description'],'values':bb,'identity_matches':True})
controls=[x for x in OPTIONS[op] if x[0] in ('ghost_count','ghost_casts')];assert controls[0][1]=='在场魂灵之影数量';assert controls[1][1]=='窗口内命中当前目标的魂灵施放次数'
checks=[]
for elite,level in [(0,1),(0,50),(1,1),(1,80),(2,1),(2,59),(2,60),(2,90)]:
 for potential in range(1,7):
  for module_level in range(4):
   s={'operator':op,'elite':elite,'level':level,'potential':potential,'module_id':'uniequip_002_wisdel' if module_level else None,'module_level':module_level};talents,_=selected_talents(profile,s);chosen=next((x for x in talents if x['name']==t['name']),None);assert (chosen is not None)==(elite>=2);checks.append({'scenario':s,'base_route_cultivation_qualified':elite>=2,'second_talent_selected':chosen is not None})
selectors={'character_table.char_1035_wisdel.talents[1]':raw['talents'][1],'character_table.char_1035_wisdel.skills[2]':entry,'skill_table.skchr_wisdel_3.levels':levels,'character_table.token_10035_wisdel_wward.skills':tables['character_table'][token]['skills']}
(p/'pinned-summon-route-selectors.json').write_text(json.dumps(selectors,ensure_ascii=False,indent=2)+'\n')
data={'schema_version':1,'operator_id':op,'token_id':token,'scope':'仅固定原表第二天赋与第三技能两条本体召唤途径的培养资格资料；不证明声明来源、当前存在、实际施放或全部模组/藏品途径。','source_commit':commit,'sources':sources,'talent_route':{'source_selector':'character_table.char_1035_wisdel.talents[1].candidates[0]','talent_index':1,'prefab_key':t['prefabKey'],'name':t['name'],'description':t['description'],'unlock_elite':2,'unlock_level':1,'required_potential_rank':0,'token_key':t['tokenKey']},'skill_route':{'source_selector':'character_table.char_1035_wisdel.skills[2]','skill_number':3,'skill_id':entry['skillId'],'override_token_key':entry['overrideTokenKey'],'unlock_elite':2,'unlock_level':1,'original_common_fragments':common,'levels':[{'source_selector':f'skill_table.skchr_wisdel_3.levels[{rank-1}]','rank':rank,'description':lv['description'],'values':{b['key']:b['value'] for b in lv['blackboard']}} for rank,lv in enumerate(levels,1)]}}
q=p/'draft/rouge/data/wisdel-summon-qualification-reference.json';q.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
engine=(frozen/'rouge/operator_engine.py').read_text();summons=(frozen/'rouge/summons.py').read_text();assert "token=self.token_stats('token_10035_wisdel_wward')" in engine and "phases=profile['tokens'][token_id]['phases'];elite=scenario.get('elite',2)" in summons
contract={'controls':controls,'declared_count_contract':'existing window source declaration; no established provenance from owner or other independent source','panel_binding':'current owner profile token phases/cultivation reference, not proof of actual source availability','old_research':'research/p2-wisdel-ghost-clock/RESEARCH.md','zero_window_positive_cast_existing_error':'零长度观察窗口不能声明魂灵施放命中。','qualification_data_does_not_change_any_gate_or_number':True,'S1_S2_rank_must_not_be_inherited_as_S3_rank':True,'S3_rank_specific_description_only_if_currently_selected_S3':True,'unselected_S3_display':'only exact shared original description fragments with dynamic count omitted'}
receipt={'baseline_head':freeze['baseline_head'],'source_commit':commit,'sources':sources,'actual_raw_bytes_rehashed':True,'new_download':False,'direct_talent_tokenKey_and_skill_overrideTokenKey':True,'catalog_talent_did_not_retain_tokenKey_field':'new source data explicitly fixed original selector, not inferred catalog tokenKey','cultivation_selection_cases':checks,'ten_S3_rank_identity_and_common_fragments_checks':rank_checks,'field_contract':contract,'new_data_sha256':sha(q.read_bytes()),'no_native_clock_random_proof':True,'no_private_state_read':True,'no_production_edits':True}
(p/'source-closure.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'source_closed':True,'baseline':freeze['baseline_head'],'qualification_cases':len(checks),'skill_ranks':len(rank_checks),'data_sha256':sha(q.read_bytes())}))
