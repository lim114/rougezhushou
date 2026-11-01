from pathlib import Path
import sys,json,subprocess,time
from hashlib import sha256
R=Path.cwd();out=R/'verification/sections/450-event-samples/ocr-anchor-probe'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
sys.path.insert(0,str(R))
import cv2,numpy as np
from rapidocr_onnxruntime import RapidOCR
from rouge.run_recognition import near_number
engine=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2);source=R/'.cache/video414/194.png';full=cv2.imdecode(np.frombuffer(source.read_bytes(),np.uint8),1);rows=[]
for scale in (1,.75):
 image=full if scale==1 else cv2.resize(full,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA);h,w=image.shape[:2];raw,_=engine(image,use_cls=False)
 texts=[{'text':t.replace(' ',''),'confidence':float(c),'box':[[float(x)/w,float(y)/h]for x,y in box]}for box,t,c in raw or[]]
 for label,expected in [('收藏品',2),('干员',3)]:
  anchors=[t for t in texts if t['text']==label];calls=[]
  def traced(im,**kwargs):
   result=engine(im,**kwargs);calls.append({'size_wh':[im.shape[1],im.shape[0]],'kwargs':kwargs,'texts':[r[-2:]for r in result[0]or[]]});return result
  value=near_number(image,texts,anchors[0],traced,side='above' if label=='收藏品'else'right')if len(anchors)==1 else None
  rows.append({'scale':scale,'label':label,'independently_viewed_expected':expected,'anchor_count':len(anchors),'anchors':anchors,'actual_value':value,'matches':value==expected,'local_crop_calls':calls})
(out/'results.json').write_text(json.dumps({'rows':rows,'public_source_sha256':sha256(source.read_bytes()).hexdigest(),'manual_field_coordinates_used':False,'production_anchor_code_used':True,'production_changed':False,'actual_read_run_or_live_page_acceptance':False,'scope':'Outcome-selected public video composite containing a separate helper overlay;four fields diagnose observed-label geometry only,not production game-only routing or accuracy.No forced numeric hints or thresholds changed.','production_source_sha256':{p:sha256((R/p).read_bytes()).hexdigest()for p in ('rouge/run_recognition.py','rouge/anchors.py')}},ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(rows,ensure_ascii=False))
