"""Isolated Qt verification for the documented Angel S3 partial ammo packet."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_relic_ui_025 import OfflineWindow, module, QApplication, Qt
from PySide6.QtGui import QFont, QFontDatabase

ANGEL = 'char_1041_angel2'
BOOK = 'rogue_6_relic_legacy_139'
YA = 'rogue_6_relic_legacy_140'
PACKET_NOTE = '当前技能不足5发的最后一包仍完成五连击，天赋按5次消耗处理；不按余弹比例裁减。'


def main():
    start = time.perf_counter()
    evidence_folder = ROOT / '.cache/packet-ui-054'
    evidence_folder.mkdir(parents=True, exist_ok=True)
    sources = ('rouge/app.py', 'rouge/damage.py', 'rouge/estimate.py',
        'rouge/operator_engine.py', 'rouge/relics.py', 'rouge/relic_events.py',
        'rouge/ammo_reference.py', 'rouge/reporting.py',
        'rouge/data/ammo-refill-reference.json', 'rouge/data/relic-mechanics.json',
        'scripts/verify_packet_ui_054.py', 'scripts/verify_relic_ui_025.py')
    before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources}
    cases = []
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

        def choose(operator, number):
            window.select_operator(operator)
            window.skill.setCurrentIndex(window.skill.findData(number))

        def configure(ids, frames=True):
            window.frame_timing.setChecked(frames)
            window.relic_list.blockSignals(True)
            for index in range(window.relic_list.count()):
                item = window.relic_list.item(index)
                item.setCheckState(Qt.CheckState.Checked if item.data(Qt.ItemDataRole.UserRole) in ids
                                   else Qt.CheckState.Unchecked)
            window.relic_list.blockSignals(False)
            window.calculate()
            assert window.damage_result, window.damage_text.toPlainText()
            assert window.damage_text.isReadOnly()
            return window.damage_result['result'], window.damage_text.toPlainText()

        def reference(result):
            return next((block for block in result['report']['sections']
                         if block['id'] == 'ammo_refill_reference'), None)

        def check_known(result, text, hits, label):
            skill = result['estimate']['skill']
            assert result['relic_resolution']['complete']
            assert skill['hit_counts']['技能攻击'] == hits
            assert skill['hit_counts']['火力电台本体生命回复'] == hits
            for key in ('total_damage', 'duration_seconds', 'cycle_seconds', 'cycle_dps'):
                assert skill[key] is not None, (label, key)
            assert reference(result) is not None
            rows = {row['key']: row for row in reference(result)['metrics']}
            assert rows['ammo_full_cast_hits']['value'] == hits
            assert rows['ammo_full_cast_recoveries']['value'] == hits
            assert f'单次技能预测攻击命中：{hits} 次' in text
            assert f'单次技能预测天赋回复次数：{hits} 次' in text
            assert PACKET_NOTE in text
            assert '末包机制资料' in text
            assert '单次技能总伤：未知' not in text
            assert '预计回转：未知' not in text
            assert 'partial_packet_reference' not in text
            assert 'https://' not in text
            # The debug view is the user's actual structured-data widget.
            # Record this separately from the Chinese report's visible metrics.
            window.raw_damage.setChecked(True)
            debug = json.loads(window.damage_text.toPlainText())
            assert debug['result']['estimate']['skill']['hit_counts']['技能攻击'] == hits
            assert debug['result']['estimate']['skill']['hit_counts']['火力电台本体生命回复'] == hits
            window.raw_damage.setChecked(False)
            assert PACKET_NOTE in window.damage_text.toPlainText()
            cases.append({'case': label, 'known': True, 'skill_hits': hits,
                'talent_consumption_reply_events': hits,
                'duration_seconds': skill['duration_seconds'], 'cycle_seconds': skill['cycle_seconds'],
                'chinese_packet_note_visible': True, 'ordinary_report_counts_visible': True,
                'structured_data_widget_counts_visible': True})

        def check_unknown(result, text, label, *, order=False):
            skill = result['estimate']['skill']
            assert not result['relic_resolution']['complete']
            assert skill['total_damage'] is None
            assert skill['cycle_seconds'] is None
            assert skill['cycle_dps'] is None
            assert skill['recharge_seconds'] is not None
            assert '单次技能总伤：未知' in text
            if order:
                assert '获取先后未确认' in text
                assert reference(result) is None
                assert PACKET_NOTE not in text
            cases.append({'case': label, 'known': False,
                'complete_cast_and_cycle_unknown': True, 'independent_recharge_retained': True})

        def reorder_books(order):
            window.relic_list.blockSignals(True)
            items = {}
            for rid in order:
                index = next(i for i in range(window.relic_list.count())
                    if window.relic_list.item(i).data(Qt.ItemDataRole.UserRole) == rid)
                items[rid] = window.relic_list.takeItem(index)
            for rid in reversed(order):
                window.relic_list.insertItem(0, items[rid])
            window.relic_list.blockSignals(False)

        try:
            assert not window.auto.isChecked() and window.capture.target is None
            assert not window.desktop.process
            window.auto_relics.setChecked(False)
            window.use_run_training.setChecked(False)
            window.limit_window.setChecked(False)
            window.timing_scenario.clear()
            window.damage_technical.setChecked(False)
            for rid, hits in ((BOOK, 70), (YA, 75)):
                for frames in (True, False):
                    choose(ANGEL, 3)
                    result, text = configure((rid,), frames)
                    check_known(result, text, hits, f's3-{rid}-'+('frames' if frames else 'continuous'))

            for rid in (BOOK, YA):
                choose(ANGEL, 2)
                result, text = configure((rid,))
                check_unknown(result, text, f's2-dynamic-ammo-{rid}')
                assert PACKET_NOTE not in text and '末包机制资料' not in text
                assert reference(result) is None

            choose(ANGEL, 3)
            window.limit_window.setChecked(True)
            window.window_seconds.setValue(0.1)
            result, text = configure((BOOK,))
            assert result['estimate']['skill']['hit_counts']['技能攻击'] == 70
            window_hits = next(c['hits'] for c in result['components'] if c['name'] == '技能攻击')
            assert window_hits < 70
            rows = {row['key']: row for row in reference(result)['metrics']}
            assert rows['ammo_full_cast_hits']['value'] == 70
            assert rows['ammo_full_cast_recoveries']['value'] == 70
            assert '单次技能预测攻击命中：70 次' in text
            assert '次数为完整技能参考，不表示观察窗口内已经完成' in text
            cases.append({'case': 'short-window-retains-full-cast-predicted-counts',
                'window_seconds': 0.1, 'modeled_window_hits': window_hits,
                'full_cast_skill_hits': 70, 'full_cast_talent_reply_events': 70,
                'window_and_full_cast_counts_separate': True})
            window.limit_window.setChecked(False)

            for operator, number in ((ANGEL, 1), ('mechanist', 1), ('kaltsit', 2)):
                choose(operator, number)
                result, text = configure((BOOK,))
                assert PACKET_NOTE not in text and '末包机制资料' not in text
                assert not any(rule.get('ammo_parameters', {}).get('partial_packet_reference')
                    for rule in result['relic_resolution']['rules'])
                if reference(result):
                    assert not any(row['key'] in ('ammo_full_cast_hits', 'ammo_full_cast_recoveries')
                        for row in reference(result)['metrics'])
                cases.append({'case': f'no-packet-leak-{operator}-s{number}',
                    'unrelated_packet_proof_absent': True})

            for order in ((BOOK, YA), (YA, BOOK)):
                reorder_books(order)
                choose(ANGEL, 3)
                result, text = configure(order)
                assert window.damage_result['scenario']['relic_ids'] == list(order)
                check_unknown(result, text, 'both-books-order-'+','.join(order), order=True)

            choose(ANGEL, 3)
            with patch('rouge.ammo_reference.refill_before_empty_is_safe', return_value=False):
                result, text = configure((BOOK,))
            check_unknown(result, text, 'unsafe-polling-window')
            assert '耗尽前检查窗口不足' in text
            rows = {row['key']: row for row in reference(result)['metrics']}
            assert rows['ammo_full_cast_hits']['value'] is None
            assert rows['ammo_full_cast_recoveries']['value'] is None
            assert '单次技能预测攻击命中：未知' in text
            assert '单次技能预测天赋回复次数：未知' in text

            # Reuse the application's refresh/render methods with empty isolated
            # run state; this exercises stale notes without any game sampling.
            for operator, number, ids, expected in (
                (ANGEL, 1, (BOOK,), False), (ANGEL, 2, (BOOK,), False),
                ('mechanist', 1, (BOOK,), False), (ANGEL, 3, (), False),
                (ANGEL, 3, (BOOK,), True),
            ):
                choose(operator, number)
                result, _ = configure(ids)
                selection = (window.operator.currentData(), window.skill.currentData())
                window.sync_run_config()
                window.sync_run_relics()
                window.update_operator(preserve_level=True)
                window.render_damage()
                assert (window.operator.currentData(), window.skill.currentData()) == selection
                text = window.damage_text.toPlainText()
                assert (PACKET_NOTE in text) == expected
                assert ('末包机制资料' in text) == expected
                cases.append({'case': f'selection-refresh-{operator}-s{number}-packet-{expected}',
                    'selection_preserved': True, 'stale_packet_note_absent': not expected})

            choose(ANGEL, 3)
            result, text = configure((BOOK,))
            assert PACKET_NOTE in text
            window.resize(1600, 1050)
            window.centralWidget().setCurrentIndex(1)
            window.show()
            app.processEvents()
            window.damage_text.moveCursor(window.damage_text.textCursor().MoveOperation.Start)
            assert window.damage_text.find(PACKET_NOTE)
            window.damage_text.centerCursor()
            app.processEvents()
            screenshot = evidence_folder / 'angel-s3-book-partial-last-packet.png'
            assert window.grab().save(str(screenshot), 'PNG')

            assert len(cases) == 18, len(cases)
            assert window.run.state['config'] == {} and window.run.state['history'] == []
            assert not window.auto.isChecked() and window.capture.target is None
            assert not window.desktop.process and not (isolated / 'chat').exists()
            after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sources}
            assert before == after, 'Sources changed during Qt verification.'
            receipt = {'version': '0.54.0', 'passed': True, 'verified_at': time.time(),
                'elapsed_seconds': time.perf_counter()-start, 'case_count': len(cases), 'cases': cases,
                'chinese_partial_packet_note_visible': True, 'known_s3_counts': [70, 75],
                'ordinary_report_predicted_counts_visible': True,
                'full_cast_and_window_counts_separate': True,
                'unknown_s2_dynamic_maximum_retained': True,
                'both_book_orders_unknown': True, 'polling_guard_retained': True,
                'selection_refresh_notes_isolated': True,
                'screenshot': screenshot.relative_to(ROOT).as_posix(),
                'screenshot_focus': 'Chinese partial last-packet explanation and full-cast/window count distinction, Angel S3, 30 percent book.',
                'screenshot_sha256': hashlib.sha256(screenshot.read_bytes()).hexdigest(),
                'synthetic_cultivation_only': True, 'private_data_isolated': True,
                'game_captures': 0, 'game_actions': 0, 'chat_requests': 0,
                'source_hashes': before, 'source_hashes_after': after,
                'limits': ['Offscreen Qt/public calculation wiring only; no live partial packet, polling phase, recipients or acquisition order validated.']}
            (ROOT / 'PACKET_UI_0.54_VERIFICATION.json').write_text(
                json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            (evidence_folder / 'report.txt').write_text(text, encoding='utf-8')
            print(json.dumps({key: receipt[key] for key in ('passed', 'case_count',
                'known_s3_counts', 'private_data_isolated', 'elapsed_seconds')}, ensure_ascii=False), flush=True)
        finally:
            window.close()
            app.processEvents()


if __name__ == '__main__':
    main()
