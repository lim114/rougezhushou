from pathlib import Path
import subprocess,sys,json
R=Path.cwd();out=R/'verification/sections/459-viewport'
with(out/'ocr-profile-quiet-stdout.txt').open('xb')as stdout,(out/'ocr-profile-quiet-stderr.txt').open('xb')as stderr:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/profile_viewport459_ocr_quiet.py')],cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
(out/'ocr-profile-quiet-process.json').write_text(json.dumps({'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
print((out/'ocr-profile-quiet-stdout.txt').read_text('utf8')[-4000:]);print((out/'ocr-profile-quiet-stderr.txt').read_text('utf8')[-1500:]);raise SystemExit(code)
