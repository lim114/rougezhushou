"""Positive contradictory slot evidence invalidates a prior inventory proof.

These are state-seam tests using isolated synthetic observations, not captured
inventory coverage or a claim that every held page has been recognized.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from rouge.damage import calculate_damage
from rouge.run_state import RunState


OLD_RELICS = ['rogue_6_relic_cargo_1', 'rogue_6_relic_fight_26']
OLD_TOOL = 'rogue_6_active_tool_5'
FOREIGN = ['rogue_6_relic_legacy_22', 'rogue_6_relic_legacy_23']


def slot(identity, candidates=None, confirmed=True):
    return {'id': identity, 'candidates': candidates or [identity],
            'confirmed': confirmed, 'score': .97}


def observation(icons=(), count=None):
    return {'relics': {'ids': [], 'icons': copy.deepcopy(list(icons)),
                      'count': count, 'source': 'held_bar'}}


class RelicReading050Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / 'run.json'
        self.run = RunState(self.file)
        self.at = self.run.state['started_at'] + 1
        self.run.apply(observation([slot(rid) for rid in OLD_RELICS + [OLD_TOOL]], 3), self.at)
        self.assertTrue(self.run.inventory_status()['complete'])
        self.initial_history = copy.deepcopy(self.run.state['history'])

    def ambiguous(self, count=3, candidates=None):
        self.run.apply(observation([slot(FOREIGN[0], candidates or FOREIGN, False)], count), self.at + 1)

    def preserved_records(self):
        self.assertEqual(self.run.held_relic_ids(), OLD_RELICS)
        self.assertEqual(self.run.held_tool_ids(), [OLD_TOOL])
        self.assertEqual(self.run.state['history'][:len(self.initial_history)], self.initial_history)

    def test_foreign_unconfirmed_partial_slot_revokes_inventory_proof(self):
        self.ambiguous()
        self.assertFalse(self.run.inventory_status()['complete'])
        self.preserved_records()
        self.assertFalse(self.run.state['relic_icon_memory']['complete_bar'])

    def test_foreign_unconfirmed_slot_without_current_count_revokes_proof(self):
        self.ambiguous(count=None)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.preserved_records()

    def test_old_identity_plus_foreign_challenger_is_unresolved_not_old_proof(self):
        self.ambiguous(candidates=[OLD_RELICS[0], FOREIGN[0]])
        self.assertFalse(self.run.inventory_status()['complete'])
        self.preserved_records()

    def test_unread_frame_preserves_complete_memory_and_confirmation_time(self):
        before = copy.deepcopy(self.run.inventory_status())
        self.run.apply(observation([], None), self.at + 1)
        self.assertEqual(self.run.inventory_status(), before)
        self.preserved_records()

    def test_matching_partial_slot_preserves_previous_full_proof(self):
        self.run.apply(observation([slot(OLD_RELICS[0])], 3), self.at + 1)
        self.assertTrue(self.run.inventory_status()['complete'])
        self.assertTrue(self.run.state['relic_icon_memory']['complete_bar'])
        self.preserved_records()

    def test_explicit_count_change_invalidates_without_erasing_history(self):
        self.run.apply(observation([], 4), self.at + 1)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.preserved_records()

    def test_count_correction_does_not_confirm_old_slots_by_arithmetic(self):
        self.run.apply(observation([], 4), self.at + 1)
        self.run.apply(observation([], 3), self.at + 2)
        self.assertFalse(self.run.inventory_status()['complete'])
        self.preserved_records()

    def test_restart_preserves_revoked_proof_until_a_full_current_bar(self):
        self.ambiguous()
        restored = RunState(self.file)
        self.assertFalse(restored.inventory_status()['complete'])
        restored.apply(observation([slot(rid) for rid in OLD_RELICS + [FOREIGN[0]]], 3), self.at + 2)
        self.assertTrue(restored.inventory_status()['complete'])
        self.assertEqual(restored.held_tool_ids(), [])
        self.assertEqual(restored.held_relic_ids(), sorted(OLD_RELICS + [FOREIGN[0]]))

    def test_revoked_inventory_marks_public_calculation_incomplete(self):
        self.ambiguous()
        result = calculate_damage({'operator': 'mechanist', 'skill': 3,
            'relic_ids': self.run.held_relic_ids(), 'inventory_status': self.run.inventory_status()})
        self.assertFalse(result['estimate']['complete'])
        self.assertTrue(any('本局藏品读取未完整' in note for note in result['estimate']['notes']))


if __name__ == '__main__':
    unittest.main()
