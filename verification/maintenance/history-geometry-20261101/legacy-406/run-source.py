from pathlib import Path
import sys,subprocess,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/history-geometry-20261101'
if len(sys.argv)>1:
 from player_ui_verification import run
 n=int(sys.argv[1]);raise SystemExit(run(n,B/('legacy-'+str(n))/'window.json'))
for n in(406,408,432):
 out=B/('legacy-'+str(n));out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),str(n)],cwd=R,stdout=a,stderr=b);print({'scope':n,'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes())
 value=json.loads((out/'window.json').read_bytes());print({'scope':n,'actual_exit':code,'checks':value['unique_checks'],'failure':value['failure']},flush=True)
 if code:raise SystemExit(code)
