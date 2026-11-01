from pathlib import Path
from hashlib import sha256
import sys,subprocess,json,time,statistics
R=Path.cwd();out=R/'verification/maintenance/map-thumbnail-fit-20261101/cache-bytes-trial'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'source.py').write_bytes(Path(__file__).read_bytes());raise SystemExit(code)
import numpy as np
image=np.random.default_rng(0).integers(0,256,size=(1127,1920,3),dtype=np.uint8);items={'full_C':image,'cropped_rows':image[30:130,100:650],'column_stride':image[30:130,100:650:2],'negative_row_stride':image[130:30:-1,100:650],'transposed':image[30:130,100:650].transpose(1,0,2),'crop_gray':image[30:130,100:650,0]};rows=[]
for name,a in items.items():
 baseline=np.ascontiguousarray(a).tobytes();candidate=a.tobytes(order='C');assert baseline==candidate;timings={k:[]for k in('existing','direct')};functions={'existing':lambda:np.ascontiguousarray(a).tobytes(),'direct':lambda:a.tobytes(order='C')}
 for repeat in range(5):
  for key in(('existing','direct')if repeat%2==0 else('direct','existing')):
   start=time.perf_counter()
   for _ in range(10):value=functions[key]()
   timings[key].append((time.perf_counter()-start)*1000/10);assert value==baseline
 rows.append({'kind':name,'shape':list(a.shape),'dtype':a.dtype.str,'contiguous':bool(a.flags.c_contiguous),'bytes':a.nbytes,'exact_byte_parity':True,'median_ms':{k:statistics.median(v)for k,v in timings.items()},'all_ms':timings})
(out/'results.json').write_text(json.dumps({'numpy_version':np.__version__,'rows':rows,'production_cache_changed':False,'synthetic_arrays_only':True,'private_game_data_used':False,'claim':'Serialization-only repeat trial; exact bytes do not establish recognition accuracy or full cache/whole pipeline speedup.'},indent=2)+'\n','utf8');print(json.dumps([{'kind':x['kind'],'median_ms':x['median_ms']}for x in rows]))
