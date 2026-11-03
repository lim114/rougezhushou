from pathlib import Path
from hashlib import sha256
import sys,json,subprocess,time,os,shutil,dataclasses
R=Path.cwd();out=R/'verification/maintenance/mechanism-reading-density-20261101/maa-public-regions'
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
engine=RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2);characters=engine.text_rec.session.get_character_list();bundle=R/'.cache/mechanism-reading-density-ocr-resource';(bundle/'pipeline').mkdir(parents=True);models=bundle/'model/ocr';models.mkdir(parents=True);(bundle/'pipeline/empty.json').write_text('{}','utf8');installed=R/'.venv/Lib/site-packages/rapidocr_onnxruntime/models';pins=[]
for source,target in[('ch_PP-OCRv4_det_infer.onnx','det.onnx'),('ch_PP-OCRv4_rec_infer.onnx','rec.onnx')]:
 raw=(installed/source).read_bytes();(models/target).write_bytes(raw);pins.append({'source':source,'sha256':sha256(raw).hexdigest(),'bytes':len(raw)})
(models/'keys.txt').write_text('\n'.join(characters)+'\n','utf8');Tasker.set_log_dir(R/'.cache/mechanism-reading-density-maa-log');Tasker.set_stdout_level(LoggingLevelEnum.Off);Tasker.set_save_draw(False);Tasker.set_save_on_error(False);forbidden=[]
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
labels_path=R/'verification/maintenance/mechanism-reading-density-20261101/public-ocr-labels-before-inference.json';labels_bytes=labels_path.read_bytes();labels=json.loads(labels_bytes)
for case in labels['cases']:
 public=R/'.cache/video414'/f"{case['reference_second']}.png";assert sha256(public.read_bytes()).hexdigest()==case['full_public_image_sha256'];full=cv2.imdecode(np.frombuffer(public.read_bytes(),np.uint8),1);x,y,w,h=case['manual_crop_xywh'];crop=full[y:y+h,x:x+w];assert crop.shape[:2]==(h,w)
 for scale in(1,.75):
  image=crop.copy()if scale==1 else cv2.resize(crop,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
  start=time.perf_counter();raw,_=engine(image,use_cls=False);rapid_ms=(time.perf_counter()-start)*1000;baseline={r[1]for r in raw or[]if r[2]>=.9};start=time.perf_counter();job=tasker.post_recognition(JRecognitionType.OCR,JOCR(threshold=.9),image).wait();native_ms=(time.perf_counter()-start)*1000;result=job.get();assert result is not None and job.succeeded;details=[node.recognition for node in result.nodes if node.recognition];observations=[item for detail in details for item in detail.filtered_results];texts={item.text for item in observations};expected=set(case['expected_exact_strings']);rows.append({'reference_second':case['reference_second'],'manual_game_only_crop_xywh':case['manual_crop_xywh'],'scale':scale,'actual_input_size_wh':[image.shape[1],image.shape[0]],'expected_exact_strings':sorted(expected),'rapid_exact_matches':sorted(expected&baseline),'rapid_unmatched_expected':sorted(expected-baseline),'maa_exact_matches':sorted(expected&texts),'maa_unmatched_expected':sorted(expected-texts),'rapid_observations':[{'text':r[1],'score':float(r[2]),'polygon':np.asarray(r[0]).tolist()}for r in raw or[]if r[2]>=.9],'maa_observations':[{'text':r.text,'score':float(r.score),'box_xywh':list(r.box)}for r in observations],'rapid_ms':rapid_ms,'maa_ms':native_ms,'job_succeeded':job.succeeded})
assert not forbidden and labels_bytes==labels_path.read_bytes()
(out/'results.json').write_text(json.dumps({'candidate':'Existing isolated MaaFw5.14.3 native CPU OCR with original installed RapidOCR PP-OCRv4 det/rec and dictionary metadata','installed_model_pins':pins,'dictionary_characters':len(characters),'dictionary_sha256':sha256((models/'keys.txt').read_bytes()).hexdigest(),'independent_manual_labels_sha256':sha256(labels_bytes).hexdigest(),'rows':rows,'real_controller_or_actions':forbidden,'production_integration':False,'new_model_install_download':False,'private_data_or_pixels_published':False,'scope':'Three manually cropped game-only regions from public recording,inference after manual exact-string labels,two resolutions.One shop region and two different map headers/footers,not independent full-page or continuous native captures.Exact matches not normalized field accuracy;merged tokens/geometry/preprocessing unaligned.Timings single ordered observations,not a fair speed benchmark.','label_geometry_not_field_ground_truth':True},ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'runtime_completed':True,'cases':[{'second':r['reference_second'],'scale':r['scale'],'expected':len(r['expected_exact_strings']),'rapid_matches':len(r['rapid_exact_matches']),'maa_matches':len(r['maa_exact_matches'])}for r in rows],'production_integrated':False}))
