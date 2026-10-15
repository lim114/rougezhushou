"""Read-only comparison against the complete previously downloaded public table."""
from hashlib import sha256
import json
from pathlib import Path

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'rouge/app.py').is_file())
raw=(ROOT/'.cache/p3-287-event-research/fixed-game-topic.json').read_bytes()
expected='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
assert sha256(raw).hexdigest()==expected and len(raw)==17943244
topic=json.loads(raw)['details']['rogue_6']
path=ROOT/'research/p3-choice-recruitment-290/original-records.json'
selected=json.loads(path.read_bytes())
assert selected['source']['sha256']==expected and selected['source']['bytes']==len(raw)
assert list(selected['choices'])==['choice_ro6_hire1_1','choice_ro6_hire1_4','choice_ro6_hire1_5','choice_ro6_hire1_6']
for key,record in selected['choices'].items():
    assert record==topic['choices'][key]
for key,record in selected['choiceScenes'].items():
    assert record==topic['choiceScenes'][key]
report={'passed':True,'complete_public_table_sha256':expected,'complete_public_table_bytes':len(raw),
    'selected_records_sha256':sha256(path.read_bytes()).hexdigest(),
    'full_choice_objects_compared':4,'full_scene_objects_compared':1,
    'original_entry_edges_inferred':False,'current_server_or_actual_recruitment_verified':False,
    'private_state_used':False,'scope':'Root independently compares full raw public objects; no extraction/builder function is used.'}
with Path(__file__).with_name('root-original-record-audit.json').open('x',encoding='utf8',newline='\n') as stream:
    stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report))
