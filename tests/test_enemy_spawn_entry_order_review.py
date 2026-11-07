from unittest import TestCase
from unittest.mock import patch
from rouge import current_enemy_spawns as model


class EnemySpawnEntryOrderTests(TestCase):
    def test_missing_stage_does_not_load_scope(self):
        with patch.object(model.battle,'stage_reference',return_value=None),patch.object(model,'evidence') as scope:
            self.assertIsNone(model.stage_reference('missing','0'))
        scope.assert_not_called()

    def test_invalid_inputs_do_not_load_either_source(self):
        with patch.object(model.battle,'stage_reference') as stage,patch.object(model,'evidence') as scope:
            for args in [(None,'0'),('stage',None),(True,'0'),('stage',False)]:
                self.assertIsNone(model.stage_reference(*args))
        stage.assert_not_called();scope.assert_not_called()

    def test_present_stage_still_requires_scope(self):
        with patch.object(model.battle,'stage_reference',return_value={'source_identity':'source'}),patch.object(model,'evidence',return_value=None) as scope:
            self.assertIsNone(model.stage_reference('stage','0'))
        scope.assert_called_once_with()
