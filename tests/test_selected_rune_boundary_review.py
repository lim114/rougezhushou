from collections import Counter
from unittest.mock import patch
import unittest

from rouge import relic_attributes as runes, supplemental_run as run
from rouge.damage import calculate_damage
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment


class SelectedRuneBoundaryReviewTests(unittest.TestCase):
    def test_supplemental_calculation_consumes_its_classified_runes(self):
        with patch.object(run,'is_attribute_rune',wraps=runes.is_attribute_rune) as classify:
            with patch.object(runes,'is_attribute_rune',classify):
                result=run.run_skill_reference(defaults(),environment(['rogue_6_relic_legacy_27']))
        # Only the adapter's own effects: other preparation stages can classify
        # their separate inputs. Each object received by this adapter is counted.
        selected=result['attribute_resolution']['runes']
        self.assertTrue(selected)
        counts=Counter(id(call.args[0]) for call in classify.call_args_list)
        self.assertTrue(all(n==1 for n in counts.values()),counts)

    def test_token_finish_classifies_each_applicable_effect_once(self):
        from rouge import relics
        original=relics.finish;calls=[]

        def finish(*args,**kwargs):
            with patch.object(runes,'is_attribute_rune',wraps=runes.is_attribute_rune) as qualify:
                result=original(*args,**kwargs)
            calls.extend(qualify.call_args_list)
            return result

        with patch.object(relics,'finish',side_effect=finish):
            result=calculate_damage({'operator':'char_110_deepcl','skill':1,'elite':2,'level':70,
                'module_id':'uniequip_002_deepcl','module_level':3,
                'relic_ids':['rogue_6_relic_legacy_134','rogue_6_relic_legacy_91']})
        counts=Counter(id(call.args[0]) for call in calls)
        self.assertTrue(counts)
        self.assertTrue(all(n==1 for n in counts.values()),counts)
        token=next(t for t in result['relic_token_stats'] if t['id']=='token_10001_deepcl_tentac')
        self.assertAlmostEqual(token['hp'],3014.15)
        self.assertAlmostEqual(token['regeneration_rate'],30.1415)
