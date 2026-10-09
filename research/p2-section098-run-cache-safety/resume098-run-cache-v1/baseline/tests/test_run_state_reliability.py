"""Public temporary-state contracts; Source proposal, not an executed receipt.

Inventory inputs exercise RunState directly. The inspected producer emits
int/None; these tests do not assert that image/OCR recognition produces bool.
"""
from copy import deepcopy
import json
import math
from pathlib import Path
import tempfile
import unittest

from rouge.run_state import RunState


RELICS = ('rogue_6_relic_cargo_1', 'rogue_6_relic_fight_26')
TOOL = 'rogue_6_active_tool_5'
MISSING = object()


def icon(identity):
    return {'id': identity, 'candidates': [identity], 'confirmed': True}


def bar(count=MISSING, *, one=False):
    relics = {'ids': [], 'icons': [icon(RELICS[0])] if one else [],
              'source': 'held_bar'}
    if count is not MISSING:
        relics['count'] = count
    observed = {'relics': relics, 'operators': []}
    shared = [None, False, 0, -0.0, ('public', 1), b'public']
    cycle = []
    cycle.append(cycle)
    observed['public_opaque'] = {'first': shared, 'same': shared,
                                'members_alias': observed['operators'], 'cycle': cycle}
    return observed


def caller_receipt(value):
    """Retain this fixture's types, order, object identities and graph aliases."""
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
            return ('float', item.hex())
        return (kind.__name__, item)

    return visit(value)


class TemporaryRunTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='public-run-reliability-')
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.sequence = 0

    def path(self):
        self.sequence += 1
        return self.directory / (str(self.sequence) + '.json')

    def load_raw(self, raw):
        path = self.path()
        path.write_bytes(raw)
        return RunState(file=path)

    def load_saved(self, saved):
        raw = (json.dumps(saved, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        return self.load_raw(raw), raw

    def visible(self, run):
        return (run.summary(), run.inventory_status(),
                run.held_relic_ids(), run.held_tool_ids())

    def seed(self):
        run = RunState(file=self.path())
        observed = {'relics': {'ids': list(RELICS), 'count': 3, 'source': 'held_bar',
                              'icons': [icon(rid) for rid in (*RELICS, TOOL)]},
                    'tactical_tools': {'ids': [TOOL], 'source': 'held_bar'}, 'operators': []}
        before = caller_receipt(observed)
        self.assertIs(run.apply(observed, run.state['started_at'] + 1), True)
        self.assertEqual(caller_receipt(observed), before)
        self.assertTrue(run.inventory_status()['complete'])
        return run


class RunStateCacheShapeTests(TemporaryRunTests):
    def test_five_consumed_shape_faults_keep_original_and_do_not_install_siblings(self):
        faults = (
            ('maps_array', {'maps': []}),
            ('null_graph', {'maps': {'public_zone': None}}),
            ('null_history_event', {'history': [None]}),
            ('null_member', {'operators': {'mechanist': None, 'char_151_myrtle': {}}}),
            ('null_relic', {'relics': {RELICS[0]: None, RELICS[1]: {}}}),
        )
        for name, change in faults:
            with self.subTest(fault=name):
                saved = {'id': 'public-rejected-record',
                         'operators': {'mechanist': {'scope': None, 'public_nullable': None}},
                         'relics': {RELICS[0]: {'held': True, 'public_nullable': None}},
                         'public_not_installed': {'nullable': None}, **change}
                run, raw = self.load_saved(saved)
                self.assertIs(run.preserve_unreadable, True)
                self.assertNotEqual(run.state['id'], saved['id'])
                self.assertNotIn('public_not_installed', run.state)
                self.assertEqual(run.state['operators'], {})
                self.assertEqual(run.state['relics'], {})
                self.assertEqual(run.state['maps'], {})
                self.assertEqual(run.state['history'], [])
                self.assertIn('原本局记录无法读取', run.summary())
                self.assertEqual(run.held_relic_ids(), [])
                self.assertEqual(run.held_tool_ids(), [])
                self.assertFalse(run.inventory_status()['complete'])
                self.assertEqual(run.file.read_bytes(), raw)
                self.assertFalse(run.file.with_suffix('.tmp').exists())

    def test_protection_stays_sticky_while_valid_observations_are_usable_in_memory(self):
        run, raw = self.load_saved({'operators': {}, 'relics': {}, 'maps': []})
        identity = run.state['id']
        observed = {'relics': {'ids': [RELICS[0]], 'icons': [icon(RELICS[0])],
                              'count': 1, 'source': 'held_bar'}, 'operators': []}
        self.assertIs(run.apply(observed, run.state['started_at'] + 1), True)
        self.assertEqual(run.state['id'], identity)
        self.assertEqual(run.held_relic_ids(), [RELICS[0]])
        self.assertTrue(run.inventory_status()['complete'])
        self.assertIs(run.preserve_unreadable, True)
        run.save()
        self.assertEqual(run.file.read_bytes(), raw)
        self.assertFalse(run.file.with_suffix('.tmp').exists())
        restored = RunState(file=run.file)
        self.assertIs(restored.preserve_unreadable, True)
        self.assertEqual(restored.held_relic_ids(), [])
        self.assertEqual(restored.file.read_bytes(), raw)
        self.visible(restored)

    def test_only_explicit_manual_reset_unblocks_own_file_and_leaves_other_run_alone(self):
        run, raw = self.load_saved({'operators': {}, 'relics': {}, 'maps': []})
        other = self.seed()
        other_raw = other.file.read_bytes()
        old_identity = run.state['id']
        run.save()
        self.assertEqual(run.file.read_bytes(), raw)
        run.reset()  # Explicit user action simulated only inside this temporary fixture.
        self.assertIs(run.preserve_unreadable, False)
        self.assertNotEqual(run.state['id'], old_identity)
        self.assertEqual(run.state['history'], [])
        self.assertEqual(run.held_relic_ids(), [])
        self.assertEqual(run.held_tool_ids(), [])
        persisted = json.loads(run.file.read_text(encoding='utf-8'))
        self.assertEqual(persisted['id'], run.state['id'])
        self.assertEqual(persisted['relics'], {})
        self.assertFalse(run.file.with_suffix('.tmp').exists())
        self.assertEqual(other.file.read_bytes(), other_raw)
        self.assertEqual(other.held_relic_ids(), list(RELICS))

    def test_omitted_optional_fields_and_missing_file_keep_old_defaults(self):
        run, raw = self.load_saved({'operators': {}, 'relics': {}})
        self.assertIs(run.preserve_unreadable, False)
        self.assertEqual(run.state['maps'], {})
        self.assertEqual(run.state['history'], [])
        self.visible(run)
        self.assertEqual(run.file.read_bytes(), raw)
        missing = RunState(file=self.path())
        self.assertIs(missing.preserve_unreadable, False)
        self.assertFalse(missing.file.exists())
        self.visible(missing)

    def test_empty_records_and_nullable_opaque_deeper_extras_remain_accepted(self):
        saved = {'operators': {'mechanist': {'public_nullable': None}},
                 'relics': {RELICS[0]: {'public_nested': {'nullable': None}}},
                 'maps': {'public_zone': {'nodes': [{}], 'current_node': None,
                                         'public_nested': {'leaf': None}}},
                 'history': [{}, {'kind': 'public_opaque', 'public_nested': [None, {}]}],
                 'public_nullable': None, 'last_node_content': None}
        run, raw = self.load_saved(saved)
        self.assertIs(run.preserve_unreadable, False)
        for key in saved:
            self.assertEqual(run.state[key], saved[key], key)
        self.visible(run)
        self.assertEqual(run.file.read_bytes(), raw)
        self.assertFalse(run.file.with_suffix('.tmp').exists())

    def test_existing_stored_counts_and_nonfinite_opaque_history_values_are_not_sanitized(self):
        # Saved bool is legacy data here; incoming bool qualification is separate.
        for count in (None, False, True, 0, 1, 0.0, '0', -1, 1.5):
            with self.subTest(count=count, native_type=type(count).__name__):
                saved = {'operators': {}, 'relics': {}, 'relic_count': count,
                         'history': [{'kind': 'public_opaque', 'at': float('nan'),
                                      'public_infinity': float('inf'), 'public_nullable': None}]}
                run, raw = self.load_saved(saved)
                self.assertIs(run.preserve_unreadable, False)
                self.assertIs(type(run.state['relic_count']), type(count))
                self.assertEqual(run.state['relic_count'], count)
                event = run.state['history'][0]
                self.assertTrue(math.isnan(event['at']))
                self.assertEqual(event['public_infinity'], float('inf'))
                self.assertIs(event['public_nullable'], None)
                self.visible(run)
                self.assertEqual(run.file.read_bytes(), raw)

    def test_valid_legacy_full_signature_migrates_and_accepted_memory_continues(self):
        seed = self.seed()
        saved = json.loads(seed.file.read_text(encoding='utf-8'))
        saved.pop('relic_icon_memory')
        saved['public_legacy'] = {'nullable': None, 'extra': [None, {'v': 'kept'}]}
        run, raw = self.load_saved(saved)
        self.assertIs(run.preserve_unreadable, False)
        self.assertEqual(run.state['id'], saved['id'])
        self.assertEqual(run.state['history'], saved['history'])
        self.assertEqual(run.state['public_legacy'], saved['public_legacy'])
        self.assertEqual(run.state['relic_icon_memory']['source'], 'legacy_same_run_signature')
        self.assertEqual(run.file.read_bytes(), raw)
        self.assertIs(run.apply(bar(False), run.state['last_read'] + 1), True)
        self.assertEqual(run.held_relic_ids(), list(RELICS))
        self.assertEqual(run.held_tool_ids(), [TOOL])
        self.assertIs(type(run.state['relic_count']), int)
        self.assertEqual(run.state['relic_count'], 3)
        self.assertEqual(run.state['history'], saved['history'])
        restored = RunState(file=run.file)
        self.assertEqual(restored.state['id'], saved['id'])
        self.assertEqual(restored.state['public_legacy'], saved['public_legacy'])
        self.assertTrue(restored.inventory_status()['complete'])
        self.visible(restored)

    def test_existing_json_and_top_container_failures_still_preserve_original(self):
        raws = (b'{', b'null\n', b'{"operators":[],"relics":{}}\n',
                b'{"operators":{},"relics":[]}\n', b'{"relics":{}}\n')
        for raw in raws:
            with self.subTest(raw=raw):
                run = self.load_raw(raw)
                self.assertIs(run.preserve_unreadable, True)
                self.visible(run)
                run.save()
                self.assertEqual(run.file.read_bytes(), raw)
                self.assertFalse(run.file.with_suffix('.tmp').exists())


class RunStateInventoryCountQualificationTests(TemporaryRunTests):
    def test_bool_inputs_match_paired_unread_results_and_preserve_full_caller_graph(self):
        seed = self.seed()
        raw = seed.file.read_bytes()
        at = seed.state['last_read'] + 1
        for count, one in ((False, False), (True, True)):
            with self.subTest(count=count):
                actual = self.load_raw(raw)
                unread = self.load_raw(raw)
                observed = bar(count, one=one)
                before = caller_receipt(observed)
                self.assertIs(actual.apply(observed, at), True)
                self.assertIs(unread.apply(bar(None, one=one), at), True)
                self.assertEqual(caller_receipt(observed), before)
                self.assertIs(type(observed['relics']['count']), bool)
                self.assertIs(observed['relics']['count'], count)
                self.assertEqual(actual.state, unread.state)
                self.assertEqual(actual.file.read_bytes(), unread.file.read_bytes())
                self.assertEqual(self.visible(actual), self.visible(unread))
                self.assertEqual(actual.held_relic_ids(), list(RELICS))
                self.assertEqual(actual.held_tool_ids(), [TOOL])
                self.assertIs(type(actual.state['relic_count']), int)
                self.assertEqual(actual.state['relic_count'], 3)
                self.assertFalse(actual.file.with_suffix('.tmp').exists())

    def test_integer_zero_and_one_still_prove_corresponding_inventory_removals(self):
        seed = self.seed()
        raw = seed.file.read_bytes()
        for count, one, held in ((0, False, []), (1, True, [RELICS[0]])):
            with self.subTest(count=count):
                run = self.load_raw(raw)
                observed = bar(count, one=one)
                before = caller_receipt(observed)
                self.assertIs(run.apply(observed, seed.state['last_read'] + 1), True)
                self.assertEqual(caller_receipt(observed), before)
                self.assertIs(type(run.state['relic_count']), int)
                self.assertEqual(run.state['relic_count'], count)
                self.assertEqual(run.held_relic_ids(), held)
                self.assertEqual(run.held_tool_ids(), [])
                self.assertTrue(run.inventory_status()['complete'])
                self.assertTrue(any(e['kind'] == 'tool_no_longer_held'
                                    for e in run.state['history']))
                restored = RunState(file=run.file)
                self.assertEqual(restored.inventory_status(), run.inventory_status())
                self.assertEqual(restored.held_relic_ids(), run.held_relic_ids())
                self.assertEqual(restored.held_tool_ids(), run.held_tool_ids())
                self.assertIn(f'{count} / {count} 件', restored.summary())

    def test_none_and_missing_count_keep_original_positive_records_and_history(self):
        seed = self.seed()
        raw = seed.file.read_bytes()
        for count, one in ((None, False), (None, True), (MISSING, False)):
            with self.subTest(count='missing' if count is MISSING else count, one=one):
                run = self.load_raw(raw)
                before_history = deepcopy(run.state['history'])
                observed = bar(count, one=one)
                before = caller_receipt(observed)
                self.assertIs(run.apply(observed, seed.state['last_read'] + 1), True)
                self.assertEqual(caller_receipt(observed), before)
                self.assertEqual(run.state['history'], before_history)
                self.assertEqual(run.held_relic_ids(), list(RELICS))
                self.assertEqual(run.held_tool_ids(), [TOOL])
                self.assertEqual(run.state['relic_count'], 3)
                self.assertIs(type(run.state['relic_count']), int)

    def test_duplicate_physical_slots_with_bool_remain_partial_like_unread_count(self):
        # Repeated matches do not establish acquisition/stacking of duplicate relics.
        seed = self.seed()
        raw = seed.file.read_bytes()
        runs = []
        for count in (True, None):
            run = self.load_raw(raw)
            observed = bar(count)
            observed['relics']['icons'] = [icon(RELICS[0]), icon(RELICS[0])]
            before = caller_receipt(observed)
            self.assertIs(run.apply(observed, seed.state['last_read'] + 1), True)
            self.assertEqual(caller_receipt(observed), before)
            self.assertFalse(run.inventory_status()['complete'])
            self.assertFalse(run.state['relic_icon_memory']['complete_bar'])
            self.assertEqual(run.held_relic_ids(), list(RELICS))
            self.assertEqual(run.held_tool_ids(), [TOOL])
            runs.append(run)
        self.assertEqual(runs[0].state, runs[1].state)

    def test_new_positive_tool_with_bool_retains_prior_items_without_complete_claim(self):
        seed = self.seed()
        raw = seed.file.read_bytes()
        new_tool = 'rogue_6_active_tool_1'
        runs = []
        for count in (False, None):
            run = self.load_raw(raw)
            observed = bar(count)
            observed['tactical_tools'] = {'ids': [new_tool], 'source': 'held_bar_or_cards'}
            observed['relics']['cards'] = [{'id': new_tool, 'candidates': [new_tool],
                                           'confirmed': True, 'source': 'held_name_and_usage'}]
            before = caller_receipt(observed)
            self.assertIs(run.apply(observed, seed.state['last_read'] + 1), True)
            self.assertEqual(caller_receipt(observed), before)
            self.assertEqual(run.held_relic_ids(), list(RELICS))
            self.assertEqual(run.held_tool_ids(), sorted([TOOL, new_tool]))
            self.assertFalse(run.inventory_status()['complete'])
            self.assertEqual(run.state['relic_count'], 3)
            runs.append(run)
        self.assertEqual(runs[0].state, runs[1].state)

    def test_stale_and_cross_run_bool_inputs_remain_ignored_before_any_mutation(self):
        for reason in ('stale', 'cross_run'):
            with self.subTest(reason=reason):
                run = self.seed()
                observed = bar(False)
                at = run.state['last_read'] + 1
                if reason == 'stale':
                    at = run.state['started_at'] - 1
                else:
                    observed['config_reuse'] = {'run_id': 'different-public-run'}
                before = deepcopy(run.state)
                caller = caller_receipt(observed)
                raw = run.file.read_bytes()
                self.assertIs(run.apply(observed, at), False)
                self.assertEqual(run.state, before)
                self.assertEqual(caller_receipt(observed), caller)
                self.assertEqual(run.file.read_bytes(), raw)

    def test_original_member_completeness_error_precedes_inventory_qualification(self):
        run = self.seed()
        observed = bar(True, one=True)
        observed['operators'].append({'id': 'mechanist', 'scope': 'run', 'fields': {},
                                      'char_buff_ids': [], 'char_buffs_complete': 1})
        before = deepcopy(run.state)
        raw = run.file.read_bytes()
        caller = caller_receipt(observed)
        with self.assertRaises(ValueError) as raised:
            run.apply(observed, run.state['last_read'] + 1)
        self.assertEqual(str(raised.exception), '个人强化列表完整性必须为布尔值。')
        self.assertEqual(run.state, before)
        self.assertEqual(run.file.read_bytes(), raw)
        self.assertEqual(caller_receipt(observed), caller)

    def test_nonbool_float_inventory_zero_keeps_existing_native_count_contract(self):
        run = self.seed()
        observed = bar(0.0)
        before = caller_receipt(observed)
        self.assertIs(run.apply(observed, run.state['last_read'] + 1), True)
        self.assertEqual(caller_receipt(observed), before)
        self.assertIs(type(run.state['relic_count']), float)
        self.assertEqual(run.state['relic_count'], 0.0)
        self.assertEqual(run.held_relic_ids(), [])
        self.assertEqual(run.held_tool_ids(), [])
        self.assertTrue(run.inventory_status()['complete'])

    def test_inventory_bool_does_not_broaden_existing_float_string_crew_contract(self):
        for crew, present in ((0.0, False), ('0', True)):
            with self.subTest(crew=crew):
                run = self.seed()
                member = {'id': 'mechanist', 'scope': 'run', 'fields': {'elite': 0},
                          'skill_ranks': {}}
                self.assertIs(run.apply({'operators': [member], 'crew_count': 1},
                                        run.state['last_read'] + 1), True)
                observed = bar(False)
                observed['crew_count'] = crew
                caller = caller_receipt(observed)
                self.assertIs(run.apply(observed, run.state['last_read'] + 1), True)
                self.assertEqual(caller_receipt(observed), caller)
                self.assertIs(type(run.state['crew_count']), type(crew))
                self.assertEqual(run.state['crew_count'], crew)
                self.assertIs(run.state['operators']['mechanist']['present'], present)
                self.assertEqual(run.held_relic_ids(), list(RELICS))
                self.assertEqual(run.held_tool_ids(), [TOOL])
                self.assertIs(type(run.state['relic_count']), int)
                self.assertEqual(run.state['relic_count'], 3)


if __name__ == '__main__':
    unittest.main()
