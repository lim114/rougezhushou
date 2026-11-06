import unittest
from pathlib import Path
from unittest.mock import patch

from rouge import current_critical_reward_origins as model


class CriticalRewardSourceReuseTests(unittest.TestCase):
    def test_data_file_is_read_once(self):
        original = Path.read_bytes
        reads = []
        target = model.ROOT / model.DATA

        def read(path):
            if path == target:
                reads.append(path)
            return original(path)

        with patch.object(Path, 'read_bytes', autospec=True, side_effect=read):
            self.assertIsNotNone(model.packet())
        self.assertEqual(len(reads), 1)

    def test_exit_source_loaded_once_per_critical_packet(self):
        with patch.object(model.exit_flow, 'packet', wraps=model.exit_flow.packet) as read:
            self.assertIsNotNone(model.packet())
        self.assertEqual(read.call_count, 1)

    def test_source_rows_use_supplied_exit_snapshot(self):
        current = model.version.packet()['current']['details']
        packets = [provider.packet() for provider in model.PROVIDERS]
        expected = model.source_rows(current, *packets)
        with patch.object(model.exit_flow, 'packet', side_effect=AssertionError('unexpected reread')):
            actual = model.source_rows(current, *packets)
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
