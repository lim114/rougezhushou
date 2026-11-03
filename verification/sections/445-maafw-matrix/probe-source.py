from pathlib import Path
from hashlib import sha256
import sys,json,time,dataclasses,os
R=Path.cwd();root=R/'.cache/external-solutions-445';sys.path.insert(0,str(root/'runtime'))
out=R/'verification/sections/445-maafw-matrix';out.mkdir(exist_ok=False)
os.chdir(root)
from maa.tasker import Tasker
from maa.resource import Resource
from maa.controller import CustomController,Win32Controller,AdbController
from maa.pipeline import JFeatureMatch,JRecognitionType
from maa.define import LoggingLevelEnum
import cv2,numpy as np
Tasker.set_log_dir(root/'probe-log');Tasker.set_stdout_level(LoggingLevelEnum.Off);Tasker.set_save_draw(False);Tasker.set_save_on_error(False)
forbidden=[]
def fail(*args,**kwargs):forbidden.append('real_controller_or_action');raise AssertionError('Only static image recognition is allowed')
Win32Controller.__init__=AdbController.__init__=Tasker.post_action=Tasker.post_task=fail
public=R/'.cache/video414/158.png';raw=public.read_bytes();image=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
bundle=root/'probe-resource-matrix';(bundle/'pipeline').mkdir(parents=True);(bundle/'image').mkdir()
(bundle/'pipeline/probe.json').write_text('{}','utf8')
template=image[370:445,340:650];cv2.imencode('.png',template)[1].tofile(bundle/'image/shop-label.png')
resource=Resource();resource.set_cpu();assert resource.post_bundle(bundle).wait().succeeded
class StaticFrameController(CustomController):
 def connect(self):return True
 def request_uuid(self):return 'public-static-image-only'
 def get_features(self):return 0
 def screencap(self):return image
 start_app=stop_app=click=swipe=touch_down=touch_move=touch_up=click_key=input_text=key_down=key_up=fail
controller=StaticFrameController();assert controller.post_connection().wait().succeeded
tasker=Tasker();assert tasker.bind(resource,controller)and tasker.inited
rows=[]
negative=cv2.imdecode(np.frombuffer((R/'.cache/video414/60.png').read_bytes(),np.uint8),cv2.IMREAD_COLOR)
for detector in ('SIFT','AKAZE','ORB'):
 for name,frame,expected in [('same_frame',image,[340,370,310,75]),('resized',cv2.resize(image,None,fx=.75,fy=.75),[255,277.5,232.5,56.25]),('different_public_page',negative,None),('blank',np.zeros_like(image),None)]:
  start=time.perf_counter();job=tasker.post_recognition(JRecognitionType.FeatureMatch,JFeatureMatch(template=['shop-label.png'],detector=detector,order_by='Score',count=20),frame).wait();result=job.get();milliseconds=(time.perf_counter()-start)*1000
  found=[n.recognition for n in result.nodes if n.recognition]if result else[]
  rec=found[0]if found else None;box=dataclasses.asdict(rec.box)if rec and rec.box else None;iou=None
  if box and expected:
   x,y,w,h=expected;intersection=max(0,min(x+w,box['x']+box['w'])-max(x,box['x']))*max(0,min(y+h,box['y']+box['h'])-max(y,box['y']))
   iou=intersection/(w*h+box['w']*box['h']-intersection)
  rows.append({'detector':detector,'case':name,'milliseconds':milliseconds,'task_succeeded':job.succeeded,'expected_template_box':expected,'hit':bool(rec and rec.hit),'box':box,'IoU':iou,'matches_expected':bool(rec and rec.hit and iou and iou>.8)if expected else not(rec and rec.hit),'raw_detail':rec.raw_detail if rec else None})
assert not forbidden
value={'package':'MaaFw','version':'5.14.3','wheel_sha256':sha256((root/'wheels/maafw-5.14.3-py3-none-win_amd64.whl').read_bytes()).hexdigest(),'public_source_image_sha256':sha256(raw).hexdigest(),'rows':rows,'real_controllers_or_actions':forbidden,'backend':'CPU FeatureMatch','parameters':{'order_by':'Score','count':20},'parameter_choice_used_prior_same_frame_evidence_not_independent_test':True,'same_source_transforms_and_one_negative_not_overall_accuracy_or_latency':True,'production_integrated':False,'project_environment_modified':False,'no_game_no_chat_no_private_data':True}
(out/'results.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');(out/'probe-source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'runtime_completed':True,'cases':[{k:v for k,v in row.items()if k!='raw_detail'}for row in rows],'production_integrated':False},ensure_ascii=False))
