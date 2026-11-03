from pathlib import Path
import sys,json,subprocess,time
from hashlib import sha256
R=Path.cwd();sys.path.insert(0,str(R));out=R/'verification/maintenance/mechanism-focus-20261101/hud-trial'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');print({'actual_exit':code});raise SystemExit(code)
from unittest.mock import patch
import cv2
from rapidocr_onnxruntime import RapidOCR
from rouge.recognition import ScreenReader
from rouge.recognition_cache import CachedOCR
from rouge import hud_resources as hud
video=next(R.glob('*.mp4'));assert sha256(video.read_bytes()).hexdigest()=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda';cap=cv2.VideoCapture(str(video));rows=[];current_second=None
alternate=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2,det_limit_type='max');assert alternate.text_det.limit_type=='max';original=hud._number
def compare(image,texts,box,engine,**kw):
 provider=engine.engine if type(engine)is CachedOCR else engine;observed={};times={'min':[],'max':[]}
 for repeat in range(3):
  for name in(('min','max')if repeat%2==0 else('max','min')):
   started=time.perf_counter();value=original(image,texts,box,provider if name=='min'else alternate,**kw);times[name].append((time.perf_counter()-started)*1000)
   if name in observed:assert observed[name]==value,'Within-provider result changed'
   observed[name]=value
 row={'public_second':current_second,'ratio':kw.get('ratio',False),'segmented':kw.get('segmented',False),'image_size':[image.shape[1],image.shape[0]],'same_numeric_observation':observed['min']==observed['max'],'baseline_observed':observed['min']is not None,'candidate_observed':observed['max']is not None,'milliseconds':times};rows.append(row);(out/'progress.json').write_text(json.dumps({'rows':rows},indent=2)+'\n','utf8');return observed['min']
with patch.object(hud,'_number',compare):
 for current_second in(44,60):
  cap.set(cv2.CAP_PROP_POS_MSEC,current_second*1000);ok,image=cap.read();assert ok;ScreenReader().read(image)
cap.release();value={'source':'Installed RapidOCR1.4.4 official det_limit_type min/max setting; unchanged models/threads. Isolated candidate only.','rows':rows,'all_paired_numeric_observations_equal':all(r['same_numeric_observation']for r in rows),'raw_text_numbers_pixels_or_private_state_persisted':False,'production_provider_configuration_changed':False,'coverage_not_complete_or_independent_accuracy':True};(out/'results.json').write_text(json.dumps(value,indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(value))
