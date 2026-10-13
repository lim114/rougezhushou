import json,sys,tempfile,traceback,time
from pathlib import Path
ROOT=Path(r'Z:\workspace\rougezhushou');sys.path.insert(0,str(ROOT))
OUT=ROOT/'verification/full-245/new-window';OUT.mkdir(parents=True,exist_ok=True)
record={'platform':'Windows binaries under Wine','native_windows_verified':False,'game_captures':0,'chat_requests':0,'private_state_isolated':True,'passed':False,'checks':[],'scope':'actual current MainWindow workflow additions 238–245; independent of preserved legacy831 assertions'}
window=None
try:
 from PySide6.QtWidgets import QApplication
 import win32gui
 import rouge.app as module
 with tempfile.TemporaryDirectory() as folder:
  tmp=Path(folder);module.RUN_STATE=tmp/'run.json';module.OPERATOR_STATE=tmp/'operators.json';module.SETTINGS=tmp/'settings.json'
  backend=module.DesktopBackend;module.DesktopBackend=lambda path,callback:backend(tmp/'chat',callback)
  qt=QApplication([]);window=module.MainWindow();window.show();qt.processEvents();tabs=window.centralWidget()
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
  assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
  window.close();qt.processEvents();window=None
 record['passed']=True
except BaseException as exc:record['failure']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
finally:
 if window is not None:window.close()
 (OUT/'window.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,ensure_ascii=False));sys.exit(0 if record['passed'] else 1)
