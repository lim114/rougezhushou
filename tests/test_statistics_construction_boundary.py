from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from rouge import public_node_statistics as model, player_map_reference as maps
from rouge.node_statistics_source import NodeStatisticsSource
from tests.test_node_card_source_review import public_example


class StatisticsConstructionBoundaryTests(unittest.TestCase):
    def tearDown(self):
        maps.default_frequencies.cache_clear()

    def test_validated_index_errors_are_not_replaced_by_empty_statistics(self):
        with TemporaryDirectory() as folder, patch.object(model, 'load', return_value=public_example()):
            for error in (OSError, ValueError, KeyError, TypeError):
                with self.subTest(error=error), patch.object(model.FrequencyIndex, 'from_validated', side_effect=error('internal index')):
                    with self.assertRaises(error):
                        NodeStatisticsSource(Path(folder) / 'nodes.json')
                    maps.default_frequencies.cache_clear()
                    with self.assertRaises(error):
                        maps.default_frequencies()

    def test_loading_failures_keep_empty_index(self):
        with TemporaryDirectory() as folder:
            for error in (OSError, ValueError, KeyError, TypeError):
                with self.subTest(error=error), patch.object(model, 'load', side_effect=error('input')):
                    source = NodeStatisticsSource(Path(folder) / 'nodes.json')
                    self.assertIsNone(source.data)
                    self.assertIsNone(source.index.identity)
                    maps.default_frequencies.cache_clear()
                    self.assertIsNone(maps.default_frequencies().identity)
