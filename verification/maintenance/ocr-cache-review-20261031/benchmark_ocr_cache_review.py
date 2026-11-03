from pathlib import Path
from hashlib import sha256
from statistics import median
from time import perf_counter
import importlib.util,json,sys,subprocess
import cv2,numpy as np

R=Path.cwd();sys.path.insert(0,str(R));out=R/'verification/maintenance/ocr-cache-review-20261031/benchmark';out.mkdir(parents=True,exist_ok=False)
def load(name,file):
 spec=importlib.util.spec_from_file_location('rouge.'+name,R/file);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
old_cache=load('_cache_baseline','research/ocr-cache-review-20261031/before-recognition_cache.py')
old_page=load('_page_baseline','research/ocr-cache-review-20261031/before-page_ocr.py')
from rouge import page_ocr,recognition_cache
from rapidocr_onnxruntime import RapidOCR
from importlib.metadata import version
assert version('rapidocr-onnxruntime')=='1.4.4'
engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
old=old_page.PageOCR(engine);new=page_ocr.PageOCR(engine)
assert old._supported()and new._supported()
files=['verification/maintenance/player-tool-navigation-review-20261031/native-current/default-player-technical-fold.png','verification/maintenance/compact-battle-review-20261031/native-current/overview.png']
def digest(value):return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,default=lambda x:x.item(),separators=(',',':')).encode('utf8')).hexdigest()
rows=[];old_times=[];new_times=[]
for filename in files:
 raw=(R/filename).read_bytes();original=cv2.imdecode(np.frombuffer(raw,np.uint8),1)
 for scale in(1.0,.75):
  image=cv2.resize(original,None,fx=scale,fy=scale)if scale!=1 else original.copy()
  direct,_=engine(image)
  case={'source':filename,'source_sha256':sha256(raw).hexdigest(),'scale':scale,'shape':list(image.shape),'direct_output_sha256':digest(direct),'text_records':len(direct or[]),'rounds':[]}
  for repeat in range(3):
   results={};times={};metrics={}
   order=[('old',old),('new',new)]if repeat%2==0 else[('new',new),('old',old)]
   for label,reader in order:
    started=perf_counter();value,_=reader(image,regions=[[0,0,image.shape[1]//2,image.shape[0]]]);times[label]=(perf_counter()-started)*1000;results[label]=digest(value);metrics[label]=dict(reader.metrics)
   assert results['old']==results['new']==case['direct_output_sha256']
   for key in ('detected_boxes','recognized_batches','reused_batches','recognized_boxes','cache_bytes','page_boxes','guard_boxes'):
    assert metrics['old'].get(key)==metrics['new'].get(key),(key,metrics)
   case['rounds'].append({'repeat':repeat,'order':[x[0]for x in order],'old_ms':times['old'],'new_ms':times['new'],'complete_text_boxes_strings_confidences_equal_to_original_engine':True,'recognized_batches':metrics['new']['recognized_batches'],'reused_batches':metrics['new']['reused_batches'],'detected_boxes':metrics['new']['detected_boxes']})
   if repeat:old_times.append(times['old']);new_times.append(times['new'])
  rows.append(case)
  (out/'progress.json').write_text(json.dumps({'completed_frame_cases':len(rows),'last_text_records':case['text_records']})+'\n','utf8')

image=cv2.imdecode(np.frombuffer((R/files[0]).read_bytes(),np.uint8),1)
crop=image[120:184,:min(image.shape[1],1024)]
old_exact=old_cache.ExactImageCache();new_exact=recognition_cache.ExactImageCache()
compute=lambda:([['生命值','12345','攻击力','1200']],None)
assert old_exact.call(crop,('detail',),compute)==new_exact.call(crop,('detail',),compute)
batch_crops=[image[y:y+48,:min(320+32*i,image.shape[1])].copy()for i,y in enumerate(range(80,368,48))]
old_batch=old_page.PageOCR(engine);new_batch=page_ocr.PageOCR(engine)
assert digest(old_batch._recognize_batch(batch_crops)[0])==digest(new_batch._recognize_batch(batch_crops)[0])
samples=[];loops=300
for repeat in range(9):
 times={}
 order=[('old',old_exact,old_batch),('new',new_exact,new_batch)]if repeat%2==0 else[('new',new_exact,new_batch),('old',old_exact,old_batch)]
 for label,exact,batch in order:
  start=perf_counter()
  for _ in range(loops):exact.call(crop,('detail',),compute)
  times[label+'_exact_ms']=(perf_counter()-start)*1000/loops
  start=perf_counter()
  for _ in range(loops):batch._recognize_batch(batch_crops)
  times[label+'_batch_ms']=(perf_counter()-start)*1000/loops
 samples.append({'repeat':repeat,**times})
medians={key:median(row[key]for row in samples)for key in('old_exact_ms','new_exact_ms','old_batch_ms','new_batch_ms')}
result={'passed':True,'scope':'actual installed RapidOCR1.4.4 CPU,2x2 threads; two public isolated UI images at two sizes; not live game accuracy or whole-app latency','raw_frame_cases':rows,'whole_page_warm_median_ms':{'old':median(old_times),'new':median(new_times),'paired_samples':len(new_times),'not_a_generalized_speedup_claim':True},'cache_hit_component':{'source_crop_shape':list(crop.shape),'loops_per_sample':loops,'alternating_order_samples':samples,'medians':medians,'inference_time_excluded_from_warm_cache_component':True},'array_pixel_change_dtype_shape_context_and_memory_limits':'covered by separate necessary checks','new_external_dependencies':False,'private_images_or_run_state_used':False,'game_operated':False,'chat_sent':False}
(out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'passed':True,'actual_RapidOCR_frame_cases':len(rows),'old_new_original_outputs_all_equal':True,'cache_component_medians_ms':medians,'whole_page_warm_median_ms':result['whole_page_warm_median_ms']},ensure_ascii=False))
