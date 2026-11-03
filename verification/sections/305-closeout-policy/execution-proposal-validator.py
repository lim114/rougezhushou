"""Cache-only closeout proposal. Never applies docs/index, Qt, tests or Git.

Missing final full/main/PNG proofs fail closed. Root reviews the emitted JSON
then uses its separately reviewed closeout implementation to apply changes.
"""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import argparse,json,re

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
OUT=ROOT/'.cache/p3-305-closeout'
NECESSARY='verification/sections/305-necessary-readable/process.json'
WINDOW='verification/sections/305-window-attempt2/actual/window.json'
PROCESS='verification/sections/305-window-attempt2/process.json'
PNG='verification/sections/305-root-png-review.json'
DATA='rouge/data/relic-exchange-flow.json'
DOCS=('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md','AGENTS.md','PROJECT_REQUIREMENTS.md',
 'PROJECT_PROGRESS.md','DEVELOPMENT_CHECKPOINT.json','CLOUD_INDEX.json','CLOUD_HANDOFF.md')
TITLE='回滚文明收藏品提供物核对与两类完整文献流程'
CAPABILITY=('回滚文明完整11场景、19条选择/说明/导航资料可手动阅读；固定本体272件收藏品逐项核对能否交换出去，'
 '251项原提供物旗标为真、21项为假，21项均与完整编目角标对应。区分持有声明、第一次/第二次交换、手掌和首次同类条件，'
 '不把条件相符当实际可选。两条见好就收分别补充文献后续，保留既有导航及四个同文原场景候选。'
 '默认未选，同范围刷新保留搜索、声明与阅读；换范围或来源失效清旧内容。原零件工具完整结果保持不变。')
LIMITS=('272件为固定本体快照，不是当前完整收藏品目录；提供物资格不是奖励池，不能反推奖励档次、数量或概率。'
 '旧PRTS两条退出导航指向场景5，另一份完整调查记录却记载不同退出原文，双源冲突分别保留，不恢复唯一服务器入口。'
 '实际选择、持有、消耗、奖励、剩余次数及当前服务器资格仍未知；25个原场景/57原选项入口、10条附注、17条typed奖励口径不减少。'
 'P3/P2/P1均未全部完成，识别优化仍最后，不推荐或自动选路。')

def need(v,msg):
 if not v:raise ValueError(msg)
def file(name):
 need(type(name)is str,'Explicit public relative proof path required')
 p=PurePosixPath(name)
 need(not p.is_absolute()and'..'not in p.parts and'\\'not in name and':'not in name,'Unsafe proof path')
 q=ROOT.joinpath(*p.parts)
 need(q.is_file()and not q.is_symlink()and q.resolve().is_relative_to(ROOT.resolve()),'Missing/linked proof: '+name)
 need(p.parts[0]in('verification','research','rouge','tests','scripts')or name in DOCS or name=='CORE_0.70_VERIFICATION.json','No private input')
 return q
def pin(name):
 p=file(name);b=p.read_bytes();return{'file':name,'sha256':sha256(b).hexdigest(),'bytes':len(b)}
def read(name):return json.loads(file(name).read_bytes())
def same_sources(record):
 b,a=record['source_sha256_before'],record['source_sha256_after']
 need(type(b)is dict and b and b==a,'Original source before/after differ')
 for name,h in b.items():need(pin(name)['sha256']==h,'Current source differs from actual receipt: '+name)
 return b
def proof_binding(name,expected):need(pin(name)['sha256']==expected,'Actual proof bytes differ: '+name)

