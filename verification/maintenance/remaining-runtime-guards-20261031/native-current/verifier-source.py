"""Native public-reader checks for data-only runtime manifests; no game/chat."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import argparse
import json
import os
import sys

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    images = []

    def check(section, window, gui, require):
        from PySide6.QtCore import Qt
        from PySide6.QtTest import QTest
        import win32gui
        import win32process
        from rouge import node_catalog as catalog, choice_recruitment_results as recruit
        from rouge import peace_guardian_results as peace, stage_entry_reference as entry
        from rouge import current_reward_reference as rewards
        from rouge.current_battle_view import CurrentBattlePanel

        initial_state = deepcopy(window.run.state)
        node = window.node_catalog

        def save(widget, name):
            gui.processEvents()
            hwnd = int(widget.winId())
            require(widget.isVisible() and win32gui.IsWindowVisible(hwnd)
                    and win32process.GetWindowThreadProcessId(hwnd)[1] == os.getpid(), name + '_owned_visible')
            path = args.receipt.with_name(name + '.png')
            require(widget.grab().save(str(path)), name + '_saved')
            images.append({'file': path.as_posix(), 'sha256': sha256(path.read_bytes()).hexdigest()})

        def event(identity, scene=None, choice=None):
            row = next(e for e in catalog.all_events(include_indirect=True)['rows'] if e['id'] == identity)
            node.kind.setCurrentIndex(node.kind.findData('event'))
            node.floor.setCurrentIndex(0)
            node.node_type.setCurrentIndex(0)
            node.search.setText(row['title'])
            node.refresh()
            index = next(i for i, e in enumerate(node.entries)
                         if e['kind'] == 'event' and e['record']['id'] == identity)
            node.list.setCurrentRow(index)
            window.centralWidget().setCurrentWidget(node)
            window.show()
            if scene is not None:
                node.event_scene_filter.setCurrentIndex(node.event_scene_filter.findData(scene))
            if choice is not None:
                node.event_choice_filter.setCurrentIndex(node.event_choice_filter.findData(choice))
            gui.processEvents()
            require(node.isVisible(), 'normal_player_event_page_visible')

        event(recruit.EVENT, recruit.SCENE, recruit.CHOICE)
        require('直升' in node.player_detail.toPlainText(), 'recruitment_documented_promotion_readable')
        require(node.event_choice_filter.currentData() == recruit.CHOICE, 'recruitment_exact_choice')
        save(node, 'recruitment')
        event(peace.EVENT, peace.SCENE, peace.CHOICE)
        require(node.event_choice_filter.currentData() == peace.CHOICE, 'movement_exact_choice')
        require('若已完成当前层' in node.player_detail.toPlainText(), 'documented_movement_exception_readable')
        save(node, 'peace-guardian')
        event('community_group_023')
        require(node.resting_button.isEnabled() and node.resting_button.isVisible(), 'resting_entry_available')
        QTest.mouseClick(node.resting_button, Qt.MouseButton.LeftButton)
        gui.processEvents()
        resting = node.resting_window
        require(resting.isVisible() and resting.choice.count() == 4
                and resting.choice.currentData() is None, 'resting_default_four_explicit_choices')
        resting.choice.setCurrentIndex(0)
        gui.processEvents()
        require(resting.branch.count() == 3, 'resting_first_choice_three_distinct_branches')
        resting.branch.setCurrentIndex(0)
        QTest.mouseClick(resting.open_scene_button, Qt.MouseButton.LeftButton)
        gui.processEvents()
        require(resting._scene_identity[-1] == 'community_group_023:scene:2', 'resting_exact_future_scene')
        require('不表示已进入游戏' in resting.scene_text.toPlainText(), 'resting_reading_not_actual_game_action')
        save(resting, 'resting-corner')
        resting.close()
        preview = window.battle_preview
        preview.set_stage(entry.STAGE_ID)
        window.centralWidget().setCurrentWidget(preview)
        window.show()
        gui.processEvents()
        require(preview.entry_reference_button.isEnabled(), 'stage_configuration_entry_available')
        QTest.mouseClick(preview.entry_reference_button, Qt.MouseButton.LeftButton)
        gui.processEvents()
        configuration = preview.entry_reference_window
        require(configuration.isVisible(), 'stage_configuration_reader_open')
        save(configuration, 'stage-configuration')
        configuration.close()
        battle = CurrentBattlePanel('ro6_n_2_6')
        try:
            battle.resize(1050, 720)
            battle.show()
            gui.processEvents()
            panel = battle.rewards
            require(panel.result is not None and bool(panel.result['rows']), 'current_rewards_rows_available')
            battle.tabs.setCurrentWidget(panel)
            row = next(r for r in panel.result['rows'] if r['source_action_keys'])
            panel.choices.select_value(row['id'])
            panel.source_combo.setCurrentIndex(1)
            key = panel.source_combo.currentData()
            require(panel.source_button.isEnabled(), 'reward_explicit_source_available')
            save(battle, 'current-rewards')
            QTest.mouseClick(panel.source_button, Qt.MouseButton.LeftButton)
            gui.processEvents()
            require(battle.action_key == key and battle.tabs.currentIndex() == 2,
                    'reward_actual_button_maps_to_exact_fixed_source')
            require('准确时刻：未知' in battle.action_player.toPlainText(), 'fixed_source_does_not_invent_actual_time')
            save(battle, 'reward-source')
            before = deepcopy(battle.result)
            with TemporaryDirectory(prefix='rouge-reward-public-loss-') as folder, patch.object(rewards, 'ROOT', Path(folder)):
                require(not panel.refresh_reference(), 'missing_reward_source_rejected')
                gui.processEvents()
                require(panel.result is None and not panel.source_button.isEnabled(), 'missing_source_clears_old_reward_link')
                require(battle.result == before, 'reward_failure_preserves_independent_battle')
            require(panel.refresh_reference(), 'public_reward_source_recovers')
            require(panel.combo.currentData() is None, 'recovered_reward_requires_manual_choice')
        finally:
            battle.close()
        require(window.run.state == initial_state, 'all_public_navigation_preserves_fixture_run')
        window.player_validation_target = node

    player_acceptance.check = check
    code = run(419, args.receipt)
    args.receipt.with_name('review-images.json').write_text(json.dumps({
        'images': images, 'isolated_public_fixtures_only': True,
        'whole_video_parity_claimed': False}, ensure_ascii=False, indent=2) + '\n', 'utf8')
    raise SystemExit(code)
