"""Native Windows preview of conditional moving-enemy rewards; public state only."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    receipt = Path(args.receipt).resolve()
    if receipt.exists():
        raise FileExistsError('Preserve the original report; select a new path.')
    receipt.parent.mkdir(parents=True, exist_ok=True)
    checks, stages = [], []
    report = {'started_utc': datetime.now(timezone.utc).isoformat(), 'passed': False,
              'game_captures': 0, 'chat_sends': 0, 'private_state_loaded': False}

    def require(condition, label):
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    try:
        if sys.platform != 'win32' or os.environ.get('QT_QPA_PLATFORM') == 'offscreen':
            raise RuntimeError('Requires a visible original Windows desktop.')
        import win32gui
        import win32process
        from PySide6.QtCore import QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from rouge import app as app_module
        from rouge.battle_reward_planning import MOVING

        files = ['rouge/app.py', 'rouge/battle_reward_planning.py',
                 'rouge/player_node_information.py', 'rouge/moving_reward_reference.py',
                 'rouge/battle_view.py', 'rouge/node_catalog_view.py',
                 'rouge/data/moving-reward-current-reference.json',
                 'scripts/verify_moving_reward_window_287.py']
        fingerprint = lambda: {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
        before = fingerprint()
        gui = QApplication([])
        require(gui.platformName() == 'windows', 'native_windows_qpa')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        def forbidden(*_args, **_kwargs):
            raise AssertionError('Game enumeration is forbidden in this public test.')

        with tempfile.TemporaryDirectory(prefix='rouge-287-public-') as temporary, \
                patch.object(app_module, 'list_game_windows', side_effect=forbidden):
            temp = Path(temporary)
            app_module.ROOT = temp
            app_module.SETTINGS = temp / 'settings.json'
            app_module.OPERATOR_STATE = temp / 'operators.json'
            app_module.RUN_STATE = temp / 'run.json'
            window = PublicWindow()
            window.setWindowTitle('第287节 · 条件奖励预览（公开隔离测试）')
            window.resize(1350, 930)
            window.show()
            tabs = window.centralWidget()
            battle, nodes = window.battle_preview, window.node_catalog
            window.show_catalog_battle('ro6_n_5_3')
            index = next(i for i in range(1, battle.reward_combo.count())
                         if battle.reward_combo.itemData(i)['entity_id'] == MOVING)
            battle.reward_combo.setCurrentIndex(index)
            failed = []

            def snapshot(name):
                handle = int(window.winId())
                require(win32gui.IsWindowVisible(handle) and not win32gui.IsIconic(handle), name + '_visible')
                require(win32process.GetWindowThreadProcessId(handle)[1] == os.getpid(), name + '_owned_window')
                image = receipt.with_name(receipt.stem + '-' + name + '.png')
                if image.exists():
                    raise FileExistsError(str(image))
                require(window.grab().save(str(image)), name + '_screenshot_saved')
                stages.append({'name': name, 'file': image.name,
                               'sha256': sha256(image.read_bytes()).hexdigest(), 'hwnd': handle})

            def check_battle():
                try:
                    require(tabs.currentWidget() is battle and battle.current_stage == 'ro6_n_5_3', 'exact_higher_level_stage')
                    text = battle.spawn_detail.toPlainText()
                    for value in ('+10源石锭', '-10源石锭', '战斗结束', '两个结果互斥', '实际奖励总量与完整结算池：未知'):
                        require(value in text, 'battle_text_' + value)
                    require('https://' not in text and MOVING not in text, 'player_view_hides_raw_ids_and_urls')
                    require(battle.grid.reference_cell is None and battle.original.reference_cell is None, 'unbound_position_remains_unknown')
                    require(battle.reward_combo.currentData()['rule']['referenced_levels'] == [2], 'fixed_reference_grade_is_two')
                    require(battle.reward_result['actual_reward_total'] is None, 'actual_total_unknown')
                    cursor = battle.spawn_detail.textCursor()
                    cursor.setPosition(3)
                    cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
                    battle.spawn_detail.setTextCursor(cursor)
                    bar = battle.spawn_detail.verticalScrollBar()
                    require(bar.maximum() > 0, 'real_scroll_range')
                    bar.setValue(max(1, bar.maximum() // 2))
                    saved = (cursor.selectedText(), bar.value(), battle.reward_combo.currentData()['id'])
                    battle.render_rows()
                    gui.processEvents()
                    require((battle.spawn_detail.textCursor().selectedText(), bar.value(), battle.reward_combo.currentData()['id']) == saved, 'refresh_preserves_reading')
                    snapshot('battle')
                    tabs.setCurrentWidget(nodes)
                    nodes.list.setCurrentRow(next(i for i, entry in enumerate(nodes.entries)
                        if entry['kind'] == 'battle' and entry['record'].get('id') == 'ro6_n_5_3'))
                    nodes.reading_tabs.setCurrentWidget(nodes.player_detail)
                    QTimer.singleShot(400, check_nodes)
                except BaseException:
                    failed.append(traceback.format_exc())
                    window.close()

            def check_nodes():
                try:
                    text = nodes.player_detail.toPlainText()
                    for value in ('10源石锭', '-10源石锭', '击倒收益和漏过损失',
                                  '同一移动敌人的奖励只能算一次', '实际出现及领取总量：未知'):
                        require(value in text, 'node_text_' + value)
                    require('https://' not in text and MOVING not in text, 'node_view_hides_raw_ids_and_urls')
                    snapshot('node')
                    nodes.battle_button.click()
                    require(tabs.currentWidget() is battle and battle.current_stage == 'ro6_n_5_3', 'node_link_opens_exact_battle')
                    require(not window.auto.isChecked() and not window.timer.isActive(), 'game_sampling_disabled')
                    require(window.capture.target is None and window.desktop.process is None, 'no_game_target_or_chat_process')
                    require(fingerprint() == before, 'frozen_source_unchanged')
                    report['passed'] = True
                    window.close()
                except BaseException:
                    failed.append(traceback.format_exc())
                    window.close()

            QTimer.singleShot(600, check_battle)
            QTimer.singleShot(30000, window.close)
            report['qt_exit_code'] = gui.exec()
            require(not window.isVisible(), 'verification_window_closed')
            require(fingerprint() == before, 'source_unchanged_through_closure')
            report['source_sha256'] = before
            if failed:
                raise AssertionError('\n'.join(failed))
            require(report['passed'], 'all_stages_finished')
    except BaseException:
        report['passed'] = False
        report['error'] = traceback.format_exc()
    report.update(checks=checks, unique_checks=len(set(checks)), stages=stages,
                  finished_utc=datetime.now(timezone.utc).isoformat())
    with receipt.open('x', encoding='utf8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
