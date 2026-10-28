import argparse,faulthandler,hashlib,json,sys,tempfile,traceback,time
faulthandler.enable(all_threads=True)
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=next(path for path in [HERE,*HERE.parents] if (path/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE/'evidence');parser.add_argument('--revision',default='unlabeled frozen working tree');args=parser.parse_args()
OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
FREEZE_SHA256='75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0'
assert hashlib.sha256((HERE/'source-freeze.json').read_bytes()).hexdigest()==FREEZE_SHA256
FREEZE=json.loads((HERE/'source-freeze.json').read_text(encoding='utf-8'))
def source_hashes():
 return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FREEZE['source_sha256']}
source_before=source_hashes()
record={'platform':'Actual current native Windows Qt fixture; original Windows history remains unverified','native_windows_verified':False,'game_captures':0,'chat_requests':0,'private_state_isolated':True,'passed':False,'checks':[],'scope':'261 maintenance recheck of all29 actual MainWindow238–260 workflows; no new UI feature or replacement of legacy52 saved-state scope', 'head_label':args.revision,'source_sha256_before':source_before,'added_section_checks':[]}
record['source_freeze_sha256']=FREEZE_SHA256
record['frozen_source_binding_matches']=source_before==FREEZE['source_sha256']
record['verification_scripts_sha256']={path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in HERE.glob('window*.py')}
# BEGIN EXPLICIT NATIVE275 HISTORICAL FIXTURE CONSTRUCTOR
import native275_bootstrap as _native275_bootstrap
_native275_restore, _native275_write = _native275_bootstrap.install(ROOT, OUT)
# END EXPLICIT NATIVE275 HISTORICAL FIXTURE CONSTRUCTOR

window=None;qt=None
def mark(section,name):
 record['checks'].append(str(section)+' '+name);record['added_section_checks'].append({'section':str(section),'name':name})
