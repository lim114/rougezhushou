import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import current_exchange_reference as model
from rouge.current_exchange_view import CurrentExchangePanel


class ExchangeTargetContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_wrong_types_raise_without_loading(self):
        for category, key in ((None, 'id'), ('relics', False), ([], 'id'), ('choices', {})):
            with self.subTest(category=category, key=key), patch.object(model, 'packet') as load:
                with self.assertRaises(TypeError):
                    model.target_entry(category, key)
                load.assert_not_called()

    def test_missing_required_selection_fields_raise(self):
        for missing in ('item_id', 'group_id'):
            target = {'tab': 'document', 'item_id': None, 'group_id': None}
            del target[missing]
            with self.subTest(missing=missing), self.assertRaises(KeyError):
                CurrentExchangePanel(target)

    def test_none_values_are_valid_unselected_state(self):
        panel = CurrentExchangePanel({'tab': 'document', 'item_id': None, 'group_id': None})
        self.addCleanup(panel.close)
        self.assertEqual(panel.tabs.currentIndex(), 1)
        self.assertIsNone(panel.item_id)
        self.assertIsNone(panel.group_id)
