import tempfile
import unittest
from pathlib import Path
from rouge.run_state import RunState


class InventoryToolTests(unittest.TestCase):
    def test_one_owned_name_cannot_resolve_two_shared_art_slots(self):
        with tempfile.TemporaryDirectory() as directory:
            memory=RunState(Path(directory)/'run.json')
            base='rogue_6_relic_legacy_22';variant=base+'_a'
            icon={'id':base,'candidates':[base,variant],'confirmed':False}
            observation={'relics':{'ids':[variant],'count':2,'source':'held_bar','icons':[
                {**icon,'center':[.18,.95]},{**icon,'center':[.23,.95]}],
                'cards':[{'id':variant,'candidates':[variant],'confirmed':True,'source':'held_name_and_usage'}]},'operators':[]}
            memory.apply(observation,memory.state['started_at']+1)
            self.assertFalse(memory.inventory_status()['complete'])
            self.assertEqual(memory.held_relic_ids(),[variant])

    def test_exact_owned_card_resolves_a_unique_ambiguous_slot_without_forgetting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            memory=RunState(Path(directory)/'run.json');at=memory.state['started_at']+1
            base='rogue_6_relic_legacy_22';variant=base+'_a'
            icon={'id':base,'candidates':[base,variant,base+'_b',base+'_c'],'confirmed':False,'center':[.18,.95]}
            observation={'relics':{'ids':[variant],'count':1,'source':'held_bar','icons':[icon],
                'cards':[{'id':variant,'candidates':[variant],'confirmed':True,'source':'held_name_and_usage'}]},'operators':[]}
            memory.apply(observation,at)
            self.assertTrue(memory.inventory_status()['complete'])
            self.assertEqual(memory.held_relic_ids(),[variant])
            memory.apply({'relics':{'ids':[],'count':1,'source':'held_bar','icons':[icon]},'operators':[]},at+1)
            self.assertTrue(memory.inventory_status()['complete'])
            self.assertEqual(memory.held_relic_ids(),[variant])

    def test_total_badge_includes_tactical_tools_and_memory_keeps_partial_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'run.json';memory=RunState(file);at=memory.state['started_at']+1
            relics=['rogue_6_relic_cargo_1','rogue_6_relic_fight_26'];tool='rogue_6_active_tool_5'
            observation={'relics':{'ids':relics,'count':3,'source':'held_bar',
                'icons':[{'id':i,'candidates':[i],'confirmed':True} for i in relics+[tool]]},
                'tactical_tools':{'ids':[tool],'source':'held_bar'},'operators':[]}
            memory.apply(observation,at)
            self.assertTrue(memory.inventory_status()['complete'])
            self.assertEqual(memory.inventory_status()['recognized'],2)
            self.assertEqual(memory.inventory_status()['recognized_tools'],1)
            self.assertEqual(memory.inventory_status()['expected_count'],2)
            self.assertEqual(memory.held_tool_ids(),[tool])
            memory.apply({'relics':{'ids':[relics[0]],'count':None,'icons':[],'source':'held_bar'},'operators':[]},at+1)
            restored=RunState(file)
            self.assertEqual(restored.held_tool_ids(),[tool])
            self.assertEqual(restored.held_relic_ids(),sorted(relics))
            self.assertTrue(restored.inventory_status()['complete'])
            restored.apply({'relics':{'ids':relics,'count':2,'source':'held_bar',
                'icons':[{'id':i,'candidates':[i],'confirmed':True} for i in relics]},
                'tactical_tools':{'ids':[],'source':'held_bar'},'operators':[]},at+2)
            self.assertEqual(restored.held_tool_ids(),[])
            self.assertTrue(any(h['kind']=='tool_no_longer_held' for h in restored.state['history']))
            restored.reset()
            self.assertEqual(restored.held_relic_ids(),[])
            self.assertEqual(restored.held_tool_ids(),[])
