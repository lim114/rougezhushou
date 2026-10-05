"""Offline spawn branches are alternatives, never a sampled current enemy."""
import copy
import unittest
from unittest.mock import patch

from rouge.catalog import stage_previews
from rouge.catalog import operator_attributes
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.relics import mechanics

COFFEE='rogue_6_relic_fight_25'
PICTURE='rogue_6_relic_legacy_84'
FIRE='rogue_6_relic_cargo_11'
DRAGON='rogue_6_start_3'
VIP='rogue_6_relic_fight_26'


def target(stage='ro6_n_1_2',enemy='enemy_1093_ccsbr'):
    e=next(e for e in stage_previews()[stage]['possible_enemies'] if e['id']==enemy) if enemy else stage_previews()[stage]['possible_enemies'][0]
    return {'stage_id':stage,'enemy_id':e['id'],'level':e['level']}


def scenario(**extra):
    return {'operator':'mechanist','skill':3,'target_enemy':target(),
        'run_config':{'difficulty':{'value':4},'zone':{'id':'zone_1'}},**extra}


def coffee(**extra):return calculate_damage(scenario(relic_ids=[COFFEE],**extra))


def allied_stat_reference(values):
    # Independent native writer values for raw char_attribute_mul: HP3631*1.3
    # ->4720; ATK573*1.3->745. Feed that basis to the unchanged skill path.
    attributes = operator_attributes('mechanist')
    attributes.update(hp=4720, attack=745)
    with patch('rouge.catalog.operator_attributes', return_value=attributes):
        return calculate_damage(values)


