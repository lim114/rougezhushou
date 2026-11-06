from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge import supplemental_enemies as subject
from rouge.supplemental_run import ENVIRONMENT_KEYS
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment


class SupplementalEnemyPreparationReviewTests(unittest.TestCase):
    def test_candidate_source_scanned_once_without_losing_ambiguity_rejection(self):
        env=environment();preview=subject.enemy_defaults(env)
        stages=deepcopy(subject.stage_previews());sid=preview['stage_id']
        scans=[]

        class Candidates(list):
            def __iter__(self):
                scans.append(1)
                return super().__iter__()

        stages[sid]['possible_enemies']=Candidates(stages[sid]['possible_enemies'])
        with patch.object(subject,'stage_previews',return_value=stages):
            result=subject.compare_fixed_enemies(defaults(),env,preview)
        self.assertEqual(len(scans),1)
        self.assertEqual([r['enemy_id'] for r in result['variants']],
                         [r['enemy_id'] for r in preview['enemies']])
        stages[sid]['possible_enemies'].append(deepcopy(stages[sid]['possible_enemies'][0]))
        with patch.object(subject,'stage_previews',return_value=stages):
            with self.assertRaisesRegex(ValueError,'唯一匹配'):
                subject.compare_fixed_enemies(defaults(),env,preview)

    def test_environment_prepared_once_per_grade_and_results_remain_independent(self):
        env=environment();preview=subject.enemy_defaults(env)
        preview.update(enemies=preview['enemies'][:2],grades=[4,5])
        before=deepcopy(env);copied=[]

        def copy(value):
            if type(value) is dict and set(value)==ENVIRONMENT_KEYS:copied.append(1)
            return deepcopy(value)

        with patch.object(subject,'deepcopy',side_effect=copy):
            result=subject.compare_fixed_enemies(defaults(),env,preview)
        self.assertEqual(len(copied),3)  # input snapshot plus one per grade
        self.assertEqual([r['grade'] for r in result['variants']],[4,5,4,5])
        result['variants'][0]['result']['environment']['run_config']['difficulty']['value']=99
        self.assertEqual(result['variants'][2]['result']['environment']['run_config']['difficulty']['value'],4)
        self.assertEqual(env,before)
