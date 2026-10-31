from pathlib import Path
import sys,json,time,statistics
R=Path.cwd();sys.path.insert(0,str(R))
import cv2,numpy as np
from rapidocr_onnxruntime import RapidOCR
from rouge.page_ocr import PageOCR
from rouge.recognition_cache import CachedOCR
video=next(R.glob('*.mp4'));cap=cv2.VideoCapture(str(video))
engine=CachedOCR(RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2));page=PageOCR(engine);rows=[]
# Actual distinct public reference frames, with all texts kept in RAM only.
for second in(44,47,52,55):
 cap.set(cv2.CAP_PROP_POS_MSEC,1000*second);ok,image=cap.read();assert ok
 for order in(('original','batch'),('batch','original')):
  raw={};ms={}
  for backend in order:
   started=time.perf_counter()
   raw[backend]=(engine(image)if backend=='original'else page(image))[0]
   ms[backend]=(time.perf_counter()-started)*1000
  assert raw['original']==raw['batch'],'Outputs differ; keep original behavior'
  rows.append({'public_video_second':second,'order':order,'milliseconds':ms,'texts_equal':True,'batch_metrics':{k:page.metrics.get(k)for k in('detected_boxes','recognized_batches','reused_batches','full_detection','complete_current_texts')}})
cap.release();out=R/'.cache/universal-frame-ocr-experiment';out.mkdir(exist_ok=False)
(out/'results.json').write_text(json.dumps({'rows':rows,'raw_pixels_or_text_saved':False,'source':'user-supplied public reference video; original captured desktop frames, not game client crops','interpretation':'Warm repeated full image lets CachedOCR reuse the entire original output; not representative of changed game frames.'},indent=2)+'\n','utf8')
print(json.dumps(rows))
