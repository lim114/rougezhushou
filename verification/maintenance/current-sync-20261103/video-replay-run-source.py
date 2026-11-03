from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import sys,cv2,time,json,tempfile,gc
r=Path.cwd();sys.path[:0]=[str(r),str(r/'.cache/305-window-tooldeps')]
import psutil
psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
from rouge.recognition import ScreenReader
from rouge.run_state import RunState
from rouge.account_cache import AccountCache
from rouge.catalog import catalog,operator_profiles
from rouge.observation_timeline import ObservationTimeline,memory_model
folder=Path((r/'.cache/current-sync-session-folder.txt').read_text('utf8'))/'video-replay';folder.mkdir(exist_ok=False)
cap=cv2.VideoCapture((r/'.cache/current-sync-video-path.txt').read_text('utf8'));images=[]
for t in(0,2,4,6,8):
 cap.set(cv2.CAP_PROP_POS_FRAMES,t*30);ok,im=cap.read();assert ok
 # Fixture-only crop of this existing desktop recording, never runtime capture.
 images.append(im[155:1234,104:2150].copy())
cap.release();results={};timings={};reports=[]
def facts(value):
 if isinstance(value,dict):return {k:facts(v)for k,v in value.items()if k not in('confidence','box','center','badge','evidence','header_evidence','popup_evidence','position','observed_at','captured_at','captured','source_rect','frame','score','grid_error','node_name_box','viewport')and not k.endswith('_evidence')}
 if isinstance(value,list):return [facts(v)for v in value]
 return value
for name,order in [('fifo',[1,2,3,4]),('current_first',[4,1,3,2])]:
 reader=ScreenReader();reader.read(images[0]);elapsed=0;rows={};times={}
 for index in order:
  start=time.perf_counter();value=reader.read(images[index]);ms=(time.perf_counter()-start)*1000;elapsed+=ms;times[index]=ms;rows[index]=value
  print({'mode':name,'index':index,'ms':round(ms,2)},flush=True)
 results[name]=rows;timings[name]=times
 reports.append({'mode':name,'order':order,'read_ms':[times[i]for i in order],'newest_ready_after_ms':sum(times[i]for i in order[:order.index(4)+1]),'all_ready_after_ms':elapsed})
 del reader;gc.collect()
comparisons=[];different=[]
for i in range(1,5):
 a={k:facts(results['fifo'][i].get(k))for k in('page','operator','run','node_content','stage')}
 b={k:facts(results['current_first'][i].get(k))for k in('page','operator','run','node_content','stage')}
 comparisons.append(a==b)
 if a!=b:different.append({'index':i,'keys':[k for k in a if a[k]!=b[k]]})
(folder/'observations-private.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),'utf8')
with tempfile.TemporaryDirectory()as temp:
 run=RunState(Path(temp)/'run.json');account=AccountCache(Path(temp)/'account.json',operator_profiles(),catalog()['operators']);at=run.state['started_at']+1
 oracle=memory_model(run,('state',));oracle_account=memory_model(account,('records','issues'))
 for i in range(1,5):
  packet=results['fifo'][i]
  if packet.get('run'):oracle.apply(packet['run'],at+i)
  if packet.get('operator'):oracle_account.observe(packet['operator'],at+i)
 timeline=ObservationTimeline(run,account);remaining={1,2,3,4}
 for i in(4,1,3,2):
  remaining.remove(i);packet={**results['current_first'][i],'captured_at':at+i};timeline=timeline.prepare(packet,i,min(remaining)if remaining else None)
 same=facts(timeline.run.state)==facts(oracle.state)and facts(timeline.account.records)==facts(oracle_account.records)
value={'scope':'Existing private desktop-video crops; same four inputs with independently warmed engines, chronological versus current-first order. Not a new real game session and not a guarantee for all pages.','same_semantic_observations':comparisons,'same_final_state_without_pixel_provenance':same,'different_semantic_sections':different,'read_orders':reports,'recognition_source_sha256':sha256((r/'rouge/recognition.py').read_bytes()).hexdigest(),'timeline_source_sha256':sha256((r/'rouge/observation_timeline.py').read_bytes()).hexdigest(),'private_observations_images_uploaded':False,'game_operated':False}
(folder/'summary.json').write_text(json.dumps(value,indent=2)+'\n','utf8');(r/'verification/maintenance/current-sync-20261103/video-replay-summary.json').write_text(json.dumps(value,indent=2)+'\n','utf8');print(json.dumps(value))
