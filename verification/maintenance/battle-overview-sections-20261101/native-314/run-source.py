from pathlib import Path
import sys,json,subprocess
R=Path.cwd();out=R/'verification/maintenance/battle-overview-sections-20261101/native-314';out.mkdir(exist_ok=False)
with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8','scripts/verify_current_battle_window_314.py','--receipt',str(out/'window.json')],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
(out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code,'original_60000ms_guard_preserved':True},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code,'failure':json.loads((out/'window.json').read_bytes())['failure']if(out/'window.json').exists()else'missing receipt'},flush=True);raise SystemExit(code)
