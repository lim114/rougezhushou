"""Explicit source declaration plus selected repairs after complete3 and its audit."""
from pathlib import Path
from hashlib import sha256
import json,re,runpy,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'.cache/full425-prepared/attempt-4';assert sys.argv[1:]==['--execute']
assert not(B/'root-launch').exists()and not(B/'full425-once.json').exists()and not(R/'verification/full-425/source-freeze-attempt4.json').exists()
assert not(R/'.cache/425-selected-repair4-once.json').exists()
base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'));assert base['read']('DEVELOPMENT_CHECKPOINT.json')['completed_sections']==424
audit=base['read']('verification/full-425/baseline3-readonly-audit.json');audit_process=base['read']('verification/full-425/baseline3-readonly-audit-process/process.json')
assert audit['passed']and not audit['baseline_full_suite_passed']and audit_process['passed']and audit_process['actual_observed_exit']==0
assert base['read']('verification/full-425/repair-source-baseline-attempt3/manifest.json')['original_failed_source_preserved']
spec=base['read']('.cache/spec425.json');source=base['source']()
for key in ['unit_receipt','native_receipt','native_process_receipt']:
 row=base['read'](spec[key]);assert row['passed']and row['source_sha256_before']==row['source_sha256_after']==source
for path in ['verification/sections/425-overlay-input-probe-attempt2/receipt.json','verification/sections/425-overlay-input-probe-process-attempt2/process.json']:
 row=base['read'](path);assert row['passed']and row['source_sha256_before']==row['source_sha256_after']==source
assert runpy.run_path(str(B/'full425_common.py'))['tool_pins']()['fresh_attempt']==4
parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert parent=='523009cce1065289bb84acf18315d37abd9998cc'
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip()=='codex/p2-development'
def save(path,data):
 assert not path.exists();path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
unit=base['read'](spec['unit_receipt']);count=int(re.search(r'Ran (\d+) tests?',(R/spec['unit_receipt']).with_name('stderr.txt').read_text('utf8'))[1])
necessary={**unit,'section':425,'kind':'functional425_actual_unittest_process_with_count','methods_ran':count,'underlying_process_receipt':base['pin'](spec['unit_receipt']),'original_receipt_not_rewritten':True,'qt_exec_exit_invented':False}
necessary_path=R/'verification/sections/425-functional-necessary-repair4-final.json';save(necessary_path,necessary)
input_path=R/'verification/sections/425-full-input-repair4-final.json';save(input_path,{'section':425,'kind':'source_declaration_for_selected_repairs_not_whole_full4','references':{'necessary':necessary_path.relative_to(R).as_posix(),'native':spec['native_receipt'],'native_process':spec['native_process_receipt']}})
python=str(R/'.venv/Scripts/python.exe')
subprocess.run([python,'-B','-X','utf8',str(B/'declare_current425.py'),'--source-finalized','--expected-parent-commit',parent,'--functional-receipts',str(input_path)],cwd=R,check=True)
freeze=R/'verification/full-425/source-freeze-attempt4.json';freeze_sha=sha256(freeze.read_bytes()).hexdigest()
subprocess.run([python,'-B','-X','utf8',str(B/'activate_full425.py'),'--activate','--expected-parent-commit',parent,'--freeze-sha256',freeze_sha],cwd=R,check=True)
activation_sha=sha256((B/'activation425.json').read_bytes()).hexdigest();save(R/'.cache/425-selected-repair4-launch-input.json',{'parent':parent,'freeze_sha256':freeze_sha,'activation_sha256':activation_sha,'whole_full4_execution_claimed':False})
folder=R/'verification/full-425/selected-repair4-tools';assert not folder.exists();folder.mkdir();files=[]
for path in [Path(__file__),R/'.cache/run425_selected_repairs.py',R/'.cache/repair425_unit_child.py']:
 raw=path.read_bytes();copy=folder/path.name;copy.write_bytes(raw);files.append({'source':path.relative_to(R).as_posix(),'preserved':copy.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)})
save(folder/'manifest.json',{'section':425,'scope':'Only explicit selected-repair tools. Complete original full3 and failures remain separate.','files':files})
base['execute']([python,'-B','-X','utf8',str(R/'.cache/run425_selected_repairs.py'),'--execute','--expected-parent-commit',parent,'--freeze-sha256',freeze_sha,'--activation-sha256',activation_sha],'verification/full-425/selected-repair4-process')
print('Selected repairs observed terminal; no complete-scope success claimed before audit and actual visual review.')
