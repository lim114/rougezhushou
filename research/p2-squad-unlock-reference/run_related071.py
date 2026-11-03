from pathlib import Path
import subprocess,sys,unittest,hashlib,json,datetime
base=Path(__file__).parent;root=Path('/workspace/rougezhushou');draft=base/'draft071'
commit='59531ff2e9475410a84ef0e60836f89793fd35a9'
mods=['test_run_modifiers','test_run_config_validation','test_enemy_environment','test_enemy_rune_selectors',
      'test_technology_reference','test_shu_periodic_sp_reference']
tests=draft/'tests';tests.mkdir(exist_ok=True);(tests/'__init__.py').write_text('')
files={}
for name in mods:
    raw=subprocess.check_output(['git','show',f'{commit}:tests/{name}.py'],cwd=root)
    path=tests/(name+'.py');path.write_bytes(raw)
    files[str(path.relative_to(draft))]={'sha256':hashlib.sha256(raw).hexdigest(),'source_commit':commit}
sys.path.insert(0,str(draft));sys.path.insert(0,str(base))
from tests.test_enemy_environment import EnemyEnvironmentTests
fixture='samples/native-client/run-map-empty.png'
present=subprocess.run(['git','cat-file','-e',commit+':'+fixture],cwd=root,capture_output=True).returncode==0
if present:
    path=draft/fixture;path.parent.mkdir(parents=True,exist_ok=True)
    raw=subprocess.check_output(['git','show',commit+':'+fixture],cwd=root);path.write_bytes(raw)
    files[fixture]={'sha256':hashlib.sha256(raw).hexdigest(),'source_commit':commit}
else:
    name='test_visible_region_updates_and_survives_partial_pages_and_restart'
    method=getattr(EnemyEnvironmentTests,name)
    setattr(EnemyEnvironmentTests,name,unittest.skip('Fixed committed public snapshot has no '+fixture+'; no private/current screenshot substituted.')(method))
sources=('rouge/run_modifiers.py','rouge/reporting.py','rouge/squad_unlock_reference.py')
start={name:hashlib.sha256((draft/name).read_bytes()).hexdigest() for name in sources}
suite=unittest.TestSuite()
for name in mods:suite.addTests(unittest.defaultTestLoader.loadTestsFromName('tests.'+name))
suite.addTests(unittest.defaultTestLoader.loadTestsFromName('test_squad_unlock_reference'))
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':str(draft),'test_sources':files,
         'run':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
         'failures':[{'id':t.id(),'traceback':s} for t,s in result.failures],
         'errors':[{'id':t.id(),'traceback':s} for t,s in result.errors],
         'skipped':[{'id':t.id(),'reason':s} for t,s in result.skipped],
         'source_start_sha256':start,'source_end_sha256':{name:hashlib.sha256((draft/name).read_bytes()).hexdigest() for name in sources},
         'available_checks_passed':result.wasSuccessful()}
assert receipt['source_start_sha256']==receipt['source_end_sha256']
(base/'related-tests071.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in receipt.items() if k not in ('test_sources','failures','errors','skipped')})
sys.exit(0 if result.wasSuccessful() else 1)
