from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, ast
ROOT=Path(__file__).resolve().parents[1]
name='tests/test_future_region_effects_300.py'
path=ROOT/name;before=path.read_bytes()
assert sha256(before).hexdigest()=='2de614b37b39c224ae22e54a2fb22ab0122cf50428905d67ae88230a3381c8a7'
archive=ROOT/'verification/sections/300-preparation/first-necessary-source'/name
archive.parent.mkdir(parents=True,exist_ok=True)
with archive.open('xb') as stream:stream.write(before)
needle=b'    def setUp(self):\n        self.subject._parsed_packet = None\n'
assert before.count(needle)==1
after=before.replace(needle,needle+b"        self.addCleanup(setattr, self.subject, '_parsed_packet', None)\n")
old_ast,new_ast=ast.parse(before),ast.parse(after)
old_class=next(n for n in old_ast.body if isinstance(n,ast.ClassDef))
new_class=next(n for n in new_ast.body if isinstance(n,ast.ClassDef))
old_methods={n.name:ast.dump(n) for n in old_class.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
new_methods={n.name:ast.dump(n) for n in new_class.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
assert old_methods==new_methods and len(old_methods)==23
path.write_bytes(after)
first=json.loads((ROOT/'verification/sections/300-necessary-attempt1/process.json').read_bytes())
assert first['exit_code']==1 and first['source_unchanged']
promotion=json.loads((ROOT/'verification/sections/300-preparation/promotion.json').read_bytes())
assert promotion['promoted'][name]==sha256(before).hexdigest()
promotion['promoted'][name]=sha256(after).hexdigest()
promotion.update(kind='root_final_promotion_after_new_test_fixture_cleanup',
    prior_promotion='verification/sections/300-preparation/promotion.json',
    prior_promotion_sha256=sha256((ROOT/'verification/sections/300-preparation/promotion.json').read_bytes()).hexdigest(),
    first_actual_failure='verification/sections/300-necessary-attempt1/process.json',
    first_actual_failure_sha256=sha256((ROOT/'verification/sections/300-necessary-attempt1/process.json').read_bytes()).hexdigest(),
    repair={'kind':'new_test_fixture_cleanup_only','file':name,'before_sha256':sha256(before).hexdigest(),
    'after_sha256':sha256(after).hexdigest(),'all_23_method_ASTs_identical':True,
    'reason':'Warm corruption negative leaves cached packet poisoned for later modules; reset the isolated test subject cache via addCleanup.',
    'production_or_mechanism_changed':False,'old_tracked_tests_changed':False},
    repaired_at_utc=datetime.now(timezone.utc).isoformat())
target=ROOT/'verification/sections/300-preparation/final-promotion.json'
with target.open('x',encoding='utf8') as stream:stream.write(json.dumps(promotion,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'only_new_test_fixture_changed':True,'all_23_original_test_ASTs_unchanged':True,
    'final_promotion':target.relative_to(ROOT).as_posix(),'new_test_sha256':sha256(after).hexdigest()}))
