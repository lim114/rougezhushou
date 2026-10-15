from pathlib import Path
from hashlib import sha256
import json

root=Path(__file__).resolve().parents[1]
source=root/'.cache/p3-292-choice-preview-repair'
handoff=json.loads((source/'REPAIR_HANDOFF.json').read_bytes())
for row in handoff['preconditions']:
    assert sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256']
for row in handoff['candidate']:
    assert sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256']
dest=root/'verification/sections/292-preparation/first-actual-repair'
dest.mkdir(parents=True,exist_ok=False)
members=['REPAIR_HANDOFF.json','node_catalog_view.py.diff','test_event_preview_filters_292.py.diff',
 'first-real-original/rouge/node_catalog_view.py','first-real-original/tests/test_event_preview_filters_292.py']
copied={}
for name in members:
    raw=(source/name).read_bytes();path=dest/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw);copied[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
for original,candidate in zip(handoff['preconditions'],handoff['candidate']):
    (root/original['path']).write_bytes((root/candidate['path']).read_bytes())
    assert sha256((root/original['path']).read_bytes()).hexdigest()==candidate['sha256']
row={'section':292,'actual_first_attempt':'verification/sections/292-necessary-first/process.json',
 'first_attempt_result':{'tests':79,'failures':3,'errors':3,'exit_code':1},
 'repair':'New event explicitly selects the first preview. Same-event scope retains exact origin or no selection. Three test contexts declared independently of directory floor filtering.',
 'files':copied,'before':handoff['preconditions'],'after':handoff['candidate'],
 'new_functional_test_run_required':True,'source_mechanisms_changed':False}
(dest/'application.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'section':292,'repair_applied':True,'actual_functional_tests_yet':False}))
