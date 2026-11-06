import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge import player_statistics_samples as model

class SampleBindingReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_row_binding_is_parsed_once_and_replaced_with_new_digest(self):
        page=model.StatisticsSamplesPage();self.addCleanup(page.close)
        records=[{'state':{'id':'one','resources':{'gold':{'value':7}}},'state_sha256':'a'*64},
                 {'state':{'id':'bad'},'state_sha256':'invalid'}]
        received=[];page.archiveRequested.connect(received.append)
        with patch.object(model,'sample_binding',wraps=model.sample_binding)as parse:
            page.install(records,None);self.assertEqual(parse.call_count,2)
            page.table.selectRow(0);self.assertTrue(page.open_button.isEnabled())
            page.request_archive();page.request_archive()
            self.assertEqual(parse.call_count,2)
            self.assertEqual(received[-1],{'id':'one','state_sha256':'a'*64})
            received[-1]['id']='external mutation'
            page.request_archive();self.assertEqual(received[-1]['id'],'one')
            page.render();self.assertEqual(parse.call_count,2)
            records[0]['state']['resources']['gold']['value']=8
            page.install(records,None);self.assertEqual(parse.call_count,4)
            self.assertEqual(page.table.currentRow(),0)
            records[0]['state_sha256']='b'*64
            page.install(records,None);self.assertEqual(page.table.currentRow(),-1)
            self.assertFalse(page.open_button.isEnabled())
            page.table.selectRow(0);page.request_archive()
            self.assertEqual(received[-1]['state_sha256'],'b'*64)
            page.table.selectRow(1);self.assertFalse(page.open_button.isEnabled())
            count=len(received);page.request_archive();self.assertEqual(len(received),count)
            page.install(None,None);page.request_archive();self.assertEqual(len(received),count)

if __name__=='__main__':unittest.main()
