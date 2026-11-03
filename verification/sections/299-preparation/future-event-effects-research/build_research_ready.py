"""Cache research inventory; does not certify a product or feature section."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def pin(path):
 raw=path.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
owned={str(p.relative_to(ROOT)).replace('\\','/'):pin(p) for p in sorted(HERE.iterdir())
       if p.is_file() and p.name!='READY.json'}
seams=('rouge/player_node_information.py','rouge/node_catalog_view.py','rouge/event_planning.py',
       'rouge/exploration_planning.py','rouge/data/node-catalog.json','rouge/data/run-config.json','PROJECT_PROGRESS.md')
ready={'kind':'cache-only-P3-candidate-research-not-section-completion','created_at':datetime.now(timezone.utc).isoformat(),
 'parent_reported_live_remote':'b56cbf352cf5d171f52ba05839312950df462e8c','Git_not_used_to_independently_verify_this_value':True,
 'recommended_capability':'Exact red-moss choices to future-region phase/effect and conditional victory-reward preview',
 'optional_related_capability':'Resting-corner conditional future-order reference, preserving source wording difference',
 'canonical_source_extraction':'.cache/p3-299-event-gap-research/source-context-complete-v3.json',
 'proposal':'.cache/p3-299-event-gap-research/PROPOSAL.md',
 'owned_files':owned,'current_readonly_seam_pins':{p:pin(ROOT/p) for p in seams},
 'actual_actions':{'pure_source_extractions_exit0':True,'current_database_web_tool_response_saved':True,
   'single_fixed_HTML_HTTP_attempt_status':403,'fixed_revision_web_tool_attempt':'not_accessible',
   'tests_run':False,'Qt_or_GUI_run':False,'production_or_project_docs_modified':False,
   'Git_or_game_or_chat_or_private_state_operations':False},
 'source_limits':['Current ordinary database tool response footer identifies oldid434599; fixed HTML was not obtained.',
   'Early wrong details/customizeData-only selectors are not absence evidence; corrected full-table walk is authoritative for records.',
   'The initially limited selector transcript was not fully archived; do not claim original complete failure raw exists.',
   'A later diagnostic Python -c quoting SyntaxError remains only in tool transcript; it did not alter sources.',
   'Old exact event wording and database wording differ for beautiful-new-land activation; no actual queue or probability is asserted.'],
 'unchanged_gap_counts':{'unbound_original_scenes':25,'unbound_original_choices':57,'unparsed_annotations':10,
   'typed_grant_references':17,'unknown_special_stage_global_floors':15,'uncalibrated_stages':81,'uncalibrated_unique_maps':59},
 'READY_scope':'Source-backed implementation proposal only; root must authorize and perform product integration/necessary/native acceptance.'}
target=HERE/'READY.json';target.write_text(json.dumps(ready,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'path':str(target.relative_to(ROOT)),'sha256':sha256(target.read_bytes()).hexdigest(),
                  'bytes':target.stat().st_size,'owned_file_count':len(owned)},ensure_ascii=False,indent=2))
