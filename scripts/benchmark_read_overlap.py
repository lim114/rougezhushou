"""Opt-in benchmark: two warmed readers, current frame arrives100ms after old read.

Reports latency and process CPU; does not change application scheduling, publish
images or emit recognized text. Facts are compared without timing/confidence.
The two readers have separate caches, so this measures the complete proposed
overlap arrangement, not a pure thread-count effect.
"""
from pathlib import Path
import sys,json,time,threading,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cv2,numpy as np
from rouge.recognition import ScreenReader
from scripts.profile_run_059 import differences
import argparse
parser=argparse.ArgumentParser(description='Measure serial versus overlapping full-page reads; local images stay local. Excludes capture/UI and engine warmup.')
parser.add_argument('warmup',type=Path)
parser.add_argument('page_a',type=Path)
parser.add_argument('page_b',type=Path)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
images=[cv2.imdecode(np.fromfile(f,np.uint8),1) for f in (args.warmup,args.page_a,args.page_b)]
def clean(x):
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k not in ('performance','observed_at','elapsed_ms','confidence','score','counter_performance')}
 if isinstance(x,list):return [clean(v) for v in x]
 return x
rows=[]
for case,(old,new) in enumerate([(1,2),(2,1),(0,2)]):
 outputs={}
 for mode in ('serial','parallel'):
  readers=[ScreenReader(),ScreenReader()]
  for r in readers:r.read(images[0])
  started=threading.Event();old_done=threading.Event();errors=[]
  def previous():
   try:
    started.set();readers[0].read(images[old])
   except BaseException as e:errors.append(repr(e))
   finally:old_done.set()
  before_cpu=time.process_time();worker=threading.Thread(target=previous);worker.start();started.wait();time.sleep(.1);t=time.perf_counter()
  if mode=='serial':worker.join()
  result=readers[1 if mode=='parallel' else 0].read(images[new]);latency=round((time.perf_counter()-t)*1000,2);worker.join();assert not errors,errors
  outputs[mode]=clean(result);rows.append({'case':case,'mode':mode,'current_read_ms':latency,'combined_cpu_ms':round((time.process_time()-before_cpu)*1000,2)});print(rows[-1],flush=True)
 diff=differences(outputs['serial'],outputs['parallel']);rows[-1]['fact_difference_count']=len(diff);print('fact differences',len(diff),flush=True)
args.output.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
