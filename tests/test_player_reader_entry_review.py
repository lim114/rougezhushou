from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QPushButton,QComboBox,QListWidget,QLabel
from PySide6.QtCore import Qt
from rouge import player_overview as overview
from rouge.player_action_menu import ButtonMenu
from rouge.player_context import Fold

class ReaderEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_overview_initial_values_use_one_snapshot_and_refresh_after_state_change(self):
        run=SimpleNamespace(state={});expected=overview.overview_facts(run.state)
        with patch.object(overview,'overview_facts',wraps=overview.overview_facts)as facts:
            panel=overview.RunOverviewPanel(run,show_map=lambda:None,show_operators=lambda:None,show_items=lambda:None)
            self.addCleanup(panel.close)
            self.assertEqual({k:v.text()for k,v in panel.cards.items()},expected)
            self.assertEqual(facts.call_count,1)
            run.state={'inventory_verified':True,'relic_count':0}
            panel.refresh()
            self.assertEqual(panel.cards['收藏品完整性'].text(),'已核对完整')
            self.assertEqual(facts.call_count,2)

    def test_menu_positions_are_read_once_and_actions_stay_ordered(self):
        class Layout(QVBoxLayout):
            def indexOf(self,widget):
                self.lookups.append(widget)
                return super().indexOf(widget)
        owner=QWidget();self.addCleanup(owner.close);layout=Layout(owner);layout.lookups=[]
        first=QPushButton('甲');second=QPushButton('乙');layout.addWidget(first);layout.addWidget(second)
        menu=ButtonMenu(owner,[first,second])
        self.assertEqual(layout.lookups,[first,second])
        self.assertIs(layout.itemAt(0).widget(),menu)
        self.assertEqual([action.text()for _,action in menu.actions],['甲','乙'])

    def test_fold_initial_and_toggled_states(self):
        content=QWidget();fold=Fold('资料',content);self.addCleanup(fold.close)
        self.assertTrue(content.isHidden());self.assertEqual(fold.toggle.arrowType(),Qt.ArrowType.RightArrow)
        fold.toggle.setChecked(True)
        self.assertFalse(content.isHidden());self.assertEqual(fold.toggle.arrowType(),Qt.ArrowType.DownArrow)
        fold.toggle.setChecked(False)
        self.assertTrue(content.isHidden())

    def test_battle_group_projection_checks_each_action_once(self):
        from rouge.current_battle_view import CurrentBattlePanel
        from rouge import player_spawn_filters as filters
        from tests.test_player_feature_434 import actions
        rows=actions()
        for i,row in enumerate(rows):row.update(enemy_candidates=[],predefined_candidates=[],action_index=i)
        owner=QWidget();self.addCleanup(owner.close)
        panel=SimpleNamespace(actions=QListWidget(owner),queue_kind=QComboBox(owner),
            action_group=QComboBox(owner),action_focus=QComboBox(owner),result={'actions':rows},
            enemy_key=None,_action_object_names={},_enemy_icons={},
            action_filter_notice=QLabel(owner),sender=lambda:None,_action_changed=lambda *a,**k:None)
        for combo in (panel.queue_kind,panel.action_group,panel.action_focus):combo.addItem('全部',None)
        with patch.object(filters,'group_key',wraps=filters.group_key)as grouping:
            CurrentBattlePanel._actions_changed(panel)
            self.assertEqual(grouping.call_count,len(rows))
        self.assertEqual([panel.action_group.itemData(i)for i in range(1,panel.action_group.count())],
            [('main',1,1),('main',1,2),('branch',2,1)])
        self.assertEqual([panel.actions.item(i).data(Qt.ItemDataRole.UserRole)for i in range(panel.actions.count())],
            [row['key']for row in rows])

if __name__=='__main__':unittest.main()
