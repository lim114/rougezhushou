from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[1]
def load(n):return json.loads((ROOT/n).read_bytes())
def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';before=cp_path.read_bytes();cp=json.loads(before)
assert cp['completed_sections']==304 and cp['policy']['wrap_up_below_usage_percent']==15
suggest=load('.cache/p3-305-full-failure-triage/closeout-review/restored15-20261018/PATCH_SUGGESTIONS.json')
for edit in suggest['checkpoint_edits']:
 key=edit['path'].split('.',1)[1]
 if 'observed_old' in edit:assert cp['policy'][key]==edit['observed_old']
 cp['policy'][key]=edit['suggested_new']
cp_path.write_bytes(encode(cp))
validator=ROOT/'.cache/p3-305-closeout/validate_and_propose_305_current_policy.py'
text=validator.read_text('utf8')
old=" need(cp['last_verified_cloud_save']['section']==304,'Previous publication must be actual304')"
assert text.count(old)==1
new=""" latest_instruction_name=cp['policy']['latest_usage_and_pause_instruction_receipt']
 latest_instruction=read(latest_instruction_name)
 need(latest_instruction['current_threshold_percent']==15 and latest_instruction['strictly_below']is True
  and latest_instruction['pause_after_section']==305 and latest_instruction['new306_started']is False,'Restored15 and explicit pause305 instruction required')
"""+old
text=text.replace(old,new).replace("'Verified below5 trigger missing'","'Historical below5 trigger missing; this does not infer current usage'")
text=text.replace("inputs=[NECESSARY,WINDOW,PROCESS,PNG,DATA,args.full_summary", "inputs=[latest_instruction_name,NECESSARY,WINDOW,PROCESS,PNG,DATA,args.full_summary")
text=text.replace('usage4 trigger, ordinary publication still pending','historical usage4 trigger plus restored15 and explicit user pause after305, ordinary publication still pending')
text=text.replace('preserve all highest requirements and usage5 full-section rule','preserve all highest requirements and restored15 full-section rule with explicit pause after305')
validator.write_text(text,encoding='utf8')
out=ROOT/'verification/sections/305-closeout-policy';out.mkdir()
(out/'execution-policy.py').write_bytes(Path(__file__).read_bytes())
(out/'execution-proposal-validator.py').write_bytes(validator.read_bytes())
(out/'execution-main-window.py').write_bytes((ROOT/'.cache/open_test_window_305.py').read_bytes())
record={'section':305,'at_utc':datetime.now(timezone.utc).isoformat(),'kind':'CURRENT_POLICY_METADATA_ONLY','CP_before_sha256':sha256(before).hexdigest(),'CP_after_sha256':sha256(cp_path.read_bytes()).hexdigest(),'historical_trigger_preserved':True,'current_threshold_percent':15,'pause_after_section':305,'new306_started':False,'business_or_private_files_changed':False,'actual_main_window_start_failed_attempt':{'observed_via':'Windows-mcp PowerShell tool result','actual_status_code':1,'reason':'ModuleNotFoundError: No module named psutil before any window/state action','repair':'psutil7.2.2 installed only in .cache/305-window-tooldeps; original app dependencies unchanged','successful_followup':'verification/sections/305-main-window.json'},'desktop_snapshot_attempt':{'result':'RPC server unavailable','claimed_screenshot':False},'actual_successful_main_window_observed_status_code':0}
(out/'policy-and-tool-attempts.json').write_bytes(encode(record))
print(json.dumps({'CP_current_usage_policy':cp['policy']['usage_monitoring'],'validator_current_policy_instruction_bound':True}))