def save_result(section,result):
 (OUT/('section-'+str(section)+'-result.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
try:
 assert record['frozen_source_binding_matches'], 'Current source does not match exact261 freeze'
 from PySide6.QtWidgets import QApplication
 import win32gui
 import rouge.app as module
 with tempfile.TemporaryDirectory() as folder:
  tmp=Path(folder);module.RUN_STATE=tmp/'run.json';module.OPERATOR_STATE=tmp/'operators.json';module.SETTINGS=tmp/'settings.json'
  backend=module.DesktopBackend;module.DesktopBackend=lambda path,callback:backend(tmp/'chat',callback)
  qt=QApplication([]);window=module.MainWindow();window.resize(1500,1000);window.show();qt.processEvents();tabs=window.centralWidget()
  record['qt_platform']=qt.platformName();assert record['qt_platform']=='windows'
  assert all(Path(getattr(module,name)).is_relative_to(tmp) for name in ['RUN_STATE','OPERATOR_STATE','SETTINGS'])
  record['actual_desktop_api']='real installed win32gui';record['actual_runtime_requested']='Native project Windows Python, ownedPopen/job supervisor'
  assert window.isVisible() and win32gui.IsWindowVisible(int(window.winId()))
  assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
  for name in ['paired_calibration','route_constraints','attack_state_sequence','timing_calibration']:
   panel=getattr(window,name);tabs.setCurrentWidget(panel);qt.processEvents()
   assert tabs.currentWidget() is panel and panel.isVisible()
   record['checks'].append('visible actual tab '+name)
  for operator in ['kaltsit','silverash','mechanist']:
   panel=window.timing_calibration;tabs.setCurrentWidget(panel)
   panel.template.setCurrentIndex(panel.template.findData(operator));panel.load_template.click();panel.run_button.click();qt.processEvents()
   result=panel.result_snapshot();assert result is not None
   assert '首次就绪' in panel.result_view.toPlainText()
   record['checks'].append('timing formula event ledger '+operator)
  panel=window.attack_state_sequence;tabs.setCurrentWidget(panel);panel.operator.setCurrentIndex(panel.operator.findData('kaltsit'));panel.load_template.click();panel.calculate_button.click();qt.processEvents()
  assert panel.result_snapshot() is not None
  record['checks'].append('attack-state declaration template and result')
  panel=window.route_constraints;tabs.setCurrentWidget(panel);panel.load_example.click();panel.run_button.click()
  deadline=time.monotonic()+30
  while panel._workers and time.monotonic()<deadline:qt.processEvents();time.sleep(.01)
  assert panel._result is not None and not panel._workers
  record['checks'].append('bounded declared route worker completed in actual window')
  before=window.timing_calibration.observation_editor.toPlainText();window.select_operator('mechanist');window.calculate();qt.processEvents()
  assert window.timing_calibration.observation_editor.toPlainText()==before
  assert window.timing_calibration._scenario['operator']=='mechanist'
  record['checks'].append('calculator refresh retains independent timing record')
  window.select_operator('char_2027_wang');window.skill.setCurrentIndex(window.skill.findData(1));qt.processEvents()
  assert not window.wang_resource_button.isHidden();window.wang_resource_button.click();qt.processEvents()
  assert window.wang_resource_dialog.isVisible();window.wang_resource_dialog.close()
  record['checks'].append('Wang resource dialog opens from actual owner/skill')
  panel=window.battle_preview;panel.set_stage('ro6_duel_2');tabs.setCurrentWidget(panel);panel.duel_reward_button.click();qt.processEvents()
  assert panel.duel_reward_window.isVisible() and panel.duel_reward_window.stage.currentData()=='ro6_duel_2'
  panel.duel_reward_window.close();record['checks'].append('duel tier window actual battle entry')
  panel=window.node_catalog;tabs.setCurrentWidget(panel);index=next(i for i,e in enumerate(panel.entries) if e['kind']=='event' and e['record']['id']=='community_group_025')
  panel.list.setCurrentRow(index);panel.exchange_button.click();qt.processEvents();assert panel.exchange_window.isVisible()
  panel.exchange_window.offered.setCurrentIndex(panel.exchange_window.offered.findData('rogue_6_scrap_M_01'));qt.processEvents()
  assert len(panel.exchange_window.result['documented_candidates'])==9
  assert panel.exchange_window.grab().save(str(OUT/'exchange.png'));panel.exchange_window.close()
  record['checks'].append('exchange event entry and complete nine-candidate pool')
  tabs.setCurrentWidget(window.timing_calibration);qt.processEvents();assert window.grab().save(str(OUT/'main-timing.png'))
  from window_added_flows import run_added_flows,check_global_preservation
  from window_extra_flows import run_extra_flows
  frozen_run_state=json.dumps(window.run.state,sort_keys=True,ensure_ascii=False)
  run_added_flows(window,qt,mark,save_result,OUT)
  run_extra_flows(window,qt,mark,save_result,OUT)
  check_global_preservation(window,qt,mark)
  assert json.dumps(window.run.state,sort_keys=True,ensure_ascii=False)==frozen_run_state
  expected={str(section) for section in range(246,261)}
  assert expected <= {row['section'] for row in record['added_section_checks']}
  record['new_sections_covered']=sorted(int(section) for section in expected)
  assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
  record['run_memory_unchanged_by_added_flows']=True
  record['maintenance261_safe_save_check']=False
  record['maintenance261_symlink_specialization']='unavailable: actual same-kind native Windows probe returned WinError1314'
  record['original30_full_script_retained_and_required']=True
  window.close();qt.processEvents();window=None
 record['passed']=True
except BaseException as exc:record['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
finally:
 try:
  if window is not None:window.close()
  if qt is not None:
   from PySide6.QtCore import QCoreApplication,QEvent,QThreadPool
   import shiboken6
   remaining=list(qt.topLevelWidgets())
   assert QThreadPool.globalInstance().waitForDone(5000), 'Qt worker pool unfinished'
   for widget in remaining:widget.close();widget.deleteLater()
   qt.processEvents();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);qt.shutdown()
   record['qt_cleanup']={'application_destroyed':QApplication.instance() is None,'remaining_wrappers_valid':sum(shiboken6.isValid(w) for w in remaining),'top_level_widgets_before_shutdown':len(remaining)}
   assert record['qt_cleanup']['application_destroyed'] and record['qt_cleanup']['remaining_wrappers_valid']==0
 except BaseException as exc:
  record['passed']=False
  record['qt_cleanup_failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
 record['source_sha256_after']=source_hashes();record['source_drift']=[p for p in sorted(set(source_before)|set(record['source_sha256_after'])) if source_before.get(p)!=record['source_sha256_after'].get(p)]
 if record['source_drift'] or record['source_sha256_after']!=FREEZE['source_sha256']:record['passed']=False
 (OUT/'window.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,ensure_ascii=False));sys.exit(0 if record['passed'] else 1)
