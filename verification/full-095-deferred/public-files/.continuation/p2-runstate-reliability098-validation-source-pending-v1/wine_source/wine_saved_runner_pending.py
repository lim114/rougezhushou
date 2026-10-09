PENDING_PREPARATION = True
if PENDING_PREPARATION:
    raise SystemExit('PENDING SOURCE ONLY: no project, codec, Qt, Wine or runtime admission.')

"""Pending public Wine/MainWindow saved-state collection; never a Product PASS.

Root must materialize and independently review a separate FINAL after the real
095 publication and completed 096/097 guards. This pending file is not run.
All fixture paths and incoming recipes belong to the common sealed plan. No
fixture, seed UUID, timestamp, state, report text or widget text is normalized.
"""
import copy
import json
import os
from pathlib import Path
import re
import sys
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pending_common import open_runtime


def main():
    ctx = open_runtime('wine_saved', argv=sys.argv[1:])
    ctx.guard('before_Qt_and_project_imports')
    if sys.platform != 'win32':
        raise RuntimeError('This collector requires the separately bound real Wine Windows Python.')
    if os.environ.get('PYTHONDONTWRITEBYTECODE') != '1':
        raise RuntimeError('Exact-source runtime requires PYTHONDONTWRITEBYTECODE=1.')
    if os.environ.get('QT_QPA_PLATFORM') in ('offscreen', 'minimal'):
        raise RuntimeError('An offscreen/minimal Qt platform is not an actual Wine window.')
    sys.path.insert(0, str(ctx.repo_root))
    from PySide6.QtCore import QCoreApplication, QEvent, Qt
    from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPlainTextEdit,
                                 QLineEdit, QCheckBox, QComboBox, QSpinBox,
                                 QDoubleSpinBox, QListWidget, QPushButton)
    import rouge.app as module
    from rouge.damage import calculate_damage
    from rouge.reporting import format_report

    app_holder = {}
    case_now = 'runtime'
    phase_now = 'bootstrap'
    qt_errors = []
    window_holder = {}
    original_hook = sys.excepthook
    original_unraisable = sys.unraisablehook
    original_globals = {name: getattr(module, name) for name in
                        ('RUN_STATE', 'OPERATOR_STATE', 'SETTINGS', 'DesktopBackend')}
    original_backend = module.DesktopBackend
    collection_error = None
    rows = []
    active_paths = {}

    def qt_hook(kind, error, tb):
        row = {'kind': 'Qt_slot_exception', 'case': case_now, 'phase': phase_now,
               'exception_type': kind.__module__ + '.' + kind.__qualname__,
               'message': str(error),
               'traceback_original': ''.join(traceback.format_exception(kind, error, tb)),
               'frames': [{'file': frame.filename, 'line': frame.lineno,
                           'name': frame.name, 'source': frame.line}
                          for frame in traceback.extract_tb(tb)]}
        qt_errors.append(row)
        ctx.emit(row)
        # Set the failure flag and save its original prefix before the strict
        # args codec can reject an unsupported graph. Such rejection is failure.
        row['args'] = ctx.native(error.args)
        ctx.emit({'kind': 'Qt_slot_exception_full_native_args', 'case': case_now,
                  'phase': phase_now, 'exception': row})

    def unraisable_hook(event):
        row = {'kind': 'unraisable_exception', 'case': case_now, 'phase': phase_now,
               'exception_type': event.exc_type.__module__ + '.' + event.exc_type.__qualname__,
               'message': str(event.exc_value), 'error_message': event.err_msg,
               'traceback_original': ''.join(traceback.format_exception(
                   event.exc_type, event.exc_value, event.exc_traceback))}
        qt_errors.append(row)
        ctx.emit(row)

    sys.excepthook = qt_hook
    sys.unraisablehook = unraisable_hook

    def call(case, phase, label, fn, args=(), kwargs=None):
        nonlocal case_now, phase_now
        case_now, phase_now = case, phase
        with ctx.phase(case, phase):
            return ctx.call(case, phase, label, fn, args=args, kwargs=kwargs)

    def required(result, label):
        if not result['ok']:
            raise RuntimeError('Collection operation failed after its original evidence was sealed: ' + label)
        return result['value']

    def process_events(case, phase):
        return required(call(case, phase, 'QApplication.processEvents',
                             application.processEvents), 'QApplication.processEvents')

    class OfflineWindow(module.MainWindow):
        def __init__(self):
            # Retain the actual allocated wrapper even if the original constructor
            # raises. The original MainWindow.__init__ still executes unchanged.
            window_holder['allocated'] = self
            super().__init__()

        def refresh_windows(self):
            # No list_game_windows/process_names/EnumWindows call.
            self.windows.clear()

    def widget_rows(window):
        result = []
        for widget in [window, *window.findChildren(QWidget)]:
            geometry = widget.geometry()
            row = {'live_object_id': id(widget), 'class': type(widget).__name__,
                   'object_name': widget.objectName(), 'accessible_name': widget.accessibleName(),
                   'enabled': widget.isEnabled(), 'visible': widget.isVisible(),
                   'geometry': [geometry.x(), geometry.y(), geometry.width(), geometry.height()]}
            if isinstance(widget, QLabel):
                row['text_original'] = widget.text()
            elif isinstance(widget, QPlainTextEdit):
                row['text_original'] = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                row['text_original'] = widget.text()
            elif isinstance(widget, QCheckBox):
                row.update(text_original=widget.text(), checked=widget.isChecked())
            elif isinstance(widget, QComboBox):
                row.update(current_index=widget.currentIndex(), current_data=widget.currentData(),
                           items=[{'text_original': widget.itemText(index),
                                   'data': widget.itemData(index)} for index in range(widget.count())])
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                row.update(value=widget.value(), minimum=widget.minimum(), maximum=widget.maximum())
            elif isinstance(widget, QListWidget):
                row['items'] = [{'text_original': widget.item(index).text(),
                                 'data': widget.item(index).data(Qt.ItemDataRole.UserRole),
                                 'check_state_name': widget.item(index).checkState().name,
                                 'flags_name': str(widget.item(index).flags())}
                                for index in range(widget.count())]
            elif isinstance(widget, QPushButton):
                row.update(text_original=widget.text(), checkable=widget.isCheckable(),
                           checked=widget.isChecked())
            result.append(row)
        return result

    def files(paths):
        return {name: ctx.file_evidence(path) for name, path in paths.items()
                if name != 'desktop_dir'}

    def tree(folder):
        # Retain every generated file, including undeclared output, before cleanup.
        return {str(path.relative_to(folder)): ctx.file_evidence(path)
                for path in sorted(folder.rglob('*')) if path.is_file()}

    def idle(window, paths):
        result = {'auto': window.auto.isChecked(), 'timer_active': window.timer.isActive(),
                  'game_target': window.capture.target, 'capture_control': window.capture._control is not None,
                  'native_capture': window.capture._capture is not None,
                  'desktop_process_present': window.desktop.process is not None,
                  'desktop_request_busy': window.desktop_request_busy,
                  'desktop_pending_count': len(window.desktop.pending),
                  'desktop_dir_exists': paths['desktop_dir'].exists(),
                  'window_scan_combo_count': window.windows.count()}
        if (result['auto'] or result['timer_active'] or result['game_target'] is not None
                or result['capture_control'] or result['native_capture']
                or result['desktop_process_present'] or result['desktop_request_busy']
                or result['desktop_pending_count'] or result['desktop_dir_exists']
                or result['window_scan_combo_count']):
            ctx.emit({'kind': 'external_idle_violation', 'case': case_now,
                      'phase': phase_now, 'actual': ctx.native(result)})
            raise RuntimeError('The isolated actual window was not idle.')
        return result

    def snapshot(case, phase, window, paths):
        # Capture one live combined graph so aliases in this capture remain facts.
        def collect():
            consumers = {}
            for label, method in (('summary', window.run.summary),
                                  ('inventory_status', window.run.inventory_status),
                                  ('held_relic_ids', window.run.held_relic_ids),
                                  ('held_tool_ids', window.run.held_tool_ids)):
                outcome = call(case, phase, 'RunState.' + label, method)
                consumers[label] = (ctx.native(outcome['value']) if outcome['ok']
                                    else {'exception': outcome['error']})
            graph = {'run_state': window.run.state,
                     'account_records': window.account_cache.records,
                     'operator_observations': window.operator_observations,
                     'account_issues': window.account_cache.issues,
                     'account_preserve_original': window.account_cache.preserve_original,
                     'run_preserve_unreadable': window.run.preserve_unreadable,
                     'current_operator_state': window.current_operator_state(),
                     'damage_result': window.damage_result,
                     'widgets': widget_rows(window)}
            return {'live_graph': ctx.native(graph), 'consumers': consumers,
                    'operator_observations_is_account_records':
                        window.operator_observations is window.account_cache.records,
                    'run_summary_widget_original': ctx.native(window.run_summary.text()),
                    'damage_widget_original': ctx.native(window.damage_text.toPlainText()),
                    'window_visible': window.isVisible(),
                    'window_handle_actual': int(window.winId()),
                    'reset_button_enabled': window.reset_run_button.isEnabled(),
                    'reset_button_text_original': ctx.native(window.reset_run_button.text()),
                    'external_idle_actual': ctx.native(idle(window, paths)),
                    'files': files(paths), 'whole_generated_tree': tree(paths['run'].parent)}
        result = call(case, phase, 'full_window_native_file_snapshot', collect)
        captured = required(result, 'full_window_native_file_snapshot')
        ctx.emit({'kind': 'window_snapshot', 'case': case, 'phase': phase, 'snapshot': captured})
        return captured

    def raw_fixture(relative):
        # fixture_path resolves only exact MF-bound common public fixture files.
        path = ctx.fixture_path(relative)
        raw = path.read_bytes()
        return raw, ctx.file_evidence(path)

    def prepare_case(case, raw):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', case) or '..' in case:
            raise ValueError('Unsafe public case identifier')
        folder = ctx.case_root / case
        folder.mkdir(exist_ok=False)
        other = folder / 'other'
        other.mkdir()
        paths = {'run': folder / 'run.json', 'run_tmp': folder / 'run.tmp',
                 'account': folder / 'accounts.json', 'account_tmp': folder / 'accounts.tmp',
                 'settings': folder / 'settings.json', 'settings_tmp': folder / 'settings.tmp',
                 'other_run': other / 'run.json', 'other_run_tmp': other / 'run.tmp',
                 'other_account': other / 'accounts.json', 'other_account_tmp': other / 'accounts.tmp',
                 'desktop_dir': folder / 'desktop-not-started'}
        account_raw, account_source = raw_fixture(ctx.plan['ui']['account_raw_path'])
        other_account_raw, other_account_source = raw_fixture(ctx.plan['ui']['account_other_raw_path'])
        other_run_raw, other_run_source = raw_fixture(ctx.plan['ui']['other_run_raw_path'])
        paths['run'].write_bytes(raw)
        paths['account'].write_bytes(account_raw)
        paths['other_run'].write_bytes(other_run_raw)
        paths['other_account'].write_bytes(other_account_raw)
        active_paths.clear()
        active_paths.update(paths)
        ctx.emit({'kind': 'isolated_case_prepared', 'case': case, 'files': files(paths),
                  'account_fixture_source': account_source,
                  'other_account_fixture_source': other_account_source,
                  'other_run_fixture_source': other_run_source,
                  'same_shared_seed_bytes': raw == ctx.seed_raw,
                  'fixture_text_state_time_or_id_normalization': False})
        return paths

    def construct(case, phase, paths):
        module.RUN_STATE = paths['run']
        module.OPERATOR_STATE = paths['account']
        module.SETTINGS = paths['settings']
        module.DesktopBackend = lambda _ignored_default_path, callback: original_backend(
            paths['desktop_dir'], callback)
        window_holder.clear()
        def create():
            window = OfflineWindow()
            window_holder['complete'] = window
            return {'actual_wrapper_id': id(window), 'original_MainWindow_constructor_requested': True,
                    'actual_window_title_original': window.windowTitle()}
        outcome = call(case, phase, 'actual_OfflineWindow_original_MainWindow_constructor', create)
        window = window_holder.get('complete')
        ctx.emit({'kind': 'window_constructor_outcome', 'case': case, 'phase': phase,
                  'outcome': outcome['record'], 'files_after_constructor': files(paths),
                  'whole_generated_tree': tree(paths['run'].parent)})
        if not outcome['ok']:
            partial = window_holder.get('allocated')
            if partial is not None:
                partial_meta = call(case, phase, 'partial_Qt_wrapper_evidence',
                                    lambda: {'class': type(partial).__name__,
                                             'live_object_id': id(partial),
                                             'visible': partial.isVisible(),
                                             'widgets': widget_rows(partial)})
                ctx.emit({'kind': 'partial_constructor_Qt_evidence', 'case': case,
                          'phase': phase, 'outcome': partial_meta['record']})
                # An incomplete original constructor has no timer/desktop/run;
                # invoking its closeEvent would manufacture another failure.
                call(case, 'partial_cleanup', 'partial_Qt_hide', partial.hide)
                call(case, 'partial_cleanup', 'partial_Qt_deleteLater', partial.deleteLater)
                process_events(case, 'partial_cleanup')
                call(case, 'partial_cleanup', 'actual_Qt_DeferredDelete_delivery',
                     lambda: QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value))
            window_holder.clear()
            return None
        required(call(case, phase, 'actual_window_show', window.show), 'actual_window_show')
        process_events(case, phase)
        snapshot(case, phase, window, paths)
        return window

    def close(case, phase, window, paths):
        before = snapshot(case, phase + '_before', window, paths)
        outcome = call(case, phase, 'actual_MainWindow_closeEvent_via_QWidget_close', window.close)
        process_events(case, phase)
        ctx.emit({'kind': 'window_close_outcome', 'case': case, 'phase': phase,
                  'outcome': outcome['record'], 'before': before,
                  'files_after_close': files(paths), 'whole_generated_tree': tree(paths['run'].parent),
                  'visible_after_close': window.isVisible(),
                  'closing_flag_actual': window.closing})
        required(outcome, 'actual_MainWindow_closeEvent_via_QWidget_close')
        required(call(case, phase, 'actual_Qt_deleteLater', window.deleteLater), 'actual_Qt_deleteLater')
        process_events(case, phase)
        required(call(case, phase, 'actual_Qt_DeferredDelete_delivery',
                      lambda: QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value)),
                 'actual_Qt_DeferredDelete_delivery')
        window_holder.clear()

    def controls(case, window):
        ui = ctx.plan['ui']
        operations = [('damage_tab', lambda: window.centralWidget().setCurrentIndex(1)),
                      ('auto_relics', lambda: window.auto_relics.setChecked(True)),
                      ('run_training', lambda: window.use_run_training.setChecked(True)),
                      ('frame_timing', lambda: window.frame_timing.setChecked(False)),
                      ('limit_window', lambda: window.limit_window.setChecked(False)),
                      ('target_buff_test', lambda: window.target_buff_test.setChecked(False)),
                      ('target_stage_manual', lambda: window.target_stage_choices.select_value(None)),
                      ('target_enemy_manual', lambda: window.target_enemy.setCurrentIndex(0)),
                      ('known_operator', lambda: window.select_operator(ui['operator'])),
                      ('known_skill', lambda: window.skill.setCurrentIndex(window.skill.findData(ui['skill']))),
                      ('manual_enemy_defense', lambda: window.defense.setValue(ui['enemy_defense'])),
                      ('manual_enemy_resistance', lambda: window.resistance.setValue(ui['enemy_resistance'])),
                      ('timing_text_empty', window.timing_scenario.clear),
                      ('relic_context_text_empty', window.relic_context.clear)]
        for label, action in operations:
            required(call(case, 'ordinary_public_controls', label, action), label)
            process_events(case, 'ordinary_public_controls')
        if window.operator.currentData() != ui['operator'] or window.skill.currentData() != ui['skill']:
            raise RuntimeError('Bound known operator/skill selection was not realized.')
        required(call(case, 'explicit_window_calculation', 'MainWindow.calculate', window.calculate),
                 'MainWindow.calculate')
        process_events(case, 'explicit_window_calculation')

    def reports(case, window, paths, screenshot):
        controls(case, window)
        initial = snapshot(case, 'before_API_and_reports', window, paths)
        row = {'kind': 'damage_API_and_three_actual_report_modes', 'case': case,
               'before': initial, 'reports': [], 'Product_PASS': None,
               'strict_saved_pair_comparator_result': None}
        if window.damage_result is None:
            row.update(applicable=False, reason='Actual window calculation has no native damage result',
                       original_widget_text=ctx.native(window.damage_text.toPlainText()))
            ctx.emit(row)
            return row
        row['applicable'] = True
        scenario = copy.deepcopy(window.damage_result['scenario'])
        api_caller_before = ctx.native(scenario)
        api = call(case, 'direct_damage_API', 'calculate_damage', calculate_damage, args=(scenario,))
        row['direct_API_outcome'] = api['record']
        row['direct_API_caller_before'] = api_caller_before
        row['direct_API_caller_after'] = ctx.native(scenario)
        if api['ok']:
            # Mirror the original calculate() post-processing, preserving the
            # direct API's unmodified return as an earlier independently sealed call.
            api_result = api['value']
            row['direct_API_return_before_history_notice'] = ctx.native(api_result)
            notice = call(case, 'direct_damage_API', 'app.apply_relic_history_notice',
                          module.apply_relic_history_notice, args=(scenario, api_result))
            row['history_notice_outcome'] = notice['record']
            row['direct_API_return_after_history_notice'] = ctx.native(api_result)
            row['window_original_scenario_and_result'] = ctx.native(window.damage_result)
            # No typed-graph ID rewriting or JSON projection comparison here.
            # The later formal Saved comparator receives both original graphs.
        for name, raw, technical in (('general', False, False), ('technical', False, True),
                                     ('JSON', True, True)):
            required(call(case, 'report_' + name, 'raw_damage_existing_control',
                          window.raw_damage.setChecked, args=(raw,)), 'raw_damage_existing_control')
            required(call(case, 'report_' + name, 'damage_technical_existing_control',
                          window.damage_technical.setChecked, args=(technical,)),
                     'damage_technical_existing_control')
            required(call(case, 'report_' + name, 'MainWindow.render_damage', window.render_damage),
                     'MainWindow.render_damage')
            process_events(case, 'report_' + name)
            if raw:
                original = call(case, 'report_' + name, 'stdlib_JSON_original_damage_text',
                                lambda: json.dumps(window.damage_result, ensure_ascii=False, indent=2))
            else:
                original = call(case, 'report_' + name, 'format_report_original_full_text',
                                format_report, args=(window.damage_result['result'],),
                                kwargs={'technical': technical})
            report_text = required(original, 'original report text')
            widget_text = window.damage_text.toPlainText()
            entry = {'mode': name, 'formatter_original': ctx.native(report_text),
                     'widget_original': ctx.native(widget_text),
                     'formatter_utf8_file': ctx.write_text(case + '-' + name + '-formatter.txt', report_text),
                     'widget_utf8_file': ctx.write_text(case + '-' + name + '-widget.txt', widget_text),
                     'original_string_equality_observation': report_text == widget_text,
                     'source_text_or_widget_normalization': False,
                     'snapshot': snapshot(case, 'report_' + name, window, paths)}
            if screenshot:
                png = ctx.out_root / (case + '-' + name + '-actual-window.png')
                saved = call(case, 'report_' + name, 'actual_public_window_grab_PNG',
                             lambda: window.grab().save(str(png)))
                entry['actual_PNG_save_outcome'] = saved['record']
                entry['actual_PNG_original_file'] = ctx.file_evidence(png)
            row['reports'].append(entry)
            # Seal the completed mode before the next real toggle/render.
            ctx.emit({'kind': 'completed_original_report_mode', 'case': case, 'report': entry})
        row['after'] = snapshot(case, 'after_API_and_reports', window, paths)
        ctx.emit(row)
        return row

    def observe(case, window, paths, recipe, captured_at):
        observed = ctx.observed(recipe)
        before = ctx.native(observed)
        files_before = files(paths)
        outcome = call(case, 'ordinary_apply', 'MainWindow.apply_run_observation',
                       window.apply_run_observation, args=(observed, captured_at))
        process_events(case, 'ordinary_apply')
        ctx.emit({'kind': 'public_apply_outcome', 'case': case,
                  'captured_at_original': ctx.native(captured_at),
                  'caller_before': before, 'caller_after': ctx.native(observed),
                  'outcome': outcome['record'], 'files_before': files_before,
                  'snapshot_after': snapshot(case, 'ordinary_apply_after', window, paths)})
        return outcome

    def restart(case, window, paths, screenshot):
        close(case, 'valid_or_protected_original_close', window, paths)
        restored = construct(case, 'actual_same_file_restart', paths)
        if restored is None:
            return None
        reports(case + '-restart', restored, paths, screenshot)
        snapshot(case, 'actual_restart_saved_consumers', restored, paths)
        close(case, 'actual_restart_final_close', restored, paths)
        return None

    def startup_case(recipe):
        case = 'startup-' + recipe['id']
        if not recipe['ui_applicable']:
            ctx.emit({'kind': 'explicit_UI_inapplicability', 'case': case,
                      'reason': recipe['ui_inapplicability_reason'],
                      'actual_window_or_consumer_calls_for_this_case': None,
                      'RunState_only_receipt_reference': None})
            return
        raw, source = raw_fixture(recipe['raw_path'])
        paths = prepare_case(case, raw)
        ctx.emit({'kind': 'startup_public_raw_source', 'case': case, 'source': source})
        window = construct(case, 'actual_startup', paths)
        if window is None:
            rows.append({'case': case, 'constructor_returned_window': False})
            return
        reports(case, window, paths, recipe.get('screenshot', False))
        if recipe.get('apply_observed') is not None:
            # A fresh protected fallback owns its naturally generated start/id.
            # Preserve and record this natural time; do not pair-normalize it.
            offset = recipe.get('captured_at_offset', 1)
            captured_at = window.run.state['started_at'] + offset
            observe(case, window, paths, recipe['apply_observed'], captured_at)
            required(call(case, 'protected_explicit_save_probe', 'RunState.save', window.run.save),
                     'RunState.save')
            snapshot(case, 'after_explicit_protected_save_probe', window, paths)
            reports(case + '-after-apply', window, paths, recipe.get('screenshot', False))
        if recipe.get('manual_reset', False):
            # This dedicated case exercises the existing button, with another
            # isolated run and account original visible in every file snapshot.
            before = snapshot(case, 'before_explicit_manual_button', window, paths)
            outcome = call(case, 'explicit_manual_user_action', 'reset_run_button.click',
                           window.reset_run_button.click)
            process_events(case, 'explicit_manual_user_action')
            ctx.emit({'kind': 'explicit_manual_reset_outcome', 'case': case,
                      'button_request': outcome['record'], 'before': before,
                      'after': snapshot(case, 'after_explicit_manual_button', window, paths)})
            reports(case + '-after-manual-reset', window, paths, recipe.get('screenshot', False))
        restart(case, window, paths, recipe.get('screenshot', False))
        rows.append({'case': case, 'constructor_returned_window': True})

    def inventory_case(recipe):
        case = 'inventory-' + recipe['id']
        if not recipe['ui_applicable']:
            ctx.emit({'kind': 'explicit_UI_inapplicability', 'case': case,
                      'reason': recipe['ui_inapplicability_reason'],
                      'actual_window_or_consumer_calls_for_this_case': None})
            return
        paths = prepare_case(case, ctx.seed_raw)
        window = construct(case, 'same_whole_seed_actual_startup', paths)
        if window is None:
            rows.append({'case': case, 'constructor_returned_window': False})
            return
        offset = recipe.get('captured_at_offset', 0)
        captured_at = ctx.captured_at if offset == 0 else ctx.captured_at + offset
        observe(case, window, paths, recipe['observed'], captured_at)
        reports(case, window, paths, recipe.get('screenshot', False))
        restart(case, window, paths, recipe.get('screenshot', False))
        rows.append({'case': case, 'constructor_returned_window': True})

    try:
        def create_application():
            application = QApplication([])
            app_holder['application'] = application
            application.setQuitOnLastWindowClosed(False)
            return {'actual_QApplication_created': True,
                    'actual_platform_plugin': application.platformName(),
                    'actual_executable': sys.executable, 'actual_python_version': sys.version}
        application_info = required(call('runtime', 'bootstrap', 'actual_QApplication', create_application),
                                    'actual_QApplication')
        application = app_holder['application']
        ctx.emit({'kind': 'actual_Wine_Qt_application', 'metadata': application_info,
                  'binding_original': ctx.native(ctx.binding),
                  'same_shared_seed_raw_evidence': ctx.native(ctx.seed_raw),
                  'shared_captured_at_original': ctx.native(ctx.captured_at),
                  'Product_PASS': None})
        if application.platformName() != 'windows':
            raise RuntimeError('This Source route requires the actual Windows Qt platform plugin.')
        for recipe in ctx.plan['startup']:
            startup_case(recipe)
        for recipe in ctx.plan['inventory']:
            inventory_case(recipe)
        ctx.emit({'kind': 'finished_Wine_worker_collection', 'actual_case_rows': rows,
                  'Qt_exceptions_original': qt_errors,
                  'remaining_top_level_widgets': [type(widget).__name__
                                                  for widget in application.topLevelWidgets()],
                  'Product_PASS': None, 'formal_Saved_pair_gate': None,
                  'actual095publication': None, 'actual096ref': None,
                  'actual097ref': None, 'actual098ref': None})
        if qt_errors:
            raise RuntimeError('Qt callback/unraisable exceptions were retained; collection is incomplete.')
        if application.topLevelWidgets():
            raise RuntimeError('Actual Qt top-level widgets remain after final close/deletion.')
    except BaseException as error:
        collection_error = {'type': type(error).__module__ + '.' + type(error).__qualname__,
                            'message': str(error), 'args': ctx.native(error.args),
                            'traceback_original': traceback.format_exc(),
                            'case': case_now, 'phase': phase_now}
        ctx.emit({'kind': 'Wine_collection_failure_original', 'error': collection_error,
                  'Product_PASS': None, 'formal_Saved_pair_gate': None})
        if active_paths:
            ctx.emit({'kind': 'failure_prefix_original_files', 'case': case_now,
                      'phase': phase_now, 'files': files(active_paths),
                      'whole_generated_tree': tree(active_paths['run'].parent)})
    finally:
        remaining = window_holder.get('complete')
        if remaining is not None:
            if not remaining.closing:
                call(case_now, 'failure_cleanup', 'actual_remaining_window_close', remaining.close)
                if app_holder.get('application') is not None:
                    application.processEvents()
            call(case_now, 'failure_cleanup', 'remaining_window_deleteLater', remaining.deleteLater)
            if app_holder.get('application') is not None:
                application.processEvents()
                QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete.value)
        if active_paths:
            ctx.emit({'kind': 'final_cleanup_original_files', 'case': case_now,
                      'phase': phase_now, 'files': files(active_paths),
                      'whole_generated_tree': tree(active_paths['run'].parent)})
        for name, value in original_globals.items():
            setattr(module, name, value)
        sys.excepthook = original_hook
        sys.unraisablehook = original_unraisable
        ctx.guard('after_all_Wine_saved_collection_and_cleanup')
        ctx.finish('COLLECTION_FAILED' if collection_error else 'COLLECTION_COMPLETED_PRODUCT_PASS_NULL')
    return 1 if collection_error else 0


if __name__ == '__main__':
    raise SystemExit(main())
