from pathlib import Path
from hashlib import sha256
from time import perf_counter
from unittest.mock import patch
import sys,json,subprocess
R=Path.cwd();sys.path.insert(0,str(R));B=R/'verification/sections/462-statistics/opencl'
if len(sys.argv)==1:
 B.mkdir(exist_ok=False)
 with(B/'stdout.txt').open('xb')as a,(B/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (B/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(B/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
import cv2,numpy as np
from rouge.recognition import ScreenReader
from rouge import relic_recognition as icons
sources={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in(R/'rouge').rglob('*.py')};(B/'source-before.json').write_text(json.dumps(sources,indent=2)+'\n','utf8')
assert cv2.ocl.haveOpenCL()and cv2.ocl.useOpenCL()
video=next(R.glob('*.mp4'));digest=sha256(video.read_bytes()).hexdigest();assert digest=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda'
cap=cv2.VideoCapture(str(video));reader=ScreenReader();original_bar=icons._match_bar;inputs=[]
def capture(roi,*args):inputs.append((roi.copy(),args));return original_bar(roi,*args)
for second in [60,95]:
 cap.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,frame=cap.read();assert ok
 with patch.object(icons,'_match_bar',side_effect=capture):reader.read(frame)
cap.release();assert len(inputs)==2
original_match=cv2.matchTemplate;rows=[]
for input_id,(roi,args)in enumerate(inputs):
 pixels=roi.astype(np.float32);screen=icons.ProjectionScreen(pixels,icons.EnergyScreen(pixels));references=icons.prepared_templates(args[0]);references=references[::max(1,len(references)//32)][:32]
 references=[t for t in references if t[4].shape[0]<roi.shape[0]and t[4].shape[1]<roi.shape[1]];assert references
 gpu_inputs={}
 def gpu_match(image,template,method):
  for value in (image,template):
   if id(value)not in gpu_inputs:gpu_inputs[id(value)]=(value,cv2.UMat(value))
  return original_match(gpu_inputs[id(image)][1],gpu_inputs[id(template)][1],method).get()
 baseline=[screen.possible(t[3],t[4],t[5],t[6])for t in references]
 for repeat,order in enumerate([['numpy','umat_requested'],['umat_requested','numpy'],['numpy','umat_requested']]):
  for backend in order:
   cv2.ocl.finish();start=perf_counter()
   with patch.object(cv2,'matchTemplate',gpu_match if backend=='umat_requested'else original_match):decisions=[screen.possible(t[3],t[4],t[5],t[6])for t in references]
   cv2.ocl.finish();elapsed=(perf_counter()-start)*1000
   rows.append({'input':input_id,'source_second':[60,95][input_id],'bar_shape':list(roi.shape),'reference_count':len(references),'repeat':repeat,'backend':backend,'ms':elapsed,'exact_decisions_equal':decisions==baseline,'reused_umat_inputs':len(gpu_inputs)if backend=='umat_requested'else None})
   (B/'progress.json').write_text(json.dumps({'completed_rounds':len(rows)})+'\n','utf8')
assert cv2.matchTemplate is original_match and all(sha256((R/n).read_bytes()).hexdigest()==h for n,h in sources.items())
result={'passed':True,'rows':rows,'all_decisions_equal':all(r['exact_decisions_equal']for r in rows),'video_sha256':digest,'source_unchanged':True,'private_data_used':False,'production_backend_changed':False,'scope':'Original ProjectionScreen.possible on32 evenly sampled compatible reference templates and each of two public-video bars. UMat inputs are cached by live ndarray identity only inside this isolated frame experiment. Includes result download for original NumPy decision math; no full pipeline or GPU execution-trace claim.'}
(B/'results.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps({'all_decisions_equal':result['all_decisions_equal'],'rows':rows}))
