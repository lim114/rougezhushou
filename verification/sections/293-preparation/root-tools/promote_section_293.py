from pathlib import Path
from hashlib import sha256
import ast,json
root=Path(__file__).resolve().parents[1]
base=root/'.cache/p3-293-resting-results-candidate'
handoff=json.loads((base/'CANDIDATE_HANDOFF.json').read_bytes())
catalog=handoff['precondition_catalog']
assert sha256((root/catalog['path']).read_bytes()).hexdigest()==catalog['sha256']
node=root/'rouge/node_catalog_view.py'
assert sha256(node.read_bytes()).hexdigest()=='61c65384c2f9420cf43d134497406cdec0f65d85c507ae8da88403e639ac5791'
mapping={row['destination']:root/row['path'] for row in handoff['candidate_files']}
for row in handoff['candidate_files']:
    assert not (root/row['destination']).exists()
    assert sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256']
ui=root/'.cache/p3-293-root-ui'
ui_handoff=json.loads((ui/'UI_HANDOFF.json').read_bytes())
for name,value in ui_handoff['candidate_sha256'].items():assert sha256((ui/'rouge'/name).read_bytes()).hexdigest()==value
mapping.update({f'rouge/{name}':ui/'rouge'/name for name in ('node_catalog_view.py','resting_corner_view.py')})
mapping['tests/test_resting_corner_view_293.py']=ui/'tests/test_resting_corner_view_293.py'
mapping['scripts/verify_resting_corner_window_293.py']=root/'.cache/p3-293-native-window/verify_resting_corner_window_293.py'
assert not (root/'rouge/resting_corner_view.py').exists()
dest=root/'verification/sections/293-preparation/promotion';dest.mkdir(exist_ok=False)
public={}
for name in ('CANDIDATE_HANDOFF.json','build-first-process.json','build-first.stderr','build-first.stdout',
 'build-attempt2-process.json','build-attempt2.stderr','build-attempt2.stdout',
 'build-revision2-process.json','build-revision2.stderr','build-revision2.stdout',
 'build-revision3-process.json','build-revision3.stderr','build-revision3.stdout',
 'original-scene-text-differences.json','first-build-original/build_resting_corner_results_293.py',
 'revision2/scripts/build_resting_corner_results_293.py'):
    raw=(base/name).read_bytes();key=name.replace('/','--');(dest/key).write_bytes(raw)
    public[key]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
for name,source in mapping.items():
    raw=source.read_bytes()
    if source.suffix=='.py':ast.parse(raw)
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
sources={name:sha256((root/name).read_bytes()).hexdigest() for name in mapping}
row={'section':293,'files_promoted':sources,'public_builder_originals':public,
 'new_tests_not_yet_executed':True,'native_window_not_yet_executed':True,
 'existing_engine_data_eligibility_state_modified':False}
(dest/'application.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'section':293,'promoted':len(mapping),'functional_tests_executed':False,'window_executed':False}))
