"""Necessary documentary UI tests; prepared without executing Qt or unittest."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QPlainTextEdit

from rouge import boss_hunt_reference as model
from rouge.boss_hunt_view import BossHuntReferencePanel, PICTURES, target_identity, _technical_json

KEYS = (('ro6_b_4', 'enemy_2145_cadejo', 0), ('ro6_b_4', 'enemy_2146_cadesd', 0),
        ('ro6_b_4', 'enemy_2137_shsdgo', 0))


class BossHuntView311Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def reader(self):
        window = BossHuntReferencePanel()
        window.resize(940, 440)
        window.show()
        self.addCleanup(window.close)
        self.qt.processEvents()
        return window

    def test_technical_json_roundtrips_special_unicode_and_literal_escapes_through_actual_Qt(self):
        original = {'中文': '甲\u00a0乙\u2028丙\u2029丁', '字面转义': '\\u00a0\\u2028\\u2029',
                    '混合类型': [None, False, 0, 0.5, {'符号': '<原文>'}]}
        widget = QPlainTextEdit()
        self.addCleanup(widget.close)
        widget.setPlainText(_technical_json(original))
        self.qt.processEvents()
        displayed = widget.toPlainText()
        self.assertIn('中文', displayed)
        self.assertEqual(json.loads(displayed), original)

    def assert_empty(self, window):
        self.assertIsNone(window.identity)
        self.assertIsNone(window.scope_key)
        self.assertIsNone(window.result)
        self.assertEqual(window.topic.count(), 0)
        self.assertFalse(window.topic.isEnabled())
        self.assertEqual(window.player.toPlainText(), '')
        self.assertEqual(window.technical.toPlainText(), '')
        for attribute, _, _ in PICTURES:
            self.assertEqual(getattr(window, attribute).key, (None, None, ''))

    def test_three_exact_entries_manual_overview_and_three_distinct_original_subjects(self):
        window = self.reader()
        self.assert_empty(window)
        self.assertEqual(model.TARGETS, KEYS)
        for key in KEYS:
            with self.subTest(identity=key):
                self.assertTrue(window.set_reference(key))
                self.assertEqual(window.identity, key)
                self.assertIsNone(window.topic.currentData())
                self.assertFalse(window.isModal())
                self.assertIn(window.result['reference']['entry_name'], window.windowTitle())
                self.assertEqual(window.player.toPlainText(), model.reference_text(window.result, topic_id=None))
                for attribute, enemy_id, _ in PICTURES:
                    self.assertEqual(getattr(window, attribute).key[:2], ('enemy', enemy_id))

    def test_each_selected_subject_can_read_all_dynamic_topics_without_identity_substitution(self):
        window = self.reader()
        for key in KEYS:
            self.assertTrue(window.set_reference(key))
            topics = window.result['reference']['topics']
            self.assertTrue(topics)
            self.assertEqual([window.topic.itemData(i) for i in range(1, window.topic.count())],
                             [row['id'] for row in topics])
            for row in topics:
                with self.subTest(identity=key, topic=row['id']):
                    window.topic.setCurrentIndex(window.topic.findData(row['id']))
                    self.qt.processEvents()
                    self.assertEqual(window.identity, key)
                    self.assertEqual(window.result['reference']['enemy_id'], key[1])
                    self.assertEqual(window.player.toPlainText(), model.reference_text(window.result, topic_id=row['id']))
                    source = json.loads(window.technical.toPlainText())
                    self.assertEqual(source['selected_topic_id'], row['id'])
                    self.assertEqual(source['result'], window.result)

    def test_other_stage_custom_and_nonint_identity_are_not_entries(self):
        window = self.reader()
        key = KEYS[0]
        for value in (None, list(key), ('ro6_b_4_b', key[1], 0), ('custom', key[1], 0),
                      (key[0], 'enemy_2147_shophm', 0), (key[0], key[1], False), (key[0], key[1], 0.0)):
            self.assertFalse(target_identity(value), value)
            self.assertFalse(window.set_reference(value))
            self.assert_empty(window)

    def test_top_and_nested_source_identity_must_both_match_the_selected_tuple(self):
        window = self.reader()
        for container in ('top', 'reference'):
            for field, value in (('stage_id', 'ro6_b_4_b'), ('enemy_id', KEYS[1][1]), ('level', False)):
                packet = model.hunt_reference(*KEYS[0])
                target = packet if container == 'top' else packet['reference']
                target[field] = value
                self.assertFalse(window.set_reference(KEYS[0], packet), (container, field))
                self.assert_empty(window)

    def test_same_identity_source_and_topic_preserve_both_readers_and_real_nonzero_scroll(self):
        window = self.reader()
        for key in KEYS:
            window.set_reference(key)
            topic_id = max(window.result['reference']['topics'],
                           key=lambda row: len(model.reference_text(window.result, topic_id=row['id'])))['id']
            window.topic.setCurrentIndex(window.topic.findData(topic_id))
            self.qt.processEvents()
            for widget in (window.player, window.technical):
                window.tabs.setCurrentWidget(widget)
                self.qt.processEvents()
                cursor = widget.textCursor()
                cursor.setPosition(3)
                cursor.setPosition(14, QTextCursor.MoveMode.KeepAnchor)
                widget.setTextCursor(cursor)
                bar = widget.verticalScrollBar()
                self.assertGreater(bar.maximum(), 0)
                bar.setValue(min(13, bar.maximum()))
                before = (cursor.anchor(), cursor.position(), cursor.selectedText(), bar.value(), window.scope_key)
                self.assertTrue(window.refresh_reference())
                self.qt.processEvents()
                now = widget.textCursor()
                self.assertEqual((now.anchor(), now.position(), now.selectedText(), bar.value(), window.scope_key), before)
                self.assertIs(window.tabs.currentWidget(), widget)
                self.assertEqual(window.topic.currentData(), topic_id)

    def test_unselected_overview_source_reading_is_also_preserved(self):
        window = self.reader()
        window.set_reference(KEYS[0])
        window.tabs.setCurrentWidget(window.technical)
        self.qt.processEvents()
        cursor = window.technical.textCursor()
        cursor.setPosition(2)
        cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
        window.technical.setTextCursor(cursor)
        bar = window.technical.verticalScrollBar()
        self.assertGreater(bar.maximum(), 0)
        bar.setValue(min(9, bar.maximum()))
        before = (cursor.anchor(), cursor.position(), cursor.selectedText(), bar.value())
        self.assertTrue(window.refresh_reference())
        self.qt.processEvents()
        now = window.technical.textCursor()
        self.assertEqual((now.anchor(), now.position(), now.selectedText(), bar.value()), before)
        self.assertIsNone(window.topic.currentData())
        self.assertIs(window.tabs.currentWidget(), window.technical)

    def test_switching_three_subjects_discards_old_topic_tab_and_selection(self):
        window = self.reader()
        for before_key, after_key in zip(KEYS, KEYS[1:] + KEYS[:1]):
            window.set_reference(before_key)
            window.topic.setCurrentIndex(1)
            window.tabs.setCurrentWidget(window.technical)
            old_scope = window.scope_key
            self.assertTrue(window.set_reference(after_key))
            self.assertEqual(window.identity, after_key)
            self.assertNotEqual(window.scope_key, old_scope)
            self.assertIsNone(window.topic.currentData())
            self.assertIs(window.tabs.currentWidget(), window.player)
            self.assertFalse(window.player.textCursor().hasSelection())

    def test_source_loss_clears_all_three_pictures_and_requires_manual_reopen_after_recovery(self):
        window = self.reader()
        window.set_reference(KEYS[0])
        window.topic.setCurrentIndex(1)
        with patch.object(model, 'hunt_reference', return_value={'source_valid': False, 'status': 'source_unavailable',
                                                               'reference': None, 'source_identity': None}):
            self.assertFalse(window.refresh_reference())
        self.assert_empty(window)
        self.assertFalse(window.refresh_reference())
        self.assertTrue(window.set_reference(KEYS[0]))
        self.assertIsNone(window.topic.currentData())

    def test_manual_topic_selection_queries_fresh_not_the_prior_result(self):
        window = self.reader()
        window.set_reference(KEYS[2])
        with patch.object(model, 'hunt_reference', return_value=None):
            window.topic.setCurrentIndex(1)
        self.assert_empty(window)

    def test_new_source_epoch_clears_old_reading_until_manual_reopen(self):
        window = self.reader()
        window.set_reference(KEYS[0])
        changed = deepcopy(window.result)
        changed['source_identity']['data_sha256'] = '0' * 64
        with patch.object(model, 'hunt_reference', return_value=changed):
            self.assertFalse(window.refresh_reference())
            self.assert_empty(window)
            self.assertFalse(window.refresh_reference())
            self.assertTrue(window.set_reference(KEYS[0]))
            self.assertIsNone(window.topic.currentData())

    def test_packet_ownership_and_invalid_topic_or_source_metadata_fail_closed(self):
        window = self.reader()
        packet = model.hunt_reference(*KEYS[0])
        self.assertTrue(window.set_reference(KEYS[0], packet))
        packet['reference']['entry_name'] = 'external mutation'
        self.assertNotEqual(window.result['reference']['entry_name'], packet['reference']['entry_name'])
        for kind in ('duplicate', 'bool', 'empty_name', 'bad_digest'):
            value = model.hunt_reference(*KEYS[0])
            if kind == 'duplicate':
                value['reference']['topics'].append(deepcopy(value['reference']['topics'][0]))
            elif kind == 'bool':
                value['reference']['topics'][0]['id'] = True
            elif kind == 'empty_name':
                value['reference']['topics'][0]['name'] = ''
            else:
                value['source_identity']['data_sha256'] = 'wrong-source'
            self.assertFalse(window.set_reference(KEYS[0], value), kind)
            self.assert_empty(window)


if __name__ == '__main__':
    unittest.main()
