from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication,QComboBox,QLabel,QLineEdit,QPushButton
from rouge import player_map
from rouge.player_map_acceptance import fixtures


class MapFinderEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_one_projection_per_refresh_and_rebuild_after_changed_history(self):
        graphs,*_=fixtures();graphs={g['zone_id']:g for g in graphs};before=deepcopy(graphs)
        page=SimpleNamespace(graphs=graphs,node_results=QComboBox(),coverage_notice=QLabel(),node_query=QLineEdit(),read_scope=QComboBox(),find_node=QPushButton())
        page.read_scope.addItem('全部',None)
        count=sum(len(g['nodes'])for g in graphs.values())
        with patch.object(player_map,'node_style',wraps=player_map.node_style)as style,patch.object(player_map,'zone_info',wraps=player_map.zone_info)as zone:
            player_map.MapPanel.update_node_finder(page)
            self.assertEqual(style.call_count,count)
            self.assertEqual(zone.call_count,len(graphs))
        self.assertEqual(page.node_results.count(),count);self.assertEqual(graphs,before)
        key=page.node_results.currentData();node=next(n for n in graphs[key[0]]['nodes']if n['id']==key[2])
        node['content']={'title':'本次新读到的标题','source':'same_frame_selected_node'}
        page.node_query.setText('本次新读到的标题')
        player_map.MapPanel.update_node_finder(page)
        self.assertEqual(page.node_results.count(),1);self.assertEqual(page.node_results.currentData(),key)
        self.assertIn('本次新读到的标题',page.node_results.currentText())


if __name__=='__main__':unittest.main()
