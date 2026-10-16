"""Copy only already-public fixed sources. No reader outputs are accessed."""
from hashlib import sha256
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PACK=HERE/'candidate/research/p3-map-direct-ground-303'
PACK.mkdir(parents=True,exist_ok=True)
def pin(path):
 raw=path.read_bytes();return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
inputs={
 'prior-direct-references.json':ROOT/'rouge/data/fixed-landmark-references.json',
 'prior-regular-projections.json':ROOT/'rouge/data/battle-map-projections.json',
 'REQUEST_MANIFEST.json':ROOT/'.cache/p3-303-map-candidates/logical-reader-requests-all-lowland.json',
 'reader-grid-ro6_b_6.json':ROOT/'.cache/p3-303-map-candidates/reader-grid-ro6_b_6.json',
 'reader-grid-ro6_n_2_3.json':ROOT/'.cache/p3-303-map-candidates/reader-grid-ro6_n_2_3.json',
}
prior=json.loads(inputs['prior-direct-references.json'].read_bytes())
assert(len(prior['references']),len(prior['stages']),sum(len(r['points'])for r in prior['references'].values()))==(10,18,58)
assert pin(inputs['prior-direct-references.json'])['sha256'].startswith('63ec')
assert pin(inputs['REQUEST_MANIFEST.json'])['sha256']=='c5a5ca22b11b36875c8890e8cce3a1f7d465925c7ddb7320de3963bd0b35854a'
copied={}
for name,source in inputs.items():
 target=PACK/name
 assert not target.exists()
 shutil.copyfile(source,target)
 assert pin(source)==pin(target)
 copied[name]={'original':str(source.relative_to(ROOT)).replace('\\','/'),**pin(target)}
battle=json.loads((ROOT/'rouge/data/battle-previews.json').read_bytes())['stages']
levels=json.loads((ROOT/'research/p3-spawn-candidates-299/source-manifest.json').read_bytes())['stage_files']
records={}
for identity in('ro6_b_6','ro6_n_2_3','ro6_e_2_3'):
 stage=battle[identity]
 semantic=[[{key:stage['tiles'][i].get(key)for key in('tileKey','heightType','buildableType','passableMask')}
            for i in row]for row in stage['map']]
 records[identity]={'image':stage['image'],'level_source':stage['level_source'],
  'level_file':levels[identity],'grid_size':[len(stage['map']),len(stage['map'][0])],
  'grid_sha256':sha256(json.dumps(semantic,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
template={'section':303,'status':'AWAITING_ROOT_FROZEN_ORIGINAL_READERS_NOT_SOURCE_GATE_READY',
 'agreement_tolerance_px':4,'all_source_eligible_requests':89,
 'both_first_complete_readings_frozen_before_comparison':None,'source_pixel_adjustments_after_comparison':0,
 'stages':records,'reader_source_pin_links':{'A':None,'B':None},
 'source_only_readers_not_human_gameplay_observers':True,'whole_map_gaps_unchanged':[81,59]}
(PACK/'source-records.template.json').write_bytes((json.dumps(template,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
(HERE/'fixed-input-copy-receipt.json').write_bytes((json.dumps({'kind':'PUBLIC_FIXED_INPUT_COPY_NO_READER_OBSERVATIONS','files':copied,
 'reader_outputs_accessed':False,'pixel_values_generated':False,'Qt_tests_Git_production_private_changes':False},ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'copied_files':len(copied),'prior58_sha256':copied['prior-direct-references.json']['sha256'],
 'reader_outputs_accessed':False,'source_manifest_bound':False},ensure_ascii=False))
