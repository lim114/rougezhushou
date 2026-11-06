from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import unittest
from rouge import current_peace, current_resting


class EventIconBoundaryTests(unittest.TestCase):
    def test_internal_record_errors_propagate(self):
        for model in (current_peace, current_resting):
            original = model.packet()
            for field, value, error in (('file', None, TypeError), ('bytes', None, KeyError), ('sha256', None, KeyError)):
                record = deepcopy(original)
                if field == 'file':
                    record['data']['icon_reference'][field] = value
                else:
                    del record['data']['icon_reference'][field]
                with self.subTest(module=model.__name__, field=field), patch.object(model, 'packet', return_value=record):
                    with self.assertRaises(error):
                        model.icon_bytes()

    def test_file_failure_keeps_text_available(self):
        for model in (current_peace, current_resting):
            record = model.packet()
            with self.subTest(module=model.__name__), patch.object(model, 'packet', return_value=record), patch.object(Path, 'read_bytes', side_effect=OSError('unreadable')):
                self.assertIsNone(model.icon_bytes())
                self.assertIsNotNone(model.reference())

    def test_wrong_image_bytes_are_not_returned(self):
        for model in (current_peace, current_resting):
            record = model.packet()
            with self.subTest(module=model.__name__), patch.object(model, 'packet', return_value=record), patch.object(Path, 'read_bytes', return_value=b'not an image'):
                self.assertIsNone(model.icon_bytes())
