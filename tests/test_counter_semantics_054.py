"""Counter meaning, bounds and persistent last-confirmed value contracts."""
import copy
import tempfile
import unittest
from pathlib import Path

from rouge.relic_counter_semantics import (
    COUNTER_BINDINGS,_verified_bindings,counter_resources,valid_counter_resource)
from rouge.run_state import RunState


class CounterSemanticsTests(unittest.TestCase):
    def proof(self,rid,value):
        return {'id':rid,'title':_verified_bindings()[rid]['name'],'value':value,
                'source':'held_full_name_usage_and_dynamic_held_glyph_local_numeric_ocr',
                'box':[[.1,.1],[.2,.1],[.2,.2],[.1,.2]],
                'marker':{'box':[[.05,.1],[.1,.1],[.1,.2],[.05,.2]]},
                'score':.99,'confidence':.99}

    def test_each_binding_crosschecks_own_original_layer_and_effect_maximum(self):
        self.assertEqual(set(_verified_bindings()),set(COUNTER_BINDINGS))
        for rid,(key,_,maximum) in COUNTER_BINDINGS.items():
            for value in (0,1,maximum):
                with self.subTest(rid=rid,value=value):
                    record=self.proof(rid,value);before=copy.deepcopy(record)
                    resource=counter_resources([record])[key]
                    self.assertEqual(resource['value'],value)
                    self.assertTrue(valid_counter_resource(key,resource))
                    self.assertEqual(record,before)
                    resource['counter_evidence']['value']=1234
                    self.assertEqual(record,before)

    def test_no_count_does_not_mean_zero(self):
        self.assertEqual(counter_resources([]),{})

    def test_invalid_or_conflicting_marker_never_updates_condition(self):
        rid='rogue_6_relic_legacy_103'
        for value in (True,-1,11,1.5,'1',None):
            self.assertEqual(counter_resources([self.proof(rid,value)]),{})
        a=self.proof(rid,1);b=self.proof(rid,2)
        self.assertEqual(counter_resources([a,b]),{})
        self.assertEqual(counter_resources([a,copy.deepcopy(a)]),{})
        for field,value in (('title','圆石祭'),('source','reward_offer')):
            invalid={**a,field:value}
            self.assertEqual(counter_resources([invalid]),{})

    def test_uncapped_parts_history_recipients_and_unsupported_counts_are_not_inferred(self):
        for rid in ('rogue_6_relic_cargo_2','rogue_6_start_3','rogue_6_start_4','rogue_6_relic_assign_15'):
            record={'id':rid,'title':'fixture','value':1,'source':'held_full_name_usage_and_fixture'}
            self.assertEqual(counter_resources([record]),{})
        resource=counter_resources([self.proof('rogue_6_relic_legacy_136',3)])
        self.assertEqual(set(resource),{'mercenary_stacks'})
        self.assertNotIn('mercenary_recipient',resource)

    def test_forged_resource_value_or_provenance_fails_persistence_contract(self):
        resource=counter_resources([self.proof('rogue_6_relic_legacy_103',1)])['altar_stacks']
        for field,value in (('value',2),('relic_id','rogue_6_relic_cargo_11'),
                            ('source','fixture'),('counter_rune','other')):
            self.assertFalse(valid_counter_resource('altar_stacks',{**resource,field:value}))
        self.assertFalse(valid_counter_resource('parts_count',resource))

    def test_same_run_partial_reads_preserve_history_and_new_values_sync(self):
        with tempfile.TemporaryDirectory() as directory:
            run=RunState(Path(directory)/'run.json');identity=run.state['id'];at=run.state['started_at']+1
            def observed(value):
                resources={} if value is None else counter_resources([self.proof('rogue_6_relic_legacy_103',value)])
                return {'relics':{'ids':['rogue_6_relic_legacy_103'],'count':None,'icons':[],
                                 'source':'held_bar'},'operators':[],'resources':resources}
            run.apply(observed(1),captured_at=at)
            first=copy.deepcopy(run.state['resources']['altar_stacks'])
            run.apply(observed(None),captured_at=at+1)
            self.assertEqual(run.state['resources']['altar_stacks'],first)
            run.apply(observed(2),captured_at=at+2)
            self.assertEqual(run.state['resources']['altar_stacks']['value'],2)
            self.assertEqual(run.state['id'],identity)
            self.assertEqual([h['value'] for h in run.state['history'] if h['kind']=='resource_updated'],[1,2])
            restored=RunState(Path(directory)/'run.json')
            self.assertEqual(restored.state['resources']['altar_stacks']['value'],2)
            self.assertIn('圆石祭坛层数 2',restored.summary())


if __name__=='__main__':unittest.main()