def prepare(args):
 cp=read('DEVELOPMENT_CHECKPOINT.json');n=read(NECESSARY);w=read(WINDOW);process=read(PROCESS);visual=read(PNG);data=read(DATA)
 need(cp['completed_sections']==304 and cp['next_section']==305,'Do not overwrite another checkpoint')
 need(cp['policy']['wrap_up_below_usage_percent']==15 and cp['policy']['usage_wrap_up_triggered']is True,'Actual restored usage15 wrap-up policy missing')
 need(cp['policy']['usage_remaining_percent_at_trigger']==4 and cp['policy']['usage_wrap_up_after_active_section']==305,'Wrong active usage wrap-up section')
 threshold=read(cp['policy']['usage_threshold_receipt'])
 need(threshold['triggered']is True and threshold['remaining_percent']<5 and threshold['do_not_start_section_after']==305,'Historical below5 trigger missing; this does not infer current usage')
 latest_instruction_name=cp['policy']['latest_usage_and_pause_instruction_receipt']
 latest_instruction=read(latest_instruction_name)
 need(latest_instruction['current_threshold_percent']==15 and latest_instruction['strictly_below']is True
  and latest_instruction['pause_after_section']==305 and latest_instruction['new306_started']is False,'Restored15 and explicit pause305 instruction required')
 need(cp['last_verified_cloud_save']['section']==304,'Previous publication must be actual304')
 proof_binding(cp['last_verified_cloud_save']['proof'],cp['last_verified_cloud_save']['proof_sha256'])
 need(n['section']==305 and n['passed']is True and n['exit_code']==0 and n['methods_ran']==65 and n['full_validation_rerun']is False,'Final readable necessary65/0 missing')
 ns=same_sources(n);ws=same_sources(w);ps=same_sources(process)
 need(process['status']=='completed'and process['exit_code']==process['child_primary_exit']==0 and process['timed_out']is False
  and process['owned_job_no_live_execution_verified']is True and process['window_receipt_passed']is True,'Actual native process0/Job closure missing')
 proof_binding(WINDOW,process['window_receipt_sha256'])
 need(w['section']==305 and w['passed']is True and w['failure']is None and w['qpa']=='windows'and w['qt_exit_code']==0
  and w['verification_window_closed']is True and w['unique_checks']==72 and len(set(w['checks']))==len(w['checks'])==72,'Actual functional native72/Windows0 missing')
 for name,h in ws.items():
  if name in ns:need(ns[name]==h,'Necessary/native shared source mismatch')
  if name in ps:need(ps[name]==h,'Native process source mismatch')
 need(w['actual_exchange_inventory_consumption_or_reward_verified']is False and w['private_state_read_copied_or_restored']is False
  and w['game_operated']is False and w['game_captures']==0 and w['chat_sent']is False and w['chat_attempted']is False,'Functional scope overstated')
 expected={r['choice_key']:r for r in data['choices']};actual=w['actual_flow_readings']
 need(len(expected)==len(actual)==19 and {r['choice_key']for r in actual}==set(expected),'All19 documented rows not read')
 for r in actual:
  row=expected[r['choice_key']];need(r['scene_key']==row['scene_key']and r['reference_id']==row['reference_id']and r['actual_transition']is None,'Actual flow identity/unknown boundary changed')
  need(r['documented_navigation_destinations']==row['documented_destinations'],'Original documentary navigation lost')
  if row['documented_result_text']is not None:
   need(r['stop_result']==row['documented_result_text']and r['documented_conflict_visible']is True and len(r['original_candidate_ids'])==4,'Two-source exit conflict/candidates hidden')
 need(len(data['catalogue'])==272 and sum(r['canSacrifice']is True for r in data['catalogue'])==251 and sum(r['canSacrifice']is False for r in data['catalogue'])==21,'Offering catalogue scope changed')
 need(all(r['actual_unknown']is True and r['actual_reward']is None for r in w['offering_declaration_observations']),'Offering declarations became actual results')
 need(all(r['complete_output_equal']is True and r['before_sha256']==r['after_sha256']and r['actual_reward_quantity']is None for r in w['legacy_scrap_API_comparisons']),'Legacy scrap API changed')
 review=next(r for r in visual['reviews']if r['attempt']==2 and r['actual_window_receipt_sha256']==pin(WINDOW)['sha256'])
 need(review['layout_and_text_readable']is True and review['source_information_conflict_not_hidden']is True,'Root functional PNG review missing')
 reviewed={x['sha256']for x in review['screenshots']if x['root_viewed_with_view_image']is True and pin(x['path'])['sha256']==x['sha256']}
 need(all(x['sha256']in reviewed for x in w['screenshots']),'Functional PNG unreviewed')

 # The final full aggregate must already exist and pass; current first-failure
 # archive, final summary and final freeze are kept as distinct evidence.
 full=read(args.full_summary)
 need(full.get('after_section',full.get('section'))==305 and full['available_checks_passed']is True
  and full['scope_not_reduced']is True and full['complete_repository_validation']is False,'Actual final full305 available-range PASS is required')
 need(full['source_drift']==[],'Full305 source drift unresolved')
 freeze_name=full['source_freeze'];proof_binding(freeze_name,full['source_freeze_sha256']);freeze=read(freeze_name)
 need(freeze['section']==305 and freeze['root_declared']is True,'Wrong final full305 freeze')
 for key in('source_sha256','legacy_native_source_sha256','supplemental_public_inputs_sha256'):
  for name,h in freeze[key].items():need(pin(name)['sha256']==h,'Final full freeze differs from current source: '+name)
 old_freeze=read('verification/full-290/source-freeze-final-A3.json')
 need(len(old_freeze['selectors'])==430 and freeze['selectors'][:430]==old_freeze['selectors'],'Original430 full selector prefix lost')
 need(len(freeze['p3_scripts'])==20,'Complete20 P3 native windows not frozen')
 need(type(full['actual_validation_attempt'])is int and full['actual_validation_attempt']>=2,'First failed full attempt cannot be relabelled PASS')
 full_visual=read(args.full_png_review)
 need(full_visual['section']==305 and full_visual['reviewer']=='root'and full_visual['all_reviewed']is True
  and full_visual['actual_validation_attempt']==full['actual_validation_attempt']and full_visual['source_freeze_sha256']==full['source_freeze_sha256'],'Final full PNG review is not bound to this actual attempt/freeze')
 need(full_visual['images'],'Empty full PNG review')
 for x in full_visual['images']:
  need(x['reviewed']is True,'Full PNG was not root reviewed');proof_binding(x['file'],x['sha256'])
 main=read(args.main_review)
 need(main['section']==305 and main['passed']is True and main['actual_exit']==0 and main['window_visible_and_responsive']is True
  and main['private_state_five_paths_unchanged']is True,'Actual original main window/private5 review missing')
 if 'original_receipt'in main:proof_binding(main['original_receipt'],main['original_receipt_sha256'])
 need(re.fullmatch('[0-9a-f]{40}',args.prior_commit),'Use actual root prior HEAD40, never a placeholder')
 need(cp['last_full_validation']['after_section']==290,'Historical290 pointer unexpectedly replaced already')

 overlay={'completed_sections':305,'next_section':306,'next_full_validation_after':320,
  'batch_status':'P3_SECTION305_LOCAL_ACCEPTED_PUBLICATION_PENDING_USAGE_WRAPUP',
  'next_action':'用户已恢复15%阈值并明确要求305完整完成后暂停；普通推送与实际远端核对完成后结束，不启动306，等待用户恢复，下次定期全量320。',
  'current_section_save':{'section':305,'verification':'verification/sections/305.json','scope':'current_functional_section','binding':'enclosing_commit'},
  'last_verified_cloud_save':{**deepcopy(cp['last_verified_cloud_save']),'scope':'previous_functional_section'},
  'last_full_validation':{'after_section':305,'receipt':args.full_summary,'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'source_freeze':freeze_name,'source_freeze_sha256':full['source_freeze_sha256']},
  'current_available_full_validation':{'section':305,'receipt':args.full_summary},
  'current_section_validation':{'section':305,'receipt':'verification/sections/305.json','necessary_methods_passed':65,'native_isolated_window_checks':72,'full_suite_rerun':True,'last_full_receipt':args.full_summary,'full_source_is_historical290':False},
  'latest_section_environment':{'section':305,'receipt':'verification/sections/305.json','native_windows':'65 necessary;72 unique functional-native; final complete available full305 bound separately','native_game_or_chat_verified':False,'current_section_full_rerun':True,'last_full_receipt':args.full_summary}}
 inputs=[latest_instruction_name,NECESSARY,WINDOW,PROCESS,PNG,DATA,args.full_summary,args.full_png_review,args.main_review,freeze_name,
  'verification/full-305/execution-attempt1/archive-manifest.json','verification/full-305/repairs-after-first/necessary/process.json',*DOCS]
 proposal={'kind':'ROOT_REVIEW_ONLY_305_CLOSEOUT_PROPOSAL_NOT_APPLIED','title':TITLE,'capability':CAPABILITY,'limits':LIMITS,
  'actual_bound_inputs':{n:pin(n)for n in inputs},'prior_commit_declared_by_root':args.prior_commit,
  'receipt305_fields':{'section':305,'kind':'functional_section','new_capability':CAPABILITY,'limits':[LIMITS],
   'necessary_validation':pin(NECESSARY),'native_process':pin(PROCESS),'native_windows_validation':pin(WINDOW),'functional_root_visual_review':pin(PNG),
   'full_validation':pin(args.full_summary),'full_root_visual_review':pin(args.full_png_review),'original_project_window':pin(args.main_review),
   'full_suite_rerun':True,'complete_repository_validation':False,'original_entry_gaps_unchanged':[25,57],'unparsed_notes_unchanged':10,'typed_named_grant_count_unchanged':17,
   'current_server_or_actual_inventory_verified':False,'next_section':306,'next_periodic_full_section':320,'cloud_publication_binding':'enclosing_commit','cloud_published':False},
  'checkpoint_top_level_overlay':overlay,
  'checkpoint_nested_edits':{'policy.next_full_validation_after':320,'current_batch_commit_policy.next_full_validation_after':320,
   'current_batch.next_full_validation_after':320,'current_batch.next_section':306,'current_batch.next_section_started':False,
   'current_batch.status':overlay['batch_status'],'current_batch.receipt':'verification/sections/305.json',
   'current_batch.batch_closed':False,'policy.new_functional_sections_paused':False,'policy.development_paused_by_latest_user_request':'preserve False until complete; user explicitly requested pause after305'},
  'preserve_under_historical_before305':['last_full_validation','current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'],
  'append_exactly_once':{'sections':{'number':305,'completion_ref':'p3-section-305','topic':TITLE,'verification':'verification/sections/305.json'},'functional_sections_since_latest_requirement':305},
  'remove_current_stale_running_state':'Move old active_section to history; no periodic_full_running/firstfailure state remains current after actual full PASS',
  'document_edits':{'PROJECT_COMPLETED.md':'Prepend305 capability, separate65 necessary/72 native/full actual scope; preserve failures and all limits',
   'WORK_IN_PROGRESS.md':'Prepend actual305 closeout, no306 start, historical usage4 trigger plus restored15 and explicit user pause after305, ordinary publication still pending',
   'AGENTS.md':'Replace only current304 continuation paragraph with305 actual scope; preserve all highest requirements and restored15 full-section rule with explicit pause after305',
   'PROJECT_REQUIREMENTS.md':'Replace only current-delivery marked block with305 actual scope/limits and usage completion boundary',
   'PROJECT_PROGRESS.md':'Keep every remaining todo. Optional header date only; do not remove25/57/10/17 or actual dynamic-state gaps because of this documentary reader',
   'DEVELOPMENT_CHECKPOINT.json':'Apply reviewed overlay+nested edits; append exactly one305 section row, keep304 verified publication as previous',
   'CLOUD_INDEX.json':'Regenerate with scripts/update_cloud_index.py after actual receipt/docs/CP exist; do not hand-edit counters',
   'CLOUD_HANDOFF.md':'Regenerate live index via updater, retain explicit305 completion/usage wrap-up paragraph and full305 limitations'},
  'publication_phase_only_after_ordinary_push_actual_remote_check':{'last_verified_cloud_save.section':305,'last_verified_cloud_save.scope':'current_functional_section',
   'last_verified_cloud_save.binding':'verified_remote_commit','last_verified_cloud_save.commit':'ACTUAL matching local_HEAD/remote_HEAD40 from new proof, never prefilled',
   'proof':'verification/sections/305-publication.json with actual source/tree/remote binding',
   'policy.new_functional_sections_paused':True,'current_batch.batch_closed':True,'current_batch.next_section_started':False,
   'batch_status':'P3_SECTION305_PUBLISHED_USAGE_WRAPUP_COMPLETE','current_batch.status':'P3_SECTION305_PUBLISHED_USAGE_WRAPUP_COMPLETE',
   'cloud_publication_closeout.section':305,'cloud_publication_closeout.batch_closed':True,
   'do_not_start306':True,'next_section':306,'next_full_validation_after':320},
  'production_docs_index_Git_Qt_or_tests_written_or_executed':False}
 OUT.mkdir(parents=True,exist_ok=True);target=OUT/'actual-gated-proposal.json'
 need(not target.exists(),'Never overwrite a previously bound closeout proposal')
 target.write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'proposal':str(target),'applied':False,'full305_actual_pass_bound':True,'ordinary_publication_claimed':False},ensure_ascii=True))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full-summary',required=True);p.add_argument('--full-png-review',required=True)
 p.add_argument('--main-review',required=True);p.add_argument('--prior-commit',required=True);prepare(p.parse_args())
