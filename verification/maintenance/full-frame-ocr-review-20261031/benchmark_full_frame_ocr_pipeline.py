from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from types import ModuleType
import json,sys,time
R=Path.cwd();sys.path.insert(0,str(R))
import cv2,numpy as np
from rouge.recognition import ScreenReader
old=ModuleType('rouge.prior_recognition');old.__package__='rouge';old.__file__=str(R/'rouge/recognition.py')
exec(compile((R/'research/full-frame-ocr-review-20261031/before-recognition.py').read_bytes(),'<prior-reader>','exec'),old.__dict__)
readers={'before':old.ScreenReader(),'after':ScreenReader()}
video=next(R.glob('*.mp4'));digest=sha256(video.read_bytes()).hexdigest();assert digest=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda'
cap=cv2.VideoCapture(str(video));rows=[];out=R/'verification/maintenance/full-frame-ocr-review-20261031/public-pipeline';out.mkdir(parents=True,exist_ok=False)
def facts(v):
 v=deepcopy(v);v.pop('observed_at',None);v.pop('performance',None);return v
for index,second in enumerate((44,47,52,55,60,95)):
 cap.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,image=cap.read();assert ok
 raw={};row={'second':second,'input_sha256':sha256(image.tobytes()).hexdigest(),'order':['before','after']if index%2==0 else['after','before'],'readers':{}}
 for name in row['order']:
  v=readers[name].read(image);raw[name]=facts(v);p=v['performance'];row['readers'][name]={'total_ms':p['total_ms'],'page':v['page'],'reuse':p.get('reuse'),'ocr':p.get('ocr'),'stages_ms':p.get('stages_ms'),'strategy':p['routing']['strategy']}
 assert raw['before']==raw['after'],f'Pipeline facts differ at {second}; no changed model accepted'
 row['all_interpreted_facts_equal']=True;rows.append(row)
 (out/'progress.json').write_text(json.dumps({'completed_pairs':len(rows)})+'\n','utf8')
cap.release()
result={'passed':True,'rows':rows,'reference_video_sha256':digest,'source':'User-supplied public reference video; desktop composite frames, not actual game client crops','all_current_outputs_compared_in_RAM':True,'private_state_read':False,'pixels_or_recognized_text_persisted':False,'game_operated':False,'chat_sent':False,'not_independent_game_accuracy':True,'startup_and_order_bias_not_claimed_as_general_speedup':True}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':True,'rows':rows}))
