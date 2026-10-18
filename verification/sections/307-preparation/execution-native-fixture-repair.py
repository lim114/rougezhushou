from pathlib import Path
from hashlib import sha256
import json
root=Path(__file__).resolve().parents[1]
name='scripts/verify_choice_annotations_window_307.py'
p=root/name
raw=p.read_bytes()
before=root/'verification/sections/307-preparation/before'/name
before.parent.mkdir(parents=True,exist_ok=True)
before.write_bytes(raw)
s=raw.decode('utf8')
old="('community_group_023','choice_ro6_surprise_1','scene_ro6_surprise_1','后续奖励分支说明（原文）：随机出现以下3种奖励中的1种')"
new="('community_group_023','choice_ro6_surprise_2','scene_ro6_surprise_5','后续奖励分支说明（原文）：随机出现以下2种奖励中的1种')"
assert s.count(old)==1
s=s.replace(old,new)
needle="                        destinations.append({'original_choice_id':original"
assert s.count(needle)==1
s=s.replace(needle,"                        if eid=='community_group_023':\n                            require([r['scene_key']for r in win.result['catalog_references']]==[eid+':scene:6',eid+':scene:9',eid+':scene:11'] and '数量不一致'in win.detail.toPlainText(),'original_destination_retains_all_three_documentary_candidates_and_conflicts')\n"+needle)
p.write_text(s,encoding='utf8')
runner=(root/'.cache/run307_native.py').read_text('utf8').replace('307-window-attempt1','307-window-attempt2')
(root/'.cache/run307_native2.py').write_text(runner,encoding='utf8')
record={'section':307,'repair_kind':'native_fixture_wrong_original_choice_mapping','first_attempt':'verification/sections/307-window-attempt1/process.json','original_script_sha256':sha256(raw).hexdigest(),'production_changed':False,'old_assumption':'choice_ro6_surprise_1 belongs to default original destination dropdown for community_group_023','evidence':'event_destination_choices lists surprise_2/8/3/4/7/10, not surprise_1; fixed original surprise_2 nextSceneId is surprise_5 and matches all catalog scenes6/9/11','correction':'use actual available mapped original choice, retain all three source candidates and quantity conflict; no source mapping or production menu altered'}
(root/'verification/sections/307-preparation/native-fixture-repair.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
