"""Inventory cache-only evidence; never updates a project checkpoint."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def pin(path):
 raw=path.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
selected=(
 '.cache/p3-287-event-research/fixed-game-topic.json',
 'research/p3-stage-context/community-main.html',
 'research/p3-choice-recruitment-290/prts-events-427904.html',
 'research/p3-choice-recruitment-290/prts-events-440271.html',
 '.cache/p3-287-event-research/bwiki-investigation.html',
 'rouge/data/node-catalog.json',
 '.cache/p3-299-event-gap-research/source-context-complete-v3.json',
 '.cache/p3-299-event-gap-research/actual-weather-and-event-web.json',
 '.cache/p3-299-event-gap-research/actual-weather-footer-web.json',
 '.cache/p3-299-event-gap-research/actual-weather-fixed-web-failure.json',
 '.cache/p3-299-event-gap-research/prts-database-434599-HTTP-receipt.json',
 '.cache/p3-299-event-gap-research/prts-database-434599-HTTP-error-body.bin')
result={'kind':'cache-only-independent-evidence-audit-not-300-start-or-acceptance',
 'created_at':datetime.now(timezone.utc).isoformat(),
 'scope':'Normal difficulty reference phase / low-difficulty forced weather / documented hope-gain pairing',
 'canonical_evidence':str(HERE/'phase-and-binding-source-evidence-v2.json'),
 'audit':str(HERE/'AUDIT.md'),
 'own_files':{str(p):pin(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='READY.json'},
 'source_files_absolute':{str((ROOT/p).resolve()):pin(ROOT/p) for p in selected},
 'source_versions':{'game_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
  'main_revision':'433770','events_revisions':['427904','440271'],'BW_revision':'349818',
  'database_ordinary_tool_response_footer_revision':'434599','database_fixed_full_HTML_acquired':False},
 'conclusions':{
  'normal_documented_phase_map':{'2-5':'early','6-11':'middle','12-15':'late'},
  'normal_zero_one_natural_table_cells':{'0':'无','1':'~'},
  'normal_zero_one_forced_weather_generation':None,'normal_zero_one_forced_phase':None,
  'normal_zero_one_recommendation':'Keep all three reference phases readable; do not reject choice or choose early.',
  'original_force_weather_static_target':'rogue_6_weather_8','force_limit_literal':1.0,
  'force_limit_semantics_verified':False,
  'hope_gain_pairing_documented_in_community':True,'complete_execution_pair_binding_authority':False,
  'direct_weather8_subweather4_pair_config_found_in_selected_records':False,
  'absence_claim_scope':'Only all39 literal-matching key/leaf paths and their selected complete records in this exact original table; numeric/aliased references and other scripts are not ruled out.',
  'actual_weather_or_phase_or_pairing_or_reward_or_pool_known':False,
  'resting_corner_cross_event_order_in_scope':False},
 'actions':{'pinned_public_file_extraction_exit0':True,'new_targeted_web_search_batches':2,
  'failed_fixed_HTML_retried':False,'Qt_tests_Git_game_chat_private_operations':False,
  'production_or_handoff_modified':False},
 'proposed_useful_feature':'Manual exact-choice next-region effects reader with phase table and independent conditional victory reward, no current-state or numerical-model changes.'}
target=HERE/'READY.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'path':str(target),'sha256':sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,
 'canonical_evidence_sha256':pin(HERE/'phase-and-binding-source-evidence-v2.json')['sha256']},ensure_ascii=False,indent=2))
