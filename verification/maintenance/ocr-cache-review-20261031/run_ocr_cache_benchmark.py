from pathlib import Path
import subprocess,sys,json
R=Path.cwd();out=R/'verification/maintenance/ocr-cache-review-20261031';out.mkdir(parents=True,exist_ok=True)
with(out/'benchmark-stdout.txt').open('xb')as stdout,(out/'benchmark-stderr.txt').open('xb')as stderr:
 child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/benchmark_ocr_cache_review.py')],cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
(out/'benchmark-process.json').write_text(json.dumps({'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
print((out/'benchmark-stdout.txt').read_text('utf8'));print((out/'benchmark-stderr.txt').read_text('utf8')[-2400:]);raise SystemExit(code)
