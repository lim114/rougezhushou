"""Source-only proposal. Root executes six real retained-state MainWindows.

All inputs are public temporary JSON. Ordinary UI/API/report work is pure.
Only explicitly bracketed MainWindow.apply_run_observation calls may save.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import threading
import time
import traceback

sys.dont_write_bytecode = True
from native_evidence import freeze, assert_native_equal, write_record, source_map

HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
DEADLINE = 900
OP = 'mechanist'
ATTACK = 'rogue_6_relic_legacy_15'
ALTAR = 'rogue_6_relic_legacy_103'
TOOL = 'rogue_6_active_tool_5'
SNACK = 'rogue_6_from_relic_13'
COOKIE = 'rogue_6_from_relic_9'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))}


def visible_metric_label(label):
    assert type(label) is str
    for raw, shown in (('DPS/HPS', '每秒伤害 / 每秒治疗'), ('DPS', '每秒伤害'), ('HPS', '每秒治疗')):
        label = label.replace(raw, shown)
    return re.sub(r' (?=每秒伤害|每秒治疗)', '', label).strip()


def fsync_json(path, value, *, exclusive=False):
    with path.open('x' if exclusive else 'w', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser()
    for key in ('root', 'guard', 'out'):
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--source-count', type=int, required=True)
    args = parser.parse_args()
    root, out = Path(args.root).resolve(), Path(args.out).resolve()
    artifact, guard_path = Path(__file__).resolve().parent, Path(args.guard).resolve()
    assert not out.exists() and root not in out.parents and out != root
    assert artifact != root and root not in artifact.parents
    assert sha((artifact / 'native_evidence.py').read_bytes()) == HELPER_SHA
    cases_raw = (artifact / 'cases.json').read_bytes()
    specs = json.loads(cases_raw)
    assert specs['section'] == 122 and specs['expected_contexts'] == 6
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    expected, extra = guard['source_sha256'], guard['source_additional_sha256']
    assert guard['section'] == 122 and len(expected) == args.source_count and source_map(root) == expected
    assert set(extra) == {'CORE_0.70_VERIFICATION.json'}
    for name, want in extra.items():
        assert sha((root / name).read_bytes()) == want
    out.mkdir()
    (out / 'records').mkdir()
    (out / 'public-state').mkdir()
    rows, records, pngs, calls, errors, contexts, ingresses = [], [], [], [], [], [], []
    active = {'context': 'bootstrap', 'case': 'bootstrap', 'phase': 'constructor'}
    window = module = backend = calculator = None
    original_paths = None
    started = time.perf_counter()
    done = threading.Event()
    receipt = {'kind': 'ROOT_ACTUAL_122_REAL_MAINWINDOW', 'section': 122, 'phase': 'candidate',
               'passed': False, 'workflow_complete': False,
               'runner_sha256': sha(Path(__file__).read_bytes()),
               'cases_sha256': sha(cases_raw), 'native_helper_sha256': HELPER_SHA,
               'source_guard_sha256': sha(guard_raw), 'source_count': args.source_count,
               'source_before': expected, 'source_additional_before': extra,
               'rows': rows, 'records': records, 'contexts': contexts,
               'ingresses': ingresses, 'pngs': pngs, 'Qt_errors': errors,
               'deadline_seconds': DEADLINE, 'private_state_access': False,
               'native_windows_verified': False, 'game_chat_sampling_executed': False,
               'read_purity_scope': 'Ordinary MainWindow/UI/API/three-formatters preserve complete current run/account/raw disks; public ingress is separately and narrowly bracketed.',
               'mutation_scope': 'Only public MainWindow.apply_run_observation runs; numeric callbacks inside each exact bracket see the final saved joint. No generic case or phase mutation exemption.',
               'restart_scope': 'Six real close operations followed by direct RunState and AccountCache reloads. The RunState constructor changes only the documented restore notice; no second live window or JSON alias claim.',
               'PNG_scope': 'Two actual bounded views linked to their immediate native snapshot: initial unknown run-summary QLabel and later fresh-Snack damage metrics. Root separately views original PNG pixels.',
               'rank_erratum': specs['rank_erratum']}

    def checkpoint():
        fsync_json(out / 'checkpoint.json', {'active': dict(active),
                   'completed_row_ids': [row['id'] for row in rows],
                   'completed_context_ids': [item['id'] for item in contexts],
                   'records': records, 'rows': rows, 'ingresses': ingresses,
                   'contexts': contexts, 'pngs': pngs,
                   'source_guard_sha256': sha(guard_raw)})

    def save(kind, **value):
        ref = write_record(out / 'records', len(records) + 1,
                           {'kind': kind, **active, **value})
        ref.update(kind=kind, **active)
        records.append(ref)
        checkpoint()
        return ref

    def watchdog():
        if not done.wait(DEADLINE):
            fsync_json(out / 'timeout.json', {'passed': False, 'active': dict(active),
                       'deadline_seconds': DEADLINE}, exclusive=True)
            os._exit(124)

    threading.Thread(target=watchdog, daemon=True).start()
    old_hook = sys.excepthook

    def hook(kind, value, tb):
        errors.append({**active, 'type': kind.__name__, 'message': str(value)})
        old_hook(kind, value, tb)

    sys.excepthook = hook
    try:
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(root))
        from PySide6.QtCore import Qt, qVersion
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from rouge import app as module, estimate, reporting
        from rouge.account_cache import AccountCache
        from rouge.catalog import catalog, operator_profiles
        from rouge.record_flags import metadata_mask, RECIPIENT_KEYS
        from rouge.run_state import RunState
        from rouge.training_view import format_run_training_observation
        application = QApplication.instance() or QApplication([])
        backend, calculator = module.DesktopBackend, module.calculate_damage
        original_paths = (module.RUN_STATE, module.OPERATOR_STATE, module.SETTINGS)
        receipt.update(python=sys.version, platform=sys.platform,
                       newline=os.linesep, qt=qVersion())

        def observed(*positional, **keywords):
            context = {'args': positional, 'kwargs': keywords,
                       **({'joint': joint()} if window is not None else {})}
            before = freeze(context)
            try:
                value = calculator(*positional, **keywords)
            except Exception as error:
                after = {'args': positional, 'kwargs': keywords,
                         **({'joint': joint()} if window is not None else {})}
                ref = save('actual_calculate_exception', before=before, after=after,
                           error=error_record(error))
                calls.append({'before': before, 'error': error_record(error), 'native': ref})
                assert_native_equal(after, before, 'exception complete caller purity')
                raise
            after = {'args': positional, 'kwargs': keywords,
                     **({'joint': joint()} if window is not None else {})}
            ref = save('actual_calculate_result', before=before, after=after, result=value)
            calls.append({'before': before, 'after': after, 'error': None,
                          'native': ref, 'return_value': value})
            assert_native_equal(after, before, 'numeric complete caller purity')
            return value

        module.calculate_damage = observed
        for context_case in specs['contexts']:
            identity = context_case['id']
            active.update(context=identity, case='initial', phase='constructor')
            with tempfile.TemporaryDirectory(prefix='public122-' + identity + '-',
                                             dir=out / 'public-state') as directory:
                folder = Path(directory)
                run_path, account_path = folder / 'run.json', folder / 'account.json'
                run_raw = (json.dumps(context_case['run'], ensure_ascii=False, indent=2) + '\n').encode()
                account_raw = (json.dumps(context_case['account'], ensure_ascii=False, indent=2) + '\n').encode()
                run_path.write_bytes(run_raw)
                account_path.write_bytes(account_raw)
                module.RUN_STATE, module.OPERATOR_STATE = run_path, account_path
                module.SETTINGS = folder / 'settings.json'
                module.DesktopBackend = lambda _path, callback: backend(folder / 'chat', callback)

                def joint():
                    return {'run': window.run.state, 'account': window.account_cache.records,
                            'disks': {p.relative_to(folder).as_posix(): p.read_bytes()
                                      for p in sorted(folder.rglob('*')) if p.is_file()}}

                window = module.MainWindow()
                window.resize(1400, 1050)
                window.show()
                window.centralWidget().setCurrentIndex(1)

                def idle():
                    application.processEvents()
                    assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
                    assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                    assert window.desktop.process is None and not window.desktop.pending and not errors

                def pure(label, callback, *, display_only=False):
                    before = freeze({'joint': joint(), 'damage_result': window.damage_result})
                    value = callback()
                    idle()
                    after = freeze({'joint': joint(), 'damage_result': window.damage_result})
                    ref = save('actual_UI_step', label=label, display_only=display_only,
                               before=before, after=after)
                    assert_native_equal(after['joint'], before['joint'], label + ' joint purity')
                    if display_only:
                        assert_native_equal(after, before, label + ' complete result/joint purity')
                    return value, ref

                def projection():
                    before = freeze(joint())
                    member = window.run.state['operators'][OP]
                    result = {'held': window.run.held_relic_ids(), 'tools': window.run.held_tool_ids(),
                              'inventory': window.run.inventory_status(),
                              'resources': window.run.calculation_resources(),
                              'recruited': window.recruited_operator_ids(),
                              'overview_ids': [entry[1] for entry in window.operator_choices.entries('__overview__')],
                              'run_metadata': window.current_run_operator_state(),
                              'training': window.current_operator_state(),
                              'rank_selection': window.skill_rank_selection(),
                              'mask': sorted(metadata_mask(member)),
                              'summary': window.run.summary(),
                              'raw_training_text': format_run_training_observation(OP, member),
                              'training_status': window.training_status.text(),
                              'buff_status': window.target_buff_status.text(),
                              'rank_label': window.rank.text(),
                              'rank_explanation': window.skill_cultivation_explanation.text(),
                              'widgets': {'operator': window.operator.currentData(),
                                          'skill': window.skill.currentData(), 'level': window.level.value(),
                                          'frame_timing': window.frame_timing.isChecked(),
                                          'auto_relics': window.auto_relics.isChecked(),
                                          'use_run_training': window.use_run_training.isChecked(),
                                          'manual_account': window.account_skill_reference.isChecked()},
                              'checked_relics': [window.relic_list.item(i).data(Qt.ItemDataRole.UserRole)
                                  for i in range(window.relic_list.count())
                                  if window.relic_list.item(i).checkState() == Qt.CheckState.Checked]}
                    assert_native_equal(joint(), before, 'all public consumer projection purity')
                    return result

                def check_expected(want, caller, result, projected):
                    for key, original in (('skill', 'skill'), ('rank', 'skill_rank'), ('elite', 'elite'), ('level', 'level')):
                        assert type(caller[original]) is int and caller[original] == want[key], (active, original, caller[original], want[key])
                    assert caller['operator'] == OP and caller['trust'] == 0 and caller['potential'] == 1
                    assert caller['module_id'] is None and caller['module_level'] == 0
                    assert caller['enemy_defense'] == 0 and caller['enemy_resistance'] == 0
                    assert sorted(caller['relic_ids']) == sorted(want['held'])
                    assert projected['held'] == sorted(want['held']) and projected['tools'] == sorted(want['tools'])
                    assert sorted(projected['checked_relics']) == sorted(want['held'])
                    assert caller['char_buff_ids'] == want['buffs']
                    assert projected['rank_selection']['source'] == want['rank_source']
                    assert (OP in projected['recruited']) is want['recruited']
                    assert (OP in projected['overview_ids']) is want['recruited']
                    assert ('altar_stacks' in projected['resources']) is want['counter']
                    assert ('altar_stacks' in caller['relic_context']) is want['counter']
                    assert caller['inventory_status'] == projected['inventory']
                    assert projected['widgets']['auto_relics'] is True and projected['widgets']['use_run_training'] is True
                    assert not window.target_buff_test.isChecked() and window.target_enemy.currentData() is None
                    if want.get('unknown'):
                        assert projected['inventory']['complete'] is False
                        assert sorted(projected['inventory']['unconfirmed_item_ids']) == sorted([ATTACK, ALTAR, TOOL])
                        assert '在场状态未确认' in projected['summary'] and '持有状态未确认' in projected['summary']
                        assert '在场标记未确认' in projected['training_status']
                        assert '在场状态未确认' in projected['raw_training_text']
                        assert projected['run_metadata'] == {}
                        assert '已离队' not in projected['summary']
                    if 'origin' in want:
                        assert projected['run_metadata'].get('recruitment_kind') == want['origin']
                    if 'advanced' in want:
                        if want['advanced'] == 'absent':
                            assert 'advanced' not in projected['run_metadata']
                        else:
                            assert projected['run_metadata']['advanced'] is want['advanced']
                    if 'recipient_mask' in want:
                        assert bool(set(projected['mask']).intersection(RECIPIENT_KEYS)) is want['recipient_mask']
                    if 'sp_cost' in want:
                        assert result['estimate']['skill']['sp_cost'] == want['sp_cost']
                    assert_native_equal(window.damage_result['scenario'], caller, 'actual GUI caller')

                def snapshot(case, want, mode):
                    active.update(case=case + '-' + mode, phase='ordinary_configuration')
                    pure('actual manual catalog operator preview', lambda: window.operator_choices.select_value(OP))
                    index = window.skill.findData(want['skill'])
                    assert index >= 0
                    pure('actual available skill', lambda: window.skill.setCurrentIndex(index))
                    pure('actual timing mode', lambda: window.frame_timing.setChecked(mode == 'frames'))
                    pure('actual public zero-motion timing', lambda: window.timing_scenario.setPlainText(json.dumps({'windup_frames': 0, 'recovery_frames': 0})))
                    active['phase'] = 'explicit_snapshot'
                    start = len(calls)
                    _, ui_ref = pure('MainWindow.calculate', window.calculate)
                    assert len(calls) == start + 1 and calls[-1]['error'] is None and window.damage_result is not None
                    call = calls[-1]
                    assert window.damage_result['result'] is call['return_value']
                    caller, result = window.damage_result['scenario'], window.damage_result['result']
                    projected = projection()
                    check_expected(want, caller, result, projected)
                    assert caller['timing_mode'] == mode and caller['window_seconds'] == 10.0
                    assert caller['timing'] == {'windup_frames': 0, 'recovery_frames': 0}
                    assert caller['continuous_attacks'] is True
                    assert 'base_attack' not in caller and 'target_enemy' not in caller
                    # Whole caller/joint graph is cloned once before a fresh actual API call.
                    reference_context = freeze(call['after'])
                    reference_before = freeze(reference_context)
                    reference_result = calculator(*reference_context['args'], **reference_context['kwargs'])
                    assert_native_equal(reference_context, reference_before, 'fresh complete API reference caller purity')
                    reference_ref = save('actual_fresh_API_reference', before=reference_before,
                        after={**reference_context, 'result': reference_result})
                    assert_native_equal({'args': reference_context['args'], 'kwargs': reference_context['kwargs'],
                        'joint': reference_context['joint'], 'result': reference_result},
                        {**call['after'], 'result': result}, 'complete original caller/result/joint versus fresh API')
                    before = freeze({'damage_result': window.damage_result, 'joint': joint()})
                    texts = {'estimate': estimate.format_estimate(result),
                             'default': reporting.format_report(result),
                             'technical': reporting.format_report(result, technical=True)}
                    after = freeze({'damage_result': window.damage_result, 'joint': joint()})
                    formatter_ref = save('actual_three_formatter_group', before=before, after=after, texts=texts)
                    assert_native_equal(after, before, 'three complete formatter joint purity')
                    assert texts['estimate'] == texts['default']
                    assert window.damage_text.toPlainText() == texts['default'].replace(chr(160), ' ')
                    _, technical_ref = pure('actual technical report checkbox', lambda: window.damage_technical.setChecked(True), display_only=True)
                    assert window.damage_text.toPlainText() == texts['technical'].replace(chr(160), ' ')
                    _, ordinary_ref = pure('actual ordinary report checkbox', lambda: window.damage_technical.setChecked(False), display_only=True)
                    assert window.damage_text.toPlainText() == texts['default'].replace(chr(160), ' ')
                    value = {'caller': window.damage_result['scenario'], 'damage_result': window.damage_result,
                             'texts': texts, 'displayed_damage': window.damage_text.toPlainText(),
                             'state_and_disks': joint(), 'projection': projected}
                    ref = save('actual_window_snapshot', value=value, expected=want, mode=mode)
                    row = {'id': identity + ':' + case + ':' + mode, 'context': identity,
                           'stage': case, 'mode': mode, 'expected': want, 'numeric': call['native'],
                           'ui_step': ui_ref, 'reference': reference_ref, 'formatter': formatter_ref,
                           'technical_step': technical_ref, 'ordinary_step': ordinary_ref, 'snapshot': ref}
                    rows.append(row)
                    checkpoint()
                    return row

                def ingress(stage):
                    active.update(case=stage['id'], phase='explicit_public_ingress')
                    caller = {'observed': freeze(stage['observed']), 'captured_at': stage['at']}
                    caller_before, before = freeze(caller), freeze(joint())
                    begin = save('actual_ingress_begin', caller=caller_before, before=before)
                    value = window.apply_run_observation(caller['observed'], caller['captured_at'])
                    # No UI setter, event pump or projection read is inside the narrow bracket.
                    after, caller_after = freeze(joint()), freeze(caller)
                    end = save('actual_ingress_end', begin_ref=begin, caller_before=caller_before,
                               caller_after=caller_after, before=before, after=after, return_value=value)
                    assert value is True
                    assert_native_equal(caller_after, caller_before, 'explicit public ingress caller purity')
                    assert_native_equal(after['account'], before['account'], 'explicit ingress account memory purity')
                    assert before['disks']['account.json'] == after['disks']['account.json'] == account_raw
                    assert set(after['disks']) == set(before['disks']) == {'account.json', 'run.json'}
                    saved_text = json.dumps(after['run'], ensure_ascii=False, indent=2)
                    saved_text = saved_text.encode('utf-8', errors='backslashreplace').decode('utf-8')
                    assert after['disks']['run.json'] == saved_text.replace('\n', os.linesep).encode('utf-8'), 'actual ingress exact serialized run bytes, without JSON alias claim'
                    assert window.run.save_issue is None and not window.run.preserve_unreadable
                    ingresses.append({'context': identity, 'id': stage['id'], 'begin': begin, 'end': end})
                    checkpoint()
                    active['phase'] = 'ordinary_after_ingress'
                    idle()
                    return before, after

                def summary_png(row):
                    active.update(case=row['snapshot']['case'], phase='bounded_summary_PNG')
                    pure('show actual unknown run summary', lambda: window.centralWidget().setCurrentIndex(0), display_only=True)
                    label = window.run_summary
                    viewport = window.centralWidget().rect()
                    top_left = label.mapTo(window.centralWidget(), label.rect().topLeft())
                    rectangle = label.rect().translated(top_left)
                    assert label.isVisible() and viewport.contains(rectangle)
                    assert '在场状态未确认' in label.text() and '持有状态未确认' in label.text()
                    visual = save('actual_PNG_bounded_unknown_summary', snapshot_ref=row['snapshot'],
                                  joint=joint(), damage_result=window.damage_result,
                                  displayed_text=label.text(), label_rect=(rectangle.x(), rectangle.y(), rectangle.width(), rectangle.height()),
                                  viewport_rect=(viewport.x(), viewport.y(), viewport.width(), viewport.height()))
                    path = out / 'unknown-retained-summary.png'
                    assert window.grab().save(str(path), 'PNG')
                    pngs.append({'path': path.name, 'bytes': path.stat().st_size,
                                 'sha256': sha(path.read_bytes()), 'visual': visual, 'snapshot': row['snapshot']})
                    checkpoint()
                    pure('return actual damage report tab', lambda: window.centralWidget().setCurrentIndex(1), display_only=True)

                def report_png(row):
                    active.update(case=row['snapshot']['case'], phase='bounded_report_PNG')
                    block = next(section for section in window.damage_result['result']['report']['sections'] if section['id'] == 'damage')
                    title = '【' + block['title'] + '】'
                    document = window.damage_text.document()
                    first = document.find(title)
                    assert not first.isNull() and block['metrics']
                    search = QTextCursor(first)
                    search.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    cursors = []
                    for index, metric in enumerate(block['metrics']):
                        prefix = visible_metric_label(metric['label']) + '：'
                        found = document.find(prefix, search)
                        assert not found.isNull() and found.blockNumber() == first.blockNumber() + index + 1
                        assert found.block().text().startswith(prefix)
                        cursors.append(found)
                        search = QTextCursor(found)
                        search.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                    middle, last = cursors[len(cursors) // 2], cursors[-1]
                    pure('center bounded fresh-Snack damage metrics', lambda: (window.damage_text.setTextCursor(middle), window.damage_text.centerCursor()), display_only=True)
                    cursor = QTextCursor(first)
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    blocks, rectangles = [], []
                    while cursor.blockNumber() <= last.blockNumber():
                        assert len(blocks) < 20
                        end = QTextCursor(cursor)
                        end.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                        blocks.append(cursor.block().text())
                        rectangles.extend((window.damage_text.cursorRect(cursor), window.damage_text.cursorRect(end)))
                        if cursor.blockNumber() == last.blockNumber():
                            break
                        assert cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
                    viewport = window.damage_text.viewport().rect()
                    assert window.damage_text.isVisible() and all(viewport.contains(rect) for rect in rectangles)
                    visual = save('actual_PNG_bounded_fresh_Snack_report', snapshot_ref=row['snapshot'],
                                  joint=joint(), damage_result=window.damage_result, section=block['id'], title=title,
                                  displayed_text=window.damage_text.toPlainText(), visible_blocks=blocks,
                                  cursor_rects=[(r.x(), r.y(), r.width(), r.height()) for r in rectangles],
                                  viewport_rect=(viewport.x(), viewport.y(), viewport.width(), viewport.height()))
                    path = out / 'fresh-Snack-damage-report.png'
                    assert window.grab().save(str(path), 'PNG')
                    pngs.append({'path': path.name, 'bytes': path.stat().st_size,
                                 'sha256': sha(path.read_bytes()), 'visual': visual, 'snapshot': row['snapshot']})
                    checkpoint()

                idle()
                assert not window.run.preserve_unreadable and window.run.save_issue is None
                assert not window.account_cache.issues and window.account_cache.load_issue is None
                assert run_path.read_bytes() == run_raw and account_path.read_bytes() == account_raw
                initial = save('actual_public_fixture_loaded', run_bytes=run_raw, account_bytes=account_raw, value=joint(),
                               initial_ui={'selected_catalog_operator': window.operator.currentData(),
                                           'recruited': window.recruited_operator_ids(),
                                           'overview_ids': [entry[1] for entry in window.operator_choices.entries('__overview__')]})
                active['phase'] = 'ordinary_configuration'
                pure('use public run cultivation', lambda: window.use_run_training.setChecked(True))
                pure('use actual automatically qualified holdings', lambda: window.auto_relics.setChecked(True))
                pure('synchronize only actually held relics', window.sync_run_relics)
                pure('use bounded observation interval', lambda: window.limit_window.setChecked(True))
                pure('ten second observation interval', lambda: window.window_seconds.setValue(10))
                pure('zero manual enemy defense', lambda: window.defense.setValue(0))
                pure('zero manual enemy resistance', lambda: window.resistance.setValue(0))
                pure('continuous normal attacks', lambda: window.continuous_attacks.setChecked(True))
                pure('ordinary report', lambda: window.raw_damage.setChecked(False))
                pure('hide technical expansion', lambda: window.damage_technical.setChecked(False))
                assert window.target_enemy.currentData() is None and not window.target_buff_test.isChecked()
                initial_rows = [snapshot('initial', context_case['initial'], mode) for mode in specs['modes']]
                if identity == 'unknown_string':
                    summary_png(initial_rows[-1])
                    manual = {**context_case['initial'], 'rank_source': 'manual_account_reference'}
                    pure('explicit initial account skill reference', lambda: window.account_skill_reference.setChecked(True))
                    snapshot('initial_manual_account', manual, 'frames')
                    pure('cancel initial account skill reference', lambda: window.account_skill_reference.setChecked(False))
                    snapshot('initial_manual_cancel', context_case['initial'], 'frames')
                    original_member = freeze(window.run.state['operators'][OP])
                    old_proof = freeze(window.run.state['resources']['altar_stacks'])
                    for stage in specs['string_ingress']:
                        _, changed = ingress(stage)
                        member = changed['run']['operators'][OP]
                        if stage['id'] == 'identity_only':
                            for key in ('fields', 'skill_ranks', 'char_buff_ids', 'char_buff_absent_ids', 'char_buffs_complete', 'recruitment_kind', 'advanced'):
                                assert_native_equal(member[key], original_member[key], 'identity-only original raw ' + key)
                            history = [event for event in changed['run']['history'] if event['kind'] == 'state_flag_reconfirmed' and event['record_kind'] == 'operator']
                            assert len(history) == 1
                            assert_native_equal(history[0]['previous_record'], original_member, 'full original raw member qualification receipt')
                        if stage['id'] != 'fresh_counter' and stage['at'] < 2010:
                            assert_native_equal(changed['run']['resources']['altar_stacks'], old_proof, 'original proof retained until its own fresh read')
                        assert not set(event['kind'] for event in changed['run']['history']).intersection(('recruitment_changed', 'classification_corrected', 'char_buff_absence_invalidated', 'relic_confirmed', 'tool_confirmed'))
                        stage_rows = [snapshot(stage['id'], stage['expected'], mode) for mode in specs['modes']]
                        if stage['id'] == 'identity_only':
                            manual = {**stage['expected'], 'rank': 3, 'rank_source': 'manual_account_reference'}
                            manual.pop('sp_cost')
                            pure('explicit account rank while old run ranks masked', lambda: window.account_skill_reference.setChecked(True))
                            snapshot('identity_manual_account', manual, 'frames')
                            pure('cancel account rank without requalifying old run ranks', lambda: window.account_skill_reference.setChecked(False))
                            snapshot('identity_manual_cancel', stage['expected'], 'frames')
                        if stage['id'] == 'popup_A':
                            report_png(stage_rows[-1])
                elif identity == 'unknown_number':
                    before, changed = ingress(specs['number_ingress'][0])
                    assert changed['run']['operators'][OP]['present'] is False
                    assert all(record['held'] is False for record in [*changed['run']['relics'].values(), *changed['run']['tactical_tools'].values()])
                    events = [event for event in changed['run']['history'] if event['kind'] == 'state_flag_reconfirmed']
                    assert len(events) == 4 and all(event['value'] is False for event in events)
                    assert not set(event['kind'] for event in changed['run']['history']).intersection(('operator_no_longer_present', 'relic_no_longer_held', 'tool_no_longer_held'))
                    assert_native_equal(changed['run']['resources'], before['run']['resources'], 'negative qualification retains counter proof')
                    for mode in specs['modes']:
                        snapshot('zero_inventory_and_crew', specs['number_ingress'][0]['expected'], mode)
                active.update(case='close', phase='close_direct_reload')
                live_before = freeze(joint())
                window.close()
                application.processEvents()
                assert_native_equal(joint(), live_before, 'real MainWindow close purity')
                restarted = RunState(run_path)
                assert not restarted.preserve_unreadable and restarted.save_issue is None
                # Persisted JSON deliberately has no live history/member alias.
                # All original keys are present in constructor order in these
                # public fixtures; unknown extras retain their trailing order.
                expected_restart = json.loads(run_path.read_bytes())
                expected_restart['notice'] = specs['restore_notice']
                assert_native_equal(restarted.state, expected_restart, 'reload full run with only documented notice transition')
                assert_native_equal(joint(), live_before, 'direct run reload disk purity')
                account_restarted = AccountCache(account_path, profiles=operator_profiles(), implemented_ids=catalog()['operators'])
                assert not account_restarted.issues and account_restarted.load_issue is None and not account_restarted.preserve_original
                assert_native_equal(account_restarted.records, live_before['account'], 'direct complete account reload')
                assert_native_equal(joint(), live_before, 'direct account reload disk purity')
                close = save('actual_close_RunState_account_reload', live_before=live_before,
                             persisted_json=json.loads(run_path.read_bytes()), restart_state=restarted.state,
                             account_restart_records=account_restarted.records, disks_after=joint()['disks'])
                contexts.append({'id': identity, 'initial': initial, 'close': close})
                checkpoint()
                window.deleteLater()
                application.processEvents()
                window = None
        assert len(rows) == specs['expected_rows'] and len(pngs) == specs['expected_pngs']
        assert len(contexts) == specs['expected_contexts'] and len(ingresses) == 13 and not errors
        receipt.update(passed=True, workflow_complete=True, actual_windows=6)
    except BaseException as error:
        receipt['failure'] = error_record(error)
    finally:
        if window is not None:
            window.close()
        if module is not None:
            if backend is not None:
                module.DesktopBackend = backend
            if calculator is not None:
                module.calculate_damage = calculator
            if original_paths is not None:
                module.RUN_STATE, module.OPERATOR_STATE, module.SETTINGS = original_paths
        sys.excepthook = old_hook
        receipt['actual_numeric_calls'] = len(calls)
        receipt['source_after'] = source_map(root)
        receipt['source_additional_after'] = {name: sha((root / name).read_bytes()) for name in extra}
        receipt['source_drift'] = [p for p in set(expected) | set(receipt['source_after']) if expected.get(p) != receipt['source_after'].get(p)]
        if receipt['source_drift'] or receipt['source_additional_after'] != extra or guard_path.read_bytes() != guard_raw or errors:
            receipt.update(passed=False, workflow_complete=False)
        if time.perf_counter() - started >= DEADLINE:
            receipt.update(passed=False, workflow_complete=False)
        receipt['elapsed_seconds'] = time.perf_counter() - started
        fsync_json(out / 'receipt.json', receipt, exclusive=True)
        done.set()
    print(json.dumps({'passed': receipt['passed'], 'rows': len(rows), 'contexts': len(contexts), 'pngs': len(pngs)}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
