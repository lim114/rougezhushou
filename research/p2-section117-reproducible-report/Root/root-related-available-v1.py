"""Root related regression with the maintained unavailable classifier."""
import argparse, hashlib, json, sys, unittest
from pathlib import Path
p=argparse.ArgumentParser()
for name in ('root','guard','out'):p.add_argument('--'+name,required=True)
p.add_argument('modules',nargs='+');a=p.parse_args()
R=Path(a.root).resolve();G=Path(a.guard).resolve();O=Path(a.out).resolve();raw=G.read_bytes();g=json.loads(raw)
assert not O.exists() and R not in O.parents
def sha(data):return hashlib.sha256(data).hexdigest()
def mapping():return dict(sorted((q.relative_to(R).as_posix(),sha(q.read_bytes())) for d in ('rouge','tests','scripts') for q in (R/d).rglob('*') if q.is_file() and q.suffix in ('.py','.json') and '__pycache__' not in q.parts))
assert mapping()==g['source_sha256']
assert all(sha((R/q).read_bytes())==v for q,v in g['source_additional_sha256'].items())
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'scripts'))
from verify_full_available import AvailableResult
with O.with_suffix('.tests.log').open('x',encoding='utf-8') as log:
 result=unittest.TextTestRunner(stream=log,verbosity=1,resultclass=AvailableResult).run(unittest.defaultTestLoader.loadTestsFromNames(a.modules))
assert mapping()==g['source_sha256'] and G.read_bytes()==raw
assert all(sha((R/q).read_bytes())==v for q,v in g['source_additional_sha256'].items())
passed=result.wasSuccessful()
receipt={'kind':'ROOT_ACTUAL_RELATED_AVAILABLE_REGRESSION','passed':passed,'workflow_complete':True,'source_drift':[],'guard_sha256':sha(raw),'source_count':len(g['source_sha256']),'runner_sha256':sha(Path(__file__).read_bytes()),'modules':a.modules,'tests_run':result.testsRun,'tests_passed':result.passed_count,'failures':len(result.failures),'errors':len(result.errors),'declared_skips':len(result.skipped),'unavailable_records':len(result.unavailable),'unavailable':result.unavailable,'unavailable_not_counted_passed':True,'native_windows_game_chat_verified':False}
with O.open('x',encoding='utf-8') as out:out.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('passed','tests_run','tests_passed','failures','errors','unavailable_records')}))
raise SystemExit(0 if passed else 1)
