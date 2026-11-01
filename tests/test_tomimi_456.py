import base64
from copy import deepcopy
import json
from pathlib import Path
import unittest
from urllib.parse import parse_qs,urlparse
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QLineEdit
from rouge import current_battle_reference as model
from rouge.tomimi_reference import target,stage_links
from rouge.current_battle_view import CurrentBattlePanel
from rouge.player_reference_window import ToolPage,ReferenceWindow


class PublicLinkTests(unittest.TestCase):
    def test_observed_public_configuration_vectors(self):
        cases=[('ro6_n_1_2','AQUgAAA',0,False),('ro6_e_1_2','AQUgAAE',0,True),('ro6_t_8_c','AQUwAAIA',2,False)]
        for sid,code,index,elite in cases:
            r=target(model.stage_reference(sid))
            self.assertEqual(parse_qs(urlparse(r['url']).query),{'state':[code]})
            self.assertEqual((r['variant_index'],r['elite']),(index,elite))
            self.assertEqual(urlparse(r['url']).netloc,'tomimi.dev')

    def test_registry_uses_upstream_level_facts_and_canonical_boss_group(self):
        root=Path(__file__).resolve().parents[1]
        facts=json.loads((root/'research/tomimi-456/source-facts.json').read_bytes())
        for level,row in stage_links().items():
            matches=[c for f in facts['files']if f['key']==row['family']for c in f['configurations']if c['level_id']==level]
            self.assertEqual(len(matches),1)
            self.assertEqual({k:row[k]for k in matches[0]},matches[0])
        boss=target(model.stage_reference('ro6_b_7_b'))
        self.assertEqual((boss['level_id'],boss['variant_index']),('level_rogue6_b-7-b',1))

    def test_all_local_stages_are_classified_without_name_or_dlc_guessing(self):
        stages=model.packet()['version']['current']['details']['stages'];supported=[];missing=[]
        for sid,stage in stages.items():
            r=target({'stage':stage,'id':sid})
            (supported if r else missing).append(sid)
            if r:
                self.assertEqual(r['level_id'],stage['levelId'].rsplit('/',1)[-1])
                raw=base64.urlsafe_b64decode(parse_qs(urlparse(r['url']).query)['state'][0]+'===')
                self.assertEqual(raw[:2],bytes([1,5]));self.assertEqual(raw[2]&15,0);self.assertEqual(raw[3],0)
        self.assertEqual(len(supported),134)
        self.assertEqual(len(missing),50)
        self.assertTrue(all(s.endswith('_dlc1')for s in missing))

    def test_private_fields_never_change_public_url(self):
        r=model.stage_reference('ro6_n_1_2');expected=target(r)
        r=deepcopy(r);r['run_config']={'difficulty':16,'relics':['PRIVATE_MARKER'],'account':'PRIVATE_MARKER'};r['chat_binding']='PRIVATE_MARKER'
        self.assertEqual(target(r),expected)
        self.assertIsNone(target(None))
        r['stage']['name']='同名不能替代准确对应';self.assertIsNone(target(r))


class FakeBrowser(QWidget):
    def __init__(self,result,parent=None):
        super().__init__(parent);self.result=result;self.editor=QLineEdit('public reading');QVBoxLayout(self).addWidget(self.editor)
    def refresh_reference(self):return self.result is not None
    def clear_reference(self):self.result=None;self.editor.clear()


class BrowserNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        self.owner=QWidget();self.owner.reference_window=self.host=ReferenceWindow(self.owner);self.owner.present=self.host.present
        self.addCleanup(self.owner.close);self.addCleanup(self.host.close)
        self.fake=patch('rouge.tomimi_view.TomimiPanel',FakeBrowser);self.fake.start();self.addCleanup(self.fake.stop)
        self.parent=CurrentBattlePanel('ro6_n_1_2');self.root=ToolPage('公开关卡',self.parent,self.owner);self.root.panel=self.parent;self.root.prepare=self.parent.refresh_reference;self.host.present(self.root)

    def test_same_host_back_reopen_and_refresh_preserve_web_state(self):
        self.assertTrue(self.parent.open_tomimi());page=self.host.pages.currentWidget();self.assertIs(page.source_parent,self.root);self.assertIs(page.window(),self.host)
        page.panel.editor.setText('retained browser reading');self.host.navigate(self.host.cursor-1)
        self.assertTrue(self.parent.open_tomimi());self.assertIs(self.host.pages.currentWidget(),page);self.assertEqual(page.panel.editor.text(),'retained browser reading');self.assertIsNone(self.parent.tomimi_dialog)
        self.assertTrue(page.prepare());self.assertEqual(page.panel.editor.text(),'retained browser reading')

    def test_missing_parent_source_removes_visible_dependent_page(self):
        self.parent.open_tomimi();page=self.host.pages.currentWidget()
        with patch('rouge.current_battle_reference.stage_reference',return_value=None):self.assertFalse(self.host.present(page))
        self.qt.processEvents();self.assertNotIn(page,self.host.history);self.assertIs(self.host.pages.currentWidget(),self.root);self.assertIsNone(self.parent.result)

    def test_unsupported_dlc_does_not_open_another_map(self):
        self.host.present(self.root);self.parent.stage_id='ro6_n_3_1_dlc1';self.assertTrue(self.parent.refresh_reference());self.assertFalse(self.parent.tomimi_button.isVisible());self.assertFalse(self.parent.open_tomimi());self.assertIs(self.host.pages.currentWidget(),self.root)

    def test_standalone_close_clears_once_and_reopening_uses_new_reader(self):
        from rouge.tomimi_view import TomimiDialog
        dialog=TomimiDialog(target(self.parent.result));dialog.show();self.qt.processEvents()
        with patch.object(dialog.panel,'clear_reference',wraps=dialog.panel.clear_reference)as clear:
            dialog.close();self.assertEqual(clear.call_count,1)
        self.assertIsNone(dialog.panel.result);dialog.deleteLater()


if __name__=='__main__':unittest.main()
