"""Actual Windows current-enemy Hanko/president/smoke entry and source limits."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse, json, os, sys, traceback
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
CANONICAL = 'scripts/verify_current_hanko_window_365.py'


def bound_files():
    from rouge import current_hanko as model, current_battle_reference as battle, expansion_reference as version
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    for provider in (model, battle, version):
        names.add(provider.MANIFEST); names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update((CANONICAL, 'scripts/verify_full_available.py', 'tests/test_current_hanko_365.py',
                  'tests/test_current_hanko_view_365.py'))
    for name in ('scripts/build_current_hanko_365.py', 'verification/sections/365-preparation/scope.json'):
        if (ROOT / name).is_file(): names.add(name)
    result = {}
    for name in sorted(names):
        path = ROOT / name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Exact regular installed public source required: ' + name)
        result[name] = sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--visible-ms', type=int, default=120000); args = parser.parse_args()
    dest = args.receipt.resolve(); assert not dest.exists(); dest.parent.mkdir(parents=True, exist_ok=True)
    before = bound_files(); checks = []; images = []; observations = []; refreshes = []
    calls = {k: 0 for k in ('game_connect', 'capture', 'next_frame', 'desktop_start', 'desktop_request', 'provider_chat', 'credential_read')}
    failure = None; window = None; gui = None; exitcode = None; done = False
    def require(value, name):
        if not value: raise AssertionError(name)
        if name not in checks: checks.append(name)
    def forbidden(name):
        def fail(*a, **kw): calls[name] += 1; raise AssertionError('Forbidden real operation: ' + name)
        return fail
    try:
        if sys.platform != 'win32': raise RuntimeError('Actual Windows required')
        import win32gui, win32process
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module, current_hanko as model, current_battle_reference as battle_model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge365-public-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for name, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                    'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, name, value))
            backend = app_module.DesktopBackend
            stack.enter_context(patch.object(app_module, 'DesktopBackend', lambda _path, callback: backend(temporary / 'chat', callback)))
            stack.enter_context(patch.object(app_module, 'list_game_windows', return_value=[]))
            for name, key in (('connect', 'game_connect'), ('capture', 'capture'), ('next_frame', 'next_frame')):
                stack.enter_context(patch.object(app_module.GameCapture, name, side_effect=forbidden(key)))
            for name, key in (('start', 'desktop_start'), ('request', 'desktop_request')):
                stack.enter_context(patch.object(backend, name, side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = app_module.MainWindow(); window.resize(1220, 850)
            window.setWindowTitle('第365节 · 汉科与烟雾准确敌人入口（公开隔离验收）'); window.show(); gui.processEvents()
            tabs = window.centralWidget(); main_panel = window.reference_panel('stages'); panel = main_panel
            state = deepcopy(window.run.state); context = deepcopy(window.battle_preview.context)
            battle = None; battle_dialog = None; dialog = None
            def native(widget=None):
                widget = window if widget is None else widget; hwnd = int(widget.winId())
                pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd) and pid == os.getpid(),
                        'visible_owned_native_MainWindow_HWND_PID')
                return {'hwnd': hwnd, 'pid': pid, 'size': [widget.width(), widget.height()]}
            def shot(label, widget=None):
                gui.processEvents(); widget = panel if widget is None else widget
                file = dest.with_name('window-' + label + '.png'); assert not file.exists()
                require(widget.grab().save(str(file), 'PNG'), 'actual_widget_screenshot_saved')
                images.append({'name': label, 'path': str(file), 'sha256': sha256(file.read_bytes()).hexdigest(),
                               'native': native(widget.window())})
            def choose(combo, key):
                index = combo.findData(key); require(index >= 0, 'exact_actor_topic_or_related_value')
                combo.setCurrentIndex(index); gui.processEvents()
            def select_stage(sid):
                nonlocal main_panel, battle, battle_dialog
                main_panel = window.reference_panel('stages'); gui.processEvents()
                item = next(main_panel.entries.item(i) for i in range(main_panel.entries.count())
                            if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole) == sid)
                main_panel.entries.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(main_panel.entries.viewport(), Qt.MouseButton.LeftButton, pos=main_panel.entries.visualItemRect(item).center())
                gui.processEvents(); require(main_panel.battle_button.isVisible(), 'ordinary_exact_stage_battle_entry_visible')
                QTest.mouseClick(main_panel.battle_button, Qt.MouseButton.LeftButton); gui.processEvents()
                battle_dialog = main_panel.current_battle_dialog; battle = battle_dialog.panel
                require(battle_dialog.isVisible() and battle.stage_id == sid and battle.result['id'] == sid,
                        'ordinary_stage_opens_exact_current_battle_not_same_named_legacy')
                battle.tabs.setCurrentIndex(1); gui.processEvents()
            def parent_enemy(key):
                require(battle.enemy_choices.select_value(key), 'exact_parent_enemyDbRefs_index_selected'); gui.processEvents()
                require(battle.enemy_key == key, 'actual_parent_enemy_key_is_exact_reference_index_string')
            def open_actor(key):
                nonlocal panel, dialog
                previous = getattr(battle, 'hanko_dialog', None); parent_enemy(key)
                require(battle.hanko_button.isVisible() and battle.hanko_button.isEnabled(), 'specific_hanko_button_visible_only_for_exact_target')
                QTest.mouseClick(battle.hanko_button, Qt.MouseButton.LeftButton); gui.processEvents()
                dialog = battle.hanko_dialog; panel = dialog.panel
                require(dialog.isVisible() and panel.stage_id == battle.stage_id and panel.selected_key == key
                        and panel.result is not None and panel.result['battle_source_identity'] == battle.result['source_identity'],
                        'ordinary_selected_enemy_opens_exact_owned_hanko_document')
                require(previous is None or previous is not dialog and not previous.isVisible(), 'old_owned_actor_window_not_reused_across_new_open')
            def reading(widget):
                cursor = widget.textCursor()
                return {'anchor': cursor.anchor(), 'position': cursor.position(), 'selection': cursor.selectedText(),
                        'scroll': widget.verticalScrollBar().value()}
            def view():
                return {'stage': panel.stage_id, 'entity': panel.entity_combo.currentData(),
                        'branch': panel.entities.branch.currentData(), 'topic': panel.topic.currentData(),
                        'related': panel.related.currentData()}
            def exercise():
                nonlocal done, failure, panel, dialog
                try:
                    packet = model.packet(); require(packet is not None, 'own_complete_public_packet_available')
                    require(len(packet['data']['bindings']) == 6 and len(packet['data']['originals']['levels']) == 5
                            and sum(len(v['rows']) for v in packet['data']['bindings'].values()) == 12,
                            'six_configs_five_original_levels_twelve_exact_references')
                    require({k: len(v['cards']) for k, v in packet['materials']['actors'].items()} == {'hanko': 3, 'president': 3, 'smoke': 1}
                            and sum(len(v['descriptions_original_and_corrected']) for v in packet['materials']['actors'].values()) == 4,
                            'seven_complete_cards_and_four_original_corrected_descriptions_retained')
                    for sid, group in packet['data']['bindings'].items():
                        select_stage(sid)
                        for binding in group['rows']:
                            key = binding['key']; open_actor(key); row = model.entity(panel.result, key)
                            parent = next(e for e in battle.result['enemies'] if e['key'] == key)
                            require(row['raw_binding'] == parent['raw_binding'] and row['entity_id'] == parent['id']
                                    and row['level'] == parent['level'] and row['enemy'] == parent,
                                    'every_actor_preserves_complete_exact_current_parent_reference')
                            require(all(panel.result[k] is None for k in ('actual_present', 'actual_smoke_cells', 'actual_status_removed', 'actual_skill_time'))
                                    and not panel.result['numeric_model_added'] and not panel.result['run_updated'],
                                    'document_parameters_never_become_actual_presence_time_status_or_damage_model')
                            raw_picture = battle_model.picture_bytes(row['enemy']['portrait']); pixmap = panel.portrait.pixmap()
                            require(bool(raw_picture) == bool(pixmap is not None and not pixmap.isNull()),
                                    'exact_verified_portrait_or_explicit_no_image_without_substitution')
                            if sid == 'ro6_b_1' and row['actor'] == 'hanko': shot('ordinary-enemy-entry', battle)
                            for topic, _label in model.topics(panel.result, key):
                                choose(panel.topic, topic); card = model.selected_card(panel.result, key, topic)
                                shown = json.loads(panel.technical.toPlainText()); text = panel.player.toPlainText()
                                require(shown['current_reference'] == row and shown['selected_document_card'] == card
                                        and shown['complete_actor_source_cards'] == panel.result['materials']['actors'][row['actor']]
                                        and card['complete_DOM'].startswith('<div') and card['body'] in text,
                                        'all_own_mechanism_topics_show_complete_exact_source_card_and_tooltips')
                                require('通用文献原项，不是本局预测数值' in text and shown['actual_skill_time'] is None
                                        and not shown['numeric_model_added'], 'document_card_numbers_are_not_current_effective_clock_or_panel')
                                if row['actor'] == 'smoke':
                                    require([t for t, _ in model.topics(panel.result, key)] == ['smoke']
                                            and panel.topic.findData('blink') < 0 and panel.topic.findData('flare') < 0
                                            and '另一实体' in model.player_text(panel.result),
                                            'smoke_has_only_own_topic_and_is_not_boss_second_form')
                                    require('未被阻挡' in text and '其它来源的隐匿或迷彩' in text,
                                            'smoke_conditions_do_not_claim_all_concealment_removed')
                                elif topic == 'flare':
                                    require(all(a in text for a in row['enemy']['abilities']) and '社区修正版' in text
                                            and '不会使其中所有单位' in text and '原文与修正均保留' in text,
                                            'game_handbook_and_community_antistealth_correction_separate')
                                if row['has_stage_overwrite']:
                                    require('通用文献的冷却、持续时间和数值不能直接视为本关实际值' in text
                                            and row['actual_effective_parameters'] is None,
                                            'whole_stage_overwrite_prevents_promoting_generic_parameters_to_current_result')
                                observations.append({'kind': 'topic', 'stage': sid, 'enemy_key': key, 'entity_id': row['entity_id'],
                                                     'topic': topic, 'card_title': card['title'], 'stage_overwrite': row['has_stage_overwrite']})
                                if sid == 'ro6_b_1' and row['actor'] == 'hanko' and topic == 'flare': shot('game-original-community-correction')
                                if sid == 'ro6_b_1_b' and row['actor'] == 'president' and topic == 'flare':
                                    require(row['raw_binding']['overwrittenData']['skills'][1]['blackboard'][0]['value'] == 30,
                                            'president_own_raw30_override_preserved_without_effective_duration_claim')
                                    shot('president-stage-override')
                                if sid == 'ro6_b_1' and row['actor'] == 'smoke': shot('independent-smoke')
                                if sid == 'ro6_t_4' and row['actor'] == 'president' and topic == 'attack':
                                    raw = row['raw_binding']['overwrittenData']['name']
                                    require(raw['m_defined'] is False and raw['m_value'] == '玻利瓦尔军官改'
                                            and row['enemy']['name'] == '“大总统”汉科'
                                            and row['enemy']['prefab_key'] == 'enemy_2139_shdbj2',
                                            'false_defined_meeting_placeholders_do_not_replace_real_name_or_prefab')
                                    shot('meeting-identity-placeholder')
                            request = model.related_entities(panel.result, key)[0]; choose(panel.related, request)
                            QTest.mouseClick(panel.related_button, Qt.MouseButton.LeftButton); gui.processEvents()
                            require(panel.selected_key == request['enemy_key'] and panel.stage_id == sid,
                                    'each_related_entity_click_uses_same_stage_exact_independent_reference')
                            reverse = model.related_entities(panel.result, panel.selected_key)[0]; choose(panel.related, reverse)
                            QTest.mouseClick(panel.related_button, Qt.MouseButton.LeftButton); gui.processEvents()
                            require(panel.selected_key == key, 'related_entity_roundtrip_returns_original_exact_actor')
                            observations.append({'kind': 'actor', 'stage': sid, 'enemy_key': key, 'entity_id': row['entity_id'],
                                                 'complete_binding': row['raw_binding']})
                    boss = next(r for r in panel.result['rows'] if r['actor'] != 'smoke')
                    panel.entities.select_value(boss['key']); panel.entities.select_branch('本关首领'); choose(panel.topic, 'flare')
                    dialog.resize(760, 440); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor = reader.textCursor()
                        cursor.setPosition(3); cursor.setPosition(15, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        scroll = reader.verticalScrollBar(); require(scroll.maximum() > 0, 'both_actor_readers_have_real_nonzero_range')
                        scroll.setValue(min(3, scroll.maximum())); prior = reading(reader); previous_view = view(); tab = panel.tabs.currentIndex()
                        require(prior['scroll'] > 0 and prior['position'] > prior['anchor'], 'both_readers_actual_nonzero_scroll_and_text_selection')
                        require(main_panel.refresh_reference(), 'actual_ordinary_stage_parent_refresh'); gui.processEvents()
                        require(reading(reader) == prior and view() == previous_view and panel.tabs.currentIndex() == tab,
                                'ordinary_parent_refresh_preserves_two_nonzero_readers_actor_branch_topic_related_and_tab')
                        refreshes.append({'before': prior, 'after': reading(reader), 'view': previous_view})
                    dialog.resize(1060, 840); gui.processEvents()
                    damaged = temporary / 'damaged-public'; manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST, *manifest['files']):
                        path = damaged / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((ROOT / name).read_bytes())
                    name = model.PACK + '/source-materials.json'; bad = damaged / name; original_bytes = bad.read_bytes()
                    original_file = model.battle.version._file
                    def own_file(name):
                        return damaged / name if name == model.MANIFEST or name in manifest['files'] else original_file(name)
                    with patch.object(model.battle.version, '_file', side_effect=own_file):
                        bad.write_bytes(original_bytes + b'x')
                        require(main_panel.refresh_reference(), 'ordinary_stage_source_stays_valid_on365_document_member_damage'); gui.processEvents()
                        require(panel.result is None and panel.selected_key is None and panel.entity_combo.currentData() is None
                                and panel.topic.count() == 0 and panel.related.count() == 0 and not panel.related_button.isEnabled()
                                and panel.player.toPlainText() == model.UNAVAILABLE and panel.technical.toPlainText() == ''
                                and panel.portrait.isHidden(), 'actual365_member_damage_clears_old_actor_picture_card_and_navigation')
                        shot('source-loss'); bad.write_bytes(original_bytes)
                        require(main_panel.refresh_reference(), 'actual_parent_document_recovery_refresh'); gui.processEvents()
                        require(panel.result is not None and panel.selected_key is None and panel.entity_combo.currentData() is None,
                                'source_recovery_requires_manual_actor_selection')
                    unrelated = next(e['key'] for e in battle.result['enemies'] if e['id'] not in model.ACTORS)
                    old_dialog = dialog; parent_enemy(unrelated)
                    require(battle.hanko_button.isHidden() and not old_dialog.isVisible(), 'changing_parent_enemy_hides_special_button_and_closes_owned_document')
                    select_stage('ro6_b_1'); open_actor(next(r['key'] for r in model.reference('ro6_b_1')['rows'] if r['actor'] == 'hanko'))
                    old_battle, old_dialog = battle_dialog, dialog
                    other = next(main_panel.entries.item(i) for i in range(main_panel.entries.count())
                                 if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole) == 'ro6_b_3')
                    main_panel.entries.setCurrentItem(other); gui.processEvents()
                    require(not old_battle.isVisible() and not old_dialog.isVisible(), 'changing_ordinary_stage_closes_current_battle_and_actor_tree')
                    select_stage('ro6_b_1'); open_actor(next(r['key'] for r in model.reference('ro6_b_1')['rows'] if r['actor'] == 'hanko'))
                    old_dialog = dialog
                    with patch.object(battle_model, 'stage_reference', return_value=None):
                        require(main_panel.refresh_reference(), 'ordinary_catalog_stays_readable_on_current_battle_source_failure'); gui.processEvents()
                        require(battle.result is None and not old_dialog.isVisible(), 'failed_current_battle_parent_closes_actor_tree')
                    select_stage('ro6_b_1'); open_actor(next(r['key'] for r in model.reference('ro6_b_1')['rows'] if r['actor'] == 'hanko'))
                    old_battle, old_dialog = battle_dialog, dialog; window.reference_panel('initial'); gui.processEvents()
                    require(not old_battle.isVisible() and not old_dialog.isVisible(), 'leaving_owning_common_page_closes_entire_current_actor_tree')
                    select_stage('ro6_b_1'); open_actor(next(r['key'] for r in model.reference('ro6_b_1')['rows'] if r['actor'] == 'hanko'))
                    require(window.run.state == state and window.battle_preview.context == context, 'temporary_run_and_old_battle_context_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(), 'all_seven_real_external_operations_zero'); native()
                    window.close(); gui.processEvents(); require(not battle_dialog.isVisible() and not dialog.isVisible(), 'actual_MainWindow_closes_current_battle_and_hanko_tree')
                    require(sum(r['kind'] == 'actor' for r in observations) == 12 and sum(r['kind'] == 'topic' for r in observations) == 24,
                            'all12_exact_actor_entries_and24_relevant_mechanism_cards_actually_read')
                    require(len(images) == 6, 'only_six_necessary_actual_screenshots'); done = True; gui.exit(0)
                except BaseException as error:
                    failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                    if dialog is not None: dialog.close()
                    window.close(); gui.exit(1)
            QTimer.singleShot(250, exercise); QTimer.singleShot(args.visible_ms, lambda: gui.exit(2) if not done else None)
            exitcode = gui.exec(); require(exitcode == 0 and done and not window.isVisible(), 'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        if window is not None: window.close()
    after = bound_files()
    result = {'section': 365, 'passed': done and failure is None and exitcode == 0 and before == after,
        'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None, 'qt_exit_code': exitcode,
        'verification_window_closed': window is not None and not window.isVisible(), 'unique_checks': len(checks), 'checks': checks,
        'actual_readings': observations, 'same_identity_refresh_observations': refreshes, 'screenshots': images,
        'source_sha256_before': before, 'source_sha256_after': after, 'source_scope_selected_not_all_transitive_dependencies': True,
        'external_operation_attempts': calls, 'temporary_state': True, 'private_contents_read_copied_or_restored': False,
        'game_operated': False, 'chat_sent': False, 'current_server_or_original_runtime_validated': False,
        'due365_full_validation_included': False, 'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
