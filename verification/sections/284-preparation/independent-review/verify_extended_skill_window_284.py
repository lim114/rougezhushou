"""Actual Windows main damage-page fixture for284; promote before execution.

Only public preview choices and temporary state are used. Calibration remains
limited to its existing first-three scope; no extra query is introduced here.
"""
import argparse
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
        raise FileExistsError('Keep the original actual receipt; use a new destination.')
    before = {}
    observations = []

    def write_report(data):
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            raise FileExistsError('The fixture will not overwrite an existing receipt.')
        destination.write_bytes((json.dumps(data, ensure_ascii=False, indent=2)+'\n').encode('utf8'))

    def failure(error):
        return {'passed': False, 'failure': {'type': type(error).__name__, 'message': str(error),
                                           'traceback': traceback.format_exc()},
                'public_cases_completed': deepcopy(observations), 'loaded_source_sha256': before,
                'private_state_read': False, 'temporary_state_root': True,
                'game_operated': False, 'game_captures': 0, 'chat_sent': False}

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Actual Windows required, not Wine or an offscreen fixture.')
        if Path(__file__).resolve() != (ROOT/'scripts/verify_extended_skill_window_284.py').resolve():
            raise RuntimeError('Promote the reviewed draft to scripts/ before actual execution.')
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication, QCheckBox
        from rouge import app as app_module
        from rouge.damage import calculate_damage
        from rouge.offline_tools_view import run_offline_query, PRODUCT_QUERIES, QUERIES
        from rouge.panel_native_finalization import source_data
        from rouge.reporting import format_report

        source = source_data()
        if source is None:
            raise RuntimeError('Panel native source guard is invalid.')
        files = {'rouge/app.py', 'rouge/operator_engine.py', 'rouge/panel_native_bridge.py',
                 'rouge/panel_native_finalization.py', 'rouge/panel_native_precision.py',
                 'rouge/damage.py', 'rouge/reporting.py', 'rouge/calibration.py',
                 'rouge/offline_tools_view.py', 'rouge/information_scope.py',
                 'rouge/operator_options.py', 'rouge/branch_choice.py', 'rouge/data/catalog.json',
                 'tests/test_extended_skill_native_284.py', 'scripts/verify_extended_skill_window_284.py'}
        files.update(source['files'])
        packet = ROOT/'research/p2-panel-native-finalization-283'
        files.update(p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file())
        before = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(files)}
        gui = QApplication([])
        if gui.platformName() != 'windows':
            raise RuntimeError('Actual Windows QPA required.')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-284-extended-skill-') as state:
            temp = Path(state)
            app_module.ROOT = temp
            app_module.SETTINGS = temp/'settings.json'
            app_module.OPERATOR_STATE = temp/'operators.json'
            app_module.RUN_STATE = temp/'run.json'
            w = PublicWindow()
            w.resize(1500, 1080)
            w.setWindowTitle('第284节 · 扩展干员技能面板 · 字段条件参考')
            w.show()
            tabs = w.centralWidget()
            damage_index = next(i for i in range(tabs.count()) if tabs.widget(i).isAncestorOf(w.damage_text))
            tabs.setCurrentIndex(damage_index)
            # Boolean options are the existing UI controls. This fixture does
            # not inject a prepared native result or change cultivation files.
            cases = [
                ('char_151_myrtle', 2, {}, True, True, None),
                ('char_110_deepcl', 1, {}, False, True, '召唤物技能加攻不能套给本体'),
                ('char_1050_chen3', 2, {}, False, True, '斩击后强化改变攻击'),
                ('char_4182_oblvns', 2, {'organ_mode': False}, False, True, '钢琴模式的额外攻击'),
                ('char_4182_oblvns', 2, {'organ_mode': True}, True, False, '风琴模式的额外攻速'),
            ]
            index = [0]
            checked = [False]
            failed = [False]

            def assert_isolated():
                assert w.isVisible() and not w.auto.isChecked() and not w.timer.isActive()
                assert w.capture.target is None and w.desktop.process is None

            def snapshot():
                cursor = w.damage_text.textCursor()
                return (w.operator_choices.branch.currentData(), w.operator.currentData(), w.skill.currentData(),
                        w.timing_scenario.toPlainText(), w.relic_context.toPlainText(),
                        w.damage_text.toPlainText(), cursor.anchor(), cursor.position(),
                        w.damage_text.verticalScrollBar().value(),
                        deepcopy(w.damage_result['result']['panel_native_finalization']))

            def run_case():
                try:
                    operator, number, options, attack_known, speed_known, phrase = cases[index[0]]
                    assert w.select_operator(operator)
                    assert w.operator.currentData() == operator
                    skill_index = w.skill.findData(number)
                    assert skill_index >= 0, 'Requested public preview skill is not available.'
                    w.skill.setCurrentIndex(skill_index)
                    for key, value in options.items():
                        matches = [widget for owner, name, skills, widget in w.model_option_widgets
                                   if owner == operator and name == key and number in skills]
                        assert len(matches) == 1 and isinstance(matches[0], QCheckBox)
                        matches[0].setChecked(value)
                    # Public zero travel declaration is neutral. The same key
                    # must survive a same-context recalculation/refresh.
                    w.timing_scenario.setPlainText('{\n  "projectile_travel_seconds": 0\n}\n')
                    w.calculate()
                    gui.processEvents()
                    assert w.damage_result is not None, w.damage_text.toPlainText()
                    scenario = deepcopy(w.damage_result['scenario'])
                    result = w.damage_result['result']
                    assert scenario['operator'] == operator and scenario['skill'] == number
                    native = result['panel_native_finalization']
                    assert native == calculate_damage(deepcopy(scenario))['panel_native_finalization']
                    assert native['source_valid'] is True and len(native['fields']) == 17
                    assert native['complete_native_panel'] is False and native['actual_panel'] is None
                    rows = {row['field']: row for row in native['fields'] if row['phase'] == 'skill'}
                    scope = native['skill_primitive_qualification']
                    for field, expected, model_key in [('attack', attack_known, 'skill_attack'),
                                                       ('attack_speed', speed_known, 'skill_attack_speed_reference')]:
                        row = rows[field]
                        assert scope[field]['common_model_primitives_captured'] is expected
                        assert row['primitive_qualification'] == scope[field]
                        assert row['model_value'] == result['estimate']['skill'][model_key]
                        assert scope[field]['actual_activation_or_phase_clock_verified'] is False
                        assert row['actual_getter_raw'] is None and row['actual_decoded_value'] is None
                        assert row['complete_native_value'] is False
                        if expected:
                            assert row['references']['input_fp_raw'] is not None and scope[field]['reason'] is None
                        else:
                            assert row['references']['input_fp_raw'] is None
                            assert row['conditional_complete'] is False and scope[field]['reason']
                    rendered = w.damage_text.toPlainText()
                    assert '面板算式与精度核验' in rendered and '完整原生面板' in rendered
                    assert '面板算式与精度核验' in format_report(result)
                    if phrase is not None:
                        assert phrase in rendered, phrase
                    assert tabs.currentIndex() == damage_index and w.damage_text.isVisible()
                    gui.processEvents()
                    bar = w.damage_text.verticalScrollBar()
                    assert bar.maximum() > 0, 'Real nonzero report scroll required.'
                    cursor = w.damage_text.textCursor()
                    cursor.setPosition(3)
                    cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
                    w.damage_text.setTextCursor(cursor)
                    bar.setValue(max(1, bar.maximum()//2))
                    saved = snapshot()
                    # This is the real same-context UI calculation path; source
                    # field capture does not reset the user's selected report.
                    w.calculate()
                    gui.processEvents()
                    assert snapshot() == saved
                    assert_isolated()
                    observations.append({'operator': operator, 'skill': number, 'public_boolean_options': options,
                                         'attack_common_model_captured': attack_known,
                                         'attack_speed_common_model_captured': speed_known,
                                         'native_fields': 17, 'actual_state_unknown': True,
                                         'real_report_scroll_value_preserved': bar.value(),
                                         'report_cursor_and_timing_input_preserved': True,
                                         'same_main_reference': True})
                    index[0] += 1
                    if index[0] < len(cases):
                        QTimer.singleShot(250, run_case)
                        return
                    # Section284 does not silently implement section285's
                    # broader calibration gate or create another query.
                    try:
                        run_offline_query('calibration', 'panel', {'scenario': {'operator': 'char_151_myrtle', 'skill': 2}})
                    except ValueError:
                        extended_calibration_rejected = True
                    else:
                        extended_calibration_rejected = False
                    assert extended_calibration_rejected
                    assert len(QUERIES['calibration']) + len(QUERIES['battle']) == 37
                    assert len(PRODUCT_QUERIES['exploration']) == 9 and len(QUERIES['exploration']) == 13
                    after = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(files)}
                    assert before == after
                    report = {'passed': True, 'qpa': gui.platformName(), 'visible': True,
                              'page': 'actual_main_damage_report', 'cases': deepcopy(observations),
                              'case_count': len(observations), 'generic_and_field_specific_unknowns_visible': True,
                              'body_vs_summon_and_post_slash_not_conflated': True,
                              'opposite_music_modes_do_not_reuse_old_field_qualification': True,
                              'same_context_refresh_preserves_operator_skill_branch_input_report_cursor_scroll': True,
                              'current_main_report_reused_without_new_query': True,
                              'extended_calibration_still_rejected': True,
                              'calibration_and_battle_queries': 37,
                              'exploration_product_queries': 9, 'historical_exploration_queries': 13,
                              'loaded_source_sha256': before, 'source_sha256_after': after,
                              'new_native_primary_readback_performed_by_window': False,
                              'new_native_fresh_methods_claimed': 0, 'new_native_fresh_spans_claimed': 0,
                              'private_state_read': False, 'temporary_state_root': True,
                              'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                              'scope': 'Actual public Windows main damage page and report only; model primitive qualification is not actual activation, native call normality, codec roundtrip or a phase clock.'}
                except BaseException as error:
                    report = failure(error)
                    failed[0] = True
                checked[0] = True
                write_report(report)
                if failed[0]:
                    w.close()
                    gui.exit(1)

            def close():
                if not checked[0]:
                    write_report(failure(TimeoutError('The actual window closed before all selected public cases.')))
                    checked[0] = True
                    failed[0] = True
                w.close()

            QTimer.singleShot(500, run_case)
            QTimer.singleShot(max(25000, args.visible_ms), close)
            code = gui.exec()
            if not checked[0] and not destination.exists():
                write_report(failure(RuntimeError('The actual window exited before verification completed.')))
                failed[0] = True
            return 1 if failed[0] else code
    except BaseException as error:
        if not destination.exists():
            write_report(failure(error))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
