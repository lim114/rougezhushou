from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtCore import QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from rouge import current_agency_view as agency, current_peace_view as peace, current_scout_view as scout, current_shadow_view as shadow


class ImageFallbackReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        image = QImage(8, 8, QImage.Format.Format_ARGB32)
        image.fill(0xffeeeeee)
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, 'PNG')
        cls.png = bytes(data)

    def test_reward_cards_valid_bad_missing_and_hidden(self):
        cases = ((peace, peace.CurrentPeacePanel._update_specific, 'shows_reward', 'reward_icon', 'reward_card'),
                 (scout, scout.CurrentScoutPanel._update_return_card, 'shows_return_item', 'return_icon', 'return_card'),
                 (shadow, shadow.CurrentShadowPanel._update_reward, 'shows_reward', 'reward_icon', 'reward_card'))
        for module, update, predicate, icon_name, card_name in cases:
            label, card = QLabel(), QWidget()
            panel = SimpleNamespace(result={'test': True}, scene_id='scene', choice_id='choice', completion_controls=QWidget())
            setattr(panel, icon_name, label)
            setattr(panel, card_name, card)
            for raw in (self.png, b'broken image', None):
                with self.subTest(module=module.__name__, raw=raw is None), patch.object(module.model, predicate, return_value=True), patch.object(module.model, 'icon_bytes', return_value=raw) as read:
                    update(panel, {'role': 'join'})
                    read.assert_called_once_with()
                    self.assertFalse(card.isHidden())
                    if raw == self.png:
                        self.assertFalse(label.pixmap().isNull())
                    else:
                        self.assertIn('图片暂缺', label.text())
                        self.assertTrue(label.pixmap().isNull())
            with patch.object(module.model, predicate, return_value=False), patch.object(module.model, 'icon_bytes') as read:
                update(panel, None)
                read.assert_not_called()
                self.assertTrue(card.isHidden())
                self.assertEqual(label.text(), '')

    def test_profession_pair_valid_bad_missing_and_hidden(self):
        panel = SimpleNamespace(offer_controls=QWidget(), pair_icons=[QLabel(), QLabel()], pair_label=QLabel())
        choice = {'role': 'promoted', 'profession_pair': ['先锋', '近卫']}
        for raw in (self.png, b'broken image', None):
            with self.subTest(raw=raw is None), patch.object(agency.model, 'icon_bytes', return_value=raw) as read:
                agency.CurrentAgencyPanel._update_professions(panel, choice)
                self.assertEqual(read.call_count, 2)
                self.assertIn('先锋或近卫', panel.pair_label.text())
                for label in panel.pair_icons:
                    if raw == self.png:
                        self.assertFalse(label.pixmap().isNull())
                    else:
                        self.assertIn('图标暂缺', label.text())
                        self.assertTrue(label.pixmap().isNull())
        with patch.object(agency.model, 'icon_bytes') as read:
            agency.CurrentAgencyPanel._update_professions(panel, None)
            read.assert_not_called()
            self.assertTrue(panel.offer_controls.isHidden())
            self.assertEqual(panel.pair_label.text(), '')
            self.assertTrue(all(label.text() == '' for label in panel.pair_icons))
