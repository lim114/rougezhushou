from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys
root=Path(__file__).resolve().parents[1]
runtime=root/'.cache/p3-full305-attempt2-prep-revision2'
process=json.loads((runtime/'root-launch-attempt2/controller-process.json').read_bytes())
assert process['status']=='completed'and process['actual_observed_exit']==0 and process['source_guard_exception_after']is None
assert(runtime/'root-launch-attempt2/process.exit').read_text('ascii').strip()=='0'
dest=root/'verification/full-305/second-archive-invocation';assert not dest.exists();dest.mkdir()
argv=[sys.executable,'-B','-X','utf8',str(runtime/'archive_full305.py'),'--archive','--container',r'C:\Users\李娜\AppData\Local\Temp\rouge-full305-attempt2-08fc1d008e904924b0d6f19436e61f2f','--attempt-name','execution-attempt2','--expected-parent-commit','89606d703dc121d26f869723e1bb7d1d356a913e','--freeze-sha256','4e2528deb25cbb166b74d74db8e0c3a6212ec6095a6d7b441bf62a911ade8086','--activation-sha256','8623ee7ab99e9a198169e289f84c7db22266b60eb1bed2fba74422a57d430fda']
started=datetime.now(timezone.utc).isoformat()
with(dest/'stdout.log').open('xb')as out,(dest/'stderr.log').open('xb')as err:
 p=subprocess.Popen(argv,cwd=root,stdin=subprocess.DEVNULL,stdout=out,stderr=err);code=p.wait()
value={'section':305,'actual_validation_attempt':2,'kind':'root_explicit_second_strict_archive_actual_execution','argv':argv,'pid':p.pid,'owned_popen_retained':True,'actual_exit':code,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'original_controller_actual_exit':process['actual_observed_exit'],'archive_script_sha256':sha256((runtime/'archive_full305.py').read_bytes()).hexdigest()}
manifest=root/'verification/full-305/execution-attempt2/archive-manifest.json'
if manifest.is_file():value['archive_manifest_sha256']=sha256(manifest.read_bytes()).hexdigest()
(dest/'process.json').write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8'));(dest/'process.exit').write_text(str(code)+'\n',encoding='ascii');(dest/'executed-root-archive.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(value,ensure_ascii=False));print((dest/'stdout.log').read_text('utf8',errors='replace'));print((dest/'stderr.log').read_text('utf8',errors='replace'))
raise SystemExit(code)
