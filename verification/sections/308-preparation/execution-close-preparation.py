from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(p):return sha256(p.read_bytes()).hexdigest()
p=ROOT/'verification/sections/308-window-attempt1/actual/window.json';w=json.loads(p.read_bytes());assert w['passed']and w['unique_checks']==57 and len(w['screenshots'])==5
images=[]
for r in w['screenshots']:
 p=Path(r['path']);assert p.is_relative_to(ROOT)and sha(p)==r['sha256']
 images.append({'file':p.relative_to(ROOT).as_posix(),'sha256':r['sha256'],'root_viewed':True,'review':'Root viewed full actual PNG at high detail. Four exact stage variants show readable manual-cell and mapped-original selection; fifth shows the unknown logical cell and no corresponding original marker. No whole-map calibration claim.'})
(ROOT/'verification/sections/308-root-visual.json').write_bytes(enc({'section':308,'all_reviewed':True,'images':images,'native_receipt':'verification/sections/308-window-attempt1/actual/window.json'}))
s=(ROOT/'.cache/open_test_window_307.py').read_text('utf8').replace('307','308')
s=s.replace("old=load('verification/sections/306-main-window.json')","old=load('verification/sections/307-main-window.json')").replace('308-window-attempt2','308-window-attempt1').replace("necessary['methods_ran']==87","necessary['methods_ran']==99")
(ROOT/'.cache/open_test_window_308.py').write_text(s,encoding='utf8')
(ROOT/'verification/sections/308-preparation/current-legacy-source-contract-observation.json').write_bytes(enc({'section':308,'kind':'actual_exec_command_observation_not_native_pass','observed_actual_exit':0,'scripts':['scripts/verify_direct_map_window_303_full308.py','scripts/verify_direct_map_window_294_full308.py'],'source_contracts_executed_without_Qt':True,'source_contract_functions_returned_without_error':True,'old_stage_counts':[3,4],'original_main_AST_unchanged_per_review':True,'original_stage_and_size_and_assertion_scope_preserved':True,'native_windows_executed_for_these_variants':False,'scheduled_for_next_full_scope':320,'original_native_sources_preserved':True,'selected_source_sha256':{n:sha(ROOT/n)for n in('scripts/verify_direct_map_window_303_full308.py','scripts/verify_direct_map_window_294_full308.py','scripts/verify_direct_map_window_303.py','scripts/verify_direct_map_window_294_full305.py','rouge/data/fixed-landmark-references.json')},'raw_process_retention_claimed':False}))
(ROOT/'verification/sections/308-preparation/execution-close-preparation.py').write_bytes(Path(__file__).read_bytes())
