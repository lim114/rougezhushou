import unittest
from PySide6.QtWidgets import QApplication
from rouge.player_floor_resources import FloorResourcesPage
from rouge.run_config import config_data

class FloorResourceEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_initial_refresh_retains_selection_until_run_changes(self):
        page=FloorResourcesPage();self.addCleanup(page.close)
        self.assertIsNone(page.identity)
        page.refresh({'id':'a','history':[]})
        self.assertEqual(page.entries.count(),0)
        zone=next(iter(config_data()['zones']))
        state={'id':'a','history':[{'kind':'floor_resources_read','source':'same_frame_zone_and_resources',
            'zone_id':zone,'values':{'gold':7},'at':100}]}
        page.refresh(state);page.entries.setCurrentRow(0)
        selected=page.entries.currentItem();self.assertIn('7',page.detail.text())
        page.refresh(state);self.assertIs(page.entries.currentItem(),selected)
        page.refresh({**state,'id':'b'})
        self.assertEqual(page.entries.currentRow(),-1)
        self.assertIn('尚未记录',page.detail.text())

if __name__=='__main__':unittest.main()
