import tempfile
import time
import unittest
from pathlib import Path
from rouge.run_state import RunState


class TargetMemoryTests(unittest.TestCase):
    def test_partial_bindings_merge_but_recruitment_change_requires_new_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json')
            def observe(**member):
                run.apply({'relics':{'ids':[],'source':'test'},'operators':[
                    {'id':'mechanist','scope':'run','fields':{},**member}]},time.time())
            observe(recruitment_kind='non_emergency',char_buff_ids=['rogue_6_from_relic_9'])
            observe(char_buff_ids=['rogue_6_from_relic_12'])
            self.assertEqual(set(run.state['operators']['mechanist']['char_buff_ids']),
                             {'rogue_6_from_relic_9','rogue_6_from_relic_12'})
            observe(recruitment_kind='emergency_hire')
            self.assertEqual(run.state['operators']['mechanist']['char_buff_ids'],[])
            self.assertTrue(any(h.get('previous_char_buff_ids')==['rogue_6_from_relic_9','rogue_6_from_relic_12']
                                for h in run.state['history']))
            before=run.file.read_bytes()
            with self.assertRaisesRegex(ValueError,'职业不符'):
                observe(char_buff_ids=['rogue_6_from_relic_5'])
            self.assertEqual(run.file.read_bytes(),before)

    def test_recipient_bindings_survive_missing_pages_restart_and_item_consumption(self):
        with tempfile.TemporaryDirectory() as directory:
            file=Path(directory)/'run.json';run=RunState(file)
            def observe(**member):
                run.apply({'relics':{'ids':[],'count':0,'icons':[],'source':'test'},
                           'operators':[{'id':'mechanist','scope':'run','fields':{},**member}]},time.time())
            observe(char_buff_ids=['rogue_6_from_relic_9'],char_buffs_complete=True)
            observe()
            restored=RunState(file)
            self.assertEqual(restored.state['operators']['mechanist']['char_buff_ids'],['rogue_6_from_relic_9'])
            self.assertEqual(restored.held_relic_ids(),[])
            self.assertTrue(any(h['kind']=='char_buffs_updated' for h in restored.state['history']))
            run=restored
            observe(char_buff_ids=[],char_buffs_complete=True)
            self.assertEqual(run.state['operators']['mechanist']['char_buff_ids'],[])
            self.assertTrue(any(h.get('char_buff_ids')==['rogue_6_from_relic_9'] for h in run.state['history']))
            run.reset()
            self.assertEqual(run.state['operators'],{})
