"""Verify actual ordinary functional push, then prepare publication metadata."""
from datetime import datetime,timezone,timedelta
from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
PARENT='c2b78e4aa4136fe739067b5ccf9d13b595142320'
def git(args,**kw):return subprocess.check_output(['git',*args],cwd=ROOT,**kw)
def sha(raw):return sha256(raw).hexdigest()
def load(name):return json.loads((ROOT/name).read_bytes())
def write(name,value):(ROOT/name).write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
head=git(['rev-parse','HEAD']).decode().strip();stage=load('.cache/section303-stage-readback.json')
assert git(['rev-parse','HEAD^']).decode().strip()==stage['prior_commit']==PARENT
assert git(['branch','--show-current']).decode().strip()=='codex/p2-development'and not git(['status','--porcelain'])
push=load('.cache/section303-functional-push.json')
assert push['section']==303 and push['kind']=='functional'and push['exit_code']==0 and push['commit']==head and push['ordinary_push']is True and push['timed_out']is False
remote=git(['ls-remote','origin','refs/heads/codex/p2-development']).decode().strip();assert remote.split()[0]==head
changed=git(['diff-tree','--no-commit-id','--name-only','-r',head]).decode().splitlines()
assert set(changed)==set(stage['staged_and_disk_sha256'])
section=load('verification/sections/303.json');necessary=load(section['necessary_validation']['receipt']);window=load(section['native_windows_validation']['receipt'])
assert section['section']==303 and section['next_section']==304 and section['prior_commit']==PARENT
assert necessary['exit_code']==0 and window['passed']is True and window['qt_exit_code']==0
assert necessary['source_sha256_before']==necessary['source_sha256_after']and window['source_sha256_before']==window['source_sha256_after']
assert {'tests.test_direct_landmark_303','tests.test_direct_landmark_294','tests.test_map_projection_048'}<=set(necessary['modules']) and len(necessary['modules'])==5
assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]
assert section['remaining_global_stage_floor_gaps_unchanged']==15 and section['unparsed_notes_unchanged']==10
assert set(section['old_tracked_test_maintenance'])=={'tests/test_direct_landmark_294.py','tests/test_map_projection_048.py'}
assert section['only_existing_production_sources_changed']==['rouge/data/fixed-landmark-references.json']
assert section['partial_direct_reference_scope_before']==[10,18,58]and section['partial_direct_reference_scope']==[12,21,107]and section['whole_map_gaps_unchanged']==[81,59]
assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun']is False
assert section['source_reference']['all89_original_requests_preserved']is True and section['source_reference']['accepted_points']==49 and section['source_reference']['rejected_or_unknown_points']==40
expected=dict(stage['staged_and_disk_sha256'])
for mapping in(section['validated_source_sha256'],necessary['source_sha256_after'],window['source_sha256_after']):
 for name,value in mapping.items():
  assert not name.startswith(('.cache/','.local/'))and name!='local-settings.json'
  assert name not in expected or expected[name]==value;expected[name]=value
names=sorted(expected);blobs=git(['cat-file','--batch'],input=(''.join(head+':'+p+'\n'for p in names)).encode('utf8'));offset=0
for name in names:
 end=blobs.index(b'\n',offset);header=blobs[offset:end].split();assert header[1]==b'blob'
 size=int(header[2]);offset=end+1;raw=blobs[offset:offset+size];offset+=size
 assert blobs[offset:offset+1]==b'\n';offset+=1
 assert sha(raw)==expected[name]and raw==(ROOT/name).read_bytes(),name
