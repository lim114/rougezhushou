import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.reference_copy import mechanism_copy
from rouge import current_hanko_view as hanko, current_sun_boss_view as sun


class DocumentPanelSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])

    def test_hanko_selection_and_topic_lookup_once(self):
        panel = hanko.CurrentHankoPanel('ro6_b_1')
        self.addCleanup(panel.close)
        with patch.object(hanko.model, 'entity', wraps=hanko.model.entity) as lookup:
            panel.entities.select_value('0')
            lookup.assert_called_once()
        with patch.object(hanko.model, 'entity', wraps=hanko.model.entity) as lookup:
            panel.topic.setCurrentIndex(1)
            lookup.assert_called_once()
        self.assertEqual(panel.player.toPlainText(), mechanism_copy(hanko.model.player_text(panel.result, panel.selected_key, panel.topic.currentData()), panel.notice.property('referenceBaseText'))[0])

    def test_sun_selection_topic_and_card_lookup_once(self):
        panel = sun.CurrentSunBossPanel('ro6_b_7')
        self.addCleanup(panel.close)
        with patch.object(sun.model, 'entity', wraps=sun.model.entity) as lookup:
            panel.forms.select_value('0')
            lookup.assert_called_once()
        with patch.object(sun.model, 'entity', wraps=sun.model.entity) as lookup:
            panel.topic.setCurrentIndex(panel.topic.findData('skills'))
            lookup.assert_called_once()
        with patch.object(sun.model, 'entity', wraps=sun.model.entity) as lookup:
            panel.card.setCurrentIndex(1)
            lookup.assert_called_once()
        self.assertEqual(panel.player.toPlainText(), mechanism_copy(sun.model.player_text(panel.result, panel.selected_key, panel.topic.currentData(), panel.card.currentData()), panel.notice.property('referenceBaseText'))[0])
