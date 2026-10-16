from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.cache/promote_section_301.py'
before=source.read_bytes()
old=b"for name,pin in view['promotion_allowlist'].items():add(name,pin['candidate'],pin['sha256'])"
new=b"for name,pin in view['promote_files'].items():add(name,Path(view['candidate_root'])/name,pin['sha256'])"
assert before.count(old)==1
target=ROOT/'.cache/promote_section_301_v2.py';assert not target.exists()
target.write_bytes(before.replace(old,new))
note={'section':301,'kind':'observed_exec_tool_result_summary_not_subprocess_raw',
 'first_producer_sha256':sha256(before).hexdigest(),'observed_exit':1,
 'error':'KeyError: promotion_allowlist','live_functional_files_written':0,
 'tracked_changed_files_after':['DEVELOPMENT_CHECKPOINT.json','WORK_IN_PROGRESS.md'],
 'fix':'Read frozen301 view promote_files and candidate_root schema; original producer retained.',
 'failed_shell_wrapper_created_no_files':True,
 'shell_wrapper_error':'PowerShell ParserError before Python started; dependent v2 invocation then found no file.',
 'game_private_tests_or_native_operations_in_these_preparation_errors':False}
path=ROOT/'verification/sections/301-preparation/promotion-preparation-first-error.json'
with path.open('x',encoding='utf8') as stream:stream.write(json.dumps(note,ensure_ascii=False,indent=2)+'\n')
print('Prepared schema-corrected producer; no functional files written by this preparation.')
