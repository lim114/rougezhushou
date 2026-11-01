from pathlib import Path
from hashlib import sha256
import sys,json,subprocess,time,os,shutil,dataclasses
R=Path.cwd();out=R/'verification/sections/448-current-enemy-component/ocr-detection-probe'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
root=R/'.cache/external-solutions-445';sys.path.insert(0,str(root/'runtime'))
import cv2,numpy as np
from rapidocr_onnxruntime import RapidOCR
from maa.tasker import Tasker
from maa.resource import Resource
from maa.controller import CustomController,Win32Controller,AdbController
from maa.pipeline import JOCR,JRecognitionType
from maa.define import LoggingLevelEnum
engine=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2);characters=engine.text_rec.session.get_character_list();bundle=R/'.cache/section448-ocr-resource';(bundle/'pipeline').mkdir(parents=True);models=bundle/'model/ocr';models.mkdir(parents=True);(bundle/'pipeline/empty.json').write_text('{}','utf8');installed=R/'.venv/Lib/site-packages/rapidocr_onnxruntime/models';pins=[]
for source,target in[('ch_PP-OCRv4_det_infer.onnx','det.onnx'),('ch_PP-OCRv4_rec_infer.onnx','rec.onnx')]:
 raw=(installed/source).read_bytes();(models/target).write_bytes(raw);pins.append({'source':source,'sha256':sha256(raw).hexdigest(),'bytes':len(raw)})
(models/'keys.txt').write_text('\n'.join(characters)+'\n','utf8');Tasker.set_log_dir(R/'.cache/section448-maa-log');Tasker.set_stdout_level(LoggingLevelEnum.Off);Tasker.set_save_draw(False);Tasker.set_save_on_error(False);forbidden=[]
def fail(*args,**kwargs):forbidden.append('real_controller_or_action');raise AssertionError('Static public image recognition only')
Win32Controller.__init__=AdbController.__init__=Tasker.post_action=Tasker.post_task=fail
public=R/'.cache/video414/158.png';image=cv2.imdecode(np.frombuffer(public.read_bytes(),np.uint8),1)
class StaticController(CustomController):
 def connect(self):return True
 def request_uuid(self):return 'public-static-ocr-only'
 def get_features(self):return 0
 def screencap(self):return image
 start_app=stop_app=click=swipe=touch_down=touch_move=touch_up=click_key=input_text=key_down=key_up=fail
resource=Resource();assert resource.use_cpu()and resource.post_bundle(bundle).wait().succeeded;controller=StaticController();assert controller.post_connection().wait().succeeded;tasker=Tasker();assert tasker.bind(resource,controller)and tasker.inited;rows=[]
labels_path=R/'verification/sections/448-current-enemy-component/ocr-diagnostic-regions.json';labels_bytes=labels_path.read_bytes();cases=json.loads(labels_bytes)['cases']
for case in cases:
 public=R/'.cache/video414'/f"{case['second']}.png";assert sha256(public.read_bytes()).hexdigest()==case['public_image_sha256'];full=cv2.imdecode(np.frombuffer(public.read_bytes(),np.uint8),1);x,y,w,h=case['box_xywh'];image=full[y:y+h,x:x+w].copy()
 if case['scale']!=1:image=cv2.resize(image,None,fx=case['scale'],fy=case['scale'],interpolation=cv2.INTER_AREA)
 for only_rec in(False,True):
  raw,_=engine(image,use_cls=False,use_det=not only_rec);rapid=[{'text':r[-2],'score':float(r[-1])}for r in raw or[]];job=tasker.post_recognition(JRecognitionType.OCR,JOCR(threshold=.9,only_rec=only_rec),image).wait();result=job.get();assert job.succeeded and result is not None;details=[n.recognition for n in result.nodes if n.recognition];observations=[r for detail in details for r in detail.all_results];maa=[{'text':r.text,'score':float(r.score),'box_xywh':list(r.box)}for r in observations];rows.append({'case':case['label'],'expected':case['expected'],'only_rec':only_rec,'input_size_wh':[image.shape[1],image.shape[0]],'rapid_all':rapid,'maa_all':maa,'rapid_exact_high_confidence':any(r['text']==case['expected']and r['score']>=.9 for r in rapid),'maa_exact_high_confidence':any(r['text']==case['expected']and r['score']>=.9 for r in maa)})
assert not forbidden and labels_bytes==labels_path.read_bytes()
(out/'results.json').write_text(json.dumps({'rows':rows,'labels_sha256':sha256(labels_bytes).hexdigest(),'installed_model_pins':pins,'dictionary_characters':len(characters),'native_public_only':True,'production_changed':False,'real_controller_or_actions':forbidden,'scope':'Diagnostic detector+recognizer versus recognition-only on manually verified single-field public crops.Outcome-selected,not field localization or continuous/page accuracy,no timing claim.No expected/replace hint sent to either OCR provider.'},ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(rows,ensure_ascii=False))
