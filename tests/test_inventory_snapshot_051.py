"""Inventory slot multiplicity and recipient evidence in temporary run files.

Repeated physical matches are a recognition consistency case. These fixtures
do not assert that duplicate instances of a particular relic can be acquired.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from rouge.run_state import RunState
from rouge.catalog import catalog, tactical_tools


IDS = ['rogue_6_relic_cargo_1', 'rogue_6_relic_fight_26', 'rogue_6_active_tool_5']
BASE = 'rogue_6_relic_legacy_24'


def icon(rid, x=.2, candidates=None, confirmed=True):
    return {'id': rid, 'candidates': candidates or [rid], 'confirmed': confirmed,
            'score': .97, 'center': [x, .9]}


def bar(rows, count=None):
    return {'relics': {'ids': [], 'icons': copy.deepcopy(rows), 'count': count, 'source': 'held_bar'}}


class InventorySnapshot051Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / 'run.json'
        self.run = RunState(self.file)
        self.at = self.run.state['started_at'] + 1

    def confirmed_three(self):
        rows = [icon(rid, .2 + i * .1) for i, rid in enumerate(IDS)]
        self.run.apply(bar(rows, 3), self.at)
        self.assertTrue(self.run.inventory_status()['complete'])
        return rows

    def test_two_physical_matches_cannot_reuse_one_historical_slot(self):
        self.confirmed_three()
        history = copy.deepcopy(self.run.state['history'])
        self.run.apply(bar([icon(IDS[0], .2), icon(IDS[0], .3)], 3), self.at + 1)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.assertFalse(self.run.state['relic_icon_memory']['complete_bar'])
        self.assertEqual(self.run.held_relic_ids(), IDS[:2])
        self.assertEqual(self.run.held_tool_ids(), IDS[2:])
        self.assertEqual(self.run.state['history'][:len(history)], history)

    def test_excess_slot_multiplicity_is_unknown_without_current_count(self):
        self.confirmed_three()
        self.run.apply(bar([icon(IDS[0], .2), icon(IDS[0], .3)]), self.at + 1)
        self.assertFalse(self.run.inventory_status()['complete'])

    def test_grade_resolution_does_not_hide_repeated_family_matches(self):
        family = [BASE, BASE + '_a', BASE + '_b', BASE + '_c']
        initial = [icon(BASE, .2, family, False), icon(IDS[1], .3), icon(IDS[2], .4)]
        observed = bar(initial, 3)
        observed['config'] = {'difficulty': {'value': 10, 'source': '本局等级标签'}}
        self.run.apply(observed, self.at)
        self.assertTrue(self.run.inventory_status()['complete'])
        self.run.apply(bar([icon(BASE, .2, family, False), icon(BASE, .3, family, False)], 3), self.at + 1)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.assertEqual(self.run.held_relic_ids(), sorted([BASE + '_c', IDS[1]]))

    def test_excess_multiplicity_revocation_survives_restart_and_full_recheck(self):
        full = self.confirmed_three()
        self.run.apply(bar([icon(IDS[0], .2), icon(IDS[0], .3)], 3), self.at + 1)
        self.run = RunState(self.file)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.run.apply(bar(full, 3), self.at + 2)
        self.assertTrue(self.run.inventory_status()['complete'])
        self.assertEqual(self.run.held_relic_ids(), IDS[:2])

    def test_reordered_partial_unique_slots_preserve_complete_proof(self):
        self.confirmed_three()
        self.run.apply(bar([icon(IDS[2], .25), icon(IDS[0], .4)], 3), self.at + 1)
        self.assertTrue(self.run.inventory_status()['complete'])
        self.assertEqual(len(self.run.state['relic_icon_memory']['icons']), 3)

    def test_empty_observation_does_not_erase_a_valid_snapshot(self):
        self.confirmed_three()
        snapshot = copy.deepcopy(self.run.state['relic_icon_memory'])
        self.run.apply(bar([]), self.at + 1)
        self.assertTrue(self.run.inventory_status()['complete'])
        self.assertEqual(self.run.state['relic_icon_memory'], snapshot)

    def test_full_length_duplicate_candidates_do_not_prove_all_items(self):
        self.confirmed_three()
        self.run.apply(bar([icon(IDS[0], .2), icon(IDS[0], .3), icon(IDS[2], .4)], 3), self.at + 1)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.assertEqual(self.run.held_relic_ids(), IDS[:2])
        self.assertEqual(self.run.held_tool_ids(), IDS[2:])

    def test_separate_partial_pages_cannot_create_a_complete_snapshot(self):
        self.run.apply(bar([icon(IDS[0], .2)], 3), self.at)
        self.run.apply(bar([icon(IDS[1], .2)], 3), self.at + 1)
        self.run.apply(bar([icon(IDS[2], .2)], 3), self.at + 2)
        self.assertEqual(self.run.held_relic_ids(), IDS[:2])
        self.assertEqual(self.run.held_tool_ids(), IDS[2:])
        self.assertFalse(self.run.inventory_status()['complete'])

    def test_definitive_current_full_bar_excludes_lost_item_without_erasing_history(self):
        self.confirmed_three()
        self.run.apply(bar([icon(IDS[0]), icon(IDS[2], .3)], 2), self.at + 1)
        self.assertEqual(self.run.held_relic_ids(), IDS[:1])
        self.assertFalse(self.run.state['relics'][IDS[1]]['held'])
        self.assertTrue(self.run.inventory_status()['complete'])
        self.assertTrue(any(event.get('kind') == 'relic_no_longer_held' and event.get('id') == IDS[1]
                            for event in self.run.state['history']))

    def test_partial_personal_list_cannot_remain_complete(self):
        member = {'id': 'mechanist', 'scope': 'run', 'fields': {},
                  'char_buff_ids': ['rogue_6_from_relic_9'], 'char_buffs_complete': True}
        self.run.apply({'operators': [member]}, self.at)
        self.run.apply({'operators': [{**member, 'char_buff_ids': ['rogue_6_from_relic_12'],
                                      'char_buffs_complete': False}]}, self.at + 1)
        saved = self.run.state['operators']['mechanist']
        self.assertEqual(set(saved['char_buff_ids']), {'rogue_6_from_relic_9', 'rogue_6_from_relic_12'})
        self.assertIs(saved['char_buffs_complete'], False)

    def test_account_personal_ids_are_rejected_before_state_write(self):
        self.confirmed_three()
        before = self.file.read_bytes()
        with self.assertRaises(ValueError):
            self.run.apply({'operators': [{'id': 'mechanist', 'scope': 'account', 'fields': {},
                'char_buff_ids': ['rogue_6_from_relic_9'], 'char_buffs_complete': True}]}, self.at + 1)
        self.assertEqual(self.file.read_bytes(), before)

    def initial_grade_inventory(self):
        family = [BASE, BASE + '_a', BASE + '_b', BASE + '_c']
        observed = bar([icon(BASE, .2, family, False), icon(IDS[0], .3), icon(IDS[2], .4)], 3)
        observed['config'] = {'difficulty': {'value': 10, 'source': '本局等级标签'}}
        self.run.apply(observed, self.at)
        self.assertTrue(self.run.inventory_status()['complete'])

    def owned_tool_card(self, identity):
        return {'relics': {'ids': [], 'icons': [], 'count': None, 'cards': [{
            'id': identity, 'candidates': [identity], 'confirmed': True,
            'source': 'held_name_and_usage', 'title': tactical_tools()[identity]['name']}], 'source': 'held_bar'},
            'tactical_tools': {'ids': [identity], 'source': 'held_bar_or_cards'}}

    def test_new_exact_owned_tool_invalidates_old_full_icon_memory(self):
        self.initial_grade_inventory()
        fresh = 'rogue_6_active_tool_1'
        self.run.apply(self.owned_tool_card(fresh), self.at + 1)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.assertIsNone(self.run.state['relic_icon_memory'])
        self.assertIn(fresh, self.run.held_tool_ids())
        self.assertNotIn(fresh, self.run.state['relics'])

    def test_grade_correction_cannot_remove_a_new_tool_using_an_obsolete_snapshot(self):
        self.initial_grade_inventory()
        fresh = 'rogue_6_active_tool_1'
        self.run.apply(self.owned_tool_card(fresh), self.at + 1)
        history = copy.deepcopy(self.run.state['history'])
        self.run.apply({'config': {'difficulty': {'value': 3, 'source': '本局等级标签'}}}, self.at + 2)
        self.assertIn(fresh, self.run.held_tool_ids())
        self.assertFalse(self.run.inventory_status()['complete'])
        self.assertEqual(self.run.state['history'][:len(history)], history)

    def test_new_tool_invalidates_snapshot_after_restart_too(self):
        self.initial_grade_inventory()
        fresh = 'rogue_6_active_tool_1'
        self.run.apply(self.owned_tool_card(fresh), self.at + 1)
        self.run = RunState(self.file)
        self.run.apply({'config': {'difficulty': {'value': 3, 'source': '本局等级标签'}}}, self.at + 2)
        self.assertIn(fresh, self.run.held_tool_ids())
        self.assertFalse(self.run.inventory_status()['complete'])

    def test_new_exact_relic_card_without_icons_revokes_the_complete_proof(self):
        self.initial_grade_inventory()
        fresh = IDS[1]
        self.run.apply({'relics': {'ids': [fresh], 'icons': [], 'count': None,
            'cards': [{'id': fresh, 'candidates': [fresh], 'confirmed': True,
                       'source': 'held_name_and_usage', 'title': catalog()['relics'][fresh]['name']}],
            'source': 'held_bar'}}, self.at + 1)
        self.assertIsNone(self.run.state['relic_icon_memory'])
        self.assertIs(self.run.state['inventory_verified'], False)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.run = RunState(self.file)
        self.run.apply({'config': {'difficulty': {'value': 3, 'source': '本局等级标签'}}}, self.at + 2)
        self.assertIn(fresh, self.run.held_relic_ids())
        self.assertFalse(self.run.inventory_status()['complete'])

    def test_matching_owned_tool_card_keeps_a_valid_snapshot(self):
        self.initial_grade_inventory()
        self.run.apply(self.owned_tool_card(IDS[2]), self.at + 1)
        self.assertTrue(self.run.inventory_status()['complete'])
        self.assertTrue(self.run.state['relic_icon_memory']['complete_bar'])
        self.run.apply({'config': {'difficulty': {'value': 3, 'source': '本局等级标签'}}}, self.at + 2)
        self.assertEqual(self.run.held_tool_ids(), IDS[2:])
        self.assertTrue(self.run.inventory_status()['complete'])

    def test_non_bool_personal_completeness_is_rejected_atomically(self):
        self.confirmed_three()
        before = self.file.read_bytes()
        state = copy.deepcopy(self.run.state)
        for flag in ('true', 'false', 1, 0, None, [], {}):
            with self.subTest(flag=flag), self.assertRaises(ValueError):
                self.run.apply({'operators': [
                    {'id': 'kaltsit', 'scope': 'run', 'fields': {'level': 90}},
                    {'id': 'mechanist', 'scope': 'run', 'fields': {},
                     'char_buff_ids': [], 'char_buffs_complete': flag}]}, self.at + 1)
            self.assertEqual(self.file.read_bytes(), before)
            self.assertEqual(self.run.state, state)

    def test_complete_personal_evidence_requires_a_list_and_run_scope(self):
        self.confirmed_three()
        before = self.file.read_bytes()
        state = copy.deepcopy(self.run.state)
        for scope in ('run', 'account'):
            for complete in (True, False):
                with self.subTest(scope=scope, complete=complete), self.assertRaises(ValueError):
                    self.run.apply({'operators': [{'id': 'mechanist', 'scope': scope, 'fields': {},
                                                 'char_buffs_complete': complete}]}, self.at + 1)
                self.assertEqual(self.file.read_bytes(), before)
                self.assertEqual(self.run.state, state)

    def test_explicit_boolean_complete_with_empty_list_is_valid(self):
        for complete in (False, True):
            self.run.apply({'operators': [{'id': 'mechanist', 'scope': 'run', 'fields': {},
                'char_buff_ids': [], 'char_buffs_complete': complete}]}, self.at + (1 if complete else 0))
            self.assertIs(self.run.state['operators']['mechanist']['char_buffs_complete'], complete)


if __name__ == '__main__':
    unittest.main()
