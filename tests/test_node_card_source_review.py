"""Accepted public statistics, local cache failures, and retained node readings."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget
from rouge import public_node_statistics as statistics,player_map_reference as model
from rouge.node_statistics_source import NodeStatisticsSource
from rouge.player_map import MapPanel,PreviewMapView
from rouge.player_map_hover import NodeHoverCard
from rouge.player_map_acceptance import fixtures


def public_example(trader=70):
    return {'schema':'rouge-public-node-frequency-v1','metadata':{
        'sourceSchemaVersion':'merged-node-distance@1','updatedAt':'2026-10-20T00:00:00Z','sampleCount':100},
        'counts':{'rogue-trader':{'0':{'2':trader}},'encounter':{'0':{'2':100-trader}}},
        'scope':'Synthetic public fixture, not actual website data.'}


class IndexTests(unittest.TestCase):
    def test_all_606_queries_match_existing_count_and_denominator_semantics(self):
        data=statistics.load();index=statistics.FrequencyIndex(data)
        for floor in ('0','1','2','3','4','remembrance'):
            for distance in range(101):
                self.assertEqual(index.rows(floor,distance),statistics.frequency_rows(data,floor,distance))

    def test_public_snapshot_preserves_exact_keys_aliases_and_type_order(self):
        data=public_example();data['counts']['rogue-trader']['0']['02']=17;data['metadata']['sampleCount']+=17
        index=statistics.FrequencyIndex(data)
        self.assertEqual(index.rows('0',2),statistics.frequency_rows(data,'0',2))
        self.assertEqual([r['count']for r in index.rows('0',2)],[70,30])
        reverse=deepcopy(data);reverse['counts']=dict(reversed(list(data['counts'].items())))
        self.assertNotEqual(index.identity,statistics.FrequencyIndex(reverse).identity)
        with self.assertRaises(ValueError):index.rows('0',True)

    def test_snapshot_and_returned_rows_do_not_change_with_caller_mutation(self):
        data=public_example();index=statistics.FrequencyIndex(data)
        data['counts']['rogue-trader']['0']['2']=99;data['metadata']['updatedAt']='2000-01-01'
        rows=index.rows('0',2);rows[0]['frequency']=0
        self.assertEqual(index.rows('0',2)[0]['frequency'],.7)
        self.assertEqual(index.metadata['updatedAt'],'2026-10-20T00:00:00Z')


class SourceAndCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def source(self):
        folder=TemporaryDirectory();self.addCleanup(folder.cleanup)
        return NodeStatisticsSource(Path(folder.name)/'nodes.json')

    def test_accept_persists_once_and_retrieval_time_does_not_rebuild_views(self):
        source=self.source();events=[];source.changed.connect(lambda:events.append(source.index.identity))
        self.assertTrue(source.accept(public_example()));self.assertEqual(len(events),1)
        data=public_example();data['retrieved_at']='a later retrieval'
        self.assertFalse(source.accept(data));self.assertEqual(len(events),1)
        reloaded=NodeStatisticsSource(source.cache)
        self.assertEqual(reloaded.index.rows('0',2)[0]['frequency'],.7)
        self.assertEqual(reloaded.data['retrieved_at'],'a later retrieval')

    def test_invalid_or_unwritable_update_retains_last_good_source_and_file(self):
        source=self.source();source.accept(public_example());raw=source.cache.read_bytes();identity=source.index.identity
        events=[];source.changed.connect(lambda:events.append(True))
        bad=public_example();bad['metadata']['sampleCount']=101
        with self.assertRaises(ValueError):source.accept(bad)
        for bad in (None,[],True,12,'missing'):
            with self.assertRaises(ValueError):source.accept(bad)
        for metadata in (None,[],True,12,'missing'):
            bad=public_example();bad['metadata']=metadata
            with self.assertRaises(ValueError):source.accept(bad)
        with patch('rouge.node_statistics_source.os.replace',side_effect=OSError('test write failure')):
            with self.assertRaises(OSError):source.accept(public_example(80))
        self.assertEqual(source.cache.read_bytes(),raw);self.assertEqual(source.index.identity,identity)
        self.assertEqual(source.index.rows('0',2)[0]['frequency'],.7);self.assertEqual(events,[])

    def test_corrupt_cache_is_explicitly_empty_not_an_older_bundled_rate(self):
        source=self.source()
        for raw in ('{','null','[]','true','12','"missing"'):
            source.cache.write_text(raw,'utf8');damaged=NodeStatisticsSource(source.cache)
            self.assertIsNone(damaged.data);self.assertEqual(model.historical_rows('zone_1',2,damaged.index),())
        for metadata in (None,[],True,12,'missing'):
            bad=public_example();bad['metadata']=metadata;source.cache.write_text(json.dumps(bad),'utf8')
            damaged=NodeStatisticsSource(source.cache)
            self.assertIsNone(damaged.data);self.assertEqual(model.historical_rows('zone_1',2,damaged.index),())

    def test_statistics_dialog_and_source_keep_same_snapshot_after_failed_update(self):
        from rouge.public_node_statistics_view import StatisticsDialog
        source=self.source();source.accept(public_example());dialog=StatisticsDialog(source.cache,source=source)
        self.addCleanup(dialog.close);dialog.distance.setValue(2)
        self.assertEqual(dialog.table.item(0,1).text(),'70.00%')
        dialog.accept_data({'data':public_example(80)})
        self.assertIs(dialog.source,source);self.assertEqual(dialog.table.item(0,1).text(),'80.00%')
        dialog.accept_data({'error':'simulated network failure'})
        self.assertEqual(dialog.table.item(0,1).text(),'80.00%');self.assertIn('更新失败',dialog.status.text())

    def map(self,source):
        graphs,node_id,*_=fixtures();node=next(n for n in graphs[0]['nodes']if n['id']==node_id);node['distance']=2
        owner=SimpleNamespace(run=SimpleNamespace(state={'id':'isolated','maps':{g['zone_id']:g for g in graphs},'config':{}}),
            map_view=SimpleNamespace(graph=None,historical=False),compact_window=None)
        panel=MapPanel(owner,statistics_source=source);self.addCleanup(panel.close);panel.resize(1000,650);panel.show();self.qt.processEvents()
        return panel,node_id

    def test_accepted_update_reaches_map_pinned_card_and_overlay_without_sampling(self):
        from rouge.player_game_map import GameMapOverlay
        source=self.source();source.accept(public_example());panel,node_id=self.map(source)
        panel.set_type_filter('诡意行商');graph=panel.view.graph
        binding=(panel.epoch,graph['zone_id'],graph['template_id'],node_id)
        card=panel.hover_card;card.install(binding,graph,node_id,{},panel.view);card.show();card.pin.setChecked(True)
        self.assertEqual(card.type_values['诡意行商'],'历史 70.00%')
        holder=QWidget();self.addCleanup(holder.close);overlay=GameMapOverlay(holder,panel.owner,statistics_source=source)
        self.addCleanup(overlay.close);overlay.timer.stop()
        source.accept(public_example(80));self.qt.processEvents()
        self.assertEqual(panel.view.overlay[node_id]['frequency']['frequency'],.8)
        self.assertEqual(card.type_values['诡意行商'],'历史 80.00%')
        self.assertTrue(card.pinned);self.assertEqual(card.binding,binding)
        self.assertIs(overlay.surface.frequencies,source.index)
        self.assertIsNone(overlay.current);self.assertIsNone(overlay.surface.data)
        panel.hide()
        with patch.object(panel,'refresh',wraps=panel.refresh)as refresh:
            source.accept(public_example(90));refresh.assert_not_called()
        panel.show();panel.refresh();self.qt.processEvents()
        self.assertEqual(panel.view.overlay[node_id]['frequency']['frequency'],.9)

    def test_passed_and_unconfirmed_nodes_show_only_actual_saved_history(self):
        for observed in ('林间空地','未知的诡秘'):
            graph={'zone_id':'zone_1','template_id':'isolated','grid':{'rows':3},'nodes':[{
                'id':'old','row':1,'col':1,'observed_type':observed,'remembered_type':'不期而遇',
                'remembered_content':{'kind':'event','title':'桑尼的邀请'},
                'content_history':[{'kind':'battle','title':'遗忘时间','variant_id':'ro6_n_1_2'}]}]}
            before=deepcopy(graph);result=model.node_dossier(graph,'old',{})
            self.assertEqual(result['rows'],[]);self.assertEqual(result['battle_rows'],[])
            self.assertTrue(result['history_observed_event_rows']);self.assertTrue(result['history_observed_battle_rows'])
            view=PreviewMapView();self.addCleanup(view.close);view.historical=False
            card=NodeHoverCard(view);self.addCleanup(card.close);card.install(('run','zone_1','isolated','old'),graph,'old',{},view)
            self.assertTrue(card.entry_buttons)
            self.assertTrue(all(b.property('referenceScope')=='history'for _,_,b in card.entry_buttons))
            actions=[];card.entryRequested.connect(lambda *args:actions.append(args));card.show();self.qt.processEvents()
            kind,identity,button=card.entry_buttons[0];QTest.mouseClick(button,Qt.MouseButton.LeftButton)
            self.assertEqual(actions,[('old',kind,identity)]);self.assertEqual(graph,before)

    def test_old_type_without_read_title_does_not_expand_into_global_directory(self):
        graph={'zone_id':'zone_1','template_id':'isolated','grid':{'rows':3},'nodes':[{
            'id':'old','row':1,'col':1,'observed_type':'未知的诡秘','remembered_type':'诡意行商'}]}
        self.assertIsNone(model.node_dossier(graph,'old',{}))


if __name__=='__main__':unittest.main()
