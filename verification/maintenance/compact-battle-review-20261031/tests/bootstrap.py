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
modules=['tests.test_compact_battle_review', 'tests.test_current_battle_view_314', 'tests.test_current_reward_view_315', 'tests.test_current_reward_integration_315', 'tests.test_current_settlement_view_318', 'tests.test_current_settlement_modes_view_362', 'tests.test_current_settlement_integration_318', 'tests.test_current_boss_documents_view_369', 'tests.test_player_scene_battle_395', 'tests.test_branch_layout_review']
with TemporaryDirectory(prefix='rouge-state-suite-')as folder,ExitStack()as stack:
 root=Path(folder)
 for key,path in {'ROOT':root,'SETTINGS':root/'settings.json','RUN_STATE':root/'run.json','OPERATOR_STATE':root/'account.json'}.items():stack.enter_context(patch.object(a,key,path))
 backend=a.DesktopBackend
 stack.enter_context(patch.object(a,'list_game_windows',return_value=[]))
 for name in ('connect','capture','next_frame'):stack.enter_context(patch.object(a.GameCapture,name,side_effect=fail(name)))
 for name in ('start','request'):stack.enter_context(patch.object(backend,name,side_effect=fail(name)))
 for owner,name in ((a,'stream_chat'),(a,'read_key'),(public_archive,'fetch'),(public_node_statistics,'fetch')):stack.enter_context(patch.object(owner,name,side_effect=fail(name)))
 suite=unittest.TestLoader().loadTestsFromNames(modules)
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 assert not forbidden,forbidden
 out=R/'verification/maintenance/compact-battle-review-20261031/tests';out.mkdir(exist_ok=True)
 (out/'results.json').write_text(json.dumps({'passed':result.wasSuccessful(),'tests_run':result.testsRun,'failed':len(result.failures),'errors':len(result.errors),'skipped':[{'test':str(t),'reason':r}for t,r in result.skipped],'selectors':modules,'qpa':qt.platformName(),'forbidden_external_calls':forbidden,'temporary_state_only':True},ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(0 if result.wasSuccessful()else 1)

