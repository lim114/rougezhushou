from pathlib import Path
from hashlib import sha256
import json,sys,time,os
R=Path.cwd();sys.path.insert(0,str(R))
import cv2
from rapidocr_onnxruntime import RapidOCR
from rouge.viewport import prepare_frame
threads=int(sys.argv[1]);cvthreads=int(sys.argv[2]);tag=sys.argv[3];cv2.setNumThreads(cvthreads)
out=R/'.cache/ocr-runtime-trials'/tag;out.mkdir(parents=True,exist_ok=False)
engine=RapidOCR(intra_op_num_threads=threads,inter_op_num_threads=2)
cap=cv2.VideoCapture(str(next(R.glob('*.mp4'))));rows=[]
for second in(44,60,95):
 cap.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,image=cap.read();assert ok
 image,_=prepare_frame(image)
 # Prime each workload before collecting three uncached full reads.
 raw,_=engine(image);digest=sha256(json.dumps(raw,ensure_ascii=False).encode()).hexdigest();times=[]
 for repeat in range(3):
  start=time.perf_counter();result,_=engine(image);times.append((time.perf_counter()-start)*1000)
  assert sha256(json.dumps(result,ensure_ascii=False).encode()).hexdigest()==digest
 rows.append({'public_second':second,'raw_result_sha256':digest,'milliseconds':times,'texts':len(raw or[])})
cap.release();value={'passed':True,'intra_op':threads,'inter_op':2,'OpenCV_threads':cv2.getNumThreads(),'logical_cpus':os.cpu_count(),'rows':rows,'raw_pixels_or_text_saved':False,'private_state_read':False}
(out/'results.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(value))
