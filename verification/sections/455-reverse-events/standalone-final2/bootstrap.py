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
modules=['tests.test_current_event_battles_view_326.CurrentEventBattlesView326Tests.test_emergency_only_one_map_black_six_and_repeated_lake_single_choice', 'tests.test_current_event_battles_view_326.CurrentEventBattlesView326Tests.test_reverse_stage_excludes_false_emergency_link_and_preserves_own_stage_filter', 'tests.test_current_event_battles_view_326.CurrentEventBattlesView326Tests.test_two_nonzero_readers_stage_and_nested_owned_reader_keep_refresh', 'tests.test_current_event_battles_view_326.CurrentEventBattlesView326Tests.test_actual_source_damage_clear_all_old_children_recovery_manual', 'tests.test_current_event_battles_view_326.CurrentEventBattlesView326Tests.test_optional_event_source_failure_keeps_core_battle_image_and_other_pages', 'tests.test_current_lake_view_328.CurrentLakeView328Tests.test_shared_choice_waits_for_phase_preserves_prompt_then_focuses_exact_action', 'tests.test_current_lake_view_328.CurrentLakeView328Tests.test_normal_urgent_readers_exact_no_default_version_and_back_to_same_phase', 'tests.test_current_lake_view_328.CurrentLakeView328Tests.test_two_nonzero_readers_parent_refresh_keeps_phase_choice_and_nested_map']
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
 out=R/'verification/sections/455-reverse-events/standalone-final2';out.mkdir(exist_ok=True)
 (out/'results.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests_run':result.testsRun,'failed':len(result.failures),'errors':len(result.errors),'skipped':[{'test':str(t),'reason':r}for t,r in result.skipped],'selectors':modules,'qpa':qt.platformName(),'forbidden_external_calls':forbidden,'temporary_state_only':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(0 if result.wasSuccessful()else 1)

