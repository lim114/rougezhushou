from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,ast
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return sha256(p.read_bytes()).hexdigest()
h=json.loads((ROOT/'.cache/p3-306-reviewed/HANDOFF.json').read_bytes())
assert sha(ROOT/h['production_battle_view_before']['file'])==h['production_battle_view_before']['sha256']
candidate=Path(h['candidate_root']);out=ROOT/'verification/sections/306-preparation'
record={'section':306,'kind':'root_reviewed_source_and_code_promotion_not_acceptance','at_Beijing':datetime.now(timezone(timedelta(hours=8))).isoformat(),'outputs':{}}
for name,pin in h['promotion_files'].items():
 p=candidate/name;assert sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes']
 target=ROOT/name
 assert name=='rouge/battle_view.py' or not target.exists(),name
 target.parent.mkdir(parents=True,exist_ok=True);before=sha(target) if target.is_file() else None
 target.write_bytes(p.read_bytes());record['outputs'][name]={'before_sha256':before,'after_sha256':sha(target)}
old=ROOT/'tests/test_cloud_index_sync.py';raw=old.read_bytes()
draft=ROOT/'.cache/p3-306-index-label/candidate/tests/test_cloud_index_sync.py'
assert sha(draft)=='a6362e523080193f4be45de4131c9b40927a37e1d5a99998650d4f0b05e44a3a'
assert draft.read_bytes().startswith(raw)
text=draft.read_text('utf8').replace('节 · ','节 + ')
original=ast.parse(raw);updated=ast.parse(text)
for original_class in (n for n in original.body if isinstance(n,ast.ClassDef)):
 new=next(n for n in updated.body if isinstance(n,ast.ClassDef) and n.name==original_class.name)
 assert ast.dump(original_class)==ast.dump(new),'Original tests must remain unchanged.'
old.write_text(text,encoding='utf8');record['outputs']['tests/test_cloud_index_sync.py']={'before_sha256':sha256(raw).hexdigest(),'after_sha256':sha(old),'original_test_classes_preserved':True}
(out/'promotion.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(out/'execution-promotion.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'promoted_public_files':len(record['outputs']),'acceptance_claimed':False}))