class SpawnHp033Tests(unittest.TestCase):
    def test_derived_rule_retains_the_exact_probability_and_independent_factor(self):
        rule=next(e for e in mechanics()['relics'][COFFEE]['effects'] if e['kind']=='enemy_spawn_hp_branch')
        self.assertEqual(rule['probability'],.03)
        self.assertEqual(rule['value'],2)
        self.assertEqual(rule['group'],'rogue_6_enemy_prob_max_hp')

    def test_single_coffee_reports_both_variants_after_environment(self):
        base=calculate_damage(scenario())['run_resolution']['enemy']['stats']['maxHp']
        r=coffee();enemy=r['run_resolution']['enemy'];prediction=enemy['spawn_hp']
        self.assertEqual(enemy['stats']['maxHp'],base)
        self.assertEqual(prediction['untriggered_max_hp'],base)
        self.assertEqual(prediction['triggered_max_hp'],base*2)
        self.assertEqual(prediction['single_item_triggered_max_hp'],base*2)
        self.assertIsNone(prediction['current_variant'])
        self.assertEqual(prediction['excluded_hp_sources'],[])
        self.assertTrue(r['relic_resolution']['complete'])

    def test_probabilities_are_one_enemy_marginals_not_an_averaged_actual_hp(self):
        enemy=coffee()['run_resolution']['enemy'];p=enemy['spawn_hp']
        self.assertEqual(p['probabilities'],{'untriggered':.97,'triggered':.03})
        self.assertNotIn('expected_hp',p)
        self.assertNotEqual(enemy['stats']['maxHp'],p['untriggered_max_hp']*1.03)
        self.assertIn('不推定各敌人之间独立',format_estimate(coffee()))

    def test_stage_and_difficulty_modifiers_precede_the_single_item_branch(self):
        for stage in ('ro6_n_1_2','ro6_e_1_2'):
            for grade in (0,3,4,5,10,15):
                with self.subTest(stage=stage,grade=grade):
                    s=scenario(target_enemy=target(stage),run_config={'difficulty':{'value':grade},'zone':{'id':'zone_2'}})
                    reference=calculate_damage(s)['run_resolution']['enemy']['stats']
                    r=calculate_damage({**s,'relic_ids':[COFFEE]})['run_resolution']['enemy']
                    self.assertEqual(r['stats'],reference)
                    self.assertEqual(r['spawn_hp']['triggered_max_hp'],reference['maxHp']*2)

    def test_hp_branch_does_not_rescale_damage_sp_or_cycle(self):
        for mode in ('frames','continuous'):
            s=scenario(timing_mode=mode);r=calculate_damage({**s,'relic_ids':[COFFEE]})
            reference=allied_stat_reference(s)
            self.assertEqual(r['estimate']['base_stats'],reference['estimate']['base_stats'])
            self.assertEqual(r['estimate']['skill'],reference['estimate']['skill'])
            self.assertEqual(r['components'],reference['components'])

    def test_no_target_does_not_invent_an_enemy_or_hide_the_allied_stats(self):
        r=coffee(target_enemy=None)
        reference=allied_stat_reference(scenario(target_enemy=None))
        self.assertNotIn('enemy',r['run_resolution'])
        self.assertEqual(r['estimate']['base_stats'],reference['estimate']['base_stats'])
        self.assertIn('target_enemy',r['relic_resolution']['records'][0]['missing_conditions'])
        self.assertNotIn('猎犬咖啡出生生命分支',format_estimate(r))

    def test_missing_difficulty_is_still_disclosed(self):
        r=coffee(run_config={})
        self.assertIn('spawn_hp',r['run_resolution']['enemy'])
        self.assertTrue(any('保密等级尚未确认' in p for p in r['run_resolution']['pending']))
        self.assertFalse(r['estimate']['complete'])

    def test_recalculation_and_duplicate_ids_never_sample_or_mutate_state(self):
        s=scenario(relic_ids=[COFFEE,COFFEE]);before=copy.deepcopy(s)
        one=calculate_damage(s);two=calculate_damage(s)
        self.assertEqual(one['run_resolution']['enemy']['spawn_hp'],two['run_resolution']['enemy']['spawn_hp'])
        self.assertEqual(one['run_resolution']['enemy']['spawn_hp'],coffee()['run_resolution']['enemy']['spawn_hp'])
        self.assertEqual(s,before)
        self.assertEqual(len(one['relic_resolution']['enemy_effects']['spawn_hp_rules']),1)

    def test_unknown_current_branch_cannot_be_fabricated_by_an_input(self):
        r=coffee(enemy_spawn_variant='triggered',relic_context={'coffee_triggered':1})
        self.assertIsNone(r['run_resolution']['enemy']['spawn_hp']['current_variant'])

    def test_native_final_scaler_composes_with_coffee_without_sampling_current_branch(self):
        base=calculate_damage(scenario())['run_resolution']['enemy']['stats']['maxHp']
        r=calculate_damage(scenario(relic_ids=[COFFEE,PICTURE]));enemy=r['run_resolution']['enemy'];p=enemy['spawn_hp']
        self.assertAlmostEqual(enemy['stats']['maxHp'],base*.95)
        self.assertEqual(p['single_item_triggered_max_hp'],base*2)
        self.assertAlmostEqual(p['triggered_max_hp'],base*.95*2)
        self.assertEqual(p['excluded_hp_sources'],[])
        self.assertIsNone(p['current_variant'])
        self.assertTrue(r['relic_resolution']['complete'])

    def test_unknown_defense_group_does_not_disable_proven_independent_hp_instances(self):
        r=calculate_damage(scenario(relic_ids=[COFFEE,PICTURE,'rogue_6_relic_legacy_85']))
        p=r['run_resolution']['enemy']['spawn_hp']
        base=calculate_damage(scenario())['run_resolution']['enemy']['stats']['maxHp']
        self.assertAlmostEqual(p['triggered_max_hp'],base*.95*.9*2)
        self.assertEqual(p['excluded_hp_sources'],[])
        self.assertFalse(r['relic_resolution']['complete'])
        self.assertTrue(any('enemy_def_down' in x for x in r['warnings']))

    def test_native_resident_final_scaler_composes_with_both_random_hp_alternatives(self):
        s=scenario(target_enemy=target('ro6_t_8',None),relic_context={'fire_rod_stacks':0})
        base=calculate_damage(s)['run_resolution']['enemy']['stats']['maxHp']
        alone=calculate_damage({**s,'relic_ids':[FIRE]})['run_resolution']['enemy']['stats']['maxHp']
        self.assertAlmostEqual(alone,base*.6)
        r=calculate_damage({**s,'relic_ids':[COFFEE,FIRE]});p=r['run_resolution']['enemy']['spawn_hp']
        self.assertAlmostEqual(r['run_resolution']['enemy']['stats']['maxHp'],base*.6)
        self.assertAlmostEqual(p['triggered_max_hp'],base*.6*2)
        self.assertEqual(p['excluded_hp_sources'],[])
        self.assertEqual(r['relic_resolution']['enemy_effects']['hp_composition_pending'],[])
        self.assertIsNone(p['current_variant'])

    def test_inapplicable_resident_modifier_does_not_block_the_random_branch(self):
        r=calculate_damage(scenario(relic_ids=[COFFEE,FIRE],relic_context={'fire_rod_stacks':0}))
        self.assertEqual(r['run_resolution']['enemy']['spawn_hp']['excluded_hp_sources'],[])
        self.assertIsNotNone(r['run_resolution']['enemy']['spawn_hp']['triggered_max_hp'])

    def test_elite_only_hp_modifier_is_scoped_to_the_selected_enemy(self):
        normal=calculate_damage(scenario(relic_ids=[COFFEE,VIP]))['run_resolution']['enemy']
        self.assertEqual(normal['level_type'],'NORMAL')
        self.assertEqual(normal['spawn_hp']['excluded_hp_sources'],[])
        elite=calculate_damage(scenario(relic_ids=[COFFEE,VIP],target_enemy=target(enemy='enemy_2137_shsdgo')))['run_resolution']['enemy']
        self.assertEqual(elite['level_type'],'ELITE')
        elite_base=calculate_damage(scenario(target_enemy=target(enemy='enemy_2137_shsdgo')))['run_resolution']['enemy']['stats']['maxHp']
        self.assertEqual(elite['spawn_hp']['excluded_hp_sources'],[])
        self.assertAlmostEqual(elite['spawn_hp']['untriggered_max_hp'],elite_base*1.1)
        self.assertAlmostEqual(elite['spawn_hp']['triggered_max_hp'],elite_base*1.1*2)

    def test_known_expired_hp_condition_does_not_block_but_missing_condition_does(self):
        for value,expected in ((3,[]),(0,[]),(None,[DRAGON])):
            s=scenario(relic_ids=[COFFEE,DRAGON],relic_context={} if value is None else {'entered_zone_count':value})
            p=calculate_damage(s)['run_resolution']['enemy']['spawn_hp']
            self.assertEqual(p['excluded_hp_sources'],expected)
            self.assertEqual(p['triggered_max_hp'] is None,bool(expected))

    def test_no_random_hp_section_for_other_relics_or_an_unselected_target(self):
        for r in (calculate_damage(scenario()),calculate_damage(scenario(relic_ids=[PICTURE])),coffee(target_enemy=None)):
            self.assertNotIn('猎犬咖啡出生生命分支',format_estimate(r))
        self.assertIn('猎犬咖啡出生生命分支',format_estimate(coffee()))

    def test_invalid_target_remains_rejected(self):
        with self.assertRaises(ValueError):coffee(target_enemy=target()|{'enemy_id':'not-a-stage-enemy'})


if __name__=='__main__':unittest.main()
