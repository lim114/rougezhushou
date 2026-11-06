from unittest import TestCase
from unittest.mock import patch
from rouge import current_event_directory as model


class EventDirectoryErrorBoundaryTests(TestCase):
    def test_file_access_and_path_rejection_remain_unavailable(self):
        for error in (OSError('read failed'), ValueError('linked source')):
            with self.subTest(error=error), patch.object(model, '_file', side_effect=error):
                self.assertIsNone(model.packet())

    def test_internal_source_access_type_bug_is_not_missing_data(self):
        with patch.object(model, '_file', side_effect=TypeError('programming error')):
            with self.assertRaises(TypeError):
                model.packet()

    def test_post_load_snapshot_errors_are_exposed(self):
        for error in (ValueError('snapshot mismatch'), KeyError('field'), TypeError('type'), AttributeError('attribute'), StopIteration(), RecursionError()):
            with self.subTest(error=error), patch.object(model, '_snapshot', side_effect=error):
                with self.assertRaises(type(error)):
                    model.packet()
