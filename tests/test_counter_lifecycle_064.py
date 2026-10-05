"""Known current counters across persistence and calculation (constructed data)."""
import copy
import tempfile
import unittest
from pathlib import Path

from rouge.damage import calculate_damage
from rouge.run_state import RunState
from rouge.relic_counter_semantics import COUNTER_BINDINGS,counter_resources
from tests import test_counter_semantics_054 as counter_fixtures
from tests.test_recipient_lifecycle_063 import full_bar

ALTAR='rogue_6_relic_legacy_103'


def observed(rid,value):
    return {**full_bar(rid),'resources':counter_resources([counter_fixtures.CounterSemanticsTests().proof(rid,value)])}


class CounterLifecycle064Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.path=Path(temp.name)/'run.json';self.run=RunState(self.path)
        self.at=self.run.state['started_at']+1

    def apply(self,data):
        assert self.run.apply(data,self.at);self.at+=1

    def context(self):
        return {key:record['value'] for key,record in self.run.calculation_resources().items()}

    def result(self,extra=None):
        return calculate_damage({'operator':'mechanist','skill':3,
            'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_2137_shsdgo','level':0},
            'relic_ids':self.run.held_relic_ids(),'relic_context':{**self.context(),**(extra or {})}})

    def test_every_counter_remains_available_across_partial_pages_and_restart(self):
        for rid,(key,_,maximum) in COUNTER_BINDINGS.items():
            with self.subTest(rid=rid):
                self.apply(observed(rid,maximum));self.apply({'operators':[]})
                self.run=RunState(self.path)
                self.assertEqual(self.context()[key],maximum)

    def test_every_confirmed_loss_preserves_but_withholds_previous_value_on_reacquisition(self):
        for rid,(key,_,maximum) in COUNTER_BINDINGS.items():
            with self.subTest(rid=rid):
                self.apply(observed(rid,maximum));old=copy.deepcopy(self.run.state['resources'][key])
                self.apply(full_bar());self.apply(full_bar(rid))
                self.assertNotIn(key,self.context())
                self.assertEqual(self.run.state['resources'][key],old)
                self.run=RunState(self.path);self.assertNotIn(key,self.context())

    def test_fresh_same_frame_reacquisition_counter_overrides_older_loss_even_when_lower(self):
        for rid,(key,_,maximum) in COUNTER_BINDINGS.items():
            with self.subTest(rid=rid):
                self.apply(observed(rid,maximum));self.apply(full_bar());self.apply(observed(rid,1))
                self.assertEqual(self.context()[key],1)

    def test_zero_is_confirmed_value_and_not_missing(self):
        self.apply(observed(ALTAR,0))
        self.assertEqual(self.context()['altar_stacks'],0)
        self.assertEqual(self.result()['estimate']['base_stats']['attack'],573)
        record=next(r for r in self.result()['relic_resolution']['records'] if r['id']==ALTAR)
        self.assertEqual(record['missing_conditions'],[])

    def test_missing_after_reacquisition_is_unknown_not_zero_or_full(self):
        self.apply(observed(ALTAR,10));self.apply(full_bar());self.apply(full_bar(ALTAR))
        result=self.result();record=result['relic_resolution']['records'][0]
        self.assertIn('altar_stacks',record['missing_conditions'])
        self.assertFalse(result['estimate']['complete'])
        self.assertEqual(result['estimate']['base_stats']['attack'],573)
        self.assertIn('历史值，当前层数待确认',self.run.summary())

    def test_altar_confirmed_counter_reaches_rounded_attack_and_defense(self):
        # Cultivated 573 ATK / 765 DEF; established rune +5% each layer,
        # integer attributes rounded ties-to-even before ordinary buffs.
        for count,attack,defense in ((0,573,765),(1,602,803),(10,860,1148)):
            self.apply(observed(ALTAR,count));base=self.result()['estimate']['base_stats']
            self.assertEqual((base['attack'],base['defense']),(attack,defense))

    def test_mercenary_count_does_not_identify_recipient(self):
        rid='rogue_6_relic_legacy_136';self.apply(observed(rid,10))
        record=self.result()['relic_resolution']['records'][0]
        self.assertIn('mercenary_recipient',record['missing_conditions'])
        self.assertEqual(self.result()['estimate']['base_stats']['attack'],573)
        before=copy.deepcopy(self.run.state)
        base=self.result({'mercenary_recipient':1})['estimate']['base_stats']
        self.assertEqual((base['hp'],base['attack'],base['defense']),(5446,860,1148))
        self.assertEqual(self.run.state,before)

    def test_fire_rod_counter_reaches_speed_and_cycle_damage_but_not_sp_cost(self):
        rid='rogue_6_relic_cargo_11';self.apply(observed(rid,0));baseline=self.result()['estimate']['skill']
        for count in (1,99):
            self.apply(observed(rid,count));estimate=self.result()['estimate'];base=estimate['base_stats']
            self.assertEqual(base['attack_speed_reference'],100+10*count)
            self.assertEqual(base['attack_speed'],min(600,100+10*count))
            self.assertGreater(estimate['skill']['total_damage'],baseline['total_damage'])
            self.assertGreater(estimate['skill']['cycle_dps'],baseline['cycle_dps'])
            for key in ('sp_cost','initial_seconds','recharge_seconds','cycle_seconds'):
                self.assertEqual(estimate['skill'][key],baseline[key])

    def test_probe_counter_modifies_only_matching_enemy(self):
        rid='rogue_6_relic_fight_30'
        for count in (0,1,99):
            self.apply(observed(rid,count));enemy=self.result()['run_resolution']['enemy']['stats']
            self.assertAlmostEqual(enemy['maxHp'],18000*(1+.2*count))
            self.assertAlmostEqual(enemy['atk'],280*(1+.2*count))
        def other(ids):
            return calculate_damage({'operator':'mechanist','skill':3,'relic_ids':ids,'relic_context':self.context(),
                'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr','level':0}})['run_resolution']['enemy']['stats']
        self.assertEqual(other([rid]),other([]))

    def test_grudge_counter_applies_after_separate_two_percent_rune(self):
        for count in (0,1,999):
            self.apply(observed('rogue_6_relic_artifact_7',count))
            self.assertAlmostEqual(self.result()['estimate']['base_stats']['attack'],584*(1+.002*count))

    def test_reordered_observation_does_not_restore_old_count(self):
        first=self.at;self.apply(observed(ALTAR,10));self.apply(full_bar());self.apply(full_bar(ALTAR))
        before=copy.deepcopy(self.run.state)
        self.assertFalse(self.run.apply(observed(ALTAR,10),first))
        self.assertEqual(self.run.state,before);self.assertNotIn('altar_stacks',self.context())

    def test_bad_saved_counter_evidence_is_withheld_without_rewriting_file(self):
        self.apply(observed(ALTAR,1));self.run.state['resources']['altar_stacks']['value']=10;self.run.save()
        data=self.path.read_bytes();self.run=RunState(self.path)
        self.assertNotIn('altar_stacks',self.context());self.assertEqual(self.path.read_bytes(),data)

    def test_legacy_missing_held_flag_is_not_a_removal(self):
        self.apply(observed(ALTAR,1));self.run.state['relics'][ALTAR].pop('held')
        self.assertEqual(self.context()['altar_stacks'],1)

    def test_same_time_loss_wins_over_ambiguous_counter_but_later_fresh_read_recovers(self):
        self.apply(observed(ALTAR,1));at=self.run.state['resources']['altar_stacks']['captured_at']
        self.run.state['history'].append({'kind':'relic_no_longer_held','id':ALTAR,'at':at})
        self.assertNotIn('altar_stacks',self.context())
        self.apply(observed(ALTAR,2));self.assertEqual(self.context()['altar_stacks'],2)

    def test_future_or_previous_run_timestamps_never_supply_current_layer(self):
        self.apply(observed(ALTAR,1))
        for at in (self.run.state['started_at']-1,self.at+99,float('nan'),True):
            with self.subTest(timestamp=at):
                self.run.state['resources']['altar_stacks']['captured_at']=at
                self.assertNotIn('altar_stacks',self.context())

    def test_gold_parts_and_unrelated_counter_survive_other_relic_loss(self):
        fire='rogue_6_relic_cargo_11';data=observed(ALTAR,2)
        data['resources'].update(counter_resources([counter_fixtures.CounterSemanticsTests().proof(fire,3)]))
        data['resources'].update(gold={'value':25,'source':'map'},parts_count={'value':3,'capacity':12,'source':'footer'})
        data.update(full_bar(ALTAR,fire));self.apply(data);self.apply(full_bar(fire))
        self.assertEqual(self.context(),{'fire_rod_stacks':3,'gold':25,'parts_count':3})
        result=self.run.calculation_resources();result['parts_count']['value']=9
        self.assertEqual(self.run.state['resources']['parts_count']['value'],3)

    def test_manual_new_run_clears_only_temporary_run_and_no_counter_leaks(self):
        self.apply(observed(ALTAR,10));old=self.run.state['id'];self.run.reset()
        self.assertNotEqual(self.run.state['id'],old);self.assertEqual(self.context(),{})


if __name__=='__main__':unittest.main()
