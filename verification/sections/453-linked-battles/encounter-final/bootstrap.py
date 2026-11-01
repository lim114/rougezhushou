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
slot_errors=[]
def slot_error(kind,value,tb):
 import traceback
 slot_errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=slot_error
def fail(name):
 def called(*args,**kwargs):forbidden.append(name);raise AssertionError(name)
 return called
modules=['tests.test_current_encounters_view_327.CurrentEncountersView327Tests.test_all_23_scenes_25_groups_and_only_black_has_controller_control', 'tests.test_current_encounters_view_327.CurrentEncountersView327Tests.test_required_controller_false_blocks_only_its_branch_same_choice_kept', 'tests.test_current_encounters_view_327.CurrentEncountersView327Tests.test_setup_only_follows_narrative_then_exact_emergency_config_browser', 'tests.test_current_encounters_view_327.CurrentEncountersView327Tests.test_two_nonzero_readers_controller_and_child_state_preserved_refresh', 'tests.test_current_encounters_view_327.CurrentEncountersView327Tests.test_optional_battle_source_failure_keeps_flow_and_actual_core_damage_clears', 'tests.test_current_encounters_view_327.CurrentEncountersView327Tests.test_battle_browser_full_dialog_exact_parent_preserves_refresh_and_closes']
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
 assert not slot_errors,slot_errors
 out=R/'verification/sections/453-linked-battles/encounter-final';out.mkdir(exist_ok=True)
 (out/'results.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests_run':result.testsRun,'failed':len(result.failures),'errors':len(result.errors),'skipped':[{'test':str(t),'reason':r}for t,r in result.skipped],'selectors':modules,'qpa':qt.platformName(),'forbidden_external_calls':forbidden,'temporary_state_only':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(0 if result.wasSuccessful()else 1)

