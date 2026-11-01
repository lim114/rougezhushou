from pathlib import Path
from hashlib import sha256
import sys,json,subprocess,cProfile,pstats
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/sections/460-notebook/run-profile'
if len(sys.argv)==1:
 B.mkdir(exist_ok=False)
 with(B/'stdout.txt').open('xb')as a,(B/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (B/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(B/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
import cv2
from rouge.recognition import ScreenReader
sources={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in(R/'rouge').rglob('*.py')};(B/'source-before.json').write_text(json.dumps(sources,indent=2)+'\n','utf8')
video=next(R.glob('*.mp4'));digest=sha256(video.read_bytes()).hexdigest();assert digest=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda'
cap=cv2.VideoCapture(str(video));reader=ScreenReader();results=[]
def frame(second):
 cap.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,image=cap.read();assert ok;return image
reader.read(frame(52))
for second in [60,95]:
 image=frame(second);profile=cProfile.Profile();profile.enable();observation=reader.read(image);profile.disable();stats=pstats.Stats(profile);rows=[]
 for (filename,line,name),(primitive,total,self_s,cumulative,callers)in stats.stats.items():
  path=Path(filename)
  if not path.is_absolute()or not path.is_relative_to(R/'rouge'):continue
  rows.append({'file':path.relative_to(R).as_posix(),'line':line,'function':name,'primitive_calls':primitive,'total_calls':total,'self_ms':self_s*1000,'cumulative_ms':cumulative*1000})
 rows.sort(key=lambda row:row['cumulative_ms'],reverse=True)
 results.append({'second':second,'shape':list(image.shape),'page':observation['page'],'performance':observation['performance'],'top_project_functions':rows[:45]})
cap.release();assert all(sha256((R/n).read_bytes()).hexdigest()==h for n,h in sources.items())
result={'passed':True,'video_sha256':digest,'warmup_second':52,'profiled_seconds':[60,95],'rows':results,'recognized_texts_saved':False,'recognition_sources_unchanged':True,'scope':'Read-only offline reference-video composites. cProfile diagnostic includes instrumentation overhead; use it to locate work, not quote gameplay latency.','speedup_claimed':False}
(B/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':True,'top_functions':[[r['second'],[(x['function'],round(x['cumulative_ms'],1))for x in r['top_project_functions'][:12]]]for r in results]}))
