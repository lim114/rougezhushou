from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
out=R/'verification/full-365/repair/necessary313';out.mkdir()
names=('tests/test_expansion_reference_313.py','rouge/expansion_reference.py','rouge/app.py','rouge/battle_view.py','scripts/verify_full_available.py')
def snapshot():return{name:sha256((R/name).read_bytes()).hexdigest()for name in names}
before=snapshot();start=datetime.now(timezone.utc).isoformat()
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v','tests.test_expansion_reference_313']
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=R,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='offscreen'))
 code=p.wait()
after=snapshot();log=(out/'stderr.txt').read_text('utf8',errors='replace');match=re.search(r'Ran (\d+) tests? in ([\d.]+)s',log)
record={'section':365,'kind':'maintenance_notice_boundary_necessary','actual_retained_Popen_exit':code,'actual_retained_launcher_pid':p.pid,'argv':argv,'methods_ran':int(match[1])if match else None,'source_sha256_before':before,'source_sha256_after':after,'passed':code==0 and before==after and match is not None,'full_suite_or_native_window_claimed':False,'source_guard_selected_not_all_transitive_dependencies':True,'start_UTC':start,'end_UTC':datetime.now(timezone.utc).isoformat()}
(out/'process.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(out/'process.exit').write_text(str(code)+'\n',encoding='ascii')
(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in record.items()if not k.startswith('source_sha256')},ensure_ascii=False))
if not record['passed']:print(log[-10000:])
raise SystemExit(0 if record['passed']else 1)
