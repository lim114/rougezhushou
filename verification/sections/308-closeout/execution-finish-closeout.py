from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,runpy
ROOT=Path(__file__).resolve().parents[1]
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
p=ROOT/'DEVELOPMENT_CHECKPOINT.json';c=json.loads(p.read_bytes());assert c['completed_sections']==308 and c['current_batch']['start']==308 and c['batch_start_section']==307
original_start=c['batch_start_section'];c['batch_start_section']=c['current_batch']['start'];p.write_bytes(enc(c))
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/308-closeout';out.mkdir()
(out/'execution-first-closeout.py').write_bytes((ROOT/'.cache/close308.py').read_bytes());(out/'execution-finish-closeout.py').write_bytes(Path(__file__).read_bytes())
(out/'index-guard-failure-and-repair.json').write_bytes(enc({'section':308,'observed_first_exit':1,'original_error':'ValueError: Current batch pointer differs from the authoritative active batch.','cause':'Starting current308 batch preserved authoritative batch_start_section307 even though current_batch.start308','guard_was_not_relaxed':True,'old_start':original_start,'correct_current_start':c['batch_start_section'],'corrected_existing_authoritative_state_then_reran_index':True,'actual_corrected_index_call_completed':True,'no_functional_or_test_source_change':True}))
(out/'applied.json').write_bytes(enc({'section':308,'local_accepted':True,'ordinary_cloud_publication_verified':False,'at_utc':datetime.now(timezone.utc).isoformat(),'next309_started':False,'section_label':json.loads((ROOT/'CLOUD_INDEX.json').read_bytes())['current_section_label']}))
(ROOT/'verification/sections/308-preparation/execution-main-window.py').write_bytes((ROOT/'.cache/open_test_window_308.py').read_bytes())
print(json.dumps({'completed_section_label':json.loads((ROOT/'CLOUD_INDEX.json').read_bytes())['current_section_label'],'cloud_publication_pending':True},ensure_ascii=False))
