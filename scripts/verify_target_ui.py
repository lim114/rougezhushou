"""Exercise recipient previews through the public test interface without changing private state."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import sys,tempfile,time,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
import rouge.app as module

with tempfile.TemporaryDirectory() as directory:
    module.RUN_STATE=Path(directory)/'run.json'
    module.OPERATOR_STATE=Path(directory)/'operators.json'
    app=QApplication([]);window=module.MainWindow()
    try:
        def choose(op):window.operator.setCurrentIndex(window.operator.findData(op));window.calculate()
        def visible_ids():return [window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(window.target_buff_list.count())]
        choose('mechanist')
        window.target_buff_test.setChecked(True)
        assert 'rogue_6_from_relic_5' not in visible_ids()
        assert 'rogue_6_from_relic_7' not in visible_ids()
        item=next(window.target_buff_list.item(i) for i in range(window.target_buff_list.count())
                  if window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole)=='rogue_6_from_relic_9')
        item.setCheckState(Qt.CheckState.Checked)
        assert window.damage_result['result']['estimate']['base_stats']['attack_speed']==150
        assert not window.run.state['operators']
        choose('kaltsit')
        assert window.damage_result['result']['estimate']['base_stats']['attack_speed']==100
        choose('mechanist')
        assert window.damage_result['result']['estimate']['base_stats']['attack_speed']==150
        window.target_buff_test.setChecked(False)
        assert window.target_buff_list.isHidden()
        assert window.damage_result['result']['estimate']['base_stats']['attack_speed']==100
        choose('char_133_mm');window.target_buff_test.setChecked(True)
        assert 'rogue_6_from_relic_5' in visible_ids()
        assert 'rogue_6_from_relic_7' not in visible_ids()
        window.target_buff_test.setChecked(False)
        window.run.apply({'relics':{'ids':[],'count':0,'icons':[],'source':'test'},
            'operators':[{'id':'mechanist','scope':'run','fields':{'elite':2,'level':90},
                          'char_buff_ids':['rogue_6_from_relic_9'],'char_buffs_complete':True}]},time.time())
        window.use_run_training.setChecked(True);choose('mechanist')
        assert window.damage_result['scenario']['char_buff_ids']==['rogue_6_from_relic_9']
        assert window.damage_result['result']['estimate']['base_stats']['attack_speed']==150
        assert '疗养礼品卡' in window.target_buff_status.text()
        window.reset_run_button.click()
        assert window.damage_result['scenario']['char_buff_ids']==[]
        assert not window.target_buff_test.isChecked()
        assert not window.target_buff_previews
        receipt={'verified_at':time.time(),'recipient_preview_scoped_to_operator':True,
                 'incompatible_options_absent':True,'previews_never_written_to_run_memory':True,
                 'preview_toggle_off_uses_confirmed_state':True,'confirmed_binding_enters_calculation':True,
                 'manual_reset_clears_bindings_and_previews':True,'chat_requests':0,
                 'automatic_recipient_capture_verified':False}
        (ROOT/'TARGET_UI_VERIFICATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
        print(json.dumps(receipt))
    finally:window.close()
