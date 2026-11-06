from unittest import TestCase
from unittest.mock import patch
from rouge import current_map_position as model


class MapPositionEntryOrderTests(TestCase):
    def test_invalid_identity_does_not_read_source_packet(self):
        with patch.object(model,'packet') as packet:
            for identity in (None,False,1,[],{}):
                with self.subTest(identity=identity):self.assertIsNone(model.stage_reference(identity))
        packet.assert_not_called()

    def test_string_request_still_requires_current_source(self):
        with patch.object(model,'packet',return_value=None) as packet:
            self.assertIsNone(model.stage_reference('ro6_n_2_1'))
        packet.assert_called_once_with()
