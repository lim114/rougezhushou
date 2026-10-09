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


class RunStateNestedCacheBoundaryTests(TemporaryRunTests):
    def assert_protected(self, change):
        saved = {'id': 'public-nested-rejected-run', 'operators': {}, 'relics': {},
                 'public_sibling_must_not_install': {'nested': [None, {}]}, **change}
        raw = (json.dumps(saved, ensure_ascii=False) + '\n').encode('utf-8')
        path = self.path()
        path.write_bytes(raw)
        temporary = path.with_suffix('.tmp')
        temporary.write_bytes(b'public preexisting temporary sentinel\n')
        run = RunState(path)
        self.assertTrue(run.preserve_unreadable)
        self.assertNotEqual(run.state['id'], saved['id'])
        self.assertNotIn('public_sibling_must_not_install', run.state)
        self.visible(run)
        self.assertEqual(run.recognition_context()['run_id'], run.state['id'])
        self.assertEqual(run.calculation_resources(), {})
        self.assertEqual(run.relic_history_context()['persistent_growth_unknowns'], [])
        self.assertEqual(path.read_bytes(), raw)
        run.save()
        self.assertEqual(path.read_bytes(), raw)
        self.assertEqual(temporary.read_bytes(), b'public preexisting temporary sentinel\n')
        return run

    def test_history_nonlist_and_deep_consumed_container_damage_are_protected(self):
        changes = (
            {'history': None}, {'history': {}}, {'history': 'public'},
            {'maps': {'zone_2': {'nodes': None}}},
            {'maps': {'zone_2': {'nodes': [None]}}},
            {'maps': {'zone_2': {'nodes': [{'remembered_type': []}]}}},
            {'maps': {'zone_2': {'nodes': [{'prediction': {'candidates': None}}]}}},
            {'maps': {'zone_2': {'nodes': [{'content_history': [None]}]}}},
            {'resources': None}, {'resources': {'gold': None}},
            {'resources': {'gold': {'value': 8}}},
            {'resources': {'gold': {'value': 8, 'captured_at': float('inf')}}},
            {'config': []}, {'config': {'difficulty': None}},
            {'config': {'difficulty': {'source': 'public'}}},
            {'config': {'squad': {'name': None}}},
            {'config': {'zone': {'id': 'zone_2'}}},
            {'config': {'zone': {'id': [], 'name': 'public'}}},
            {'maps': {'zone_2': {'nodes': [{}]}},
             'config': {'zone': {'id': 'zone_2', 'name': 'public'}}},
            {'maps': {'zone_2': {'status': 'matched', 'nodes': []}}},
            {'tactical_tools': {TOOL: None}},
            {'relics': {RELICS[0]: {'icon_evidence': None}}},
            {'relics': {RELICS[0]: {'icon_evidence': {'tier_label': 1}}}},
            {'bar_signature': {}}, {'bar_signature': [None]},
            {'relic_icon_memory': []}, {'relic_icon_memory': {'icons': [None]}},
            {'relic_icon_memory': {'public_extra': None}},
            {'relic_icon_memory': {'icons': [{'id': RELICS[0]}]}},
            {'relic_icon_memory': {'icons': [{'id': RELICS[0], 'candidates': None}]}},
            {'node_contents': [None]}, {'last_node_content': []},
            {'last_node_content': {'kind': 'event'}},
            {'last_node_content': {'title': 'public', 'scene_candidates': None}},
            {'last_node_content': {'title': 'public', 'visible_options': [None]}},
        )
        for change in changes:
            with self.subTest(change=change):self.assert_protected(change)

    def test_member_nested_containers_and_unknown_consumed_identities_are_protected(self):
        for key in ('fields', 'skill_ranks', 'sources', 'field_times', 'skill_times',
                    'char_buff_ids', 'char_buff_absent_ids', 'char_buff_pending_ids',
                    'missing_fields', 'invalid_fields', 'invalid_skill_ranks'):
            with self.subTest(field=key):
                self.assert_protected({'operators': {'mechanist': {key: None}}})
        for change in (
            {'operators': {'mechanist': {'recipient_buffs': []}}},
            {'operators': {'mechanist': {'recipient_buffs': {'ids': [None]}}}},
            {'operators': {'public-unknown-member': {}}},
            {'relics': {'public-unknown-held-relic': {}}},
            {'tactical_tools': {'public-unknown-held-tool': {}}},
        ):
            with self.subTest(change=change):self.assert_protected(change)

    def test_deep_valid_opaque_data_stays_original_until_an_explicit_observation(self):
        seed = self.seed()
        saved = json.loads(seed.file.read_text(encoding='utf-8'))
        saved['operators']['mechanist'] = {'id': 'mechanist', 'scope': 'run',
            'present': True, 'fields': {}, 'skill_ranks': {}, 'recipient_buffs': None,
            'sources': {'public_opaque': [None, {'leaf': None}]},
            'public_nested': {'nullable': None}}
        saved['maps'] = {'public_unused_zone': {'nodes': [{'current_node': None,
            'prediction': None, 'content': None, 'remembered_content': None,
            'public_nullable': None}], 'public_opaque': [None, {}]}}
        saved['config']['public_opaque_record'] = {'anything': [None, {}]}
        saved['config']['public_nullable_extra'] = None
        saved['relics']['public-unknown-not-held'] = {'held': False, 'public': None}
        saved['resources'] = {'gold': {'value': 8, 'captured_at': saved['last_read'],
                                      'public': {'nullable': None}}}
        raw = json.dumps(saved, ensure_ascii=False, indent=2).encode('utf-8')
        run = self.load_raw(raw)
        self.assertFalse(run.preserve_unreadable)
        self.assertEqual(run.state['id'], saved['id'])
        for key in saved:
            if key != 'notice':self.assertEqual(run.state[key], saved[key], key)
        self.visible(run)
        self.assertEqual(run.file.read_bytes(), raw)
        self.assertIs(run.apply(bar(False), run.state['last_read'] + 1), True)
        self.assertEqual(run.state['operators']['mechanist']['public_nested'], {'nullable': None})
        self.assertEqual(run.state['maps'], saved['maps'])
        restored = RunState(run.file)
        self.assertFalse(restored.preserve_unreadable)
        self.assertEqual(restored.state['id'], saved['id'])
        self.visible(restored)

    def test_clearing_restore_ignores_history_without_kind_and_preserves_history(self):
        saved = {'operators': {}, 'relics': {}, 'maps': {'public_zone': {
            'nodes': [{'id': 'public_node', 'remembered_type': '林间空地'}]}},
            'history': [{'zone_id': 'public_zone', 'public_opaque': None}]}
        run, raw = self.load_saved(saved)
        self.assertFalse(run.preserve_unreadable)
        node = run.state['maps']['public_zone']['nodes'][0]
        self.assertTrue(node['visited'])
        self.assertNotIn('remembered_type', node)
        self.assertEqual(run.state['history'], saved['history'])
        self.assertEqual(run.file.read_bytes(), raw)
        self.visible(run)

    def test_valid_selected_map_and_real_report_consumers_survive_saved_restart(self):
        from rouge.map_recognition import map_data
        from rouge.map_reporting import format_map, format_node
        from rouge.run_config import config_data
        data = map_data()
        template = next(t for t in data['templates'] if t['id'] == '2a')
        graph = {'status': 'matched', 'zone_id': template['zone_id'],
            'template_id': template['id'], 'edges': deepcopy(template['edges']),
            'current_node': None, 'difficulty_value': None,
            'grid': {'rows': template['rows'], 'cols': template['cols']},
            'source': deepcopy(data['source']),
            'nodes': [{**deepcopy(node), 'template_type': node['fixed_type'],
                'observed_type': None, 'visible': False, 'prediction': None}
                for node in template['nodes']]}
        run = RunState(self.path())
        zone = template['zone_id']
        observed = {'map': graph, 'config': {'zone': {'id': zone,
            'name': config_data()['zones'][zone]['name'], 'source': 'public-visible-zone'}}}
        self.assertTrue(run.apply(observed, run.state['started_at'] + 1))
        expected_map = deepcopy(run.state['maps'][zone])
        raw = run.file.read_bytes()
        restored = RunState(run.file)
        self.assertFalse(restored.preserve_unreadable)
        self.assertEqual(restored.state['maps'][zone], expected_map)
        self.assertEqual(restored.file.read_bytes(), raw)
        self.visible(restored)
        self.assertIn('历史参考', format_map(None, restored.state['maps'][zone], technical=True))
        first = expected_map['nodes'][0]['id']
        self.assertIn('节点状态', format_node(restored.state['maps'][zone], first,
                                         historical=True, technical=True))

    def test_protected_nested_fault_can_accept_memory_updates_and_only_manual_reset_replaces_file(self):
        run = self.assert_protected({'operators': {'mechanist': {'fields': None}}})
        original = run.file.read_bytes()
        isolated_other = self.seed()
        other_raw = isolated_other.file.read_bytes()
        observed = {'operators': [{'id': 'mechanist', 'scope': 'run',
            'fields': {'elite': 0}, 'skill_ranks': {}}],
            'selected_operator': 'mechanist', 'crew_count': 1}
        self.assertTrue(run.apply(observed, run.state['started_at'] + 1))
        self.assertEqual(run.state['operators']['mechanist']['fields'], {'elite': 0})
        self.assertTrue(run.preserve_unreadable)
        self.assertEqual(run.file.read_bytes(), original)
        self.visible(run)
        run.reset()
        self.assertFalse(run.preserve_unreadable)
        self.assertEqual(run.state['operators'], {})
        self.assertNotEqual(run.file.read_bytes(), original)
        self.assertEqual(isolated_other.file.read_bytes(), other_raw)


if __name__ == '__main__':
    unittest.main()
