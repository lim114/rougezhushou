"""Bounded static SP candidate audit; no product imports or runtime calls."""
from pathlib import Path
import hashlib
import json
import subprocess

OUT=Path(__file__).parent
REPO=Path('/workspace/rougezhushou')
BASE='9ef5a469673502754db3be320a8eece9a7fd18d4'
def sha(data):return hashlib.sha256(data).hexdigest()
def save_new(name,value):
 p=OUT/name;assert not p.exists(),str(p);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
paths=['PROJECT_PROGRESS.md','rouge/relics.py','rouge/run_modifiers.py','rouge/operator_engine.py','rouge/data/relic-mechanics.json']
blobs={p:subprocess.check_output(['git','show',BASE+':'+p],cwd=REPO) for p in paths}
bindings=[{'path':p,'fixed_commit':BASE,'bytes':len(blobs[p]),'sha256':sha(blobs[p])} for p in paths]
progress=blobs['PROJECT_PROGRESS.md'].decode().splitlines()
assert '技力回复倍率、负值及其它来源的完整核验' in progress[10]
assert progress[10].startswith('| 1 |')
book=json.loads(blobs['rouge/data/relic-mechanics.json'])
assert book['commit']=='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
positive=[]
for group in ('relics','char_buffs'):
 for identity,record in book[group].items():
  for index,effect in enumerate(record.get('effects',[])):
   if effect.get('kind')=='sp_recovery':
    positive.append({'group':group,'id':identity,'name':record['name'],'effect_index':index,'effect':effect,'pending':record.get('pending',[])})
assert len(positive)==6 and all(r['effect']['value']>0 for r in positive)
selected=['rogue_6_relic_legacy_2','rogue_6_relic_legacy_74','rogue_6_relic_fight_15']
narrow=[{'id':rid,'record':book['relics'][rid]} for rid in selected]
assert narrow[0]['record']['raw_buffs'][0]['blackboard'][0]['valueStr']=='modify_sp_recover[normal]'
assert narrow[1]['record']['raw_buffs'][0]['blackboard'][0]['valueStr']=='modify_sp_recover[medic]'
assert narrow[2]['record']['raw_buffs'][0]['blackboard'][0]['valueStr']=='rogue_6_hp_ratio_to_attr_add[sp_recover]'
fortune=next(r for r in positive if r['group']=='char_buffs')
assert fortune['id']=='rogue_6_from_relic_15' and fortune['effect']['skill_sp_type']=='INCREASE_WITH_TIME'
old=Path('/workspace/.continuation/p2-after-055-sp-audit')
note=old/'NOTE060.md';note_bytes=note.read_bytes()
assert sha(note_bytes)=='cd92c581710cb3256800043e170b952d685630f1bfa38641015a2f5f2cb4ae6c'
oldhandoff=old/'handoff-receipt060.json';old_handoff_bytes=oldhandoff.read_bytes()
old_handoff=json.loads(old_handoff_bytes)
assert old_handoff['files']['NOTE060.md']['sha256']==sha(note_bytes)
assert old_handoff['section']==60

ranges={
 'PROJECT_PROGRESS.md':[(10,12)],
 'rouge/relics.py':[(8,10),(110,120),(215,239),(326,334)],
 'rouge/run_modifiers.py':[(4,11),(23,38),(50,54)],
 'rouge/operator_engine.py':[(107,120),(187,210),(1304,1315),(1339,1349),(1455,1461),(1526,1529)],
}
excerpts=[]
for p,spans in ranges.items():
 lines=blobs[p].decode().splitlines()
 excerpts.append({'path':p,'sha256':sha(blobs[p]),'ranges':[{'start':a,'end':b,'lines':[{'line':i,'text':lines[i-1]} for i in range(a,b+1)]} for a,b in spans]})
