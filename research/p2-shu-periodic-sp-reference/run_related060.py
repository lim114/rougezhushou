from pathlib import Path
import subprocess,sys,importlib.util,unittest,json,hashlib,datetime
base=Path(__file__).parent;root=Path('/workspace/rougezhushou');draft=base/'draft060'
commit='5f8d9cc90200aac68555ece4f7ddeec9fab9b352'
modules=['test_next_attack_healing_reference','test_empty_enemy_scope','test_friendly_scope_report','test_susuro_recipient_factor','test_healing_subtotal_scaling','test_timing','test_sp_sources_066']
tests=draft/'tests';tests.mkdir(exist_ok=True)
(tests/'__init__.py').write_text('')
files={}
for name in modules:
 raw=subprocess.check_output(['git','show',f'{commit}:tests/{name}.py'],cwd=root)
 p=tests/(name+'.py');p.write_bytes(raw);files[str(p.relative_to(draft))]={'sha256':hashlib.sha256(raw).hexdigest(),'source_commit':commit}
sys.path.insert(0,str(draft));sys.path.insert(0,str(base))
loader=unittest.TestLoader();collected=unittest.TestSuite()
for name in modules:collected.addTests(loader.loadTestsFromName('tests.'+name))
collected.addTests(loader.loadTestsFromName('test_shu_periodic_sp_reference'))
def flatten(suite):
 for case in suite:
  if isinstance(case,unittest.TestSuite):yield from flatten(case)
  else:yield case
unavailable=[];ready=unittest.TestSuite()
for test in flatten(collected):
 if test.id().endswith(('test_generator_preserves_the_prefab_medical_selector','test_regeneration_preserves_completed_river_reference_descriptions')):
  unavailable.append({'id':test.id(),'reason':'source generator requires unavailable original .cache/game-data/roguelike_topic_table.json; not copied or fabricated to pass'})
 else:ready.addTest(test)
result=unittest.TextTestRunner(verbosity=2).run(ready)
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':str(draft),'tests_source_commit':commit,'files':files,
 'run':result.testsRun,'passed':result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),
 'skipped':[{'id':t.id(),'reason':r} for t,r in result.skipped],
 'unavailable':unavailable,'failures':[{'id':t.id(),'traceback':r} for t,r in result.failures],
 'errors':[{'id':t.id(),'traceback':r} for t,r in result.errors],'passed_available':result.wasSuccessful()}
(base/'related-tests060.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('files','skipped','unavailable','failures','errors')},ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)
