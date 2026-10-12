"""Default-skin static choices in the real window class, public temporary state."""
import unittest
from tests import test_batch185_mainwindow as setup_module


class StaticActionWindowTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp

    def test_mechanist_s2_combo_uses_bound_segments_and_default_stays_unselected(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('mechanist')
        self.window.skill.setCurrentIndex(self.window.skill.findData(2));self.qt.processEvents()
        combo=self.window.skill_animation_reference
        self.assertIsNone(combo.currentData());self.assertEqual(combo.count(),4)
        ids=[combo.itemData(i) for i in range(1,combo.count())]
        self.assertEqual(ids,['char_4230_mcnist:Front:Skill_2_Loop',
            'char_4230_mcnist:Front:Skill_Down_2_Loop','char_4230_mcnist:Back:Skill_2_Loop'])
        self.assertIn('静态动作选择已核验',combo.toolTip())
        combo.setCurrentIndex(1);self.window.calculate();self.qt.processEvents()
        self.assertIsNotNone(self.window.damage_result)
        self.assertEqual(self.window.damage_result['scenario']['timing']['animation_reference'],ids[0])
        self.assertTrue(self.window.isVisible())
