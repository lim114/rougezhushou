from pathlib import Path
from hashlib import sha256
import sys,subprocess,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/sections/447-presentation-card';out=B/'native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),'child'],stdout=a,stderr=b,cwd=R);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'exit':code},flush=True);raise SystemExit(code)
from unittest.mock import patch
from rouge import player_statistics_card_acceptance as module
from player_ui_verification import run
original=module.check_presentation
def check(window,gui,require):
 original(window,gui,require);rows=[]
 for name,pixmap in window.player_card447_images.items():
  target=out/(name+'.png');assert pixmap.save(str(target));rows.append({'file':target.relative_to(R).as_posix(),'sha256':sha256(target.read_bytes()).hexdigest()})
 (out/'extra-images.json').write_text(json.dumps(rows,indent=2)+'\n','utf8');(out/'actual-sizes.json').write_text(json.dumps(window.player_card447_sizes,indent=2)+'\n','utf8')
with patch.object(module,'check_presentation',check):code=run(447,out/'window.json')
raise SystemExit(code)
