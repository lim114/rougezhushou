from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
from copy import deepcopy
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def load(n):return json.loads((ROOT/n).read_bytes())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()=='c45ffb00f1932a27919885440b98a52094b087e0'
h=load('.cache/p3-307-annotations/HANDOFF.json');base=Path(h['candidate_root']);before={}
for name,pin in h['production_before'].items():assert sha(ROOT/name)==pin['sha256'],name
for name,pin in h['promotion_files'].items():
 source=base/name;target=ROOT/name;assert sha(source)==pin['sha256'] and source.stat().st_size==pin['bytes']
 assert not target.exists() or name in h['production_before'],name
 before[name]=sha(target) if target.exists() else None
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
compat=load('.cache/p3-307-compat/HANDOFF.json')
old_raw=subprocess.check_output(['git','show',compat['source_commit']+':rouge/player_node_information.py'],cwd=ROOT)
assert sha256(old_raw).hexdigest()==compat['source_sha256']
for name in compat['candidate_paths']:
 source=ROOT/'.cache/p3-307-compat/candidate'/name;pin=compat['files']['candidate/'+name]
 assert sha(source)==pin['sha256'] and source.stat().st_size==pin['bytes']
 target=ROOT/name;before[name]=sha(target) if target.exists() else None;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
out=ROOT/'verification/sections/307-preparation';out.mkdir(parents=True,exist_ok=True)
record={'section':307,'kind':'source_and_code_promotion_not_acceptance','at_Beijing':datetime.now(timezone(timedelta(hours=8))).isoformat(),'before_sha256':before,'after_sha256':{n:sha(ROOT/n) for n in before},'legacy_event_planning_sha256':sha(ROOT/'rouge/event_planning.py'),'legacy_299_manifest_sha256':sha(ROOT/'research/p3-battle-entry-compatibility-299/source-manifest.json'),'only_4_old_presentation_test_calls_historical':True,'raw_190_resources_unchanged':True,'old_player_source_verified_against_real_commit':compat['source_commit']}
(out/'promotion.json').write_bytes(enc(record));(out/'execution-promotion.py').write_bytes(Path(__file__).read_bytes())
for n in ('exact-ten-evidence.json','complete-selected-DOM-groups.json'):
 (out/n).write_bytes((ROOT/'.cache/p3-307-note-evidence'/n).read_bytes())
cp=load('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==306 and cp['next_section']==307
cp['historical_before307_batch']=deepcopy(cp['current_batch']);cp['batch_start_section']=307;cp['batch_status']='P3_SECTION307_IN_PROGRESS'
cp['current_batch'].update(start=307,status=cp['batch_status'],batch_closed=False,next_section=307,next_section_started=True)
cp['active_section']={'number':307,'status':'implementation_not_completed','planned_change':'事件附注区分出现前条件和选择后结果，保留全部资格与旧结果入口','acceptance':'16附注完整核验、十条结果不误标条件、38事件当前/历史成对、资格资源原接口不变、3阅读出口及真实源失效/恢复'}
cp['next_action']='进行第307节事件附注分类与玩家阅读验证；306仍是已完成断点，不能把资料/代码准备计入完成。'
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
print(json.dumps({'promoted_public_files':len(before),'completed_sections':306,'active_section':307,'acceptance_claimed':False}))
