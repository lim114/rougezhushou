"""Actual Windows exact guest-boss conditions, source and owned reader boundaries."""
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
CANONICAL = 'scripts/verify_current_guest_knights_window_377.py'


def bound_files():
    from rouge import current_guest_knights as model, current_battle_reference as battle, expansion_reference as version, current_map_position as maps, current_terrain as terrain
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    for provider in (model,battle,version,maps,terrain):
        names.add(provider.MANIFEST); names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update((CANONICAL, 'scripts/verify_full_available.py', 'tests/test_current_guest_knights_377.py',
                  'tests/test_current_guest_knights_view_377.py'))
    for name in ('scripts/build_current_guest_knights_377.py', 'verification/sections/377-preparation/scope.json'):
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
    parser.add_argument('--visible-ms', type=int, default=180000); args = parser.parse_args()
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
        from rouge import app as app_module, current_guest_knights as model, current_battle_reference as battle_model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge377-public-') as folder, ExitStack() as stack:
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
            window.setWindowTitle('第377节 · 恶意讨薪 · 双骑士联动与完整招式（公开隔离验收）'); window.show(); gui.processEvents()
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
                previous = getattr(battle, 'guest_knights_dialog', None); parent_enemy(key)
                require(battle.guest_knights_button.isVisible() and battle.guest_knights_button.isEnabled(), 'specific_guest_knights_button_visible_only_for_exact_target')
                QTest.mouseClick(battle.guest_knights_button, Qt.MouseButton.LeftButton); gui.processEvents()
                dialog = battle.guest_knights_dialog; panel = dialog.panel
                require(dialog.isVisible() and panel.stage_id == battle.stage_id and panel.selected_key == key
                        and panel.result is not None and panel.result['battle_source_identity'] == battle.result['source_identity'],
                        'ordinary_selected_enemy_opens_exact_owned_guest_knights_document')
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
                nonlocal done,failure,panel,dialog
                try:
                    packet=model.packet();require(packet is not None,'own_complete_current_public_source_packet')
                    total=sum(len(v['rows'])for v in packet['data']['bindings'].values())
                    require(total==8 and len(packet['data']['bindings'])==4,'all_current_stage_aliases_and_exact_reference_count')
                    require(sum(len(v['cards'])for v in packet['data']['materials'].values())==8,'all_original_document_level_cards_retained')
                    first=True;topic_counts=0;actor_counts=0
                    for sid,group in packet['data']['bindings'].items():
                        select_stage(sid)
                        for binding in group['rows']:
                            key=binding['key'];open_actor(key);row=model.entity(panel.result,key);actor_counts+=1
                            parent=next(r for r in battle.result['enemies']if r['key']==key)
                            require(row['enemy']==parent and row['raw_binding']==parent['raw_binding'],'every_current_exact_parent_identity_and_full_override_preserved')
                            require(all(panel.result[k]is None for k in('actual_present','actual_form','actual_skill_time','actual_partner_retired','actual_shield','expected_stats'))
                                and not panel.result['numeric_model_added']and not panel.result['run_updated'],'document_conditions_never_become_actual_mode_clock_shield_or_stats')
                            raw=battle_model.picture_bytes(row['enemy']['portrait']);pix=panel.portrait.pixmap()
                            require(bool(raw)==bool(pix is not None and not pix.isNull()),'exact_original_portrait_no_same_name_substitution')
                            if first:shot('ordinary-current-enemy-entry',battle);first=False
                            for topic,label in model.topics(panel.result,key):
                                choose(panel.topic,topic);card=model.selected_card(panel.result,key,topic);technical=json.loads(panel.technical.toPlainText());text=panel.player.toPlainText();topic_counts+=1
                                require(technical['current_reference']==row and technical['selected_document_card']==card
                                    and technical['complete_actor_source_cards']==panel.result['data']['materials'][row['actor']],'every_topic_selects_exact_level_full_original_document')
                                require(card['complete_DOM'].startswith('<div')and card['complete_DOM'].endswith('</div>')
                                    and technical['actual_skill_time']is None and '最终预测值仍未知'in text,'complete_original_and_unknown_current_panel_kept_separate')
                                if 377==377:
                                    require(row['level']==1,'knights_current_level1_not_old_same_named_stage')
                                    if topic=='relation':require('进入终点'in text and '80%'in text,'partner_goal_entry_and_death_both_retained')
                                    if row['actor']=='wither'and topic=='skill':require('2.5秒'in text and '最多选择三名'in text,'blast_delay_is_after_impact_not_stage_clock')
                                elif 377==379:
                                    require(row['level']==0,'crystal_exact_level0_and_independent_actor')
                                    if row['actor']=='flying'and topic=='shield':require('60层'in text and '最多80层'in text and '图鉴概括说80次'in text,'sixty_added_eighty_cap_not_silently_overwriting_handbook')
                                    if topic=='mode':require('生息演算'in text and '不把'in text,'RA_universal_behaviour_not_promoted_to_IS_instance')
                                else:
                                    require(row['level']==0,'material_current_level0_not_other_level_document')
                                    if topic=='shield':require('80秒'in text and '40秒'in text and '3333'in text and '9999'in text,'shield_level_and_dynamic_parameter_not_invented_value')
                                    if topic=='bomb':require('最多'in text and '20秒'in text and '31秒'in text,'bomb_target_and_distinct_initial_cooldown')
                                    if topic=='interfere':require('最少'in text and '35秒'in text and '31秒'in text,'interference_target_and_distinct_initial_cooldown')
                                observations.append({'stage':sid,'enemy_key':key,'entity_id':row['entity_id'],'level':row['level'],'topic':topic,'card_index':card['index']})
                                if sid==model.STAGES[0]:shot('first-'+row['actor']+'-'+topic)
                            requests=model.related_entities(panel.result,key)
                            if requests:
                                choose(panel.related,requests[0]);QTest.mouseClick(panel.related_button,Qt.MouseButton.LeftButton);gui.processEvents()
                                require(panel.selected_key==requests[0]['enemy_key']and panel.stage_id==sid,'related_exact_partner_click_stays_same_current_stage')
                            else:require(not panel.related_button.isEnabled(),'no_unrelated_partner_or_other_boss_option')
                    require(actor_counts==total and topic_counts==16,'all_exact_entries_and_their_own_topics_actually_read')
                    sid=model.STAGES[0];select_stage(sid);open_actor(model.reference(sid)['rows'][0]['key']);choose(panel.topic,model.topics(panel.result,panel.selected_key)[0][0])
                    dialog.resize(760,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(15,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
                        require(reader.verticalScrollBar().maximum()>0,'both_readers_have_actual_nonzero_scroll_range')
                        reader.verticalScrollBar().setValue(min(3,reader.verticalScrollBar().maximum()));prior=reading(reader);old_view=view();tab=panel.tabs.currentIndex()
                        require(prior['scroll']>0 and prior['position']>prior['anchor'],'actual_text_selection_and_nonzero_scroll_before_parent_refresh')
                        require(main_panel.refresh_reference(),'actual_current_ordinary_stage_parent_refresh');gui.processEvents()
                        require(reading(reader)==prior and view()==old_view and panel.tabs.currentIndex()==tab,'true_parent_refresh_preserves_both_nonzero_readings_and_selection_topic_tab')
                        refreshes.append({'before':prior,'after':reading(reader),'view':old_view})
                    dialog.resize(1060,840);gui.processEvents();require(panel.map_button.isEnabled(),'accurate_current_fixed_map_entry_available')
                    QTest.mouseClick(panel.map_button,Qt.MouseButton.LeftButton);gui.processEvents();owned_map=panel.map_dialog
                    require(owned_map is not None and owned_map.isVisible()and owned_map.panel.stage_id==sid
                        and owned_map.panel.result['current_level_key']==panel.result['level_key'],'actual_owned_map_uses_same_stage_and_exact_current_level')
                    shot('accurate-owned-fixed-map',owned_map.panel)
                    owned_map.close();gui.processEvents()
                    require(not owned_map.isVisible()and owned_map.panel.result is None,'direct_owned_fixed_map_X_clears_actual_data')
                    QTest.mouseClick(panel.map_button,Qt.MouseButton.LeftButton);gui.processEvents();owned_map=panel.map_dialog
                    QTest.keyClick(owned_map,Qt.Key.Key_Escape);gui.processEvents()
                    require(not owned_map.isVisible()and owned_map.panel.result is None,'actual_owned_fixed_map_Escape_clears_actual_data')
                    QTest.mouseClick(panel.map_button,Qt.MouseButton.LeftButton);gui.processEvents();owned_map=panel.map_dialog
                    require(owned_map.isVisible()and owned_map.panel.result is not None,'manual_fixed_map_reopen_before_source_loss')
                    damaged=temporary/'damaged-public';manifest=json.loads((ROOT/model.MANIFEST).read_bytes())
                    for name in(model.MANIFEST,*manifest['files']):
                        target=damaged/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
                    bad=damaged/(model.PACK+'/reference-data.json');original_bytes=bad.read_bytes();real_file=model.battle.version._file
                    def own_file(name):return damaged/name if name==model.MANIFEST or name in manifest['files']else real_file(name)
                    with patch.object(model.battle.version,'_file',side_effect=own_file):
                        bad.write_bytes(original_bytes+b'x');require(main_panel.refresh_reference(),'ordinary_parent_survives_guest_document_source_damage');gui.processEvents()
                        require(panel.result is None and panel.selected_key is None and panel.entity_combo.currentData()is None
                            and panel.topic.count()==panel.related.count()==0 and panel.player.toPlainText()==model.UNAVAILABLE
                            and panel.technical.toPlainText()==''and panel.portrait.isHidden()and not panel.map_button.isEnabled()
                            and owned_map.panel.result is None and not owned_map.isVisible(),'damaged_source_clears_actual_document_portrait_navigation_and_owned_map_tree')
                        shot('source-loss');bad.write_bytes(original_bytes)
                        require(main_panel.refresh_reference(),'actual_parent_source_recovery');gui.processEvents()
                        require(panel.result is not None and panel.selected_key is None,'source_recovery_keeps_manual_reselection_requirement')
                    open_actor(model.reference(sid)['rows'][0]['key']);old_dialog=dialog
                    unrelated=next(e['key']for e in battle.result['enemies']if e['id']not in model.ACTORS);parent_enemy(unrelated)
                    require(battle.guest_knights_button.isHidden()and not old_dialog.isVisible()and old_dialog.panel.result is None,'ordinary_other_enemy_has_no_guest_special_options_or_stale_document')
                    open_actor(model.reference(sid)['rows'][0]['key']);old_dialog=dialog
                    with patch.object(battle_model,'stage_reference',return_value=None):
                        require(main_panel.refresh_reference(),'ordinary_catalog_survives_failed_battle_source');gui.processEvents()
                        require(battle.result is None and not old_dialog.isVisible()and old_dialog.panel.result is None,'failed_battle_source_clears_owned_actual_reader_tree')
                    select_stage(sid);open_actor(model.reference(sid)['rows'][0]['key']);old_dialog=dialog;old_battle=battle_dialog
                    window.reference_panel('initial');gui.processEvents();require(not old_dialog.isVisible()and old_dialog.panel.result is None and not old_battle.isVisible(),'leaving_common_page_closes_owned_battle_reader_tree')
                    select_stage(sid);open_actor(model.reference(sid)['rows'][0]['key']);closing=dialog;closing.close();gui.processEvents()
                    require(not closing.isVisible()and closing.panel.result is None,'direct_dialog_X_clears_actual_source')
                    open_actor(model.reference(sid)['rows'][0]['key']);closing=dialog;QTest.keyClick(closing,Qt.Key.Key_Escape);gui.processEvents()
                    require(not closing.isVisible()and closing.panel.result is None,'actual_Escape_clears_actual_source')
                    open_actor(model.reference(sid)['rows'][0]['key']);require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_numeric_context_unchanged')
                    require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero')
                    native();window.close();gui.processEvents();require(not dialog.isVisible()and dialog.panel.result is None and not battle_dialog.isVisible(),'actual_main_close_clears_guest_reader_and_current_battle')
                    require(len(images)==7,'only_planned_actual_necessary_screenshot_paths');done=True;gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    if dialog is not None:dialog.close()
                    window.close();gui.exit(1)
            QTimer.singleShot(250, exercise); QTimer.singleShot(args.visible_ms, lambda: gui.exit(2) if not done else None)
            exitcode = gui.exec(); require(exitcode == 0 and done and not window.isVisible(), 'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        if window is not None: window.close()
    after = bound_files()
    result = {'section': 377, 'passed': done and failure is None and exitcode == 0 and before == after,
        'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None, 'qt_exit_code': exitcode,
        'verification_window_closed': window is not None and not window.isVisible(), 'unique_checks': len(checks), 'checks': checks,
        'actual_readings': observations, 'same_identity_refresh_observations': refreshes, 'screenshots': images,
        'source_sha256_before': before, 'source_sha256_after': after, 'source_scope_selected_not_all_transitive_dependencies': True,
        'external_operation_attempts': calls, 'temporary_state': True, 'private_contents_read_copied_or_restored': False,
        'game_operated': False, 'chat_sent': False, 'current_server_or_original_runtime_validated': False,
        'due377_full_validation_included': False, 'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
