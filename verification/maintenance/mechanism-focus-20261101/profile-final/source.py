from pathlib import Path
import sys,cProfile,pstats,json,subprocess
from hashlib import sha256
R=Path.cwd();sys.path.insert(0,str(R));out=R/'verification/maintenance/mechanism-focus-20261101/profile-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');print({'actual_exit':code});raise SystemExit(code)
import cv2
from rouge.recognition import ScreenReader
video=next(R.glob('*.mp4'));assert sha256(video.read_bytes()).hexdigest()=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda';cap=cv2.VideoCapture(str(video));cap.set(cv2.CAP_PROP_POS_MSEC,44000);ok,image=cap.read();cap.release();assert ok
profile=cProfile.Profile();reader=ScreenReader();profile.enable();result=reader.read(image);profile.disable();rows=[]
for (filename,line,name),(primitive,calls,own,cumulative,callers)in pstats.Stats(profile).stats.items():
 if '/rouge/'in filename.replace('\\','/'):
  rows.append({'file':Path(filename).name,'line':line,'function':name,'calls':calls,'own_s':own,'cumulative_s':cumulative})
rows.sort(key=lambda x:x['cumulative_s'],reverse=True);(out/'results.json').write_text(json.dumps({'public_video_second':44,'page':result['page'],'timing':result['performance'],'top_functions':rows[:40],'pixels_text_or_run_contents_saved':False,'cold_single_call_not_general_benchmark':True},ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(rows[:16]));(out/'source.py').write_bytes(Path(__file__).read_bytes())
