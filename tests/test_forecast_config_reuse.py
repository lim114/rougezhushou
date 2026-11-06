import unittest
from unittest.mock import patch
from rouge import current_enemy_forecast as model
from rouge import current_battle_reference as battle


class ForecastConfigReuseTests(unittest.TestCase):
    def test_difficulty_and_zone_share_one_config_snapshot(self):
        stage = battle.stage_reference('ro6_n_1_1')
        config = {'difficulty': {'value': 15}, 'zone': {'id': 'zone_1'}}
        expected = model.forecasts(stage, config)
        with patch.object(model, 'config_data', wraps=model.config_data) as read:
            self.assertEqual(model.forecasts(stage, config), expected)
        read.assert_called_once()

    def test_empty_request_does_not_load_configuration(self):
        with patch.object(model, 'config_data', side_effect=AssertionError('unused configuration')):
            self.assertEqual(model.forecasts(None, {'difficulty': {'value': 15}}), {})
            self.assertEqual(model.forecasts({}, {}), {})
