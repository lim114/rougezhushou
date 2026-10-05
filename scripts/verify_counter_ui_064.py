"""Temporary evidence -> persistence -> actual Qt calculation, no game input."""
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
from verify_relic_ui_025 import OfflineWindow, module, QApplication
from tests.test_counter_semantics_054 import CounterSemanticsTests
from tests.test_recipient_lifecycle_063 import full_bar
from rouge.relic_counter_semantics import counter_resources, COUNTER_BINDINGS
from rouge.run_state import RunState


def sources():
    paths = [*(ROOT/'rouge').rglob('*.py'), *(ROOT/'rouge/data').rglob('*.json'),
             Path(__file__), ROOT/'scripts/verify_relic_ui_025.py',
             ROOT/'tests/test_counter_semantics_054.py', ROOT/'tests/test_recipient_lifecycle_063.py']
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def main():
    before=sources();checks=[]
    with tempfile.TemporaryDirectory() as directory:
        folder=Path(directory)
        module.RUN_STATE=folder/'run.json';module.OPERATOR_STATE=folder/'operators.json';module.SETTINGS=folder/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(folder/'chat',callback)
        app=QApplication([]);window=OfflineWindow();at=window.run.state['started_at']+1
        try:
            window.auto_relics.setChecked(True);window.use_run_training.setChecked(False)
            window.select_operator('mechanist');window.skill.setCurrentIndex(window.skill.findData(3))
            window.frame_timing.setChecked(False)
            window.target_stage_choices.select_value('ro6_n_1_2')
            target=next(window.target_enemy.itemData(i) for i in range(window.target_enemy.count())
                if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_2137_shsdgo')
            window.target_enemy_choices.select_value(target)
            def apply(observed):
                nonlocal at
                assert window.apply_run_observation(observed,at);at+=1
            def evidence(rid,value):
                return {**full_bar(rid),'resources':counter_resources([CounterSemanticsTests().proof(rid,value)])}
            def result():
                window.calculate();assert window.damage_result,window.damage_text.toPlainText()
                return window.damage_result['result']
            def context():
                result();return window.damage_result['scenario']['relic_context']
            altar='rogue_6_relic_legacy_103'
            apply(evidence(altar,5));assert context()['altar_stacks']==5
            first=copy.deepcopy(window.run.state['resources']['altar_stacks'])
            apply(full_bar());apply(full_bar(altar))
            assert 'altar_stacks' not in context(), 'Old held count must not cross a confirmed loss/reacquisition'
            assert window.run.state['resources']['altar_stacks']==first
            assert '当前层数待确认' in window.run.summary()
            assert not result()['relic_resolution']['complete']
            checks.append('loss_reacquisition_withholds_old_value_without_deleting_history')
            window.run=RunState(module.RUN_STATE);window.sync_run_relics()
            assert 'altar_stacks' not in context()
            checks.append('restart_keeps_count_uncertain')
            saved=copy.deepcopy(window.run.state)
            window.relic_context.setPlainText('{"altar_stacks":2}')
            assert context()['altar_stacks']==2 and window.run.state==saved
            window.relic_context.clear();assert 'altar_stacks' not in context()
            checks.append('manual_preview_isolated_from_run_and_clears_on_exit')
            # Every verified binding crosses storage/restart, the UI scenario,
            # the real numerical resolver and the visible report. No new OCR
            # result or recipient is invented by these constructed sequences.
            for rid,(key,_,maximum) in COUNTER_BINDINGS.items():
                for value in (0,1,maximum):
                    apply(evidence(rid,value))
                    window.run=RunState(module.RUN_STATE);window.sync_run_relics()
                    assert window.run.state['resources'][key]['value']==value
                    assert context()[key]==value,(key,value,context())
                    record=next(r for r in result()['relic_resolution']['records'] if r['id']==rid)
                    if key=='mercenary_stacks':
                        assert 'mercenary_recipient' not in context()
                        assert 'mercenary_recipient' in record['missing_conditions']
                        saved=copy.deepcopy(window.run.state)
                        window.relic_context.setPlainText('{"mercenary_recipient":1}')
                        record=next(r for r in result()['relic_resolution']['records'] if r['id']==rid)
                        assert all(e['value']==.05*value for e in record['applied'])
                        assert window.run.state==saved
                        window.relic_context.clear()
                    elif key=='altar_stacks':
                        assert all(e['value']==.05*value for e in record['applied'])
                    elif key=='fire_rod_stacks':
                        assert result()['estimate']['base_stats']['attack_speed_reference']==100+10*value
                        assert result()['estimate']['base_stats']['attack_speed']==min(600,100+10*value)
                        assert any(e['value']==10*value and e['kind']=='attack_speed' for e in record['applied'])
                    elif key=='probe_stacks':
                        enemy=result()['run_resolution']['enemy']['stats']
                        assert abs(enemy['maxHp']-18000*(1+.2*value))<1e-7
                        assert abs(enemy['atk']-280*(1+.2*value))<1e-7
                    elif key=='grudge_stacks':
                        assert any(e['value']==.002*value and e['condition']==key for e in record['applied'] if 'condition' in e)
                    assert record['name'] in window.damage_text.toPlainText()
                    checks.append(f'{key}_{value}_persisted_to_ui_calculation')
            apply(evidence(altar,2));assert context()['altar_stacks']==2
            saved=copy.deepcopy(window.run.state['resources']['altar_stacks'])
            apply({'operators':[]});assert context()['altar_stacks']==2
            assert window.run.state['resources']['altar_stacks']==saved
            checks.append('ordinary_partial_page_preserves_same_possession_counter')
            window.run.reset();window.sync_run_relics();result()
            assert not window.run.state['resources'] and not context()
            checks.append('temporary_manual_new_run_has_no_previous_counter')
            assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
            assert sources()==before
            receipt={'version':'0.64.0','passed':True,'checks':checks,'source_sha256':before,
                     'source_stable':True,'private_data_isolated':True,'synthetic_evidence_sequence':True,
                     'live_recognition_verified':False,'game_actions':0,'chat_requests':0}
            with (ROOT/'COUNTER_UI_0.64_VERIFICATION.json').open('x',encoding='utf-8') as stream:
                json.dump(receipt,stream,ensure_ascii=False,indent=2)
            print(json.dumps({'passed':True,'checks':len(checks)}))
        finally:
            window.close();app.processEvents()


if __name__=='__main__':main()
