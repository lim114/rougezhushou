from pathlib import Path
import sys,json,subprocess,time,re
from hashlib import sha256
R=Path.cwd();sys.path.insert(0,str(R));out=R/'verification/maintenance/compact-battle-window-20261101/number-line-trial'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');print({'actual_exit':code});raise SystemExit(code)
import cv2,numpy as np
from unittest.mock import patch
from rouge.recognition import ScreenReader
from rouge import hud_resources as hud
from rouge.anchors import crop
from rouge.operator_recognition import center
video=next(R.glob('*.mp4'));assert sha256(video.read_bytes()).hexdigest()=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda';cap=cv2.VideoCapture(str(video));original=hud._number;rows=[];inputs=[];second=0
def compare(image,texts,box,engine,**kw):
 pattern=r'(\d+)/(\d+)'if kw.get('ratio')else r'\d+';local=[t for t in texts if box[0]<=center(t)[0]<=box[2]and box[1]<=center(t)[1]<=box[3]and re.fullmatch(pattern,t['text'])];strong=[t for t in local if t['confidence']>=.9];weak=[t for t in local if .7<=t['confidence']<.9];reading=None;elapsed=None;agrees=None
 if not kw.get('segmented')and not strong and len(weak)==1:
  record=weak[0];xs=[p[0]for p in record['box']];ys=[p[1]for p in record['box']];current=crop(image,(min(xs),min(ys),max(xs),max(ys)));current=cv2.copyMakeBorder(current,5,5,5,5,cv2.BORDER_CONSTANT,value=0);started=time.perf_counter();raw,_=engine(cv2.resize(current,None,fx=2,fy=2),use_cls=False,use_det=False);elapsed=(time.perf_counter()-started)*1000
  if len(raw or[])==1 and raw[0][-1]>=.95 and raw[0][-2].replace(' ','')==record['text']:
   v=raw[0][-2].replace(' ','')
   if kw.get('ratio'):
    amount,capacity=map(int,v.split('/'));reading={'value':amount,'capacity':capacity}if amount<=capacity else None
   else:reading={'value':int(v)}
 started=time.perf_counter();baseline=original(image,texts,box,engine,**kw);duration=(time.perf_counter()-started)*1000
 rows.append({'public_second':second,'ratio':kw.get('ratio',False),'segmented':kw.get('segmented',False),'strong_current_numeric_lines':len(strong),'weak_current_numeric_lines':len(weak),'eligible_for_current_line_REConly':elapsed is not None,'candidate_available':reading is not None,'baseline_available':baseline is not None,'same_numeric_observation':reading==baseline if elapsed is not None else None,'candidate_ms':elapsed,'baseline_ms':duration});return baseline
with patch.object(hud,'_number',compare):
 for second in(44,60):
  cap.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,image=cap.read();assert ok;inputs.append({'target_second':second,'actual_frame_position_after_read':cap.get(cv2.CAP_PROP_POS_FRAMES),'public_frame_sha256':sha256(image.tobytes()).hexdigest()});ScreenReader().read(image)
cap.release();value={'candidate':'Official existing RapidOCR use_det=False on one current weak numeric detection,exact text agreement at.95,otherwise no alternate observation. Exploratory only; caller always returns old function result.','inputs':inputs,'rows':rows,'production_reader_changed':False,'raw_text_numbers_pixels_or_private_state_saved':False};(out/'results.json').write_text(json.dumps(value,indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(value))
