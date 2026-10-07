from tests.offline_scope_retirement import historical_combat_test
import unittest
from rouge.damage import calculate_damage

class RelicMechanismTests(unittest.TestCase):
    def test_bound_foam_redeploy_and_snack_use_independent_cultivation(self):
        base=calculate_damage({'operator':'mechanist','skill':3})['estimate']['base_stats']
        foam=calculate_damage({'operator':'mechanist','skill':3,'char_buff_ids':['rogue_6_from_relic_12']*2})
        self.assertEqual(foam['estimate']['base_stats']['attack_speed'],50)
        self.assertEqual(foam['estimate']['base_stats']['attack'],1261) # round-even(573*2.2)
        specialist={'operator':'char_1029_yato2','skill':2}
        redeploy=calculate_damage({**specialist,'char_buff_ids':['rogue_6_from_relic_7']})
        self.assertEqual(redeploy['estimate']['base_stats']['redeploy_seconds'],
                         calculate_damage(specialist)['estimate']['base_stats']['redeploy_seconds']*.5)
        snack=calculate_damage({'operator':'mechanist','skill':3,'char_buff_ids':['rogue_6_from_relic_13']})
        self.assertEqual(snack['estimate']['skill']['recharge_seconds'],28)
        self.assertTrue(any('自动开启' in n for n in snack['estimate']['notes']))
        with self.assertRaisesRegex(ValueError,'未知干员定向强化'):
            calculate_damage({'operator':'mechanist','skill':3,'char_buff_ids':['invalid']})

    def test_native_periodic_sp_has_a_deployment_clock_without_a_guessed_phase(self):
        r=calculate_damage({'operator':'mechanist','skill':1,'relic_ids':['rogue_6_relic_legacy_97']})
        for key in ('initial_seconds','recharge_seconds','cycle_seconds','cycle_dps','cycle_damage'):
            self.assertIsNotNone(r['estimate']['skill'][key],key)
            self.assertGreater(r['estimate']['skill'][key],0,key)
        self.assertNotIn('cycle_seconds_range',r['estimate']['skill'])
        self.assertFalse(r['relic_resolution']['timing_unresolved'])
        self.assertGreater(r['estimate']['skill']['total_damage'],0)
        natural=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_97']})
        self.assertIsNotNone(natural['estimate']['skill']['cycle_seconds'])

    def test_bound_forbidden_skill_cannot_show_active_skill_forecast(self):
        with self.assertRaisesRegex(ValueError,'指中狼.*禁止开启技能'):
            calculate_damage({'operator':'char_151_myrtle','skill':1,'char_buff_ids':['rogue_6_from_relic_10']})

    def test_bound_sniper_penetration_uses_own_physical_hits_not_global_enemy_defense(self):
        scenario={'operator':'char_133_mm','skill':1,'enemy_defense':100,'base_attack':1000}
        base=calculate_damage(scenario)
        buff=calculate_damage({**scenario,'char_buff_ids':['rogue_6_from_relic_5']})
        self.assertEqual(buff['components'][0]['per_hit']-base['components'][0]['per_hit'],50)
        self.assertEqual(buff['relic_resolution']['enemy_effects']['defense_factor'],1)
        with self.assertRaisesRegex(ValueError,'职业不符'):
            calculate_damage({'operator':'mechanist','skill':3,'char_buff_ids':['rogue_6_from_relic_5']})

    def test_confirmed_target_buff_survives_item_consumption_and_does_not_apply_from_holding(self):
        held=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_assign_9']})
        self.assertEqual(held['estimate']['base_stats']['attack_speed'],100)
        self.assertFalse(held['relic_resolution']['complete'])
        bound=calculate_damage({'operator':'mechanist','skill':3,'char_buff_ids':['rogue_6_from_relic_9']})
        self.assertEqual(bound['estimate']['base_stats']['attack_speed'],150)
        self.assertEqual(bound['relic_resolution']['records'][0]['recipient'],'mechanist')
        other=calculate_damage({'operator':'kaltsit','skill':2})
        self.assertEqual(other['estimate']['base_stats']['attack_speed'],100)

    def test_one_second_attack_buff_is_not_applied_to_every_shot_or_late_window(self):
        s={'operator':'mechanist','skill':3,'base_attack':1000,'relic_ids':['rogue_6_relic_legacy_62'],
            'timing':{'windup_frames':6,'recovery_frames':9}}
        r=calculate_damage(s)
        #Game blackboard: ATK+280%,damage multiplier2.6. One bonus is base*100%,not skillATK*100%.
        self.assertEqual(r['estimate']['skill']['total_damage'],121160) #first12480 +eleven9880
        first=calculate_damage({**s,'window_seconds':.5})
        self.assertEqual(first['total_damage'],0)  #release.2 +fixed delay.8 =1s
        landed=calculate_damage({**s,'window_seconds':31/30})
        # Existing snapshot reference takes the buff at release, before expiry,
        # even though this impact happens after its one-second window.
        self.assertEqual(landed['total_damage'],12480)
        late=calculate_damage({**s,'timing':{**s['timing'],'projectile_travel_seconds':100}})
        self.assertEqual(late['estimate']['skill']['total_damage'],121160)
        self.assertEqual(late['estimate']['skill']['cycle_damage'],0)
        idle=calculate_damage({**s,'timing':{**s['timing'],'target_windows':[[2,100]]}})
        self.assertEqual(idle['estimate']['skill']['total_damage'],108680) #delay2s leaves eleven unboosted shots

    def test_token_only_stats_and_cost_do_not_leak_into_summoner(self):
        base=calculate_damage({'operator':'char_110_deepcl','skill':1})
        r=calculate_damage({'operator':'char_110_deepcl','skill':1,'relic_ids':['rogue_6_relic_legacy_134']})
        self.assertEqual(r['estimate']['base_stats'],base['estimate']['base_stats'])
        token=r['relic_token_stats'][0]
        self.assertEqual(token['attack'],601) # round-even(462*1.3) at rune writer
        self.assertEqual(token['hp'],2621) # round-even(2016*1.3)
        self.assertEqual(token['deployment_cost'],0)
        self.assertTrue(token['free_deployment_slot'])

    def test_parts_bonus_and_emergency_identity_are_independent_conditions(self):
        s={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_cargo_2','rogue_6_relic_cargo_10'],
            'relic_context':{'parts_count':3}}
        base=calculate_damage({'operator':'mechanist','skill':3})['estimate']['base_stats']['attack']
        unknown=calculate_damage(s)
        self.assertAlmostEqual(unknown['estimate']['base_stats']['attack'],base*1.24)
        self.assertTrue(any('emergency_hire' in w for w in unknown['warnings']))
        emergency=calculate_damage({**s,'recruitment_kind':'emergency_hire'})
        self.assertAlmostEqual(emergency['estimate']['base_stats']['attack'],base*1.64)

    def test_pioneer_start_dp_is_added_once_and_hidden_for_other_professions(self):
        r=calculate_damage({'operator':'char_151_myrtle','skill':1,'relic_ids':['rogue_6_relic_book_1']})
        dp=next(s for s in r['report']['sections'] if s['id']=='dp')
        values={m['key']:m['value'] for m in dp['metrics']}
        self.assertEqual(values['per_cast'],17)
        self.assertEqual(values['immediate'],3)
        other=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_book_1']})
        self.assertFalse(any(s['id']=='dp' for s in other['report']['sections']))

    def test_gold_threshold_missing_condition_and_duplicate_relic(self):
        scenario={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_60']}
        missing=calculate_damage(scenario)
        self.assertEqual(missing['relic_resolution']['records'][0]['missing_conditions'],['gold'])
        for gold,speed in ((24,128),(25,135)):
            r=calculate_damage({**scenario,'relic_context':{'gold':gold}})
            self.assertEqual(r['estimate']['base_stats']['attack_speed'],speed)
        duplicate=calculate_damage({**scenario,'relic_ids':scenario['relic_ids']*2,'relic_context':{'gold':25}})
        self.assertEqual(duplicate['estimate']['base_stats']['attack_speed'],135)

    @historical_combat_test
    def test_hp_curve_and_unverified_stacking_remain_explicit(self):
        r=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_102'],
            'relic_context':{'current_hp_ratio':.65}})
        self.assertAlmostEqual(r['estimate']['base_stats']['attack_speed'],150)
        combined=calculate_damage({'operator':'char_196_sunbr','skill':2,
            'relic_ids':['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82']})
        self.assertTrue(any('叠加规则' in w for w in combined['warnings']))
        self.assertFalse(combined['relic_resolution']['complete'])

    def test_deployment_cost_is_derived_from_cultivation_not_free_input(self):
        r=calculate_damage({'operator':'mechanist','skill':3,'potential':6,
            'relic_ids':['rogue_6_relic_final_2']})
        rows=next(s for s in r['report']['sections'] if s['id']=='relic_deployment')['metrics']
        self.assertEqual(next(m['value'] for m in rows if m['key']=='cost'),24)

    def test_ammo_speed_bonus_expires_during_idle_before_any_attack(self):
        s={'operator':'char_1041_angel2','skill':3,
            'timing':{'windup_frames':6,'recovery_frames':9,'target_windows':[[20,100]]}}
        base=calculate_damage(s)
        boosted=calculate_damage({**s,'relic_ids':['rogue_6_relic_legacy_138']})
        self.assertEqual(boosted['estimate']['skill']['duration_seconds'],base['estimate']['skill']['duration_seconds'])
        active=calculate_damage({**s,'timing':{'windup_frames':6,'recovery_frames':9},
            'relic_ids':['rogue_6_relic_legacy_138']})
        unboosted=calculate_damage({**s,'timing':{'windup_frames':6,'recovery_frames':9}})
        self.assertLess(active['estimate']['skill']['cycle_seconds'],unboosted['estimate']['skill']['cycle_seconds'])
        self.assertEqual(active['estimate']['skill']['hit_counts']['技能攻击'],50)

    def test_elemental_buildup_and_hp_damage_are_two_distinct_modifiers(self):
        r=calculate_damage({'operator':'char_1042_phatm2','skill':1,'base_attack':1000,
            'timing_mode':'continuous','relic_ids':['rogue_6_relic_fight_21']})
        buildup=sum(c['total'] for c in r['components'] if c['damage_type']=='buildup')
        # Two300 source references*1.75. The S1 buff parameter1.8 is not
        # an established first-hit multiplier; neither creates HP damage.
        self.assertEqual(buildup,1050)
        self.assertEqual(r['known_damage_subtotals']['total_damage'],3000)
        self.assertIsNone(r['total_damage'])

    def test_regeneration_relic_is_separate_from_direct_healing(self):
        r=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_22']})
        self.assertEqual(r['estimate']['skill']['total_healing'],0)
        block=next(s for s in r['report']['sections'] if s['id']=='relic_regeneration')
        self.assertEqual(next(m['value'] for m in block['metrics'] if m['key']=='rate'),3)

    def test_attack_sp_relic_is_an_attack_event_not_natural_recovery(self):
        r=calculate_damage({'operator':'char_4182_oblvns','skill':3,'relic_ids':['rogue_6_relic_legacy_67'],
            'timing':{'windup_frames':6,'recovery_frames':9}})
        self.assertEqual(r['estimate']['skill']['initial_seconds'],77/30)  #AS112 =>35f; releases6,41,76 give9SP
        idle=calculate_damage({'operator':'char_4182_oblvns','skill':3,'relic_ids':['rogue_6_relic_legacy_67'],
            'timing':{'windup_frames':6,'recovery_frames':9,'initial_target_windows':[]}})
        #Her explicit permanent-attack trait keeps releasing notes without a target.
        self.assertEqual(idle['estimate']['skill']['initial_seconds'],77/30)

    def test_global_enemy_defense_reduction_is_applied_before_per_hit_mitigation(self):
        r=calculate_damage({'operator':'char_133_mm','skill':1,'base_attack':1000,
            'enemy_defense':1000,'timing_mode':'continuous','relic_ids':['rogue_6_relic_legacy_84']})
        self.assertEqual(r['estimate']['skill']['total_damage'],1240)  #1070*2 -900

    def test_received_healing_multiplier_is_not_attack_or_direct_damage(self):
        r=calculate_damage({'operator':'char_196_sunbr','skill':2,'base_attack':1000,
            'timing_mode':'continuous','relic_ids':['rogue_6_relic_legacy_81']})
        self.assertEqual(r['estimate']['skill']['total_healing'],17280)
        self.assertEqual(r['total_damage'],0)
        self.assertEqual(r['estimate']['base_stats']['attack'],1000)

    def test_skill_cost_reduction_obeys_profession_and_hand_subprofession(self):
        r=calculate_damage({'operator':'char_206_gnosis','skill':3,'relic_ids':['rogue_6_relic_legacy_80']})['estimate']['skill']
        self.assertEqual(r['recharge_seconds'],24)
        hand=calculate_damage({'operator':'char_4087_ines','skill':2,'relic_ids':['rogue_6_relic_hand_1']})
        self.assertIn('rogue_6_relic_hand_1',hand['inapplicable_relics'])  #agent is not pioneer/charger/counsellor

    def test_end_sp_changes_recharge_but_not_deployment_initial_sp(self):
        base=calculate_damage({'operator':'mechanist','skill':3})['estimate']['skill']
        r=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_fight_28']})['estimate']['skill']
        self.assertEqual(r['initial_seconds'],base['initial_seconds'])
        self.assertEqual(r['recharge_seconds'],31)
        self.assertEqual(r['cycle_seconds'],71)

    def test_initial_sp_reduces_initial_delay_without_changing_later_cycles(self):
        base=calculate_damage({'operator':'kaltsit','skill':1})['estimate']['skill']
        r=calculate_damage({'operator':'kaltsit','skill':1,'relic_ids':['rogue_6_relic_legacy_98']})['estimate']['skill']
        self.assertEqual(r['initial_seconds'],0)  #35 cost,28 base initial +12 >=35
        self.assertEqual(r['cycle_seconds'],base['cycle_seconds'])

    def test_specialist_redeploy_scaler_does_not_affect_other_professions(self):
        r=calculate_damage({'operator':'char_1029_yato2','skill':2,'relic_ids':['rogue_6_relic_legacy_77']})
        self.assertEqual(r['estimate']['base_stats']['redeploy_seconds'],12) # round-even(18*.65)
        other=calculate_damage({'operator':'kaltsit','skill':1,'relic_ids':['rogue_6_relic_legacy_77']})
        self.assertEqual(other['estimate']['base_stats']['redeploy_seconds'],70)
        self.assertEqual(other['inapplicable_relics'],['rogue_6_relic_legacy_77'])

if __name__=='__main__':unittest.main()
