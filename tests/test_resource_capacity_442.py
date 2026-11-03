"""Capacity is an observation, independent of quantity and later records."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from rouge.run_state import RunState
from rouge.player_resource_history import resource_rows, resource_text, ResourceHistoryPage
from rouge.player_floor_resources import snapshots, snapshot_text
from PySide6.QtWidgets import QApplication

class ResourceCapacity442Tests(unittest.TestCase):
    def setUp(self):
        folder=self.enterContext(TemporaryDirectory(prefix='rouge-capacity442-'))
        self.file=Path(folder)/'run.json';self.run=RunState(self.file);self.at=self.run.state['started_at']+1
    def observe(self,record,key='hope',**extra):
        incoming={'relics':{'ids':[],'count':None},'resources':{key:record},**extra}
        before=deepcopy(incoming);self.run.apply(incoming,self.at);self.at+=1;self.assertEqual(incoming,before)
    def events(self):return [e for e in self.run.state['history']if e.get('kind')=='resource_updated']
    def test_first_capacity_is_saved_with_its_own_historical_read(self):
        self.observe({'value':7,'capacity':13})
        self.assertEqual(self.events()[0]['capacity'],13)
        loaded=RunState(self.file)
        self.assertEqual(loaded.state['history'],self.run.state['history'])
        self.assertIn('13',resource_text(resource_rows(loaded.state)[0]))
    def test_capacity_change_without_quantity_change_is_not_lost(self):
        self.observe({'value':7,'capacity':13});self.observe({'value':7,'capacity':17})
        rows=resource_rows(self.run.state)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[-1]['delta'],0)
        self.assertEqual(rows[-1]['capacity_delta'],4)
        self.assertIn('上限',resource_text(rows[-1]))
    def test_upgrade_records_a_fresh_capacity_without_rewriting_legacy_history(self):
        legacy={'kind':'resource_updated','resource':'hope','value':7,'at':self.at-1}
        self.run.state['history'].append(deepcopy(legacy))
        self.run.state['resources']['hope']={'value':7,'capacity':13,'captured_at':self.at-1}
        self.observe({'value':7,'capacity':13})
        self.assertEqual(self.run.state['history'][0],legacy)
        self.assertEqual(self.events()[-1].get('capacity'),13)
        self.assertEqual(self.events()[-1]['at'],self.at-1)
    def test_missing_capacity_breaks_comparison_and_never_reuses_a_later_limit(self):
        self.observe({'value':7,'capacity':13});self.observe({'value':7});self.observe({'value':7,'capacity':18})
        rows=resource_rows(self.run.state)
        self.assertEqual(len(rows),3)
        self.assertIsNone(rows[1]['capacity'])
        self.assertIsNone(rows[2]['previous_capacity'])
        self.assertIsNone(rows[2]['capacity_delta'])
        self.assertNotIn('18',resource_text(rows[0]))
    def test_parts_capacity_uses_capacity_label_and_preserves_zero_quantity(self):
        self.observe({'value':0,'capacity':8},'parts_count');self.observe({'value':0,'capacity':12},'parts_count')
        rows=resource_rows(self.run.state);self.assertEqual(len(rows),2)
        self.assertIn('容量',resource_text(rows[-1]));self.assertEqual(rows[-1]['capacity_delta'],4)
    def test_floor_snapshots_distinguish_equal_quantities_with_different_limits(self):
        from rouge.run_config import config_data
        zid=next(iter(config_data()['zones']));config={'zone':{'id':zid,'name':config_data()['zones'][zid]['name']}}
        self.observe({'value':7,'capacity':13},config=config)
        self.observe({'value':7,'capacity':17},config=config)
        rows=snapshots(self.run.state)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['capacities'],{'hope':13});self.assertEqual(rows[1]['capacities'],{'hope':17})
        self.assertIn('7/13',snapshot_text(rows[0]));self.assertNotIn('7/17',snapshot_text(rows[0]))
    def test_legacy_scalar_read_is_not_backfilled_from_current_resource(self):
        self.run.state['history']=[{'kind':'resource_updated','resource':'hope','value':7,'at':1}]
        self.run.state['resources']['hope']={'value':7,'capacity':99}
        row=resource_rows(self.run.state)[0]
        self.assertNotIn('capacity',row);self.assertNotIn('99',resource_text(row))

class ResourceCapacityWidgets442Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_selected_old_limit_survives_newer_data_refresh(self):
        page=ResourceHistoryPage();self.addCleanup(page.close)
        state={'id':'public-capacity442','history':[{'kind':'resource_updated','resource':'hope','value':7,'capacity':13,'at':1}]}
        page.refresh(state);page.entries.setCurrentRow(0)
        self.assertIn('13',page.detail.toPlainText())
        state['history'].append({'kind':'resource_updated','resource':'hope','value':7,'capacity':17,'at':2})
        page.refresh(state)
        self.assertEqual(page.entries.currentRow(),0)
        self.assertIn('13',page.detail.toPlainText());self.assertNotIn('17',page.detail.toPlainText())

    def test_map_history_pills_use_only_the_selected_steps_capacity(self):
        from tests.test_map_resource_review import graph
        from rouge.player_replay_nodes import NodeReplayPage
        with TemporaryDirectory(prefix='rouge-capacity442-map-')as folder:
            run=RunState(Path(folder)/'run.json');at=run.state['started_at']+1
            run.apply({'map':graph(position=0),'resources':{'hope':{'value':7,'capacity':13}}},at)
            run.apply({'map':graph(position=1),'resources':{'hope':{'value':7,'capacity':17}}},at+1)
            page=NodeReplayPage();self.addCleanup(page.close);page.refresh(run.state);page.entries.setCurrentRow(0)
            self.assertEqual(page.resource_pills.chips['history:hope'].accessibleName(),'希望 7/13')
            run.apply({'resources':{'hope':{'value':7,'capacity':99}}},at+2)
            page.refresh(run.state)
            self.assertEqual(page.entries.currentRow(),0)
            self.assertEqual(page.resource_pills.chips['history:hope'].accessibleName(),'希望 7/13')

if __name__=='__main__':unittest.main()
