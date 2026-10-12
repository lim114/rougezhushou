"""Source-bound guardian module gates, independent of ordinary healing clocks."""
import copy,unittest
from rouge.damage import calculate_damage
from rouge.guardian_healing import FP_ONE,FP_LARGE_EPS_RAW,FIELD
from rouge.healing_budget import healing_budget
from rouge.reporting import build_report
FORMS=[('char_196_sunbr','uniequip_002_sunbr',2,40),('char_2025_shu','uniequip_002_shu',3,60)]
def evaluate(op='char_196_sunbr',skill=1,**extra):
    module=next(m for actor,m,_,_ in FORMS if actor==op)
    return calculate_damage({'operator':op,'skill':skill,'base_attack':1000,'module_id':module,'module_level':3,**extra})
class GuardianHealingGateTests(unittest.TestCase):
    def test_every_skill_in_both_modes_changes_only_direct_healing(self):
        for op,module,skills,gate in FORMS:
            for skill in range(1,skills+1):
                for mode in ('frames','continuous'):
                    high=evaluate(op,skill,timing_mode=mode,guardian_healing_target_hp_ratio=.8)
                    low=evaluate(op,skill,timing_mode=mode,guardian_healing_target_hp_ratio=.4)
                    for a,b in zip(high['components'],low['components']):
                        self.assertEqual(a['name'],b['name']);self.assertEqual(a['hits'],b['hits'])
                        factor=1.15 if a['damage_type']=='healing' else 1
                        self.assertAlmostEqual(b['per_hit'],a['per_hit']*factor)
                        self.assertAlmostEqual(b['total'],a['total']*factor)
                        if a.get('actual_total') is None:self.assertIsNone(b.get('actual_total'))
                    for key in ('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps'):
                        a=high['estimate']['skill'][key];b=low['estimate']['skill'][key]
                        if a is None:self.assertIsNone(b)
                        else:self.assertAlmostEqual(b,a*1.15)
                    self.assertEqual(high['timing'],low['timing']);self.assertEqual(high['total_damage'],low['total_damage'])
                    self.assertEqual(high['estimate']['base_stats'],low['estimate']['base_stats'])
                    self.assertEqual(high['relic_regeneration_rate'],low['relic_regeneration_rate'])
    def test_equal_threshold_and_exact_fixed_point_boundaries_are_distinct(self):
        for op,sign,equals in [('char_196_sunbr',-1,False),('char_2025_shu',1,True)]:
            boundary=FP_ONE//2+sign*FP_LARGE_EPS_RAW
            for raw,expected in [(boundary-1,True),(boundary,False),(boundary+1,False),(FP_ONE//2,equals)]:
                ref=evaluate(op,guardian_healing_target_hp_ratio=raw/FP_ONE)['guardian_module_healing_reference']
                self.assertEqual(ref['recipient_hp_ratio_raw_reference'],raw);self.assertIs(ref['qualified'],expected)
                self.assertEqual(ref['comparison_boundary_raw'],boundary)
        self.assertIs(evaluate(guardian_healing_target_hp_ratio=.499995)['guardian_module_healing_reference']['qualified'],False)
        self.assertIs(evaluate(guardian_healing_target_hp_ratio=.49998)['guardian_module_healing_reference']['qualified'],True)
        self.assertIs(evaluate('char_2025_shu',guardian_healing_target_hp_ratio=.500005)['guardian_module_healing_reference']['qualified'],True)
    def test_three_stages_and_potential_do_not_stack_trait_three_times(self):
        for op,module,skills,gate in FORMS:
            for stage in (1,2,3):
                for potential in (1,5,6):
                    high=evaluate(op,2,module_level=stage,potential=potential,guardian_healing_target_hp_ratio=.8)
                    low=evaluate(op,2,module_level=stage,potential=potential,guardian_healing_target_hp_ratio=.4)
                    self.assertEqual(low['guardian_module_healing_reference']['res_key'],('sunbr' if op=='char_196_sunbr' else 'shu')+'_equip_1_'+str(stage)+'_p1')
                    self.assertAlmostEqual(low['components'][0]['per_hit'],high['components'][0]['per_hit']*1.15)
    def test_unknown_ratio_keeps_known_subtotals_and_masks_only_affected_outputs(self):
        for op,module,skills,gate in FORMS:
            high=evaluate(op,2,guardian_healing_target_hp_ratio=.8)
            unknown=evaluate(op,2)
            self.assertEqual(high['components'],unknown['components'])
            self.assertEqual(unknown['known_healing_subtotals']['total_healing'],high['estimate']['skill']['total_healing'])
            self.assertIsNone(unknown['total_healing'])
            for key,value in unknown['known_healing_subtotals'].items():
                if value not in (None,0):self.assertIsNone(unknown['estimate']['skill'][key])
            self.assertFalse(unknown['complete']);self.assertFalse(unknown['estimate']['complete'])
            self.assertEqual(high['timing'],unknown['timing'])
    def test_s1_actual_totals_stay_unknown_with_declared_ratio(self):
        for op,module,skills,gate in FORMS:
            low=evaluate(op,1,guardian_healing_target_hp_ratio=.4)
            for key in ('total_healing','cycle_healing','window_healing','cycle_hps'):
                self.assertIsNone(low['estimate']['skill'][key])
            self.assertIsNone(low['components'][0]['actual_total'])
    def test_zero_recipients_and_empty_window_keep_zero_not_unknown(self):
        for op,module,skills,gate in FORMS:
            zero=evaluate(op,2,healing_targets=0)
            self.assertEqual(zero['total_healing'],0);self.assertEqual(zero['estimate']['skill']['total_healing'],0)
            empty=evaluate(op,2,window_seconds=0)
            self.assertEqual(empty['total_healing'],0);self.assertEqual(empty['estimate']['skill']['window_healing'],0)
            self.assertIsNone(empty['estimate']['skill']['window_hps'])
    def test_qualification_gate_is_own_elite_and_level_not_universal40(self):
        for op,module,skills,gate in FORMS:
            for extra in [{'elite':1,'skill_rank':7},{'level':gate-1},{'module_id':None,'module_level':0}]:
                self.assertEqual(evaluate(op,**extra),evaluate(op,guardian_healing_target_hp_ratio=.1,**extra))
                self.assertNotIn('guardian_module_healing_reference',evaluate(op,**extra))
            self.assertIn('guardian_module_healing_reference',evaluate(op,level=gate))
    def test_other_actors_and_susuro_ratio_cannot_control_guardians(self):
        a=calculate_damage({'operator':'char_151_myrtle','skill':2});b=calculate_damage({'operator':'char_151_myrtle','skill':2,FIELD:.1})
        self.assertEqual(a,b)
        for op,module,skills,gate in FORMS:
            self.assertIsNone(evaluate(op,healing_target_hp_ratio=.1)['guardian_module_healing_reference']['recipient_hp_ratio'])
            for extra in [{'current_hp_ratio':.1},{'enemy_current_hp':1},{'missing_hp':99999}]:
                self.assertIsNone(evaluate(op,**extra)['guardian_module_healing_reference']['recipient_hp_ratio'])
    def test_three_flowers_compose_and_regeneration_is_not_multiplied(self):
        ids=['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83','rogue_6_relic_legacy_22','rogue_6_relic_legacy_91']
        for op,module,skills,gate in FORMS:
            high=evaluate(op,2,guardian_healing_target_hp_ratio=.8)
            low=evaluate(op,2,guardian_healing_target_hp_ratio=.4,relic_ids=ids)
            self.assertAlmostEqual(low['components'][0]['per_hit'],high['components'][0]['per_hit']*1.15*2.184)
            h=evaluate(op,2,guardian_healing_target_hp_ratio=.8,relic_ids=ids)
            self.assertEqual(h['relic_regeneration_rate'],low['relic_regeneration_rate'])
            self.assertFalse(low['guardian_module_healing_reference']['natural_regeneration_affected'])
    def test_invalid_ratios_and_result_mutation_are_isolated(self):
        for op,module,skills,gate in FORMS:
            for value in [True,False,'0.4',-.1,1.1,10**1000,float('nan'),float('inf'),[],{}]:
                with self.assertRaises(ValueError):evaluate(op,guardian_healing_target_hp_ratio=value)
            scenario={'operator':op,'skill':2,'module_id':module,'module_level':3,FIELD:.4};before=copy.deepcopy(scenario)
            result=calculate_damage(scenario);result['guardian_module_healing_reference']['factor']=99
            self.assertEqual(scenario,before);self.assertEqual(calculate_damage(scenario)['guardian_module_healing_reference']['factor'],1.15)
    def test_healing_budget_uses_fixed_condition_without_deriving_it_from_recipient_state(self):
        for op,module,skills,gate in FORMS:
            high=evaluate(op,1,guardian_healing_target_hp_ratio=.8)
            preview={'recipients':[{'id':'friend','max_hp':10000,'hp':1000}], 'events':[{'at_seconds':1,'recipient':'friend','kind':'heal','source':'healing_0'}]}
            scenario={'operator':op,'skill':1,'base_attack':1000,'module_id':module,'module_level':3,FIELD:.8}
            budget=healing_budget(scenario,preview)
            self.assertAlmostEqual(budget['rows'][0]['amount_reference'],high['components'][0]['per_hit'])
            scenario[FIELD]=.4;low=healing_budget(scenario,preview)
            self.assertAlmostEqual(low['rows'][0]['amount_reference'],budget['rows'][0]['amount_reference']*1.15)
            self.assertFalse(low['actual_acquisition_verified'])
    def test_shu_multi_recipient_reference_has_single_source_factor(self):
        high=evaluate('char_2025_shu',2,guardian_healing_target_hp_ratio=.8,healing_targets=2)
        low=evaluate('char_2025_shu',2,guardian_healing_target_hp_ratio=.4,healing_targets=2)
        self.assertEqual(high['components'][0]['hits'],low['components'][0]['hits'])
        self.assertAlmostEqual(low['components'][0]['total'],high['components'][0]['total']*1.15)
    def test_report_explains_own_comparison_and_unknown_trajectory(self):
        for op,module,skills,gate in FORMS:
            scenario={'operator':op,'skill':2,'module_id':module,'module_level':3}
            result=calculate_damage(scenario);block=next(s for s in build_report(scenario,result)['sections'] if s['id']=='guardian_module_healing')
            metrics={m['key']:m['value'] for m in block['metrics']}
            self.assertIsNone(metrics['recipient_ratio']);self.assertIsNone(metrics['healing_factor'])
            self.assertEqual(metrics['comparison'],'LT' if op=='char_196_sunbr' else 'LE')
            self.assertEqual(metrics['actual_hp_trajectory'],'未知');self.assertEqual(metrics['regen_factor'],1)
if __name__=='__main__':unittest.main()
