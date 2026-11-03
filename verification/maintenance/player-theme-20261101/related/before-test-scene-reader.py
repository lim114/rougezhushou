"""One source-bound player reader for map, recent battle and recent event flows."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from types import ModuleType,SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtCore import QCoreApplication,QEvent,Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication,QWidget
from rouge import current_battle_reference as model
from rouge.player_map_reader import make_reader,REFERENCE_STYLE
from rouge.player_scene_battle import SceneBattlePanel
from rouge.player_recent_scene import RecentScenePanel

ROOT=Path(__file__).resolve().parents[1]


class SceneReaderReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def scene(self):
        run=SimpleNamespace(state={'id':'public-reader-fixture','last_node_content':{'kind':'battle','stage_id':'ro6_n_2_6','title':'旧标题仅用于对照'}})
        p=SceneBattlePanel(run);p.show();p.stages.setCurrentIndex(1);self.qt.processEvents();self.addCleanup(p.close);return run,p

    def test_shared_factory_verifies_the_stage_once_instead_of_twice_without_changing_packets(self):
        raw=(ROOT/'research/scene-reader-review-20261031/before-player-map-reader.py').read_bytes()
        self.assertEqual(sha256(raw).hexdigest(),'8d09e8720836faf59f314907d8482cb530446a577509f18a04c9148cd33c4e61')
        previous=ModuleType('rouge._before_scene_reader_review');previous.__package__='rouge';exec(compile(raw,'<verified-own-prior-factory>','exec'),previous.__dict__)
        parent=QWidget();self.addCleanup(parent.close)
        for sid in ['ro6_n_1_2','ro6_n_2_6','ro6_b_7']:
            results=[];calls=[]
            for factory in [previous.make_reader,make_reader]:
                with patch.object(model,'stage_reference',wraps=model.stage_reference)as load:
                    dialog=factory('battle',{'id':sid,'title':'not used as source identity'},parent)
                self.assertIsNotNone(dialog);calls.append(load.call_count)
                results.append(deepcopy((dialog.panel.result,dialog.panel.rewards.result,dialog.panel.settlement.result)))
                dialog.close()
            self.assertEqual(calls,[2,1]);self.assertEqual(results[0],results[1])

    def test_recent_battle_reuses_same_source_bound_frameless_reader_and_dark_palette(self):
        run,p=self.scene();state=deepcopy(run.state)
        with patch.object(model,'stage_reference',wraps=model.stage_reference)as load:p.open_stage()
        self.qt.processEvents();d=p.dialog;self.assertIsNotNone(d)
        self.assertEqual(load.call_count,1);self.assertEqual(d.panel.stage_id,'ro6_n_2_6')
        self.assertTrue(d.windowFlags()&Qt.WindowType.FramelessWindowHint)
        self.assertEqual(d.objectName(),'mapReferenceWindow');self.assertEqual(d.styleSheet(),REFERENCE_STYLE)
        self.assertEqual(d.palette().color(QPalette.ColorRole.Window).name(),'#262528')
        self.assertGreater(d.panel.details_toggle.palette().color(QPalette.ColorRole.WindowText).lightness(),200)
        self.assertEqual(d.panel.tabs.count(),4);self.assertEqual(run.state,state)

    def test_reopening_reader_refreshes_original_instance_and_preserves_accurate_selection(self):
        _,p=self.scene();p.open_stage();d=p.dialog;reward=d.panel.rewards
        row=next(r for r in reward.result['rows']if r['source_action_keys']);reward.choices.select_value(row['id']);reward.source_combo.setCurrentIndex(1)
        before=reward.combo.currentData(),reward.source_combo.currentData();d.close()
        with patch.object(model,'stage_reference',wraps=model.stage_reference)as load:p.open_stage()
        self.assertIs(p.dialog,d);self.assertEqual(load.call_count,1)
        self.assertEqual(before,(reward.combo.currentData(),reward.source_combo.currentData()))

    def test_closing_shared_reader_closes_owned_spawn_window_and_reopen_restores_base_data(self):
        _,p=self.scene();p.open_stage();d=p.dialog
        self.assertTrue(d.panel.open_spawn_candidates());child=d.panel.spawn_candidates_dialog;self.qt.processEvents()
        self.assertTrue(child.isVisible());d.close();self.qt.processEvents()
        self.assertFalse(child.isVisible());self.assertIsNone(d.panel.settlement.result)
        p.open_stage();self.assertIs(p.dialog,d);self.assertIsNotNone(d.panel.settlement.result)

    def test_changed_exact_stage_closes_old_window_and_uses_its_own_source(self):
        run,p=self.scene();p.open_stage();old=p.dialog
        run.state['last_node_content']={'kind':'battle','stage_id':'ro6_n_1_2','title':'another old title'};p.refresh()
        self.assertFalse(old.isVisible());self.assertIsNone(p.dialog);self.assertIsNone(p.stages.currentData())
        p.stages.setCurrentIndex(1);p.open_stage();self.assertEqual(p.dialog.panel.stage_id,'ro6_n_1_2')

    def test_existing_reader_source_loss_closes_old_window_without_faking_recovery(self):
        _,p=self.scene();p.open_stage();old=p.dialog
        with patch.object(model,'stage_reference',return_value=None):p.open_stage()
        self.assertIsNone(p.dialog);self.assertFalse(old.isVisible())
        p.open_stage();self.assertIsNotNone(p.dialog);self.assertIsNone(p.dialog.panel.rewards.combo.currentData())

    def test_invalid_factory_identity_returns_none_without_a_visible_or_retained_panel(self):
        from rouge.current_battle_view import CurrentBattlePanel
        parent=QWidget();self.addCleanup(parent.close)
        with patch.object(model,'stage_reference',return_value=None):self.assertIsNone(make_reader('battle',{'id':'missing','title':'遗忘时间'},parent))
        QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
        self.assertFalse(any(isinstance(w,CurrentBattlePanel)and w.stage_id=='missing'for w in QApplication.topLevelWidgets()))

    def test_recent_event_uses_same_skin_without_changing_exact_event_or_run(self):
        run=SimpleNamespace(state={'id':'event-fixture','last_node_content':{'kind':'event','title':'桑尼的邀请'}});before=deepcopy(run.state)
        p=RecentScenePanel(run);p.show();self.addCleanup(p.close);p.event_choices.setCurrentIndex(1);p.event_entries.setCurrentIndex(1)
        selected=p.event_result['selected'];self.assertTrue(p.open_event());self.qt.processEvents()
        self.assertEqual(p.event_dialog.objectName(),'mapReferenceWindow');self.assertEqual(p.event_dialog.styleSheet(),REFERENCE_STYLE)
        self.assertEqual(p.event_dialog.panel.result['event']['id'],selected['event_id'])
        self.assertEqual(run.state,before)


if __name__=='__main__':unittest.main()
