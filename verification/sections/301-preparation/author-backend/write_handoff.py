"""Freeze a cache-only candidate after the first actual public backend checks."""
from datetime import datetime,timezone
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CANDIDATE=HERE/'candidate'
sys.path.insert(0,str(ROOT))
def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def pin(path):
 raw=path.read_bytes();return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
spec=importlib.util.spec_from_file_location('rouge._named_reward301_public_example',CANDIDATE/'rouge/named_reward_items.py')
model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
event=model.event_reference('community_group_007')
details=model.item_details('community_group_007','community_group_007:scene:0','community_group_007:scene:0:choice:1')
assert event['source_valid']and details['source_valid']and details['relic']is None
example={'event':event,'details':details}
(HERE/'public-example.json').write_bytes(encoded(example))
files={p.relative_to(CANDIDATE).as_posix():pin(p)for p in sorted(CANDIDATE.rglob('*'))if p.is_file()}
promote={};dependencies={}
for name,p in files.items():
 if(ROOT/name).exists():
  assert pin(ROOT/name)==p,'Existing dependency changed: '+name
  dependencies[name]=p
 else:promote[name]=p
manifest=json.loads((CANDIDATE/model.MANIFEST).read_bytes())
build=json.loads((HERE/'source-build-first/process.json').read_bytes())
checks=json.loads((HERE/'backend-first/process.json').read_bytes())
assert build['exit_code']==checks['exit_code']==0 and checks['sources_unchanged']is True
handoff={'kind':'SECTION301_BACKEND_CACHE_READY_NOT_FORMAL_PRODUCT_OR_NATIVE_ACCEPTANCE',
 'created_at':datetime.now(timezone.utc).isoformat(),'candidate_directory':'candidate','candidate_root':str(CANDIDATE),
 'promote_files':promote,'promotion_file_count':len(promote),'existing_public_dependencies_not_to_promote':dependencies,
 'schema_file':'candidate/research/p3-named-reward-items-301/SCHEMA.md',
 'API':{'module':'rouge.named_reward_items','functions':['event_reference(event_id)','item_details(event_id,scene_key,choice_key)'],
  'constants':{'ROOT':'module parents[1]','DATA':model.DATA,'MANIFEST':model.MANIFEST,'SELECTED_AUTHORITY':model.SELECTED_AUTHORITY,
   'EVENT_IDS':list(model.EVENT_IDS),'CHOICE_KEYS':{k:list(v)for k,v in model.CHOICE_KEYS.items()}},
  'actual_fields':list(model.ACTUAL_FIELDS),'all_actual_fields_None':True,'inventory_updated':False,
  'quantity_reference':None,'source_valid_is_fixed_reference_not_run_state':True,'no_source_or_data_or_evaluator_injection':True},
 'counts':manifest['counts'],'source_contract':{'manifest_files_count':len(manifest['files']),
  'runtime_files':manifest['runtime_files'],'build_authority_files':manifest['build_authority_files'],
  'runtime_file_count':len(manifest['runtime_files']),
  'runtime_bytes_including_manifest':sum(p['bytes']for p in manifest['runtime_files'].values())+(CANDIDATE/model.MANIFEST).stat().st_size,
  'runtime_reads_complete_primary_table':False,'runtime_verifies_complete_build_original_bytes':False,
  'complete_original_reused_from_existing_public300_source':True,
  'complete_current_event_typed_check':True,'complete_live17_typed_check':True,'complete_current_reward_query_typed_check':True,
  'selected_snapshot_digest_and_independent_authority_checked':True,'public_return_is_deepcopy':True,
  'all_runtime_members_and13icons_required_for_all10targets':True,'bad_one_icon_clears_whole_packet':True,
  'recovery_requires_manual_UI_selection':True,'source_valid_does_not_prove_claim_held_or_effect':True},
 'icon_references':json.loads((CANDIDATE/model.DATA).read_bytes())['icons'],
 'author_actual_checks':{'source_build':{'process':'source-build-first/process.json','actual_exit':0,'writes_expected':True},
  'backend_first':{'process':'backend-first/process.json','actual_exit':0,'methods':24,'seconds':12.373,'sources_unchanged':True},
  'all24_test_methods_have_per_test_addCleanup_cache_isolation':True,
  'author_checks_not_to_add_to_formal_product_counts':True},
 'public_example':{'file':'public-example.json',**pin(HERE/'public-example.json')},
 'research_ready':{'file':'.cache/p3-301-named-reward-research/READY.json',
  'sha256':'2244a8f70a72f290d7b3e3ab180fd49e3abf885bed3186e0b06eca8177435fcd'},
 'source_limits':['17 original typed records remain17; only16 current exact catalog bindings/13items are shown.',
  'choice_ro6_rest_4 remains unbound and is not given a new entry.',
  'Quantity, eligibility, actual claim/held/effect, full reward pool and current server applicability remain unknown.',
  'SCRAP has no relic object; item unlock descriptions are not current-option gates.',
  'Any runtime data/query/image loss invalidates the whole package, even other targets.',
  'Full17MB primary and build originals are rebuilt/verified outside runtime queries.'],
 'production_docs_Git_Qt_game_chat_private_modified_or_executed':False,
 'formal_product_or_native_acceptance_claimed':False}
with(HERE/'HANDOFF.json').open('xb')as stream:stream.write(encoded(handoff))
ready={'kind':'SECTION301_BACKEND_CACHE_READY_NOT_ACCEPTANCE','handoff_sha256':pin(HERE/'HANDOFF.json')['sha256'],
 'handoff':str(HERE/'HANDOFF.json'),'candidate_root':str(CANDIDATE),
 'core_sha256':pin(CANDIDATE/'rouge/named_reward_items.py')['sha256'],'data_sha256':model.DATA_SHA256,'manifest_sha256':model.MANIFEST_SHA256,
 'builder_sha256':pin(CANDIDATE/'scripts/build_named_reward_items_301.py')['sha256'],
 'tests_sha256':pin(CANDIDATE/'tests/test_named_reward_items_301.py')['sha256'],
 'promotion_file_count':len(promote),'existing_public_dependencies':len(dependencies),
 'author_backend_actual_exit':0,'author_backend_methods':24,'formal_product_or_native_pass_claimed':False}
with(HERE/'READY.json').open('xb')as stream:stream.write(encoded(ready))
print(json.dumps(ready,ensure_ascii=False,indent=2))
