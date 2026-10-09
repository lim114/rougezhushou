"""Public direct-API resource admission, persistence and consumer contracts.

Constructed inputs exercise an API boundary; they do not assert natural OCR
failures or add integer/timestamp/game-mechanism policy. Root must execute.
"""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
from rouge.relic_counter_semantics import counter_resources
from rouge.run_state import RunState
from tests.test_cache_consumers_101 import native
from tests import test_counter_semantics_054 as counter_fixtures


GOLD_RELIC = 'rogue_6_relic_legacy_60'
ALTAR = 'rogue_6_relic_legacy_103'


class ResourceObservation104Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='public-resource104-')
        self.addCleanup(temporary.cleanup)
        self.file = Path(temporary.name) / 'run.json'

    def load(self, resources=None):
        saved = {'id': 'public-resource104', 'started_at': 0.0, 'last_read': 1.0,
                 'operators': {}, 'relics': {}, 'history': [],
                 'resources': copy.deepcopy(resources or {})}
        raw = (json.dumps(saved, ensure_ascii=False, indent=2) + '\n').encode()
        self.file.write_bytes(raw)
        run = RunState(self.file)
        self.assertFalse(run.preserve_unreadable)
        self.assertEqual(run.state['id'], saved['id'])
        self.assertEqual(self.file.read_bytes(), raw)
        return run

    def observe(self, run, resources, **extra):
        observed = {'operators': [], 'relics': {'ids': [], 'icons': [],
                    'count': None, 'source': 'public-resource104'}, 'resources': resources,
                    **extra}
        before = native(observed)
        at = max(run.state['started_at'], run.state['last_read'] or 0) + 1
        self.assertIs(run.apply(observed, at), True)
        self.assertEqual(native(observed), before)
        return at

    def restart(self, run):
        before = self.file.read_bytes()
        expected = native(run.state['resources'])
        restored = RunState(self.file)
        self.assertFalse(restored.preserve_unreadable)
        self.assertIsNone(restored.save_issue)
        self.assertEqual(restored.state['id'], run.state['id'])
        self.assertEqual(native(restored.state['resources']), expected)
        self.assertEqual(self.file.read_bytes(), before)
        state = native(restored.state)
        text = restored.summary()
        self.assertEqual(native(restored.state), state)
        self.assertEqual(self.file.read_bytes(), before)
        return restored, text

    def old(self, key, value):
        return {key: {'value': value, 'captured_at': 1.0,
                      'source': 'public-previous-resource104',
                      'public_opaque': {'nullable': None, 'negative_zero': -0.0}}}

    def resource_events(self, run):
        return [row for row in run.state['history'] if row.get('kind') == 'resource_updated']

    def test_missing_value_without_previous_fact_never_installs_unrestartable_record(self):
        for key in ('gold', 'parts_count'):
            with self.subTest(key=key):
                run = self.load()
                self.observe(run, {key: {}})
                self.assertNotIn(key, run.state['resources'])
                self.assertEqual(self.resource_events(run), [])
                restored, text = self.restart(run)
                self.assertEqual(restored.calculation_resources(), {})
                self.assertIn('源石锭/零件数尚未确认', text)

    def test_missing_value_keeps_previous_null_or_positive_fact_and_original_time(self):
        for key in ('gold', 'parts_count'):
            for value in (None, 8):
                with self.subTest(key=key, value=value):
                    old = self.old(key, value)
                    run = self.load(old)
                    self.observe(run, {key: {}})
                    self.assertEqual(native(run.state['resources']), native(old))
                    self.assertEqual(self.resource_events(run), [])
                    self.assertEqual(run.state['resources'][key]['captured_at'], 1.0)
                    restored, _ = self.restart(run)
                    self.assertEqual(native(restored.calculation_resources()[key]), native(old[key]))

    def test_malformed_records_preserve_old_fact_without_erasing_or_synthesizing_zero(self):
        for key in ('gold', 'parts_count'):
            for bad in (None, [], 'public', 8, False):
                with self.subTest(key=key, bad=repr(bad)):
                    old = self.old(key, 8)
                    run = self.load(old)
                    self.observe(run, {key: bad})
                    self.assertEqual(native(run.state['resources']), native(old))
                    self.assertEqual(self.resource_events(run), [])
                    self.restart(run)

    def test_malformed_resource_containers_mean_unread_field_and_keep_both_old_times(self):
        for bad in (None, [], 'public', 8, False):
            with self.subTest(bad=repr(bad)):
                old = {**self.old('gold', 8), **self.old('parts_count', 3)}
                run = self.load(old)
                self.observe(run, bad)
                self.assertEqual(native(run.state['resources']), native(old))
                self.assertEqual(self.resource_events(run), [])
                self.restart(run)

    def test_wellformed_peer_and_configuration_are_saved_while_bad_record_is_unread(self):
        run = self.load(self.old('gold', 8))
        at = self.observe(run, {'gold': {}, 'parts_count': {'value': 3, 'capacity': 12}},
                          config={'difficulty': {'value': 2, 'source': 'public-peer104'}})
        self.assertEqual(run.state['resources']['gold']['value'], 8)
        self.assertEqual(run.state['resources']['gold']['captured_at'], 1.0)
        self.assertEqual(run.state['resources']['parts_count'],
                         {'value': 3, 'capacity': 12, 'captured_at': at})
        self.assertEqual(run.state['config']['difficulty']['value'], 2)
        self.assertEqual([(r['resource'], r['value']) for r in self.resource_events(run)],
                         [('parts_count', 3)])
        restored, _ = self.restart(run)
        self.assertEqual(restored.state['config']['difficulty'], run.state['config']['difficulty'])

    def test_zero_remains_confirmed_and_unread_or_missing_pages_keep_exact_zero_timestamp(self):
        run = self.load()
        at = self.observe(run, {'gold': {'value': 0}, 'parts_count': {'value': 0, 'capacity': 12}})
        zero = copy.deepcopy(run.state['resources'])
        self.observe(run, {})
        self.observe(run, {'gold': {}, 'parts_count': None})
        self.assertEqual(native(run.state['resources']), native(zero))
        self.assertEqual([r['value'] for r in self.resource_events(run)], [0, 0])
        self.assertEqual(run.state['resources']['gold']['captured_at'], at)
        self.assertEqual(run.state['resources']['parts_count']['captured_at'], at)
        self.restart(run)

    def test_complete_legacy_value_types_keep_existing_format_and_restart_contract(self):
        for key in ('gold', 'parts_count'):
            for value in (0, 8, 8.0, None, True, False, '8', -1, [], {}):
                with self.subTest(key=key, value=repr(value)):
                    run = self.load()
                    record = {'value': value, 'source': None,
                              'public_opaque': {'nullable': None, 'signed': -0.0}}
                    self.observe(run, {key: record})
                    self.assertEqual(native(run.state['resources'][key]['value']), native(value))
                    self.assertEqual(native(run.state['resources'][key]['public_opaque']),
                                     native(record['public_opaque']))
                    self.assertIsNone(run.state['resources'][key]['source'])
                    restored, text = self.restart(run)
                    self.assertIn(str(value), text)
                    self.assertEqual(native(restored.calculation_resources()[key]['value']), native(value))

    def test_saved_boolean_resource_times_are_not_redefined_by_fresh_admission(self):
        for at in (False, True):
            with self.subTest(at=at):
                old = self.old('gold', 8)
                old['gold']['captured_at'] = at
                run = self.load(old)
                self.observe(run, {'gold': {}})
                self.assertIs(run.state['resources']['gold']['captured_at'], at)
                restored, _ = self.restart(run)
                self.assertIs(restored.state['resources']['gold']['captured_at'], at)

    def test_unknown_keys_do_not_bypass_existing_counter_provenance(self):
        for bad in (None, {}, {'value': 8}, {'value': 8, 'source': 'held_card_counter'}):
            with self.subTest(bad=repr(bad)):
                run = self.load()
                self.observe(run, {'public_counter104': bad, 'gold': {'value': 8}})
                self.assertNotIn('public_counter104', run.state['resources'])
                self.assertEqual(run.state['resources']['gold']['value'], 8)
                self.restart(run)

    def test_existing_held_counter_proof_survives_unread_record_with_original_time(self):
        run = self.load()
        proof = counter_fixtures.CounterSemanticsTests().proof(ALTAR, 1)
        resources = counter_resources([proof])
        observed = {'operators': [], 'relics': {'ids': [ALTAR], 'icons': [],
                    'count': None, 'source': 'held_bar'}, 'resources': resources}
        before = native(observed)
        at = self.observe(run, resources, relics=observed['relics'])
        self.assertEqual(native(observed), before)
        first = copy.deepcopy(run.state['resources']['altar_stacks'])
        self.assertEqual(run.calculation_resources()['altar_stacks']['value'], 1)
        self.observe(run, {'altar_stacks': {}})
        self.assertEqual(native(run.state['resources']['altar_stacks']), native(first))
        self.assertEqual(run.state['resources']['altar_stacks']['captured_at'], at)
        restored, _ = self.restart(run)
        self.assertEqual(restored.calculation_resources()['altar_stacks']['value'], 1)

    def test_missing_resource_preserves_existing_real_numeric_result_and_all_three_reports(self):
        run = self.load()
        self.observe(run, {'gold': {'value': 25}})
        def calculate():
            scenario = {'operator': 'mechanist', 'skill': 3, 'relic_ids': [GOLD_RELIC],
                        'relic_context': {'gold': run.calculation_resources()['gold']['value']}}
            original = native(scenario)
            result = calculate_damage(scenario)
            self.assertEqual(native(scenario), original)
            return result, (format_estimate(result), format_report(result),
                            format_report(result, technical=True))
        before, texts = calculate()
        self.assertEqual(before['estimate']['base_stats']['attack_speed'], 135)
        self.observe(run, {'gold': {}})
        after, later_texts = calculate()
        self.assertEqual(native(after), native(before))
        self.assertEqual(later_texts, texts)
        run, _ = self.restart(run)
        restarted, restarted_texts = calculate()
        self.assertEqual(native(restarted), native(before))
        self.assertEqual(restarted_texts, texts)

    def test_complete_record_metadata_aliases_keep_original_memory_and_json_policy(self):
        shared = {'public': [None, -0.0]}
        run = self.load()
        record = {'value': 8, 'public_left': shared, 'public_right': shared}
        self.observe(run, {'gold': record})
        stored = run.state['resources']['gold']
        self.assertIs(stored['public_left'], stored['public_right'])
        self.assertIs(record['public_left'], record['public_right'])
        raw = self.file.read_bytes()
        saved = json.loads(raw)
        self.assertEqual(saved['resources']['gold']['public_left'], shared)
        self.assertEqual(saved['resources']['gold']['public_right'], shared)
        restored = RunState(self.file)
        self.assertFalse(restored.preserve_unreadable)
        restored_record = restored.state['resources']['gold']
        self.assertEqual(restored_record['public_left'], shared)
        self.assertEqual(restored_record['public_right'], shared)
        self.assertIsNot(restored_record['public_left'], restored_record['public_right'])
        self.assertEqual(self.file.read_bytes(), raw)
        restored.summary()

    def test_unused_opaque_caller_aliases_and_cycles_are_not_washed_or_mutated(self):
        shared = {'public': [None, -0.0]}
        cycle = []
        cycle.append(cycle)
        opaque = {'left': shared, 'right': shared, 'cycle': cycle}
        run = self.load()
        self.observe(run, {'gold': {'value': 8}}, public_opaque=opaque)
        self.assertIs(opaque['left'], opaque['right'])
        self.assertIs(opaque['cycle'][0], opaque['cycle'])
        self.assertNotIn('public_opaque', run.state)
        self.restart(run)

    def test_complete_resource_opaque_cycle_keeps_original_save_exception_and_old_bytes(self):
        run = self.load()
        original = self.file.read_bytes()
        temporary = self.file.with_suffix('.tmp')
        temporary.write_bytes(b'public-existing-temporary104\n')
        cycle = []
        cycle.append(cycle)
        observed = {'resources': {'gold': {'value': 8, 'public_cycle': cycle}}}
        caller = native(observed)
        with self.assertRaisesRegex(ValueError, 'Circular reference'):
            run.apply(observed, 2.0)
        self.assertEqual(native(observed), caller)
        stored_cycle = run.state['resources']['gold']['public_cycle']
        self.assertIs(stored_cycle[0], stored_cycle)
        self.assertEqual(self.file.read_bytes(), original)
        self.assertEqual(temporary.read_bytes(), b'public-existing-temporary104\n')
        self.assertIsNone(run.save_issue)
        restored = RunState(self.file)
        self.assertFalse(restored.preserve_unreadable)
        self.assertEqual(restored.state['resources'], {})

    def test_actual_failed_io_keeps_memory_scope_and_does_not_clear_save_issue_on_bad_read(self):
        run = self.load()
        original = self.file.read_bytes()
        temporary = self.file.with_suffix('.tmp')
        temporary.mkdir()
        marker = temporary / 'public-marker'
        marker.write_bytes(b'public-nonempty-directory104')
        self.observe(run, {'gold': {'value': 8}})
        issue = copy.deepcopy(run.save_issue)
        self.assertIsNotNone(issue)
        old = copy.deepcopy(run.state['resources']['gold'])
        self.observe(run, {'gold': {}})
        self.assertEqual(run.save_issue, issue)
        self.assertEqual(native(run.state['resources']['gold']), native(old))
        self.assertEqual(self.file.read_bytes(), original)
        self.assertEqual(marker.read_bytes(), b'public-nonempty-directory104')
        self.assertIn('仅在当前运行有效', run.summary())
        restored = RunState(self.file)
        self.assertFalse(restored.preserve_unreadable)
        self.assertEqual(restored.state['resources'], {})


if __name__ == '__main__':
    unittest.main()
