import unittest
from pathlib import Path
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from rouge import current_reward_origins as model
from rouge import current_named_reward_origins as named
from rouge.current_reward_origins_view import CurrentRewardOriginsPanel


class CountedRows(list):
    def __iter__(self):
        self.iterations += 1
        return super().__iter__()


class RewardRenderSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_player_and_source_readers_share_one_selection(self):
        for item_id in ('rogue_6_relic_artifact_5', 'rogue_6_relic_cargo_13', 'rogue_6_relic_final_7'):
            with self.subTest(item_id=item_id):
                result = model.reference('relics', item_id)
                self.assertIsNotNone(result)
                keys = [None, 'missing-key', *(row['key'] for row in result['rows'])]
                expected = {key: model.player_text(result, key) for key in keys}
                counted = CountedRows(result['rows'])
                counted.iterations = 0
                result['rows'] = counted
                with patch.object(model, 'reference', return_value=result):
                    panel = CurrentRewardOriginsPanel('relics', item_id)
                self.addCleanup(panel.close)
                for key in keys:
                    with self.subTest(key=key):
                        counted.iterations = 0
                        panel._render(key, False)
                        self.assertEqual(counted.iterations, 1)
                        self.assertEqual(panel.player.toPlainText(), expected[key])

    def test_packet_parses_the_data_bytes_it_has_already_verified(self):
        read_bytes = Path.read_bytes
        for module in (model, named):
            with self.subTest(module=module.__name__):
                reads = []
                target = module.ROOT / module.DATA

                def read(path):
                    if path == target:
                        reads.append(path)
                    return read_bytes(path)

                with patch.object(Path, 'read_bytes', autospec=True, side_effect=read):
                    self.assertIsNotNone(module.packet())
                self.assertEqual(len(reads), 1)


if __name__ == '__main__':
    unittest.main()
