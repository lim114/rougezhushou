from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json
ROOT=Path(__file__).resolve().parents[1]
name='tests/test_documented_item_integration_295.py';source=ROOT/name
old=source.read_bytes();assert sha256(old).hexdigest()=='4e946fd3579f37bc3f222f855f9c23811c1279c946a4345431161ed141fcc2f9'
cache=ROOT/'.cache/p3-301-historical-test-repair'
new=(cache/'candidate'/name).read_bytes()
assert sha256(new).hexdigest()=='53b54f8f3524ca9aa5ecfec976af0231aba9113e6e1b32e380d71ef89926e3cc'
proof_raw=(cache/'migration.json').read_bytes()
assert sha256(proof_raw).hexdigest()=='9367f7dc8c1e49065eb8a9aef443155ea34448204b730e809cf95cefed7c3f35'
method='test_every_reward_query_including_target_is_exactly_unchanged'
old_tree,new_tree=ast.parse(old),ast.parse(new)
old_cls=next(n for n in old_tree.body if isinstance(n,ast.ClassDef));new_cls=next(n for n in new_tree.body if isinstance(n,ast.ClassDef))
old_methods={n.name:n for n in old_cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
new_methods={n.name:n for n in new_cls.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
assert len(old_methods)==len(new_methods)==9 and set(old_methods)==set(new_methods)
assert all(ast.dump(old_methods[n])==ast.dump(new_methods[n]) for n in old_methods if n!=method)
prefix=old_methods[method].body[:-1]
assert [ast.dump(n) for n in prefix]==[ast.dump(n) for n in new_methods[method].body[:len(prefix)]]
before=ROOT/'verification/sections/298-preparation/before/rouge/node_catalog.py'
assert sha256(before.read_bytes()).hexdigest()=='5fd1d9d839f2d26ee0d1a0c6e99935b0197017dcb491bf9525e5b1081de404c1'
def function(raw):return ast.dump(next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef) and n.name=='event_reward_options'))
assert function(before.read_bytes())==function((ROOT/'rouge/node_catalog.py').read_bytes())
archive=ROOT/'verification/sections/301-preparation/first-necessary-source'/name;archive.parent.mkdir(parents=True,exist_ok=True)
with archive.open('xb') as stream:stream.write(old)
proof=ROOT/'verification/sections/301-preparation/historical295-query-guard/migration.json';proof.parent.mkdir(parents=True,exist_ok=True)
with proof.open('xb') as stream:stream.write(proof_raw)
source.write_bytes(new)
promotion_path=ROOT/'verification/sections/301-preparation/promotion.json'
promotion=json.loads(promotion_path.read_bytes())
promotion.update(kind='root_final_promotion_with_narrow_historical_query_guard_migration',
 prior_promotion=promotion_path.relative_to(ROOT).as_posix(),prior_promotion_sha256=sha256(promotion_path.read_bytes()).hexdigest(),
 old_tests_modified=True,existing_test_maintenance={name:sha256(new).hexdigest()},
 before_test_sha256={name:sha256(old).hexdigest()},
 repair_proof={'receipt':proof.relative_to(ROOT).as_posix(),'sha256':sha256(proof_raw).hexdigest()},
 repair_at_utc=datetime.now(timezone.utc).isoformat())
target=ROOT/'verification/sections/301-preparation/final-promotion.json'
with target.open('x',encoding='utf8') as stream:stream.write(json.dumps(promotion,ensure_ascii=False,indent=2)+'\n')
runner_old=ROOT/'.cache/p3-301-native-window/necessary-revision2/run_section_301_necessary.py'
raw=runner_old.read_bytes();assert sha256(raw).hexdigest()=='1ee0293c7564c5bad09cce6b460d874339b23208120f561cf150164eb0945be2'
old_literal=b"  'verification/sections/295-preparation/pre295-query-baseline.json')}"
new_literal=b"  'verification/sections/295-preparation/pre295-query-baseline.json',\r\n  'verification/sections/298-preparation/before/rouge/node_catalog.py')}"
if old_literal not in raw:
    old_literal=old_literal.replace(b'\n',b'\r\n')
assert raw.count(old_literal)==1
updated=raw.replace(old_literal,new_literal);ast.parse(updated)
runner=ROOT/'.cache/p3-301-native-window/necessary-revision3/run_section_301_necessary.py';runner.parent.mkdir(parents=True,exist_ok=True)
with runner.open('xb') as stream:stream.write(updated)
ready={'kind':'SOURCE_GUARD_REVISION_NOT_NEW_TEST_ACCEPTANCE','old_runner_sha256':sha256(raw).hexdigest(),
 'new_runner_sha256':sha256(updated).hexdigest(),'only_added_source':'verification/sections/298-preparation/before/rouge/node_catalog.py',
 'same_nine_modules':True,'timeout_seconds_unchanged':300,'executed':False}
(runner.parent/'READY.json').write_text(json.dumps(ready,indent=2)+'\n',encoding='utf8')
print(json.dumps({'old_test_methods':9,'unchanged_other_methods':8,'original_38_comparisons_preserved':True,
 'business_sources_changed_for_this_repair':False,'final_promotion':target.relative_to(ROOT).as_posix(),
 'necessary_runner_sha256':sha256(updated).hexdigest()}))
