from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge import player_theme
from rouge.player_map_reader import make_reader,REFERENCE_STYLE


class MapReaderThemeEntryReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_standalone_battle_constructs_final_reference_theme_once(self):
        with patch.object(player_theme,'apply_theme',wraps=player_theme.apply_theme)as apply:
            dialog=make_reader('battle',{'id':'ro6_n_2_6','title':'公开固定作战'},None)
            self.addCleanup(dialog.close)
        calls=[call for call in apply.call_args_list if call.args[0]is dialog]
        self.assertEqual(len(calls),1)
        self.assertEqual(dialog.objectName(),'mapReferenceWindow')
        self.assertEqual(dialog.property('playerThemeVariant'),'reference')
        self.assertEqual(dialog.styleSheet(),player_theme.assets('reference')[0]+REFERENCE_STYLE)
        self.assertEqual(dialog.panel.result['id'],'ro6_n_2_6')


if __name__=='__main__':unittest.main()
