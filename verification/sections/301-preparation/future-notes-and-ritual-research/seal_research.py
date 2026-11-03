from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCES=(
 '.cache/p3-287-event-research/fixed-game-topic.json',
 'research/p3-choice-recruitment-290/prts-events-427904.html',
 'research/p3-choice-recruitment-290/prts-events-440271.html',
 'research/p3-stage-context/community-main.html',
 'rouge/data/node-catalog.json',
 'rouge/event_planning.py','rouge/node_catalog.py','rouge/player_node_information.py',
 'rouge/enemy_panel.py','rouge/enemy_environment.py','rouge/auxiliary_enemy_mechanisms.py')
def pin(p):
 b=p.read_bytes();return {'sha256':sha256(b).hexdigest(),'bytes':len(b)}
out={'kind':'cache-only-candidate-research-not-section301-implementation-or-acceptance',
 'selected_section301_scope':'typed named reward illustrations, not this ritual candidate',
 'facts':{'events':38,'scenes':190,'choices':233,'unparsed_notes':10,
          'notes_default_labelled_conditions':10,'notes_added_as_eligibility_checks':0},
 'source_pins':{n:pin(ROOT/n) for n in SOURCES},
 'owned_files':{p.relative_to(HERE).as_posix():pin(p) for p in HERE.rglob('*') if p.is_file() and p.name!='READY.json'},
 'unavailable':{'enemy_complete_HTML':'TLS EOF then Windows HTTP403; actual web tool response only',
                'actual_attached_or_executed':'unknown','original_sourceScene':'not inferred'},
 'actions':{'Qt_tests_Git_game_chat_private_or_live_edits':False,'new_function_completed':False}}
(HERE/'READY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'READY_sha256':pin(HERE/'READY.json'),'owned_files':len(out['owned_files'])},ensure_ascii=False))
