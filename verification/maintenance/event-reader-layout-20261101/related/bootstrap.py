from pathlib import Path
from contextlib import ExitStack
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys,json,unittest
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')]
from PySide6.QtWidgets import QApplication
from rouge import app as a,public_archive,public_node_statistics
qt=QApplication([]);assert qt.platformName()=='windows'
forbidden=[]
def fail(name):
 def called(*args,**kwargs):forbidden.append(name);raise AssertionError(name)
 return called
modules=['tests.test_event_reader_layout_review', 'tests.test_box_event_view_322', 'tests.test_current_agency_view_340', 'tests.test_current_cave_view_334', 'tests.test_current_encounters_view_327', 'tests.test_current_exit_view_339', 'tests.test_current_lake_view_328', 'tests.test_current_lone_dog_view_335', 'tests.test_current_memory_tree_view_336', 'tests.test_current_peace_view_343', 'tests.test_current_portal_view_341', 'tests.test_current_reconstruction_view_344', 'tests.test_current_resource_events_view_329', 'tests.test_current_rest_travel_view_331', 'tests.test_current_resting_view_345', 'tests.test_current_ritual_view_324', 'tests.test_current_sand_view_325', 'tests.test_current_scout_view_342', 'tests.test_current_shadow_view_346', 'tests.test_current_startup_view_350', 'tests.test_current_unattended_shop_view_330', 'tests.test_current_vine_events_view_333', 'tests.test_documented_event_flow_view_321']
with TemporaryDirectory(prefix='rouge-state-suite-')as folder,ExitStack()as stack:
 root=Path(folder)
 for key,path in {'ROOT':root,'SETTINGS':root/'settings.json','RUN_STATE':root/'run.json','OPERATOR_STATE':root/'account.json'}.items():stack.enter_context(patch.object(a,key,path))
 backend=a.DesktopBackend
 stack.enter_context(patch.object(a,'list_game_windows',return_value=[]))
 for name in ('connect','capture','next_frame'):stack.enter_context(patch.object(a.GameCapture,name,side_effect=fail(name)))
 for name in ('start','request'):stack.enter_context(patch.object(backend,name,side_effect=fail(name)))
 for owner,name in ((a,'stream_chat'),(a,'read_key'),(public_archive,'fetch'),(public_node_statistics,'fetch')):stack.enter_context(patch.object(owner,name,side_effect=fail(name)))
 suite=unittest.TestLoader().loadTestsFromNames(modules)
 def case_ids(suite):
  return [case.id() for group in suite for case in (list_cases(group))]
 def list_cases(group):
  return [group] if isinstance(group,unittest.TestCase) else [case for sub in group for case in list_cases(sub)]
 ids=case_ids(suite)
 assert len(ids)==len(set(ids)), "Duplicate test identities are not distinct coverage"
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 assert not forbidden,forbidden
 out=R/'verification/maintenance/event-reader-layout-20261101/related';out.mkdir(exist_ok=True)
 (out/'results.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests_run':result.testsRun,'failed':len(result.failures),'errors':len(result.errors),'skipped':[{'test':str(t),'reason':r}for t,r in result.skipped],'selectors':modules,'qpa':qt.platformName(),'forbidden_external_calls':forbidden,'temporary_state_only':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(0 if result.wasSuccessful()else 1)

