from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json,sys,time,statistics
R=Path.cwd();sys.path.insert(0,str(R))
import cv2,numpy as np
from rapidocr_onnxruntime import RapidOCR
from rouge.viewport import prepare_frame
out=R/'verification/maintenance/ocr-runtime-review-20261031/raw-parity';out.mkdir(parents=True,exist_ok=False)
engines={2:RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2),4:RapidOCR(intra_op_num_threads=4,inter_op_num_threads=2)};cases=[]
for source in sorted((R/'samples/native-client').glob('*.png')):
 image=cv2.imdecode(np.fromfile(source,np.uint8),1);image,_=prepare_frame(image)
 row={'case':source.stem,'same_full_output':True,'measurements':{}};values={}
 for threads in((2,4)if len(cases)%2==0 else(4,2)):
  start=time.perf_counter();cpu=time.process_time();value,_=engines[threads](image)
  row['measurements'][str(threads)]={'elapsed_ms':(time.perf_counter()-start)*1000,'process_CPU_ms':(time.process_time()-cpu)*1000}
  values[threads]=value
 assert values[2]==values[4],'Raw OCR differs: '+source.stem
 cases.append(row);(out/'progress.json').write_text(json.dumps({'complete':len(cases)})+'\n','utf8')
# Shop reader deliberately skips orientation classification; verify that route too.
for case in cases[:3]:
 source=R/'samples/native-client'/(case['case']+'.png');image,_=prepare_frame(cv2.imdecode(np.fromfile(source,np.uint8),1))
 a,_=engines[2](image,use_cls=False);b,_=engines[4](image,use_cls=False);assert a==b
value={'passed':True,'cases':cases,'cls_disabled_cases':3,'full_box_text_score_outputs_equal':True,'raw_images_text_or_sample_pixel_hashes_saved':False,'scope':'Preexisting authorized local development samples. Aggregate comparison only; not independent game accuracy or complete layouts.','source_stable':sha256((R/'rouge/recognition.py').read_bytes()).hexdigest(),'private_run_state_read':False,'game_operated':False,'chat_sent':False}
(out/'results.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':True,'cases':len(cases),'cls_disabled_cases':3}))
