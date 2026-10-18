"""Necessary reader behavior; root executes after source and model promotion."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge import boss_phase_reference as model
from rouge.boss_phase_view import BossPhaseReferencePanel,target_identity

KEY=('ro6_b_6','enemy_2150_shchmr',0)


class BossPhaseView309Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def reader(self):
        window=BossPhaseReferencePanel();window.resize(820,420);window.show()
        self.addCleanup(window.close);self.qt.processEvents();return window

    def test_default_is_empty_until_explicit_open_then_overview_and_original_boss_picture(self):
        window=self.reader();self.assertIsNone(window.identity);self.assertFalse(window.phase.isEnabled())
        self.assertEqual(window.boss_picture.key,(None,None,''));self.assertEqual(window.player.toPlainText(),'')
        self.assertTrue(window.set_reference(KEY));self.assertIsNone(window.phase.currentData())
        self.assertFalse(window.isModal());self.assertIs(window.tabs.currentWidget(),window.player)
        self.assertEqual(window.boss_picture.key[:2],('enemy',KEY[1]))
        self.assertEqual(window.player.toPlainText(),model.reference_text(window.result,phase_id=None))

    def test_every_documented_phase_uses_exact_id_in_original_order_not_hardcoded_count(self):
        window=self.reader();self.assertTrue(window.set_reference(KEY))
        rows=window.result['reference']['phases'];self.assertTrue(rows)
        self.assertEqual([(window.phase.itemData(i),window.phase.itemText(i))for i in range(1,window.phase.count())],
            [(row['id'],row['name'])for row in rows])
        for row in rows:
            with self.subTest(phase=row['id']):
                window.phase.setCurrentIndex(window.phase.findData(row['id']));self.qt.processEvents()
                self.assertEqual(window.phase.currentData(),row['id'])
                self.assertEqual(window.player.toPlainText(),model.reference_text(window.result,phase_id=row['id']))
                technical=json.loads(window.technical.toPlainText())
                self.assertEqual(technical['selected_phase_id'],row['id'])
                self.assertEqual(technical['result'],window.result)

    def test_strict_tuple_and_exact_reference_identity_reject_other_enemy_or_bool_level(self):
        window=self.reader();result=model.phase_reference(*KEY)
        for identity in(None,list(KEY),(KEY[0],KEY[1],False),(KEY[0],KEY[1],0.0),
                ('ro6_b_5',KEY[1],0),(KEY[0],KEY[1]+'_alias',0)):
            self.assertFalse(target_identity(identity));self.assertFalse(window.set_reference(identity))
            self.assertEqual(window.phase.count(),0);self.assertIsNone(window.identity)
        other=deepcopy(result);other['reference']['stage_id']='ro6_b_5'
        self.assertFalse(window.set_reference(KEY,other));self.assertIsNone(window.result)

    def test_same_identity_source_and_selected_phase_preserve_real_reading_state(self):
        window=self.reader();window.set_reference(KEY)
        selected=max(window.result['reference']['phases'],key=lambda row:len(model.reference_text(window.result,phase_id=row['id'])))['id']
        window.phase.setCurrentIndex(window.phase.findData(selected));self.qt.processEvents()
        for widget in(window.player,window.technical):
            window.tabs.setCurrentWidget(widget);self.qt.processEvents()
            cursor=widget.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
            bar=widget.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(9,bar.maximum()))
            before=(cursor.anchor(),cursor.position(),cursor.selectedText(),bar.value(),window.scope_key)
            self.assertTrue(window.refresh_reference());self.qt.processEvents()
            now=widget.textCursor()
            self.assertEqual((now.anchor(),now.position(),now.selectedText(),bar.value(),window.scope_key),before)
            self.assertEqual(window.phase.currentData(),selected);self.assertIs(window.tabs.currentWidget(),widget)

    def test_source_failure_clears_both_readers_picture_and_phase_until_manual_reopen(self):
        window=self.reader();window.set_reference(KEY);window.phase.setCurrentIndex(1)
        with patch.object(model,'phase_reference',return_value={'source_valid':False,'status':'source_unavailable','reference':None,'source_identity':None}):
            self.assertFalse(window.refresh_reference())
        self.assertIsNone(window.identity);self.assertIsNone(window.result)
        self.assertEqual(window.phase.count(),0);self.assertFalse(window.phase.isEnabled())
        self.assertEqual(window.player.toPlainText(),'');self.assertEqual(window.technical.toPlainText(),'')
        self.assertEqual(window.boss_picture.key,(None,None,''));self.assertFalse(window.refresh_reference())
        self.assertTrue(window.set_reference(KEY));self.assertIsNone(window.phase.currentData())

    def test_manual_phase_query_cannot_reuse_stale_valid_packet_after_source_loss(self):
        window=self.reader();window.set_reference(KEY)
        with patch.object(model,'phase_reference',return_value=None):window.phase.setCurrentIndex(1)
        self.assertIsNone(window.identity);self.assertEqual(window.phase.count(),0)
        self.assertEqual(window.boss_picture.key,(None,None,''))

    def test_changed_source_epoch_invalidates_periodic_reader_and_requires_explicit_open(self):
        window=self.reader();window.set_reference(KEY);changed=deepcopy(window.result)
        changed['source_identity']['manifest_sha256']='0'*64
        with patch.object(model,'phase_reference',return_value=changed):
            self.assertFalse(window.refresh_reference());self.assertIsNone(window.identity)
            self.assertFalse(window.refresh_reference());self.assertEqual(window.player.toPlainText(),'')
            self.assertTrue(window.set_reference(KEY));self.assertIsNone(window.phase.currentData())

    def test_packet_is_defensively_owned_and_duplicate_or_nonstring_phase_ids_are_rejected(self):
        window=self.reader();original=model.phase_reference(*KEY);window.set_reference(KEY,original)
        original['reference']['boss_name']='mutated caller object'
        self.assertNotEqual(window.result['reference']['boss_name'],'mutated caller object')
        for invalid in('duplicate','boolean'):
            packet=model.phase_reference(*KEY)
            if invalid=='duplicate':packet['reference']['phases'].append(deepcopy(packet['reference']['phases'][0]))
            else:packet['reference']['phases'][0]['id']=False
            self.assertFalse(window.set_reference(KEY,packet));self.assertIsNone(window.identity)
