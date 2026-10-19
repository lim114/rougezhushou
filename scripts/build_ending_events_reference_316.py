"""Source-bound current ending-event records; no inferred source scripts."""
from pathlib import Path
from hashlib import sha256
import json,argparse
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-ending-events-316'
DATA='rouge/data/ending-events-reference.json'
CHOICES={'entry':['choice_ro6_final1_8'],'button':['choice_ro6_end4_1','choice_ro6_end4_2','choice_ro6_end4_3'],
 'revive':['choice_ro6_revive_1','choice_ro6_revive_2','choice_ro6_revive_3'],
 'blueprint':['choice_ro6_end5_1','choice_ro6_end5_2','choice_ro6_end5_3','choice_ro6_end5_4','choice_ro6_end5_5']}
ITEMS=['rogue_6_relic_final_'+str(n)for n in(7,8,9,10)]
STAGES=['ro6_s_1','ro6_n_7_1','ro6_e_7_1','ro6_n_7_2','ro6_e_7_2','ro6_b_7','ro6_b_7_b']

def encode(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def build(root=ROOT):
 root=Path(root);current=json.loads((root/'research/p3-expansion-313/current-topic.json').read_bytes())['details'];receipt=json.loads((root/PACK/'source-receipt.json').read_bytes());excerpt=(root/PACK/'topic-441984-excerpt.md').read_bytes()
 assert receipt['revision_from_actual_scraped_fixed_link']=='441984'and sha256(excerpt).hexdigest()==receipt['excerpt_sha256']and len(excerpt)==receipt['excerpt_bytes']
 text=excerpt.decode();assert '灰坑'in text and'手术祭坛'in text and'该机会每局流程仅限一次'in text and'最少6（待补充）'in text
 ids=[c for cs in CHOICES.values()for c in cs];assert len(ids)==len(set(ids))==12
 selected={'choices':{k:current['choices'][k]for k in ids},'items':{k:current['items'][k]for k in ITEMS},'stages':{k:current['stages'][k]for k in STAGES},'zone':current['zones']['zone_7']}
 selected['scenes']={k:current['choiceScenes'][k]for k in dict.fromkeys(c['nextSceneId']for c in selected['choices'].values()if c['nextSceneId'])}
 assert selected['choices']['choice_ro6_end4_3']['title']=='这下有麻烦了'and selected['choices']['choice_ro6_final1_8']['title']=='帮助倒下的探险家同伴'
 assert selected['stages']['ro6_s_1']['name']=='灰坑'and [s['name']for k,s in selected['stages'].items()if k.startswith('ro6_b_7')]==['熄日','熄日']
 assert selected['zone']['name']=='盲目者所见'
 records=[{'id':'entry','title':'险路尽头 · 取得线索','group':'线索与区域','choice_ids':CHOICES['entry'],'item_ids':[ITEMS[0]],'stage_ids':[],
  'facts':['内容拓展一之后，完成一次结局可解锁相关收藏品。','在第一或第二主层的险路尽头，可看到帮助探险家同伴的相关选项。','选择该项消耗10源石锭，关联藏品为谒日之祈；能否支付与事件是否出现分别核对。']},
 {'id':'side_path','title':'熄日余径 · 后续区域说明','group':'线索与区域','choice_ids':[],'item_ids':ITEMS[:2],'stage_ids':[],
  'facts':['持有谒日之祈后，从血色空脉起的后续区域会出现熄日余径；这里是探索区域，不是战斗关卡名。','该部分不与主要区域连通，不能直接徒步进入。','祭日之契使后续不再出现熄日余径；这不证明应删除以前经过的节点。','节点总数仍待补充，不将旧6至7或当前最少6写成已核验的模板上限。']},
 {'id':'path_bonus','title':'熄日余径 · 普通作战附加奖励','group':'线索与区域','choice_ids':[],'item_ids':[],'stage_ids':[],
  'facts':['固定社区资料说明：完成熄日余径的普通作战节点后，额外获得1件随机收藏品。','这不是所有区域、紧急作战或分支都额外加1的依据，也不是已领奖或完整奖励池。']},
 {'id':'button','title':'大红按钮','group':'命运所指','choice_ids':CHOICES['button'],'item_ids':[ITEMS[1]],'stage_ids':['ro6_s_1'],
  'facts':['熄日余径中的命运所指固定对应大红按钮。','探险家存活时，选择“这个按钮是做什么用的？”后，再选“这下有麻烦了”，文献明确指向特殊作战灰坑。','存活条件针对这条推进分支，不应因此把拒绝选项或整个事件当作不存在。','灰坑中的沉沦探险者有强制结束关卡的相关技能；这里不代替战斗判断或操作。']},
 {'id':'revive','title':'手术祭坛','group':'不期而遇','choice_ids':CHOICES['revive'],'item_ids':[ITEMS[2]],'stage_ids':[],
  'facts':['探险家在余径战斗中首次倒下后，下次进入无标记不期而遇会遭遇该事件；救援机会每局一次。','小心地移除电极会失去一半目标生命上限，并关联破碎噩兆，使探险者重新出现在余径战斗中。','一半的实际整数处理和已发生的领奖仍未核验，不在此推算数值或改写记忆。']},
 {'id':'blueprint','title':'制图桌','group':'出现类型未确认','choice_ids':CHOICES['blueprint'],'item_ids':[ITEMS[3]],'stage_ids':[],
  'facts':['端详那册精致的图纸关联生命蓝图；该项在结局说明中是非必须选择。','原文说明强化敌人并使熄日出现额外敌人，具体效果阅读藏品原文。','文献未明确给出完整出现前置、所属节点类型及具体关卡版本绑定，不因属于同一结局就塞入所有命运所指或不期而遇。']},
 {'id':'hidden_region','title':'盲目者所见 · 相关作战','group':'线索与区域','choice_ids':[],'item_ids':ITEMS[1:],'stage_ids':STAGES[1:],
  'facts':['文献标为第六层隐藏区域；普通作战包括贫瘠行军、不解之缘及各自紧急版，险路恶敌为熄日。','原表有两份同名熄日配置，保留独立入口；没有逐条证据时不按名称、后缀或是否持有生命蓝图自动挑选版本。','阅读相关战斗不表示本局已进入隐藏区域、满足全部前置或触发了对应版本。']}]
 data={'schema':'ending_events_316_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','source':receipt,'selected_originals':selected,'records':records,
       'direct_documented_choice_battle_links':{'choice_ro6_end4_3':['ro6_s_1']},'original_scene_choice_script_restored':False,'actual_server_verified':False,'actual_rewards':None,'inventory_updated':False,'generation_probabilities':None}
 raw=encode(data);names=['research/p3-expansion-313/current-topic.json',PACK+'/source-receipt.json',PACK+'/topic-441984-excerpt.md']
 files={n:{'sha256':sha256((root/n).read_bytes()).hexdigest(),'bytes':(root/n).stat().st_size}for n in names};files[DATA]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
 manifest=encode({'schema':'ending_events_316_manifest_v1','game_commit':data['game_commit'],'files':files,'current_battle_reference_required':True,'original_scene_choice_script_restored':False})
 return raw,manifest

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args();raw,manifest=build()
 for name,value in((DATA,raw),(PACK+'/runtime-manifest.json',manifest)):
  if a.check:assert(ROOT/name).read_bytes()==value
  if a.write:(ROOT/name).write_bytes(value)
 print(json.dumps({'manifest_sha256':sha256(manifest).hexdigest(),'records':7,'choices':12,'stage_refs':7}))
