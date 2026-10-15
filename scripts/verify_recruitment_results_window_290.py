"""Native isolated MainWindow: four documented recruitment alternatives.

Run only the canonical reviewed script after root freezes source. This fixture
does not enumerate a game window, sample a game, open a chat or read private state.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback
import types
from unittest.mock import patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
PACKET = ROOT / 'research/p3-choice-recruitment-290'
TARGET = 'community_group_018'
SCENE = TARGET + ':scene:0'
CHOICE = SCENE + ':choice:1'
TITLE = '可靠的中介值得信任'
PAIRS = [['先锋', '近卫'], ['重装', '辅助'], ['医疗', '狙击'], ['术师', '特种']]
ORIGINAL_IDS = ['choice_ro6_hire1_1', 'choice_ro6_hire1_4',
                'choice_ro6_hire1_5', 'choice_ro6_hire1_6']
PRIOR = 'verification/sections/290-preparation/prior-289/rouge/event_planning.py'
PRIOR_SHA = 'abf3dadb856accb9f7239aa98cedda2c66fd9476e331592fa89438b25418782b'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve the first actual receipt; use a new path.')
    if args.visible_ms <= 0:
        raise ValueError('--visible-ms must be positive.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    screenshots = [destination.with_name(destination.stem + suffix)
                   for suffix in ('-01-player.png', '-02-evidence.png')]
    for image in screenshots:
        if image.exists():
            raise FileExistsError('Preserve the first actual screenshot: ' + str(image))
    checks, stages, observations = [], [], []
    executions = 0
    before, after = {}, {}
    qpa, failure, qt_exit = None, None, None
    done, closed = False, False
    started = datetime.now(timezone.utc).isoformat()

    def require(condition, name):
        nonlocal executions
        if not condition:
            raise AssertionError(name)
        executions += 1
        if name not in checks:
            checks.append(name)

    def bound_files():
        files = {
            'rouge/app.py', 'rouge/ui_state.py', 'rouge/node_catalog.py',
            'rouge/node_catalog_view.py', 'rouge/player_node_information.py',
            'rouge/event_planning.py', 'rouge/choice_held_requirements.py',
            'rouge/node_rewards.py', 'rouge/event_named_reward_links.py',
            'rouge/choice_recruitment_results.py',
            'rouge/data/choice-recruitment-results.json',
            'rouge/data/node-catalog.json', 'rouge/data/node-reward-reference.json',
            'rouge/data/node-events.json', 'rouge/data/event-planning-reference.json',
            'rouge/data/event-current-observation.json', 'rouge/data/original-entry-reference.json',
            'scripts/build_choice_recruitment_results_290.py',
            'scripts/verify_recruitment_results_window_290.py', PRIOR,
        }
        if not PACKET.is_dir():
            raise FileNotFoundError('The reviewed recruitment source packet has not been promoted.')
        for path in PACKET.rglob('*'):
            if path.is_symlink():
                raise ValueError('The public packet must contain regular original files.')
            if path.is_file():
                files.add(path.relative_to(ROOT).as_posix())
        manifest_path = PACKET / 'source-manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf8'))
        for name in manifest['files']:
            path = ROOT / name
            if path.resolve().is_relative_to(ROOT.resolve()) is False or path.is_symlink():
                raise ValueError('Manifest dependencies must be regular files within the project.')
            files.add(path.relative_to(ROOT).as_posix())
        tests = sorted((ROOT / 'tests').glob('test_*290*.py'))
        if not tests:
            raise FileNotFoundError('Section290 necessary tests must exist before window verification.')
        files.update(path.relative_to(ROOT).as_posix() for path in tests)
        return {name: sha(ROOT / name) for name in sorted(files)}

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Original Windows is required; Wine/offscreen is not native validation.')
        if Path(__file__).resolve() != (ROOT / 'scripts/verify_recruitment_results_window_290.py').resolve():
            raise RuntimeError('Use the canonical reviewed script in scripts/.')
        from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        import win32gui
        import win32process
        from rouge import app as app_module
        from rouge import node_catalog as catalog
        from rouge import event_planning, choice_recruitment_results

        before = bound_files()
        require(choice_recruitment_results.source_data() is not None,
                'fresh_recruitment_source_packet_valid')
        prior_raw = (ROOT / PRIOR).read_bytes()
        require(hashlib.sha256(prior_raw).hexdigest() == PRIOR_SHA,
                'original_289_eligibility_source_exact_bytes')
        previous = types.ModuleType('rouge._window290_prior_event_planning')
        previous.__package__ = 'rouge'
        previous.__file__ = str(ROOT / 'rouge/event_planning.py')
        exec(compile(prior_raw, str(ROOT / PRIOR), 'exec'), previous.__dict__)
        original_event = deepcopy(catalog._event(TARGET))
        original_choice = deepcopy(catalog._scene(TARGET, SCENE)['choices'][1])
        require(original_choice['key'] == CHOICE and original_choice['title'] == TITLE,
                'exact_documented_event_scene_and_choice')
        require(original_choice['game_choice_ids'] == [] and '??或??' in original_choice['description'],
                'raw_catalog_keeps_empty_ids_and_original_placeholder')
        gui = QApplication([])
        qpa = gui.platformName()
        require(qpa == 'windows', 'actual_native_windows_qpa')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        def forbidden(*_args, **_kwargs):
            raise AssertionError('Game enumeration is forbidden in this public fixture.')

        with tempfile.TemporaryDirectory(prefix='rouge-290-recruitment-') as directory, \
                patch.object(app_module, 'list_game_windows', side_effect=forbidden):
            temporary = Path(directory)
            app_module.ROOT = temporary
            app_module.SETTINGS = temporary / 'settings.json'
            app_module.OPERATOR_STATE = temporary / 'operators.json'
            app_module.RUN_STATE = temporary / 'run.json'
            window = PublicWindow()
            window.setWindowTitle('第290节 · 临时中介所四种职业结果（公开隔离验收）')
            window.resize(1440, 930)
            window.show()
            panel, tabs = window.node_catalog, window.centralWidget()
            saved = None
            isolated_run = deepcopy(window.run.state)

            def isolated():
                require(not window.auto.isChecked(), 'automatic_game_sampling_disabled')
                require(not window.timer.isActive(), 'game_sampling_timer_inactive')
                require(window.capture.target is None, 'no_game_capture_target')
                require(window.desktop.process is None, 'desktop_chat_backend_not_started')

            def native_window():
                handle = int(window.winId())
                thread, process = win32process.GetWindowThreadProcessId(handle)
                require(bool(win32gui.IsWindow(handle)), 'actual_win32_hwnd_exists')
                require(bool(win32gui.IsWindowVisible(handle)) and window.isVisible(),
                        'actual_win32_hwnd_visible')
                require(process == os.getpid(), 'actual_win32_hwnd_owned_by_fixture_process')
                require(not bool(win32gui.IsIconic(handle)), 'verification_window_not_minimized')
                return {'hwnd': handle, 'process_id': process, 'thread_id': thread,
                        'visible': True, 'caption': win32gui.GetWindowText(handle),
                        'rectangle': list(win32gui.GetWindowRect(handle)), 'qpa': qpa}

            def reading(widget):
                cursor = widget.textCursor()
                return {'text_sha256': hashlib.sha256(widget.toPlainText().encode('utf8')).hexdigest(),
                        'anchor': cursor.anchor(), 'position': cursor.position(),
                        'selected_text': cursor.selectedText(),
                        'vertical': widget.verticalScrollBar().value(),
                        'horizontal': widget.horizontalScrollBar().value()}

            def snapshot():
                return {'main_tab': tabs.currentIndex(), 'reading_tab': panel.reading_tabs.currentIndex(),
                        'kind': panel.kind.currentData(), 'node_type': panel.node_type.currentData(),
                        'floor': panel.floor.currentData(), 'search_text': panel.search.text(),
                        'search_cursor': panel.search.cursorPosition(),
                        'search_selection_start': panel.search.selectionStart(),
                        'search_selected_text': panel.search.selectedText(),
                        'selected_key': panel.list.selected_key(), 'detail_key': panel.detail_key,
                        'expanded_groups': sorted(panel.list.expanded_groups()),
                        'tree_scroll': panel.list.verticalScrollBar().value(),
                        'player': reading(panel.player_detail), 'evidence': reading(panel.detail),
                        'runtime_context': deepcopy(panel.runtime_context)}

            def prime(widget, label):
                require(widget.document().characterCount() > 30, label + '_real_formatter_text_available')
                cursor = widget.textCursor()
                cursor.setPosition(1)
                cursor.setPosition(8, QTextCursor.MoveMode.KeepAnchor)
                widget.setTextCursor(cursor)
                panel.search.setSelection(0, 2)
                gui.processEvents()
                bar = widget.verticalScrollBar()
                require(bar.maximum() > 0, label + '_actual_scroll_range_nonzero')
                bar.setValue(max(1, bar.maximum() // 2))
                gui.processEvents()
                require(bar.value() > 0 and bool(widget.textCursor().selectedText()),
                        label + '_actual_nonzero_scroll_and_nonempty_text_selection')
                require(bool(panel.search.selectedText()), label + '_actual_search_text_selection')

            def selected_entry():
                entry = next(row for row in panel.entries if row['key'] == panel.list.selected_key())
                require(entry['kind'] == 'event' and entry['record']['id'] == TARGET,
                        'actual_directory_selection_is_exact_recruitment_event')
                return entry

            def recruitment_contract():
                entry = selected_entry()
                context = panel._event_context(entry['record'])
                current = event_planning.choice_eligibility(TARGET, SCENE, context)
                target = next(row for row in current['rows'] if row['choice_key'] == CHOICE)
                reference = target['recruitment_result_reference']
                require(reference['status'] == 'documented_reference'
                        and reference['annotation_role'] == 'selection_result'
                        and reference['reference_kind'] == 'documented_recruitment_result_variants',
                        'actual_choice_uses_documented_result_annotation')
                require(reference['variants_are_alternatives'] is True
                        and len(reference['variants']) == 4,
                        'four_alternative_result_groups_not_four_simultaneous_grants')
                require([v['profession_pair'] for v in reference['variants']] == PAIRS
                        and [v['original_choice_id'] for v in reference['variants']] == ORIGINAL_IDS,
                        'four_exact_profession_pairs_match_four_original_records')
                for number, variant in enumerate(reference['variants'], 1):
                    require((variant['hope_gain_reference'], variant['recruit_count_reference'],
                             variant['rarity_ceiling_reference'], variant['upgrade_reference_text']) ==
                            (2, 1, 5, '直升'), f'variant_{number}_literal_amount_rarity_and_upgrade_text')
                    require(bool(variant['original_record']) and bool(variant['source_reference']),
                            f'variant_{number}_retains_original_record_and_provenance')
                require((reference['hope_gain_reference'], reference['recruit_count_reference'],
                         reference['rarity_ceiling_reference'], reference['upgrade_reference_text']) ==
                        (2, 1, 5, '直升'), 'top_level_amount_is_one_selection_not_sum_of_variants')
                unknowns = ('actual_selectable', 'actual_result_variant', 'actual_recruited_operator',
                            'actual_hope_gain', 'actual_cultivation', 'actual_granted', 'recruitment_cost')
                require(all(reference[key] is None for key in unknowns),
                        'actual_variant_operator_cost_cultivation_and_grants_remain_unknown')
                require(reference['original_entry_scene_verified'] is False
                        and reference['source_scene_link_verified'] is False
                        and reference['full_recruitment_pool_known'] is False
                        and reference['current_server_verified'] is False,
                        'document_reference_does_not_close_original_entry_or_server_gaps')
                require(target['unparsed_condition_text'] is None
                        and target['conditional_text'] == original_choice['conditional']
                        and target['game_choice_ids'] == [] and target['actual_selectable'] is None,
                        'result_annotation_preserves_raw_condition_empty_ids_and_unknown_availability')
                normalized = deepcopy(current)
                changed = next(row for row in normalized['rows'] if row['choice_key'] == CHOICE)
                changed.pop('recruitment_result_reference')
                changed['unparsed_condition_text'] = changed['conditional_text']
                require(normalized == previous.choice_eligibility(TARGET, SCENE, context),
                        'entire_original_eligibility_result_unchanged_except_result_annotation')
                resources = event_planning.choice_resources(TARGET, SCENE, context)
                resource_row = next(row for row in resources['rows'] if row['choice_key'] == CHOICE)
                amounts = resource_row['resource_references']
                require(len(amounts) == 1 and amounts[0]['kind'] == 'nominal_gain_or_recovery'
                        and amounts[0]['resource'] == 'hope' and amounts[0]['quantity_reference'] == 2
                        and amounts[0]['actual_changed'] is None,
                        'resource_model_keeps_one_documented_two_hope_gain')
                require(resource_row['actual_new_resources'] is None,
                        'reference_never_applies_actual_resource_change')
                require(catalog._event(TARGET) == original_event,
                        'original_catalog_choice_ids_and_all_scene_text_unchanged')
                return reference

            def player_contract():
                text = panel.player_detail.toPlainText()
                start = '选项 2：' + TITLE
                end = '选项 3：前行的速度更重要'
                require(start in text and end in text, 'player_page_retains_separate_option_boundaries')
                target = text.split(start, 1)[1].split(end, 1)[0]
                require('选择后可能的招募结果：' in target,
                        'profession_variants_presented_as_selection_results')
                for number, pair in enumerate(PAIRS, 1):
                    require(target.count(f'职业组合 {number}：' + '或'.join(pair) + '。') == 1,
                            f'player_result_{number}_exact_chinese_profession_pair_once')
                require(target.count('每种结果的资料参考：获得2希望，招募1名5星及以下的直升干员。') == 1,
                        'player_amount_is_two_hope_one_operator_at_most_five_stars')
                require('本次职业组合、实际招募、招募费用和直升后的等级/精英阶段：尚未确认。' in target,
                        'player_page_keeps_actual_group_cost_and_cultivation_unknown')
                require('这些是资料列出的不同可能结果，不相加；职业组合说明不作为选项出现条件。' in target,
                        'alternatives_are_not_summed_or_promoted_to_appearance_conditions')
                require('??' not in target and '条件原文：可出现的职业搭配' not in target
                        and '这段附加条件尚未完整解析' not in target,
                        'target_player_result_has_no_unresolved_profession_placeholder_or_wrong_condition_warning')
                require('实际可选仍未知' in target,
                        'player_result_reference_does_not_certify_actual_option_availability')
                require(not any(value in text for value in ('http://', 'https://', 'choice_ro6_',
                        'scene_ro6_', 'community_group_')),
                        'player_page_hides_raw_ids_and_document_urls')
                return text

            def image(name, path):
                isolated()
                native = native_window()
                pixels = window.grab()
                require(not pixels.isNull(), name + '_actual_own_window_pixels_available')
                data = QByteArray()
                buffer = QBuffer(data)
                require(buffer.open(QIODevice.OpenModeFlag.WriteOnly), name + '_png_buffer_open')
                require(bool(pixels.save(buffer, 'PNG')), name + '_actual_png_encoded')
                buffer.close()
                with path.open('xb') as stream:
                    stream.write(bytes(data))
                stages.append({'name': name, 'native_window': native, 'screenshot': str(path),
                               'screenshot_sha256': sha(path), 'reading_state': snapshot()})

            def fail(error):
                nonlocal failure, done
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error),
                               'traceback': traceback.format_exc()}
                done = True
                window.close()
                gui.exit(1)

            def later(callback, delay=350):
                def guarded():
                    try:
                        isolated()
                        callback()
                    except BaseException as error:
                        fail(error)
                QTimer.singleShot(delay, guarded)

            def begin():
                tabs.setCurrentWidget(panel)
                panel.set_map_context(None, runtime_context={'resources': {'hope': 0}})
                panel.kind.setCurrentIndex(panel.kind.findData('event'))
                panel.node_type.setCurrentIndex(panel.node_type.findData('不期而遇'))
                panel.floor.setCurrentIndex(panel.floor.findData(2))
                panel.search.setText('临时中介所')
                index = next(i for i, entry in enumerate(panel.entries)
                             if entry['kind'] == 'event' and entry['record']['id'] == TARGET)
                panel.list.setCurrentRow(index)
                panel.reading_tabs.setCurrentWidget(panel.player_detail)
                recruitment_contract()
                player_contract()
                later(prime_player)

            def prime_player():
                nonlocal saved
                prime(panel.player_detail, 'player_page')
                saved = snapshot()
                panel.refresh()
                later(check_player)

            def check_player():
                require(snapshot() == saved,
                        'player_refresh_preserves_filters_choice_page_selection_and_nonzero_scroll')
                recruitment_contract()
                player_contract()
                image('player', screenshots[0])
                panel.reading_tabs.setCurrentWidget(panel.detail)
                later(prime_evidence)

            def prime_evidence():
                nonlocal saved
                text = panel.detail.toPlainText()
                require('??或??' in text and original_choice['conditional'] in text,
                        'evidence_page_retains_original_placeholder_and_full_annotation')
                require(all(value in text for value in ORIGINAL_IDS),
                        'evidence_page_keeps_four_distinct_original_choice_ids')
                require('https://wiki.biligame.com/arknights/' in text
                        and '349818' in text and '427904' in text and '440271' in text,
                        'evidence_page_exposes_attributed_document_and_fixed_revisions')
                require('selection_result' in text and 'documented_recruitment_result_variants' in text,
                        'evidence_page_preserves_result_role_and_full_technical_reference')
                prime(panel.detail, 'evidence_page')
                saved = snapshot()
                panel.refresh()
                later(check_evidence)

            def check_evidence():
                require(snapshot() == saved,
                        'evidence_refresh_preserves_filters_choice_page_selection_and_nonzero_scroll')
                recruitment_contract()
                image('evidence', screenshots[1])
                panel.set_map_context(None, runtime_context={'resources': {'hope': 20}})
                later(check_changed_hope)

            def check_changed_hope():
                nonlocal done
                selected_entry()
                require(panel.reading_tabs.currentWidget() is panel.detail
                        and panel.kind.currentData() == 'event' and panel.node_type.currentData() == '不期而遇'
                        and panel.floor.currentData() == 2 and panel.search.text() == '临时中介所',
                        'resource_update_keeps_directory_filters_selected_event_and_reading_page')
                recruitment_contract()
                player_contract()
                require(window.run.state == isolated_run,
                        'declared_resources_and_recruitment_references_do_not_mutate_run_memory')
                require(choice_recruitment_results.source_data() is not None,
                        'source_packet_remains_freshly_valid_at_completion')
                require(bound_files() == before, 'bound_source_unchanged_during_both_actual_pages')
                require(len(stages) == 2, 'both_actual_native_page_screenshots_saved')
                observations.append({'event_id': TARGET, 'scene_key': SCENE, 'choice_key': CHOICE,
                    'profession_pairs': PAIRS, 'variants_are_alternatives': True,
                    'single_selection_hope_reference': 2, 'single_selection_recruit_count_reference': 1,
                    'rarity_ceiling_reference': 5, 'upgrade_reference_text': '直升',
                    'declared_hope_contexts': [0, 20], 'original_eligibility_unchanged': True,
                    'game_choice_ids': [], 'actual_result_variant': None,
                    'actual_recruited_operator': None, 'recruitment_cost': None,
                    'actual_cultivation': None, 'actual_granted': None})
                done = True

            def close_at_deadline():
                nonlocal failure
                if not done:
                    failure = {'type': 'TimeoutError', 'message': 'Both actual recruitment pages did not complete.'}
                window.close()

            later(begin, 650)
            QTimer.singleShot(max(12000, args.visible_ms), close_at_deadline)
            qt_exit = gui.exec()
            closed = not window.isVisible()
            if not done and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'Window closed before all recruitment checks completed.'}
            if (qt_exit != 0 or not closed) and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'The actual verification window did not close normally.'}
            after = bound_files()
            if after != before and failure is None:
                failure = {'type': 'AssertionError', 'message': 'Bound public source changed before window closure.'}
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}

    report = {'section': 290, 'kind': 'isolated_native_windows_recruitment_result_alternatives',
              'passed': done and failure is None, 'failure': failure,
              'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
              'qpa': qpa, 'process_id': os.getpid(), 'qt_exit_code': qt_exit,
              'verification_window_closed': closed,
              'checks': checks, 'unique_checks': len(checks),
              'successful_assertion_executions_including_repeated_guards': executions,
              'visible_stages': stages, 'public_observations': observations,
              'source_sha256_before': before, 'source_sha256_after': after,
              'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
              'private_state_read_or_copied': False, 'temporary_state_root': True,
              'game_operated': False, 'game_captures': 0, 'chat_sent': False,
              'original_project_window_operated_or_restarted': False,
              'scope': 'Two actual native MainWindow directory pages. Four alternatives use the same one-selection amounts. Original eligibility is compared to pinned289 source. No actual variant, recruitment, cost, cultivation, server availability or receipt is certified.'}
    with destination.open('x', encoding='utf8', newline='\n') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
