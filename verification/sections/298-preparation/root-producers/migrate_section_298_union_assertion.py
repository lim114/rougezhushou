from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[1];PREP=ROOT/'verification/sections/298-preparation'
def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def digest(p):return sha256(p.read_bytes()).hexdigest()
p=ROOT/'tests/test_node_catalog.py';raw=p.read_bytes()
assert digest(p)=='6d5ea92a97a4181a36cdd4b945f19c92fa171cdbb8801c9fece94debc0af3aef'
saved=PREP/'first-necessary-source/tests/test_node_catalog.py';saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(raw)
old="        self.assertIn('回滚文明',[e['title'] for e in r['event_union']]);self.assertFalse(r['common_event_references'])"
new="        self.assertNotIn('回滚文明',[e['title'] for e in r['event_union']]);self.assertFalse(r['common_event_references'])\n        self.assertIn('回滚文明',[e['title'] for e in c.route_events(g,['a','b'],floor=3)['event_union']])"
nl='\r\n'if b'\r\n'in raw else'\n';a=old.replace('\n',nl).encode();b=new.replace('\n',nl).encode();assert raw.count(a)==1;p.write_bytes(raw.replace(a,b))
original=PREP/'before/tests/test_node_catalog.py'
def methods(p):return {n.name:n for c in ast.parse(p.read_bytes()).body if isinstance(c,ast.ClassDef)for n in c.body if isinstance(n,ast.FunctionDef)}
first,last=methods(original),methods(p);changed=['test_172','test_183'];others=[k for k in first if k not in changed]
assert first.keys()==last.keys()and all(ast.dump(first[k])==ast.dump(last[k])for k in others)
record={'kind':'historical_assertion_migration_for_new_documented_main_floor_scope',
 'old_source':'verification/sections/298-preparation/before/tests/test_node_catalog.py','old_sha256':digest(original),
 'first_necessary_source':'verification/sections/298-preparation/first-necessary-source/tests/test_node_catalog.py','first_necessary_sha256':digest(saved),
 'first_necessary_receipt':'verification/sections/298-necessary-first/process.json','first_actual_methods':127,'first_actual_failures':1,
 'first_failure':'test_183 expected 回滚文明 in first-floor historical diagnostic union; newly source-bound main-floor rule correctly excludes it.',
 'new_source':'tests/test_node_catalog.py','new_sha256':digest(p),'changed_methods':changed,
 'methods':{k:{'old':ast.unparse(first[k]),'new':ast.unparse(last[k])}for k in changed},
 'unchanged_other_test_methods':len(others),'production_changes_after_first_necessary':False,
 'original_test_172_migration':'verification/sections/298-preparation/historical-test-migration.json',
 'coverage_scope_reduced':False,'old_failure_preserved':True,
 'reason':'Both changes are consequences of the same newly documented natural-floor restrictions. Keep the exact first-floor negative boundary and add the third-floor positive union assertion; preserve common-reference, actual-state and invalid-edge assertions. No numerical model or source restriction changed to make tests pass.'}
(PREP/'historical-test-migration-final.json').write_bytes(encode(record))
base=json.loads((PREP/'root-promotion.json').read_bytes());base['historical_test_migration']='verification/sections/298-preparation/historical-test-migration-final.json'
base['source_freeze_original']='verification/sections/298-preparation/root-promotion.json';base['maintained_test_final']={'path':'tests/test_node_catalog.py','sha256':digest(p)}
(PREP/'final-promotion.json').write_bytes(encode(base))
print(json.dumps({'two_explicit_historical_methods':changed,'other_methods_unchanged':len(others),'new_sha256':digest(p),'production_unchanged':True}))
