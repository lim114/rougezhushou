from pathlib import Path
import subprocess,sys,json
R=Path.cwd();out=R/'verification/maintenance/grade16-review-20261031';out.mkdir(parents=True,exist_ok=True)
with(out/'native-final-stdout.txt').open('xb')as stdout,(out/'native-final-stderr.txt').open('xb')as stderr:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/verify_grade16_native_final.py')],cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
(out/'native-final-process.json').write_text(json.dumps({'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
print((out/'native-final-stdout.txt').read_text('utf8')[-1500:]);print((out/'native-final-stderr.txt').read_text('utf8')[-2200:]);raise SystemExit(code)
