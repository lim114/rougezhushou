"""The verified partial packet stays isolated and its public proof is immutable."""
import copy
import unittest
from unittest.mock import patch

from rouge.ammo_reference import partial_packet_reference, refill_source
from rouge.damage import calculate_damage

ANGEL = 'char_1041_angel2'
BOOK = 'rogue_6_relic_legacy_139'
YA = 'rogue_6_relic_legacy_140'


def calc(operator, skill, ids, **options):
    return calculate_damage({'operator':operator, 'skill':skill, 'relic_ids':ids, **options})


class PacketScope054Tests(unittest.TestCase):
    def tearDown(self):
        # A red immutability assertion must not contaminate following tests.
        refill_source.cache_clear()

    def test_reference_matches_only_the_documented_operator_skill_and_attack_cost(self):
        reference = partial_packet_reference(ANGEL, 3, 5)
        self.assertEqual(reference['partial_last_packet'], 'full_attack')
        self.assertEqual(reference['consume_event_count_per_attack'], 5)
        for operator, skill, cost in (
            (ANGEL, 1, 5), (ANGEL, 2, 5), (ANGEL, 3, 1),
            ('char_1035_wisdel', 3, 5), ('char_1052_kalts2', 2, 5),
            ('char_4230_mcnist', 1, 5), ('char_1015_aglna2', 3, 5),
            ('silverash', 3, 5), ('mechanist', 1, 5), (None, 3, 5),
        ):
            with self.subTest(operator=operator, skill=skill, cost=cost):
                self.assertIsNone(partial_packet_reference(operator, skill, cost))

    def test_public_proof_and_report_note_do_not_leak_to_other_skills(self):
        for operator, skill in (
            (ANGEL, 1), (ANGEL, 2), ('char_1035_wisdel', 3),
            ('kaltsit', 2), ('mechanist', 1), ('char_151_myrtle', 1),
        ):
            with self.subTest(operator=operator, skill=skill):
                result = calc(operator, skill, [BOOK])
                self.assertFalse(any(r.get('ammo_parameters', {}).get('partial_packet_reference')
                    for r in result['relic_resolution']['rules']))
                self.assertNotIn('末包机制资料', str(result['report']))
        result = calc(ANGEL, 3, [BOOK])
        self.assertTrue(any(r.get('ammo_parameters', {}).get('partial_packet_reference')
            for r in result['relic_resolution']['rules']))
        self.assertIn('末包机制资料', str(result['report']))

    def test_mutating_previous_public_proof_cannot_corrupt_the_cached_rule(self):
        baseline = copy.deepcopy(refill_source())
        first = calc(ANGEL, 3, [BOOK])
        snapshot = copy.deepcopy(first)
        rule = next(r for r in first['relic_resolution']['rules'] if r['kind'] == 'ammo_refill')
        proof = rule['ammo_parameters']['partial_packet_reference']
        proof['pinned_data_crosschecks'][0]['value'] = 'externally modified skill'
        proof['not_included'].clear()
        proof['packet_hits'] = 999
        self.assertEqual(refill_source(), baseline)
        self.assertEqual(calc(ANGEL, 3, [BOOK]), snapshot)

    def test_mutating_direct_returned_reference_does_not_modify_source_metadata(self):
        baseline = copy.deepcopy(refill_source())
        reference = partial_packet_reference(ANGEL, 3, 5)
        reference['pinned_data_crosschecks'][1]['attack@trigger_time'] = 999
        reference['not_included'].append('external item')
        reference['skill'] = 2
        self.assertEqual(refill_source(), baseline)
        self.assertEqual(partial_packet_reference(ANGEL, 3, 5)['pinned_data_crosschecks'][1]['attack@trigger_time'], 50)

    def test_packet_proof_does_not_override_polling_or_absent_acquisition_order(self):
        with patch('rouge.ammo_reference.refill_before_empty_is_safe', return_value=False):
            result = calc(ANGEL, 3, [BOOK])
        self.assertFalse(result['relic_resolution']['complete'])
        self.assertIsNone(result['estimate']['skill']['total_damage'])
        for ids in ([BOOK, YA], [YA, BOOK]):
            result = calc(ANGEL, 3, ids)
            self.assertTrue(result['relic_resolution']['complete'])
            self.assertIsNotNone(result['estimate']['skill']['cycle_seconds'])
            self.assertFalse(result['ammo_refill_reference']['order_verified'])
            self.assertTrue(result['ammo_refill_reference']['count_order_invariant'])
        result = calc(ANGEL, 2, [BOOK])
        self.assertFalse(result['relic_resolution']['complete'])
        self.assertIsNone(result['estimate']['skill']['total_damage'])


if __name__ == '__main__':
    unittest.main()
