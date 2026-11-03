"""Independent public fixtures; never a replacement for native-client captures."""
import hashlib,json,sys
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from rapidocr_onnxruntime import RapidOCR
ROOT=Path(__file__).resolve().parent
REPO=next(parent for parent in ROOT.parents if (parent/"rouge/recognition.py").is_file() and (parent/"tests/test_adaptive_recognition.py").is_file())
sys.path.insert(0,str(REPO))
from rouge.recognition import ScreenReader,specialized_observation_valid
from rouge.recognition_cache import CachedOCR
from rouge.dynamic_ocr import DynamicOCR
from rouge.page_features import PageFeatureRouter

class TracedDynamicOCR(DynamicOCR):
 def __init__(self,engine):super().__init__(engine);self.calls=[]
 def __call__(self,image,**kwargs):
  before={'frame':list(image.shape),'prior_frame':None if self.image is None else list(self.image.shape),'prior_age':self.age,'prior_domain':self.regions,'prior_text_bounds':[r[0] for r in self.raw],'kwargs':kwargs}
  result=super().__call__(image,**kwargs);before['result_metrics']=dict(self.metrics);self.calls.append(before);return result

def reader(**kwargs):
 r=ScreenReader(**kwargs);r._engine=CachedOCR(RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2));r._frame_ocr=TracedDynamicOCR(r._engine);return r

def compact(result):
 return {'page':result['page'],'operator':result['operator'],'observed_at':result['observed_at'],'texts':[r['text'] for r in result['texts']],'performance':result['performance'],'viewport':result['viewport']}

# Real OCR through real ScreenReader, unknown public page: no operator is claimed.
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',58)
def numeric(value):
 im=Image.new('RGB',(1280,703),(8,8,8));draw=ImageDraw.Draw(im)
 draw.text((110,110),'PUBLIC '+value,font=font,fill='white')
 draw.text((110,450),'UNRELATED 100',font=font,fill='white')
 return cv2.cvtColor(np.asarray(im),cv2.COLOR_RGB2BGR)
numeric_reader=reader(page_routing_enabled=False)
first_image=numeric('42');changed=numeric('93')
first=numeric_reader.read(first_image);second=numeric_reader.read(changed)
relocated=np.full((930,1550,3),8,np.uint8);relocated[70:773,80:1360]=first_image
third=numeric_reader.read(relocated)
assert second['performance']['ocr']['pixels']<first_image.shape[0]*first_image.shape[1]
assert 'PUBLIC42' in [t['text'] for t in first['texts']]
fresh=reader(cache_enabled=False,page_routing_enabled=False).read(changed)
print('Independent public text OCR:',[t['text'] for t in first['texts']],[t['text'] for t in second['texts']],[t['text'] for t in fresh['texts']],flush=True)
assert 'PUBLIC42' not in [t['text'] for t in second['texts']]
assert third['performance']['ocr']['mode']=='full_discovery'
for name,im in [('public-text-before',first_image),('public-text-after',changed)]:cv2.imwrite(str(ROOT/(name+'.png')),im)

# Public control patches only, explicitly incomplete page, not an operator capture.
router=PageFeatureRouter();p=router.pages[0];w,h=p['reference_size']
controls=np.full((h,w,3),8,np.uint8);patches=[]
for anchor,patch in zip(p['anchors'],p['patches']):
 x0,y0,x1,y1=anchor['box'];controls[y0:y1,x0:x1]=patch[:,:,None]
 file=REPO/'rouge/data/page-features'/anchor['patch']
 patches.append({'path':str(file.relative_to(REPO)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
control_reader=reader()
a=control_reader.read(controls)
changed_controls=controls.copy();changed_controls[249:369,1060:1198]=0
before=router.classify(controls);after=router.classify(changed_controls)
b=control_reader.read(changed_controls)
assert before['specialized'] is True and after['specialized'] is False
assert b['performance']['ocr']['mode']=='full_discovery'
print('Control-erasure metrics',b['performance']['ocr'],b['viewport'],flush=True)
assert b['performance']['ocr']['pixels']==b['viewport']['analysis_size'][0]*b['viewport']['analysis_size'][1]
cv2.imwrite(str(ROOT/'public-controls-after-erasure.png'),changed_controls)
partial={'page':'operator_detail','operator':{'scope':'operator_profile','complete':False,'fields':{}},'run':None,'node_content':None}
assert specialized_observation_valid(partial,'operator_detail') is False

from importlib.metadata import version
result={'runtime':{name:version(name) for name in ('rapidocr-onnxruntime','onnxruntime','opencv-python','numpy','Pillow')},'engine_doubles_used':False,'traced_dynamic_subclass_changes_only_logging':True,'private_case_run':False,'private_case_pass':False,'production_edited':False,'fixtures_are_independent_public_synthetic':True,
 'numeric_legacy_real_ScreenReader':{'first':compact(first),'second':compact(second),'fresh_uncached_changed':compact(fresh),'drawn_ground_truth':'PUBLIC 93','warm_matches_fresh_texts':[t['text'] for t in second['texts']]==[t['text'] for t in fresh['texts']],'warm_has_single_line_ground_truth':'PUBLIC93' in [t['text'] for t in second['texts']],'third':compact(third),'dynamic_calls':numeric_reader._frame_ocr.calls},
 'controls_only_real_default_ScreenReader':{'patches':patches,'before_plan':before,'after_plan':after,'first':compact(a),'second':compact(b),'dynamic_calls':control_reader._frame_ocr.calls},
 'direct_partial_operator_gate':{'input_is_declared_model_not_OCR_fact':True,'counts_as_actual_ocr':False,'accepted':False},
 'limits':['No original operator-mechanist.png or original recognition environment recovered.','Control composite never establishes operator identity or potential.','Full fallback on this independent control erasure is not asserted to be the actual old230 cause.']}
(ROOT/'public-diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Independent public real ScreenReader: changed OCR text logged against fresh uncached baseline; smaller legacy dirty OCR; geometry full rediscovery; erased static controls trigger full fallback. Original private230 test not run.')
