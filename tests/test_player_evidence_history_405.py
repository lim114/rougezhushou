from copy import deepcopy
import unittest
from rouge.catalog import catalog,tactical_tools
from rouge.player_evidence_history import evidence_rows,evidence_text

class EvidenceHistoryTests(unittest.TestCase):
    def test_relic_tool_and_roster_records_are_distinct_not_drop_events(self):
        relic=next(iter(catalog()['relics']));tool=next(iter(tactical_tools()))
        state={'history':[{'kind':'relic_confirmed','id':relic,'at':2},{'kind':'tool_confirmed','id':tool,'at':2},{'kind':'operator_updated','id':'mechanist','at':2,'fields':{'elite':1,'level':80}},{'kind':'node_content_seen','at':2,'title':'同帧读到的节点'}]};before=deepcopy(state)
        rows=evidence_rows(state);self.assertEqual([r['kind']for r in rows],['relic','tool','operator']);self.assertEqual(state,before)
        for row in rows:
            text=evidence_text(row);self.assertIn('不能证明该节点发放',text);self.assertIn('确认持有不是本次获得',text);self.assertEqual(row['same_time_contexts'],['同帧读到的节点'])
        self.assertIn('机械师',evidence_text(rows[2]));self.assertIn('等级：80',evidence_text(rows[2]))
    def test_missing_invalid_or_boolean_time_does_not_link_other_unknown_times(self):
        for at in(None,True,float('nan'),float('inf')):
            rows=evidence_rows({'history':[{'kind':'relic_confirmed','id':'not-known','at':at},{'kind':'node_content_seen','title':'不能归因','at':at}]})
            self.assertEqual(rows[0]['same_time_contexts'],[]);self.assertIn('未核对',rows[0]['name'])
    def test_departure_and_no_longer_held_are_only_explicit_saved_events(self):
        state={'history':[{'kind':'operator_no_longer_present','id':'mechanist','at':1},{'kind':'relic_no_longer_held','id':'missing','at':2},{'kind':[]},None]}
        rows=evidence_rows(state);self.assertEqual(len(rows),2);self.assertEqual(rows[0]['label'],'确认离队');self.assertEqual(rows[1]['label'],'确认不再持有')
    def test_invalid_operator_fields_not_invented_from_account_or_current_profile(self):
        row=evidence_rows({'history':[{'kind':'operator_updated','id':'mechanist','fields':{'elite':True,'level':900,'potential':'6'}}]})[0]
        text=evidence_text(row);self.assertNotIn('等级：900',text);self.assertNotIn('潜能：6',text);self.assertNotIn('精英阶段：True',text)

if __name__=='__main__':unittest.main()
