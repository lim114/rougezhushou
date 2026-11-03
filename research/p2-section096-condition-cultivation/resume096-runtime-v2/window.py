"""Root-only bounded, isolated real MainWindow verification for section 096.

This source has not been executed by its author. It reuses every original plan
step. Only the named real entrypoints are wrapped to observe their outcomes;
there is no application-wide profile/trace hook, fake calculation or codec graph.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from datetime import datetime, timezone
import functools
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import (freeze, assert_native_equal, sha256, source_map,
                             write_record, read_record)

HERE = Path(__file__).resolve().parent
PLAN_SHA = '55eab397b5bc908263d073318e610c7e23ddd33116759935b31e302144dc20fc'
GOLD_SHA = '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
CODE_SHA = '255d95b7c7241ebc34bb85a01a543bac0f50f7d9b44ad9de7b178a4598c45c36'
PNG_STEPS = {
    'value/four_sui/0': 'condition096-shu-declaration.png',
    'module/uniequip_003_mizuki/stage3/at-P5': 'condition096-mizuki-module.png',
    'priority/account-susuro': 'condition096-account-module.png',
    'priority/return-run': 'condition096-run-base.png',
}
DEADLINE_SECONDS = 600


def fixed_json(name, expected):
    data = (HERE / name).read_bytes()
    assert sha256(data) == expected, ('Bound Source changed', name)
    return json.loads(data)


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n',
                         encoding='utf-8')
    os.replace(temporary, path)


def delta(before, after):
    return {key: after.get(key, 0) - before.get(key, 0)
            for key in sorted(set(before) | set(after))}


def filesystem(folder):
    rows = []
    for path in sorted(folder.rglob('*')):
        if path.is_dir():
            rows.append({'path': path.relative_to(folder).as_posix(), 'kind': 'directory'})
        else:
            raw = path.read_bytes()
            row = {'path': path.relative_to(folder).as_posix(), 'kind': 'file',
                   'raw_bytes': raw, 'sha256': sha256(raw)}
            try:
                row['decoded'] = json.loads(raw.decode('utf-8'))
            except (UnicodeDecodeError, ValueError) as error:
                row['decode_error'] = {'type': type(error).__name__, 'message': str(error)}
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--mode', choices=('gold', 'candidate'), required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--baseline')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.out).resolve()
    assert not output.exists(), 'Use a fresh absent output directory for every attempt'
    assert root.is_dir() and output != root and root not in output.parents
    if args.mode == 'candidate':
        assert args.baseline, 'Candidate requires an actual successful gold output directory'
    else:
        assert not args.baseline, 'Gold does not use a candidate baseline'
    plan = fixed_json('plan.json', PLAN_SHA)
    gold = fixed_json('gold-source.json', GOLD_SHA)['source_sha256_after']
    code = fixed_json('candidate-code.json', CODE_SHA)
    expected = {path: value for path, value in gold.items() if path.startswith('rouge/')}
    if args.mode == 'candidate':
        expected.update({row['destination_repo_path']: row['sha256'] for row in code['files']
                         if row['destination_repo_path'].startswith('rouge/')})
    source_before = source_map(root, ('rouge',))
    assert source_before == expected, 'Exact maintained source set/hash must match the selected mode'
    assert len(gold) == 735 and len(plan['steps']) == 146
    assert len(plan['Linux_cases']) == 1132
    assert set(PNG_STEPS) <= {step['id'] for step in plan['steps']}
    output.mkdir(parents=True)
    records_dir = output / 'records'
    records_dir.mkdir()
    started = time.perf_counter()
    current = 'preimport'
    phase = 'preimport'
    window_id = None
    window = None
    active_folder = None
    account_path = None
    run_path = None
    application = None
    baseline_dir = Path(args.baseline).resolve() if args.baseline else None
    baseline = None
    if baseline_dir:
        baseline = json.loads((baseline_dir / 'receipt.json').read_text(encoding='utf-8'))
        assert baseline['passed'] is True and baseline['workflow_complete'] is True
        assert baseline['kind'] == 'ACTUAL_CONDITION096_BOUNDED_REAL_WINDOW'
        assert baseline['mode'] == 'gold' and baseline['plan_sha256'] == PLAN_SHA
        assert baseline['source_before'] == {path: value for path, value in gold.items()
                                             if path.startswith('rouge/')} and not baseline['source_drift']
        assert baseline['steps_completed'] == 146 and baseline['fresh_windows'] == 2
        assert baseline['explicit_button_requests'] == 144
        assert baseline['runner_sha256'] == sha256(Path(__file__).read_bytes())
        assert baseline['native_helper_sha256'] == sha256((HERE / 'native_evidence.py').read_bytes())
        assert len(baseline['records']) == 146
        assert [row['id'] for row in baseline['records']] == [step['id'] for step in plan['steps']]
    counts = Counter()
    calls = []
    signals = []
    qt_exceptions = []
    record_refs = []
    pngs = []
    fresh_windows = 0
    explicit_buttons = 0
    explicit_texts = 0
    level_restore_buttons = 0
    repeat_level_probes = 0
    auxiliary_actions = []
    finished = threading.Event()
    progress_lock = threading.Lock()
    folders = ExitStack()
    originals = []
    receipt = {'kind': 'ACTUAL_CONDITION096_BOUNDED_REAL_WINDOW', 'mode': args.mode,
               'passed': False, 'workflow_complete': False, 'plan_sha256': PLAN_SHA,
               'runner_sha256': sha256(Path(__file__).read_bytes()),
               'native_helper_sha256': sha256((HERE / 'native_evidence.py').read_bytes()),
               'actual_root': str(root), 'actual_argv': list(sys.argv),
               'actual_cwd': str(Path.cwd()),
               'started_at_UTC': datetime.now(timezone.utc).isoformat(),
               'source_before': source_before, 'source_drift': None,
               'native_windows_verified': False, 'game_chat_executed': False,
               'private_state_isolated': True, 'records': record_refs,
               'all_original_plan_steps_retained': True,
               'historical_plan_corrections': {
                   'placeholder/overview': 'After sparse-run, actual overview contains recruited Susuro; expect original numerical behaviour, not an empty overview.',
                   'empty_overview_constructor_probe': 'In first fresh empty run, use real empty overview and restore original owner before observing ordinary signals.',
                   'damage_tab_visibility': 'Select the actual damage page in both modes before asserting source row visibility.',
                   'module_below_gate_preserved_manual_level': 'Same-owner account observation intentionally preserves a manual level. Use the real read-level restore button before every explicit below-gate fixture, retaining the actual preserved-preview capture.',
                   'repeated_same_level_value': 'After each genuinely changed level action, separately set the same value and require no level signal, no new calculation or durable mutation.',
               },
               'global_profile_or_trace_installed': False,
               'observed_entrypoints': ['calculate_damage', '_prepare_damage', 'MainWindow.calculate',
                                       'AccountCache.observe', 'RunState.apply',
                                       'format_estimate', 'format_report_default', 'format_report_technical'],
               'legacy_all_project_function_vector_measured': False,
               'deadline_seconds': DEADLINE_SECONDS, 'actual_PNGs': pngs}
    previous_hook = sys.excepthook

    def progress(status='running'):
        with progress_lock:
            write_json(output / 'progress.json', {
                'status': status, 'current_step': current, 'phase': phase,
                'completed_steps': len(record_refs), 'planned_steps': 146,
                'fresh_windows': fresh_windows, 'actual_wrapped_entries': len(calls),
                'explicit_button_requests': explicit_buttons,
                'elapsed_seconds': round(time.perf_counter() - started, 3),
                'actual_PNGs': pngs, 'failure': receipt.get('failure'),
            })

    def watchdog():
        if finished.wait(DEADLINE_SECONDS):
            return
        receipt.update(passed=False, workflow_complete=False)
        receipt['failure'] = {'type': 'TimeoutError', 'message': 'Declared 600 second deadline exceeded',
                              'step': current, 'phase': phase}
        receipt['steps_completed'] = len(record_refs)
        receipt['elapsed_seconds'] = round(time.perf_counter() - started, 3)
        receipt['primary_exit_by_watchdog'] = 124
        # Successful per-step native files already exist. This truthfully records
        # a hard deadline even when a native call never returns to Python.
        progress('deadline_exceeded')
        with progress_lock:
            write_json(output / 'receipt.json', receipt)
        os._exit(124)

    threading.Thread(target=watchdog, name='condition096-deadline', daemon=True).start()

    def qt_hook(kind, error, tb):
        qt_exceptions.append({'step': current, 'phase': phase,
                              'type': kind.__name__, 'message': str(error),
                              'traceback': ''.join(traceback.format_exception(kind, error, tb))})

    def check_deadline():
        assert time.perf_counter() - started < DEADLINE_SECONDS, 'Declared runtime deadline exceeded'
        assert not qt_exceptions, ('Unexpected real Qt slot exception', qt_exceptions)

    def wrap_native(owner, name, key, arguments):
        original = getattr(owner, name)
        originals.append((owner, name, original))

        @functools.wraps(original)
        def observed(*positional, **keywords):
            counts[key] += 1
            inputs = arguments(positional, keywords)
            before = freeze(inputs)
            row = {'key': key, 'step': current, 'phase': phase, 'window': window_id,
                   'caller_before': before, 'outcome': 'pending'}
            calls.append(row)
            if key == 'MainWindow.calculate':
                instance = positional[0]
                row['all_outputs_and_controls_exist'] = all(
                    hasattr(instance, item) for item in ('damage_text', 'relic_context') +
                    tuple(c['widget'] for c in plan['controls']))
            try:
                returned = original(*positional, **keywords)
            except BaseException as error:
                row.update(outcome='raised_exception',
                           error={'type': type(error).__name__, 'message': str(error), 'args': error.args},
                           caller_after=inputs)
                assert_native_equal(before, inputs, 'Numeric caller unchanged after original error') if key in ('calculate_damage', '_prepare_damage') else None
                row.update(freeze(row))
                raise
            else:
                row.update(outcome='returned', caller_after=inputs, returned=returned,
                           caller_and_returned={'caller': inputs, 'returned': returned})
                if key in ('calculate_damage', '_prepare_damage'):
                    assert_native_equal(before, inputs, 'Original numeric caller unchanged')
                # Freeze the entire completed graph now, preserving cross-links
                # between the real caller and real returned object.
                complete = freeze(row)
                row.clear()
                row.update(complete)
                return returned

        setattr(owner, name, observed)
        return observed

    def wrap_formatter(owner, name, classifier):
        original = getattr(owner, name)
        originals.append((owner, name, original))

        @functools.wraps(original)
        def observed(*positional, **keywords):
            counts[classifier(positional, keywords)] += 1
            return original(*positional, **keywords)

        setattr(owner, name, observed)
        return observed

    def widget_value(widget):
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QComboBox):
            return widget.currentData()
        if isinstance(widget, QPlainTextEdit):
            return widget.toPlainText()
        return widget.value()

    def common_widget_snapshot(name, widget):
        row = {'name': name, 'class': type(widget).__name__, 'visible': widget.isVisible(),
               'enabled': widget.isEnabled(), 'tooltip': widget.toolTip()}
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            row.update(value=widget.value(), minimum=widget.minimum(), maximum=widget.maximum(),
                       singleStep=widget.singleStep(), prefix=widget.prefix(), suffix=widget.suffix())
            if isinstance(widget, QDoubleSpinBox):
                row['decimals'] = widget.decimals()
        elif isinstance(widget, QCheckBox):
            row.update(value=widget.isChecked(), text=widget.text())
        elif isinstance(widget, QComboBox):
            row.update(current_index=widget.currentIndex(), current_data=widget.currentData(),
                       items=[{'text': widget.itemText(i), 'data': widget.itemData(i)}
                              for i in range(widget.count())])
        elif isinstance(widget, QPlainTextEdit):
            row.update(text=widget.toPlainText(), placeholder=widget.placeholderText(),
                       read_only=widget.isReadOnly())
        elif isinstance(widget, QLineEdit):
            row.update(text=widget.text(), placeholder=widget.placeholderText())
        elif isinstance(widget, QLabel):
            row['text'] = widget.text()
        elif isinstance(widget, QListWidget):
            row['items'] = [{'text': widget.item(i).text(), 'data': widget.item(i).data(Qt.ItemDataRole.UserRole),
                             'check': widget.item(i).checkState().value,
                             'flags': widget.item(i).flags().value,
                             'hidden': widget.item(i).isHidden(), 'tooltip': widget.item(i).toolTip()}
                            for i in range(widget.count())]
        return row

    def ui_snapshot():
        supported = (QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QPlainTextEdit,
                     QLineEdit, QLabel, QListWidget)
        return {'owner': window.operator.currentData(), 'skill': window.skill.currentData(),
                'level': window.level.value(), 'level_override': window.level_override,
                'use_run_training': window.use_run_training.isChecked(),
                'current_operator_state': window.current_operator_state(),
                'visible': window.isVisible(),
                'original_named_widgets': [common_widget_snapshot(name, widget)
                    for name, widget in window.__dict__.items()
                    if isinstance(widget, supported) and name != 'condition_cultivation_explanation'],
                'original_branch_widgets': [common_widget_snapshot(name + '.branch', widget.branch)
                    for name, widget in window.__dict__.items()
                    if hasattr(widget, 'branch') and isinstance(widget.branch, QComboBox)]}

    def durable_snapshot():
        if window is None:
            return None
        return freeze({'run': window.run.state, 'account_records': window.account_cache.records,
                       'account_issues': window.account_cache.issues,
                       'preserve_original': window.account_cache.preserve_original,
                       'account_bytes': account_path.read_bytes() if account_path.exists() else None,
                       'run_bytes': run_path.read_bytes() if run_path.exists() else None,
                       'files': filesystem(active_folder),
                       'operator_observations_alias_is_records': window.operator_observations is window.account_cache.records})

    def external_idle():
        assert not window.auto.isChecked() and window.capture.target is None
        assert not window.desktop.process and not window.desktop_request_busy
        assert not (active_folder / 'chat').exists()
        assert not module.list_game_windows(), 'No live game integration is used'

    def observe_signals():
        def received(binding, widget, value):
            signals.append(freeze({'window': window_id, 'step': current, 'phase': phase,
                                   'binding': binding, 'widget_class': type(widget).__name__,
                                   'emitted_value': value, 'current_widget_value': widget_value(widget)}))
        for item in plan['controls']:
            widget = getattr(window, item['widget'])
            binding = {'kind': 'common', 'widget': item['widget'], 'signal': item['signal']}
            if item['widget'] == 'timing_scenario':
                getattr(widget, item['signal']).connect(
                    lambda w=widget, b=binding: received(b, w, w.toPlainText()))
            else:
                getattr(widget, item['signal']).connect(
                    lambda value, w=widget, b=binding: received(b, w, value))
        observed = []
        for index, (owner, field, skills, widget) in enumerate(window.model_option_widgets):
            matching = [item for item in plan['condition_controls']
                        if item['owner'] == owner and item['field'] == field]
            if not matching:
                continue
            assert len(matching) == 1
            item = matching[0]
            assert list(skills) == item['skills'] and type(widget).__name__ == item['widget_class']
            binding = {'kind': 'condition', 'owner': owner, 'field': field,
                       'skills': list(skills), 'model_option_index': index, 'signal': item['signal']}
            getattr(widget, item['signal']).connect(
                lambda value, w=widget, b=binding: received(b, w, value))
            observed.append(binding)
        assert len(observed) == 9

    def three_texts():
        nonlocal explicit_texts
        if window.damage_result is None:
            return {'applicable': False, 'visible_status': window.damage_text.toPlainText()}
        value = window.damage_result
        before = freeze(value)
        result = value['result']
        strings = {'estimate': estimate.format_estimate(result),
                   'default': reporting.format_report(result),
                   'technical': reporting.format_report(result, technical=True)}
        explicit_texts += 3
        assert strings['estimate'] == strings['default']
        expected_text = (json.dumps(value, ensure_ascii=False, indent=2)
                         if window.raw_damage.isChecked() else
                         strings['technical' if window.damage_technical.isChecked() else 'default'])
        assert window.damage_text.toPlainText() == expected_text.replace(chr(160), ' ')
        assert_native_equal(value, before, 'Real formatting must not mutate the native report')
        return {'applicable': True, 'strings': strings, 'requested_count': 3}

    def old_controls():
        full = []
        comparable = []
        allowed = {(item['owner'], item['field']) for item in plan['condition_controls']}
        for index, (owner, field, skills, widget) in enumerate(window.model_option_widgets):
            row = {'index': index, 'owner': owner, 'field': field, 'skills': skills,
                   'widget_class': type(widget).__name__, 'value': widget_value(widget),
                   'visible': widget.isVisible(), 'enabled': widget.isEnabled(), 'tooltip': widget.toolTip()}
            if hasattr(widget, 'minimum'):
                row.update(minimum=widget.minimum(), maximum=widget.maximum(), singleStep=widget.singleStep())
            full.append(row)
            comparison = dict(row)
            if (owner, field) in allowed:
                comparison['tooltip'] = 'EXACT_NINE_SOURCE_BOUND_PRESENTATION_TOOLTIP_DELTA'
            comparable.append(comparison)
        return {'full': full, 'comparison': comparable}

    def condition_probe(ui, step):
        if args.mode == 'gold':
            assert not hasattr(window, 'condition_cultivation_rows')
            assert not hasattr(window, 'condition_cultivation_explanation')
            return None
        rows = window.condition_cultivation_rows
        label = window.condition_cultivation_explanation
        owner, skill = ui['owner'], ui['skill']
        expected_fields = [field for op, field, skills, widget in window.model_option_widgets
                           if op == owner and skill in skills and field in plan['target_fields']]
        assert [row['field'] for row in rows] == expected_fields
        state = ui['current_operator_state'] or {}
        fields = state.get('fields', {})
        confirmed = state.get('run_confirmed_fields', ()) if state.get('scope') == 'run' else ()
        provenance = {key: ('simulated_override' if key == 'level' and ui['level_override'] else
                           'preview_unconfirmed' if key not in fields else
                           'run_confirmed' if key in confirmed else 'account_reference')
                      for key in ('elite', 'level', 'potential', 'module_id', 'module_level')}
        effective = ({'elite': fields.get('elite', plan['profile_preview_facts'][owner]['maximum_elite']),
                      'level': ui['level'], 'potential': fields.get('potential', 1),
                      'module_id': fields.get('module_id'), 'module_level': fields.get('module_level', 0)}
                     if rows else None)
        source_labels = {'run_confirmed': '本局确认', 'account_reference': '账号参考（本局未确认）',
                         'preview_unconfirmed': '来源缺失，采用预览', 'simulated_override': '手动等级预览'}
        tooltips = []
        for row in rows:
            widget = next(widget for op, field, skills, widget in window.model_option_widgets
                          if op == owner and field == row['field'] and skill in skills)
            assert row['operator'] == owner
            assert row['eligibility_status'] == ('unavailable' if row['selection_error'] is not None else
                                                 'met' if row['selected_talent'] is not None else 'unmet')
            assert_native_equal(row['condition_value'], widget_value(widget), 'Fresh displayed condition value')
            assert row['new_arithmetic_applied'] is False
            assert row['actual_activation'] is None and row['native_attachment'] is None
            assert row['account_unlock_verified'] is None
            assert_native_equal(row['training_provenance'], provenance, 'Per-field public provenance')
            assert_native_equal(row['effective_training'], effective, 'Current merged training and manual level')
            relevant = ('elite', 'level', 'potential') + (('module_id', 'module_level') if effective['module_id'] else ())
            assert row['uses_unconfirmed_preview'] is any(provenance[key] in ('preview_unconfirmed', 'simulated_override') for key in relevant)
            assert row['uses_account_reference'] is any(provenance[key] == 'account_reference' for key in relevant)
            definition = next(item for item in plan['field_source_definitions'][owner]
                              if item['field'] == row['field'])
            for key in ('label', 'talent_name', 'talent_index', 'first_original_gate', 'modeled_parameter_keys', 'scope_note'):
                assert_native_equal(row[key], definition[key], 'Complete pinned definition: ' + key)
            original = row['original_source']
            if original is not None:
                assert plan['source_coordinate_owners'][original['path']] == owner
                for key, value in plan['source_coordinate_facts'][original['path']].items():
                    assert_native_equal(original[key], value, 'Complete raw original coordinate: ' + key)
                assert row['source_status'] == 'located'
            elif row['selected_talent'] is not None or row['selection_error'] is not None:
                assert row['source_status'] == 'missing'
            else:
                assert row['source_status'] == 'not_selected'
            if row['field'] in step.get('expected_field_qualification', {}):
                assert row['eligibility_status'] == step['expected_field_qualification'][row['field']]
            designated = step.get('expected_presentation')
            if designated:
                for key in ('training_provenance', 'uses_unconfirmed_preview', 'uses_account_reference',
                            'eligibility_status', 'source_status', 'effective_training'):
                    assert_native_equal(row[key], designated[key], 'Designated source-bound transition: ' + key)
                assert original is not None and original['path'] == designated['original_source_path']
                assert ui['level_override'] is designated['level_override']
                assert designated['source_text_contains'] in widget.toolTip()
            tooltip = widget.toolTip()
            assert tooltip and row['talent_name'] in tooltip and row['scope_note'] in tooltip
            assert '培养资格不确认实际触发、账号任务解锁或原生附着。' in tooltip
            assert all(source_labels[provenance[key]] in tooltip for key in relevant)
            tooltips.append(tooltip)
        assert label.text() == '\n\n'.join(tooltips)
        assert label.isVisible() is bool(rows)
        if not rows:
            assert not label.text()
        return {'rows': rows, 'text': label.text(), 'visible': label.isVisible(), 'tooltips': tooltips,
                'verified_without_calling_presentation_helper_for_expected_answer': True}

    def capture(step):
        ui = ui_snapshot()
        return freeze({'damage_result': window.damage_result, 'UI': ui,
                       'visible_status': window.damage_text.toPlainText(), 'three_texts': three_texts(),
                       'old_controls': old_controls(), 'new_presentation': condition_probe(ui, step)})

    def comparable_capture(value):
        # The exact nine newly replaced tooltip strings are allowed presentation
        # changes. Both complete tooltip vectors remain saved. No math/report/
        # text section or non-target control is projected away.
        return {'damage_result': value['damage_result'], 'UI': value['UI'],
                'visible_status': value['visible_status'], 'three_texts': value['three_texts'],
                'old_controls': value['old_controls']['comparison']}

    def close_window():
        nonlocal window, phase
        if window is None:
            return
        phase = 'close_window'
        external_idle()
        before = durable_snapshot()
        window.close()
        application.processEvents()
        assert_native_equal(durable_snapshot(), before, 'Closing preserves public durable state')
        window.deleteLater()
        application.processEvents()
        window = None

    def fresh_window(step):
        nonlocal window, active_folder, account_path, run_path, window_id, fresh_windows, phase
        close_window()
        fresh_windows += 1
        window_id = 'public-condition096-window-' + str(fresh_windows)
        active_folder = Path(folders.enter_context(tempfile.TemporaryDirectory(prefix='public-condition096-')))
        account_path = active_folder / 'account.json'
        run_path = active_folder / 'run.json'
        account_path.write_text(json.dumps(step['fixture'], ensure_ascii=False, allow_nan=False), encoding='utf-8')
        run_path.write_text(json.dumps(plan['public_run_initial'], ensure_ascii=False, allow_nan=False), encoding='utf-8')
        module.OPERATOR_STATE = account_path
        module.RUN_STATE = run_path
        module.SETTINGS = active_folder / 'settings.json'
        module.DesktopBackend = lambda _path, callback: real_backend(active_folder / 'chat', callback)
        phase = 'real_MainWindow_constructor'
        index = len(calls)
        window = module.MainWindow()
        window.resize(1400, 1050)
        window.show()
        # Make the actual damage page visible in both modes. The original
        # pending template never selected it before asserting QLabel visibility.
        window.centralWidget().setCurrentIndex(1)
        application.processEvents()
        assert type(window.run) is RunState
        assert window.operator_observations is window.account_cache.records
        assert window.isVisible()
        assert all(row['all_outputs_and_controls_exist'] for row in calls[index:]
                   if row['key'] == 'MainWindow.calculate')
        external_idle()
        empty_probe = None
        if fresh_windows == 1:
            # The old later plan expected an empty overview even after adding
            # a recruited operator. Cover the real empty state here instead;
            # no RunState mutation/reset and no invented calculation result.
            assert not window.recruited_operator_ids()
            original_owner = window.operator.currentData()
            assert original_owner is not None
            durable_before = durable_snapshot()
            counts_before = dict(counts)
            call_start = len(calls)
            phase = 'real_empty_overview_constructor_probe'
            assert window.operator_choices.select_branch('__overview__')
            application.processEvents()
            assert window.operator.currentData() is None and window.damage_result is None
            assert '本局总览暂无已确认招募干员。' in window.damage_text.toPlainText()
            assert counts['MainWindow.calculate'] > counts_before.get('MainWindow.calculate', 0)
            assert not any(row['key'] == 'calculate_damage' for row in calls[call_start:])
            empty_probe = {'original_owner': original_owner, 'empty': capture(step),
                           'empty_entries': delta(counts_before, counts),
                           'durable_before': durable_before}
            assert_native_equal(durable_snapshot(), durable_before, 'Real empty overview preserves public state')
            restore_before = dict(counts)
            phase = 'real_empty_overview_restore_original_owner'
            assert window.select_operator(original_owner)
            application.processEvents()
            assert window.operator.currentData() == original_owner
            assert counts['MainWindow.calculate'] > restore_before.get('MainWindow.calculate', 0)
            empty_probe.update(restored=capture(step), restore_entries=delta(restore_before, counts),
                               durable_after=durable_snapshot())
            assert_native_equal(empty_probe['durable_after'], durable_before, 'Restoring original owner preserves public state')
        observe_signals()
        return freeze(empty_probe)

    def action(step):
        nonlocal phase, level_restore_buttons, repeat_level_probes
        phase = 'automatic_action'
        kind = step['action']
        if kind == 'account_observation':
            data = freeze(step['observation'])
            window.apply_operator_observation(data, data['captured_at'])
            application.processEvents()
            assert window.operator.currentData() == data['id'] and window.skill.currentData() == step['skill']
            for key, value in data['fields'].items():
                assert_native_equal(window.account_cache.records[data['id']]['fields'].get(key), value,
                                    'Actual account observation ' + key)
            if step['id'].startswith('module/') and step['id'].endswith('/below-P4'):
                # Account observation keeps an existing same-owner manual
                # preview by design. Restore via the existing real UI action
                # so this named below-gate test genuinely uses the read level.
                before_restore = durable_snapshot()
                preserved = capture(step)
                restore_counts = dict(counts)
                restore_signals = len(signals)
                phase = 'actual_use_read_level_restore_button'
                button = next(button for button in window.findChildren(QPushButton)
                              if button.text() == '使用读取等级')
                button.click()
                level_restore_buttons += 1
                application.processEvents()
                assert window.level.value() == data['fields']['level']
                assert window.level_override is False
                assert counts['MainWindow.calculate'] > restore_counts.get('MainWindow.calculate', 0)
                assert not any(row['binding'].get('widget') == 'level' for row in signals[restore_signals:]), 'Read-level restoration deliberately blocks the widget valueChanged signal'
                assert_native_equal(durable_snapshot(), before_restore,
                                    'Actual read-level restore does not mutate account/run/files')
                restored = capture(step)
                auxiliary_actions.append(freeze({'kind': 'actual_read_level_restore', 'step': current,
                    'preserved_manual_preview': preserved, 'restored_read_level': restored,
                    'entry_counts': delta(restore_counts, counts), 'durable_before': before_restore,
                    'durable_after': durable_snapshot(), 'signals': signals[restore_signals:]}))
                phase = 'automatic_action'
        elif kind == 'run_observation':
            assert window.apply_run_observation(freeze(step['observation']), step['captured_at'])
            application.processEvents()
            assert window.current_operator_state()['scope'] == 'run'
        elif kind == 'condition_value':
            matching = [widget for owner, field, skills, widget in window.model_option_widgets
                        if owner == step['owner'] and field == step['field'] and window.skill.currentData() in skills]
            assert len(matching) == 1
            widget = matching[0]
            before = widget_value(widget)
            assert type(before) is type(step['value']) and before != step['value']
            first = len(signals)
            if isinstance(widget, QCheckBox):
                widget.setChecked(step['value'])
            else:
                widget.setValue(step['value'])
            application.processEvents()
            actual = [row for row in signals[first:] if row['binding'].get('owner') == step['owner']
                      and row['binding'].get('field') == step['field']]
            assert len(actual) == 1
            assert_native_equal(actual[0]['emitted_value'], step['value'], 'Exactly one actual condition signal')
            assert_native_equal(actual[0]['current_widget_value'], step['value'], 'Actual current raw widget value')
        elif kind == 'level':
            before_level = window.level.value()
            assert before_level != step['value'], 'A declared changed-level step must really change the current value'
            signal_start = len(signals)
            window.level.setValue(step['value'])
            application.processEvents()
            emitted = [row for row in signals[signal_start:] if row['binding'].get('widget') == 'level']
            assert len(emitted) == 1
            assert_native_equal(emitted[0]['emitted_value'], step['value'], 'Genuine changed-level valueChanged')
            assert window.level_override is True and window.level.value() == step['value']
            changed = capture(step)
            repeat_durable = durable_snapshot()
            repeat_counts = dict(counts)
            repeat_signals = len(signals)
            phase = 'actual_repeat_same_level_value'
            window.level.setValue(step['value'])
            repeat_level_probes += 1
            application.processEvents()
            assert window.level.value() == step['value'] and window.level_override is True
            assert len(signals) == repeat_signals, 'Setting the same QSpinBox value must not emit a fresh signal'
            assert dict(counts) == repeat_counts, 'Same-value level setter must not recalculate or format'
            repeat_after_setter = dict(counts)
            assert_native_equal(durable_snapshot(), repeat_durable, 'Same-value level setter preserves complete state/files')
            repeated = capture(step)
            assert_native_equal(repeated, changed, 'Same-value level setter preserves full native/UI/three texts/presentation')
            auxiliary_actions.append(freeze({'kind': 'actual_repeat_same_level_value', 'step': current,
                'changed_value': changed, 'same_value': repeated, 'level_before_genuine_change': before_level,
                'level_after': step['value'], 'new_signal_count': len(signals) - repeat_signals,
                'setter_entries_before_formatter_probe': delta(repeat_counts, repeat_after_setter),
                'durable_before': repeat_durable, 'durable_after': durable_snapshot()}))
            phase = 'automatic_action'
        elif kind in ('technical', 'raw', 'use_run_training'):
            widget = getattr(window, {'technical': 'damage_technical', 'raw': 'raw_damage',
                                      'use_run_training': 'use_run_training'}[kind])
            assert widget.isChecked() != step['value']
            widget.setChecked(step['value'])
        elif kind == 'timing_text':
            assert window.timing_scenario.toPlainText() != step['value']
            window.timing_scenario.setPlainText(step['value'])
        elif kind == 'overview':
            # Source-corrected original step: sparse-run has already recruited
            # Susuro. Its identity remains selected when opening this overview,
            # so BranchChoice legitimately emits no unchanged identity callback.
            assert 'char_298_susuro' in window.recruited_operator_ids()
            assert window.operator.currentData() == 'char_298_susuro'
            assert window.operator_choices.select_branch('__overview__')
            assert window.operator.currentData() == 'char_298_susuro'
        elif kind == 'select':
            assert window.select_operator(step['owner'])
            index = window.skill.findData(step['skill'])
            assert index >= 0
            window.skill.setCurrentIndex(index)
        else:
            raise AssertionError(('Unknown original fixed-plan action', kind))
        application.processEvents()

    def validate(step, observed, changes, require_callback=True):
        expected = step.get('expected', {})
        kind = ('numerical_result' if step['id'] == 'placeholder/overview'
                else expected.get('kind', 'numerical_result'))
        numeric = [row for row in observed if row['key'] == 'calculate_damage']
        if require_callback:
            assert changes.get('MainWindow.calculate', 0) > 0, ('No actual calculation callback', step['id'])
        if kind == 'JSON_error_before_numerical_API':
            assert not numeric and window.damage_result is None
            assert window.damage_text.toPlainText() == expected['message']
        elif kind == 'natural_early_return':
            assert not numeric and window.damage_result is None
            assert expected['text_contains'] in window.damage_text.toPlainText()
        else:
            assert type(window.damage_result) is dict, window.damage_text.toPlainText()
            assert all(row['outcome'] == 'returned' and type(row['returned']) is dict for row in numeric)
        return kind

    def screenshot(step):
        if args.mode != 'candidate' or step['id'] not in PNG_STEPS:
            return
        label = window.condition_cultivation_explanation
        assert label.isVisible() and label.text()
        damage_tab = window.centralWidget().widget(1)
        scroll = damage_tab.findChild(QScrollArea)
        assert scroll is not None
        scroll.ensureWidgetVisible(label, 20, 20)
        application.processEvents()
        path = output / PNG_STEPS[step['id']]
        assert window.grab().save(str(path)) and path.stat().st_size > 0
        pngs.append({'file': path.name, 'step': step['id'], 'bytes': path.stat().st_size,
                     'sha256': sha256(path.read_bytes()), 'actual_view_by_root_pending': True})

    def run_step(step, sequence):
        nonlocal current, phase, explicit_buttons
        check_deadline()
        current = step['id']
        phase = 'before_step'
        progress()
        count_before = dict(counts)
        call_before = len(calls)
        signal_before = len(signals)
        auxiliary_before = len(auxiliary_actions)
        record = {'id': current, 'planned': freeze(step), 'passed': False,
                  'window_before': window_id, 'durable_before': durable_snapshot()}
        if step['action'] == 'fresh_window':
            record['constructor_empty_probe'] = fresh_window(step)
            record['automatic'] = capture(step)
        else:
            before_automatic = dict(counts)
            before_call = len(calls)
            action(step)
            changes = delta(before_automatic, counts)
            render_only = step['action'] in ('technical', 'raw')
            if render_only:
                assert not any(row['key'] == 'calculate_damage' for row in calls[before_call:])
                assert changes.get('MainWindow.calculate', 0) == 0
            if step['id'] == 'placeholder/overview':
                assert changes.get('MainWindow.calculate', 0) == 0
                assert not any(row['key'] == 'calculate_damage' for row in calls[before_call:])
            outcome = validate(step, calls[before_call:], changes,
                               not render_only and step['id'] != 'placeholder/overview')
            record['automatic'] = capture(step)
            record['automatic_entries'] = delta(before_automatic, counts)
            after_automatic = durable_snapshot()
            record['durable_after_automatic'] = after_automatic
            if step['action'] not in ('account_observation', 'run_observation'):
                assert_native_equal(after_automatic, record['durable_before'], 'Preview and render preserve durable state')
            phase = 'manual_button'
            progress()
            before_manual = dict(counts)
            before_call = len(calls)
            explicit_buttons += 1
            button = next(button for button in window.findChildren(QPushButton)
                          if button.text() == '计算属性与技能预估')
            button.click()
            application.processEvents()
            assert validate(step, calls[before_call:], delta(before_manual, counts)) == outcome
            record['manual'] = capture(step)
            record['manual_entries'] = delta(before_manual, counts)
            assert_native_equal(record['automatic']['damage_result'], record['manual']['damage_result'],
                                'Automatic and actual manual button full native result')
            assert_native_equal(record['automatic']['three_texts'], record['manual']['three_texts'],
                                'Automatic and actual manual button all three full strings')
            assert_native_equal(durable_snapshot(), after_automatic, 'Actual manual calculation preserves state and files')
        check_deadline()
        record.update(window_after=window_id, durable_after=durable_snapshot(),
                      entry_counts=delta(count_before, counts),
                      completed_native_calls=calls[call_before:], actual_signals=signals[signal_before:],
                      auxiliary_actions=auxiliary_actions[auxiliary_before:])
        assert all(row['outcome'] != 'pending' for row in record['completed_native_calls'])
        external_idle()
        if baseline:
            old = read_record(baseline_dir / 'records', baseline['records'][sequence - 1])
            for key in ('id', 'planned', 'window_before', 'window_after', 'durable_before', 'durable_after',
                        'entry_counts', 'completed_native_calls', 'actual_signals'):
                assert_native_equal(record[key], old[key], 'Complete old behaviour pair: ' + key)
            assert len(record['auxiliary_actions']) == len(old['auxiliary_actions'])
            for probe, old_probe in zip(record['auxiliary_actions'], old['auxiliary_actions']):
                assert probe['kind'] == old_probe['kind']
                capture_keys = (('preserved_manual_preview', 'restored_read_level')
                                if probe['kind'] == 'actual_read_level_restore' else ('changed_value', 'same_value'))
                for key in probe:
                    assert key in old_probe
                    if key in capture_keys:
                        assert_native_equal(comparable_capture(probe[key]), comparable_capture(old_probe[key]),
                                            'Actual auxiliary full native/UI/three-text pair: ' + key)
                    else:
                        assert_native_equal(probe[key], old_probe[key], 'Actual auxiliary signal/state/entry pair: ' + key)
            if 'durable_after_automatic' in record:
                assert_native_equal(record['durable_after_automatic'], old['durable_after_automatic'], 'Full automatic durable pair')
            if 'constructor_empty_probe' in record:
                probe, old_probe = record['constructor_empty_probe'], old['constructor_empty_probe']
                if probe is None:
                    assert old_probe is None
                else:
                    for key in ('original_owner', 'empty_entries', 'restore_entries', 'durable_before', 'durable_after'):
                        assert_native_equal(probe[key], old_probe[key], 'Real constructor empty/restore pair: ' + key)
                    for key in ('empty', 'restored'):
                        assert_native_equal(comparable_capture(probe[key]), comparable_capture(old_probe[key]),
                                            'Real constructor empty/restore complete native/UI/text pair: ' + key)
            for key in ('automatic', 'manual'):
                if key in record:
                    assert_native_equal(comparable_capture(record[key]), comparable_capture(old[key]),
                                        'Complete old native/UI/three-text capture pair: ' + key)
            for key in ('automatic_entries', 'manual_entries'):
                if key in record:
                    assert_native_equal(record[key], old[key], 'Actual wrapped entry pair: ' + key)
        record['passed'] = True
        reference = write_record(records_dir, sequence, freeze(record))
        reference['id'] = current
        record_refs.append(reference)
        screenshot(step)
        progress()

    try:
        sys.excepthook = qt_hook
        sys.path.insert(0, str(root))
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QLabel, QLineEdit,
                                      QListWidget, QPlainTextEdit, QPushButton, QSpinBox,
                                      QDoubleSpinBox, QScrollArea)
        import rouge.app as module
        import rouge.damage as damage
        import rouge.estimate as estimate
        import rouge.reporting as reporting
        from rouge.run_state import RunState
        from rouge.account_cache import AccountCache
        real_backend = module.DesktopBackend
        wrap_native(damage, '_prepare_damage', '_prepare_damage', lambda a, k: {'scenario': a[0] if a else k['scenario']})
        real_damage = wrap_native(module, 'calculate_damage', 'calculate_damage', lambda a, k: {'scenario': a[0] if a else k['scenario']})
        # Both actual import aliases retain the same observed real entrypoint.
        originals.append((damage, 'calculate_damage', damage.calculate_damage))
        damage.calculate_damage = real_damage
        wrap_native(module.MainWindow, 'calculate', 'MainWindow.calculate', lambda a, k: {})
        wrap_native(AccountCache, 'observe', 'AccountCache.observe',
                    lambda a, k: {'operator': a[1] if len(a) > 1 else k['operator'],
                                  'captured_at': a[2] if len(a) > 2 else k['captured_at']})
        wrap_native(RunState, 'apply', 'RunState.apply',
                    lambda a, k: {'observed': a[1] if len(a) > 1 else k['observed'],
                                  'captured_at': a[2] if len(a) > 2 else k['captured_at']})
        observed_estimate = wrap_formatter(estimate, 'format_estimate', lambda a, k: 'format_estimate')
        observed_report = wrap_formatter(reporting, 'format_report',
            lambda a, k: 'format_report_technical' if k.get('technical', a[1] if len(a) > 1 else False)
            else 'format_report_default')
        originals.extend([(module, 'format_estimate', module.format_estimate),
                          (module, 'format_report', module.format_report)])
        module.format_estimate, module.format_report = observed_estimate, observed_report
        application = QApplication([])
        application.setQuitOnLastWindowClosed(False)
        for sequence, step in enumerate(plan['steps'], 1):
            run_step(step, sequence)
        close_window()
        assert len(record_refs) == 146 and fresh_windows == 2 and explicit_buttons == 144
        assert level_restore_buttons == 24 and repeat_level_probes == 26
        assert not qt_exceptions
        assert all(row['outcome'] != 'pending' for row in calls)
        if args.mode == 'candidate':
            assert len(pngs) == 4
        else:
            assert not pngs
        receipt.update(passed=True, workflow_complete=True)
    except BaseException as error:
        receipt['failure'] = {'type': type(error).__name__, 'message': str(error),
                              'step': current, 'phase': phase, 'traceback': traceback.format_exc()}
        # Keep the unfinished native graph in addition to every successful prefix.
        try:
            receipt['unfinished'] = write_record(output, 1, freeze({
                'step': current, 'phase': phase, 'calls': calls, 'signals': signals,
                'Qt_slot_exceptions': qt_exceptions, 'durable': durable_snapshot(),
                'auxiliary_actions': auxiliary_actions}))
        except BaseException as evidence_error:
            receipt['unfinished_save_error'] = str(evidence_error)
    finally:
        try:
            close_window()
        except BaseException as error:
            receipt.update(passed=False, workflow_complete=False,
                           close_error={'type': type(error).__name__, 'message': str(error)})
        for owner, name, original in reversed(originals):
            setattr(owner, name, original)
        sys.excepthook = previous_hook
        source_after = source_map(root, ('rouge',))
        receipt['source_after'] = source_after
        receipt['source_drift'] = [path for path in sorted(set(source_before) | set(source_after))
                                   if source_before.get(path) != source_after.get(path)]
        if receipt['source_drift']:
            receipt.update(passed=False, workflow_complete=False)
        receipt.update(steps_completed=len(record_refs), fresh_windows=fresh_windows,
                       explicit_button_requests=explicit_buttons, explicit_three_text_requests=explicit_texts,
                       actual_read_level_restore_button_requests=level_restore_buttons,
                       actual_repeat_same_level_value_probes=repeat_level_probes,
                       actual_wrapped_calls=len(calls), actual_signal_count=len(signals),
                       actual_entry_counts=dict(counts), Qt_slot_exceptions=qt_exceptions,
                       elapsed_seconds=round(time.perf_counter() - started, 3),
                       ended_at_UTC=datetime.now(timezone.utc).isoformat())
        folders.close()
        with progress_lock:
            write_json(output / 'receipt.json', receipt)
        progress('passed' if receipt['passed'] else 'failed')
        finished.set()
        print(json.dumps({'passed': receipt['passed'], 'steps': len(record_refs),
                          'failure': receipt.get('failure')}, ensure_ascii=False), flush=True)
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
