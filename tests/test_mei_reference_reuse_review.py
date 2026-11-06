from unittest.mock import patch
from copy import deepcopy
import unittest

from rouge import mei_module_static_reference as reference
from rouge import mei_module_reference as parameters
from rouge.damage import calculate_damage
from rouge.catalog import catalog


class MeiReferenceReuseReviewTests(unittest.TestCase):
    def test_standalone_qualification_resolves_module_once(self):
        class Modules(list):
            scans=0
            def __iter__(self):
                self.scans+=1
                return super().__iter__()
        profile=deepcopy(catalog()['operators']['char_133_mm'])
        profile['modules']=Modules(profile['modules'])
        scenario={'operator':'char_133_mm','skill':1,'elite':2,'level':40,
                  'module_id':'uniequip_002_mm','module_level':1}
        with patch.object(reference,'catalog',return_value={'operators':{'char_133_mm':profile}}):
            result=reference.qualification(scenario)
        self.assertTrue(result['qualified'])
        self.assertEqual(profile['modules'].scans,1)

    def test_explicit_empty_parts_stay_unavailable(self):
        profile=catalog()['operators']['char_133_mm']
        scenario={'operator':'char_133_mm','module_id':'uniequip_002_mm','module_level':1}
        for parts in (None,[]):
            self.assertIsNone(parameters.reference(profile,scenario,parts)[0])

    def test_finalizer_reuses_parameters_already_computed_by_combat(self):
        scenario={'operator':'char_133_mm','skill':1,'elite':2,'level':40,
                  'module_id':'uniequip_002_mm','module_level':1,
                  reference.FLAG:True,'relic_context':{reference.MOTION:'fly'}}
        with patch.object(parameters,'reference',wraps=parameters.reference) as read:
            result=calculate_damage(scenario)
        self.assertEqual(read.call_count,1)
        self.assertTrue(result['mei_module_static_reference']['qualified']['qualified'])

    def test_unavailable_parameter_result_is_not_queried_again(self):
        scenario={'operator':'char_133_mm','skill':1,'elite':2,'level':39,
                  'module_id':'uniequip_002_mm','module_level':1,
                  reference.FLAG:True}
        with patch.object(parameters,'reference',wraps=parameters.reference) as read:
            result=calculate_damage(scenario)
        self.assertEqual(read.call_count,1)
        self.assertNotIn('mei_airborne_module_reference',result)
        self.assertNotIn('mei_module_static_reference',result)

    def test_enabled_reference_qualifies_once_and_reports_same_conditions(self):
        scenario={'operator':'char_133_mm','skill':1,'elite':2,'level':40,
                  'module_id':'uniequip_002_mm','module_level':1,
                  reference.FLAG:True,'relic_context':{reference.MOTION:'fly'}}
        with patch.object(reference,'_qualification',wraps=reference._qualification) as qualify:
            result=calculate_damage(scenario)
        self.assertEqual(qualify.call_count,1)
        self.assertEqual(result['mei_module_static_reference']['qualified'],reference.qualification(scenario))

    def test_disabled_reference_does_not_qualify(self):
        with patch.object(reference,'_qualification',wraps=reference._qualification) as qualify:
            result=calculate_damage({'operator':'char_133_mm','skill':1,reference.FLAG:False})
        qualify.assert_not_called()
        self.assertNotIn('mei_module_static_reference',result)
