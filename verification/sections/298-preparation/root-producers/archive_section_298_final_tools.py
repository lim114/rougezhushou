from pathlib import Path
from hashlib import sha256
import json,shutil
ROOT=Path(__file__).resolve().parents[1];PREP=ROOT/'verification/sections/298-preparation'
row={'section':298,'kind':'actual_preflight_coordination_errors_not_product_or_test_failures',
 'recorded_from':'actual tool outputs before any formal298 necessary tests were launched',
 'events':[{'action':'freeze_section_298_runtime.py first invocation','result':'AssertionError on old READY SHA5fcc4c; helper author had concurrently published the explicitly requested historical-test maintenance revision with SHA67103d.',
            'production_or_runtime_test_promotion_performed':False,'Qt_or_tests_started':False},
           {'action':'necessary producer preflight after unsuccessful freeze','result':'FileNotFoundError canonical scripts/verify_event_node_requirements_window_298.py before destination creation or unittest launch.',
            'receipt_directory_created':False,'Qt_or_tests_started':False}],
 'resolution':'Fresh READY67103 and unchanged native/view/runner bytes were verified and frozen sequentially. Later cache closeout revisions use separate paths; original READY is unchanged.',
 'full_stdout_stderr_separately_captured':False,'original_tool_output_retained':True,'not_counted_as_product_tests':True}
(PREP/'root-coordination-preflight.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode())
names=['.cache/freeze_section_298_runtime.py','.cache/migrate_section_298_union_assertion.py','.cache/prepare_section_298_main_visual.py',
 '.cache/restart_window_298.py','.cache/focus_window_298.py','.cache/archive_section_298_final_tools.py',
 '.cache/p3-298-runtime-preparation/run_section_298_necessary.py']
manifest={}
for name in names:
 p=ROOT/name;dest=PREP/'root-producers'/p.name
 assert not dest.exists();shutil.copyfile(p,dest);manifest[p.name]={'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
for relative in ['READY.json','preparation-check.json','CONTRACT.md','RUN_PLAN.md','common-provenance.json',
 'before-historical-test-maintenance/READY.json','before-historical-test-maintenance/close_section_298.py',
 'closeout-v3/REVISED_READY.json','closeout-v3/close_section_298.py','closeout-v4/REVISED_READY.json','closeout-v4/CONTRACT.md']:
 p=ROOT/'.cache/p3-298-runtime-preparation'/relative
 assert p.is_file(),relative
 dest=PREP/'runtime-preparation'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
(PREP/'root-producers/final-tools-manifest.json').write_bytes((json.dumps({'section':298,'files':manifest,'private_files_or_hash_lists_copied':False},ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'final_root_tools':len(manifest),'actual_closeout_and_runtime_preparation_archived':True}))
