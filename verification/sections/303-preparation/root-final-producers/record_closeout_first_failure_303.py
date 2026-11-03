from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'verification/sections/303-preparation/closeout-first-preview'
base.mkdir(parents=True,exist_ok=True)
source='.cache/p3-303-closeout/close_section_303.py';raw=(ROOT/source).read_bytes()
assert sha256(raw).hexdigest()=='6f17bd56a601b333165b2f739fe200b3966140e0f7f1c1f093afeaf5b92fa547'
old=(ROOT/'verification/sections/303-preparation/historical-tests/before/tests/test_map_projection_048.py').read_bytes()
new=(ROOT/'tests/test_map_projection_048.py').read_bytes()
def funcs(raw):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.FunctionDef)}
before,after=funcs(old),funcs(new)
changed=[n for n in before if before[n]!=after.get(n)]
tests=[n for n in before if n.startswith('test_')]
assert len(before)==len(after)==9 and len(tests)==8 and changed==['test_unaccepted_wood_decorations_and_portal_probes_are_retained']
inventory={'all_function_names':list(before),'all_functions':9,'changed_function_names':changed,'unchanged_functions_including_load_helper':8,
 'test_method_names':tests,'test_method_count':8,'unchanged_other_test_methods':7,'standalone_load_helper_unchanged':before['load']==after['load'],
 'original_test_sha256':sha256(old).hexdigest(),'current_test_sha256':sha256(new).hexdigest()}
(base/'actual-historical048-function-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf8')
changes=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
assert set(changes)=={'DEVELOPMENT_CHECKPOINT.json','rouge/data/fixed-landmark-references.json','tests/test_direct_landmark_294.py','tests/test_map_projection_048.py'}
record={'section':303,'kind':'actual_closeout_preview_tool_output_summary_not_raw_subprocess_log','at_utc':datetime.now(timezone.utc).isoformat(),
 'actual_exit_code':1,'source':source,'source_sha256':sha256(raw).hexdigest(),
 'actual_error':'ValueError: 303 closeout prerequisite: only one historical048 method changes; other8 ASTs unchanged',
 'error_site':'historical_maintenance, original line208: functions filtered to tests_only but expected all-functions count9',
 'actual_inventory':inventory,'no_apply_or_publication_occurred':True,'tracked_changes_after_failed_preview':changes,
 'business_necessary_and_native_passes_unchanged':True,'raw_stdout_or_stderr_log_claimed':False}
target=base/'first-tool-output-summary.json';assert not target.exists();target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'original_tool_preserved':True,'actual_all_functions':9,'actual_test_methods':8,'unchanged_test_methods':7,'changed_test_methods':1,'business_source_or_receipts_modified':False}))
