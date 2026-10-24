"""Actual Windows current-enemy Elbert/Heretic/Firebrand entry and source limits."""
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
CANONICAL = 'scripts/verify_current_elbert_window_366.py'


def bound_files():
    from rouge import current_elbert_reference as model, current_battle_reference as battle, expansion_reference as version
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    for provider in (model, battle, version):
        names.add(provider.MANIFEST); names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update((CANONICAL, 'scripts/verify_full_available.py', 'tests/test_current_elbert_366.py',
                  'tests/test_current_elbert_view_366.py'))
    for name in ('scripts/build_current_elbert_366.py', 'verification/sections/366-preparation/scope.json'):
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
    before = bound_files(); checks = []; images = []; observations = []; refreshes = []; dialog_lifecycles = []
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
        import win32gui, win32process, win32con
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module, current_elbert_reference as model, current_battle_reference as battle_model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge366-public-') as folder, ExitStack() as stack:
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
            window.setWindowTitle('第366节 · 埃尔伯特与火种准确敌人入口（公开隔离验收）'); window.show(); gui.processEvents()
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
                previous = getattr(battle, 'elbert_dialog', None); parent_enemy(key)
                require(battle.elbert_button.isVisible() and battle.elbert_button.isEnabled(), 'specific_elbert_button_visible_only_for_exact_target')
                QTest.mouseClick(battle.elbert_button, Qt.MouseButton.LeftButton); gui.processEvents()
                dialog = battle.elbert_dialog; panel = dialog.panel
                require(dialog.isVisible() and panel.stage_id == battle.stage_id and panel.selected_key == key
                        and panel.result is not None and panel.result['battle_source_identity'] == battle.result['source_identity'],
                        'ordinary_selected_enemy_opens_exact_owned_elbert_document')
                require(previous is None or previous is not dialog and not previous.isVisible(), 'old_owned_actor_window_not_reused_across_new_open')
            def reading(widget):
                cursor = widget.textCursor()
                return {'anchor': cursor.anchor(), 'position': cursor.position(), 'selection': cursor.selectedText(),
                        'scroll': widget.verticalScrollBar().value()}
            def view():
                return {'stage': panel.stage_id, 'entity': panel.entity_combo.currentData(),
                        'branch': panel.entities.branch.currentData(), 'topic': panel.topic.currentData(),
                        'related': deepcopy(panel.related_request)}
            def closed_document_snapshot(owned):
                child = owned.panel
                picture = child.portrait.pixmap()
                return {'visible': owned.isVisible(), 'base_cleared': child.base is None,
                        'result_cleared': child.result is None, 'source_identity_cleared': child.source_identity is None,
                        'selected_key_cleared': child.selected_key is None, 'related_request_cleared': child.related_request is None,
                        'selector_unselected': child.entity_combo.currentData() is None, 'topic_count': child.topic.count(),
                        'topic_hidden': child.topic.isHidden(), 'related_hidden': child.related_button.isHidden(),
                        'related_disabled': not child.related_button.isEnabled(), 'portrait_hidden': child.portrait.isHidden(),
                        'portrait_cleared': child.portrait.text() == '' and (picture is None or picture.isNull()),
                        'player_cleared': child.player.toPlainText() == model.UNAVAILABLE,
                        'technical_cleared': child.technical.toPlainText() == '', 'tab_reset': child.tabs.currentIndex() == 0}
            def closed_document_is_empty(snapshot):
                return not snapshot['visible'] and snapshot['topic_count'] == 0 and all(
                    value for key, value in snapshot.items() if key not in ('visible', 'topic_count'))
            def exercise():
                nonlocal done, failure, panel, dialog
                try:
                    packet = model.packet(); require(packet is not None, 'own_complete_public_packet_available')
                    require(tuple(packet['data']['stages']) == model.STAGES and len(model.STAGES) == 4
                            and sum(len(s['entities']) for s in packet['data']['stages'].values()) == 8,
                            'four_exact_stage_configs_eight_original_enemy_references')
                    require(set(packet['data']['complete_cards']) == {'elbert', 'heretic', 'firebrand'},
                            'three_independent_complete_documentary_cards_and_tooltips_retained')
                    for sid, stage in packet['data']['stages'].items():
                        select_stage(sid)
                        for binding in stage['entities']:
                            key = binding['key']; open_actor(key); row = model.entity(panel.base, key)
                            parent = next(e for e in battle.result['enemies'] if e['key'] == key)
                            require(row['raw_binding'] == parent['raw_binding'] and row['enemy_id'] == parent['id']
                                    and row['level'] == parent['level'] and row['name'] == parent['name'],
                                    'every_actor_matches_complete_exact_current_parent_binding_and_identity')
                            require(all(panel.result[k] is None for k in ('actual_present', 'actual_phase', 'actual_target',
                                    'actual_blink', 'actual_fire_direction', 'actual_staff_position', 'actual_damage',
                                    'actual_clock', 'actual_received_buff')) and not panel.result['numerical_model_applied']
                                    and not panel.result['run_updated'],
                                    'reference_never_applies_actual_fire_curve_clock_staff_damage_or_panel')
                            raw_picture = battle_model.picture_bytes(panel.base['portraits'][sid].get(key)); pixmap = panel.portrait.pixmap()
                            require(bool(raw_picture) == bool(pixmap is not None and not pixmap.isNull()),
                                    'exact_verified_portrait_or_explicit_no_independent_image_without_substitution')
                            if sid == 'ro6_b_3' and row['kind'] == 'boss': shot('ordinary-enemy-entry', battle)
                            actual_topics = [panel.topic.itemData(i) for i in range(panel.topic.count())]
                            require(actual_topics == [t for t, _ in model.CARDS[row['kind']]],
                                    'boss_and_firebrand_have_only_their_own_mechanism_topics')
                            for topic, _label in model.CARDS[row['kind']]:
                                choose(panel.topic, topic); shown = json.loads(panel.technical.toPlainText())
                                text = panel.player.toPlainText(); card = model.selected_card(panel.result, key)
                                require(shown['exact_selected_entity'] == row and shown['complete_selected_mechanism_card'] == card
                                        and card['full_html'] and card['full_visible_text']
                                        and card['one_complete_current_visible_card_and_legacy_table_retained'] is True,
                                        'every_topic_keeps_own_whole_source_card_and_all_qualifying_tooltips')
                                require(shown['full_original_game_and_documentary_prose_kept_separately'] is True
                                        and all(shown[k] is None for k in ('actual_fire_direction', 'actual_staff_position', 'actual_damage', 'actual_clock'))
                                        and not shown['numerical_model_applied'],
                                        'source_card_and_raw_parameters_not_converted_into_actual_combat_results')
                                if row['kind'] == 'boss':
                                    if topic in ('overview', 'summon'):
                                        require('由火种在这份关卡里的配置决定' in text and '两种来源分别保留' in text
                                                and '不能直接用移动距离计算伤害' in text,
                                                'game_distance_summary_and_documentary_time_stage_rule_separate')
                                        require(all(battle_model.plain(a['text']) in battle.enemy_player.toPlainText()
                                                    for a in row['handbook']['abilityList']),
                                                'ordinary_parent_still_shows_exact_original_handbook_not_rewritten_document')
                                    if topic in ('overview', 'blink'):
                                        profile = panel.result['data']['profiles'][row['profile']]
                                        require('未被阻挡时才可触发' in text and '正常结束' in text and '下一个路径点' in text
                                                and '后摇' + profile['blink_recovery_text'] + '秒' in text
                                                and '之后冷却' + str(profile['blink_cooldown']) + '秒' in text
                                                and '不是整场战斗的绝对时间' in text,
                                                'ordinary30_vs_heretic75_blink_and_recovery_are_conditional_document_values')
                                        if sid == 'ro6_b_3' and topic == 'blink': shot('normal-blink-conditions')
                                    if topic in ('overview', 'staff'):
                                        require(all(term in text for term in ('退场后', '半径20', '攻击速度+50', '150%',
                                                '不是增加150%', '同名效果不叠加', '不证明本局已留下法杖')),
                                                'post_exit_staff_scope_final_move_multiplier_and_nonstack_are_reference_not_actual_buff')
                                        if sid == 'ro6_b_3_b' and topic == 'staff': shot('heretic-post-exit-staff')
                                    if sid == 'ro6_b_3':
                                        raw = row['raw_binding']['overwrittenData']['name']
                                        require(row['override_status'] == 'undefined_wrappers' and raw['m_defined'] is False
                                                and raw['m_value'] is None and row['name'] == '埃尔伯特',
                                                'all_false_normal_override_placeholders_do_not_replace_database_identity')
                                else:
                                    require(panel.topic.findData('blink') < 0 and panel.topic.findData('staff') < 0,
                                            'independent_firebrand_has_no_foreign_boss_controls')
                                    if topic in ('overview', 'collision'):
                                        require(all(term in text for term in ('半径0.25', '中心在触发的我方单位处', '然后自身退场',
                                                '中点判定', '不受迷彩', '不计算实际碰撞时间')),
                                                'firebrand_collision_center_qualifications_and_exit_not_map_footpoint_prediction')
                                    if topic in ('overview', 'configuration'):
                                        values = {r['key']: r['value'] for r in row['declared_configuration']['talentBlackboard']}
                                        if row['constructor'] == 'independent':
                                            require(row['raw_binding']['useDb'] is False
                                                    and (values['DamageAura.duration'], values['DamageAura.value'], values['DamageAura.circle']) == (6, 500, 1.5)
                                                    and row['declared_configuration'] == row['raw_binding']['overwrittenData']
                                                    and '不能直接套用上述10秒' in text and '不因为本关首领叫“异端”' in text
                                                    and '不按路程反算' in text,
                                                    'both_independent_firebrands_preserve6_500_1point5_without_default_or_direction_inference')
                                            if sid == 'ro6_b_3_b' and topic == 'configuration': shot('independent-firebrand')
                                        else:
                                            require((values['DamageAura.duration'], values['DamageAura.value'], values['DamageAura.circle']) == (10, 1000, 2)
                                                    and '这只证明固定资料对应' in text and '不直接输出一条伤害曲线' in text,
                                                    'both_database_firebrands_preserve10_1000_2_as_reference_not_actual_curve')
                                            if sid == 'ro6_b_3' and topic == 'configuration': shot('database-firebrand')
                                observations.append({'kind': 'topic', 'stage': sid, 'enemy_key': key,
                                    'enemy_id': row['enemy_id'], 'topic': topic, 'constructor': row['constructor'],
                                    'actual_damage': panel.result['actual_damage']})
                            request = deepcopy(panel.related_request)
                            require(request in model.related_entities(panel.base, key) and request['stage_id'] == sid,
                                    'related_request_names_only_the_exact_other_entity_in_same_stage')
                            QTest.mouseClick(panel.related_button, Qt.MouseButton.LeftButton); gui.processEvents()
                            require(panel.selected_key == request['enemy_key'] and panel.stage_id == sid,
                                    'actual_related_button_switches_to_exact_same_stage_entity')
                            QTest.mouseClick(panel.related_button, Qt.MouseButton.LeftButton); gui.processEvents()
                            require(panel.selected_key == key, 'bidirectional_related_click_returns_original_exact_entity')
                            observations.append({'kind': 'actor', 'stage': sid, 'enemy_key': key, 'enemy_id': row['enemy_id'],
                                                 'complete_binding': row['raw_binding']})
                    # Send the native close command used by the title-bar X to the verified owned HWND.
                    # No foreground, game, browser, chat or other application's window is touched.
                    open_actor('0'); closed = dialog; before_close_source = panel.source_identity
                    close_native = native(closed)
                    win32gui.SendMessage(close_native['hwnd'], win32con.WM_SYSCOMMAND, win32con.SC_CLOSE, 0)
                    gui.processEvents(); snapshot = closed_document_snapshot(closed)
                    require(closed_document_is_empty(snapshot), 'native_titlebar_X_command_clears_owned_document_picture_topics_and_related_state')
                    require(window.isVisible() and battle_dialog.isVisible() and battle.result is not None
                            and battle.elbert_button.isVisible() and battle.elbert_button.isEnabled(),
                            'native_titlebar_X_leaves_owning_battle_and_reopen_entry_usable')
                    open_actor('0')
                    require(dialog is not closed and panel.base is not None and panel.result is not None
                            and panel.selected_key == '0' and panel.source_identity == before_close_source
                            and panel.result['battle_source_identity'] == battle.result['source_identity']
                            and closed_document_is_empty(closed_document_snapshot(closed)),
                            'ordinary_entry_reopens_new_exact_document_after_titlebar_X_without_reviving_closed_content')
                    dialog_lifecycles.append({'method': 'native_titlebar_X_system_close_command',
                        'native_before': close_native, 'closed_state': snapshot, 'reopened_exact_stage': panel.stage_id,
                        'reopened_enemy_key': panel.selected_key, 'source_identity_preserved': panel.source_identity == before_close_source})
                    closed = dialog; before_close_source = panel.source_identity; escape_native = native(closed)
                    QTest.keyClick(closed, Qt.Key.Key_Escape); gui.processEvents(); snapshot = closed_document_snapshot(closed)
                    require(closed_document_is_empty(snapshot), 'actual_Escape_key_clears_owned_document_picture_topics_and_related_state')
                    require(window.isVisible() and battle_dialog.isVisible() and battle.result is not None
                            and battle.elbert_button.isVisible() and battle.elbert_button.isEnabled(),
                            'actual_Escape_leaves_owning_battle_and_reopen_entry_usable')
                    open_actor('0')
                    require(dialog is not closed and panel.base is not None and panel.result is not None
                            and panel.selected_key == '0' and panel.source_identity == before_close_source
                            and panel.result['battle_source_identity'] == battle.result['source_identity']
                            and closed_document_is_empty(closed_document_snapshot(closed)),
                            'ordinary_entry_reopens_new_exact_document_after_Escape_without_reviving_closed_content')
                    dialog_lifecycles.append({'method': 'actual_QTest_Escape_key',
                        'native_before': escape_native, 'closed_state': snapshot, 'reopened_exact_stage': panel.stage_id,
                        'reopened_enemy_key': panel.selected_key, 'source_identity_preserved': panel.source_identity == before_close_source})
                    boss = next(r for r in panel.base['entities'] if r['kind'] == 'boss')
                    panel.entities.select_value(boss['key']); panel.entities.select_branch('本关首领'); choose(panel.topic, 'staff')
                    dialog.resize(760, 440); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor = reader.textCursor()
                        cursor.setPosition(3); cursor.setPosition(15, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        scroll = reader.verticalScrollBar(); require(scroll.maximum() > 0, 'both_actor_readers_have_real_nonzero_range')
                        scroll.setValue(min(3, scroll.maximum())); prior = reading(reader); previous_view = view(); tab = panel.tabs.currentIndex()
                        require(prior['scroll'] > 0 and prior['position'] > prior['anchor'], 'both_readers_actual_nonzero_scroll_and_text_selection')
                        require(main_panel.refresh_reference(), 'actual_ordinary_stage_parent_refresh'); gui.processEvents()
                        require(reading(reader) == prior and view() == previous_view and panel.tabs.currentIndex() == tab,
                                'ordinary_parent_refresh_preserves_two_nonzero_readers_entity_branch_topic_related_and_tab')
                        refreshes.append({'before': prior, 'after': reading(reader), 'view': previous_view})
                    dialog.resize(1080, 825); gui.processEvents()
                    damaged = temporary / 'damaged-public'; manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST, *manifest['files']):
                        path = damaged / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((ROOT / name).read_bytes())
                    bad = damaged / (model.PACK + '/firebrand-page.html'); original_bytes = bad.read_bytes()
                    original_read = model._read_public
                    def own_read(name):
                        return (damaged / name).read_bytes() if name == model.MANIFEST or name in manifest['files'] else original_read(name)
                    with patch.object(model, '_read_public', side_effect=own_read):
                        bad.write_bytes(original_bytes + b'x')
                        require(main_panel.refresh_reference(), 'ordinary_stage_and314_parent_source_stay_valid_on366_own_document_damage'); gui.processEvents()
                        require(panel.base is None and panel.result is None and panel.selected_key is None
                                and panel.entity_combo.currentData() is None and panel.topic.count() == 0
                                and panel.related_request is None and not panel.related_button.isEnabled()
                                and panel.topic.isHidden() and panel.related_button.isHidden()
                                and panel.player.toPlainText() == model.UNAVAILABLE and panel.technical.toPlainText() == ''
                                and panel.portrait.isHidden(), 'actual366_member_damage_clears_actor_picture_topics_related_request_and_readers')
                        shot('source-loss'); bad.write_bytes(original_bytes)
                        require(main_panel.refresh_reference(), 'actual_parent_document_recovery_refresh'); gui.processEvents()
                        require(panel.base is not None and panel.selected_key is None and panel.entity_combo.currentData() is None,
                                'restored_source_requires_manual_boss_or_firebrand_selection')
                    unrelated = next(e['key'] for e in battle.result['enemies'] if e['id'] not in model.PROFILES)
                    old_dialog = dialog; parent_enemy(unrelated)
                    require(battle.elbert_button.isHidden() and not old_dialog.isVisible(), 'changing_parent_enemy_hides_special_button_and_closes_owned_document')
                    select_stage('ro6_b_3'); open_actor('0'); old_battle, old_dialog = battle_dialog, dialog
                    other = next(main_panel.entries.item(i) for i in range(main_panel.entries.count())
                                 if main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole) == 'ro6_b_1')
                    main_panel.entries.setCurrentItem(other); gui.processEvents()
                    require(not old_battle.isVisible() and not old_dialog.isVisible(), 'changing_ordinary_stage_closes_current_battle_and_elbert_tree')
                    select_stage('ro6_b_3'); open_actor('0'); old_dialog = dialog
                    with patch.object(battle_model, 'stage_reference', return_value=None):
                        require(main_panel.refresh_reference(), 'ordinary_catalog_stays_readable_on_current_battle_parent_failure'); gui.processEvents()
                        require(battle.result is None and not old_dialog.isVisible(), 'failed_current_battle_parent_closes_elbert_tree')
                    select_stage('ro6_b_3'); open_actor('0'); old_battle, old_dialog = battle_dialog, dialog
                    window.reference_panel('initial'); gui.processEvents()
                    require(not old_battle.isVisible() and not old_dialog.isVisible(), 'leaving_owning_common_page_closes_entire_current_elbert_tree')
                    select_stage('ro6_b_3'); open_actor('0')
                    require(window.run.state == state and window.battle_preview.context == context, 'temporary_run_and_old_battle_context_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(), 'all_seven_real_external_operations_zero'); native()
                    window.close(); gui.processEvents()
                    require(not battle_dialog.isVisible() and not dialog.isVisible(), 'actual_MainWindow_closes_current_battle_and_elbert_tree')
                    require(sum(r['kind'] == 'actor' for r in observations) == 8 and sum(r['kind'] == 'topic' for r in observations) == 28,
                            'all8_exact_actor_entries_and28_relevant_mechanism_topics_actually_read')
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
    result = {'section': 366, 'passed': done and failure is None and exitcode == 0 and before == after,
        'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None, 'qt_exit_code': exitcode,
        'verification_window_closed': window is not None and not window.isVisible(), 'unique_checks': len(checks), 'checks': checks,
        'actual_readings': observations, 'same_identity_refresh_observations': refreshes, 'screenshots': images,
        'direct_dialog_close_and_reopen_observations': dialog_lifecycles,
        'source_sha256_before': before, 'source_sha256_after': after, 'source_scope_selected_not_all_transitive_dependencies': True,
        'external_operation_attempts': calls, 'temporary_state': True, 'private_contents_read_copied_or_restored': False,
        'game_operated': False, 'chat_sent': False, 'current_server_or_original_runtime_validated': False,
        'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
