from unittest import TestCase
from unittest.mock import patch
from rouge import supplemental_run as run
from rouge.supplemental_skills import defaults,skill_reference,MissingHpExceedsMaximum
from tests.test_supplemental_run_141 import environment


class BaselineErrorTests(TestCase):
    def test_unexpected_baseline_value_error_is_exposed(self):
        original=run._skill_reference
        calls=[]
        def calculate(*args):
            calls.append(args)
            if len(calls)==2:raise ValueError('internal calculation failure')
            return original(*args)
        with patch.object(run,'_skill_reference',side_effect=calculate):
            with self.assertRaisesRegex(ValueError,'internal calculation failure'):
                run.run_skill_reference(defaults(),environment())
        self.assertEqual(len(calls),2)

    def test_self_heal_overflow_has_specific_input_error(self):
        preview=defaults('char_209_ardign');preview['missing_hp']=100000
        with self.assertRaises(MissingHpExceedsMaximum):skill_reference(preview)
