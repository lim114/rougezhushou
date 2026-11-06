import unittest
from unittest.mock import patch
from rouge import current_hanko as model


class HankoCardReuseTests(unittest.TestCase):
    def test_card_and_text_resolve_each_entity_once(self):
        for stage in model.STAGES:
            result = model.reference(stage)
            for row in result['rows']:
                for topic, _ in model.topics(result, row['key']):
                    with self.subTest(stage=stage, key=row['key'], topic=topic):
                        with patch.object(model, 'entity', wraps=model.entity) as read:
                            card = model.selected_card(result, row['key'], topic)
                            read.assert_called_once()
                        with patch.object(model, 'entity', wraps=model.entity) as read:
                            text = model.player_text(result, row['key'], topic)
                            read.assert_called_once()
                        self.assertIn(card['body'], text)

    def test_foreign_topic_and_missing_entity_remain_rejected(self):
        result = model.reference('ro6_b_1')
        for key in ('missing', None, 0):
            self.assertIsNone(model.selected_card(result, key, 'blink'))
        for row in result['rows']:
            self.assertIsNone(model.selected_card(result, row['key'], 'invalid'))
