import tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
import rouge.app as module
from rouge.battle_view import BattlePreviewPanel
from rouge.offline_tools_view import OfflineToolsPanel

class EnemyConfigurationViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def test_fixed_preview_unknown_grade_keeps_source_but_no_prediction(self):
        panel=BattlePreviewPanel();self.addCleanup(panel.close);panel.show()
        panel.set_stage('ro6_n_2_3');self.qt.processEvents()
        index=next(i for i in range(panel.enemy_combo.count()) if (panel.enemy_combo.itemData(i) or (None,))[0]=='enemy_2133_shdopl_lancer')
        panel.enemy_combo.setCurrentIndex(index);self.qt.processEvents()
        text=panel.enemy_detail.toPlainText()
        self.assertIn('本关使用专属敌人资料',text);self.assertIn('预计生命值：未知',text)
        self.assertIn('生命值已证分项：6000',text)
        panel.technical.setChecked(True);self.qt.processEvents()
        self.assertIn('原字段投影',panel.enemy_detail.toPlainText())

    def test_offline_query_displays_compiled_counts_and_keeps_declaration_on_refresh(self):
        panel=OfflineToolsPanel();self.addCleanup(panel.close);panel.show()
        panel.select_query('battle','mechanism');panel.run_button.click()
        end=time.monotonic()+8
        while panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(panel._workers);self.assertIsNotNone(panel.result_snapshot())
        self.assertIn('compiled_configuration',panel.result_snapshot())
        self.assertIn('基包配置分项',panel.result_view.toPlainText())
        before=(panel.editor.toPlainText(),panel.result_view.toHtml(),panel.result_snapshot())
        panel.set_stage('ro6_n_2_3');self.qt.processEvents()
        self.assertEqual(before,(panel.editor.toPlainText(),panel.result_view.toHtml(),panel.result_snapshot()))

    def test_mainwindow_rejects_unqualified_target_without_stale_damage_result(self):
        folder=tempfile.TemporaryDirectory(prefix='public-enemy-configuration-');self.addCleanup(folder.cleanup);directory=Path(folder.name)
        for key,name in (('RUN_STATE','run.json'),('OPERATOR_STATE','account.json'),('SETTINGS','settings.json')):
            p=patch.object(module,key,directory/name);p.start();self.addCleanup(p.stop)
        backend=module.DesktopBackend
        p=patch.object(module,'DesktopBackend',lambda _path,callback:backend(directory/'chat',callback));p.start();self.addCleanup(p.stop)
        p=patch.object(module,'list_game_windows',return_value=[]);p.start();self.addCleanup(p.stop)
        window=module.MainWindow();self.addCleanup(window.close);window.show();self.qt.processEvents()
        self.assertFalse(window.auto.isChecked());window.use_run_training.setChecked(False)
        window.select_operator('mechanist');window.calculate();self.assertIsNotNone(window.damage_result)
        window.target_stage.setCurrentIndex(window.target_stage.findData('ro6_n_2_3'));self.qt.processEvents()
        i=next(i for i in range(window.target_enemy.count()) if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_2133_shdopl_lancer')
        window.target_enemy.setCurrentIndex(i);window.calculate();self.qt.processEvents()
        self.assertIsNotNone(window.damage_result)
        self.assertEqual(window.damage_result['result']['run_resolution']['enemy']['fixed_source_qualification']['state'],'stage_constructor_overrides_available')
        window.target_stage.setCurrentIndex(window.target_stage.findData('ro6_n_3_2'));self.qt.processEvents()
        i=next(i for i in range(window.target_enemy.count()) if (window.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_1303_mhshep_2b')
        window.target_enemy.setCurrentIndex(i);window.calculate();self.qt.processEvents()
        self.assertIsNone(window.damage_result);self.assertFalse(window.enemy_comparison_button.isEnabled())
        self.assertIn('不能填零',window.damage_text.toPlainText())
        self.assertTrue(window.isVisible())

if __name__=='__main__':unittest.main()
