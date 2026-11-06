import unittest
from unittest.mock import patch
from rouge import current_sun_boss as model


class SunCardReuseTests(unittest.TestCase):
    def test_each_card_and_text_resolves_once_and_card_is_independent(self):
        for stage in model.STAGES:
            result = model.reference(stage)
            for row in result['rows']:
                for original in model.cards(result, row['key']):
                    with self.subTest(stage=stage, key=row['key'], index=original['index']):
                        with patch.object(model, 'entity', wraps=model.entity) as lookup:
                            selected = model.card(result, row['key'], original['index'])
                            lookup.assert_called_once()
                        self.assertEqual(selected, original)
                        selected['title'] = 'changed locally'
                        self.assertEqual(model.card(result, row['key'], original['index']), original)
                        with patch.object(model, 'entity', wraps=model.entity) as lookup:
                            text = model.player_text(result, row['key'], 'skills', original['index'])
                            lookup.assert_called_once()
                        self.assertIn(original['title'], text)

    def test_invalid_card_or_entity_remains_unavailable(self):
        result = model.reference(model.STAGES[0])
        key = result['rows'][0]['key']
        for index in (None, False, 1.0, '1', -10000):
            self.assertIsNone(model.card(result, key, index))
        for key in (None, 'missing', 0):
            self.assertIsNone(model.card(result, key, 0))
