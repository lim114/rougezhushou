"""Source-only Saved proposal; Root executes after independent Source review.

No project/API/formatter/Qt imports or result recalculation. Bind the complete
original section122 window protocol, native graphs and compressed evidence.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import threading
import time
import traceback

sys.dont_write_bytecode = True
import native_evidence as native

HELPER_SHA = 'f040258eddbb7ad624e547e2c422a3d432f7ffeae025b2576b625683ea43fe9a'
NOTICE = '已恢复同一局的记忆；切换另一局时请手动点击“开始新局”。'
WINDOW_SHA = '83e96b323101d93d70c24a04f2e6519f3659ccac5f04f6475e88709ef41c54e7'
CASES_SHA = 'ba420ec06d02f9476814a4b3da0b2b353a1703cfaa9885f464164c41be7af6e1'
WINDOW_MANIFEST_SHA = '6e3d3d1e4843a82087b8fdc12b9ac6245d53ab25b6210d45167f2050d3bc5736'
SAVED_DEADLINE = 180
OP = 'mechanist'
ATTACK = 'rogue_6_relic_legacy_15'
ALTAR = 'rogue_6_relic_legacy_103'
TOOL = 'rogue_6_active_tool_5'
SNACK = 'rogue_6_from_relic_13'
COOKIE = 'rogue_6_from_relic_9'
RECIPIENT_KEYS = ('char_buff_ids', 'char_buffs_complete',
                  'char_buff_absent_ids', 'char_buff_pending_ids')
RUN_KEYS = ('id', 'started_at', 'last_read', 'operators', 'crew_count', 'selected_operator',
            'relics', 'relic_count', 'bar_signature', 'inventory_verified', 'inventory_confirmed_at',
            'relic_icon_memory', 'history', 'resources', 'tactical_tools', 'config', 'maps',
            'last_node_content', 'node_contents', 'notice')


def sha(raw):
    assert type(raw) is bytes
    return hashlib.sha256(raw).hexdigest()


def same(actual, expected, label):
    native.assert_native_equal(actual, expected, label)


def joint_projection(value, keys):
    """Retain original graph references, including edges between selected fields."""
    return {key: value[key] for key in keys}


def same_projection(actual, expected, keys, label):
    same(joint_projection(actual, keys), joint_projection(expected, keys), label)


def read_pinned(path, frozen):
    path = Path(path)
    assert not path.is_symlink()
    path = path.resolve()
    assert path.is_file() and not path.is_symlink()
    raw = path.read_bytes()
    if path in frozen:
        assert raw == frozen[path]
    else:
        frozen[path] = raw
    return raw


def write_exact(path, raw):
    path = Path(path)
    assert type(raw) is bytes and not path.exists()
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    assert path.read_bytes() == raw


class NativeLedger:
    """Root runtime-only full native loader; keep compressed original bytes intact."""
    def __init__(self, folder, refs, contexts, frozen, copy_folder):
        self.folder = Path(folder).resolve()
        record_folder = self.folder / 'records'
        assert record_folder.is_dir() and not record_folder.is_symlink()
        assert type(refs) is list and refs
        self.refs, self.values, self.positions = {}, {}, {}
        names = ['%06d.pickle.gz' % n for n in range(1, len(refs) + 1)]
        assert [ref['path'] for ref in refs] == names
        assert {path.name for path in record_folder.iterdir()} == set(names)
        copy_folder.mkdir()
        required = {'path', 'bytes', 'sha256', 'decoded_bytes',
                    'decoded_sha256', 'pickle_protocol', 'kind',
                    'context', 'case', 'phase'}
        for position, ref in enumerate(refs):
            assert type(ref) is dict and set(ref) == required
            assert type(ref['bytes']) is int and ref['bytes'] > 0
            assert type(ref['decoded_bytes']) is int and ref['decoded_bytes'] > 0
            assert type(ref['pickle_protocol']) is int and ref['pickle_protocol'] == 4
            for key in ('path', 'sha256', 'decoded_sha256', 'kind', 'context', 'case', 'phase'):
                assert type(ref[key]) is str and ref[key]
            assert ref['context'] in contexts
            path = record_folder / ref['path']
            assert path.is_file() and not path.is_symlink()
            raw = path.read_bytes()
            assert len(raw) == ref['bytes'] and sha(raw) == ref['sha256']
            frozen[path] = raw
            value = native.read_record(record_folder, ref)
            for key in ('kind', 'context', 'case', 'phase'):
                same(value[key], ref[key], 'complete ledger active metadata ' + key)
            self.refs[ref['path']] = ref
            self.values[ref['path']] = value
            self.positions[ref['path']] = position
            write_exact(copy_folder / ref['path'], raw)
        self.names = names

    def get(self, ref, kind):
        assert type(ref) is dict and ref['path'] in self.refs
        same(ref, self.refs[ref['path']], 'complete record reference/hash/native metadata')
        value = self.values[ref['path']]
        assert value['kind'] == kind
        return value

    def position(self, ref):
        self.get(ref, ref['kind'])
        return self.positions[ref['path']]


def validate_receipt_common(receipt, guard, guard_raw, source_count,
                            contexts, runner_sha, deadline):
    assert receipt['kind'] == 'ROOT_ACTUAL_122_REAL_MAINWINDOW'
    assert type(receipt['section']) is int and receipt['section'] == 122
    assert receipt['passed'] is True and receipt['workflow_complete'] is True
    assert not receipt.get('failure')
    assert receipt['runner_sha256'] == runner_sha
    assert receipt['native_helper_sha256'] == HELPER_SHA
    assert receipt['source_guard_sha256'] == sha(guard_raw)
    assert type(receipt['source_count']) is int
    assert receipt['source_count'] == source_count == len(guard['source_sha256'])
    same(receipt['source_before'], guard['source_sha256'], 'whole Source before')
    same(receipt['source_after'], guard['source_sha256'], 'whole Source after')
    same(receipt['source_additional_before'], guard['source_additional_sha256'], 'CORE before')
    same(receipt['source_additional_after'], guard['source_additional_sha256'], 'CORE after')
    assert receipt['source_drift'] == [] and receipt['Qt_errors'] == []
    assert type(receipt['actual_windows']) is int and receipt['actual_windows'] == len(contexts)
    assert receipt['private_state_access'] is False
    assert receipt['native_windows_verified'] is False
    assert receipt['game_chat_sampling_executed'] is False
    assert type(receipt['deadline_seconds']) is int and receipt['deadline_seconds'] == deadline
    assert type(receipt['elapsed_seconds']) in (int, float)
    assert math.isfinite(receipt['elapsed_seconds'])
    assert 0 <= receipt['elapsed_seconds'] < deadline


def validate_guard(root, guard, source_count):
    assert type(guard['section']) is int and guard['section'] == 122
    assert source_count == len(guard['source_sha256'])
    same(native.source_map(root), guard['source_sha256'], 'actual whole maintained Source')
    extra = guard['source_additional_sha256']
    assert set(extra) == {'CORE_0.70_VERIFICATION.json'}
    same({name: sha((root / name).read_bytes()) for name in extra}, extra,
         'actual additional CORE original bytes')


def same_reload_notice_only(close, joint):
    """Derive the exact JSON boundary and constructor notice independently.

    A saved member buff list may alias its history list in live memory. JSON
    persistence breaks that edge; the actual parsed graph, not a clone of the
    live graph, is therefore the independently valid restart expectation.
    """
    same(close['live_before'], joint, 'real close complete current public graph')
    persisted = json.loads(joint['disks']['run.json'])
    expected = constructor_run_graph(persisted)
    same(close['restart_state'], expected, 'actual complete RunState reload')
    same(close['account_restart_records'], joint['account'], 'actual complete AccountCache reload')
    same(close['disks_after'], joint['disks'], 'actual close/reload every public disk byte')
    same(close['persisted_json'], persisted,
         'actual persisted JSON independently derived from exact current disk bytes')


def validate_chronological_joint(ledger, contexts, brackets, display_only_labels):
    """A Source-bound begin/end bracket is the only route to a new current graph.

    Every bracket entry must already have exact full references named begin/end.
    Its numeric callbacks may only see the declared final_after graph. Repeated
    active case metadata outside the exact interval gives no permission to write.
    """
    initial = {}
    for name in ledger.names:
        value = ledger.values[name]
        if value['kind'] == 'actual_public_fixture_loaded':
            assert value['context'] not in initial
            initial[value['context']] = (ledger.positions[name], value)
    assert set(initial) == set(contexts)
    current = {context: value['value'] for context, (_, value) in initial.items()}
    begin_by_name, end_by_name, numeric_brackets = {}, {}, {}
    for row in brackets:
        begin = ledger.get(row['begin'], 'actual_ingress_begin')
        end = ledger.get(row['end'], 'actual_ingress_end')
        same(end['begin_ref'], row['begin'], 'ingress ending exact full begin reference')
        begin_name, end_name = row['begin']['path'], row['end']['path']
        first, stop = ledger.positions[begin_name], ledger.positions[end_name]
        assert first < stop and begin_name not in begin_by_name and end_name not in end_by_name
        for key in ('context', 'case', 'phase'):
            same(begin[key], end[key], 'ingress begin/end exact active metadata')
        same(end['before'], begin['before'], 'ingress complete before graph binding')
        same(end['caller_before'], begin['caller'], 'ingress original typed caller binding')
        same(end['caller_after'], end['caller_before'], 'ingress typed public caller purity')
        assert end['return_value'] is True
        bracket = {'row': row, 'begin': begin, 'end': end}
        begin_by_name[begin_name] = bracket
        end_by_name[end_name] = bracket
        for position in range(first + 1, stop):
            name = ledger.names[position]
            value = ledger.values[name]
            assert value['kind'] == 'actual_calculate_result'
            for key in ('context', 'case', 'phase'):
                same(value[key], begin[key], 'ingress callback exact active metadata')
            assert name not in numeric_brackets
            numeric_brackets[name] = bracket
    assert {name for name in ledger.names if ledger.values[name]['kind'] == 'actual_ingress_begin'} == set(begin_by_name)
    assert {name for name in ledger.names if ledger.values[name]['kind'] == 'actual_ingress_end'} == set(end_by_name)
    active = {}
    numeric_count = 0
    for name in ledger.names:
        value = ledger.values[name]
        kind, context = value['kind'], value['context']
        joint = current[context]
        if kind == 'actual_public_fixture_loaded':
            assert context not in active
            same(value['value'], joint, 'loaded public fixture current graph')
        elif kind == 'actual_ingress_begin':
            assert context not in active
            same(value['before'], joint, 'explicit ingress begins at exact current graph')
            active[context] = begin_by_name[name]
        elif kind == 'actual_ingress_end':
            assert context in active and active[context] is end_by_name[name]
            same(value['before'], joint, 'explicit ingress before remains current graph')
            current[context] = value['after']
            del active[context]
        elif kind == 'actual_calculate_result':
            same(value['after'], value['before'], 'complete numeric caller/joint native purity')
            if name in numeric_brackets:
                bracket = numeric_brackets[name]
                assert active.get(context) is bracket
                same(value['before']['joint'], bracket['end']['after'],
                     'reentrant ingress numeric joint exact final_after graph')
            elif 'joint' in value['before']:
                assert context not in active
                same(value['before']['joint'], joint, 'ordinary numeric complete current graph')
            else:
                assert ledger.positions[name] < initial[context][0]
                assert value['case'] == 'initial' and value['phase'] == 'constructor' and context not in active
            numeric_count += 1
        elif kind == 'actual_UI_step':
            assert context not in active
            same(value['before']['joint'], joint, 'ordinary UI enters current complete graph')
            same(value['after']['joint'], joint, 'ordinary UI preserves current complete graph')
            assert type(value['display_only']) is bool
            if value['display_only']:
                assert value['label'] in display_only_labels
                same(value['after'], value['before'], 'display-only UI whole graph purity')
        elif kind == 'actual_fresh_API_reference':
            assert context not in active
            same_projection(value['after'], value['before'], ('args', 'kwargs', 'joint'),
                            'fresh reference original API complete caller/joint purity')
            same(value['before']['joint'], joint, 'fresh original API exact current public graph')
        elif kind == 'actual_three_formatter_group':
            assert context not in active
            same(value['after'], value['before'], 'three formatter complete whole graph purity')
            same(value['before']['joint'], joint, 'three formatter current complete graph')
        elif kind == 'actual_window_snapshot':
            assert context not in active
            same(value['value']['state_and_disks'], joint, 'snapshot current complete public graph')
        elif kind == 'actual_close_RunState_account_reload':
            assert context not in active
            same_reload_notice_only(value, joint)
        elif kind in ('actual_PNG_bounded_unknown_summary', 'actual_PNG_bounded_fresh_Snack_report'):
            assert context not in active
            same(value['joint'], joint, 'PNG exact current complete public graph')
        else:
            raise AssertionError('Unbound section122 record kind: ' + kind)
    assert not active
    return {'initial': initial, 'current': current, 'numeric_count': numeric_count,
            'intentional_reentrant_numeric_count': len(numeric_brackets),
            'intentional_bracket_count': len(brackets)}


def verify_initial_fixtures(initial, cases):
    """Expected native graphs come from the exact sealed public input, not output."""
    specs = {item['id']: item for item in cases['contexts']}
    assert set(initial) == set(specs) and len(specs) == 6
    for context, (_, saved) in initial.items():
        spec = specs[context]
        joint = saved['value']
        same(saved['run_bytes'], joint['disks']['run.json'], 'original public run file raw bytes')
        same(saved['account_bytes'], joint['disks']['account.json'], 'original public account file raw bytes')
        raw_run = json.loads(saved['run_bytes'])
        raw_account = json.loads(saved['account_bytes'])
        same(raw_run, spec['run'], 'exact sealed public run input including native type/order')
        same(raw_account, spec['account'], 'exact sealed public account input including native type/order')
        loaded = constructor_run_graph(raw_run)
        same(joint['run'], loaded, 'existing constructor graph/order with notice-only presentation')
        same(joint['account'], raw_account, 'complete loaded public account graph')
        same(joint['run']['public_opaque'], {'signed_zero': -0.0, 'nullable': None},
             'opaque signed-zero and nullable public graph')


def constructor_run_graph(parsed):
    result = {key: parsed[key] for key in RUN_KEYS if key != 'notice'}
    result['notice'] = NOTICE
    for key, item in parsed.items():
        if key not in result:
            result[key] = item
    return result


def row_specifications(cases):
    rows = []
    def add(context, stage, wanted, modes=None):
        for mode in modes or cases['modes']:
            rows.append({'id': context + ':' + stage + ':' + mode,
                         'context': context, 'stage': stage, 'mode': mode,
                         'expected': wanted})
    for context in cases['contexts']:
        identity = context['id']
        add(identity, 'initial', context['initial'])
        if identity == 'unknown_string':
            manual = {**context['initial'], 'rank_source': 'manual_account_reference'}
            add(identity, 'initial_manual_account', manual, ('frames',))
            add(identity, 'initial_manual_cancel', context['initial'], ('frames',))
            for stage in cases['string_ingress']:
                add(identity, stage['id'], stage['expected'])
                if stage['id'] == 'identity_only':
                    manual = {**stage['expected'], 'rank': 3,
                              'rank_source': 'manual_account_reference'}
                    manual.pop('sp_cost')
                    add(identity, 'identity_manual_account', manual, ('frames',))
                    add(identity, 'identity_manual_cancel', stage['expected'], ('frames',))
        elif identity == 'unknown_number':
            for stage in cases['number_ingress']:
                add(identity, stage['id'], stage['expected'])
    assert len(rows) == cases['expected_rows'] == 42
    return rows


def check_snapshot_expected(want, snapshot, mode):
    caller, projected = snapshot['caller'], snapshot['projection']
    result = snapshot['damage_result']['result']
    for key, field in (('skill', 'skill'), ('rank', 'skill_rank'), ('elite', 'elite'), ('level', 'level')):
        same(caller[field], want[key], 'sealed case exact selected ' + field)
    same(caller['operator'], OP, 'actual catalog owner')
    for key, value in (('trust', 0), ('potential', 1), ('module_id', None), ('module_level', 0)):
        same(caller[key], value, 'actual complete cultivation ' + key)
    assert caller['enemy_defense'] == 0 and caller['enemy_resistance'] == 0
    assert 'base_attack' not in caller and 'target_enemy' not in caller
    same(caller['timing_mode'], mode, 'actual requested timing mode')
    assert caller['window_seconds'] == 10.0 and caller['continuous_attacks'] is True
    same(caller['timing'], {'windup_frames': 0, 'recovery_frames': 0}, 'actual zero-motion public timing')
    same(sorted(caller['relic_ids']), sorted(want['held']), 'qualified automatic real relic inputs')
    same(projected['held'], sorted(want['held']), 'qualified public held query')
    same(projected['tools'], sorted(want['tools']), 'qualified public tool query')
    same(sorted(projected['checked_relics']), sorted(want['held']), 'actual checked inventory')
    same(caller['char_buff_ids'], want['buffs'], 'qualified own positive buff subset')
    same(projected['rank_selection']['source'], want['rank_source'], 'actual rank source')
    assert (OP in projected['recruited']) is want['recruited']
    assert (OP in projected['overview_ids']) is want['recruited']
    assert ('altar_stacks' in projected['resources']) is want['counter']
    assert ('altar_stacks' in caller['relic_context']) is want['counter']
    if want['counter']:
        same(projected['resources']['altar_stacks'],
             snapshot['state_and_disks']['run']['resources']['altar_stacks'],
             'complete qualified public counter record equals current stored proof')
        same(caller['relic_context']['altar_stacks'],
             projected['resources']['altar_stacks']['value'],
             'actual numeric counter value equals complete qualified public proof')
    same(caller['inventory_status'], projected['inventory'], 'full caller/public inventory status')
    assert projected['widgets']['auto_relics'] is True and projected['widgets']['use_run_training'] is True
    same(projected['widgets']['operator'], OP, 'actual selected widget owner')
    same(projected['widgets']['skill'], want['skill'], 'actual selected widget skill')
    same(projected['widgets']['level'], want['level'], 'actual selected widget level')
    assert projected['widgets']['frame_timing'] is (mode == 'frames')
    manual = want['rank_source'] == 'manual_account_reference'
    assert projected['widgets']['manual_account'] is manual
    assert projected['rank_selection']['manual_reference_applied'] is manual
    if want.get('unknown'):
        assert projected['inventory']['complete'] is False
        same(sorted(projected['inventory']['unconfirmed_item_ids']), sorted([ATTACK, ALTAR, TOOL]),
             'exact retained unknown inventory qualification IDs')
        assert '在场状态未确认' in projected['summary'] and '持有状态未确认' in projected['summary']
        assert '在场标记未确认' in projected['training_status']
        assert '在场状态未确认' in projected['raw_training_text']
        assert '已离队' not in projected['summary']
        same(projected['run_metadata'], {}, 'unknown run metadata not consumed')
    if 'origin' in want:
        same(projected['run_metadata'].get('recruitment_kind'), want['origin'], 'individually requalified origin')
    if 'advanced' in want:
        if want['advanced'] == 'absent':
            assert 'advanced' not in projected['run_metadata']
        else:
            same(projected['run_metadata']['advanced'], want['advanced'], 'individually requalified advanced flag')
    if 'recipient_mask' in want:
        assert bool(set(projected['mask']).intersection(RECIPIENT_KEYS)) is want['recipient_mask']
    if 'sp_cost' in want:
        cost = result['estimate']['skill']['sp_cost']
        # The source-backed numeric oracle is35/28; the original whole result
        # comparison above retains the actual int/float contract. Snack's0.8
        # multiplication produces28.0, so do not invent an int result schema.
        assert type(cost) in (int, float) and math.isfinite(cost) and cost == want['sp_cost']


def verify_snapshots(ledger, receipt, cases):
    specs = row_specifications(cases)
    assert len(receipt['rows']) == len(specs)
    assert [row['id'] for row in receipt['rows']] == [row['id'] for row in specs]
    snapshots, references = {}, {}
    proof = []
    for row, spec in zip(receipt['rows'], specs):
        same_projection(row, spec, ('id', 'context', 'stage', 'mode', 'expected'), 'whole ordered public row definition')
        refs = (row['numeric'], row['ui_step'], row['reference'], row['formatter'],
                row['technical_step'], row['ordinary_step'], row['snapshot'])
        kinds = ('actual_calculate_result', 'actual_UI_step', 'actual_fresh_API_reference',
                 'actual_three_formatter_group', 'actual_UI_step', 'actual_UI_step', 'actual_window_snapshot')
        values = [ledger.get(ref, kind) for ref, kind in zip(refs, kinds)]
        positions = [ledger.position(ref) for ref in refs]
        assert positions == list(range(positions[0], positions[0] + 7))
        for value in values:
            same(value['context'], spec['context'], 'whole snapshot context')
            same(value['case'], spec['stage'] + '-' + spec['mode'], 'whole snapshot case')
            same(value['phase'], 'explicit_snapshot', 'whole snapshot phase')
        numeric, step, reference, formatter, technical, ordinary, saved = values
        assert step['label'] == 'MainWindow.calculate' and step['display_only'] is False
        assert technical['label'] == 'actual technical report checkbox' and technical['display_only'] is True
        assert ordinary['label'] == 'actual ordinary report checkbox' and ordinary['display_only'] is True
        same(saved['expected'], spec['expected'], 'full sealed snapshot expected case')
        same(saved['mode'], spec['mode'], 'full sealed snapshot mode')
        value = saved['value']
        result = value['damage_result']['result']
        actual_joint = {'args': (value['caller'],), 'kwargs': {},
                        'joint': value['state_and_disks'], 'result': result}
        numeric_joint = {**numeric['after'], 'result': numeric['result']}
        same(actual_joint, numeric_joint, 'whole actual caller/result/public graph including cross-container aliases')
        same(reference['after'], numeric_joint, 'fresh original API whole caller/result/joint graph with aliases')
        same_projection(reference['after'], reference['before'], ('args', 'kwargs', 'joint'), 'fresh original API caller/joint purity')
        actual_wrapper = {'caller': value['caller'], 'damage_result': value['damage_result'],
                          'joint': value['state_and_disks']}
        expected_wrapper = {'caller': numeric['after']['args'][0],
                            'damage_result': {'scenario': numeric['after']['args'][0],
                                              'result': numeric['result']},
                            'joint': numeric['after']['joint']}
        same(actual_wrapper, expected_wrapper, 'complete snapshot caller/GUI-wrapper/public graph aliases')
        reference_wrapper = {'caller': reference['after']['args'][0],
                             'damage_result': {'scenario': reference['after']['args'][0],
                                               'result': reference['after']['result']},
                             'joint': reference['after']['joint']}
        same(actual_wrapper, reference_wrapper, 'complete fresh API caller/GUI-wrapper/public graph aliases')
        # UI_step saves joint first; formatter saves damage_result first.
        # Preserve each producer's exact dict order, and compare cross-protocol
        # fields jointly in a shared order without splitting their alias graph.
        expected_ui = {'joint': value['state_and_disks'], 'damage_result': value['damage_result']}
        expected_formatter = {'damage_result': value['damage_result'], 'joint': value['state_and_disks']}
        same(step['after'], expected_ui, 'actual calculate UI completion whole result/joint graph')
        same(formatter['before'], expected_formatter, 'complete formatter input/result/joint cross aliases')
        same(formatter['after'], formatter['before'], 'complete three formatter group native purity')
        same_projection(technical['before'], formatter['after'], ('joint', 'damage_result'),
                        'actual technical toggle whole original cross-protocol graph')
        same(ordinary['before'], technical['after'], 'actual ordinary toggle exact prior graph')
        same(formatter['texts'], value['texts'], 'all three complete native report strings')
        assert tuple(value['texts']) == ('estimate', 'default', 'technical')
        assert all(type(text) is str and text for text in value['texts'].values())
        assert value['texts']['estimate'] == value['texts']['default']
        same(value['displayed_damage'], value['texts']['default'].replace(chr(160), ' '), 'complete actual ordinary display')
        check_snapshot_expected(spec['expected'], value, spec['mode'])
        snapshots[spec['id']] = value
        references[row['snapshot']['path']] = spec['id']
        proof.append({'id': spec['id'], 'full_references': refs,
                      'complete_native_call_result_report_joint_graph': True})
    assert [name for name in ledger.names if ledger.values[name]['kind'] == 'actual_window_snapshot'] == [row['snapshot']['path'] for row in receipt['rows']]
    assert len([name for name in ledger.names if ledger.values[name]['kind'] == 'actual_fresh_API_reference']) == len(specs)
    assert len([name for name in ledger.names if ledger.values[name]['kind'] == 'actual_three_formatter_group']) == len(specs)
    for before, after in (('initial', 'initial_manual_cancel'), ('identity_only', 'identity_manual_cancel')):
        a = snapshots['unknown_string:' + before + ':frames']
        b = snapshots['unknown_string:' + after + ':frames']
        same_projection(a, b, ('caller', 'damage_result', 'texts', 'displayed_damage', 'state_and_disks'),
                        'manual account cancellation restores complete caller/result/text/public graph')
    return snapshots, references, proof


def verify_ingress_semantics(ledger, receipt, cases):
    expected = [('unknown_string', stage) for stage in cases['string_ingress']]
    expected += [('unknown_number', stage) for stage in cases['number_ingress']]
    assert len(receipt['ingresses']) == len(expected) == 13
    assert [(row['context'], row['id']) for row in receipt['ingresses']] == [(context, stage['id']) for context, stage in expected]
    newline = receipt['newline']
    assert type(newline) is str and newline in ('\n', '\r\n')
    proof = []
    for row, (context, stage) in zip(receipt['ingresses'], expected):
        begin = ledger.get(row['begin'], 'actual_ingress_begin')
        end = ledger.get(row['end'], 'actual_ingress_end')
        for saved in (begin, end):
            same(saved['context'], context, 'exact public ingress context')
            same(saved['case'], stage['id'], 'exact public ingress case')
            same(saved['phase'], 'explicit_public_ingress', 'exact public ingress phase')
        same(begin['caller'], {'observed': stage['observed'], 'captured_at': stage['at']},
             'complete sealed public ingress caller including all native types')
        before, after = end['before'], end['after']
        same(after['account'], before['account'], 'explicit run ingress complete account purity')
        same(after['disks']['account.json'], before['disks']['account.json'], 'explicit ingress original account bytes')
        assert set(before['disks']) == set(after['disks']) == {'account.json', 'run.json'}
        same(tuple(after['run']), tuple(before['run']), 'ingress complete outer run key order')
        same(after['run']['history'][:len(before['run']['history'])], before['run']['history'], 'ingress original history prefix')
        text = json.dumps(after['run'], ensure_ascii=False, indent=2)
        text = text.encode('utf-8', errors='backslashreplace').decode('utf-8')
        same(after['disks']['run.json'], text.replace('\n', newline).encode('utf-8'),
             'exact actual save serialized bytes and newline policy without live JSON alias assumption')
        if context == 'unknown_string':
            events = after['run']['history']
            assert not {event['kind'] for event in events}.intersection(
                ('recruitment_changed', 'classification_corrected', 'char_buff_absence_invalidated',
                 'relic_confirmed', 'tool_confirmed'))
            if stage['id'] == 'identity_only':
                previous = before['run']['operators'][OP]
                actual = after['run']['operators'][OP]
                same_projection(actual, previous,
                    ('fields', 'skill_ranks', 'char_buff_ids', 'char_buff_absent_ids',
                     'char_buffs_complete', 'recruitment_kind', 'advanced', 'public_opaque'),
                    'identity-only raw cultivation/source/own-buff leaves and aliases retained')
                qualifies = [event for event in events if event['kind'] == 'state_flag_reconfirmed' and event['record_kind'] == 'operator']
                assert len(qualifies) == 1 and qualifies[0]['value'] is True
                same(qualifies[0]['previous_record'], previous, 'full original raw operator qualification evidence')
                assert actual['present'] is True
            if stage['at'] < 2010:
                same(after['run']['resources']['altar_stacks'], before['run']['resources']['altar_stacks'],
                     'retained old counter proof unchanged until independent fresh read')
            if stage['id'] == 'held_bar':
                qualifies = [event for event in events if event['kind'] == 'state_flag_reconfirmed' and event['field'] == 'held']
                assert len(qualifies) == 3 and all(event['value'] is True for event in qualifies)
                for event in qualifies:
                    collection = 'relics' if event['record_kind'] == 'relic' else 'tactical_tools'
                    same(event['previous_record'], before['run'][collection][event['id']], 'complete original raw held qualification evidence')
            if stage['id'] == 'fresh_counter':
                same(after['run']['resources']['altar_stacks'],
                     {**stage['observed']['resources']['altar_stacks'], 'captured_at': stage['at']},
                     'complete independently specified fresh counter proof')
        else:
            assert stage['id'] == 'zero_inventory_and_crew'
            assert after['run']['operators'][OP]['present'] is False
            assert all(record['held'] is False for record in [*after['run']['relics'].values(), *after['run']['tactical_tools'].values()])
            events = [event for event in after['run']['history'] if event['kind'] == 'state_flag_reconfirmed']
            assert len(events) == 4 and all(event['value'] is False for event in events)
            assert not {event['kind'] for event in after['run']['history']}.intersection(
                ('operator_no_longer_present', 'relic_no_longer_held', 'tool_no_longer_held'))
            same(after['run']['resources'], before['run']['resources'], 'negative qualification keeps full raw counter proof')
            for event in events:
                collection = {'operator': 'operators', 'relic': 'relics', 'tactical_tool': 'tactical_tools'}[event['record_kind']]
                same(event['previous_record'], before['run'][collection][event['id']], 'negative qualification complete previous raw record')
        proof.append({'context': context, 'id': stage['id'], 'begin': row['begin'], 'end': row['end'],
                      'original_caller_pure': True, 'whole_account_and_original_bytes_preserved': True})
    return proof


def visible_metric_label(label):
    assert type(label) is str
    for raw, shown in (('DPS/HPS', '每秒伤害 / 每秒治疗'), ('DPS', '每秒伤害'), ('HPS', '每秒治疗')):
        label = label.replace(raw, shown)
    return re.sub(r' (?=每秒伤害|每秒治疗)', '', label).strip()


def contained(rectangle, viewport):
    assert type(rectangle) is tuple and len(rectangle) == 4
    assert type(viewport) is tuple and len(viewport) == 4
    assert all(type(value) is int for value in rectangle + viewport)
    x, y, width, height = rectangle
    vx, vy, vw, vh = viewport
    assert width > 0 and height > 0 and vw > 0 and vh > 0
    assert vx <= x and vy <= y and x + width <= vx + vw and y + height <= vy + vh


def verify_pngs(ledger, receipt, snapshots, references, frozen, output):
    expected = (('unknown-retained-summary.png', 'unknown_string:initial:continuous', 'actual_PNG_bounded_unknown_summary'),
                ('fresh-Snack-damage-report.png', 'unknown_string:popup_A:continuous', 'actual_PNG_bounded_fresh_Snack_report'))
    assert len(receipt['pngs']) == len(expected) == 2
    proof = []
    for row, (name, case, kind) in zip(receipt['pngs'], expected):
        same(row['path'], name, 'exact bounded PNG path')
        assert references[row['snapshot']['path']] == case
        snapshot_record = ledger.get(row['snapshot'], 'actual_window_snapshot')
        visual = ledger.get(row['visual'], kind)
        same(visual['snapshot_ref'], row['snapshot'], 'PNG exact complete native snapshot reference')
        assert visual['context'] == 'unknown_string' and visual['case'] == snapshot_record['case']
        assert ledger.position(row['snapshot']) < ledger.position(row['visual'])
        snapshot = snapshots[case]
        same_projection(visual, {'joint': snapshot['state_and_disks'], 'damage_result': snapshot['damage_result']},
                        ('joint', 'damage_result'), 'PNG complete saved result/current graph cross aliases')
        if kind == 'actual_PNG_bounded_unknown_summary':
            assert visual['phase'] == 'bounded_summary_PNG'
            same(visual['displayed_text'], snapshot['projection']['summary'], 'complete actual unknown run-summary QLabel string')
            assert '在场状态未确认' in visual['displayed_text'] and '持有状态未确认' in visual['displayed_text']
            contained(visual['label_rect'], visual['viewport_rect'])
        else:
            assert visual['phase'] == 'bounded_report_PNG'
            same(visual['displayed_text'], snapshot['displayed_damage'], 'complete actual fresh-Snack displayed report string')
            section = next(item for item in snapshot['damage_result']['result']['report']['sections'] if item['id'] == 'damage')
            assert visual['section'] == 'damage' and visual['title'] == '【' + section['title'] + '】'
            lines = visual['displayed_text'].split('\n')
            assert lines.count(visual['title']) == 1 and section['metrics']
            start = lines.index(visual['title'])
            for offset, metric in enumerate(section['metrics'], 1):
                assert lines[start + offset].startswith(visible_metric_label(metric['label']) + '：')
            same(visual['visible_blocks'], lines[start:start + len(section['metrics']) + 1],
                 'exact consecutive whole damage title through last metric')
            assert len(visual['cursor_rects']) == 2 * len(visual['visible_blocks'])
            for rectangle in visual['cursor_rects']:
                contained(rectangle, visual['viewport_rect'])
        metadata = pin_png(ledger.folder, row, frozen, output / name)
        metadata.update(snapshot=row['snapshot'], visual=row['visual'], bounded_scope_only=True)
        proof.append(metadata)
    return proof


def verify_contexts(ledger, receipt, cases, chronological):
    specs = {item['id']: item for item in cases['contexts']}
    assert [item['id'] for item in receipt['contexts']] == list(specs)
    assert len(receipt['contexts']) == 6
    proof = []
    for item in receipt['contexts']:
        context = item['id']
        initial = ledger.get(item['initial'], 'actual_public_fixture_loaded')
        close = ledger.get(item['close'], 'actual_close_RunState_account_reload')
        assert initial['context'] == close['context'] == context
        assert initial['case'] == 'initial' and initial['phase'] == 'constructor'
        assert close['case'] == 'close' and close['phase'] == 'close_direct_reload'
        assert ledger.position(item['initial']) < ledger.position(item['close'])
        wanted = specs[context]['initial']['recruited']
        assert (OP in initial['initial_ui']['recruited']) is wanted
        assert (OP in initial['initial_ui']['overview_ids']) is wanted
        if not wanted:
            # make_damage_tab keeps the old manual Kal'tsit catalog preview.
            # Exclusion from automatic/recruited choices does not forbid it.
            same(initial['initial_ui']['selected_catalog_operator'], 'kaltsit',
                 'existing manual catalog default when no member is qualified')
        same_reload_notice_only(close, chronological['current'][context])
        proof.append({'context': context, 'initial': item['initial'], 'close': item['close'],
                      'JSON_alias_boundary_independently_derived': True,
                      'existing_notice_only_presentation_transition': True})
    assert len([name for name in ledger.names if ledger.values[name]['kind'] == 'actual_close_RunState_account_reload']) == 6
    return proof


def pin_png(folder, row, frozen, destination):
    assert type(row['path']) is str and Path(row['path']).name == row['path']
    path = Path(folder) / row['path']
    assert path.is_file() and not path.is_symlink()
    raw = path.read_bytes()
    assert type(row['bytes']) is int and len(raw) == row['bytes']
    assert sha(raw) == row['sha256']
    assert raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[12:16] == b'IHDR'
    width, height = struct.unpack('>II', raw[16:24])
    assert width > 0 and height > 0
    frozen[path] = raw
    write_exact(destination, raw)
    return {'path': row['path'], 'bytes': len(raw), 'sha256': sha(raw),
            'width': width, 'height': height, 'pixels_viewed': False}


def repin_every_input(frozen):
    for path, raw in frozen.items():
        assert path.is_file() and not path.is_symlink()
        assert path.read_bytes() == raw, str(path)


def verify_sealed_source_packet(artifact, runner, frozen):
    own_raw = read_pinned(artifact / 'MANIFEST.json', frozen)
    own = json.loads(own_raw)
    assert own['kind'] == 'SEALED_SOURCE_ONLY_SAVED_AUDIT_PROPOSAL'
    assert type(own['section']) is int and own['section'] == 122
    assert own['runtime_executions'] == 0
    entries = own['payloads']
    assert type(entries) is list and entries
    names = [entry['path'] for entry in entries]
    assert len(set(names)) == len(names)
    assert {path.name for path in artifact.iterdir()} == set(names) | {'MANIFEST.json'}
    for entry in entries:
        assert Path(entry['path']).name == entry['path']
        raw = read_pinned(artifact / entry['path'], frozen)
        assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256']
    pins = json.loads(read_pinned(artifact / 'source-pins.json', frozen))
    assert pins['kind'] == 'EXACT_PUBLIC_SOURCE_BINDINGS_NOT_RUNTIME'
    assert pins['section'] == 122 and pins['runtime_executions'] == 0
    assert pins['window_manifest']['sha256'] == WINDOW_MANIFEST_SHA
    assert pins['window_runner']['sha256'] == WINDOW_SHA
    assert pins['window_cases']['sha256'] == CASES_SHA
    assert pins['native_helper']['sha256'] == HELPER_SHA
    assert sha(read_pinned(artifact / 'native_evidence.py', frozen)) == HELPER_SHA
    window_raw = read_pinned(artifact / 'window-MANIFEST.json', frozen)
    assert len(window_raw) == pins['window_manifest']['bytes'] and sha(window_raw) == WINDOW_MANIFEST_SHA
    same(read_pinned(runner.parent / 'MANIFEST.json', frozen), window_raw,
         'actual producer directory exact sealed Source manifest original bytes')
    window = json.loads(window_raw)
    assert window['kind'] == 'SEALED_SOURCE_ONLY_REAL_MAINWINDOW_PROPOSAL'
    assert window['section'] == 122 and window['runtime_executions'] == 0
    for entry in window['payloads']:
        assert Path(entry['path']).name == entry['path']
        raw = read_pinned(runner.parent / entry['path'], frozen)
        assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256']
    runner_raw = read_pinned(runner, frozen)
    assert len(runner_raw) == pins['window_runner']['bytes'] and sha(runner_raw) == WINDOW_SHA
    cases_raw = read_pinned(artifact / 'cases.json', frozen)
    assert len(cases_raw) == pins['window_cases']['bytes'] and sha(cases_raw) == CASES_SHA
    same(cases_raw, read_pinned(runner.parent / 'cases.json', frozen),
         'Saved and actual producer use identical original sealed public cases bytes')
    return pins, json.loads(cases_raw), own_raw, window_raw


def verify_public_game_quotes(root, guard, artifact, pins, frozen):
    contract = json.loads(read_pinned(artifact / 'PUBLIC_GAME_CONTRACT.json', frozen))
    originals = {}
    for entry in pins['public_game_sources']:
        relative = Path(entry['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        raw = read_pinned(root / relative, frozen)
        assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256']
        assert guard['source_sha256'][relative.as_posix()] == entry['sha256']
        originals[relative.name] = json.loads(raw)
    profiles, mechanics = originals['operator-profiles.json'], originals['relic-mechanics.json']
    for name, rank in (('skill3_rank10', 9), ('skill3_rank7', 6)):
        raw = profiles['operators'][OP]['skills'][2]['levels'][rank]
        same({key: raw[key] for key in contract[name]['raw']}, contract[name]['raw'],
             'complete exact public S3 rank data quote ' + name)
    for collection, source in (('recipient_buffs', 'char_buffs'), ('relics', 'relics')):
        for identity, quoted in contract[collection].items():
            same(mechanics[source][identity], quoted, 'complete exact public mechanism quote ' + identity)
    return {'original_public_bytes_bound': True, 'literal_source_quotes_exact': True,
            'new_game_mechanisms_claimed': False}


def main():
    parser = argparse.ArgumentParser()
    for name in ('root', 'guard', 'window', 'window-exit', 'runner', 'out'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--source-count', type=int, required=True)
    args = parser.parse_args()
    artifact = Path(__file__).resolve().parent
    root, folder, out = (Path(value).resolve() for value in (args.root, args.window, args.out))
    guard_path, runner, exit_path = (Path(value).resolve() for value in
                                     (args.guard, args.runner, args.window_exit))
    assert not out.exists() and out not in (root, folder, artifact)
    assert root not in out.parents and folder not in out.parents and artifact not in out.parents
    assert artifact != root and root not in artifact.parents
    frozen = {}
    pins, cases, own_raw, window_source_raw = verify_sealed_source_packet(artifact, runner, frozen)
    contexts = [item['id'] for item in cases['contexts']]
    same(contexts, ['unknown_string', 'unknown_number', 'unknown_null',
                    'true_control', 'false_control', 'missing_control'], 'exact six public contexts')
    assert cases['section'] == 122 and cases['restore_notice'] == NOTICE
    assert cases['modes'] == ['frames', 'continuous']
    guard_raw = read_pinned(guard_path, frozen)
    guard = json.loads(guard_raw)
    validate_guard(root, guard, args.source_count)
    for name in guard['source_additional_sha256']:
        read_pinned(root / name, frozen)
    exit_raw = read_pinned(exit_path, frozen)
    assert exit_raw == b'0\n'
    receipt_raw = read_pinned(folder / 'receipt.json', frozen)
    receipt = json.loads(receipt_raw)
    validate_receipt_common(receipt, guard, guard_raw, args.source_count, contexts, WINDOW_SHA, 900)
    assert receipt['phase'] == 'candidate' and receipt['cases_sha256'] == CASES_SHA
    same(receipt['rank_erratum'], cases['rank_erratum'], 'sealed Source rank-branch clarification')
    assert type(receipt['actual_numeric_calls']) is int and receipt['actual_numeric_calls'] >= 42
    out.mkdir()
    started, done = time.perf_counter(), threading.Event()
    proof = {'kind': 'ROOT_ACTUAL122_RETAINED_PRESENCE_WINDOW_SAVED_AUDIT', 'section': 122,
             'passed': False, 'workflow_complete': False,
             'source_guard_sha256': sha(guard_raw), 'source_count': args.source_count,
             'source_before': guard['source_sha256'],
             'source_additional_before': guard['source_additional_sha256'],
             'auditor_sha256': sha(read_pinned(Path(__file__), frozen)),
             'auditor_source_manifest_sha256': sha(own_raw),
             'window_source_manifest_sha256': sha(window_source_raw),
             'window_runner_sha256': WINDOW_SHA, 'cases_sha256': CASES_SHA,
             'window_receipt_sha256': sha(receipt_raw), 'window_exit_sha256': sha(exit_raw),
             'native_helper_sha256': HELPER_SHA, 'deadline_seconds': SAVED_DEADLINE,
             'no_project_API_formatter_Qt_Wine_reexecution': True,
             'private_state_access': False, 'native_windows_verified': False,
             'game_chat_sampling_executed': False, 'PNG_pixels_viewed_by_this_auditor': False,
             'technical_intermediate_display_independently_saved': False,
             'technical_scope': 'Exact sealed runner and original raw0 bind actual technical/ordinary display assertions; Saved independently checks the complete toggle graph and ordinary displayed string.',
             'reload_scope': 'Derive the complete restart graph from exact persisted JSON and existing constructor order/notice. JSON intentionally breaks live aliases; ordinary native call/result/report graphs still retain every alias.',
             'PNG_scope': 'Only the actual bounded summary QLabel and damage metrics blocks are audited. Root separately inspects original PNG pixels.',
             'source_drift': [], 'snapshots': [], 'ingresses': [], 'close_reloads': [], 'PNGs': []}

    def checkpoint():
        raw = (json.dumps({'kind': proof['kind'], 'section': 122, 'passed': False,
                           'completed_snapshots': len(proof['snapshots']),
                           'completed_ingresses': len(proof['ingresses']),
                           'completed_close_reloads': len(proof['close_reloads']),
                           'completed_PNGs': len(proof['PNGs']),
                           'source_guard_sha256': sha(guard_raw)},
                          ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        path = out / 'checkpoint.json'
        with path.open('wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())

    def timeout():
        if not done.wait(SAVED_DEADLINE):
            raw = b'{"passed":false,"workflow_complete":false,"deadline_seconds":180}\n'
            write_exact(out / 'timeout.json', raw)
            os._exit(124)
    threading.Thread(target=timeout, daemon=True).start()
    try:
        checkpoint()
        proof['public_game_quotes'] = verify_public_game_quotes(root, guard, artifact, pins, frozen)
        ledger = NativeLedger(folder, receipt['records'], contexts, frozen, out / 'native-verified')
        labels = {'actual technical report checkbox', 'actual ordinary report checkbox',
                  'show actual unknown run summary', 'return actual damage report tab',
                  'center bounded fresh-Snack damage metrics'}
        chronological = validate_chronological_joint(ledger, contexts, receipt['ingresses'], labels)
        verify_initial_fixtures(chronological['initial'], cases)
        proof['ingresses'] = verify_ingress_semantics(ledger, receipt, cases)
        checkpoint()
        snapshots, references, proof['snapshots'] = verify_snapshots(ledger, receipt, cases)
        checkpoint()
        proof['close_reloads'] = verify_contexts(ledger, receipt, cases, chronological)
        proof['PNGs'] = verify_pngs(ledger, receipt, snapshots, references, frozen, out)
        checkpoint()
        assert chronological['numeric_count'] == receipt['actual_numeric_calls']
        assert chronological['intentional_bracket_count'] == 13
        assert len(proof['snapshots']) == 42 and len(proof['close_reloads']) == 6 and len(proof['PNGs']) == 2
        kinds = {}
        for name in ledger.names:
            kind = ledger.values[name]['kind']
            kinds[kind] = kinds.get(kind, 0) + 1
        write_exact(out / 'original-window-receipt.json', receipt_raw)
        write_exact(out / 'original-window-exit-code', exit_raw)
        write_exact(out / 'original-source-guard.json', guard_raw)
        write_exact(out / 'original-window-MANIFEST.json', window_source_raw)
        proof.update(passed=True, workflow_complete=True,
                     full_native_records_retained=receipt['records'], record_kinds=kinds,
                     actual_native_records_decoded=len(ledger.names),
                     actual_complete_states=42, actual_fresh_reference_API_records=42,
                     actual_three_formatter_groups=42, actual_complete_formatter_strings=126,
                     actual_complete_close_dual_reloads=6, actual_public_ingresses=13,
                     actual_numeric_calls=chronological['numeric_count'],
                     actual_intentional_reentrant_numeric_calls=chronological['intentional_reentrant_numeric_count'],
                     actual_PNG_hash_intersection_gates=2)
    except BaseException as error:
        proof.update(passed=False, workflow_complete=False,
                     failure={'type': type(error).__name__, 'message': str(error),
                              'traceback': traceback.format_exc()})
    finally:
        try:
            proof['source_after'] = native.source_map(root)
            proof['source_additional_after'] = {
                name: sha(read_pinned(root / name, frozen)) for name in guard['source_additional_sha256']}
            proof['source_drift'] = sorted(name for name in set(guard['source_sha256']) | set(proof['source_after'])
                                          if guard['source_sha256'].get(name) != proof['source_after'].get(name))
            same(proof['source_after'], guard['source_sha256'], 'final whole maintained Source stable')
            same(proof['source_additional_after'], guard['source_additional_sha256'], 'final CORE stable')
            repin_every_input(frozen)
        except BaseException as error:
            proof.update(passed=False, workflow_complete=False,
                         final_input_failure={'type': type(error).__name__, 'message': str(error),
                                              'traceback': traceback.format_exc()})
        proof['elapsed_seconds'] = time.perf_counter() - started
        if proof['elapsed_seconds'] >= SAVED_DEADLINE:
            proof.update(passed=False, workflow_complete=False)
        write_exact(out / 'receipt.json',
                    (json.dumps(proof, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
        done.set()
    print(json.dumps({'passed': proof['passed'], 'states': len(proof['snapshots']),
                      'ingresses': len(proof['ingresses']), 'close_reloads': len(proof['close_reloads'])}))
    return 0 if proof['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
