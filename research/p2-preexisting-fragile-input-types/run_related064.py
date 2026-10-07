from pathlib import Path
import subprocess,sys,unittest,hashlib,json,datetime
base=Path(__file__).parent;root=Path('/workspace/rougezhushou');draft=base/'draft064'
commit='c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf'
mods=['test_damage','test_declared_count_input_types','test_target_count_input_types','test_amiya_input_qualification']
tests=draft/'tests';tests.mkdir(exist_ok=True);(tests/'__init__.py').write_text('')
files={}
for name in mods:
 raw=subprocess.check_output(['git','show',f'{commit}:tests/{name}.py'],cwd=root);p=tests/(name+'.py');p.write_bytes(raw);files[str(p.relative_to(draft))]={'sha256':hashlib.sha256(raw).hexdigest(),'source_commit':commit}
sys.path.insert(0,str(draft));sys.path.insert(0,str(base))
source_hash=hashlib.sha256((draft/'rouge/damage.py').read_bytes()).hexdigest()
suite=unittest.TestSuite()
for name in mods:suite.addTests(unittest.defaultTestLoader.loadTestsFromName('tests.'+name))
suite.addTests(unittest.defaultTestLoader.loadTestsFromName('test_preexisting_fragile_input_types'))
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':str(draft),'test_sources':files,'run':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
 'failures':[{'id':t.id(),'traceback':s} for t,s in result.failures],'errors':[{'id':t.id(),'traceback':s} for t,s in result.errors],'skipped':[{'id':t.id(),'reason':s} for t,s in result.skipped],
 'source_sha256':source_hash,'source_end_sha256':hashlib.sha256((draft/'rouge/damage.py').read_bytes()).hexdigest(),'available_checks_passed':result.wasSuccessful()}
assert receipt['source_sha256']==receipt['source_end_sha256']
(base/'related-tests064.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in ('test_sources','failures','errors','skipped')},ensure_ascii=False));sys.exit(0 if result.wasSuccessful() else 1)
