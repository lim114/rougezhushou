from pathlib import Path
from hashlib import sha256
from time import perf_counter
import json,sys
import cv2
R=Path.cwd();sys.path.insert(0,str(R))
from rouge.recognition import ScreenReader
out=R/'verification/sections/459-viewport/ocr-profile-quiet';out.mkdir(parents=True,exist_ok=False)
video=next(R.glob('*.mp4'));video_digest=sha256(video.read_bytes()).hexdigest()
assert video_digest=='0b83e44f0816508ef095120961496337e6bd65d5f531ee350c078950dfb98bda'
sources={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()for p in(R/'rouge').rglob('*.py')};(out/'source-before.json').write_text(json.dumps(sources,indent=2)+'\n','utf8');previous=None
cap=cv2.VideoCapture(str(video));reader=ScreenReader();rows=[]
for second in(44.0,44.05,52.0,52.05,60.0,95.0):
 cap.set(cv2.CAP_PROP_POS_MSEC,second*1000);ok,frame=cap.read();assert ok
 for repeat in range(2):
  observation=reader.read(frame.copy());p=observation['performance'];facts={k:v for k,v in observation.items()if k not in('observed_at','performance')};same=repeat==0 or facts==previous;assert same;previous=facts
  routing=p.get('routing')or{};ocr=p.get('ocr')or{}
  row={'source_second':second,'decoder_frame_after':cap.get(cv2.CAP_PROP_POS_FRAMES),'repeat_same_pixels':repeat==1,'identical_frame_facts_equal':same,'shape':list(frame.shape),'page':observation.get('page'),'total_ms':p['total_ms'],'reuse':p['reuse'],'stages_ms':p.get('stages_ms',{}),'routing':{k:routing[k]for k in('strategy','visual_ms','fallback_reason','semantic_verified')if k in routing},'ocr':{k:ocr[k]for k in('mode','pixels','regions','recognized_batches','reused_batches','detected_boxes')if k in ocr}}
  rows.append(row)
  (out/'progress.json').write_text(json.dumps({'completed_reads':len(rows)})+'\n','utf8')
cap.release();assert all(sha256((R/n).read_bytes()).hexdigest()==h for n,h in sources.items())
result={'passed':True,'scope':'Offline full ScreenReader pipeline on four frames from the already-user-supplied reference video, each followed by the identical frame. No game capture or current-run integration claim.','reference_video_sha256':video_digest,'rows':rows,'recognition_sources_unchanged':True,'development_tests_running':False,'same_pixel_output_equality_checked':True,'raw_images_or_recognized_texts_saved_or_published':False,'private_run_state_read':False,'game_operated':False,'chat_sent':False,'speedup_claimed':False,'accuracy_claimed':False}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'reads':len(rows),'rows':[{'second':r['source_second'],'repeat':r['repeat_same_pixels'],'page':r['page'],'total_ms':r['total_ms'],'stages_ms':r['stages_ms'],'reuse':r['reuse']}for r in rows]},ensure_ascii=False))
