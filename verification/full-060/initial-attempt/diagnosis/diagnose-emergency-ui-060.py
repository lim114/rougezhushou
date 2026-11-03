import sys,json,tempfile,hashlib
from pathlib import Path
ROOT=Path(r'Z:\workspace\rougezhushou');OUT=Path(r'Z:\workspace\.compat')
sys.path.insert(0,str(ROOT))
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
import rouge.app as module
from rouge.reporting import format_report
with tempfile.TemporaryDirectory() as folder:
 isolated=Path(folder)
 module.RUN_STATE=isolated/'run.json';module.OPERATOR_STATE=isolated/'operators.json';module.SETTINGS=isolated/'settings.json'
 backend=module.DesktopBackend;module.DesktopBackend=lambda _path,cb:backend(isolated/'chat',cb)
 app=QApplication([]);window=module.MainWindow();window.show();app.processEvents()
 assert window.isVisible() and not window.auto.isChecked() and window.capture.target is None
 window.auto_relics.setChecked(False);window.use_run_training.setChecked(True)
 fields={'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0}
 member={'id':'silverash','scope':'run','present':True,'fields':fields,'skill_ranks':{'1':10,'2':10,'3':10},'recruitment_kind':None,'char_buff_ids':[],'char_buffs_complete':False}
 window.run.state['operators']={'silverash':member};window.operator_observations={'silverash':dict(member,scope='account')}
 window.select_operator('silverash');window.update_operator();window.skill.setCurrentIndex(window.skill.findData(3))
 window.limit_window.setChecked(True);window.window_seconds.setValue(3);window.timing_scenario.clear()
 for i in range(window.relic_list.count()):
  item=window.relic_list.item(i)
  item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole)=='rogue_6_relic_cargo_10' else Qt.CheckState.Unchecked)
 window.calculate();app.processEvents();assert window.damage_result,window.damage_text.toPlainText()
 result=window.damage_result['result'];actual=window.damage_text.toPlainText()
 record=next(r for r in result['relic_resolution']['records'] if r['id']=='rogue_6_relic_cargo_10')
 assert record['missing_conditions']==['emergency_hire'] and record['status']=='incomplete' and not record['applied']
 shot=OUT/'emergency-ui-060-before.png';assert window.grab().save(str(shot))
 receipt={'diagnostic_only':True,'native_windows_verified':False,'private_state_isolated':True,'game_captures':0,'chat_requests':0,'actual_human_text':actual,'technical_text':format_report(result,technical=True),'scenario':window.damage_result['scenario'],'result':result,'window_visible':window.isVisible(),'screenshot':str(shot),'raw_internal_key_visible':'emergency_hire' in actual,'human_source_name_visible':'应急招募来源' in actual,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'rouge/reporting.py',ROOT/'rouge/relics.py',ROOT/'rouge/app.py')}}
 (OUT/'emergency-ui-060-diagnosis.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:receipt[k] for k in ('diagnostic_only','window_visible','raw_internal_key_visible','human_source_name_visible','native_windows_verified')}))
 window.close();app.processEvents()