receipt={'status':'FINAL_BOUNDED_NEGATIVE_NO_CONFIRMED_SP_PRODUCT_DEFECT','candidate_section':88,'numbered_section_completed':False,'fixed_commit':BASE,'confirmed_product_bugs':0,'confirmed_actionable_leads':[],'draft_or_patch_created':False,'product_authorization_claimed':False,'roadmap_exact_quote':{'line':11,'priority':1,'topic':'藏品局外机制','pending_text':'技力回复倍率、负值及其它来源的完整核验','classification_limit':'This fixed roadmap row is priority1; do not call it a newly confirmed P2 product defect solely from a backlog item.'},'fixed_source_bindings':bindings,'scope':'Existing public normalized mechanics active sp_recovery index only, narrow three named source bindings, SP consumers in requested source files, and immutable section60 note. Not a complete SP or roguelike semantic audit.','active_normalized_sp_recovery_rows':positive,'active_normalized_negative_sp_recovery_rows':0,'narrow_existing_rule_objects':narrow,'original_source_binding':{'game_commit':book['commit'],'declared_source_url':book['source_url'],'declared_original_table_sha256':book['source_sha256'],'declared_source_hash_is_new_original_byte_verification':False,'full_original_roguelike_table_read_or_rehashed':False,'scope':'Current fixed public mechanics preserves raw_buffs and source_buff_key/index for selected existing rules; no reconstruction of original historical cache or source table.'},'old_completed_source_context':[{'path':str(note),'bytes':len(note_bytes),'sha256':sha(note_bytes),'scope':'Sealed60 note: prior0.66 covers five named positive natural SP sources; Shu periodic averaging has already been repaired into unknown clock reference, not a new candidate.'},{'path':str(oldhandoff),'bytes':len(old_handoff_bytes),'sha256':sha(old_handoff_bytes),'scope':'Existing sealed60 source and test evidence only read; no matrix/API/test replay.'}], 'consumer_findings':['relics115-117 already gates the named FortuneCookie current natural-SP requirement; profession matching routes selected existing medic source.','relics218 hp curve factor only applies where explicitly specified; chosen existing Painkillers rule has nonnegative0..2 range under existing0..1 context. No new source multiplier inferred.','engine1307 adds actual natural attribute plus normalized positive effects;1310 selects natural SP path;1339 and1342 use separate attack/received SP paths,1528 reports rate only for natural SP.','engine110 signed-effect exception is only hp_pct/attack_speed; no currently active normalized negative SP rule was found to prove a source-backed error here. This does not prove no negative original/native SP source exists.','run_modifiers23-38 shown squad path recognizes only atk/max_hp/def multipliers; this is no evidence that unimplemented SP multiplier should be guessed or activated.','Shu periodic source is already stored with native clock unknown and complete recharge withheld; reintroducing interval averaging is not authorized.'], 'source_excerpts':excerpts,'remaining_unknowns':['Any negative SP original selector and its actual consumer/value domain','Multiplicative SP composition layer, cap/clamp, stacking and native attachment','Other original SP sources not covered by this narrow existing normalized index','Current hotupdate/account/live game/source ordering and periodic clocks'],'next_step':'Keep broader SP backlog open. Reopen only with an exact new original selector or verified source contract that conflicts with actual current consumer; then seek explicit product-stage authorization. No candidate section should be manufactured from this negative result.','new_API_calls':0,'new_product_helper_calls':0,'tests_run':0,'GUI_calls':0,'Wine_calls':0,'network_calls':0,'tracked_edits':0,'historical_cache_reconstructed':False,'bool86_finite_or_module102_audit_repeated':False,'preparation_diagnostics':[{'path':'rouge/relic_rules.py','failure':'read-only guessed file absent in fixed commit; actual rule source is relics.py and relic-mechanics.json','dependent_API_tests_or_mutations_started':False}]}
save_new('sp-negative-source-receipt088.json',receipt)
note_text='''# 088 SP窄候选：阴性封存

未发现已证实的SP产品缺陷，不创建或计作第88节产品小节。固定9ef5a46的PROJECT_PROGRESS第11行其实归priority1藏品局外机制；backlog原句不是缺陷证明。

只读当前500847B公开normalized mechanics中的active sp_recovery索引，六条都是正数；再核香草沙士汽水、医者-自医、止痛片三件保存的raw_buffs绑定与对应现有consumer。幸运饼干自然SP类型gate已经在relics115–117接入。engine1307使用加算，1310/1339/1342分自然/攻击/受击SP，1528只为自然SP公开rate。没有由已有negative SP来源直接证明的错误。

engine110不接受negative SP效果，现支持signed只hp_pct/attack_speed，但本次没有发现活跃normalized负SP原来源能使这一点成为确认bug。不能据此宣称原表不存在负SP。原始table的f586哈希仅是当前normalizedbook已有声明，并非本次fresh完整原表证明；没有大扫roguelike全表、补缓存或推断native倍率层。

旧0.66五件正自然SP与第60节黍周期unknown是已完成范围，旧note/handoff只读绑定，没有重跑旧矩阵、helper或测试。周期首跳/阻回未知仍保持；不会重新平均成自然SP。分队路径目前仅把atk/max_hp/def接入也不足以授权新SP数值。

后续需要一个精确新原selector或已验证source合同，与当前实际consumer直接冲突，才可形成产品候选；负值、倍率组合层、cap/clamp/叠加和native附着仍未闭合。0API/helper/tests/Qt/Wine/network/tracked改动，无草案或补丁，不重复86布尔/finite/102模组审计。
'''
p=OUT/'NOTE.md';assert not p.exists();p.write_text(note_text)
save_new('handoff-sp-negative088.json',{'status':receipt['status'],'receipt_path':str(OUT/'sp-negative-source-receipt088.json'),'receipt_sha256':sha((OUT/'sp-negative-source-receipt088.json').read_bytes()),'source_script_path':str(OUT/'seal_sp_negative088.py'),'source_script_sha256':sha((OUT/'seal_sp_negative088.py').read_bytes()),'explicit_final_frozen':True,'confirmed_product_bugs':0,'draft_or_numbered_section':False,'new_API_helper_tests_GUI_Wine_network_tracked':0,'scope':'Narrow existing SP source-index/three bindings/actual requested source consumers only; original global/native contracts remain unknown.'})
files=[]
for path in sorted(OUT.iterdir()):
 if path.is_file():
  data=path.read_bytes();files.append({'source_path':str(path),'archive_path':path.name,'bytes':len(data),'sha256':sha(data)})
save_new('public-artifacts-manifest-sp088.json',{'format_version':1,'status':'FINAL_SEALED_BOUNDED_NEGATIVE','candidate_section':88,'files':files,'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files),'manifest_self_excluded':True,'public_artifacts_only':True,'excluded':['complete source/execution copies and large normalized mechanics; exact fixed hashes and small excerpts retained','original whole rogue table/historical caches not read or reconstructed','old source60 API matrices/tests not copied or repeated']})
for row in files:
 data=Path(row['source_path']).read_bytes();assert sha(data)==row['sha256'] and len(data)==row['bytes']
print(json.dumps({'status':receipt['status'],'handoff_sha256':sha((OUT/'handoff-sp-negative088.json').read_bytes()),'receipt_sha256':sha((OUT/'sp-negative-source-receipt088.json').read_bytes()),'manifest_sha256':sha((OUT/'public-artifacts-manifest-sp088.json').read_bytes()),'file_count':len(files),'total_bytes':sum(r['bytes'] for r in files)},ensure_ascii=False))
