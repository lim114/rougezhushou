from copy import deepcopy
from unittest.mock import patch
import unittest

from rouge.catalog import catalog, operator_attributes
from rouge.operator_engine import Combat
from rouge.damage import calculate_damage


class CombatRecipientPreparationReviewTests(unittest.TestCase):
    def test_combat_shares_module_lookup_with_recipient_reference(self):
        class Modules(list):
            scans = 0

            def __iter__(self):
                self.scans += 1
                return super().__iter__()

        for operator, identity in (
            ('char_298_susuro', 'uniequip_002_susuro'),
            ('char_196_sunbr', 'uniequip_002_sunbr'),
            ('char_2025_shu', 'uniequip_002_shu'),
        ):
            for module_id, level in ((identity, None), (identity, 1), (None, None)):
                with self.subTest(operator=operator, module=module_id, level=level):
                    data = deepcopy(catalog())
                    profile = data['operators'][operator]
                    profile['modules'] = Modules(profile['modules'])
                    stage = 3 if module_id else 0
                    attributes = operator_attributes(operator, level=level, module_id=module_id, module_level=stage)
                    scenario = {'operator': operator, 'skill': 1, 'base_attack': attributes['attack'],
                                'module_id': module_id, 'module_level': stage, 'level': level}
                    with patch('rouge.operator_engine.catalog', return_value=data):
                        combat = Combat(scenario, attributes)
                    reference = (combat.susuro_module_healing_reference if operator == 'char_298_susuro'
                                 else combat.guardian_module_healing_reference)
                    self.assertEqual(reference is not None, module_id is not None and level is None)
                    self.assertEqual(profile['modules'].scans, 1)

    def test_public_entry_rejects_invalid_stages_before_combat(self):
        for stage in (0, -1, 4, True, 1.0, '1', None):
            with self.subTest(stage=stage), patch('rouge.operator_engine.Combat') as combat:
                with self.assertRaises(ValueError):
                    calculate_damage({'operator': 'char_298_susuro', 'skill': 1,
                                      'module_id': 'uniequip_002_susuro', 'module_level': stage})
                combat.assert_not_called()
