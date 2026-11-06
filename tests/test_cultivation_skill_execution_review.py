from unittest import TestCase
from unittest.mock import patch
from rouge import cultivation_comparison as model
from tests.test_cultivation_comparison_140 import proposal


class SkillExecutionTests(TestCase):
    def test_calculation_failures_are_not_input_messages(self):
        for identity,target in [('mechanist','_calculate_prepared'),('char_208_melan','_skill_reference')]:
            with self.subTest(identity=identity):
                scenario={'operator':identity,'skill':1,'skill_rank':7}
                with patch.object(model,target,side_effect=ValueError('internal execution defect')):
                    with self.assertRaisesRegex(ValueError,'internal execution defect'):
                        model.compare_cultivation(scenario,{'proposals':[proposal('基准')]})

    def test_operator_classification_is_reused_across_proposals(self):
        original=model.catalog
        with patch.object(model,'catalog',wraps=original) as catalog:
            model.compare_cultivation({'operator':'mechanist','skill':1,'skill_rank':7},
                {'proposals':[proposal('基准'),proposal('另一项',level=55)]})
        self.assertEqual(catalog.call_count,1)
