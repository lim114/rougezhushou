"""Build a complete stage-specific body/disguise documentary reference."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,json,re,html

PACK='research/p3-enemy-form-306'
DATA='rouge/data/enemy-form-reference.json'
BATTLE='rouge/data/battle-previews.json'
BATTLE_SHA='f0155647af8766eb2f01e84295f85b7300264fc49b40ffc82e89800837d274f3'
LEVEL='research/p3-spawn-candidates-299/levels/b68d3e2163e87d4b5da63004768f6cb3f8eaa5b5c66bcf56b72732c1a42f3dda.json'
LEVEL_SHA='b68d3e2163e87d4b5da63004768f6cb3f8eaa5b5c66bcf56b72732c1a42f3dda'
DOC=PACK+'/community-complete-revisions.json'
DOC_SHA='abfba05269d8f675b32d019ef5de877a46a1a88377bc38c39390e74e7ad18413'
GLOSSARY=PACK+'/abnormal-complete-440606.html'
GLOSSARY_SHA='a6a24fd79bca9c3072e44b22032888cbaf5d366c0904c804df698cc8a73e320a'
TARGETS={'enemy_2133_shdopl_lancer':('enemy_1072_dlancer','萨卡兹穿刺手'),
 'enemy_2133_shdopl_mpmage':('enemy_10079_mpmage','稳定态萨卡兹术师结晶'),
 'enemy_2133_shdopl_sword':('enemy_1075_dmgswd','萨卡兹魔剑士'),
 'enemy_2133_shdopl_demonk':('enemy_1501_demonk','萨卡兹百夫长')}

def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def pin(raw):return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def require(value,text):
 if not value:raise ValueError(text)
def read(root,name,expected):
 raw=(root/name).read_bytes();require(sha256(raw).hexdigest()==expected,'Pinned complete source changed: '+name);return raw
def build(root,output):
 root,output=Path(root),Path(output)
 battle_raw=read(root,BATTLE,BATTLE_SHA);battle=json.loads(battle_raw)
 level_raw=read(root,LEVEL,LEVEL_SHA);level=json.loads(level_raw)
 doc_raw=read(output,DOC,DOC_SHA);doc=json.loads(doc_raw)
 glossary_raw=read(output,GLOSSARY,GLOSSARY_SHA);glossary=glossary_raw.decode('utf8')
 require(re.findall(r'"wgRevisionId"\s*:\s*(\d+)',glossary)==['440606'],'Exact freshly observed glossary revision required')
 glossary_rows=[]
 for code,title,meaning in(('ALLY_TARGET_FREE','孤立','无法被同阵营选中'),('BLOCK_FREE','不可阻挡','无法阻挡/被阻挡，自动解除阻挡')):
  anchor=glossary.index('<code>'+code+'</code>');start=glossary.rfind('<tr',0,anchor)
  first_end=glossary.index('</tr>',anchor)+5;end=glossary.index('</tr>',first_end)+5;span=glossary[start:end]
  plain=' '.join(html.unescape(re.sub('<[^>]+>',' ',span)).split())
  require(title in plain and meaning in plain,'Complete glossary definition changed: '+code)
  glossary_rows.append({'code':code,'title':title,'meaning':meaning,'byte_start':len(glossary[:start].encode('utf8')),
   'byte_end':len(glossary[:end].encode('utf8')),'span_sha256':sha256(span.encode('utf8')).hexdigest()})
 pages={p['title']:p for p in doc['query']['pages'].values()}
 body_page=pages['空值体'];stage_page=pages['ISW-NO 本性难移']
 require(body_page['revisions'][0]['revid']==440600 and stage_page['revisions'][0]['revid']==423328,'Exact complete documentary revisions required')
 body_text=body_page['revisions'][0]['slots']['main']['*'];stage_text=stage_page['revisions'][0]['slots']['main']['*']
 phrases=[
  '拥有被动Buff：{{异常效果|无敌}}、{{异常效果|不可阻挡}}、{{异常效果|孤立}}（自身的【伪装体】退场时解除）',
  '出场时在自身所在地块中心以自身路径召唤并标记一名指定的敌人作为【伪装体】（默认召唤[[狂暴的猎狗pro]]），成功召唤后自身进入消失状态',
  "'''模型上具有噪声特效'''；{{特殊机制|无害目标}}，不会阻止波次",
  '受到伤害时（优先级+2000）退场（跳过重生，视为无原因退场）',
  "退场时令召唤自身的'''空值体'''强制传送到自身所在地块中心<!--并结束其遭受的拖拽效果-->、继承自身当前剩余路径、结束消失状态、并结束当前停驻（若有）",
  "※站内关卡页面的'''空值体'''记作：'''空值体(伪装体名称)'''"
 ]
 require(all(x in body_text for x in phrases)and'|地位级别=普通'in body_text,'Complete lifecycle/name/tier documentation changed')
 source={'game_commit':battle['source']['game_commit'],'battle':{'file':BATTLE,**pin(battle_raw)},
  'original_level':{'file':LEVEL,**pin(level_raw)},'community_response':{'file':DOC,**pin(doc_raw)},
  'body_document':{'title':'空值体','revision':440600,'url':'https://prts.wiki/index.php?title=空值体&oldid=440600'},
  'stage_document':{'title':'ISW-NO 本性难移','revision':423328,'url':'https://prts.wiki/index.php?title=ISW-NO_本性难移&oldid=423328'},
  'glossary':{'file':GLOSSARY,**pin(glossary_raw),'revision':440606,'url':'https://m.prts.wiki/w/异常效果?oldid=440606'}}
 lifecycle=[
  {'phase_key':'hidden_body','title':'本体与伪装分开存在','text':'文献记载：本体具有无敌、不可阻挡（不能被阻挡）和孤立（不能被同阵营选中）；在自身格子中心召唤指定敌人作伪装，成功后本体消失。这些效果在伪装体退场时解除。','conditions':['成功召唤伪装后本体消失','伪装体退场后解除所列效果'],'source_quotes':phrases[:2]},
  {'phase_key':'disguise','title':'受伤的是伪装体','text':'文献记载：伪装外观带噪声特效，属于无害目标，不会阻止波次；受到伤害时退场，不触发其重生。详细退场处理保留在技术资料中。','conditions':['受到伤害','这次退场不能直接当作已确认的一次正常击倒'],'source_quotes':phrases[2:4]},
  {'phase_key':'revealed_body','title':'伪装退场后，本体现身','text':'文献记载：本体传送到伪装体所在格子的中心，继承其剩余路径、结束消失，并结束当前停驻（若有）。这里不生成实时位置、路线或发生时刻。','conditions':['伪装体退场','当前停驻仅在确实存在时结束'],'source_quotes':[phrases[4]]}
 ]
 differences=[
  {'key':'source_names','title':'名称差异','text':'本关专属原数据写“空植体”，原型图鉴与PRTS写“空值体”。这里只说明对应关系，不改写原敌人名称。'},
  {'key':'body_vs_disguise','title':'不是把伪装敌人变成本体','text':'指定敌人的独立资料与本体分别保留；不能把伪装目标的属性、分类或能力当成本体的数值。'},
  {'key':'base_vs_alias_tier','title':'图鉴分类不能代替本关分类','text':'文献将普通图鉴中的空值体列为普通敌人，但本关四种特殊版本的类别仍未知，不能据此套用普通或精英的难度修正。'},
  {'key':'summon_level','title':'召唤等级仍待核实','text':'本关有对应敌人的独立资料可供阅读，但召唤者的原资料没有明确实际召唤等级；不能直接把常见等级当作本局结果。'},
  {'key':'damage_vs_attack','title':'触发措辞不同','text':'本关原数据概述写“受攻击时解除”；PRTS详细文献写“受到伤害时”令伪装体退场。此处保留两份表述，不推断未造成伤害的攻击也必然触发。'},
  {'key':'documentary_lifecycle_scope','title':'图鉴文献的适用边界','text':'分阶段说明来自空值体的普通图鉴文献；本关原资料明确记载对应关系和伪装对象，但实际是否采用全部行为、触发是否已经发生仍未确认。'}
 ]
 rows=[];selected_stages={}
 for sid,difficulty in(('ro6_n_2_3','NORMAL'),('ro6_e_2_3','FOUR_STAR')):
  stage=battle['stages'][sid];require(stage['name']=='本性难移'and stage['difficulty']==difficulty and stage['level_source']['sha256']==LEVEL_SHA,'Exact fixed stage mismatch')
  selected_stages[sid]=deepcopy(stage)
  for eid,(target_id,name)in TARGETS.items():
   originals=[x for x in level['enemyDbRefs']if x['id']==eid and x['level']==0]
   bodies=[x for x in stage['enemies']if x['id']==eid and x['level']==0]
   targets=[x for x in stage['enemies']if x['id']==target_id]
   require(len(originals)==len(bodies)==len(targets)==1,'Unique complete body/target/original required')
   original,body,target=originals[0],bodies[0],targets[0];over=original['overwrittenData']
   require(original['useDb']is False and over['levelType']=={'m_defined':False,'m_value':'NORMAL'},'Do not promote unassigned rank placeholder')
   require(over['name']=={'m_defined':True,'m_value':'空植体'}and body['name']=='空植体'and body['level_type']is None,'Raw name/classification changed')
   require(over['prefabKey']=={'m_defined':True,'m_value':'enemy_2133_shdopl'},'Exact body resource changed')
   require(over['talentBlackboard']==[{'key':'summon.enemy_key','value':0.0,'valueStr':target_id}],'Exact summon declaration changed')
   require(target['name']==name and target['level']==0 and '显示名=空值体('+name+')'in stage_text,'Exact independently documented target mismatch')
   rows.append({'stage_id':sid,'stage_name':stage['name'],'difficulty':difficulty,'enemy_id':eid,'level':0,
    'fixed_name':'空植体','community_base_name':'空值体','documented_variant_name':'空值体('+name+')',
    'body_reference':deepcopy(body),'disguise_enemy_reference':deepcopy(target),
    'complete_original_reference':deepcopy(original),'declared_summon_enemy_key':target_id,
    'selected_disguise_reference_level':0,'declared_summon_level':None,
    'documented_base_tier_reference':'普通','fixed_body_tier':None,
    'documented_lifecycle':deepcopy(lifecycle),'source_differences':deepcopy(differences),
    'source':deepcopy(source),'current_server_verified':False,'original_runtime_callback_verified':False})
 require(len(rows)==8,'Complete eight stage/alias/level references required')
 authority={'schema':'enemy_form_selected_authority_v1','complete_community_pages':pages,
  'complete_selected_stages':selected_stages,'complete_battle_source':deepcopy(battle['source']),
  'complete_original_level_refs':[x for x in level['enemyDbRefs']if x['id']in TARGETS],
  'rows':deepcopy(rows),'complete_glossary_definitions':glossary_rows}
 data={'schema':'enemy_form_reference_v1','rows':rows,'source':source,
  'scope_notice':'仅列本性难移普通/紧急的四种专属派生、共8处固定引用；不是本局实际出现、完整技能或动态状态证明。',
  'level_type_applied':False,'modifiers_changed':False,'maps_changed':False}
 outputs={DATA:encoded(data),PACK+'/selected-authority-records.json':encoded(authority)}
 runtime={name:pin(raw)for name,raw in outputs.items()}
 runtime.update({BATTLE:pin(battle_raw),LEVEL:pin(level_raw),DOC:pin(doc_raw),GLOSSARY:pin(glossary_raw)})
 manifest={'schema':'enemy_form_source_manifest_v1','data_file':DATA,'data_sha256':sha256(outputs[DATA]).hexdigest(),'runtime_files':runtime,
  'all_members_required_for_each_target_query':True,'row_count':8,'actual_state_or_modifiers_applied':False,'source':source}
 outputs[PACK+'/source-manifest.json']=encoded(manifest)
 template=(output/PACK/'backend-template.py').read_text(encoding='utf8')
 outputs['rouge/enemy_form_reference.py']=template.replace('__DATA_SHA__',sha256(outputs[DATA]).hexdigest()).replace('__MANIFEST_SHA__',sha256(outputs[PACK+'/source-manifest.json']).hexdigest()).encode('utf8')
 for name,raw in outputs.items():
  path=output/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
 receipt={'kind':'source_build_only_not_product_acceptance','rows':8,'stages':2,'aliases':4,'complete_community_pages':2,'complete_glossary_pages':1,'runtime_source_members':6,'outputs':{k:pin(v)for k,v in outputs.items()}}
 (output/PACK/'build-receipt.json').write_bytes(encoded(receipt));return receipt

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output-root',type=Path,required=True);a=p.parse_args();print(json.dumps(build(a.root,a.output_root),ensure_ascii=True))
