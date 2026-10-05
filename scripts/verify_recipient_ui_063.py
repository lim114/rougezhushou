"""Exercise same-run recipient evidence through the actual offline Qt UI."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT));sys.path.insert(0, str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow, module, QApplication, Qt
from tests.test_recipient_lifecycle_063 import OWNER, COOKIE, COOKIE_BUFF, SNACK, SNACK_BUFF, full_bar, popup, member
from rouge.run_state import RunState


def sources():
    paths = [*(ROOT/'rouge').rglob('*.py'), *(ROOT/'rouge/data').rglob('*.json'),
             Path(__file__), ROOT/'scripts/verify_relic_ui_025.py', ROOT/'tests/test_recipient_lifecycle_063.py']
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def main():
    before = sources();checks = []
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        module.RUN_STATE=folder/'run.json';module.OPERATOR_STATE=folder/'operators.json';module.SETTINGS=folder/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(folder/'chat',callback)
        app=QApplication([]);window=OfflineWindow()
        try:
            window.auto_relics.setChecked(True);window.use_run_training.setChecked(True)
            at=window.run.state['started_at']+1
            def apply(observed):
                nonlocal at
                assert window.apply_run_observation(observed,at)
                at+=1
            def result():
                window.calculate();assert window.damage_result,window.damage_text.toPlainText()
                return window.damage_result['result']
            def binding(rid):
                return next(row['recipient_binding']['state'] for row in result()['relic_resolution']['records'] if row['id']==rid)
            apply(full_bar(SNACK))
            apply({'operators':[popup(fields={'elite':2,'level':90,'potential':1,'trust':100,'module_id':None,'module_level':0},
                                        skill_ranks={'1':10,'2':10,'3':10})], 'selected_operator':OWNER})
            window.select_operator(OWNER);window.skill.setCurrentIndex(window.skill.findData(3))
            assert binding(SNACK)=='absent'
            assert '已核对：无个人强化' in window.target_buff_status.text()
            checks.append('initial_complete_negative_list')
            apply(full_bar(SNACK,COOKIE))
            assert binding(COOKIE)=='unknown' and binding(SNACK)=='absent'
            assert result()['estimate']['skill']['sp_recovery_per_second']==1
            assert '幸运饼干归属待更新' in window.target_buff_status.text()
            assert '已核对：无个人强化' not in window.target_buff_status.text()
            checks.append('new_cookie_invalidates_only_cookie_absence')
            saved=copy.deepcopy(window.run.state)
            window.target_buff_test.setChecked(True)
            item=next(window.target_buff_list.item(i) for i in range(window.target_buff_list.count())
                      if window.target_buff_list.item(i).data(Qt.ItemDataRole.UserRole)==SNACK_BUFF)
            item.setCheckState(Qt.CheckState.Checked)
            assert result()['estimate']['skill']['sp_cost']==28
            assert SNACK_BUFF not in window.damage_result['scenario']['char_buff_absent_ids']
            assert window.run.state==saved
            checks.append('manual_test_overrides_negative_without_mutating_run')
            window.target_buff_test.setChecked(False)
            assert result()['estimate']['skill']['sp_cost']==35 and binding(SNACK)=='absent'
            checks.append('manual_test_exit_restores_current_evidence')
            apply(full_bar(SNACK))
            assert result()['relic_resolution']['recipient_evidence_pending']==[COOKIE_BUFF]
            assert not result()['estimate']['complete']
            assert '幸运饼干' in window.damage_text.toPlainText()
            checks.append('lost_parent_preserves_unresolved_recipient_in_calculation_and_ui')
            apply(full_bar(SNACK,COOKIE))
            apply({'operators':[popup([COOKIE_BUFF])], 'selected_operator':OWNER})
            assert binding(COOKIE)=='confirmed' and binding(SNACK)=='absent'
            assert result()['estimate']['skill']['sp_recovery_per_second']==1.8
            assert '归属待更新' not in window.target_buff_status.text()
            checks.append('fresh_complete_popup_resolves_cookie_and_clears_pending_label')
            history=copy.deepcopy(window.run.state['history']);identity=window.run.state['id']
            window.run=RunState(module.RUN_STATE);window.sync_run_relics();window.update_operator()
            assert binding(COOKIE)=='confirmed'
            assert window.run.state['id']==identity and window.run.state['history']==history
            checks.append('restart_preserves_positive_negative_and_history')
            apply({'operators':[member()]})
            assert binding(COOKIE)=='confirmed' and binding(SNACK)=='absent'
            assert window.run.state['history']==history
            checks.append('ordinary_page_reuses_evidence_without_history_growth')
            window.use_run_training.setChecked(False)
            result()
            assert window.damage_result['scenario']['char_buff_absent_ids']==[]
            assert window.damage_result['scenario']['char_buff_ids']==[]
            assert binding(COOKIE)=='unknown'
            checks.append('account_preview_does_not_inherit_run_recipient_evidence')
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            assert sources()==before
            receipt={'version':'0.63.0','passed':True,'checks':checks,'source_sha256':before,
                     'source_stable':True,'private_data_isolated':True,'synthetic_evidence_sequence':True,
                     'live_recognition_verified':False,'game_actions':0,'chat_requests':0}
            with (ROOT/'RECIPIENT_UI_0.63_VERIFICATION.json').open('x',encoding='utf-8') as stream:
                json.dump(receipt,stream,ensure_ascii=False,indent=2)
            print(json.dumps({'passed':True,'checks':len(checks)}))
        finally:
            window.close();app.processEvents()


if __name__=='__main__':
    main()
