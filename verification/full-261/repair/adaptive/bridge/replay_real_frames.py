"""Same public input PNGs, real original ONNX calls; no private sample replacement."""
import hashlib,json,sys,time
from importlib.metadata import version
from pathlib import Path
import cv2,numpy as np
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sys.path.insert(0,str(REPO))
import rouge
if sys.argv[1]=='candidate':rouge.__path__.insert(0,str(ROOT/'candidate/rouge'))
from rouge.recognition import ScreenReader
import rouge.page_ocr
from rouge.recognition_cache import CachedOCR
from rapidocr_onnxruntime.utils import OrtInferSession
INPUT=REPO/'work/adaptive-261-public-operator'
frames=json.loads((INPUT/'frames.json').read_text())['frames']
owner_sequence=json.loads((INPUT/'owner-sequence-frames.json').read_text())['sequence']

def load(record):
 p=REPO/record['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==record['png_sha256']
 image=cv2.imdecode(np.fromfile(p,np.uint8),1)
 assert list(image.shape)==record['shape'] and image.dtype.str==record['dtype']
 assert hashlib.sha256(image.tobytes()).hexdigest()==record['pixel_sha256'];return image

def project(result):
 op=result.get('operator');value={'page':result.get('page'),'operator':None if op is None else {k:op.get(k) for k in ('id','scope','fields','skill_ranks','missing_fields','complete')}}
 return json.loads(json.dumps(value,ensure_ascii=False))

def source_hashes():
 return {name:hashlib.sha256(Path(sys.modules['rouge.'+name[:-3]].__file__).read_bytes()).hexdigest() for name in ('recognition.py','dynamic_ocr.py','page_ocr.py')}
source_start=source_hashes()
phase='init';events=[]
original=OrtInferSession.__call__
def observe(session,tensor):
 started=time.perf_counter();result=original(session,tensor)
 events.append({'phase':phase,'kind':'real_onnx_inference','model':Path(session.session._model_path).name,'shape':list(tensor.shape),'elapsed_ms':(time.perf_counter()-started)*1000});return result
OrtInferSession.__call__=observe
old_cached=CachedOCR.__call__
def observe_request(engine,current,**kwargs):
 before=engine.cache.hits;result=old_cached(engine,current,**kwargs)
 events.append({'phase':phase,'kind':'ocr_request','shape':list(current.shape),'exact_cache_hit':engine.cache.hits>before});return result
CachedOCR.__call__=observe_request

results={};baseline=load(frames['baseline'])
for scenario in ('control_damaged','icon_removed','exterior_overlay','geometry_changed'):
 reader=ScreenReader();phase=scenario+':baseline';first=reader.read(baseline)
 phase=scenario+':changed';second=reader.read(load(frames[scenario]))
 before=json.loads((INPUT/'before-scenarios.json').read_text())['scenarios'][scenario]
 oracle=before['fresh_uncached']
 equality=project(second)==project(oracle)
 assert equality,(scenario,project(second),project(oracle))
 assert first['operator']['complete'] is True
 results[scenario]={'baseline':first,'changed':second,'matches_saved_real_uncached_oracle':equality,'oracle_source':'work/adaptive-261-public-operator/before-scenarios.json','input':frames[scenario]}
 print(json.dumps({'scenario':scenario,'observation':project(second),'ocr':second['performance']['ocr'],'routing':second['performance']['routing'],'matches_saved_real_uncached_oracle':equality},ensure_ascii=False),flush=True)

reader=ScreenReader();sequence=[]
for record in owner_sequence:
 phase='owner_sequence:'+record['label'];result=reader.read(load(record))
 old=json.loads((INPUT/'before-owner-sequence.json').read_text())['results'][record['label']]
 assert project(result)==project(old['fresh_uncached'])
 assert result['operator']['id']==record['declared_owner']
 sequence.append({'input':record,'result':result,'matches_saved_real_uncached_oracle':True})
 print(json.dumps({'frame':record['label'],'observation':project(result),'ocr':result['performance']['ocr'],'routing':result['performance']['routing']},ensure_ascii=False),flush=True)

summary=[]
for label in dict.fromkeys(e['phase'] for e in events):
 selected=[e for e in events if e['phase']==label];inferences=[e for e in selected if e['kind']=='real_onnx_inference']
 summary.append({'phase':label,'detector_calls':sum('det' in e['model'] for e in inferences),'recognizer_calls':sum('rec' in e['model'] for e in inferences),'classifier_calls':sum('cls' in e['model'] for e in inferences),'onnx_shapes':[{'model':e['model'],'shape':e['shape']} for e in inferences],'ocr_request_shapes':[e['shape'] for e in selected if e['kind']=='ocr_request'],'actual_inference_ms':sum(e['elapsed_ms'] for e in inferences)})
source=source_hashes();assert source==source_start,'source changed during actual replay'
receipt={'source':sys.argv[1],'private_original230_run':False,'fixture_kind':'independent public synthetic; all exact input bytes retained','provider_doubles':False,'actual_provider':'RapidOCR '+version('rapidocr-onnxruntime'),'source_hashes':source,'source_hashes_before':source_start,'source_unchanged':source==source_start,'scenarios':results,'current_owner_sequence':sequence,'actual_events':events,'work_summary':summary,'all_match_real_uncached_oracle':True}
(ROOT/(sys.argv[1]+'-real.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
