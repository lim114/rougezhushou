from pathlib import Path
import subprocess,sys,json
R=Path.cwd();out=R/'verification/maintenance/current-enemy-forecast-review-20261031'
with(out/'matrix-latest-stdout.txt').open('xb')as stdout,(out/'matrix-latest-stderr.txt').open('xb')as stderr:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/audit_current_enemy_forecasts.py')],cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
(out/'matrix-latest-process.json').write_text(json.dumps({'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
print((out/'matrix-latest-stdout.txt').read_text('utf8'));print((out/'matrix-latest-stderr.txt').read_text('utf8')[-1800:]);raise SystemExit(code)
