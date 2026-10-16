from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'.cache/restart_window_296.py';before=path.read_bytes();text=before.decode('utf8')
old="assert all(necessary['source_sha256_after'][name] == value for name, value in expected_sources.items())"
new="""extra = {'research/p3-stage-context/community-main.html':
         '366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'}
assert {k:v for k,v in expected_sources.items() if k not in necessary['source_sha256_after']} == extra
assert all(necessary['source_sha256_after'][name] == value
           for name,value in expected_sources.items() if name not in extra)
for name,value in extra.items():
    raw = subprocess.check_output(['git','show','c772147f4ee4846464b32b88f51c88f874db3fcd:'+name],cwd=ROOT)
    assert sha256(raw).hexdigest() == value and raw == (ROOT/name).read_bytes()"""
assert text.count(old)==1
directory=ROOT/'verification/sections/296-preparation/main-source-boundary-correction'
directory.mkdir(exist_ok=False)
(directory/'before-restart_window_296.py').write_bytes(before)
path.write_bytes(text.replace(old,new).encode('utf8'))
row={'section':296,'kind':'RESTART_PREFLIGHT_SOURCE_SCOPE_CORRECTION_NO_WINDOW_ACTION',
 'actual_preflight_exit':1,'actual_error':"KeyError: 'research/p3-stage-context/community-main.html'",
 'failure_precedes_try_and_all_window_actions':True,'product_necessary_or_native_failure':False,
 'necessary_source_count':405,'native_source_count':64,'matching_overlap_count':63,
 'native_only_legacy_doc':{'research/p3-stage-context/community-main.html':'366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'},
 'correction':'Verify exact63common and exact one legacy doc against original parent Git bytes/live/native before closing any window; do not invent a64subset405 relation.',
 'before_producer_sha256':sha256(before).hexdigest(),'after_producer_sha256':sha256(path.read_bytes()).hexdigest(),
 'tests_native_or_production_sources_changed':False,'private_contents_copied_or_restored':False}
(directory/'correction.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'restart_preflight_corrected':True,'actual_restart_performed':False}))
