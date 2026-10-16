"""Capture bounded static preview/camera CFG from read-only installation files."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
original=ROOT/'.cache/section283-preparation/extract_source_283.py'
raw=original.read_bytes()
source=raw.decode('utf8')
old="RESEARCH=BASE.parent/'research'"
new="RESEARCH=BASE.parents[1]/'.cache/research'"
assert source.count(old)==1
candidate=source.replace(old,new,1)
extractor=HERE/'extract_preview_cfg.py'
with extractor.open('xb')as stream:stream.write(candidate.encode('utf8'))
verification=json.loads((ROOT/'.cache/research/p2-native-current-263/mapping-verification.json').read_bytes())
metadata=Path(verification['source_metadata'])
assert sha256(metadata.read_bytes()).hexdigest()==verification['metadata_sha256']
names=['Torappu.ResourceUrls$$GetStageMapPreviewPath','Torappu.StageDataUtil$$LoadStagePreviewMap',
 'Torappu.UI.CommonMapPreviewDlg$$OnInit','Torappu.UI.CommonMapPreviewDlg$$OnRender',
 'Torappu.UI.Roguelike.RoguelikeFocusView$$LoadPreviewMap',
 'Torappu.UI.Roguelike.RoguelikeFocusView$$ShowMapPreview',
 'Torappu.UI.Roguelike.RL06.RL06FocusViewPlugin$$_LoadPreviewMap',
 'Torappu.Battle.MapGraphic$$GetCameraConfig','Torappu.Battle.MapGraphic$$GetCameraView',
 'Torappu.Battle.Map$$MapToWorldPosition','Torappu.Battle.Map$$TryGetCameraView']
argv=[sys.executable,'-B','-X','utf8',str(extractor),'--output','preview-camera-cfg']
for name in names:argv+=['--name',name]
start=time.monotonic()
actual=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=60)
for name,blob in [('cfg.stdout',actual.stdout),('cfg.stderr',actual.stderr),
                 ('cfg.exit',(str(actual.returncode)+'\n').encode())]:
 with(HERE/name).open('xb')as stream:stream.write(blob)
result={'kind':'ACTUAL_STATIC_DLL_CFG_EXTRACTION_NOT_GAME_EXECUTION','argv':argv,
 'exit_code':actual.returncode,'seconds':time.monotonic()-start,'upstream_extractor_sha256':sha256(raw).hexdigest(),
 'cache_copy_sha256':sha256(extractor.read_bytes()).hexdigest(),'only_extractor_change':{'old':old,'new':new},
 'fresh_metadata_sha256':verification['metadata_sha256'],'game_or_process_or_Qt_or_tests_executed':False,
 'manual_fit_or_pixel_adjustments':False,'product_source_or_Git_modified':False}
with(HERE/'cfg-process.json').open('xb')as stream:stream.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False))
if actual.returncode==0:print(actual.stdout.decode('utf8'))
raise SystemExit(actual.returncode)
