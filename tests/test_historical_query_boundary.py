import unittest
from unittest.mock import Mock, patch
from rouge import player_map_reference as maps, public_node_statistics as statistics
from tests.test_node_card_source_review import public_example


class HistoricalQueryBoundaryTests(unittest.TestCase):
    def test_invalid_distance_does_not_query_index(self):
        index = Mock()
        for distance in (None, True, -1, 101, '2'):
            self.assertEqual(maps.historical_rows('zone_1', distance, index), ())
        index.rows.assert_not_called()

    def test_internal_query_errors_surface(self):
        for error in (OSError, ValueError, TypeError, KeyError):
            with self.subTest(error=error):
                index = Mock();index.rows.side_effect = error('internal query')
                with self.assertRaises(error):
                    maps.historical_rows('zone_1', 2, index)

    def test_absent_category_is_not_zero_but_explicit_zero_is_retained(self):
        data = public_example(100)
        data['counts']['safe-house'] = {'1': {'3': 2}}
        data['metadata']['sampleCount'] = 102
        rows = statistics.frequency_rows(data, '0', 2)
        self.assertEqual([(r['type'], r['count'], r['frequency']) for r in rows],
                         [('rogue-trader', 100, 1), ('encounter', 0, 0)])
        self.assertEqual(rows, statistics.FrequencyIndex(data).rows('0', 2))
        self.assertEqual(statistics.frequency_rows(data, '0', 3), [])
