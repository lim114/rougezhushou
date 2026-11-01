from pathlib import Path
import subprocess,sys,json
R=Path.cwd();B=R/'verification/maintenance/enemy-table-reading-20261101';out=B/'related-final';out.mkdir(exist_ok=False)
s=(B/'related/bootstrap.py').read_text('utf8').replace('enemy-table-reading-20261101/related','enemy-table-reading-20261101/related-final');(out/'bootstrap.py').write_text(s,'utf8')
from hashlib import sha256
sources={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in(R/'rouge').rglob('*')if p.suffix in('.py','.cjs')}
(out/'source-before.json').write_text(json.dumps(sources,indent=2)+'\n','utf8')
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(out/'bootstrap.py')],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
assert sources=={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in(R/'rouge').rglob('*')if p.suffix in('.py','.cjs')}
(out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code,'all_application_sources_unchanged':True},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'exit':code,'result':json.loads((out/'results.json').read_bytes())if(out/'results.json').exists()else None,'failure':(out/'stderr.txt').read_text('utf8')[-3000:]if code else None},ensure_ascii=False));raise SystemExit(code)
