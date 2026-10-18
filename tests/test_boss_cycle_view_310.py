"""Necessary documentary reader tests; root alone executes the Qt suite."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import boss_cycle_reference as model
from rouge.boss_cycle_view import BossCycleReferencePanel,target_identity

KEYS=(('ro6_b_5','enemy_2147_shophm',0),('ro6_b_5','enemy_2148_shorbb',0))

class BossCycleView310Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def reader(self):
        window=BossCycleReferencePanel();window.resize(900,420);window.show()
        self.addCleanup(window.close);self.qt.processEvents();return window

    def assert_empty(self,window):
        self.assertIsNone(window.identity);self.assertIsNone(window.result)
        self.assertEqual(window.topic.count(),0);self.assertFalse(window.topic.isEnabled())
        self.assertEqual(window.player.toPlainText(),'');self.assertEqual(window.technical.toPlainText(),'')
        self.assertEqual(window.lorentz_picture.key,(None,None,''));self.assertEqual(window.cube_picture.key,(None,None,''))

    def test_manual_overview_for_both_exact_entries_always_shows_both_original_subjects(self):
        window=self.reader();self.assert_empty(window)
        for key in KEYS:
            with self.subTest(identity=key):
                self.assertTrue(window.set_reference(key));self.assertEqual(window.identity,key)
                self.assertIsNone(window.topic.currentData());self.assertFalse(window.isModal())
                self.assertEqual(window.result['reference']['enemy_id'],key[1])
                self.assertIn(window.result['reference']['entry_name'],window.windowTitle())
                self.assertEqual(window.lorentz_picture.key[:2],('enemy',KEYS[0][1]))
                self.assertEqual(window.cube_picture.key[:2],('enemy',KEYS[1][1]))
                self.assertEqual(window.player.toPlainText(),model.reference_text(window.result,topic_id=None))

    def test_each_entry_can_read_all_source_topics_without_switching_identity(self):
        window=self.reader()
        for key in KEYS:
            window.set_reference(key);topics=window.result['reference']['topics'];self.assertTrue(topics)
            self.assertEqual([window.topic.itemData(i)for i in range(1,window.topic.count())],[row['id']for row in topics])
            for row in topics:
                with self.subTest(identity=key,topic=row['id']):
                    window.topic.setCurrentIndex(window.topic.findData(row['id']));self.qt.processEvents()
                    self.assertEqual(window.identity,key);self.assertEqual(window.result['reference']['enemy_id'],key[1])
                    self.assertEqual(window.player.toPlainText(),model.reference_text(window.result,topic_id=row['id']))
                    technical=json.loads(window.technical.toPlainText())
                    self.assertEqual(technical['selected_topic_id'],row['id']);self.assertEqual(technical['result'],window.result)

    def test_exact_identity_rejects_other_stage_particle_device_and_nonint_level(self):
        window=self.reader();key=KEYS[0]
        for value in(None,list(key),('ro6_b_6',key[1],0),(key[0],'enemy_2149_shorsm',0),
                (key[0],'trap_324',0),(key[0],key[1],False),(key[0],key[1],0.0)):
            self.assertFalse(target_identity(value));self.assertFalse(window.set_reference(value));self.assert_empty(window)
        packet=model.cycle_reference(*key);packet['reference']['enemy_id']=KEYS[1][1]
        self.assertFalse(window.set_reference(key,packet));self.assert_empty(window)

    def test_same_identity_source_and_topic_preserve_each_real_reader_state(self):
        window=self.reader()
        for key in KEYS:
            window.set_reference(key)
            selected=max(window.result['reference']['topics'],key=lambda row:len(model.reference_text(window.result,topic_id=row['id'])))['id']
            window.topic.setCurrentIndex(window.topic.findData(selected));self.qt.processEvents()
            for widget in(window.player,window.technical):
                window.tabs.setCurrentWidget(widget);self.qt.processEvents();cursor=widget.textCursor()
                cursor.setPosition(3);cursor.setPosition(14,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
                bar=widget.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(13,bar.maximum()))
                before=(cursor.anchor(),cursor.position(),cursor.selectedText(),bar.value(),window.scope_key)
                self.assertTrue(window.refresh_reference());self.qt.processEvents();now=widget.textCursor()
                self.assertEqual((now.anchor(),now.position(),now.selectedText(),bar.value(),window.scope_key),before)
                self.assertIs(window.tabs.currentWidget(),widget);self.assertEqual(window.topic.currentData(),selected)

    def test_switching_between_two_entries_discards_old_topic_and_reading(self):
        window=self.reader();window.set_reference(KEYS[0]);window.topic.setCurrentIndex(1)
        window.tabs.setCurrentWidget(window.technical);old_scope=window.scope_key
        self.assertTrue(window.set_reference(KEYS[1]));self.assertNotEqual(window.scope_key,old_scope)
        self.assertEqual(window.identity,KEYS[1]);self.assertIsNone(window.topic.currentData())
        self.assertIs(window.tabs.currentWidget(),window.player)
        self.assertEqual(json.loads(window.technical.toPlainText())['selected_topic_id'],None)

    def test_source_loss_clears_both_pictures_and_readers_recovery_needs_manual_open(self):
        window=self.reader();window.set_reference(KEYS[0]);window.topic.setCurrentIndex(1)
        with patch.object(model,'cycle_reference',return_value={'source_valid':False,'status':'source_unavailable','reference':None,'source_identity':None}):
            self.assertFalse(window.refresh_reference())
        self.assert_empty(window);self.assertFalse(window.refresh_reference())
        self.assertTrue(window.set_reference(KEYS[0]));self.assertIsNone(window.topic.currentData())

    def test_manual_topic_change_queries_fresh_source_not_prior_packet(self):
        window=self.reader();window.set_reference(KEYS[1])
        with patch.object(model,'cycle_reference',return_value=None):window.topic.setCurrentIndex(1)
        self.assert_empty(window)

    def test_new_source_epoch_does_not_periodically_restore_previous_topic(self):
        window=self.reader();window.set_reference(KEYS[0]);changed=deepcopy(window.result)
        changed['source_identity']['data_sha256']='0'*64
        with patch.object(model,'cycle_reference',return_value=changed):
            self.assertFalse(window.refresh_reference());self.assert_empty(window)
            self.assertFalse(window.refresh_reference());self.assertTrue(window.set_reference(KEYS[0]))
            self.assertIsNone(window.topic.currentData())

    def test_packet_ownership_and_duplicate_or_bool_topic_identity_fail_closed(self):
        window=self.reader();packet=model.cycle_reference(*KEYS[0]);window.set_reference(KEYS[0],packet)
        packet['reference']['entry_name']='mutated external packet'
        self.assertNotEqual(window.result['reference']['entry_name'],'mutated external packet')
        for kind in('duplicate','bool'):
            value=model.cycle_reference(*KEYS[0])
            if kind=='duplicate':value['reference']['topics'].append(deepcopy(value['reference']['topics'][0]))
            else:value['reference']['topics'][0]['id']=True
            self.assertFalse(window.set_reference(KEYS[0],value));self.assert_empty(window)
