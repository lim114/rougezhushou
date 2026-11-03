from pathlib import Path
import subprocess,sys,json
R=Path.cwd();tag=sys.argv[1];out=R/'verification/maintenance/relic-display-image-review-20261031'/tag;out.mkdir(parents=True,exist_ok=False)
source=(R/'verification/maintenance/scene-reader-review-20261031/tests-current/bootstrap.py').read_text('utf8')
start=source.index('modules=');end=source.index('\nwith TemporaryDirectory',start)
names=['tests.test_relic_display_images_review', 'tests.test_catalog_refresh_review', 'tests.test_view_catalog_045', 'tests.test_inventory_catalog_053', 'tests.test_player_item_sources_394', 'tests.test_player_evidence_history_405']
source=source[:start]+'modules='+repr(names)+source[end:]
source=source.replace("out=R/'verification/maintenance/scene-reader-review-20261031/tests-current'",'out=R/'+repr(out.relative_to(R).as_posix()))
marker='raise SystemExit(0 if result.wasSuccessful()else 1)'

source=source.replace(marker,"(out/'catalog-comparison.json').write_text(json.dumps(sys.modules['tests.test_relic_display_images_review'].COMPARISON,ensure_ascii=False,indent=2)+'\\n','utf8')\n"+marker)
source=source.replace('result=unittest.TextTestRunner', 'def case_ids(suite):\n  return [case.id() for group in suite for case in (list_cases(group))]\n def list_cases(group):\n  return [group] if isinstance(group,unittest.TestCase) else [case for sub in group for case in list_cases(sub)]\n ids=case_ids(suite)\n assert len(ids)==len(set(ids)), \"Duplicate test identities are not distinct coverage\"\n result=unittest.TextTestRunner')
(out/'bootstrap.py').write_text(source,'utf8');argv=[sys.executable,'-B','-X','utf8',str(out/'bootstrap.py')]
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 child=subprocess.Popen(argv,cwd=R,stdout=stdout,stderr=stderr);code=child.wait()
(out/'process.json').write_text(json.dumps({'actual_retained_Popen_pid':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8')
print(json.dumps({'actual_observed_exit':code,'result':json.loads((out/'results.json').read_bytes())if(out/'results.json').exists()else None,'failure_tail':(out/'stderr.txt').read_text('utf8')[-4500:]if code else None},ensure_ascii=False))
raise SystemExit(code)
