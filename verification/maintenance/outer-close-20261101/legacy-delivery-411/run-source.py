from pathlib import Path
import sys,subprocess,json
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];B=R/'verification/maintenance/outer-close-20261101'
if len(sys.argv)>1:
 from player_ui_verification import run
 from rouge import player_acceptance
 from hashlib import sha256
 original=player_acceptance.check
 def check(section,window,gui,require):
  original(section,window,gui,require)
  if section==447:
   images=[];out=B/('legacy-delivery-'+str(section))
   for name,pixmap in window.player_card447_images.items():
    path=out/(name+'.png');require(pixmap.save(str(path)),'outer_card_image_'+name);images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
   (out/'extra-images.json').write_text(json.dumps(images,indent=2)+'\n','utf8')
 player_acceptance.check=check
 n=int(sys.argv[1]);raise SystemExit(run(n,B/('legacy-delivery-'+str(n))/'window.json'))
for n in(411,416,443,446,447):
 out=B/('legacy-delivery-'+str(n));out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),str(n)],cwd=R,stdout=a,stderr=b);print({'scope':n,'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes())
 value=json.loads((out/'window.json').read_bytes());print({'scope':n,'actual_exit':code,'checks':value['unique_checks'],'failure':value['failure']},flush=True)
 if code:raise SystemExit(code)
