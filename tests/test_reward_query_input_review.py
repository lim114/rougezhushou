import unittest
from unittest.mock import patch
from rouge import current_reward_origins, current_named_reward_origins, current_critical_reward_origins


class RewardQueryInputTests(unittest.TestCase):
    def test_invalid_types_raise_before_loading(self):
        for model in (current_reward_origins, current_named_reward_origins, current_critical_reward_origins):
            for category, item in ((True, 'id'), ('relics', None), ([], 'id'), ('relics', {})):
                with self.subTest(module=model.__name__, category=category, item=item), patch.object(model, 'packet') as load:
                    with self.assertRaises(TypeError):
                        model.reference(category, item)
                    load.assert_not_called()

    def test_unsupported_category_is_normal_absence(self):
        for model in (current_reward_origins, current_named_reward_origins, current_critical_reward_origins):
            with self.subTest(module=model.__name__), patch.object(model, 'packet') as load:
                self.assertIsNone(model.reference('scenes', 'id'))
                load.assert_not_called()
