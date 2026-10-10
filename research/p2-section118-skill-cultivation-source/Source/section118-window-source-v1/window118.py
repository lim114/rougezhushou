"""Unexecuted Source: Root alone runs the bounded skill-source MainWindows."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import traceback

from native_evidence import freeze, assert_native_equal, write_record, source_map

SU = 'char_298_susuro'
AM = 'char_002_amiya'
DEPARTED = 'char_196_sunbr'
NO_SKILL = 'char_285_medic2'
PATCHES = ('char_1001_amiya2', 'char_1037_amiya3')
HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
BUFF = 'rogue_6_from_relic_9'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error),
            'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))}


def profile(op, elite, ranks, *, level=40, selected=1):
    return {'id': op, 'scope': 'operator_profile',
            'fields': {'elite': elite, 'level': level, 'trust': 0, 'potential': 1,
                       'module_id': None, 'module_level': 0, 'selected_skill': selected},
            'skill_ranks': {str(k): v for k, v in ranks.items()}, 'captured_at': 1000.0,
            'sources': {}, 'field_times': {}, 'skill_times': {}}


def member(op, elite, ranks, *, level=40, present=True, invalid=()):
    value = profile(op, elite, ranks, level=level)
    value.update(scope='run', present=present, recruitment_kind='non_emergency',
                 char_buff_ids=[BUFF] if op == SU else [], char_buffs_complete=True,
                 char_buff_absent_ids=[], char_buff_pending_ids=[], invalid_fields=[],
                 invalid_skill_ranks=list(invalid), missing_fields=[])
    return value


def fixture(context):
    if context == 'core':
        members = {SU: member(SU, 1, {1: 5, 2: 4}), AM: member(AM, 1, {1: 2, 2: 4}),
                   DEPARTED: member(DEPARTED, 1, {1: 4}, present=False),
                   NO_SKILL: member(NO_SKILL, 0, {}, level=1)}
        accounts = {SU: profile(SU, 1, {1: 3, 2: 7}), AM: profile(AM, 1, {1: 6, 2: 7}),
                    DEPARTED: profile(DEPARTED, 1, {1: 7}), NO_SKILL: profile(NO_SKILL, 0, {}, level=1)}
        for op in PATCHES:
            members[op] = member(op, 2, {1: 10, 2: 10}, level=1)
            accounts[op] = profile(op, 2, {1: 10, 2: 10}, level=1)
    else:
        elite = 2 if context == 'I' else 0 if context == 'J' else 1
        rank = 7 if context == 'I' else 5 if context in ('J', 'K', 'unsafe') else 3
        members = {SU: member(SU, elite, {1: rank}, level=1 if elite == 0 else 40,
                              invalid=('1',) if context == 'K' else ())}
        account_elite = 2 if context in ('H', 'I') else 1
        accounts = {SU: profile(SU, account_elite, {1: 10 if context == 'I' else
                                                  3 if context in ('K', 'unsafe') else 7})}
        if context == 'unsafe':
            members[SU]['fields']['elite'] = []  # Public raw unsafe fixture, never a real game claim.
    run = {'id': 'public118-' + context, 'started_at': 0.0, 'last_read': 1000.0,
           'operators': members, 'crew_count': sum(v.get('present', True) for v in members.values()),
           'selected_operator': SU, 'relics': {}, 'tactical_tools': {}, 'relic_count': 0,
           'inventory_verified': True, 'inventory_confirmed_at': 1000.0, 'bar_signature': [],
           'relic_icon_memory': None, 'history': [], 'resources': {}, 'config': {}, 'maps': {},
           'last_node_content': None, 'node_contents': [],
           'public_opaque': {'signed_zero': -0.0, 'nullable': None}}
    return run, accounts


def main():
    parser = argparse.ArgumentParser()
    for key in ('root', 'guard', 'out'):
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--source-count', type=int, required=True)
    parser.add_argument('--section', type=int, required=True)
    parser.add_argument('--deadline', type=int, default=900)
    args = parser.parse_args()
    root, out = Path(args.root).resolve(), Path(args.out).resolve()
    artifact, guard_path = Path(__file__).resolve().parent, Path(args.guard).resolve()
    assert args.section == 118 and 1 <= args.deadline <= 1200
    assert not out.exists() and root not in out.parents and out != root
    assert artifact != root and root not in artifact.parents
    assert sha((artifact / 'native_evidence.py').read_bytes()) == HELPER_SHA
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    expected, extra = guard['source_sha256'], guard['source_additional_sha256']
    assert guard['section'] == args.section and len(expected) == args.source_count
    assert source_map(root) == expected and set(extra) == {'CORE_0.70_VERIFICATION.json'}
    for name, want in extra.items():
        assert sha((root / name).read_bytes()) == want
    original_raw = (root / 'rouge/data/skill-cultivation-reference.json').read_bytes()
    assert sha(original_raw) == expected['rouge/data/skill-cultivation-reference.json']
    original_data = json.loads(original_raw)
    out.mkdir()
    (out / 'records').mkdir()
    (out / 'public-state').mkdir()
    rows, records, pngs, calls, reference_calls, errors, pairs, reloads = [], [], [], [], [], [], [], []
    active = {'context': 'bootstrap', 'case': 'constructor', 'phase': 'prepare'}
    started, done = time.perf_counter(), threading.Event()
    window = module = backend = calculator = old_paths = None
    receipt = {'kind': 'ROOT_ACTUAL_118_REAL_MAINWINDOW', 'section': args.section,
               'passed': False, 'workflow_complete': False,
               'runner_sha256': sha(Path(__file__).read_bytes()), 'native_helper_sha256': HELPER_SHA,
               'source_guard_sha256': sha(guard_raw), 'source_before': expected,
               'source_additional_before': extra, 'source_count': args.source_count,
               'reference_data_sha256': sha(original_raw), 'rows': rows, 'records': records,
               'pairs': pairs, 'close_reloads': reloads, 'pngs': pngs, 'Qt_errors': errors,
               'deadline_seconds': args.deadline, 'private_state_access': False,
               'native_windows_verified': False, 'game_chat_sampling_executed': False,
               'fixture_scope': 'Only explicitly synthetic public fixtures. Core D and H use real public observation ingress; core L uses the real user reset button method. Those intentional changes are recorded separately from all pure controls.',
               'formatter_scope': 'Three complete formatter group purity and actual technical-checkbox views; no per-formatter isolated purity claim.',
               'numeric_scope': 'Every actual numeric snapshot matched to a fresh original calculate_damage call with its complete GUI-emitted caller. This proves the selected read rank drives existing numerical code, not native game E0 use.',
               'PNG_scope': 'Two actual form captures: explicit account rank choice and E0 choice. Only checkbox and the measured intersected explanation rectangle are claimed visible; complete long text is saved native, not automatically claimed fully on screen.',
               'restart_scope': 'Each real window closes and independent RunState/AccountCache reloads compare complete graphs and public disk bytes. The existing RunState constructor notice-only presentation transition is explicit; no other leaf, type, order or alias delta is admitted. Preference remains UI-local.'}

    def save(kind, **value):
        ref = write_record(out / 'records', len(records) + 1, {'kind': kind, **active, **value})
        ref.update(kind=kind, **active)
        records.append(ref)
        return ref

    def checkpoint():
        with (out / 'checkpoint.json').open('w', encoding='utf-8') as stream:
            stream.write(json.dumps({'completed_case_ids': [r['id'] for r in rows], 'active': active,
                                     'source_guard_sha256': sha(guard_raw)}, ensure_ascii=False))
            stream.flush()
            os.fsync(stream.fileno())

    def watchdog():
        if not done.wait(args.deadline):
            (out / 'timeout.json').write_text(json.dumps({'passed': False, 'active': active,
                                                          'deadline_seconds': args.deadline}))
            os._exit(124)

    threading.Thread(target=watchdog, daemon=True).start()
    old_hook = sys.excepthook

    def hook(kind, value, tb):
        errors.append({'case': active['case'], 'phase': active['phase'],
                       'type': kind.__name__, 'message': str(value)})
        old_hook(kind, value, tb)

    sys.excepthook = hook
    try:
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(root))
        from PySide6.QtCore import qVersion, QPoint
        from PySide6.QtWidgets import QApplication, QScrollArea
        from rouge import app as module, estimate, reporting
        from rouge.run_state import RunState
        from rouge.account_cache import AccountCache
        from rouge.catalog import catalog, operator_profiles
        application = QApplication.instance() or QApplication([])
        backend, calculator = module.DesktopBackend, module.calculate_damage
        old_paths = module.RUN_STATE, module.OPERATOR_STATE, module.SETTINGS
        receipt.update(python=sys.version, qt=qVersion())
        assert BUFF in json.loads((root / 'rouge/data/relic-mechanics.json').read_bytes())['char_buffs']

        def observed(*positional, **keywords):
            before = freeze({'args': positional, 'kwargs': keywords,
                             **({'joint': joint()} if window is not None else {})})
            try:
                value = calculator(*positional, **keywords)
            except Exception as error:
                details = error_record(error)
                after = {'args': positional, 'kwargs': keywords,
                         **({'joint': joint()} if window is not None else {})}
                ref = save('actual_calculate_exception', before=before, after=after, error=details)
                calls.append({'caller': before, 'error': details, 'native': ref})
                assert_native_equal(after, before, 'exception caller purity')
                raise
            after = {'args': positional, 'kwargs': keywords,
                     **({'joint': joint()} if window is not None else {})}
            ref = save('actual_calculate_result', before=before, after=after, result=value)
            calls.append({'caller': before, 'error': None, 'native': ref, 'return_value': value})
            assert_native_equal(after, before, 'numeric caller purity')
            return value

        module.calculate_damage = observed
        for context in ('core', 'H', 'I', 'J', 'K', 'unsafe'):
            active.update(context=context, case=context + '-constructor', phase='public_fixture_setup')
            with tempfile.TemporaryDirectory(prefix='public118-' + context + '-', dir=out / 'public-state') as directory:
                folder = Path(directory)
                run_path, account_path = folder / 'run.json', folder / 'account.json'
                run_fixture, account_fixture = fixture(context)
                run_raw = (json.dumps(run_fixture, ensure_ascii=False, indent=2) + '\n').encode()
                account_raw = (json.dumps(account_fixture, ensure_ascii=False, indent=2) + '\n').encode()
                run_path.write_bytes(run_raw)
                account_path.write_bytes(account_raw)
                module.RUN_STATE, module.OPERATOR_STATE, module.SETTINGS = run_path, account_path, folder / 'settings.json'
                module.DesktopBackend = lambda _path, callback: backend(folder / 'chat', callback)

                def joint():
                    return {'run': window.run.state, 'account': window.account_cache.records, 'disks': {
                        p.relative_to(folder).as_posix(): p.read_bytes()
                        for p in sorted(folder.rglob('*')) if p.is_file()}}

                window = module.MainWindow()
                window.resize(1500, 1100)
                window.show()
                window.centralWidget().setCurrentIndex(1)

                def idle():
                    application.processEvents()
                    assert window.isVisible() and not window.auto.isChecked() and not window.timer.isActive()
                    assert not window.busy and not window.chat_busy and not window.desktop_request_busy
                    assert window.desktop.process is None and not window.desktop.pending and not errors

                def pure(label, callback):
                    before = freeze({'joint': joint(), 'damage_result': window.damage_result})
                    value = callback()
                    idle()
                    after = freeze({'joint': joint(), 'damage_result': window.damage_result})
                    save('actual_UI_step', label=label, before=before, after=after)
                    assert_native_equal(after['joint'], before['joint'], label + ' state/account/disks')
                    return value

                def select(op, skill=1, mode='frames'):
                    assert pure('actual operator branch selection', lambda: window.operator_choices.select_value(op))
                    if skill is not None:
                        index = window.skill.findData(skill)
                        assert index >= 0
                        pure('actual skill choice', lambda: window.skill.setCurrentIndex(index))
                    pure('actual timing checkbox', lambda: window.frame_timing.setChecked(mode == 'frames'))
                    assert window.operator.currentData() == op

                def snapshot(identity, rank, source, *, manual=False, no_numeric=False, expected_elite=None):
                    active.update(case=identity, phase='actual_snapshot')
                    start = len(calls)
                    pure('MainWindow.calculate', window.calculate)
                    if no_numeric:
                        assert len(calls) == start and window.damage_result is None
                        assert window.skill_cultivation_row is None
                        assert not window.account_skill_reference.isEnabled()
                        assert not window.damage_form.isRowVisible(window.skill_cultivation_explanation)
                        ref = save('actual_non_numeric_window_snapshot', joint=joint(),
                                   display=window.damage_text.toPlainText(), rank_text=window.rank.text(),
                                   operator=window.operator.currentData(), skill=window.skill.currentData())
                        rows.append({'id': identity, 'numeric': None, 'snapshot': ref})
                        checkpoint()
                        return {'snapshot': ref}
                    assert len(calls) == start + 1 and calls[-1]['error'] is None and window.damage_result is not None
                    call = calls[-1]
                    caller, result = call['caller']['args'][0], window.damage_result['result']
                    assert result is call['return_value']
                    assert caller['skill_rank'] == rank and caller['operator'] == window.operator.currentData()
                    assert caller['skill'] == window.skill.currentData()
                    assert caller['timing_mode'] == ('frames' if window.frame_timing.isChecked() else 'continuous')
                    assert 'base_attack' not in caller and 'target_enemy' not in caller
                    assert caller['window_seconds'] == 10 and caller['trust'] == 0 and caller['potential'] == 1
                    assert caller['module_id'] is None and caller['module_level'] == 0 and caller['relic_ids'] == []
                    if expected_elite is not None:
                        assert caller['elite'] == expected_elite
                    assert_native_equal(window.damage_result['scenario'], caller, 'actual complete GUI caller')
                    row = window.skill_cultivation_row
                    assert row['rank'] == rank and row['rank_source'] == source
                    assert row['manual_reference_applied'] is manual
                    assert row['arithmetic_changed_by_explanation'] is False
                    assert window.account_skill_reference.isChecked() is manual
                    assert ('已选账号参考' in str(caller['unconfirmed_training'])) is manual
                    assert window.damage_form.isRowVisible(window.skill_cultivation_explanation)
                    if manual:
                        assert '局外模拟' in window.rank.text() and '本局未确认' in window.skill_cultivation_explanation.text()
                    else:
                        assert window.rank.text() == (f'等级 {rank}' if rank <= 7 else f'专精 {rank - 7}') + (
                            '（未确认，档案预览）' if source == 'preview_unconfirmed' else '（读取）')
                    if row['operator'] in PATCHES:
                        assert row['original_source_status'] == 'missing' and row['training_requirement'] is None
                    else:
                        raw = original_data['operators'][row['operator']]
                        assert row['original_source_status'] == 'located'
                        if 2 <= rank <= 7:
                            assert_native_equal(row['training_requirement']['raw'], raw['allSkillLvlup'][rank - 2]['unlockCond'], 'physical common-training source')
                        elif rank >= 8:
                            assert_native_equal(row['training_requirement']['raw'], raw['skills'][caller['skill'] - 1]['levelUpCostCond'][rank - 8]['unlockCond'], 'physical mastery source')
                    if caller['elite'] == 0 and 5 <= rank <= 7:
                        assert row['e0_common_use_verified'] is None and '仍未核验' in window.skill_cultivation_explanation.text()
                    if caller['operator'] == SU and caller['recruitment_kind'] is not None:
                        assert caller['recruitment_kind'] == 'non_emergency' and caller['char_buff_ids'] == [BUFF]
                    reference_caller = freeze(caller)
                    reference_before = freeze({'caller': reference_caller, 'joint': joint()})
                    expected_result = calculator(reference_caller)
                    reference_after = freeze({'caller': reference_caller, 'joint': joint()})
                    assert_native_equal(reference_after, reference_before, 'fresh same complete caller purity')
                    assert_native_equal(result, expected_result, 'complete actual GUI result equals fresh original API caller')
                    reference_ref = save('actual_reference_API_before_after_result', before=reference_before,
                                         after=reference_after, result=expected_result)
                    reference_calls.append(reference_ref)
                    before = freeze({'damage_result': window.damage_result, 'joint': joint()})
                    texts = {'estimate': estimate.format_estimate(result), 'default': reporting.format_report(result),
                             'technical': reporting.format_report(result, technical=True)}
                    after = freeze({'damage_result': window.damage_result, 'joint': joint()})
                    assert_native_equal(after, before, 'three formatter group purity')
                    save('actual_three_formatter_group', before=before, after=after, texts=texts)
                    assert texts['estimate'] == texts['default']
                    assert window.damage_text.toPlainText() == texts['default'].replace(chr(160), ' ')
                    pure('actual technical checkbox', lambda: window.damage_technical.setChecked(True))
                    assert window.damage_text.toPlainText() == texts['technical'].replace(chr(160), ' ')
                    pure('ordinary report restore', lambda: window.damage_technical.setChecked(False))
                    assert window.damage_text.toPlainText() == texts['default'].replace(chr(160), ' ')
                    assert_native_equal(freeze({'damage_result': window.damage_result, 'joint': joint()}), before, 'both report views preserve complete graph/state')
                    value = freeze({'caller': caller, 'damage_result': window.damage_result, 'texts': texts,
                                    'state_and_disks': joint(), 'selection_row': row,
                                    'rank_label': window.rank.text(), 'explanation_text': window.skill_cultivation_explanation.text(),
                                    'checkbox_checked': window.account_skill_reference.isChecked(),
                                    'checkbox_enabled': window.account_skill_reference.isEnabled()})
                    ref = save('actual_window_snapshot', value=value)
                    rows.append({'id': identity, 'operator': caller['operator'], 'skill': caller['skill'],
                                 'mode': caller['timing_mode'], 'rank': rank, 'rank_source': source,
                                 'snapshot': ref, 'numeric': call['native'], 'reference_numeric': reference_ref})
                    checkpoint()
                    return {'snapshot': ref, 'value': value}

                def capture(identity):
                    parent = window.account_skill_reference.parentWidget()
                    while parent is not None and not isinstance(parent, QScrollArea):
                        parent = parent.parentWidget()
                    assert parent is not None
                    pure('show source checkbox viewport', lambda: parent.ensureWidgetVisible(window.account_skill_reference))
                    viewport = parent.viewport().rect()
                    rects = {}
                    for name, widget in (('checkbox', window.account_skill_reference), ('explanation', window.skill_cultivation_explanation), ('rank', window.rank)):
                        point = widget.mapTo(parent.viewport(), QPoint(0, 0))
                        rect = widget.rect().translated(point)
                        intersection = rect.intersected(viewport)
                        rects[name] = {'rect': (rect.x(), rect.y(), rect.width(), rect.height()),
                                       'intersection': (intersection.x(), intersection.y(), intersection.width(), intersection.height()),
                                       'entire_widget_visible': viewport.contains(rect)}
                    assert rects['checkbox']['entire_widget_visible']
                    assert rects['explanation']['intersection'][2] > 0 and rects['explanation']['intersection'][3] > 0
                    visual = save('actual_PNG_source_form_scope', widget_rectangles=rects,
                                  viewport=(viewport.x(), viewport.y(), viewport.width(), viewport.height()),
                                  entire_explanation_claimed_visible=False, text=window.skill_cultivation_explanation.text(),
                                  rank_label=window.rank.text(), checked=window.account_skill_reference.isChecked())
                    path = out / (identity + '.png')
                    assert window.grab().save(str(path), 'PNG')
                    pngs.append({'path': path.name, 'bytes': path.stat().st_size, 'sha256': sha(path.read_bytes()), 'visual': visual})

                def reference_pair(before, selected):
                    original = before['value']['caller']
                    expected_caller = freeze(original)
                    expected_caller['skill_rank'] = selected['value']['caller']['skill_rank']
                    unconfirmed = original['unconfirmed_training']
                    expected_caller['unconfirmed_training'] = [
                        *[label for label in unconfirmed if label != '所选技能等级'],
                        '所选技能等级（已选账号参考，局外模拟）']
                    # The GUI puts the new rank label before later actual
                    # account/unconfirmed fields. Keep that physical order.
                    if '所选技能等级' in unconfirmed:
                        index = unconfirmed.index('所选技能等级')
                        expected_caller['unconfirmed_training'] = list(unconfirmed)
                        expected_caller['unconfirmed_training'][index] = '所选技能等级（已选账号参考，局外模拟）'
                    else:
                        fields = window.current_operator_state().get('fields', {})
                        prefix = [label for key, label in [('elite', '精英阶段'), ('trust', '信赖'),
                                                          ('potential', '潜能'), ('module_id', '模组'),
                                                          ('module_level', '模组阶段')] if key not in fields]
                        expected_caller['unconfirmed_training'] = [*unconfirmed[:len(prefix)],
                            '所选技能等级（已选账号参考，局外模拟）', *unconfirmed[len(prefix):]]
                    assert_native_equal(selected['value']['caller'], expected_caller,
                                        'reference changes only selected rank and its explicit unconfirmed label')
                    assert_native_equal(selected['value']['state_and_disks'], before['value']['state_and_disks'],
                                        'reference pair retains every public state/disk leaf')

                idle()
                assert not window.run.preserve_unreadable and window.run.save_issue is None
                assert not window.account_cache.issues and not window.account_cache.preserve_original
                assert run_path.read_bytes() == run_raw and account_path.read_bytes() == account_raw
                save('actual_public_fixture_loaded', run_bytes=run_raw, account_bytes=account_raw, value=joint())
                for label, callback in (
                    ('manual no-relic inventory', lambda: window.auto_relics.setChecked(False)),
                    ('actual run training', lambda: window.use_run_training.setChecked(True)),
                    ('bounded observation', lambda: window.limit_window.setChecked(True)),
                    ('ten second observation', lambda: window.window_seconds.setValue(10)),
                    ('manual zero defense', lambda: window.defense.setValue(0)),
                    ('manual zero resistance', lambda: window.resistance.setValue(0)),
                    ('continuous attacks', lambda: window.continuous_attacks.setChecked(True)),
                    ('ordinary view', lambda: window.raw_damage.setChecked(False)),
                    ('technical closed', lambda: window.damage_technical.setChecked(False))):
                    pure(label, callback)
                assert window.target_enemy.currentData() is None and not window.target_buff_test.isChecked()
                if context == 'core':
                    for mode in ('frames', 'continuous'):
                        select(SU, mode=mode)
                        pure('reference initially off', lambda: window.account_skill_reference.setChecked(False))
                        a = snapshot('A-' + mode, 5, 'run_confirmed', expected_elite=1)
                        pure('choose actual lower read account grade', lambda: window.account_skill_reference.setChecked(True))
                        b = snapshot('B-' + mode, 3, 'manual_account_reference', manual=True, expected_elite=1)
                        reference_pair(a, b)
                        assert a['value']['damage_result']['result']['estimate']['skill']['total_healing'] != b['value']['damage_result']['result']['estimate']['skill']['total_healing']
                        if mode == 'frames':
                            capture('account-reference-lower-rank')
                        pure('cancel actual account reference', lambda: window.account_skill_reference.setChecked(False))
                        c = snapshot('C-' + mode, 5, 'run_confirmed', expected_elite=1)
                        assert_native_equal(c['value']['damage_result'], a['value']['damage_result'], 'cancellation restores complete caller/result')
                        assert_native_equal(c['value']['texts'], a['value']['texts'], 'cancellation restores complete three texts')
                        assert_native_equal(c['value']['state_and_disks'], a['value']['state_and_disks'], 'control pair state/disk purity')
                        pairs.append({'id': 'cancel-' + mode, 'before': a['snapshot'], 'selected': b['snapshot'], 'restored': c['snapshot']})
                    active.update(case='D-public-observation', phase='intentional_public_fixture_update')
                    before = freeze(joint())
                    public_account = profile(SU, 1, {1: 7, 2: 7})
                    window.apply_operator_observation(public_account, 2000.0)
                    public_member = member(SU, 1, {1: 3, 2: 4})
                    assert window.apply_run_observation({'operators': [public_member]}, 2000.0)
                    idle()
                    save('actual_explicit_public_observation_ingress', before=before, after=joint(), account_input=public_account, run_input=public_member)
                    for mode in ('frames', 'continuous'):
                        select(SU, mode=mode)
                        pure('higher account rank reference', lambda: window.account_skill_reference.setChecked(True))
                        snapshot('D-' + mode, 7, 'manual_account_reference', manual=True, expected_elite=1)
                    select(SU, 2)
                    snapshot('E-skill-switch-clear', 4, 'run_confirmed', expected_elite=1)
                    pure('reference active before owner switch', lambda: window.account_skill_reference.setChecked(True))
                    snapshot('E-skill2-reference-before-owner', 7, 'manual_account_reference', manual=True, expected_elite=1)
                    select(AM)
                    snapshot('F-owner-switch-clear', 2, 'run_confirmed', expected_elite=1)
                    select(SU)
                    snapshot('G-return-without-reference', 3, 'run_confirmed', expected_elite=1)
                    pure('actual account-only training mode', lambda: window.use_run_training.setChecked(False))
                    snapshot('M-account-only', 7, 'account_reference', expected_elite=1)
                    pure('restore actual run training mode', lambda: window.use_run_training.setChecked(True))
                    snapshot('M-run-mode-restore', 3, 'run_confirmed', expected_elite=1)
                    select(DEPARTED)
                    snapshot('M-departed-account-reference', 7, 'account_reference', expected_elite=1)
                    for op in PATCHES:
                        for skill in (1, 2):
                            select(op, skill)
                            snapshot('N-missing-patch-' + op + '-S' + str(skill), 10, 'run_confirmed', expected_elite=2)
                    select(NO_SKILL, skill=None)
                    value = snapshot('O-unimplemented-no-skill', None, None, no_numeric=True)
                    assert '未知伤害' in window.damage_text.toPlainText()
                    select(SU)
                    pure('reference before real new run', lambda: window.account_skill_reference.setChecked(True))
                    snapshot('L-before-real-new-run', 7, 'manual_account_reference', manual=True, expected_elite=1)
                    before = freeze(joint())
                    active.update(case='L-real-reset', phase='explicit_user_reset')
                    window.reset_run()
                    idle()
                    assert not window.account_skill_reference.isChecked()
                    assert window.run.state['id'] != before['run']['id'] and window.run.state['operators'] == {}
                    assert_native_equal(window.account_cache.records, before['account'], 'new run retains complete account')
                    assert account_path.read_bytes() == before['disks']['account.json']
                    save('actual_explicit_new_run', before=before, after=joint())
                    select(SU)
                    snapshot('L-after-real-reset-same-skill', 7, 'account_reference', expected_elite=1)
                    pure('empty actual run overview', lambda: window.operator_choices.select_branch('__overview__'))
                    snapshot('O-empty-new-run-overview', None, None, no_numeric=True)
                elif context == 'H':
                    select(SU)
                    pure('compatible reference before source change', lambda: window.account_skill_reference.setChecked(True))
                    snapshot('H-before-incompatible-read', 7, 'manual_account_reference', manual=True, expected_elite=1)
                    active.update(case='H-new-account-mastery', phase='intentional_public_account_observation')
                    before = freeze(joint())
                    public_account = profile(SU, 2, {1: 10})
                    window.apply_operator_observation(public_account, 2000.0)
                    idle()
                    save('actual_explicit_public_account_ingress', before=before, after=joint(), input=public_account)
                    assert not window.account_skill_reference.isEnabled() and not window.account_skill_reference.isChecked()
                    assert '不会自动改成7级' in window.account_skill_reference.toolTip()
                    snapshot('H-incompatible-mastered-account', 3, 'run_confirmed', expected_elite=1)
                elif context in ('I', 'J', 'K'):
                    baseline_rank = 7 if context in ('I', 'K') else 5
                    chosen_rank = 10 if context == 'I' else 7 if context == 'J' else 3
                    baseline_source = 'preview_unconfirmed' if context == 'K' else 'run_confirmed'
                    elite = 2 if context == 'I' else 0 if context == 'J' else 1
                    for mode in ('frames', 'continuous'):
                        select(SU, mode=mode)
                        pure('off before reference pair', lambda: window.account_skill_reference.setChecked(False))
                        a = snapshot(context + '-default-' + mode, baseline_rank, baseline_source, expected_elite=elite)
                        pure('choose actual compatible account', lambda: window.account_skill_reference.setChecked(True))
                        b = snapshot(context + '-reference-' + mode, chosen_rank, 'manual_account_reference', manual=True, expected_elite=elite)
                        reference_pair(a, b)
                        if context == 'J' and mode == 'frames':
                            capture('e0-read-reference-use-unknown')
                        pure('cancel compatible account', lambda: window.account_skill_reference.setChecked(False))
                        c = snapshot(context + '-cancel-' + mode, baseline_rank, baseline_source, expected_elite=elite)
                        assert_native_equal(c['value']['damage_result'], a['value']['damage_result'], 'whole context cancellation result')
                        assert_native_equal(c['value']['texts'], a['value']['texts'], 'whole context cancellation three texts')
                        pairs.append({'id': context + '-cancel-' + mode, 'before': a['snapshot'], 'selected': b['snapshot'], 'restored': c['snapshot']})
                else:
                    for mode in ('frames', 'continuous'):
                        select(SU, mode=mode)
                        assert window.training_view_notice and '暂用' in window.training_view_notice
                        assert window.run.state['operators'][SU]['fields']['elite'] == []
                        snapshot('unsafe-original-run-retained-' + mode, 3, 'account_reference', expected_elite=1)
                active.update(case=context + '-close', phase='real_close_direct_reload')
                before = freeze(joint())
                window.close()
                application.processEvents()
                assert_native_equal(joint(), before, 'real close retains complete public joint')
                restarted = RunState(run_path)
                assert not restarted.preserve_unreadable and restarted.save_issue is None
                expected_reloaded_run = freeze(before['run'])
                original_notice = expected_reloaded_run['notice']
                expected_reloaded_run['notice'] = '已恢复同一局的记忆；切换另一局时请手动点击“开始新局”。'
                assert_native_equal(restarted.state, expected_reloaded_run, 'direct current RunState reload with exact existing constructor notice')
                account_restarted = AccountCache(account_path, profiles=operator_profiles(), implemented_ids=catalog()['operators'])
                assert not account_restarted.issues and not account_restarted.preserve_original
                assert_native_equal(account_restarted.records, before['account'], 'direct current account reload')
                assert_native_equal(joint(), before, 'both direct reload disk purity')
                ref = save('actual_close_RunState_AccountCache_reload', live_before=before, restart_state=restarted.state,
                           expected_restart_state=expected_reloaded_run,
                           existing_constructor_notice_transition={'before': original_notice, 'after': expected_reloaded_run['notice'],
                                                                   'scope': 'Only existing constructor presentation notice; no numeric/source record repair.'},
                           account_restart_records=account_restarted.records, disks_after=joint()['disks'])
                reloads.append({'context': context, 'native': ref})
                window.deleteLater()
                application.processEvents()
                window = None
        ids = {row['id'] for row in rows}
        required = {'E-skill-switch-clear', 'E-skill2-reference-before-owner', 'F-owner-switch-clear', 'G-return-without-reference',
                    'H-incompatible-mastered-account', 'M-account-only', 'M-run-mode-restore',
                    'M-departed-account-reference', 'L-after-real-reset-same-skill',
                    'O-unimplemented-no-skill', 'O-empty-new-run-overview'}
        for letter in ('A', 'B', 'C', 'D'):
            required.update(letter + '-' + mode for mode in ('frames', 'continuous'))
        for letter in ('I', 'J', 'K'):
            required.update(letter + '-' + part + '-' + mode for part in ('default', 'reference', 'cancel') for mode in ('frames', 'continuous'))
        required.update('N-missing-patch-' + op + '-S' + str(skill) for op in PATCHES for skill in (1, 2))
        required.update('unsafe-original-run-retained-' + mode for mode in ('frames', 'continuous'))
        assert required <= ids and len(ids) == len(rows)
        assert len(pngs) == 2 and len(reloads) == 6 and not errors and all(c['error'] is None for c in calls)
        receipt.update(passed=True, workflow_complete=True, required_case_ids=sorted(required), actual_windows=len(reloads))
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
            if old_paths is not None:
                module.RUN_STATE, module.OPERATOR_STATE, module.SETTINGS = old_paths
        sys.excepthook = old_hook
        receipt['actual_numeric_calls'] = len(calls)
        receipt['fresh_reference_API_calls'] = len(reference_calls)
        receipt['source_after'] = source_map(root)
        receipt['source_additional_after'] = {name: sha((root / name).read_bytes()) for name in extra}
        receipt['source_drift'] = [name for name in set(expected) | set(receipt['source_after']) if expected.get(name) != receipt['source_after'].get(name)]
        if receipt['source_drift'] or receipt['source_additional_after'] != extra or guard_path.read_bytes() != guard_raw or errors:
            receipt.update(passed=False, workflow_complete=False)
        receipt['elapsed_seconds'] = time.perf_counter() - started
        with (out / 'receipt.json').open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        done.set()
    print(json.dumps({'passed': receipt['passed'], 'rows': len(rows), 'pairs': len(pairs), 'pngs': len(pngs)}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
