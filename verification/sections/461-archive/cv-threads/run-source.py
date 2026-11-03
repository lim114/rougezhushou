from pathlib import Path
from hashlib import sha256
from time import perf_counter
from unittest.mock import patch
import sys,json,subprocess
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/sections/461-archive/cv-threads'
if len(sys.argv)==1:
 B.mkdir(exist_ok=False)
 with(B/'stdout.txt').open('xb')as a,(B/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (B/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(B/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
import cv2
from rouge.recognition import ScreenReader
from rouge import relic_recognition as icons
sources={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in(R/'rouge').rglob('*.py')};(B/'source-before.json').write_text(json.dumps(sources,indent=2)+'\n','utf8')
video=next(R.glob('*.mp4'));digest=sha256(video.read_bytes()).hexdigest();assert digest=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda'
cap=cv2.VideoCapture(str(video));reader=ScreenReader();original=icons._match_bar;inputs=[];default=cv2.getNumThreads()
def capture(roi,*args):
 inputs.append((roi.copy(),args));return original(roi,*args)
for second in [60,95]:
 cap.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,frame=cap.read();assert ok
 with patch.object(icons,'_match_bar',side_effect=capture):reader.read(frame)
cap.release();assert len(inputs)==2
rows=[];baselines={}
try:
 for repeat,order in enumerate([[default,1,4],[4,1,default]]):
  for threads in order:
   cv2.setNumThreads(threads)
   for i,(roi,args)in enumerate(inputs):
    start=perf_counter();result=original(roi.copy(),*args);elapsed=(perf_counter()-start)*1000
    if i not in baselines:baselines[i]=result
    rows.append({'repeat':repeat,'cv_threads':threads,'input':i,'source_second':[60,95][i],'bar_shape':list(roi.shape),'ms':elapsed,'exact_output_equal':result==baselines[i]})
finally:cv2.setNumThreads(default)
assert all(sha256((R/n).read_bytes()).hexdigest()==h for n,h in sources.items())
result={'passed':True,'rows':rows,'original_threads':default,'restored_threads':cv2.getNumThreads(),'all_output_exact_equal':all(r['exact_output_equal']for r in rows),'video_sha256':digest,'recognition_source_unchanged':True,'scope':'Existing matcher only, two bars extracted by the actual ScreenReader from public reference-video composites; interleaved repeated thread settings in one isolated process. Not a client-page accuracy set or whole pipeline benchmark.','production_policy_changed':False,'private_data_used':False}
(B/'results.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps({'all_output_exact_equal':result['all_output_exact_equal'],'rows':rows}))
