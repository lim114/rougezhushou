"""Isolated Qt healing recipients and relic-multiplier contract checks."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_relic_ui_025 import OfflineWindow, module, QApplication, Qt
from PySide6.QtGui import QFont, QFontDatabase

ROSE = 'rogue_6_relic_legacy_81'
CROWN = 'rogue_6_relic_legacy_82'


def main():
    start = time.perf_counter()
    evidence_folder = ROOT / '.cache/healing-ui-053'
    evidence_folder.mkdir(parents=True, exist_ok=True)
    sources = ('rouge/app.py', 'rouge/damage.py', 'rouge/estimate.py',
               'rouge/operator_engine.py', 'rouge/relics.py', 'rouge/run_modifiers.py',
               'rouge/timing.py', 'rouge/reporting.py', 'rouge/offline_scope.py',
               'rouge/data/catalog.json', 'rouge/data/relic-mechanics.json',
               'scripts/verify_healing_ui_053.py', 'scripts/verify_relic_ui_025.py')
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources}
    with tempfile.TemporaryDirectory() as folder:
        isolated = Path(folder)
        module.RUN_STATE = isolated / 'run.json'
        module.OPERATOR_STATE = isolated / 'operators.json'
        module.SETTINGS = isolated / 'settings.json'
        backend = module.DesktopBackend
        module.DesktopBackend = lambda _path, callback: backend(isolated / 'chat', callback)
        app = QApplication([])
        font_id = QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR']) / 'Fonts/msyh.ttc'))
        assert font_id >= 0
        app.setFont(QFont(QFontDatabase.applicationFontFamilies(font_id)[0], 9))
        window = OfflineWindow()
        counts = {'full_skill_cases': 0, 'cap_clamp_cases': 0, 'window_cases': 0,
                  'unknown_combo_cases': 0, 'unrelated_panel_cases': 0}
        boundaries = ((0.10, 0, 0), (0.20, 0, 0), (0.21, 0, 1),
                      (0.70, 0.5, 0), (0.71, 0.5, 1))

        def select_operator(op, number):
            window.select_operator(op)
            window.skill.setCurrentIndex(window.skill.findData(number))

        def configure(targets, relics=(), output_window=None, travel=0):
            window.healing_targets.setValue(targets)
            window.limit_window.setChecked(output_window is not None)
            if output_window is not None:
                window.window_seconds.setValue(output_window)
            window.timing_scenario.setPlainText(json.dumps({'windup_frames': 6,
                'recovery_frames': 9, 'projectile_travel_seconds': travel}))
            window.relic_list.blockSignals(True)
            for i in range(window.relic_list.count()):
                item = window.relic_list.item(i)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in relics
                                   else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
            window.calculate()
            assert window.damage_result, window.damage_text.toPlainText()
            result = window.damage_result['result']
            assert window.damage_text.isReadOnly()
            return result

        def check_healing(result, expected):
            skill = result['estimate']['skill']
            assert abs(result['total_healing'] - expected) < 1e-7, (result['total_healing'], expected)
            assert abs(skill['window_healing'] - expected) < 1e-7
            assert result['total_damage'] == 0
            sections = {row['id']: row for row in result['report']['sections']}
            assert 'healing' in sections
            assert not ({'dp', 'regeneration', 'relic_regeneration', 'ammo_refill_reference'} & sections.keys())
            assert '【治疗输出】' in window.damage_text.toPlainText()
            assert window.damage_form.isRowVisible(window.healing_targets)
            for owner, key, supported, widget in window.model_option_widgets:
                assert window.damage_form.isRowVisible(widget) == (
                    owner == 'kaltsit' and window.skill.currentData() in supported), key

        try:
            assert not window.auto.isChecked() and window.capture.target is None
            assert not window.desktop.process
            window.auto_relics.setChecked(False)
            window.frame_timing.setChecked(True)
            window.use_run_training.setChecked(False)
            caps = {}
            for number, cap in ((1, 1), (3, 2)):
                select_operator('kaltsit', number)
                caps[str(number)] = window.healing_targets.maximum()
                assert caps[str(number)] == cap
                window.healing_targets.setValue(100)
                assert window.healing_targets.value() == cap
                counts['cap_clamp_cases'] += 1
                for targets in range(cap + 1):
                    for relics, factor in (((), 1), ((ROSE,), 1.2)):
                        result = configure(targets, relics)
                        expected = result['attack'] * result['hits'] * targets * factor
                        check_healing(result, expected)
                        assert result['relic_resolution']['complete']
                        counts['full_skill_cases'] += 1
                for output_window, travel, hits in boundaries:
                    for relics, factor in (((), 1), ((ROSE,), 1.2)):
                        result = configure(cap, relics, output_window, travel)
                        assert result['hits'] == hits, (number, output_window, travel, result['hits'])
                        check_healing(result, result['attack'] * hits * cap * factor)
                        assert window.damage_result['scenario']['window_seconds'] == output_window
                        assert window.damage_result['scenario']['timing']['projectile_travel_seconds'] == travel
                        counts['window_cases'] += 1
                for targets in range(cap + 1):
                    plain = configure(targets)
                    result = configure(targets, (ROSE, CROWN))
                    check_healing(result, plain['total_healing'])
                    assert not result['relic_resolution']['complete']
                    assert not result['complete']
                    assert any('heal_scale' in message for message in result['warnings'])
                    assert all(row['status'] == 'incomplete' for row in result['relic_resolution']['records'])
                    assert '叠加规则尚未核验' in window.damage_text.toPlainText()
                    counts['unknown_combo_cases'] += 1

            # Evidence focuses the actual treatment block for a delayed,
            # two-recipient S3 result, after applying the rose exactly once.
            select_operator('kaltsit', 3)
            pictured = configure(2, (ROSE,), 0.71, 0.5)
            check_healing(pictured, pictured['attack'] * 2 * 1.2)
            window.resize(1600, 1000)
            window.centralWidget().setCurrentIndex(1)
            window.show()
            app.processEvents()
            window.damage_text.moveCursor(window.damage_text.textCursor().MoveOperation.Start)
            assert window.damage_text.find('【治疗输出】')
            window.damage_text.centerCursor()
            app.processEvents()
            screenshot = evidence_folder / 'kaltsit-s3-two-recipients-rose.png'
            assert window.grab().save(str(screenshot), 'PNG')

            for operator, number in (('mechanist', 1), ('mechanist', 2), ('mechanist', 3),
                                     ('silverash', 1), ('silverash', 2), ('silverash', 3),
                                     ('char_1029_yato2', 1), ('char_1029_yato2', 2), ('char_1029_yato2', 3)):
                select_operator(operator, number)
                result = configure(0, (ROSE,))
                assert not window.damage_form.isRowVisible(window.healing_targets), (operator, number)
                assert 'healing' not in {row['id'] for row in result['report']['sections']}
                assert '【治疗输出】' not in window.damage_text.toPlainText()
                for owner, key, supported, widget in window.model_option_widgets:
                    assert window.damage_form.isRowVisible(widget) == (owner == operator and number in supported), key
                counts['unrelated_panel_cases'] += 1
            assert counts == {'full_skill_cases': 10, 'cap_clamp_cases': 2, 'window_cases': 20,
                              'unknown_combo_cases': 5, 'unrelated_panel_cases': 9}, counts
            assert window.run.state['config'] == {} and window.run.state['history'] == []
            assert not window.auto.isChecked() and window.capture.target is None
            assert not window.desktop.process and not (isolated / 'chat').exists()
            after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources}
            assert hashes == after, 'Sources changed during isolated verification.'
            receipt = {'version': '0.53.0', 'passed': True, 'verified_at': time.time(),
                       'elapsed_seconds': time.perf_counter() - start, 'cases': counts,
                       'ui_recipient_caps': caps, 'api_100_case_not_repeated_in_ui': True,
                       'public_total_matches_window': True, 'rose_applied_once': True,
                       'known_zero_retained': True, 'explicit_frames_and_delayed_boundary': True,
                       'unknown_combinations_not_guessed': True, 'inapplicable_panels_hidden': True,
                       'screenshot': screenshot.relative_to(ROOT).as_posix(),
                       'screenshot_focus': 'Treatment block, S3, two recipients, 0.71 s window, 0.5 s projectile, rose.',
                       'screenshot_sha256': hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                       'synthetic_cultivation_only': True, 'private_data_isolated': True,
                       'game_actions': 0, 'game_captures': 0, 'chat_requests': 0,
                       'source_hashes': hashes, 'source_hashes_after': after,
                       'limits': ['Offscreen Qt wiring; no live recipients or relic acquisition validated.']}
            (ROOT / 'HEALING_UI_0.53_VERIFICATION.json').write_text(
                json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(json.dumps({key: receipt[key] for key in ('passed', 'cases', 'ui_recipient_caps',
                'private_data_isolated', 'elapsed_seconds')}, ensure_ascii=False), flush=True)
        finally:
            window.close()
            app.processEvents()


if __name__ == '__main__':
    main()
