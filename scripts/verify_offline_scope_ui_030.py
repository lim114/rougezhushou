"""Isolated Qt check: withdrawn controls never appear; stable controls remain."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from rouge.offline_scope import partition


def main():
    with tempfile.TemporaryDirectory() as folder:
        isolated=Path(folder)
        module.RUN_STATE=isolated/'run.json';module.OPERATOR_STATE=isolated/'operators.json';module.SETTINGS=isolated/'settings.json'
        backend=module.DesktopBackend
        module.DesktopBackend=lambda _path,callback:backend(isolated/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        def select(rids):
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item=window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in rids else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False);window.calculate()
            assert window.damage_result,window.damage_text.toPlainText()
        try:
            assert not window.auto.isChecked() and window.capture.target is None
            assert not hasattr(window,'received_sp_scenario')
            window.auto_relics.setChecked(False)
            refs=[]
            for rid,entry in module.mechanics()['relics'].items():
                a,r,p,rp=partition(entry,rid)
                if (r or rp) and not(a or p):refs.append(rid)
            skills=0
            for op,profile in module.catalog()['operators'].items():
                for skill in range(1,len(profile['skills'])+1):
                    window.operator.setCurrentIndex(window.operator.findData(op))
                    window.skill.setCurrentIndex(window.skill.findData(skill));select(refs)
                    assert not window.damage_form.isRowVisible(window.relic_context),(op,skill)
                    assert '事件技力（局外情景）' not in window.damage_text.toPlainText()
                    assert '藏品效果资料' in window.damage_text.toPlainText()
                    for owner,key,supported,widget in window.model_option_widgets:
                        assert window.damage_form.isRowVisible(widget)==(owner==op and skill in supported),(op,skill,key)
                    # Excluded tank callback binding must not be offered as a calculation option.
                    offered={window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(window.target_buff_list.count())}
                    assert 'rogue_6_from_relic_4' not in offered
                    skills+=1
            window.operator.setCurrentIndex(window.operator.findData('mechanist'))
            window.skill.setCurrentIndex(window.skill.findData(3));select({'rogue_6_relic_fight_11'})
            assert not window.damage_form.isRowVisible(window.relic_context)
            assert '藏品部署费用参考' in window.damage_text.toPlainText()
            assert '本次事件前当前生命参考' not in window.damage_text.toPlainText()
            select({'rogue_6_relic_cargo_11'})
            assert window.damage_form.isRowVisible(window.relic_context)
            window.relic_context.setPlainText('{"fire_rod_stacks":3}')
            assert window.damage_result and window.damage_result['scenario']['relic_context']['fire_rod_stacks']==3
            select({'rogue_6_relic_fight_6'})
            assert not window.damage_form.isRowVisible(window.relic_context)
            assert not window.damage_result['scenario']['relic_context']
            assert 'fire_rod_stacks' not in json.dumps(window.run.state)
            assert not window.desktop.process and not window.auto.isChecked()
            assert skills==87
            receipt={'version':'0.30.0','verified_at':time.time(),'skills_checked':skills,
                'reference_items_checked_together':len(refs),'event_input_removed':True,
                'unrelated_native_options_hidden':True,'native_defensive_skill_option_preserved':True,
                'stable_count_option_preserved':True,'mixed_cost_without_hp_loss':True,
                'temporary_conditions_not_saved':True,'private_data_isolated':True,'chat_requests':0,'game_actions':0,
                'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                    ('rouge/app.py','rouge/offline_scope.py','rouge/reporting.py', 'scripts/verify_offline_scope_ui_030.py')}}
            (ROOT/'UI_0.30_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps(receipt,ensure_ascii=False))
        finally:
            window.close();app.processEvents()


if __name__=='__main__':main()