assert offset==len(blobs)
public_push='verification/sections/303-publication-push.json';proof_path='verification/sections/303-publication.json'
assert not(ROOT/public_push).exists()and not(ROOT/proof_path).exists()
(ROOT/public_push).write_bytes((ROOT/'.cache/section303-functional-push.json').read_bytes())
proof={'section':303,'passed':True,'branch':'codex/p2-development','commit':head,'functional_commit':head,'local_HEAD':head,'remote_HEAD':head,
 'remote_branch':'origin/codex/p2-development','push_primary_exit':push['exit_code'],'actual_push_receipt':public_push,
 'actual_push_receipt_sha256':sha((ROOT/public_push).read_bytes()),'verified_at_Beijing':datetime.now(timezone(timedelta(hours=8))).isoformat(),
 'actual_remote_ref_command':['git','ls-remote','origin','refs/heads/codex/p2-development'],'actual_remote_ref_stdout':remote,
 'verified_public_files':{n:expected[n]for n in changed},'verified_necessary_and_window_public_source_files':len(expected),
 'all_changed_public_files_and_current_validated_sources_match_commit':True,'private_files_included':False,'source_receipt_matches_verified_git_bytes':True,
 'full290_is_historical_not_relabelled_for303':True,
 'scope':('Complete89 first readings by two isolated-context agents are retained;49 accepted and40 rejected/unknown. '+
  'Only original A pixels within the unchanged exact4px Euclidean gate are appended; no mean, fit or adjustment. '+
  'New partial ground centers cover the fixed maps of ro6_b_6 and ro6_n_2_3 plus the explicitly bound emergency alias. '+
  'Old58 whole records and regular12image24stage dictionary are unchanged; partial totals are12images21stages107points. '+
  'Whole-map81/59 gaps, highland/portal/offset/actual-position and inverse/segment limits remain. '+
  'Two old tests have exact documented compatibility maintenance; unchanged18 and8 method ASTs are preserved. '+
  'Actual local public historical inputs have exact public counterparts and dual before/after source guards; no private historical sample claimed. '+
  'Only fixed direct-reference runtime data changes; no product Python or route advice is added. '+
  'Historical290 full validation remains historical; publication does not add a functional section.'),
 'necessary_methods_actual':section['necessary_validation']['methods_run'],'native_unique_checks_actual':window['unique_checks'],
 'native_assertion_count_actual':window['successful_assertion_executions_including_repeated_guards'],'current_source_full_validation_claimed':False,
 'all89_original_requests_preserved':True,'accepted_direct_points':49,'rejected_or_unknown_points':40,
 'prior_partial_direct_scope':[10,18,58],'partial_direct_reference_scope':[12,21,107],
 'old58_complete_records_unchanged':True,'regular12_images24_stages_unchanged':True,
 'old_typed_reward_contract_unchanged':True,'typed_named_grant_count_unchanged':17,
 'old_resource_and_player_information_production_pipelines_not_modified':True,
 'unparsed_notes_unchanged':10,'actual_server_generation_or_inventory_verified':False,
 'old_tracked_tests_changed':True,'old_test_maintenance_paths':sorted(section['old_tracked_test_maintenance']),
 'PROJECT_PROGRESS_only_exact_scope_fragment_replaced':True,
 'original_entry_gaps_unchanged':[25,57],'remaining_global_stage_floor_gaps_unchanged':15,
 'whole_map_gaps_unchanged':[81,59],'actual_game_entry_verified':False}
write(proof_path,proof)
cp=load('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==303 and cp['next_section']==304 and'historical_before303_publication'not in cp
cp['historical_before303_publication']=cp['last_verified_cloud_save']
cp['last_verified_cloud_save']={'section':303,'scope':'current_functional_section','binding':'verified_remote_commit','commit':head,'proof':proof_path,'proof_sha256':sha((ROOT/proof_path).read_bytes())}
cp['batch_status']='P3_SECTION303_PUBLISHED_CONTINUATION_READY';cp['current_batch']['status']=cp['batch_status']
cp['cloud_publication_closeout']={'section':303,'functional_commit':head,'functional_source_bytes_unchanged':True,'proof':proof_path,
 'current_commit_kind':'publication metadata; no additional functional section','next_section':304,'batch_closed':False,'next_section_started':False,'numeric_continuation_target':None}
write('DEVELOPMENT_CHECKPOINT.json',cp)
note=('发布核对：功能提交'+head+'已普通推送并核对实际远端；'+str(len(changed))+'份变更公开文件及最终必要/窗口来源与提交逐字节一致，证明'+proof_path+'。仅追加发布元数据，不增加功能节数。\n\n')
for name in('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):
 p=ROOT/name;text=p.read_text(encoding='utf8');index=text.index('## 功能第302节');current=text[:index];assert current.count('待普通推送核对。')==1
 current=current.replace('待普通推送核对。','已普通推送并核对实际远端，详见下方发布证明。',1);p.write_bytes((current+note+text[index:]).encode('utf8'))
updates={'PROJECT_REQUIREMENTS.md':('待普通推送核对。','303功能提交'+head+'已普通推送并核对实际远端，公开证明'+proof_path+'；源码/要求/回执/索引一并保存。'),
 'AGENTS.md':('待普通推送核对，源码/要求/验收/索引同提交。','303功能提交'+head+'已普通推送并核对实际远端，发布证明'+proof_path+'；源码/要求/验收/索引一并保存。')}
for name,(before,after)in updates.items():
 p=ROOT/name;text=p.read_text(encoding='utf8');assert text.count(before)==1;p.write_bytes(text.replace(before,after,1).encode('utf8'))
print(json.dumps({'section':303,'verified_functional_commit':head,'actual_remote_matches':True,'changed_public_files':len(changed),'all_verified_public_files':len(expected),'next_section_started':False}))
