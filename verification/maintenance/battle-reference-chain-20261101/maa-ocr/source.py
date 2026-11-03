from pathlib import Path
from hashlib import sha256
import sys,json,subprocess,time,os,shutil
R=Path.cwd();out=R/'verification/maintenance/battle-reference-chain-20261101/maa-ocr'
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
engine=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2);characters=engine.text_rec.session.get_character_list();bundle=R/'.cache/battle-reference-chain-ocr-resource';(bundle/'pipeline').mkdir(parents=True);models=bundle/'model/ocr';models.mkdir(parents=True);(bundle/'pipeline/empty.json').write_text('{}','utf8');installed=R/'.venv/Lib/site-packages/rapidocr_onnxruntime/models';pins=[]
for source,target in[('ch_PP-OCRv4_det_infer.onnx','det.onnx'),('ch_PP-OCRv4_rec_infer.onnx','rec.onnx')]:
 raw=(installed/source).read_bytes();(models/target).write_bytes(raw);pins.append({'source':source,'sha256':sha256(raw).hexdigest(),'bytes':len(raw)})
(models/'keys.txt').write_text('\n'.join(characters)+'\n','utf8');Tasker.set_log_dir(R/'.cache/battle-reference-chain-maa-log');Tasker.set_stdout_level(LoggingLevelEnum.Off);Tasker.set_save_draw(False);Tasker.set_save_on_error(False);forbidden=[]
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
for repeat in range(2):
 start=time.perf_counter();raw,_=engine(image,use_cls=False);rapid_ms=(time.perf_counter()-start)*1000;baseline={row[1]for row in raw or[]if row[2]>=.9};start=time.perf_counter();job=tasker.post_recognition(JRecognitionType.OCR,JOCR(threshold=.9),image).wait();native_ms=(time.perf_counter()-start)*1000;result=job.get();assert result is not None;details=[node.recognition for node in result.nodes if node.recognition];assert details;observations=[item for detail in details for item in detail.filtered_results];texts={item.text for item in observations};rows.append({'repeat':repeat,'rapid_ms':rapid_ms,'maa_native_ms':native_ms,'job_succeeded':job.succeeded,'rapid_high_confidence_unique_texts':len(baseline),'maa_high_confidence_unique_texts':len(texts),'exact_shared_texts':len(baseline&texts),'rapid_only_texts':len(baseline-texts),'maa_only_texts':len(texts-baseline),'text_sets_equal':baseline==texts,'baseline_text_set_sha256':sha256(json.dumps(sorted(baseline),ensure_ascii=False).encode()).hexdigest(),'candidate_text_set_sha256':sha256(json.dumps(sorted(texts),ensure_ascii=False).encode()).hexdigest()})
assert not forbidden
(out/'results.json').write_text(json.dumps({'candidate':'Existing isolated MaaFw5.14.3 native CPU OCR with original installed RapidOCR PP-OCRv4 det/rec and dictionary metadata;no model install/download','installed_model_pins':pins,'dictionary_characters':len(characters),'dictionary_sha256':sha256((models/'keys.txt').read_bytes()).hexdigest(),'public_input_sha256':sha256(public.read_bytes()).hexdigest(),'rows':rows,'real_controller_or_actions':forbidden,'production_integration':False,'raw_text_pixels_or_private_data_published':False,'scope':'One public composite shop image,cold+warm single order,not fair performance benchmark or independent ground truth. Geometry/preprocess/dictionary contract and more pages need validation before replacement.'},indent=2)+'\n','utf8');print(json.dumps({'runtime_completed':True,'rows':rows,'production_integrated':False}))
