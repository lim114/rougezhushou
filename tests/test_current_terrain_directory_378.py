import unittest
from copy import deepcopy
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from rouge import current_terrain_directory as model
from rouge import current_battle_reference as battle
from rouge.current_terrain_directory_view import CurrentTerrainDirectoryPanel,CurrentTerrainDirectoryDialog

class TerrainDirectory378Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([]);cls.reference=model.packet()

    def panel(self):
        p=CurrentTerrainDirectoryPanel();p.resize(1100,520);p.show();self.addCleanup(p.close);self.app.processEvents();return p

    def test_every_current_grid_cell_has_exact_one_original_tile_declaration(self):
        ref=self.reference;self.assertIsNotNone(ref);current=battle.packet();expected={}
        for sid,stage in current['version']['current']['details']['stages'].items():
            level=current['inputs']['levels']['levels/'+stage['levelId'].lower()+'.json']
            for r,line in enumerate(level['mapData']['map']):
                for c,index in enumerate(line):expected[(sid,r,c)]=(index,level['mapData']['tiles'][index])
        seen={}
        for row in ref['rows']:
            for r,c in row['cells']:
                key=(row['stage_id'],r,c);self.assertNotIn(key,seen);seen[key]=(row['tile_index'],row['tile'])
        self.assertEqual(seen,expected);self.assertEqual(ref['stage_count'],len(current['version']['current']['details']['stages']))

    def test_filters_use_player_text_and_preserve_all_parameter_variants(self):
        ref=self.reference
        for kind,_ in model.KINDS:
            actual=model.rows(kind=kind,reference=ref);expected=[r for r in ref['rows'] if kind is None or r['terrain_kind']==kind]
            self.assertEqual(actual,expected)
        actual=model.rows('生命',reference=ref);self.assertTrue(actual)
        self.assertTrue(all('生命' in ' '.join([r['stage_name'],r['terrain_name'],*r['terrain']['effects'],*r['terrain']['unknowns']]) for r in actual))
        self.assertEqual(len({tuple(r['key']) for r in ref['rows']}),len(ref['rows']))
        with self.assertRaises(ValueError):model.rows(kind='invented',reference=ref)
        with self.assertRaises(ValueError):model.rows(floor=True,reference=ref)

    def test_player_labels_distinguish_every_original_record_without_raw_identifiers(self):
        ref=self.reference;stages=battle.packet()['version']['current']['details']['stages'];same_names={}
        for sid,stage in stages.items():same_names.setdefault(stage['name'],[]).append(sid)
        labels=[]
        for row in ref['rows']:
            self.assertEqual(row['same_name_stage_number'],same_names[row['stage_name']].index(row['stage_id'])+1)
            self.assertEqual(row['same_name_stage_count'],len(same_names[row['stage_name']]))
            self.assertEqual(row['terrain_setting_number'],row['tile_index']+1)
            text=model.label(row);labels.append(text)
            self.assertIn(dict(model.directory.KINDS)[row['play_kind']],text)
            self.assertIn('同名关卡资料'+str(row['same_name_stage_number'])+'/'+str(row['same_name_stage_count']),text)
            self.assertIn('地形设置'+str(row['tile_index']+1),text)
            self.assertIn(model.effect_summary(row),text);self.assertNotIn(row['stage_id'],text);self.assertNotIn(row['tile_key'],text)
        self.assertEqual(len(labels),len(set(labels)))
        healing=deepcopy(next(r for r in ref['rows'] if r['tile_key']=='tile_healing'))
        healing['terrain']['effects']=['持续回复生命。','每秒回复：干员最大生命值的2%。']
        different=deepcopy(healing);different['terrain']['effects'][-1]='每秒回复：干员最大生命值的3%。'
        self.assertIn('2%',model.label(healing));self.assertIn('3%',model.label(different));self.assertNotEqual(model.label(healing),model.label(different))

    def test_unknown_effect_and_live_qualification_remain_unknown(self):
        row=next(r for r in self.reference['rows'] if r['tile_key']=='tile_pollution_roadf');info=model.detail(row['key'],reference=self.reference)
        self.assertEqual(row['terrain_kind'],'unknown');self.assertEqual(row['terrain']['effects'],[])
        for key in ('actual_occurrence','actual_deployment_qualification','actual_effect_applied'):self.assertIsNone(info[key])
        self.assertFalse(info['run_updated']);self.assertIn('名称',model.player_text(info));self.assertNotIn('tile_pollution_roadf',model.player_text(info))
        self.assertIn('效果尚未核验',model.label(row));self.assertIn('不能判断是否有额外效果',model.player_text(info))
        self.assertNotIn('原资料未为这类地块提供额外效果',model.player_text(info))

    def test_exact_map_rechecks_source_pair_and_original_parameters(self):
        row=next(r for r in self.reference['rows'] if r['tile_key']=='tile_healing');info=model.detail(row['key'],reference=self.reference)
        mapped=model.exact_map(info);self.assertIsNotNone(mapped);self.assertEqual(mapped['stage_id'],row['stage_id'])
        for r,c in row['cells']:self.assertEqual(mapped['tiles'][mapped['map'][r][c]],row['tile'])
        bad=deepcopy(info);bad['row']['tile']['tileKey']='tile_start';self.assertIsNone(model.exact_map(bad))
        bad=deepcopy(info);bad['row']['stage_id']='ro6_t_6';self.assertIsNone(model.exact_map(bad))
        with patch.object(model.terrain,'evidence_identity',return_value=None):self.assertIsNone(model.packet());self.assertIsNone(model.exact_map(info))

    def test_no_implicit_selection_and_exact_manual_cell_navigation(self):
        p=self.panel();self.assertIsNone(p.result);self.assertFalse(p.open_button.isEnabled())
        row=next(r for r in self.reference['rows'] if r['tile_key']=='tile_healing')
        self.assertTrue(p.select_target(row['key']));self.assertEqual(p.cells.currentIndex(),-1);self.assertFalse(p.open_button.isEnabled())
        p.cells.setCurrentIndex(0);self.assertTrue(p.open_map());child=p.map_dialog;self.app.processEvents()
        self.assertTrue(child.isVisible());self.assertEqual(child.panel.stage_id,row['stage_id']);self.assertEqual(child.panel.selected,tuple(row['cells'][0]))
        self.assertEqual(child.panel.result['tiles'][child.panel.result['map'][row['cells'][0][0]][row['cells'][0][1]]],row['tile'])

    def test_same_source_refresh_preserves_exact_cell_reading_and_owned_map(self):
        p=self.panel();row=next(r for r in self.reference['rows'] if r['tile_key']=='tile_healing')
        p.search.setText(row['terrain_name']);p.kind.setCurrentIndex(p.kind.findData(row['terrain_kind']))
        p.floor.setCurrentIndex(p.floor.findData(row['floor']));p.play_kind.setCurrentIndex(p.play_kind.findData(row['play_kind']));self.app.processEvents()
        filters=(p.search.text(),p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData());self.assertTrue(all(value not in (None,'') for value in filters))
        item=next(p.entries.item(i) for i in range(p.entries.count()) if tuple(p.entries.item(i).data(Qt.ItemDataRole.UserRole))==tuple(row['key']))
        p.entries.setCurrentItem(item);self.assertEqual(p.selected_key,tuple(row['key']));self.assertEqual(p.cells.currentIndex(),-1)
        p.cells.setCurrentIndex(0);p.open_map();child=p.map_dialog
        p.tabs.setCurrentWidget(p.technical);c=p.technical.textCursor();c.setPosition(4);c.setPosition(20,QTextCursor.MoveMode.KeepAnchor);p.technical.setTextCursor(c)
        self.app.processEvents();p.technical.verticalScrollBar().setValue(2)
        expected=(p.selected_key,p.cells.currentData(),p.technical.textCursor().selectedText(),p.technical.verticalScrollBar().value(),p.tabs.currentIndex())
        self.assertTrue(p.refresh_reference());self.app.processEvents()
        self.assertEqual(expected,(p.selected_key,p.cells.currentData(),p.technical.textCursor().selectedText(),p.technical.verticalScrollBar().value(),p.tabs.currentIndex()))
        self.assertIs(p.map_dialog,child);self.assertTrue(child.isVisible())
        self.assertEqual(filters,(p.search.text(),p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData()))

    def test_bad_source_clears_old_map_and_recovery_requires_reselection(self):
        p=self.panel();row=self.reference['rows'][0];p.select_target(row['key']);p.cells.setCurrentIndex(0);p.open_map();child=p.map_dialog
        with patch.object(model.terrain,'evidence_identity',return_value=None):
            self.assertFalse(p.refresh_reference());self.app.processEvents();self.assertIsNone(p.reference);self.assertIsNone(p.result);self.assertEqual(p.entries.count(),0)
            self.assertFalse(child.isVisible());self.assertIsNone(child.panel.result);self.assertIsNone(child.panel.image_raw);self.assertFalse(p.open_button.isEnabled())
        self.assertTrue(p.refresh_reference());self.assertIsNone(p.result);self.assertIsNone(p.selected_key)

    def test_filter_and_dialog_rejection_clear_owned_tree(self):
        p=self.panel();row=self.reference['rows'][0];p.select_target(row['key']);p.cells.setCurrentIndex(0);p.open_map();child=p.map_dialog
        p.search.setText('不存在的地形');self.app.processEvents();self.assertFalse(child.isVisible());self.assertIsNone(p.result)
        d=CurrentTerrainDirectoryDialog();self.addCleanup(d.close);d.show();d.panel.select_target(row['key']);d.panel.cells.setCurrentIndex(0);d.panel.open_map();child=d.panel.map_dialog
        d.reject();self.app.processEvents();self.assertIsNone(d.panel.reference);self.assertIsNone(d.panel.result);self.assertFalse(child.isVisible());self.assertIsNone(child.panel.result)

    def test_forged_or_malformed_key_never_reuses_old_target(self):
        p=self.panel();row=self.reference['rows'][0];p.select_target(row['key']);p.cells.setCurrentIndex(0);p.result['row']['cells'][0]=[-1,-1]
        self.assertFalse(p.open_map());self.assertIsNone(p.reference);self.assertIsNone(p.result)
        self.assertTrue(p.refresh_reference());self.assertFalse(p.select_target(('wrong',True)));self.assertIsNone(p.result)
        for key in (None,'x',['x'],['x',True],['x',0,1]):self.assertIsNone(model.detail(key,reference=self.reference))


    def test_nonempty_combined_effect_kind_floor_and_source_matches_exact_order(self):
        p=self.panel();exemplar=next(r for r in self.reference['rows'] if r['tile_key']=='tile_healing')
        p.search.setText(exemplar['terrain_name'])
        p.kind.setCurrentIndex(p.kind.findData(exemplar['terrain_kind']))
        p.floor.setCurrentIndex(p.floor.findData(exemplar['floor']))
        p.play_kind.setCurrentIndex(p.play_kind.findData(exemplar['play_kind']));self.app.processEvents()
        expected=model.rows(exemplar['terrain_name'],exemplar['terrain_kind'],exemplar['floor'],exemplar['play_kind'],reference=self.reference)
        actual=[tuple(p.entries.item(i).data(Qt.ItemDataRole.UserRole))for i in range(p.entries.count())]
        self.assertTrue(expected);self.assertEqual(actual,[tuple(r['key'])for r in expected])
        self.assertEqual((p.kind.currentData(),p.floor.currentData(),p.play_kind.currentData()),(exemplar['terrain_kind'],exemplar['floor'],exemplar['play_kind']))
        self.assertIsNone(p.result);self.assertFalse(p.open_button.isEnabled())

    def test_actual_owned_map_X_and_Escape_clear_data_and_can_manually_reopen(self):
        p=self.panel();row=next(r for r in self.reference['rows']if r['tile_key']=='tile_healing');p.select_target(row['key']);p.cells.setCurrentIndex(0)
        self.assertTrue(p.open_map());child=p.map_dialog;child.close();self.app.processEvents()
        self.assertIsNone(p.map_dialog);self.assertFalse(child.isVisible());self.assertIsNone(child.panel.result);self.assertIsNone(child.panel.image_raw)
        self.assertTrue(p.open_map());child=p.map_dialog;QTest.keyClick(child,Qt.Key.Key_Escape);self.app.processEvents()
        self.assertIsNone(p.map_dialog);self.assertFalse(child.isVisible());self.assertIsNone(child.panel.result);self.assertIsNone(child.panel.image_raw)
        self.assertTrue(p.open_map());self.assertTrue(p.map_dialog.isVisible());self.assertEqual(p.map_dialog.panel.selected,tuple(row['cells'][0]))

    def test_actual_directory_Escape_clears_directory_and_map_actual_data(self):
        row=next(r for r in self.reference['rows']if r['tile_key']=='tile_healing')
        d=CurrentTerrainDirectoryDialog();self.addCleanup(d.close);d.show();d.panel.select_target(row['key']);d.panel.cells.setCurrentIndex(0);self.assertTrue(d.panel.open_map())
        child=d.panel.map_dialog;QTest.keyClick(d,Qt.Key.Key_Escape);self.app.processEvents()
        self.assertFalse(d.isVisible());self.assertIsNone(d.panel.reference);self.assertIsNone(d.panel.result);self.assertIsNone(d.panel.selected_key)
        self.assertEqual(d.panel.entries.count(),0);self.assertIsNone(d.panel.map_dialog)
        self.assertFalse(child.isVisible());self.assertIsNone(child.panel.result);self.assertIsNone(child.panel.image_raw)

if __name__=='__main__':unittest.main()
