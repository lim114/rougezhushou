"""Future102 Source proposal: real RunState API, temporary owned JSON only.

Not executed by the Source author; this file is not an actual validation receipt.
"""
from copy import deepcopy
import json
from pathlib import Path
import struct
import tempfile
import unittest

from rouge.run_state import RunState


RELICS = ('rogue_6_relic_cargo_1', 'rogue_6_relic_fight_26')
TOOL = 'rogue_6_active_tool_5'


def icon(identity):
    return {'id': identity, 'candidates': [identity], 'confirmed': True}


def caller_receipt(value):
    """Keep original types, float bits, aliases and cycles in caller evidence."""
    seen = {}

    def visit(item):
        kind = type(item)
        if kind in (dict, list, tuple):
            identity = id(item)
            if identity in seen:
                return ('ref', kind.__name__, identity, seen[identity])
            label = len(seen)
            seen[identity] = label
            children = (tuple((visit(k), visit(v)) for k, v in item.items())
                        if kind is dict else tuple(visit(v) for v in item))
            return (kind.__name__, identity, label, children)
        if kind is float:
            return ('float', struct.pack('>d', item))
        return (kind.__name__, item)

    return visit(value)


class InventoryConfirmation102Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='public-inventory102-')
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.sequence = 0

    def load(self, flag, *, count=0, relics=(), tools=()):
        self.sequence += 1
        path = self.directory / (str(self.sequence) + '.json')
        saved = {'id': 'public-confirmation102-' + str(self.sequence),
                 'started_at': 1000.0, 'last_read': 1000.0,
                 'operators': {},
                 'relics': {rid: {'held': True, 'source': 'held_bar',
                                  'captured_at': 1000.0} for rid in relics},
                 'tactical_tools': {tid: {'held': True, 'source': 'held_bar',
                                         'captured_at': 1000.0} for tid in tools},
                 'relic_count': count, 'inventory_verified': deepcopy(flag),
                 'inventory_confirmed_at': None,
                 'public_opaque': {'nullable': None, 'ordered': ['b', 'a'],
                                   'signed_zero': -0.0}}
        raw = (json.dumps(saved, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        path.write_bytes(raw)
        run = RunState(path)
        self.assertIs(run.preserve_unreadable, False)
        self.assertIsNone(run.save_issue)
        self.assertEqual(path.read_bytes(), raw)
        self.assertFalse(path.with_suffix('.tmp').exists())
        return run, raw

    def unchanged_query(self, run, raw):
        before = deepcopy(run.state)
        status = run.inventory_status()
        summary = run.summary()
        self.assertEqual(run.state, before)
        self.assertEqual(run.file.read_bytes(), raw)
        self.assertFalse(run.file.with_suffix('.tmp').exists())
        return status, summary

    def observed(self, *, count=None, ids=(), tools=(), full=False):
        result = {'relics': {'ids': list(ids), 'icons': [], 'count': count,
                             'source': 'held_bar'}, 'operators': []}
        if full:
            result['relics']['icons'] = [icon(i) for i in (*ids, *tools)]
        if tools:
            result['tactical_tools'] = {'ids': list(tools), 'source': 'held_bar'}
        shared = [None, False, 0, -0.0, ('public', 1), b'public']
        cycle = []
        cycle.append(cycle)
        result['public_opaque'] = {'first': shared, 'same': shared, 'cycle': cycle,
                                   'members_alias': result['operators']}
        return result

    def test_text_flags_cannot_claim_complete_and_keep_original_raw_evidence(self):
        for flag in ('false', 'true', '0', '1', 'yes'):
            with self.subTest(flag=flag):
                run, raw = self.load(flag)
                status, summary = self.unchanged_query(run, raw)
                self.assertIs(status['complete'], False)
                self.assertEqual(run.state['inventory_verified'], flag)
                self.assertIs(type(run.state['inventory_verified']), str)
                self.assertNotIn('持有清单已核对（本局记录）', summary)
                self.assertIn('变更待核对或尚未读全', summary)

    def test_container_flags_cannot_claim_complete_or_install_their_contents(self):
        for flag in ([1], {'confirmed': True}, [[False]], {'count': 0}):
            with self.subTest(flag=flag):
                run, raw = self.load(flag)
                status, _ = self.unchanged_query(run, raw)
                self.assertIs(status['complete'], False)
                self.assertEqual(run.state['inventory_verified'], flag)
                self.assertIs(type(run.state['inventory_verified']), type(flag))
                self.assertEqual(run.state['relics'], {})
                self.assertEqual(run.state['tactical_tools'], {})

    def test_empty_invalid_flags_are_false_but_remain_saved_native_values(self):
        for flag in ('', [], {}):
            with self.subTest(flag=flag):
                run, raw = self.load(flag)
                status, _ = self.unchanged_query(run, raw)
                self.assertIs(status['complete'], False)
                self.assertEqual(run.state['inventory_verified'], flag)
                self.assertIs(type(run.state['inventory_verified']), type(flag))

    def test_actual_legacy_bool_int_and_none_short_circuit_types_are_preserved(self):
        cases = ((True, True), (False, False), (None, None), (1, True), (0, 0))
        for flag, expected in cases:
            with self.subTest(flag=flag, native_type=type(flag).__name__):
                run, raw = self.load(flag)
                status, _ = self.unchanged_query(run, raw)
                self.assertIs(type(status['complete']), type(expected))
                self.assertEqual(status['complete'], expected)
                self.assertIs(type(run.state['inventory_verified']), type(flag))
                self.assertEqual(run.state['inventory_verified'], flag)

    def test_numeric_edge_controls_preserve_original_expression_without_new_schema(self):
        # These are old-API compatibility controls, not observed producer facts.
        for flag, expected in ((2, True), (-1, True), (1.0, True),
                               (0.0, 0.0), (-0.0, -0.0)):
            with self.subTest(flag=flag):
                run, raw = self.load(flag)
                status, _ = self.unchanged_query(run, raw)
                self.assertIs(type(status['complete']), type(expected))
                self.assertEqual(status['complete'], expected)
                if type(expected) is float:
                    self.assertEqual(struct.pack('>d', status['complete']),
                                     struct.pack('>d', expected))

    def test_confirmation_boundary_does_not_redefine_saved_count_values_or_types(self):
        for count in (0, 0.0, -0.0, True, False, None, '0'):
            with self.subTest(count=count, native_type=type(count).__name__):
                run, raw = self.load('false', count=count)
                status, _ = self.unchanged_query(run, raw)
                self.assertIs(status['complete'], False)
                self.assertIs(type(run.state['relic_count']), type(count))
                self.assertEqual(run.state['relic_count'], count)
                self.assertIs(type(status['total_badge_count']), type(count))
                self.assertEqual(status['total_badge_count'], count)
                self.assertIs(type(status['expected_count']), type(count))
                if type(count) is float:
                    self.assertEqual(struct.pack('>d', status['total_badge_count']),
                                     struct.pack('>d', count))

    def test_old_integer_claim_still_requires_original_count_and_known_item_match(self):
        for count in (None, 1, '0'):
            with self.subTest(count=count):
                run, raw = self.load(1, count=count)
                status, _ = self.unchanged_query(run, raw)
                self.assertIs(status['complete'], False)
                self.assertEqual(run.state['inventory_verified'], 1)
                self.assertIs(type(run.state['inventory_verified']), int)

    def test_anomalous_flag_keeps_independent_known_relics_and_tools(self):
        run, raw = self.load([1], count=3, relics=RELICS, tools=(TOOL,))
        status, _ = self.unchanged_query(run, raw)
        self.assertIs(status['complete'], False)
        self.assertEqual(status['recognized'], 2)
        self.assertEqual(status['recognized_tools'], 1)
        self.assertIsNone(status['expected_count'])
        self.assertEqual(run.held_relic_ids(), sorted(RELICS))
        self.assertEqual(run.held_tool_ids(), [TOOL])
        self.assertEqual(run.state['relic_count'], 3)

    def test_restart_without_new_reading_preserves_raw_flag_and_incomplete_status(self):
        for flag in ('false', [1], {'verified': True}):
            with self.subTest(flag=flag):
                run, raw = self.load(flag, count=1, relics=(RELICS[0],))
                first = run.inventory_status()
                restored = RunState(run.file)
                status, _ = self.unchanged_query(restored, raw)
                self.assertEqual(status, first)
                self.assertIs(status['complete'], False)
                self.assertEqual(restored.state['inventory_verified'], flag)
                self.assertEqual(restored.held_relic_ids(), [RELICS[0]])

    def test_partial_or_unread_observation_cannot_upgrade_anomalous_flag(self):
        for flag in ('false', [1]):
            with self.subTest(flag=flag):
                run, _ = self.load(flag, count=1, relics=(RELICS[0],))
                observed = self.observed(count=None)
                caller = caller_receipt(observed)
                self.assertIs(run.apply(observed, 1001.0), True)
                self.assertEqual(caller_receipt(observed), caller)
                self.assertEqual(run.state['inventory_verified'], flag)
                self.assertIs(run.inventory_status()['complete'], False)
                self.assertEqual(run.held_relic_ids(), [RELICS[0]])
                restored = RunState(run.file)
                self.assertEqual(restored.state['inventory_verified'], flag)
                self.assertIs(restored.inventory_status()['complete'], False)

    def test_new_positive_record_does_not_pretend_prior_anomalous_claim_was_verified(self):
        run, _ = self.load('false', count=1, relics=(RELICS[0],))
        observed = self.observed(count=None, ids=(RELICS[1],))
        caller = caller_receipt(observed)
        self.assertIs(run.apply(observed, 1001.0), True)
        self.assertEqual(caller_receipt(observed), caller)
        self.assertEqual(run.state['inventory_verified'], 'false')
        self.assertIs(run.inventory_status()['complete'], False)
        self.assertEqual(run.held_relic_ids(), sorted(RELICS))
        self.assertFalse(any(e['kind'] == 'inventory_changed' for e in run.state['history']))
        self.assertTrue(any(e['kind'] == 'relic_confirmed' and e['id'] == RELICS[1]
                            for e in run.state['history']))

    def test_current_explicit_integer_zero_is_legitimate_new_proof_and_removal(self):
        for flag in ('false', [1]):
            with self.subTest(flag=flag):
                run, _ = self.load(flag, count=3, relics=RELICS, tools=(TOOL,))
                observed = self.observed(count=0)
                caller = caller_receipt(observed)
                self.assertIs(run.apply(observed, 1001.0), True)
                self.assertEqual(caller_receipt(observed), caller)
                self.assertIs(run.state['inventory_verified'], True)
                self.assertIs(run.inventory_status()['complete'], True)
                self.assertIs(type(run.state['relic_count']), int)
                self.assertEqual(run.state['relic_count'], 0)
                self.assertEqual(run.held_relic_ids(), [])
                self.assertEqual(run.held_tool_ids(), [])
                self.assertEqual(run.state['inventory_confirmed_at'], 1001.0)
                self.assertTrue(any(e['kind'] == 'relic_no_longer_held'
                                    for e in run.state['history']))
                self.assertTrue(any(e['kind'] == 'tool_no_longer_held'
                                    for e in run.state['history']))
                restored = RunState(run.file)
                self.assertIs(restored.state['inventory_verified'], True)
                self.assertEqual(restored.inventory_status(), run.inventory_status())

    def test_current_full_relic_and_tool_read_supplies_new_bool_proof_and_restart(self):
        for flag in ('false', [1], {'verified': True}):
            with self.subTest(flag=flag):
                run, _ = self.load(flag, count=0)
                observed = self.observed(count=3, ids=RELICS, tools=(TOOL,), full=True)
                caller = caller_receipt(observed)
                opaque = deepcopy(run.state['public_opaque'])
                self.assertIs(run.apply(observed, 1001.0), True)
                self.assertEqual(caller_receipt(observed), caller)
                self.assertIs(run.state['inventory_verified'], True)
                self.assertIs(run.inventory_status()['complete'], True)
                self.assertEqual(run.inventory_status()['expected_count'], 2)
                self.assertEqual(run.held_relic_ids(), sorted(RELICS))
                self.assertEqual(run.held_tool_ids(), [TOOL])
                self.assertEqual(run.state['public_opaque'], opaque)
                restored = RunState(run.file)
                self.assertIs(restored.state['inventory_verified'], True)
                self.assertEqual(restored.inventory_status(), run.inventory_status())
                self.assertEqual(restored.state['public_opaque'], opaque)

    def test_stale_and_cross_run_observation_remain_atomic_and_cannot_upgrade(self):
        for reason in ('stale', 'cross_run'):
            with self.subTest(reason=reason):
                run, raw = self.load('false', count=1, relics=(RELICS[0],))
                observed = self.observed(count=0)
                at = 999.0 if reason == 'stale' else 1001.0
                if reason == 'cross_run':
                    observed['config_reuse'] = {'run_id': 'another-public-run'}
                caller = caller_receipt(observed)
                before = deepcopy(run.state)
                self.assertIs(run.apply(observed, at), False)
                self.assertEqual(caller_receipt(observed), caller)
                self.assertEqual(run.state, before)
                self.assertEqual(run.file.read_bytes(), raw)
                self.assertFalse(run.file.with_suffix('.tmp').exists())
                self.assertIs(run.inventory_status()['complete'], False)

    def test_manual_reset_uses_original_false_producer_not_anomalous_record(self):
        run, _ = self.load([1], count=1, relics=(RELICS[0],))
        old_id = run.state['id']
        run.reset()
        self.assertNotEqual(run.state['id'], old_id)
        self.assertIs(run.state['inventory_verified'], False)
        self.assertIs(run.inventory_status()['complete'], False)
        self.assertEqual(run.state['relics'], {})
        self.assertEqual(run.state['tactical_tools'], {})
        self.assertIsNone(run.state['relic_count'])
        restored = RunState(run.file)
        self.assertIs(restored.state['inventory_verified'], False)
        self.assertEqual(restored.state['id'], run.state['id'])
