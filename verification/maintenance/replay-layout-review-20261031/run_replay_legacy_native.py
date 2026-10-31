from pathlib import Path
import subprocess,sys,json
base=Path('verification/maintenance/replay-layout-review-20261031/legacy-native');base.mkdir(exist_ok=False)
for section in (401,402,403):
 out=base/str(section);out.mkdir()
 source="import sys;sys.path.insert(0,'scripts');from player_ui_verification import run;raise SystemExit(run("+str(section)+","+repr(str(out/'receipt.json'))+"))"
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8','-c',source],stdout=a,stderr=b);code=p.wait()
 (out/'process.json').write_text(json.dumps({'pid':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
 print((out/'stdout.txt').read_text('utf8')[-1300:],flush=True)
 if code:raise SystemExit(code)
