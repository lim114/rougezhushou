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
modules=['tests.test_replay_layout_review', 'tests.test_player_replay_401', 'tests.test_player_history_store_402', 'tests.test_player_replay_nodes_403', 'tests.test_player_resource_history_404', 'tests.test_player_evidence_history_405', 'tests.test_history_reader_review', 'tests.test_map_resource_review', 'tests.test_player_resource_strip']
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
 out=R/'verification/maintenance/replay-layout-review-20261031/tests-final';out.mkdir(exist_ok=True)
 (out/'results.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests_run':result.testsRun,'failed':len(result.failures),'errors':len(result.errors),'skipped':[{'test':str(t),'reason':r}for t,r in result.skipped],'selectors':modules,'qpa':qt.platformName(),'forbidden_external_calls':forbidden,'temporary_state_only':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(0 if result.wasSuccessful()else 1)

