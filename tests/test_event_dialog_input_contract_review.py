from unittest import TestCase
from unittest.mock import patch
from rouge import current_event_directory as model
from rouge.current_event_directory_view import make_event_dialog


class EventDialogInputContractTests(TestCase):
    def test_internal_wrong_target_shape_is_not_missing_reference(self):
        for target, error in [(None, TypeError), ({}, KeyError), ({'event': None}, TypeError)]:
            with self.subTest(target=target), patch.object(model, 'reference') as read:
                with self.assertRaises(error):
                    make_event_dialog(target)
                read.assert_not_called()

    def test_source_lost_after_resolve_still_returns_unavailable(self):
        result = model.reference('flows321:button')
        target = model.resolve(result)
        self.assertIsNotNone(target)
        with patch.object(model, 'reference', return_value=None):
            self.assertIsNone(make_event_dialog(target))
