"""Execute the two repaired test modules on the explicitly selected Qt backend."""
from pathlib import Path
import argparse,io,json,os,sys,unittest
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
p=argparse.ArgumentParser();p.add_argument('--qpa',choices=['windows','offscreen'],required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
assert sys.platform=='win32'and not a.receipt.exists();os.environ['QT_QPA_PLATFORM']=a.qpa
from player_ui_verification import source_hashes
before=source_hashes();modules=['tests.test_player_compact_389','tests.test_player_feature_416'];suite=unittest.defaultTestLoader.loadTestsFromNames(modules)
def ids(suite):
 for item in suite:
  if isinstance(item,unittest.TestSuite):yield from ids(item)
  else:yield item.id()
selectors=list(ids(suite));assert len(selectors)==5
result=unittest.TextTestRunner(verbosity=2).run(suite)
from PySide6.QtWidgets import QApplication
gui=QApplication.instance();actual_backend=gui.platformName()if gui else None
from qt_verification_cleanup import shutdown_verification_qt
cleanup=shutdown_verification_qt();after=source_hashes()
record={'section':425,'kind':'actual_repaired_unit_modules_backend_execution','modules':modules,'selectors':selectors,'tests_run':result.testsRun,'failures':[{'test':t.id(),'traceback':e}for t,e in result.failures],'errors':[{'test':t.id(),'traceback':e}for t,e in result.errors],'skips':[{'test':t.id(),'reason':e}for t,e in result.skipped],'requested_qpa':a.qpa,'actual_qpa':actual_backend,'source_sha256_before':before,'source_sha256_after':after,'qt_shutdown':cleanup,'entire_7055_suite_rerun_claimed':False,'private_state_copied':False}
expected_skips=['tests.test_player_feature_416.BindingTests.test_owned_native_identity_and_geometry']if a.qpa=='offscreen'else[]
record['passed']=result.wasSuccessful()and result.testsRun==5 and actual_backend==a.qpa and [t.id()for t,_ in result.skipped]==expected_skips and before==after
a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
raise SystemExit(0 if record['passed']else 1)
