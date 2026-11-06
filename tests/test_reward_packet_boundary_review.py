import unittest
from pathlib import Path
from unittest.mock import patch
from rouge import current_reward_origins as model


class RewardPacketBoundaryTests(unittest.TestCase):
    def test_internal_row_errors_propagate(self):
        for error in (KeyError('internal'),TypeError('internal'),AttributeError('internal')):
            with self.subTest(error=type(error).__name__),patch.object(model,'source_rows',side_effect=error):
                with self.assertRaises(type(error)):model.packet()

    def test_declared_source_identity_mismatch_remains_unavailable(self):
        with patch.object(model,'source_rows',side_effect=ValueError('Named reward identity differs')):
            self.assertIsNone(model.packet())

    def test_provider_internal_error_propagates(self):
        with patch.object(model.memory,'packet',side_effect=ValueError('internal provider defect')):
            with self.assertRaisesRegex(ValueError,'internal provider'):model.packet()

    def test_file_read_failure_remains_unavailable(self):
        with patch.object(Path,'read_bytes',side_effect=OSError('unreadable')):
            self.assertIsNone(model.packet())

    def test_member_link_still_rejected(self):
        original=Path.is_symlink
        def linked(path):
            return path==model.ROOT/model.DATA or original(path)
        with patch.object(Path,'is_symlink',linked):
            self.assertIsNone(model.packet())
