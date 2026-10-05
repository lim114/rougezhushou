"""Offline Qt acceptance with independent temporary state and no game target."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from scripts.verify_relic_ui_025 import OfflineWindow, module


def main():
    start=time.perf_counter()
    with tempfile.TemporaryDirectory() as folder:
        isolated=Path(folder)
        module.RUN_STATE=isolated/'run.json'
        module.OPERATOR_STATE=isolated/'operators.json'
        module.SETTINGS=isolated/'settings.json'
        backend=module.DesktopBackend
        module.DesktopBackend=lambda _path,callback:backend(isolated/'chat',callback)
        app=QApplication([])
        window=OfflineWindow()
        def choose(op,skill):
            window.operator.setCurrentIndex(window.operator.findData(op))
            window.skill.setCurrentIndex(window.skill.findData(skill))
            window.calculate()
            assert window.damage_result,window.damage_text.toPlainText()
        def relic(rid=None):
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item=window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole)==rid else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
            window.calculate()
        def binding(bid,checked):
            item=next((window.target_buff_list.item(i) for i in range(window.target_buff_list.count())
                       if window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole)==bid),None)
            assert item,bid
            item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            window.calculate()
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            window.auto_relics.setChecked(False)
            choose('mechanist',3)
            assert not window.damage_form.isRowVisible(window.received_sp_scenario)
            window.target_buff_test.setChecked(True)
            binding('rogue_6_from_relic_4',True)
            assert window.damage_form.isRowVisible(window.received_sp_scenario)
            assert '受到攻击' in window.received_sp_scenario.toolTip()
            text=json.dumps({'initial':[{'at_seconds':t,'type':'attack'} for t in (1,2,3)],
                             'cycle':[{'at_seconds':t,'type':'attack'} for t in (41,42,43)]})
            window.received_sp_scenario.setPlainText(text)
            result=window.damage_result['result']
            assert result['estimate']['skill']['initial_seconds']==4
            assert result['estimate']['skill']['cycle_seconds']==69
            assert '受击技力' in window.damage_text.toPlainText()
            choose('kaltsit',1)
            assert not window.damage_form.isRowVisible(window.received_sp_scenario)
            assert 'rogue_6_from_relic_4' not in [window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole)
                                               for i in range(window.target_buff_list.count())]
            assert 'sp_events' not in window.damage_result['scenario'].get('timing',{})
            choose('mechanist',3)
            assert window.received_sp_scenario.toPlainText()==text
            assert window.damage_result['result']['estimate']['skill']['initial_seconds']==4
            window.target_buff_test.setChecked(False)
            assert not window.damage_form.isRowVisible(window.received_sp_scenario)
            assert 'sp_events' not in window.damage_result['scenario'].get('timing',{})
            relic('rogue_6_relic_legacy_118')
            choose('char_151_myrtle',1)
            assert window.damage_form.isRowVisible(window.received_sp_scenario)
            assert '受到元素损伤' in window.received_sp_scenario.toolTip()
            window.received_sp_scenario.setPlainText('{"initial":[{"at_seconds":1,"type":"damage"}],"cycle":[]}')
            assert window.damage_result['result']['estimate']['skill']['initial_seconds']==8
            window.frame_timing.setChecked(False)
            assert window.damage_result['result']['estimate']['skill']['initial_seconds']==8
            assert 'sp_events' in window.damage_result['scenario']['timing']
            window.frame_timing.setChecked(True)
            choose('char_1029_yato2',1)
            assert not window.damage_form.isRowVisible(window.received_sp_scenario)
            assert 'received_sp' not in [s['id'] for s in window.damage_result['result']['report']['sections']]
            choose('char_1044_hsgma2',1)
            interval=next(widget for owner,key,_,widget in window.model_option_widgets
                          if owner=='char_1044_hsgma2' and key=='incoming_attack_interval')
            assert not window.damage_form.isRowVisible(interval)
            assert 'incoming_attack_interval' not in window.damage_result['scenario']
            relic()
            assert window.damage_form.isRowVisible(interval)
            assert not window.damage_form.isRowVisible(window.received_sp_scenario)
            skills=0
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    choose(op,skill)
                    assert not window.damage_form.isRowVisible(window.received_sp_scenario)
                    for owner,key,supported,widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                    skills+=1
            assert skills==87
            assert not window.desktop.process and not window.auto.isChecked()
            assert not (isolated/'chat').exists()
            state=json.dumps(window.run.state)
            assert 'sp_events' not in state and 'rogue_6_from_relic_4' not in state
            receipt={'version':'0.26.0','verified_at':time.time(),'passed':True,
                'seconds':round(time.perf_counter()-start,3),'skill_option_visibility_cases':skills,
                'tank_binding_only_shows_current_recipient':True,'per_operator_skill_preview_preserved':True,
                'inactive_rule_removes_event_input_and_scenario':True,'bloom_typed_events_and_continuous_mode':True,
                'passive_and_deployment_event_fields_absent':True,
                'native_interval_input_hidden_to_avoid_duplicate_hits':True,'private_state_isolated':True,
                'event_preview_not_saved_to_run':True,'game_captures':0,'chat_requests':0,
                'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                    ('rouge/app.py','rouge/reporting.py','rouge/sp_events.py','rouge/data/relic-mechanics.json')},
                'limits':['Offscreen UI wiring; no new live recipient acquisition or incoming-hit measurement.']}
            (ROOT/'UI_0.26_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps(receipt,ensure_ascii=False))
        finally:
            window.close()
            app.processEvents()


if __name__=='__main__':main()
