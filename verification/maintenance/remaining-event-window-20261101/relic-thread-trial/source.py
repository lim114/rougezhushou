from pathlib import Path
from hashlib import sha256
import sys,json,time,subprocess
R=Path.cwd();sys.path.insert(0,str(R));out=R/'verification/maintenance/remaining-event-window-20261101/relic-thread-trial'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());raise SystemExit(code)
import cv2
from unittest.mock import patch
from rouge.recognition import ScreenReader
from rouge import relic_recognition as relic
original=relic._match_bar;threads=cv2.getNumThreads();rows=[];inputs=[];second=0
def compare(*args):
 baseline=original(*args);values=[]
 try:
  for repeat in range(3):
   for count in((threads,1)if repeat%2==0 else(1,threads)):
    cv2.setNumThreads(count);start=time.perf_counter();value=original(*args);duration=(time.perf_counter()-start)*1000
    values.append({'repeat':repeat,'opencv_threads':count,'milliseconds':duration,'exact_original_output':value==baseline,'matches':len(value),'output_sha256':sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()})
 finally:cv2.setNumThreads(threads)
 rows.append({'public_second':second,'roi_shape':list(args[0].shape),'runs':values});print({'finished_public_target':second,'runs':len(values)},flush=True);return baseline
video=next(R.glob('*.mp4'));assert sha256(video.read_bytes()).hexdigest()=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda';cap=cv2.VideoCapture(str(video))
with patch.object(relic,'_match_bar',compare):
 for second in(44,60):
  cap.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,image=cap.read();assert ok;inputs.append({'public_second':second,'frame_position_after_read':cap.get(cv2.CAP_PROP_POS_FRAMES),'frame_sha256':sha256(image.tobytes()).hexdigest()});ScreenReader().read(image)
cap.release();assert cv2.getNumThreads()==threads
value={'opencv_version':cv2.__version__,'original_threads':threads,'rows':rows,'inputs':inputs,'thread_count_restored':True,'production_runtime_settings_changed':False,'game_bound_or_private_input_read':False,'claim':'Whole current held-bar matching only on two public composite targets; repeated outputs are baseline parity,not independent truth or complete end-to-end speedup.'};(out/'results.json').write_text(json.dumps(value,indent=2)+'\n','utf8')
