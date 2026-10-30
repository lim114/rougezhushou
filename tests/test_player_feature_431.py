import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QWidget
from rouge.player_map_reader import make_reader
from rouge.player_map_acceptance import fixtures
from rouge.player_map_reference import node_dossier

class CompactMapReaders(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def test_exact_event_catalog_group_uses_verified_reader(self):
  graphs,node,*_=fixtures();row=node_dossier(graphs[0],node,{})['rows'][0];parent=QWidget();dialog=make_reader('event',row,parent,historical=True)
  try:
   self.assertIsNotNone(dialog);self.assertEqual(dialog.node_reference_binding['expected_summary']['id'],row['id']);self.assertIn('历史节点',dialog.node_reference_banner.text())
  finally:
   if dialog:dialog.close()
   parent.close()
 def test_exact_stage_opens_its_own_fixed_panel(self):
  parent=QWidget();dialog=make_reader('battle',{'id':'ro6_n_1_2','title':'遗忘时间'},parent)
  try:self.assertIsNotNone(dialog);self.assertEqual(dialog.panel.stage_id,'ro6_n_1_2');self.assertIsNotNone(dialog.panel.result)
  finally:
   if dialog:dialog.close()
   parent.close()
 def test_unknown_identity_never_uses_known_name_as_substitute(self):
  parent=QWidget()
  try:
   self.assertIsNone(make_reader('battle',{'id':'missing','title':'遗忘时间'},parent))
   self.assertIsNone(make_reader('event',{'id':'missing','title':'桑尼的邀请'},parent))
  finally:parent.close()
 def test_source_loss_refuses_cached_stage(self):
  parent=QWidget()
  try:
   with patch('rouge.current_battle_reference.stage_reference',return_value=None):self.assertIsNone(make_reader('battle',{'id':'ro6_n_1_2','title':'遗忘时间'},parent))
  finally:parent.close()

if __name__=='__main__':unittest.main()
