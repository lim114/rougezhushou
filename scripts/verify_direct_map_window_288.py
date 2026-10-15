"""Native Windows, isolated MainWindow verification of three partial maps.

Only real QTest clicks on this fixture's left grid are sent. The right bitmap
keeps approximate registered centers; no inverse, plane, path or game position
is inferred. Run only after production source has been reviewed and frozen.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
SOURCE_PACKET = ROOT / 'research/p3-map-direct-road-288'
STAGES = ('ro6_t_1', 'ro6_t_3', 'ro6_e_t_3')
SIZES = ((1440, 900), (1280, 850), (1520, 940))
TECHNICAL = (False, True, True)
# The frozen author's independently checked observations, not model-fit output.
POINTS = {
    'ro6_t_1': ((1, 2, 166, 82), (1, 4, 237, 82), (3, 4, 237, 144),
                (3, 5, 277, 144), (3, 6, 317, 144), (4, 5, 275, 178),
                (4, 6, 316, 178), (4, 7, 357, 178)),
    'ro6_t_3': ((1, 6, 290, 57), (1, 8, 357, 57), (4, 6, 297, 144), (4, 8, 374, 144)),
    'ro6_e_t_3': ((1, 6, 290, 57), (1, 8, 357, 57), (4, 6, 297, 144), (4, 8, 374, 144)),
}
BITMAPS = {'ro6_t_1': 'f0514fd94588d874e46761401d62c88987c35d28b23f9e74b02528ed0e14512b',
           'ro6_t_3': '3f6307be8408345a78436a5274305b321989a0477cec6b52360bf5d41a1b1a92',
           'ro6_e_t_3': '3f6307be8408345a78436a5274305b321989a0477cec6b52360bf5d41a1b1a92'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve the first actual receipt; use another path.')
    if args.visible_ms <= 0:
        raise ValueError('--visible-ms must be positive.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    images = {sid: destination.with_name(destination.stem + '-' + sid + '.png') for sid in STAGES}
    for image in images.values():
        if image.exists():
            raise FileExistsError('Preserve the first actual screenshot: ' + str(image))
    started = datetime.now(timezone.utc).isoformat()
    checks, visible_stages = [], []
    before, after = {}, {}
    failure = None
    qpa = None
    checked = False
    closed = False
    qt_exit = None
    assertion_executions = 0

    def require(condition, name):
        nonlocal assertion_executions
        if not condition:
            raise AssertionError(name)
        assertion_executions += 1
        if name not in checks:
            checks.append(name)

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Original Windows is required; compatibility/offscreen is not equivalent.')
        if Path(__file__).resolve() != (ROOT / 'scripts/verify_direct_map_window_288.py').resolve():
            raise RuntimeError('Use the canonical reviewed script under scripts/.')
        from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QTimer, Qt
        from PySide6.QtGui import QTextCursor
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication
        import win32gui
        import win32process
        from rouge import app as app_module
        from rouge.battle_preview import battle_data, DATA
        from rouge.fixed_landmark_mapping import landmark_data

        files = {
            'rouge/app.py', 'rouge/battle_preview.py', 'rouge/battle_view.py',
            'rouge/map_projection.py', 'rouge/fixed_landmark_mapping.py',
            'rouge/player_tile_information.py',
            'rouge/branch_choice.py', 'rouge/branch_reference_view.py',
            'rouge/spawn_reference.py', 'rouge/ui_state.py',
            'rouge/data/battle-previews.json', 'rouge/data/fixed-landmark-references.json',
            'rouge/data/battle-map-projections.json',
            'scripts/extend_direct_landmark_288.py', 'scripts/map_fit_replay.py',
            'scripts/verify_direct_map_window_288.py',
            'tests/test_direct_landmark_288.py', 'tests/test_player_tile_information_288.py',
        }
        if not SOURCE_PACKET.is_dir():
            raise FileNotFoundError('The reviewed source packet has not been promoted.')
        for path in SOURCE_PACKET.rglob('*'):
            if path.is_symlink():
                raise ValueError('The public source packet must contain regular original files.')
            if path.is_file():
                files.add(path.relative_to(ROOT).as_posix())
        new_tests = sorted((ROOT / 'tests').glob('test_*288*.py'))
        if not new_tests:
            raise FileNotFoundError('The section288 necessary tests must be present before window execution.')
        files.update(path.relative_to(ROOT).as_posix() for path in new_tests)
        for sid in STAGES:
            stage = battle_data()['stages'][sid]
            files.add((DATA / stage['image']['file']).relative_to(ROOT).as_posix())
        before = {name: sha(ROOT / name) for name in sorted(files)}
        gui = QApplication([])
        qpa = gui.platformName()
        require(qpa == 'windows', 'actual_native_windows_qpa')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        def forbidden(*_args, **_kwargs):
            raise AssertionError('Game enumeration is forbidden in this isolated public window.')

        with tempfile.TemporaryDirectory(prefix='rouge-288-direct-map-window-') as directory, \
                patch.object(app_module, 'list_game_windows', side_effect=forbidden):
            temporary = Path(directory)
            app_module.ROOT = temporary
            app_module.SETTINGS = temporary / 'settings.json'
            app_module.OPERATOR_STATE = temporary / 'operators.json'
            app_module.RUN_STATE = temporary / 'run.json'
            window = PublicWindow()
            window.setWindowTitle('第288节 · 已核对地面格中心 · 固定地图隔离验收')
            window.resize(*SIZES[0])
            window.show()
            panel = window.battle_preview
            tabs = window.centralWidget()
            index = 0
            state = {}
            grid_emissions, inverse_emissions = [], []
            panel.grid.cellSelected.connect(lambda cell: grid_emissions.append(deepcopy(cell)))
            panel.original.cellSelected.connect(lambda cell: inverse_emissions.append(deepcopy(cell)))

            def isolated():
                require(not window.auto.isChecked(), 'automatic_game_sampling_disabled')
                require(not window.timer.isActive(), 'game_sampling_timer_inactive')
                require(window.capture.target is None, 'no_game_capture_target')
                require(window.desktop.process is None, 'desktop_chat_process_not_started')

            def native_window():
                handle = int(window.winId())
                thread, process = win32process.GetWindowThreadProcessId(handle)
                require(bool(win32gui.IsWindow(handle)), 'owned_win32_hwnd_exists')
                require(bool(win32gui.IsWindowVisible(handle)) and window.isVisible(), 'owned_win32_hwnd_visible')
                require(process == os.getpid(), 'owned_win32_hwnd_matches_actual_process')
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

            def selection_snapshot():
                return {'main_tab': tabs.currentIndex(), 'stage': panel.current_stage,
                        'stage_branch': panel.stage_choices.branch.currentData(),
                        'stage_choice': panel.stage_combo.currentData(),
                        'wave': panel.wave_combo.currentData(),
                        'enemy_branch': panel.enemy_choices.branch.currentData(),
                        'enemy': deepcopy(panel.enemy_combo.currentData()),
                        'include_branches': panel.include_branches.isChecked(),
                        'technical': panel.technical.isChecked(),
                        'detail_key': deepcopy(panel._detail_key),
                        'tile': deepcopy(panel._tile_cell),
                        'grid_reference_cell': deepcopy(panel.grid.reference_cell),
                        'original_reference_cell': deepcopy(panel.original.reference_cell),
                        'spawn_detail': reading(panel.spawn_detail),
                        'enemy_detail': reading(panel.enemy_detail),
                        'fixed_rows': [row['id'] for row in panel.rows]}

            def click_left(cell):
                point = panel.grid.cell_center(cell)
                require(panel.grid.cell_at(point.toPoint()) == cell, 'real_left_grid_click_is_inside_exact_cell')
                previous = len(grid_emissions)
                QTest.mouseClick(panel.grid, Qt.MouseButton.LeftButton, pos=point.toPoint())
                gui.processEvents()
                require(len(grid_emissions) == previous + 1 and grid_emissions[-1] == cell,
                        'real_qtest_left_grid_click_emits_exact_cell')
                return [point.x(), point.y()]

            def projected_points(sid):
                expected = POINTS[sid]
                projection = panel.original.projection
                require(projection is not None, sid + '_production_projection_available')
                require(projection.mapping_mode == 'direct_verified_centers', sid + '_direct_centers_mode')
                require(projection.supports_segment_reference is False, sid + '_no_unproven_segments')
                require(tuple(projection.points) == expected, sid + '_all_fixed_points_match_frozen_observations')
                rect = panel.original.image_rect()
                require(rect.width() > 0 and rect.height() > 0, sid + '_actual_bitmap_viewport_available')
                result = []
                for row, col, x, y in expected:
                    cell = {'row': row, 'col': col}
                    require(projection.project(cell) == (x, y), sid + '_source_pixel_exact')
                    point = panel.original.cell_center(cell)
                    require(point is not None, sid + '_registered_cell_has_scaled_pixel')
                    target = (rect.left() + x * rect.width() / 512,
                              rect.top() + y * rect.height() / 286)
                    require(math.isclose(point.x(), target[0], rel_tol=0, abs_tol=1e-7)
                            and math.isclose(point.y(), target[1], rel_tol=0, abs_tol=1e-7),
                            sid + '_actual_widget_scales_original_pixel')
                    require(panel.original.cell_at(point) is None, sid + '_registered_pixel_has_no_inferred_inverse')
                    result.append({'cell': cell, 'source_pixel': [x, y],
                                   'widget_pixel': [point.x(), point.y()]})
                require(set(panel.original.marker_cells()) <= {(r, c) for r, c, *_ in expected},
                        sid + '_unregistered_spawn_markers_not_painted_on_bitmap')
                return result

            def prime_reading():
                # The actual generated enemy evidence is long; the tile note
                # may be short. Never add filler to manufacture scroll coverage.
                for widget in (panel.spawn_detail, panel.enemy_detail):
                    require(widget.document().characterCount() > 15, 'actual_detail_text_available')
                    cursor = widget.textCursor()
                    cursor.setPosition(1)
                    cursor.setPosition(8, QTextCursor.MoveMode.KeepAnchor)
                    widget.setTextCursor(cursor)
                gui.processEvents()
                bar = panel.enemy_detail.verticalScrollBar()
                require(bar.maximum() > 0, 'actual_enemy_detail_scroll_range_nonzero')
                bar.setValue(max(1, bar.maximum() // 2))
                gui.processEvents()
                require(bar.value() > 0, 'actual_enemy_detail_scroll_position_nonzero')
                require(bool(panel.enemy_detail.textCursor().selectedText())
                        and bool(panel.spawn_detail.textCursor().selectedText()),
                        'actual_enemy_and_tile_detail_text_selections_nonempty')

            def fail(error):
                nonlocal failure, checked
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error),
                               'traceback': traceback.format_exc()}
                checked = True
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

            def configure():
                sid = STAGES[index]
                window.resize(*SIZES[index])
                window.show_catalog_battle(sid)
                require(panel.current_stage == window.target_stage.currentData() == sid,
                        sid + '_exact_mainwindow_stage_binding')
                stage = battle_data()['stages'][sid]
                require(panel.original.image_sha256 == stage['image']['sha256'] == BITMAPS[sid],
                        sid + '_original_bitmap_sha_matches_exact_stage')
                require((panel.original.pixmap.width(), panel.original.pixmap.height()) == (512, 286),
                        sid + '_source_bitmap_dimensions_unchanged')
                require(sid in landmark_data()['stages'], sid + '_binding_is_production_data')
                panel.include_branches.setChecked(False)
                require(panel.wave_combo.count() > 1, sid + '_real_wave_option_available')
                panel.wave_combo.setCurrentIndex(1)
                require(bool(panel.rows), sid + '_selected_wave_has_real_fixed_rows')
                enemy_id = panel.rows[0]['action']['key']
                choice = next(panel.enemy_combo.itemData(i) for i in range(panel.enemy_combo.count())
                              if panel.enemy_combo.itemData(i) and panel.enemy_combo.itemData(i)[0] == enemy_id)
                require(panel.enemy_choices.select_value(choice), sid + '_real_enemy_option_selected')
                panel.technical.setChecked(TECHNICAL[index])
                state.clear()
                state['stage'] = stage
                later(exercise_clicks)

            def exercise_clicks():
                sid = STAGES[index]
                stage = state['stage']
                points = projected_points(sid)
                known = {(row, col) for row, col, *_ in POINTS[sid]}
                starts = {(row['route']['start']['row'], row['route']['start']['col'])
                          for row in panel.rows if row['route']['start']}
                cells = [{'row': row, 'col': col} for row, col, *_ in POINTS[sid]
                         if (row, col) not in starts]
                require(bool(cells), sid + '_registered_ground_cell_without_spawn_reference_available')
                chosen = next((cell for cell in cells if stage['tiles'][stage['map'][cell['row']][cell['col']]]['tileKey'] == 'tile_road'), cells[0])
                tile = stage['tiles'][stage['map'][chosen['row']][chosen['col']]]
                require(tile['heightType'] == 'LOWLAND' and tile['tileKey'] in ('tile_floor', 'tile_road'),
                        sid + '_clicked_registered_cell_is_reviewed_ground_type')
                unknown = next(({'row': row, 'col': col}
                                for row, line in enumerate(stage['map']) for col, value in enumerate(line)
                                if (row, col) not in known and (row, col) not in starts
                                and stage['tiles'][value]['heightType'] == 'LOWLAND'
                                and stage['tiles'][value]['tileKey'] in ('tile_floor', 'tile_road')), None)
                require(unknown is not None, sid + '_real_unregistered_ground_cell_available')
                click_left(chosen)
                require(panel._tile_cell == panel.grid.reference_cell == panel.original.reference_cell == chosen,
                        sid + '_left_click_sets_matching_grid_and_bitmap_reference')
                original_point = panel.original.cell_center(chosen)
                previous = len(inverse_emissions)
                QTest.mouseClick(panel.original, Qt.MouseButton.LeftButton, pos=original_point.toPoint())
                gui.processEvents()
                require(len(inverse_emissions) == previous, sid + '_bitmap_click_does_not_invent_inverse_cell')
                click_left(unknown)
                require(panel._tile_cell == panel.grid.reference_cell == unknown
                        and panel.original.reference_cell is None and panel.original.selected is None,
                        sid + '_unregistered_grid_click_clears_prior_bitmap_marker')
                require(panel.original.cell_center(unknown) is None
                        and '位置尚未核对' in panel.spawn_detail.toPlainText(),
                        sid + '_unknown_center_remains_explicitly_unmapped')
                click = click_left(chosen)
                detail = panel.spawn_detail.toPlainText()
                require('近似中心' in detail, sid + '_mapped_center_still_labelled_approximate')
                if TECHNICAL[index]:
                    require('【原始地块资料】' in detail
                            and json.dumps(tile, ensure_ascii=False, indent=2) in detail,
                            sid + '_technical_view_retains_exact_original_tile_fields')
                else:
                    require(('地形：道路' in detail or '地形：地面地块' in detail)
                            and '位置高度：地面' in detail,
                            sid + '_default_ground_labels_are_readable_chinese')
                    require('地块部署标记：近战位' in detail or '地块部署标记：全部类型' in detail,
                            sid + '_default_deployment_label_is_readable_chinese')
                    require('tile_road' not in detail and 'tile_floor' not in detail and 'LOWLAND' not in detail
                            and '【原始地块资料】' not in detail,
                            sid + '_default_tile_view_hides_original_english_fields')
                    require('不包含战斗中的变化' in detail and '不等于本局一定没有敌人经过' in detail,
                            sid + '_tile_labels_do_not_predict_runtime_placement_or_enemy_motion')
                require('近似' in panel.map_caption.text(), sid + '_caption_does_not_claim_actual_position')
                state.update(chosen=chosen, unknown=unknown, points=points, click=click)
                later(refresh)

            def refresh():
                prime_reading()
                state['saved'] = selection_snapshot()
                panel.render_rows()
                later(check_refresh)

            def check_refresh():
                nonlocal index, checked
                sid = STAGES[index]
                require(selection_snapshot() == state['saved'],
                        sid + '_refresh_preserves_all_options_cells_text_selection_and_nonzero_scroll')
                require(tabs.currentWidget() is panel and panel.technical.isChecked() == TECHNICAL[index]
                        and panel.wave_combo.currentData() is not None
                        and panel.enemy_combo.currentData() is not None
                        and not panel.include_branches.isChecked(),
                        sid + '_real_nondefault_view_options_still_selected')
                projected_points(sid)
                native = native_window()
                pixels = window.grab()
                require(not pixels.isNull(), sid + '_actual_public_window_pixels_available')
                data = QByteArray()
                buffer = QBuffer(data)
                require(buffer.open(QIODevice.OpenModeFlag.WriteOnly), sid + '_image_buffer_open')
                require(bool(pixels.save(buffer, 'PNG')), sid + '_actual_png_encoded')
                buffer.close()
                with images[sid].open('xb') as stream:
                    stream.write(bytes(data))
                visible_stages.append({'stage_id': sid, 'native_window': native,
                    'requested_window_size': list(SIZES[index]),
                    'actual_widget_size': [window.width(), window.height()],
                    'technical_view': TECHNICAL[index],
                    'screenshot': str(images[sid]), 'screenshot_sha256': sha(images[sid]),
                    'registered_points_observed': state['points'],
                    'clicked_registered_ground_cell': deepcopy(state['chosen']),
                    'qtest_left_widget_pixel': state['click'],
                    'clicked_unknown_ground_cell_left_unmapped': deepcopy(state['unknown']),
                    'preserved_reading_state': deepcopy(state['saved']),
                    'actual_position_or_inverse_accuracy_certified': False})
                index += 1
                if index < len(STAGES):
                    later(configure)
                else:
                    require(len(visible_stages) == 3, 'all_three_exact_stage_screenshots_saved')
                    require({name: sha(ROOT / name) for name in sorted(files)} == before,
                            'all_bound_source_unchanged_during_stages')
                    checked = True

            def close_at_deadline():
                nonlocal failure
                if not checked:
                    failure = {'type': 'TimeoutError', 'message': 'Three actual map stages did not complete before deadline.'}
                window.close()

            later(configure, 650)
            QTimer.singleShot(max(12000, args.visible_ms), close_at_deadline)
            qt_exit = gui.exec()
            closed = not window.isVisible()
            if not checked and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'Window closed before all three actual stages completed.'}
            if (qt_exit != 0 or not closed) and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'Qt did not close the actual verification window normally.'}
            after = {name: sha(ROOT / name) for name in sorted(files)}
            if after != before and failure is None:
                failure = {'type': 'AssertionError', 'message': 'Bound source changed before actual window closure.'}
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}

    report = {'section': 288, 'kind': 'isolated_native_windows_direct_map',
              'passed': checked and failure is None, 'failure': failure,
              'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
              'qpa': qpa, 'process_id': os.getpid(), 'qt_exit_code': qt_exit,
              'verification_window_closed': closed,
              'checks': checks, 'unique_checks': len(checks),
              'successful_assertion_executions_including_repeated_guards': assertion_executions,
              'visible_stages': visible_stages,
              'actual_distinct_widget_sizes_observed': len({tuple(s['actual_widget_size']) for s in visible_stages}),
              'source_sha256_before': before, 'source_sha256_after': after,
              'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
              'private_state_read_or_copied': False, 'temporary_state_root': True,
              'game_operated': False, 'game_captures': 0, 'chat_sent': False,
              'original_project_window_operated_or_restarted': False,
              'scope': 'Three real public Windows MainWindow stages and QTest grid clicks. Only registered approximate bitmap centers are mapped. Existing whole-plane coverage is not expanded, unknown pixels remain unmapped, and no inverse, live combat position, actual route or time is certified.'}
    with destination.open('x', encoding='utf8', newline='\n') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
