from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge import supplemental_skills as skills
from rouge import supplemental_enemies as enemies
from rouge import supplemental_run as run
from tests.test_supplemental_run_141 import environment


class EnemyCultivationReviewTests(unittest.TestCase):
    def test_fixed_cultivation_resolved_once_and_result_snapshots_are_independent(self):
        preview=skills.defaults();env=environment(['rogue_6_relic_legacy_84'])
        selection=enemies.enemy_defaults(env)
        selection.update(enemies=selection['enemies'][:2],grades=[4,5])
        original=deepcopy((preview,env,selection))
        with patch.object(skills,'operator_attributes',wraps=skills.operator_attributes) as resolve:
            result=enemies.compare_fixed_enemies(preview,env,selection)
        self.assertEqual(resolve.call_count,1)
        self.assertEqual((preview,env,selection),original)
        first,second=result['variants'][:2]
        before=deepcopy(second['result'])
        first['result']['attributes']['attack']=-1
        first['result']['run_attributes']['hp']=-1
        first['result']['preview']['level']=1
        self.assertEqual(second['result'],before)

    def test_original_difficulty_is_still_validated_before_grade_override(self):
        for value in (True,16):
            with self.subTest(value=value):
                env=environment();env['run_config']={'difficulty':{'value':value}}
                selection=enemies.enemy_defaults(environment())
                with self.assertRaisesRegex(ValueError,'保密等级需要0–15'):
                    enemies.compare_fixed_enemies(skills.defaults(),env,selection)

    def test_public_run_still_validates_cultivation_before_environment(self):
        preview=skills.defaults();preview['level']=True
        with self.assertRaisesRegex(ValueError,'level需要整数'):
            run.run_skill_reference(preview,None)

    def test_healing_gap_error_is_not_lost_by_prepared_cultivation(self):
        preview=skills.defaults('char_209_ardign');preview['missing_hp']=100000
        env=environment();selection=enemies.enemy_defaults(env)
        with self.assertRaisesRegex(ValueError,'自身生命缺口不能超过'):
            enemies.compare_fixed_enemies(preview,env,selection)
