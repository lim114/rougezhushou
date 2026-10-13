import unittest
from copy import deepcopy

from rouge.ling_fusion_reference import (ling_fusion_reference,
    format_ling_fusion_reference, fusion_source)


END = {'token_elite': 2, 'endpoint': 'last'}
TRAINING = {'elite': 2, 'level': 90}


class LingFusionReferenceTests(unittest.TestCase):
    def row(self, result, module=3, form='advanced', active=True):
        return next(r for r in result['rows'] if
                    (r['module_level'], r['form'], r['skill_active_declared']) == (module, form, active))

    def test_public_full_endpoint_example_and_same_layer_not_product(self):
        result = ling_fusion_reference(TRAINING, END, 10)
        row = self.row(result); values = row['values']
        self.assertEqual(values['hp'], 7714)
        self.assertAlmostEqual(values['attack'], 2472.4)
        self.assertAlmostEqual(values['defense'], 1184.4)
        self.assertEqual(values['resistance'], 20)
        self.assertAlmostEqual(values['base_interval'], 2.3)
        self.assertEqual((values['block'], values['attack_speed'], values['deployment_slots'], values['damage_type']),
                         (4, 100, 2, '法术'))
        self.assertNotAlmostEqual(values['attack'], 883 * 1.8 * 2)
        self.assertIsNone(row['actual_current_panel'])
        self.assertIsNone(row['actual_skill_active'])
        self.assertIsNone(row['cycle_dps'])

    def test_all_four_modes_and_all_module_stages_stay_separate(self):
        result = ling_fusion_reference(TRAINING, END, 1)
        self.assertEqual(len(result['rows']), 16)
        base = self.row(result, 0, 'basic', False)['values']
        self.assertEqual((base['hp'], base['attack'], base['defense'], base['resistance']), (3607, 823, 423, 10))
        inactive = self.row(result, 0, 'advanced', False)['values']
        self.assertEqual(inactive['hp'], 7214)
        self.assertAlmostEqual(inactive['attack'], 1481.4)
        active = self.row(result, 3, 'advanced', True)['values']
        self.assertAlmostEqual(active['attack'], 1942.6)
        self.assertAlmostEqual(active['defense'], 930.6)
        self.assertEqual(self.row(result, 3, 'basic', True)['values']['deployment_slots'], 1)

    def test_host_skill_and_module_qualification_never_create_fake_panels(self):
        locked = ling_fusion_reference({'elite': 1, 'level': 80}, END, 7)
        self.assertTrue(all(r['state'] == 'host_gate_unmet' for r in locked['rows']))
        self.assertTrue(all(v is None for r in locked['rows'] for v in r['values'].values()))
        low = ling_fusion_reference({'elite': 2, 'level': 59}, END, 10)
        self.assertTrue(all(r['state'] == 'host_gate_unmet' for r in low['rows'] if r['module_level']))
        self.assertEqual(self.row(low, 0)['values']['hp'], 7214)

    def test_all_ranks_and_endpoints_do_not_borrow_host_trust_or_potential(self):
        for elite in range(3):
            for endpoint in ('first', 'last'):
                for rank in range(1, 11):
                    with self.subTest(elite=elite, endpoint=endpoint, rank=rank):
                        selection = {'token_elite': elite, 'endpoint': endpoint}
                        left = ling_fusion_reference(TRAINING, selection, rank)
                        right = ling_fusion_reference({**TRAINING, 'trust': 0, 'potential': 6}, selection, rank)
                        self.assertEqual([r['values'] for r in left['rows']], [r['values'] for r in right['rows']])
                        self.assertTrue(all(r['full_skill_damage'] is None for r in left['rows']))

    def test_inputs_are_preserved_and_invalid_ranks_denied(self):
        before = deepcopy((TRAINING, END)); ling_fusion_reference(TRAINING, END)
        self.assertEqual((TRAINING, END), before)
        for rank in (True, False, None, 0, 11, 1.0, '10'):
            with self.subTest(rank=rank), self.assertRaises(ValueError):
                ling_fusion_reference(TRAINING, END, rank)

    def test_fixed_source_binding_and_chinese_unknown_boundary(self):
        from scripts.build_ling_fusion_source import build
        self.assertEqual(build(), fusion_source())
        text = format_ling_fusion_reference(ling_fusion_reference(TRAINING, END))
        self.assertIn('高级形态', text); self.assertIn('文档算式', text)
        self.assertIn('完整当前面板、伤害与周期未知', text)


class LingFusionViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def test_ling_only_options_recompute_and_invalidate_without_modifying_training(self):
        from rouge.p2_supplemental_token_module_view import SupplementalTokenModuleDialog
        window = SupplementalTokenModuleDialog('char_2023_ling', TRAINING)
        try:
            window.show(); self.app.processEvents()
            self.assertTrue(window.ling_panel.isVisible())
            window.phase.setCurrentIndex(window.phase.findData(2))
            window.endpoint.setCurrentIndex(window.endpoint.findData('last'))
            window.calculate_button.click()
            self.assertIsNone(window.fusion_result)
            window.ling_rank.setCurrentIndex(window.ling_rank.findData(10))
            window.calculate_button.click()
            self.assertEqual(window.ling_forms.rowCount(), 16)
            self.assertEqual(window.ling_forms.item(15, 4).text(), '7714')
            self.assertEqual(window.ling_forms.item(15, 5).text(), '2472.4')
            self.assertIn('高级形态', window.details.toPlainText())
            window.ling_rank.setCurrentIndex(window.ling_rank.findData(1))
            self.assertIsNone(window.result); self.assertIsNone(window.fusion_result)
            self.assertEqual(window.ling_forms.rowCount(), 0)
            window.calculate_button.click()
            self.assertEqual(window.ling_forms.item(15, 5).text(), '1942.6')
            self.assertEqual(window.training, TRAINING)
        finally:
            window.close(); window.deleteLater(); self.app.processEvents()

    def test_magallan_has_no_ling_form_or_skill_options(self):
        from rouge.p2_supplemental_token_module_view import SupplementalTokenModuleDialog
        window = SupplementalTokenModuleDialog('char_248_mgllan', TRAINING)
        try:
            self.assertFalse(hasattr(window, 'ling_rank'))
            self.assertFalse(hasattr(window, 'ling_panel'))
            self.assertFalse(hasattr(window, 'ling_forms'))
        finally:
            window.close(); window.deleteLater(); self.app.processEvents()


if __name__ == '__main__':
    unittest.main()
