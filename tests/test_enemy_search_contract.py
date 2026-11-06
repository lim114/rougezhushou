import unittest
from rouge import current_battle_reference as battle
from rouge.player_enemy_search import matches


class EnemySearchContractTests(unittest.TestCase):
    def test_invalid_internal_records_surface(self):
        for row, error in ((None, TypeError), ({'name': 'enemy'}, KeyError),
                           ({'name': 'enemy', 'description': 3, 'abilities': []}, TypeError),
                           ({'name': 'enemy', 'description': '', 'abilities': [3]}, TypeError)):
            with self.subTest(row=row), self.assertRaises(error):
                matches(row, 'enemy')
        with self.assertRaises(AttributeError):
            matches({'name': 'enemy', 'description': '', 'abilities': []}, None)

    def test_producer_normalizes_actual_stage_records(self):
        for stage_id in ('ro6_n_1_1', 'ro6_b_5_b', 'ro6_b_7'):
            result = battle.stage_reference(stage_id)
            for row in result['enemies']:
                self.assertIsInstance(row['name'], str)
                self.assertIsInstance(row['description'], str)
                self.assertTrue(all(isinstance(value, str) for value in row['abilities']))
                self.assertTrue(matches(row, row['name']))
                self.assertTrue(matches(row, ''))
