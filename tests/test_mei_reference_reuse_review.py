from unittest.mock import patch
import unittest

from rouge import mei_module_static_reference as reference
from rouge.damage import calculate_damage


class MeiReferenceReuseReviewTests(unittest.TestCase):
    def test_enabled_reference_qualifies_once_and_reports_same_conditions(self):
        scenario={'operator':'char_133_mm','skill':1,'elite':2,'level':40,
                  'module_id':'uniequip_002_mm','module_level':1,
                  reference.FLAG:True,'relic_context':{reference.MOTION:'fly'}}
        with patch.object(reference,'qualification',wraps=reference.qualification) as qualify:
            result=calculate_damage(scenario)
        self.assertEqual(qualify.call_count,1)
        self.assertEqual(result['mei_module_static_reference']['qualified'],reference.qualification(scenario))

    def test_disabled_reference_does_not_qualify(self):
        with patch.object(reference,'qualification',wraps=reference.qualification) as qualify:
            result=calculate_damage({'operator':'char_133_mm','skill':1,reference.FLAG:False})
        qualify.assert_not_called()
        self.assertNotIn('mei_module_static_reference',result)
