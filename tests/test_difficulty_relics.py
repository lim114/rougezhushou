import unittest,tempfile
from pathlib import Path
from rouge.run_state import RunState

class DifficultyRelicTests(unittest.TestCase):
    def test_missing_grade_and_cross_family_artwork_remain_unconfirmed(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');base='rogue_6_relic_legacy_22'
            icon={'id':base,'candidates':[base,base+'_a',base+'_b',base+'_c'],'confirmed':False}
            observation={'relics':{'ids':[],'icons':[icon],'count':1,'source':'held_bar'},'operators':[]}
            run.apply(observation,run.state['started_at']+1)
            self.assertEqual(run.held_relic_ids(),[])
            self.assertFalse(run.inventory_status()['complete'])
            icon['candidates']+=['rogue_6_relic_legacy_23']
            run.apply({**observation,'config':{'difficulty':{'value':10}}},run.state['started_at']+2)
            self.assertEqual(run.held_relic_ids(),[])
            self.assertFalse(run.inventory_status()['complete'])

    def test_same_artwork_resolves_its_current_difficulty_tier_and_keeps_signature(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');base='rogue_6_relic_legacy_22'
            icon={'id':base,'candidates':[base,base+'_a',base+'_b',base+'_c'],'confirmed':False,'center':[.18,.95]}
            observation={'config':{'difficulty':{'value':10,'source':'本局等级标签'}},
                         'relics':{'ids':[],'icons':[icon],'count':1,'source':'held_bar'},'operators':[]}
            run.apply(observation,run.state['started_at']+1)
            self.assertEqual(run.held_relic_ids(),[base+'_c'])
            self.assertTrue(run.inventory_status()['complete'])
            signature=run.state['bar_signature']
            run.apply({**observation,'config':{}},run.state['started_at']+2)
            self.assertEqual(run.held_relic_ids(),[base+'_c'])
            self.assertEqual(run.state['bar_signature'],signature)
