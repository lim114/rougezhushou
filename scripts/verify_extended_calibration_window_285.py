"""Actual isolated Windows panel/skills import fixture285; promote before run."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import traceback

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt)
    if destination.exists():
        raise FileExistsError('Preserve the original receipt; choose another path.')
    before = {}
    completed = []
    observations = []

    def write(data):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError('A previous actual receipt must not be overwritten.')
        destination.write_bytes((json.dumps(data, ensure_ascii=False, indent=2)+'\n').encode('utf8'))

    def failure(error):
        return {'passed': False, 'failure': {'type': type(error).__name__, 'message': str(error),
                                           'traceback': traceback.format_exc()},
                'completed_checks': completed, 'public_observations': observations,
                'loaded_source_sha256': before, 'private_state_read': False,
                'temporary_state_root': True, 'game_operated': False, 'game_captures': 0, 'chat_sent': False}

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Actual Windows required; compatibility/offscreen is not equivalent.')
        if Path(__file__).resolve() != (ROOT/'scripts/verify_extended_calibration_window_285.py').resolve():
            raise RuntimeError('Promote the reviewed draft to scripts/ before running.')
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QApplication
        from rouge import app as app_module
        from rouge.damage import calculate_damage
        from rouge.offline_tools_view import public_payload, run_offline_query, PRODUCT_QUERIES, QUERIES
        from rouge.panel_native_finalization import source_data

        source = source_data()
        if source is None:
            raise RuntimeError('Unbound panel source.')
        files = {'rouge/app.py','rouge/calibration.py','rouge/offline_tools_view.py','rouge/information_scope.py',
                 'rouge/damage.py','rouge/operator_engine.py','rouge/panel_native_bridge.py',
                 'rouge/panel_native_finalization.py','rouge/panel_native_precision.py',
                 'rouge/data/catalog.json','rouge/animation_reference.py','rouge/relics.py',
                 'tests/test_extended_calibration_285.py','scripts/verify_extended_calibration_window_285.py'}
        files.update(source['files'])
        packet = ROOT/'research/p2-panel-native-finalization-283'
        files.update(p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file())
        before = {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(files)}
        gui = QApplication([])
        if gui.platformName() != 'windows':
            raise RuntimeError('Actual Windows QPA required.')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-285-extended-calibration-') as state:
            temp = Path(state)
            app_module.ROOT = temp
            app_module.SETTINGS = temp/'settings.json'
            app_module.OPERATOR_STATE = temp/'operators.json'
            app_module.RUN_STATE = temp/'run.json'
            w = PublicWindow()
            w.resize(1500, 1080)
            w.setWindowTitle('第285节 · 当前干员四层与全部技能 · 声明参考')
            w.show()
            panel = w.offline_tools
            w.centralWidget().setCurrentWidget(panel)
            phases = [('char_151_myrtle','panel'),('char_151_myrtle','skills'),
                      ('char_151_myrtle','locked-skills'),('char_1050_chen3','panel'),('char_1050_chen3','skills')]
            index = [0]
            elapsed = [0]
            checked = [False]
            failed = [False]
            payload = [None]
            main_operator = [None]

            def isolated():
                assert w.isVisible() and not w.auto.isChecked() and not w.timer.isActive()
                assert w.capture.target is None and w.desktop.process is None

            def snapshot():
                return (panel.current_query(),panel.editor.toPlainText(),deepcopy(panel.result_snapshot()),
                        panel.result_view.toHtml(),panel.raw_result.toPlainText(),panel.technical.isChecked(),
                        panel.editor.verticalScrollBar().value(),panel.result_view.verticalScrollBar().value(),
                        panel.raw_result.verticalScrollBar().value())

            def choose_main(operator):
                previous = snapshot()
                had_result = panel.result_snapshot() is not None
                assert w.select_operator(operator)
                assert w.operator.currentData() == operator
                n = w.skill.findData(2)
                assert n >= 0
                w.skill.setCurrentIndex(n)
                w.calculate()
                gui.processEvents()
                assert w.damage_result is not None,w.damage_text.toPlainText()
                assert w.damage_result['scenario']['operator'] == operator
                assert w.damage_result['scenario']['skill'] == 2
                assert panel._scenario['operator'] == operator
                if had_result:
                    assert snapshot() == previous
                    completed.append('main_context_changed_without_overwriting_existing_tool_view')
                main_operator[0] = operator

            def begin():
                try:
                    operator, command = phases[index[0]]
                    if main_operator[0] != operator:
                        choose_main(operator)
                    panel.select_query('calibration','skills' if command == 'locked-skills' else command)
                    gui.processEvents()
                    if command == 'locked-skills':
                        declared = {'scenario': {'operator':operator,'skill':1,'elite':0,'level':1,'skill_rank':7},
                                    'operators':[operator]}
                    else:
                        assert panel.import_scenario.isEnabled()
                        panel.import_scenario.click()
                        declared = json.loads(panel.editor.toPlainText())
                        assert declared['scenario']['operator'] == operator
                        assert declared['scenario']['skill'] == 2
                        assert not any(str(k).startswith('_') for k in declared['scenario'])
                        if command == 'skills':
                            assert declared['operators'] == [operator]
                        else:
                            assert 'operators' not in declared
                    payload[0] = deepcopy(declared)
                    panel.editor.setPlainText(json.dumps(declared,ensure_ascii=False,indent=2)+'\n'*80)
                    assert panel.result_snapshot() is None
                    panel.run_button.click()
                    elapsed[0] = 0
                    QTimer.singleShot(100, check)
                except BaseException as error:
                    checked[0] = True;failed[0] = True
                    write(failure(error));w.close();gui.exit(1)

            def validate_native(native):
                assert native['source_valid'] is True and len(native['fields']) == 17
                assert Counter(r['phase'] for r in native['fields']) == {'cultivation':5,'rune':5,'normal':5,'skill':2}
                assert native['complete_native_panel'] is False and native['actual_panel'] is None
                assert all(r['actual_getter_raw'] is None and r['actual_decoded_value'] is None
                           and r['complete_native_value'] is False for r in native['fields'])

            def check():
                try:
                    if panel._workers:
                        elapsed[0] += 100
                        if elapsed[0] > 20000:
                            raise TimeoutError('The actual imported panel/skills query stalled.')
                        QTimer.singleShot(100,check)
                        return
                    operator, command = phases[index[0]]
                    actual_command = 'skills' if command == 'locked-skills' else command
                    data = panel.result_snapshot()
                    assert data is not None,panel.status.text()
                    assert data == run_offline_query('calibration',actual_command,payload[0])
                    assert data['selected_operator']['key'] == operator and data['native_verified'] is False
                    text = panel.result_view.toPlainText()
                    observed = {'operator':operator,'command':command,'same_main_native':True}
                    if command == 'panel':
                        native = data['native_panel_reference'];validate_native(native)
                        assert native == w.damage_result['result']['panel_native_finalization']
                        assert data['panels']['已覆盖常态天赋与效果'] == w.damage_result['result']['estimate']['base_stats']
                        assert '同一主结果 · 原生算式与精度核验' in text
                        if operator == 'char_1050_chen3':
                            row = next(r for r in native['fields'] if r['phase']=='skill' and r['field']=='attack')
                            assert row['references']['input_fp_raw'] is None and row['conditional_complete'] is False
                            assert row['primitive_qualification']['reason']
                            observed['post_slash_attack_qualification_unknown'] = True
                    else:
                        expected_numbers = [1,2] if operator == 'char_151_myrtle' else [1,2,3]
                        assert [r['skill'] for r in data['rows']] == expected_numbers
                        assert all(r['operator_key']==operator for r in data['rows'])
                        assert data['selection_mode'] == 'explicit_current_operator'
                        assert '当前条件归属：' in text
                        if command == 'locked-skills':
                            first,second = data['rows']
                            assert first['unlocked'] is True and second['unlocked'] is False
                            assert second['native_panel_reference'] is None
                            assert second['full_skill_damage'] is None and second['full_skill_healing'] is None
                            assert second['unlock_reasons'] and '培养条件未开放' in text
                            observed['locked_row_not_given_native_result'] = True
                        for row in data['rows']:
                            assert row['native_verified'] is False and row['native_clock_verified'] is False
                            if not row['unlocked']:
                                continue
                            native = row['native_panel_reference'];validate_native(native)
                            declared = deepcopy(payload[0]['scenario']);declared['skill'] = row['skill']
                            assert native == calculate_damage(declared)['panel_native_finalization']
                            assert row['full_skill_damage'] is None and row['full_skill_healing'] is None
                            if operator == 'char_1050_chen3' and row['skill'] == 2:
                                atk = next(r for r in native['fields'] if r['phase']=='skill' and r['field']=='attack')
                                assert atk['references']['input_fp_raw'] is None and atk['primitive_qualification']['reason']
                        observed['skill_numbers'] = expected_numbers
                        assert '对应主结果 · 技能攻击与攻速' in text
                    panel.technical.setChecked(True)
                    gui.processEvents()
                    for widget in (panel.editor,panel.result_view,panel.raw_result):
                        bar = widget.verticalScrollBar()
                        assert bar.maximum()>0,'Actual nonzero scroll required before asserting preservation.'
                        bar.setValue(max(1,bar.maximum()//2))
                    saved = snapshot()
                    # Only the available import context changes. Neither this
                    # update nor restoring the real main context is an import.
                    panel.set_scenario({'operator':'mechanist','skill':1})
                    gui.processEvents()
                    assert snapshot() == saved and panel.import_scenario.isEnabled()
                    panel.set_scenario(deepcopy(w.damage_result['scenario']))
                    gui.processEvents()
                    assert snapshot() == saved
                    observed['refresh_preserved_nonzero_scroll_input_result_selection'] = True
                    observed['scroll_values'] = list(saved[-3:])
                    observations.append(observed)
                    completed.append(operator+'/'+command)
                    isolated()
                    index[0] += 1
                    if index[0] < len(phases):
                        QTimer.singleShot(200,begin)
                        return
                    default = run_offline_query('calibration','skills',public_payload('calibration','skills'))
                    assert default['selection_mode'] == 'legacy_first_three' and len(default['rows']) == 9
                    assert len(QUERIES['calibration'])+len(QUERIES['battle']) == 37
                    assert len(PRODUCT_QUERIES['exploration']) == 9 and len(QUERIES['exploration']) == 13
                    after = {f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in sorted(files)}
                    assert before == after
                    report = {'passed':True,'qpa':gui.platformName(),'visible':True,
                              'query_family':'calibration','queries':['panel','skills'],
                              'public_observations':deepcopy(observations),'completed_checks':completed,
                              'actual_main_context_import_exercised':True,
                              'myrtle_own_two_skills_and_chen_own_three_skills':True,
                              'chen_post_slash_attack_keeps_unknown_qualification':True,
                              'locked_skill_name_reason_without_native_result':True,
                              'legacy_public_default_nine_skills_preserved':True,
                              'refresh_preserves_nonzero_scroll_and_edited_input_result_selection':True,
                              'scenario_import_enabled_and_explicit':True,
                              'main_result_native_reference_reused_exactly':True,
                              'calibration_and_battle_queries':37,'exploration_product_queries':9,
                              'historical_exploration_queries':13,'loaded_source_sha256':before,
                              'source_sha256_after':after,'private_state_read':False,'temporary_state_root':True,
                              'game_operated':False,'game_captures':0,'chat_sent':False,
                              'new_native_primary_readback_performed_by_window':False,
                              'new_native_fresh_methods_claimed':0,'new_native_fresh_spans_claimed':0,
                              'scope':'Actual public Windows existing panel/skills adapter, imports and view state. Shared declared skill rank is a preview condition; no actual per-skill mastery, native clock, active inventory or complete total is certified.'}
                except BaseException as error:
                    report = failure(error);failed[0] = True
                checked[0] = True
                write(report)
                if failed[0]:
                    w.close();gui.exit(1)

            def close():
                if not checked[0]:
                    write(failure(TimeoutError('Window closed before all imported queries finished.')))
                    checked[0] = True;failed[0] = True
                w.close()

            QTimer.singleShot(500,begin)
            QTimer.singleShot(max(30000,args.visible_ms),close)
            code = gui.exec()
            if not checked[0] and not destination.exists():
                write(failure(RuntimeError('The actual window exited before verification completed.')))
                failed[0] = True
            return 1 if failed[0] else code
    except BaseException as error:
        if not destination.exists():
            write(failure(error))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
