from pathlib import Path
import subprocess,sys,json
R=Path.cwd();out=R/'verification/maintenance/player-theme-20261101/related-verified'
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(out/'bootstrap.py')],cwd=R,stdout=stdout,stderr=stderr);print(json.dumps({'actual_retained_PID':child.pid}),flush=True);code=child.wait()
(out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
print(json.dumps({'exit':code,'result':json.loads((out/'results.json').read_bytes())if(out/'results.json').exists()else None,'failure':(out/'stderr.txt').read_text('utf8')[-4500:]if code else None},ensure_ascii=False))
raise SystemExit(code)
