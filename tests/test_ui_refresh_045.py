"""Reader state survives real data refreshes; sampling and chat remain isolated."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import copy
import json
import tempfile
import time
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QPlainTextEdit
import rouge.app as module
from rouge.battle_preview import battle_data, spawn_rows
from rouge.battle_view import BattlePreviewPanel
from rouge.catalog import stage_previews
from rouge.ui_state import replace_text, append_text


APP = QApplication.instance() or QApplication([])


def reading(widget):
    c = widget.textCursor()
    return c.anchor(), c.position(), widget.verticalScrollBar().value(), widget.horizontalScrollBar().value()


def select_and_scroll(widget):
    cursor = widget.textCursor()
    cursor.setPosition(min(20, widget.document().characterCount()-1))
    cursor.setPosition(min(33, widget.document().characterCount()-1), QTextCursor.MoveMode.KeepAnchor)
    widget.setTextCursor(cursor)
    widget.verticalScrollBar().setValue(min(5, widget.verticalScrollBar().maximum()))
    widget.horizontalScrollBar().setValue(min(8, widget.horizontalScrollBar().maximum()))
    return reading(widget)


class TextRefreshTests(unittest.TestCase):
    def setUp(self):
        self.widget = QPlainTextEdit()
        self.widget.setReadOnly(True)
        self.widget.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.widget.resize(320, 120)
        self.widget.show()
        self.text = '\n'.join('第%d行 😀 '%i + '长文本'*40 for i in range(120))
        self.widget.setPlainText(self.text)
        APP.processEvents()

    def tearDown(self):
        self.widget.close()

    def test_identical_refresh_does_not_rewrite_document(self):
        before = select_and_scroll(self.widget)
        revision = self.widget.document().revision()
        self.assertFalse(replace_text(self.widget, self.text))
        self.assertEqual(self.widget.document().revision(), revision)
        self.assertEqual(reading(self.widget), before)

    def test_changed_text_preserves_unicode_selection_and_both_scrollbars(self):
        before = select_and_scroll(self.widget)
        self.assertGreater(before[2], 0)
        self.assertGreater(before[3], 0)
        self.assertTrue(replace_text(self.widget, self.text+'\n新的数据'))
        APP.processEvents()
        self.assertEqual(reading(self.widget), before)
        self.assertTrue(self.widget.toPlainText().endswith('新的数据'))

    def test_shortened_text_clamps_document_positions_and_scroll(self):
        c = self.widget.textCursor(); c.movePosition(QTextCursor.MoveOperation.End)
        self.widget.setTextCursor(c)
        replace_text(self.widget, '😀')
        last = self.widget.document().characterCount()-1
        self.assertEqual(last, 2)
        self.assertEqual(reading(self.widget), (last, last, 0, 0))

    def test_new_item_resets_reading_position(self):
        select_and_scroll(self.widget)
        replace_text(self.widget, self.text, preserve=False)
        self.assertEqual(reading(self.widget), (0, 0, 0, 0))

    def test_default_refresh_does_not_follow_tail(self):
        bar = self.widget.verticalScrollBar(); bar.setValue(bar.maximum())
        before = reading(self.widget)
        replace_text(self.widget, self.text+'\n新增\n内容')
        self.assertEqual(reading(self.widget), before)
        self.assertLess(bar.value(), bar.maximum())

    def test_reply_refresh_follows_only_when_already_at_tail(self):
        bar = self.widget.verticalScrollBar(); bar.setValue(bar.maximum())
        replace_text(self.widget, self.text+'\n新增\n内容', follow_tail=True)
        self.assertEqual(bar.value(), bar.maximum())
        before = select_and_scroll(self.widget)
        replace_text(self.widget, self.text+'\n又有新的回复', follow_tail=True)
        self.assertEqual(reading(self.widget), before)

    def test_reply_append_keeps_reader_selection_away_from_tail(self):
        before = select_and_scroll(self.widget)
        append_text(self.widget, '\n新片段😀')
        APP.processEvents()
        self.assertEqual(reading(self.widget), before)
        self.assertTrue(self.widget.toPlainText().endswith('\n新片段😀'))

    def test_reply_append_follows_tail_without_moving_cursor(self):
        bar = self.widget.verticalScrollBar(); bar.setValue(bar.maximum())
        before = reading(self.widget)[:2]
        append_text(self.widget, '\n新片段\n另一行')
        self.assertEqual(bar.value(), bar.maximum())
        self.assertEqual(reading(self.widget)[:2], before)
        self.assertFalse(append_text(self.widget, ''))


class BattleRefreshTests(unittest.TestCase):
    def setUp(self):
        self.panel = BattlePreviewPanel()
        self.panel.resize(1000, 730); self.panel.show()
        self.panel.set_stage('ro6_n_1_2'); APP.processEvents()
        index = next(i for i, r in enumerate(self.panel.rows) if r['action']['count']>2)
        self.panel.spawn_list.setCurrentRow(index)
        self.panel.occurrence.setValue(3)

    def tearDown(self):
        self.panel.close()

    def test_row_identity_is_unique_within_every_stage(self):
        for sid in battle_data()['stages']:
            ids = [r['id'] for r in spawn_rows(sid)]
            self.assertEqual(len(ids), len(set(ids)), sid)

    def test_context_updates_values_without_rebuilding_rows_or_selection(self):
        p = self.panel
        p.set_context({'difficulty':{'value':0}, 'zone':{'id':'zone_3'}})
        rows = p.rows; item = p.spawn_list.currentItem()
        spawn_state = select_and_scroll(p.spawn_detail)
        enemy_state = select_and_scroll(p.enemy_detail)
        old_text = p.enemy_detail.toPlainText()
        p.set_context({'difficulty':{'value':15}, 'zone':{'id':'zone_3'}})
        self.assertNotEqual(p.enemy_detail.toPlainText(), old_text)
        self.assertIs(p.rows, rows); self.assertIs(p.spawn_list.currentItem(), item)
        self.assertEqual(p.occurrence.value(), 3)
        self.assertEqual(p.grid.selected, p.original.selected)
        self.assertEqual(reading(p.spawn_detail), spawn_state)
        self.assertEqual(reading(p.enemy_detail), enemy_state)
        revision = p.enemy_detail.document().revision()
        p.set_context({'difficulty':{'value':15, 'captured_at':123}, 'zone':{'id':'zone_3'}})
        self.assertEqual(p.enemy_detail.document().revision(), revision)
        self.assertIs(p.spawn_list.currentItem(), item)

    def test_filter_refresh_retains_valid_row_and_ordinal(self):
        p = self.panel; row = p.grid.selected
        text_state = select_and_scroll(p.spawn_detail)
        p.include_branches.setChecked(False)
        self.assertEqual(p.grid.selected['id'], row['id'])
        self.assertEqual(p.occurrence.value(), 3)
        self.assertEqual(reading(p.spawn_detail), text_state)
        p.render_rows()
        self.assertEqual(p.grid.selected['id'], row['id'])
        self.assertEqual(p.occurrence.value(), 3)

    def test_changed_row_count_clamps_saved_ordinal(self):
        p = self.panel; selected = p.grid.selected['id']
        rows = copy.deepcopy(p.rows)
        next(r for r in rows if r['id']==selected)['action']['count'] = 2
        with patch('rouge.battle_view.spawn_rows', return_value=rows):
            p.render_rows()
        self.assertEqual(p.grid.selected['id'], selected)
        self.assertEqual(p.occurrence.value(), 2)
        self.assertEqual(p.original.selected_ordinal, 2)
        self.assertEqual(p.grid.selected_ordinal, 2)

    def test_removed_row_falls_back_and_empty_filter_clears_selection(self):
        p = self.panel; old = p.grid.selected['id']
        other_wave = next(w['index'] for w in p.grid.stage['waves'] if w['index']!=p.grid.selected['wave']
                          and spawn_rows(p.current_stage, w['index'], None, False))
        p.include_branches.setChecked(False)
        p.wave_combo.setCurrentIndex(p.wave_combo.findData(other_wave))
        self.assertNotEqual(p.grid.selected['id'], old)
        self.assertEqual(p.spawn_list.currentRow(), 0); self.assertEqual(p.occurrence.value(), 1)
        p.set_stage('ro6_n_1_2'); p.wave_combo.setCurrentIndex(p.wave_combo.findData(1))
        self.assertFalse(p.rows); self.assertIsNone(p.grid.selected); self.assertIsNone(p.original.selected)
        self.assertTrue(p.occurrence_bar.isHidden()); self.assertFalse(p.spawn_detail.toPlainText())

    def test_new_stage_does_not_reuse_colliding_row_id(self):
        p = self.panel
        p.set_stage('ro6_n_1_1')
        p.spawn_list.setCurrentRow(min(3, len(p.rows)-1))
        p.set_stage('ro6_e_1_1')
        self.assertEqual(p.spawn_list.currentRow(), 0)
        self.assertEqual(p.occurrence.value(), 1)
        self.assertEqual(p._shown_enemy[0], 'ro6_e_1_1')

    def test_non_spawn_tile_survives_context_and_list_refresh(self):
        p = self.panel
        used = [r['route']['start'] for r in p.rows]
        cell = next({'row':r,'col':c} for r,line in enumerate(p.grid.stage['map']) for c,_ in enumerate(line)
                    if {'row':r,'col':c} not in used)
        p._cell_selected(cell)
        before = p.spawn_detail.toPlainText()
        p.set_context({'difficulty':{'value':15}, 'zone':{'id':'zone_3'}})
        p.render_rows()
        self.assertEqual(p.spawn_detail.toPlainText(), before)
        self.assertIsNone(p.grid.selected); self.assertIsNone(p.original.selected)
        self.assertTrue(p.occurrence_bar.isHidden())


class OfflineWindow(module.MainWindow):
    def refresh_windows(self):
        self.windows.clear()


class SamplingRefreshTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack(); self.addCleanup(self.stack.close)
        folder = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.folder = Path(folder)
        backend = module.DesktopBackend
        for key, name in [('RUN_STATE','run.json'), ('OPERATOR_STATE','operators.json'), ('SETTINGS','settings.json')]:
            self.stack.enter_context(patch.object(module, key, self.folder/name))
        self.stack.enter_context(patch.object(module, 'DesktopBackend', lambda _path, callback:backend(self.folder/'chat', callback)))
        self.window = OfflineWindow(); self.window.show(); APP.processEvents()
        self.addCleanup(self.close)

    def close(self):
        self.assertFalse(self.window.auto.isChecked())
        self.assertIsNone(self.window.capture.target)
        self.assertIsNone(self.window.desktop.process)
        self.assertFalse((self.folder/'settings.json').exists())
        self.assertFalse((self.folder/'chat').exists())
        self.window.close(); APP.processEvents()

    def account(self, op='mechanist', **fields):
        record = {'id':op, 'scope':'account', 'fields':fields, 'skill_ranks':{'1':7}}
        self.window.apply_operator_observation(record, time.time())

    def run_observe(self, op='mechanist', **fields):
        observed = {'operators':[{'id':op, 'scope':'run', 'fields':fields, 'skill_ranks':{'1':7}}],
                    'selected_operator':op, 'relics':{'ids':[], 'icons':[], 'source':'test'}}
        self.assertTrue(self.window.apply_run_observation(observed, time.time()))

    def sample_stage(self, sid):
        stage = battle_data()['stages'][sid]
        data = {'page':'node_detail', 'stage':{'name':stage['name'], 'id':sid, 'visible_variant_id':sid},
                'nodes':[], 'captured_at':time.time()}
        self.window.sample_received((np.zeros((120,200,3),dtype=np.uint8), data))

    def test_repeated_stage_samples_keep_manual_preview_new_identity_follows_once(self):
        w = self.window; panel = w.battle_preview
        self.sample_stage('ro6_n_1_2')
        self.assertEqual(w.target_stage.currentData(), 'ro6_n_1_2')
        w.target_stage.setCurrentIndex(w.target_stage.findData('ro6_n_1_1'))
        panel.spawn_list.setCurrentRow(2); row = panel.grid.selected['id']
        w.centralWidget().setCurrentWidget(panel)
        select_and_scroll(w.observed_text)
        cursor = reading(w.observed_text)
        self.sample_stage('ro6_n_1_2')
        self.assertEqual(w.target_stage.currentData(), 'ro6_n_1_1')
        self.assertEqual(panel.grid.selected['id'], row)
        self.assertEqual(w.centralWidget().currentWidget(), panel)
        self.assertEqual(reading(w.observed_text), cursor)
        self.sample_stage('ro6_e_1_2')
        self.assertEqual(w.target_stage.currentData(), 'ro6_e_1_2')
        self.assertEqual(panel.spawn_list.currentRow(), 0)

    def test_account_updates_do_not_steal_browsing_and_still_merge_latest_fields(self):
        w = self.window
        self.account(elite=2, level=80, trust=100, potential=1)
        w.select_operator('silverash')
        self.account(elite=2, level=90, trust=100, potential=2)
        self.assertEqual(w.operator.currentData(), 'silverash')
        self.assertEqual(w.operator_observations['mechanist']['fields']['level'], 90)
        saved = json.loads((self.folder/'operators.json').read_text(encoding='utf-8'))
        self.assertEqual(saved['mechanist']['fields']['potential'], 2)
        self.account('kaltsit', elite=2, level=90)
        self.assertEqual(w.operator.currentData(), 'kaltsit')

    def test_run_updates_keep_manual_operator_skill_level_relic_filter_and_reading(self):
        w = self.window
        self.run_observe(elite=2, level=80, selected_skill=1)
        w.select_operator('silverash')
        w.skill.setCurrentIndex(w.skill.findData(2)); w.level.setValue(61)
        w.relic_filter.setText('书'); w.relic_list.setCurrentRow(11)
        before = select_and_scroll(w.damage_text); run_id = w.run.state['id']
        self.run_observe(elite=2, level=90, selected_skill=3)
        self.assertEqual(w.operator.currentData(), 'silverash')
        self.assertEqual(w.skill.currentData(), 2); self.assertEqual(w.level.value(), 61)
        self.assertEqual(w.relic_filter.text(), '书'); self.assertEqual(w.relic_list.currentRow(), 11)
        self.assertEqual(reading(w.damage_text), before)
        self.assertEqual(w.run.state['id'], run_id)
        self.assertEqual(w.run.state['operators']['mechanist']['fields']['level'], 90)
        self.assertTrue(w.run.state['history'])

    def test_current_operator_receives_new_stats_but_keeps_simulation_choices(self):
        w = self.window
        self.account(elite=2, level=80, potential=1, trust=0)
        w.level.setValue(70); w.skill.setCurrentIndex(w.skill.findData(3))
        before = w.attack.text()
        self.account(elite=2, level=90, potential=3, trust=100, selected_skill=1)
        self.assertNotEqual(w.attack.text(), before)
        self.assertEqual(w.level.value(), 70); self.assertEqual(w.skill.currentData(), 3)
        self.assertEqual(w.damage_result['scenario']['potential'], 3)
        self.account(elite=1, level=80, selected_skill=1)
        self.assertLessEqual(w.level.value(), w.level.maximum())
        self.assertIn(w.skill.currentData(), (1,2))

    def test_enemy_refresh_keeps_selection_and_special_option_only_for_that_enemy(self):
        w = self.window
        sid = next(s for s, d in stage_previews().items() if any(e['id']=='enemy_2148_shorbb' for e in d['possible_enemies']))
        w.target_stage.setCurrentIndex(w.target_stage.findData(sid))
        i = next(i for i in range(1,w.target_enemy.count()) if (w.target_enemy.itemData(i) or {}).get('enemy_id')=='enemy_2148_shorbb')
        w.target_enemy.setCurrentIndex(i); w.orb_mode.setCurrentIndex(2)
        target = w.target_enemy.currentData()
        w.update_target_enemies(); w.update_enemy_context()
        self.assertEqual(w.target_enemy.currentData(), target)
        self.assertEqual(w.orb_mode.currentIndex(), 2)
        self.assertTrue(w.damage_form.isRowVisible(w.orb_mode))
        w.target_stage.setCurrentIndex(w.target_stage.findData('ro6_n_1_2'))
        self.assertIsNone(w.target_enemy.currentData()); self.assertEqual(w.orb_mode.currentIndex(), 0)
        self.assertFalse(w.damage_form.isRowVisible(w.orb_mode))

    def test_same_map_refresh_preserves_node_and_new_layout_clears_it(self):
        w = self.window
        graph = {'zone_id':'zone_1', 'template_id':'test-a', 'captured_at':time.time(),
                 'grid':{'rows':3, 'cols':3}, 'edges':[], 'source':{'url':'test'},
                 'nodes':[{'id':'n1', 'row':0, 'col':0, 'center':[.2,.2], 'visible':True,
                           'distance':1, 'observed_type':'作战', 'prediction':{'candidates':[], 'reason':'资料\n'*50}},
                          {'id':'n2', 'row':1, 'col':1, 'center':[.4,.4], 'visible':False, 'distance':2}]}
        w.run.state['maps']['zone_1'] = copy.deepcopy(graph)
        w.run.state['config']['zone'] = {'id':'zone_1'}
        w.render_map(); w.map_view.select_node('n1')
        before = select_and_scroll(w.map_detail)
        w.run.state['maps']['zone_1']['nodes'][0]['remembered_type'] = '作战'
        w.render_map()
        self.assertEqual(w.map_view.selected, 'n1'); self.assertEqual(w.map_nodes.currentData(), 'n1')
        self.assertEqual(reading(w.map_detail), before)
        self.assertIn('本局已揭示记录：作战', w.map_detail.toPlainText())
        w.run.state['maps']['zone_1']['template_id'] = 'test-b'; w.render_map()
        self.assertIsNone(w.map_view.selected); self.assertEqual(w.map_nodes.currentIndex(), 0)
        self.assertFalse(w.map_detail.toPlainText())

    def test_chat_poll_and_local_chunks_keep_reading_without_any_chat_requests(self):
        w = self.window
        snapshot = {'threads':[{'kind':'chatgpt','title':'测试1','id':'a'}, {'kind':'chatgpt','title':'测试2','id':'b'}],
                    'states':{'chat':{'threadId':'a','title':'测试1','running':False,'pending':False,
                                     'progress':'本地测试','output':'回复\n'*160}}}
        w.centralWidget().setCurrentIndex(2)
        w.desktop_state_received(snapshot); APP.processEvents()
        w.desktop_threads.setCurrentIndex(w.desktop_threads.findData('b'))
        before = select_and_scroll(w.transcript)
        snapshot['states']['chat']['output'] += '本地新数据\n'
        w.desktop_state_received(snapshot)
        self.assertEqual(w.desktop_threads.currentData(), 'b')
        self.assertEqual(reading(w.transcript), before)
        w.chat_chunk('仅合成片段\n')
        self.assertEqual(reading(w.transcript), before)
        self.assertTrue(w.transcript.toPlainText().endswith('仅合成片段\n'))
        snapshot['threads'] = snapshot['threads'][:1]; w.desktop_state_received(snapshot)
        self.assertEqual(w.desktop_threads.currentData(), 'a')

    def test_window_list_refresh_keeps_target_by_handle_and_process(self):
        w = self.window
        targets = [{'hwnd':11,'pid':101,'title':'测试1','minimized':False},
                   {'hwnd':22,'pid':102,'title':'测试2','minimized':False}]
        with patch.object(module, 'list_game_windows', return_value=targets):
            module.MainWindow.refresh_windows(w); w.windows.setCurrentIndex(1)
        targets[1]['title'] = '标题已更新'
        with patch.object(module, 'list_game_windows', return_value=list(reversed(targets))):
            module.MainWindow.refresh_windows(w)
        self.assertEqual(w.windows.currentData()['hwnd'], 22)
        self.assertIn('标题已更新', w.windows.currentText())
        with patch.object(module, 'list_game_windows', return_value=targets[:1]):
            module.MainWindow.refresh_windows(w)
        self.assertEqual(w.windows.currentData()['hwnd'], 11)


if __name__ == '__main__':
    unittest.main()
