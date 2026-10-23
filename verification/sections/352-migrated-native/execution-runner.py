from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys,os
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from scripts.verify_common_content_window_352 import bound_files
out=R/'verification/sections/352-migrated-native';out.mkdir()
before=bound_files();cases=[(313,'expansion'),(316,'ending_events'),(317,'current_stage_directory'),(349,'current_critical_reward_origins'),(350,'current_startup'),(351,'current_enemy_traits')];rows=[]
for section,name in cases:
 dest=out/str(section);dest.mkdir();script=f'scripts/verify_{name}_window_{section}.py';argv=[sys.executable,'-B','-X','utf8',script,'--receipt',str(dest/'actual/window.json'),'--visible-ms','120000'];started=datetime.now(timezone.utc).isoformat()
 with(dest/'stdout.txt').open('xb')as stdout,(dest/'stderr.txt').open('xb')as stderr:
  child=subprocess.Popen(argv,cwd=R,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=dict(os.environ,QT_QPA_PLATFORM='windows',PYTHONDONTWRITEBYTECODE='1'));code=child.wait()
 receipt=dest/'actual/window.json';w=json.loads(receipt.read_bytes())if receipt.exists()else None
 row={'source_section':section,'argv':argv,'retained_popen_pid':child.pid,'actual_observed_exit':code,'started_at_utc':started,'finished_at_utc':datetime.now(timezone.utc).isoformat(),'script_sha256':sha256((R/script).read_bytes()).hexdigest(),'receipt':receipt.relative_to(R).as_posix(),'receipt_sha256':sha256(receipt.read_bytes()).hexdigest()if w else None,'passed':code==0 and w is not None and w['passed'],'failure':w['failure']if w else 'Missing native receipt','unique_checks':w['unique_checks']if w else None,'scope':'Explicit migrated representatives, not all38 or full suite.'}
 (dest/'process.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf8');rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 if not row['passed']:break
after=bound_files();report={'section':352,'passed':len(rows)==len(cases)and all(r['passed']for r in rows)and before==after,'all38_native_scripts_rerun':False,'selected_representatives':rows,'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'no_cloud_execution':True}
(out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes());raise SystemExit(0 if report['passed']else 1)
