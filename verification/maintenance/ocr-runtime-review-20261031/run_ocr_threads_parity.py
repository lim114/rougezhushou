from pathlib import Path
import subprocess,sys,json
R=Path.cwd();out=R/'verification/maintenance/ocr-runtime-review-20261031';out.mkdir(exist_ok=True)
with(out/'raw-parity-stdout.txt').open('xb')as stdout,(out/'raw-parity-stderr.txt').open('xb')as stderr:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/verify_ocr_threads_parity.py')],cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
(out/'raw-parity-process.json').write_text(json.dumps({'retained_Popen_pid':child.pid,'actual_exit':code},indent=2)+'\n','utf8')
print((out/'raw-parity-stdout.txt').read_text('utf8'));print((out/'raw-parity-stderr.txt').read_text('utf8')[-2000:]);raise SystemExit(code)
