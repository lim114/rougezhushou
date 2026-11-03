"""Public temporary-run persistence contracts; Source proposal, not a receipt.

The author has not imported or executed RunState, this test module, or codecs.
Root must apply to the actually completed 098 source and validate freshly.
"""
from contextlib import ExitStack
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rouge.run_state import RunState


RELIC = 'rogue_6_relic_cargo_1'
OTHER_RELIC = 'rogue_6_relic_fight_26'


def observation(identity=RELIC):
    return {'operators': [],
            'relics': {'ids': [identity], 'count': 1, 'source': 'held_bar',
                       'icons': [{'id': identity, 'candidates': [identity],
                                  'confirmed': True}]}}


class RunPersistenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='public-run-persistence-')
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.sequence = 0

    def path(self):
        self.sequence += 1
        return self.folder / ('public-%d.json' % self.sequence)

    def seed(self):
        run = RunState(self.path())
        self.assertIs(run.apply(observation(), run.state['started_at'] + 1), True)
        self.assertIsNone(run.save_issue)
        self.assertFalse(run.preserve_unreadable)
        return run

    def apply_next(self, run, identity=OTHER_RELIC):
        incoming = observation(identity)
        caller = deepcopy(incoming)
        at = max(run.state['started_at'], run.state['last_read'] or 0) + 1
        self.assertIs(run.apply(incoming, at), True)
        self.assertEqual(incoming, caller)
        self.assertEqual(run.state['last_read'], at)
        self.assertEqual(run.held_relic_ids(), [identity])
        return at

    def assert_failed(self, run):
        self.assertIsNotNone(run.save_issue)
        self.assertFalse(run.preserve_unreadable)
        text = run.summary()
        self.assertIn('保存未完成', text)
        self.assertIn('仅在当前运行有效', text)
        self.assertIn('可能恢复磁盘中较早的记录', text)
        self.assertIn('不会再次写入或覆盖本局记录', text)
        self.assertNotIn('原本局记录无法读取', text)
        self.assertNotIn('原文件已保留', text)
        self.assertNotIn('持续累积并保存', text)

    def assert_disk_matches(self, run):
        self.assertEqual(json.loads(run.file.read_text(encoding='utf-8')), run.state)
        self.assertFalse(run.file.with_suffix('.tmp').exists())
        self.assertIsNone(run.save_issue)
        self.assertFalse(run.preserve_unreadable)

    def test_ordinary_unicode_preserves_platform_writer_and_healthy_restart(self):
        run = self.seed()
        run.state['public_opaque'] = {'name': '中文', 'emoji': '\U0001f642',
                                    'literal': '\\ud800', 'typed': [None, False, 0, -0.0]}
        self.assertIs(run.save(), True)
        reference = self.folder / 'platform-writer.json'
        reference.write_text(json.dumps(run.state, ensure_ascii=False, indent=2),
                             encoding='utf-8')
        self.assertEqual(run.file.read_bytes(), reference.read_bytes())
        self.assert_disk_matches(run)
        before = deepcopy(run.state)
        restarted = RunState(run.file)
        self.assertEqual(restarted.state['id'], before['id'])
        self.assertEqual(restarted.state['history'], before['history'])
        self.assertEqual(restarted.state['public_opaque'], before['public_opaque'])
        self.assertEqual(restarted.held_relic_ids(), [RELIC])
        self.assertIsNone(restarted.save_issue)
        self.assertIn('已恢复同一局的记忆', restarted.summary())

    def test_loaded_lone_surrogate_keys_and_values_keep_exact_decoded_points(self):
        for point in ('\ud800', '\udbff', '\udc00', '\udfff'):
            for role in ('key', 'value'):
                with self.subTest(point=hex(ord(point)), role=role):
                    path = self.path()
                    opaque = {point: 'public'} if role == 'key' else {'public': point}
                    path.write_bytes(json.dumps({'operators': {}, 'relics': {},
                                                 'public_opaque': opaque},
                                                ensure_ascii=True).encode('ascii'))
                    run = RunState(path)
                    self.apply_next(run)
                    self.assert_disk_matches(run)
                    restarted = RunState(path)
                    self.assertEqual(restarted.state['public_opaque'], opaque)
                    value = (next(iter(restarted.state['public_opaque']))
                             if role == 'key' else restarted.state['public_opaque']['public'])
                    self.assertEqual([ord(c) for c in value], [ord(point)])

    def test_native_nonadjacent_surrogates_and_literal_escapes_remain_distinct(self):
        for value in ('\ud800', '\udc00', '\ud800x\udc00', '\udc00\ud800',
                      '\\ud800\\udc00', '\U00010000'):
            with self.subTest(points=[hex(ord(c)) for c in value]):
                run = self.seed()
                run.state['public_opaque'] = value
                self.apply_next(run)
                self.assert_disk_matches(run)
                self.assertEqual(RunState(run.file).state['public_opaque'], value)

    def test_ascii_escaped_pair_loads_as_scalar_and_saves_normally(self):
        path = self.path()
        path.write_bytes(b'{"operators":{},"relics":{},"public_opaque":"\\ud83d\\ude42"}')
        run = RunState(path)
        self.assertEqual(run.state['public_opaque'], '\U0001f642')
        self.apply_next(run)
        self.assert_disk_matches(run)
        self.assertEqual(RunState(path).state['public_opaque'], '\U0001f642')

    def test_native_adjacent_pair_refuses_before_io_and_keeps_accepted_memory(self):
        for value in ('\ud800\udc00', '\udbff\udfff'):
            for role in ('key', 'value'):
                with self.subTest(points=[hex(ord(c)) for c in value], role=role):
                    run = self.seed()
                    original = run.file.read_bytes()
                    pending = run.file.with_suffix('.tmp')
                    pending.write_bytes(b'public-existing-temporary')
                    opaque = {value: 'public'} if role == 'key' else {'public': value}
                    run.state['public_opaque'] = opaque
                    identity = run.state['id']
                    with ExitStack() as stack:
                        spies = [stack.enter_context(patch.object(Path, name))
                                 for name in ('mkdir', 'write_text', 'replace')]
                        self.apply_next(run)
                        for spy in spies:
                            spy.assert_not_called()
                    self.assertEqual(run.state['id'], identity)
                    self.assertEqual(run.state['public_opaque'], opaque)
                    self.assertEqual(run.file.read_bytes(), original)
                    self.assertEqual(pending.read_bytes(), b'public-existing-temporary')
                    self.assert_failed(run)
                    self.assertIn('无法无损保存', run.summary())

    def test_pair_refusal_of_absent_target_does_not_create_parent(self):
        path = self.folder / 'not-created' / 'run.json'
        run = RunState(path)
        run.state['public_opaque'] = '\ud800\udc00'
        self.apply_next(run)
        self.assertFalse(path.parent.exists())
        self.assertFalse(path.exists())
        self.assert_failed(run)

    def test_serialization_errors_precede_io_and_do_not_claim_io_failure(self):
        for kind in ('object', 'cycle', 'object_with_pair'):
            with self.subTest(kind=kind):
                run = self.seed()
                original = run.file.read_bytes()
                pending = run.file.with_suffix('.tmp')
                pending.write_bytes(b'public-existing-temporary')
                if kind == 'cycle':
                    value = []
                    value.append(value)
                    run.state['public_opaque'] = value
                    error = ValueError
                else:
                    run.state['public_opaque'] = object()
                    if kind == 'object_with_pair':
                        run.state['public_pair'] = '\ud800\udc00'
                    error = TypeError
                before = run.state['id']
                with ExitStack() as stack:
                    spies = [stack.enter_context(patch.object(Path, name,
                              side_effect=PermissionError('public IO denied')))
                             for name in ('mkdir', 'write_text', 'replace')]
                    with self.assertRaises(error):
                        run.save()
                    for spy in spies:
                        spy.assert_not_called()
                self.assertIsNone(run.save_issue)
                self.assertFalse(run.preserve_unreadable)
                self.assertEqual(run.state['id'], before)
                self.assertEqual(run.file.read_bytes(), original)
                self.assertEqual(pending.read_bytes(), b'public-existing-temporary')

    def test_non_io_program_errors_are_not_mislabeled_or_swallowed(self):
        for stage in ('mkdir', 'write_text', 'replace'):
            for error in (RuntimeError('public program error'), ValueError('public value error')):
                with self.subTest(stage=stage, error=type(error).__name__):
                    run = self.seed()
                    original = run.file.read_bytes()
                    identity = run.state['id']
                    with patch.object(Path, stage, side_effect=error):
                        with self.assertRaises(type(error)):
                            run.apply(observation(OTHER_RELIC), run.state['last_read'] + 1)
                    self.assertIsNone(run.save_issue)
                    self.assertFalse(run.preserve_unreadable)
                    self.assertEqual(run.state['id'], identity)
                    self.assertEqual(run.held_relic_ids(), [OTHER_RELIC])
                    self.assertEqual(run.file.read_bytes(), original)

    def test_oserror_at_each_stage_keeps_target_memory_and_stop_order(self):
        for stage in ('mkdir', 'write_text', 'replace'):
            for error in (PermissionError('public denied'), OSError('public IO error'),
                          FileExistsError('public conflict')):
                with self.subTest(stage=stage, error=type(error).__name__):
                    run = self.seed()
                    original = run.file.read_bytes()
                    identity = run.state['id']
                    old_write = Path.write_text
                    old_replace = Path.replace
                    with ExitStack() as stack:
                        failing = stack.enter_context(patch.object(Path, stage, side_effect=error))
                        after_write = (stack.enter_context(patch.object(Path, 'write_text',
                                       autospec=True, side_effect=old_write))
                                       if stage == 'mkdir' else None)
                        after_replace = (stack.enter_context(patch.object(Path, 'replace',
                                         autospec=True, side_effect=old_replace))
                                         if stage != 'replace' else None)
                        self.apply_next(run)
                        failing.assert_called_once()
                        if after_write is not None:after_write.assert_not_called()
                        if after_replace is not None:after_replace.assert_not_called()
                    self.assertEqual(run.state['id'], identity)
                    self.assertEqual(run.file.read_bytes(), original)
                    self.assert_failed(run)

    def test_partial_write_evidence_is_neither_deleted_nor_published(self):
        run = self.seed()
        original = run.file.read_bytes()
        pending = run.file.with_suffix('.tmp')
        old_write = Path.write_text

        def interrupted(file, text, *args, **kwargs):
            if file == pending:
                file.write_bytes(b'public-partial-write')
                raise OSError('public interrupted write')
            return old_write(file, text, *args, **kwargs)

        with patch.object(Path, 'write_text', new=interrupted):
            self.apply_next(run)
        self.assertEqual(run.file.read_bytes(), original)
        self.assertEqual(pending.read_bytes(), b'public-partial-write')
        self.assert_failed(run)
        before = deepcopy(run.state)
        self.assertIs(run.save(), False)
        self.assertEqual(run.state, before)
        self.assertEqual(pending.read_bytes(), b'public-partial-write')

    def test_replace_failure_retains_complete_temp_distinct_from_final_target(self):
        run = self.seed()
        original = run.file.read_bytes()
        with patch.object(Path, 'replace', side_effect=PermissionError('public replace denied')):
            self.apply_next(run)
        pending = run.file.with_suffix('.tmp')
        self.assertEqual(run.file.read_bytes(), original)
        self.assertEqual(json.loads(pending.read_text(encoding='utf-8')), run.state)
        self.assert_failed(run)
        pending_raw = pending.read_bytes()
        self.apply_next(run, RELIC)
        self.assertEqual(run.file.read_bytes(), original)
        self.assertEqual(pending.read_bytes(), pending_raw)
        restarted = RunState(run.file)
        self.assertEqual(restarted.held_relic_ids(), [RELIC])
        self.assertIsNone(restarted.save_issue)
        self.assertFalse(restarted.preserve_unreadable)
        self.assertEqual(pending.read_bytes(), pending_raw)

    def test_actual_open_failure_keeps_nonempty_temp_directory_and_healthy_old_restart(self):
        run = self.seed()
        original = run.file.read_bytes()
        original_id = run.state['id']
        pending = run.file.with_suffix('.tmp')
        pending.mkdir()
        sentinel = pending / 'public-sentinel'
        sentinel.write_bytes(b'public-open-failure-evidence')
        self.apply_next(run)
        self.assertEqual(run.file.read_bytes(), original)
        self.assertEqual(run.state['id'], original_id)
        self.assertEqual(sentinel.read_bytes(), b'public-open-failure-evidence')
        self.assertEqual(list(pending.iterdir()), [sentinel])
        self.assert_failed(run)
        restarted = RunState(run.file)
        self.assertEqual(restarted.state['id'], original_id)
        self.assertEqual(restarted.held_relic_ids(), [RELIC])
        self.assertIsNone(restarted.save_issue)
        self.assertFalse(restarted.preserve_unreadable)
        self.assertEqual(run.file.read_bytes(), original)
        self.assertEqual(sentinel.read_bytes(), b'public-open-failure-evidence')

    def test_absent_target_io_failure_does_not_invent_saved_original(self):
        run = RunState(self.path())
        with patch.object(Path, 'mkdir', side_effect=PermissionError('public mkdir denied')):
            self.apply_next(run)
        self.assertFalse(run.file.exists())
        self.assertFalse(run.file.with_suffix('.tmp').exists())
        self.assert_failed(run)

    def test_failed_session_keeps_accepting_current_run_without_automatic_retry(self):
        run = self.seed()
        original = run.file.read_bytes()
        identity = run.state['id']
        with patch.object(Path, 'replace', side_effect=OSError('public replace denied')):
            first_at = self.apply_next(run)
        pending_raw = run.file.with_suffix('.tmp').read_bytes()
        history = deepcopy(run.state['history'])
        with ExitStack() as stack:
            spies = [stack.enter_context(patch.object(Path, name))
                     for name in ('mkdir', 'write_text', 'replace')]
            second_at = self.apply_next(run, RELIC)
            third_at = self.apply_next(run, OTHER_RELIC)
            self.assertIs(run.save(), False)
            for spy in spies:spy.assert_not_called()
        self.assertEqual(run.state['id'], identity)
        self.assertLess(first_at, second_at)
        self.assertLess(second_at, third_at)
        self.assertEqual(run.state['history'][:len(history)], history)
        self.assertEqual(run.file.read_bytes(), original)
        self.assertEqual(run.file.with_suffix('.tmp').read_bytes(), pending_raw)
        self.assert_failed(run)

    def test_manual_reset_after_save_failure_clears_memory_without_retry_or_rollback(self):
        run = self.seed()
        other = self.seed()
        original = run.file.read_bytes()
        other_original = other.file.read_bytes()
        with patch.object(Path, 'replace', side_effect=OSError('public replace denied')):
            self.apply_next(run)
        pending_raw = run.file.with_suffix('.tmp').read_bytes()
        previous_id = run.state['id']
        issue = run.save_issue
        with ExitStack() as stack:
            spies = [stack.enter_context(patch.object(Path, name))
                     for name in ('mkdir', 'write_text', 'replace')]
            run.reset()  # Explicit manual action in this public temporary fixture.
            for spy in spies:spy.assert_not_called()
        self.assertNotEqual(run.state['id'], previous_id)
        self.assertEqual(run.state['operators'], {})
        self.assertEqual(run.state['relics'], {})
        self.assertEqual(run.state['maps'], {})
        self.assertEqual(run.state['history'], [])
        self.assertIsNone(run.state['last_read'])
        self.assertEqual(run.save_issue, issue)
        self.assertFalse(run.preserve_unreadable)
        self.assertEqual(run.file.read_bytes(), original)
        self.assertEqual(run.file.with_suffix('.tmp').read_bytes(), pending_raw)
        self.assertEqual(other.file.read_bytes(), other_original)
        self.assert_failed(run)
        new_id = run.state['id']
        self.apply_next(run)
        self.assertEqual(run.state['id'], new_id)
        self.assertEqual(run.file.read_bytes(), original)

    def test_io_failure_during_first_manual_reset_keeps_new_run_in_memory(self):
        run = self.seed()
        original = run.file.read_bytes()
        old_id = run.state['id']
        with patch.object(Path, 'write_text', side_effect=OSError('public write denied')):
            run.reset()
        self.assertNotEqual(run.state['id'], old_id)
        self.assertEqual(run.state['history'], [])
        self.assertEqual(run.held_relic_ids(), [])
        self.assertEqual(run.file.read_bytes(), original)
        self.assert_failed(run)
        restarted = RunState(run.file)
        self.assertEqual(restarted.state['id'], old_id)
        self.assertEqual(restarted.held_relic_ids(), [RELIC])
        self.assertIsNone(restarted.save_issue)

    def test_healthy_manual_reset_still_persists_new_id_and_leaves_other_file_alone(self):
        run = self.seed()
        other = self.seed()
        other_original = other.file.read_bytes()
        old_id = run.state['id']
        run.reset()
        self.assertNotEqual(run.state['id'], old_id)
        self.assertEqual(run.state['history'], [])
        self.assertEqual(run.held_relic_ids(), [])
        self.assert_disk_matches(run)
        restarted = RunState(run.file)
        self.assertEqual(restarted.state['id'], run.state['id'])
        self.assertEqual(restarted.held_relic_ids(), [])
        self.assertEqual(other.file.read_bytes(), other_original)

    def test_load_corruption_remains_distinct_and_manual_reset_retains_old_contract(self):
        for raw in (b'{', b'\xff', b'{"operators":{},"relics":{},"maps":[]}'):
            with self.subTest(raw=raw):
                path = self.path()
                path.write_bytes(raw)
                run = RunState(path)
                self.assertTrue(run.preserve_unreadable)
                self.assertIsNone(run.save_issue)
                self.apply_next(run)
                self.assertEqual(path.read_bytes(), raw)
                self.assertIn('原本局记录无法读取', run.summary())
                self.assertNotIn('保存未完成', run.summary())
                old_id = run.state['id']
                run.reset()
                self.assertNotEqual(run.state['id'], old_id)
                self.assertFalse(run.preserve_unreadable)
                self.assertIsNone(run.save_issue)
                self.assert_disk_matches(run)

    def test_existing_load_guard_precedes_serializer_and_new_io(self):
        path = self.path()
        path.write_bytes(b'{')
        run = RunState(path)
        run.state['public_non_json'] = object()
        pending = path.with_suffix('.tmp')
        pending.write_bytes(b'public-existing-temporary')
        with ExitStack() as stack:
            spies = [stack.enter_context(patch.object(Path, name))
                     for name in ('mkdir', 'write_text', 'replace')]
            self.assertIs(run.save(), False)
            for spy in spies:spy.assert_not_called()
        self.assertTrue(run.preserve_unreadable)
        self.assertIsNone(run.save_issue)
        self.assertEqual(path.read_bytes(), b'{')
        self.assertEqual(pending.read_bytes(), b'public-existing-temporary')

    def test_restart_repair_write_failure_is_not_misreported_as_load_corruption(self):
        run = self.seed()
        original = run.file.read_bytes()
        identity = run.state['id']

        def qualified_repair(target):
            # Isolate constructor repair→save classification. The real repair
            # evidence and numerical behavior remain in origin_discovery tests.
            target.state['public_constructor_repair'] = {'source': 'public-test-control'}
            return True

        with patch.object(RunState, 'restore_origin_discovery_buffs', new=qualified_repair):
            with patch.object(Path, 'replace', side_effect=OSError('public replacement denied')):
                restarted = RunState(run.file)
        self.assertEqual(restarted.state['id'], identity)
        self.assertEqual(restarted.held_relic_ids(), [RELIC])
        self.assertEqual(restarted.state['public_constructor_repair'],
                         {'source': 'public-test-control'})
        self.assertEqual(restarted.file.read_bytes(), original)
        self.assertEqual(json.loads(restarted.file.with_suffix('.tmp').read_text(encoding='utf-8')),
                         restarted.state)
        self.assertIn('已恢复同一局的记忆', restarted.summary())
        self.assert_failed(restarted)

    def test_non_io_error_in_restart_repair_save_escapes_read_error_handler(self):
        run = self.seed()
        original = run.file.read_bytes()

        def qualified_repair(target):
            target.state['public_constructor_repair'] = {'source': 'public-test-control'}
            return True

        with patch.object(RunState, 'restore_origin_discovery_buffs', new=qualified_repair):
            with patch.object(Path, 'write_text', side_effect=ValueError('public program error')):
                with self.assertRaisesRegex(ValueError, 'public program error'):
                    RunState(run.file)
        self.assertEqual(run.file.read_bytes(), original)

