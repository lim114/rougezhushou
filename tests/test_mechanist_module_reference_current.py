import copy
import json
import unittest
from pathlib import Path

from rouge.calibration import packet_worksheet
from rouge.charge_timeline import compare_charge_windows
from rouge.damage import calculate_damage
from rouge.damage_budget import damage_sources
from rouge.mechanist_module_reference import FLAG, BLOCKER, qualification, rule
from rouge.reporting import format_report
from rouge.shield_timeline import compare_shield_windows


def scenario(skill=3, stage=2, **extra):
    return {'operator':'mechanist','skill':skill,'module_id':'uniequip_002_mcnist',
            'module_level':stage,FLAG:True,'relic_context':{BLOCKER:'own_token'},**extra}


def packets(result):
    return {p['key']:p for p in result['mechanist_module_reference']['packets']}


class MechanistModuleReferenceTests(unittest.TestCase):
    def test_default_off_and_inactive_inputs_preserve_existing_results(self):
        for skill in (1,2,3):
            base=scenario(skill);base.pop(FLAG)
            control=calculate_damage(base)
            self.assertEqual(control,calculate_damage({**base,FLAG:False}))
            self.assertNotIn('mechanist_module_reference',control)
        for extra in ({'level':59},{'map_tag':'rogue_5'},{'module_id':None,'module_level':0}):
            source=scenario(relic_context={BLOCKER:99},**extra)
            r=calculate_damage(source)
            self.assertNotIn('mechanist_module_reference',r)

    def test_current_native_stage_and_zero_based_skill_index_gates(self):
        for stage in (1,2,3):
            for skill in (1,2,3):
                with self.subTest(stage=stage,skill=skill):
                    q=qualification(scenario(skill,stage))
                    self.assertEqual(q['native_skill_index'],skill-1)
                    self.assertEqual(q['qualified'],stage>1 or skill==1)
                    r=calculate_damage(scenario(skill,stage))
                    self.assertEqual('mechanist_module_reference' in r,q['qualified'])
        for extra in ({'elite':1,'level':80},{'level':59},{'map_tag':'rogue_5'}):
            self.assertFalse(qualification(scenario(**extra))['qualified'])
        self.assertTrue(qualification(scenario(level=60))['qualified'])
        self.assertEqual(rule()['stages']['1']['skill_indices'],[0])

    def test_self_and_own_token_share_one_factor_other_and_none_do_not(self):
        results={b:calculate_damage(scenario(relic_context={BLOCKER:b})) for b in ('self','own_token','other','none')}
        for key in ('normal','bombard','charge'):
            self.assertEqual(packets(results['self'])[key]['per_hit_reference'],packets(results['own_token'])[key]['per_hit_reference'])
            self.assertEqual(packets(results['other'])[key]['per_hit_reference'],packets(results['none'])[key]['per_hit_reference'])
            self.assertEqual(packets(results['self'])[key]['module_attack_scale'],1.5)
            self.assertEqual(packets(results['none'])[key]['module_attack_scale'],1)
        self.assertEqual(len(packets(results['self'])),3)

    def test_scale_is_before_armor_and_does_not_change_panel_attack(self):
        s=scenario(base_attack=1000,enemy_defense=2000,enemy_resistance=50,charge_count=2,window_seconds=10)
        r=calculate_damage(s);p=packets(r)
        # (1000 * 3.8 * 3 * 1.5) - 2000; scaling after armor would differ by1000.
        self.assertAlmostEqual(p['charge']['per_hit_reference'],15100)
        self.assertNotEqual(p['charge']['per_hit_reference'],(11400-2000)*1.5)
        self.assertAlmostEqual(p['bombard']['per_hit_reference'],1000*3.8*2.6*1.5*.5)
        unselected=calculate_damage({**s,FLAG:False})
        self.assertEqual(r['attack'],unselected['attack'])
        self.assertEqual(r['estimate']['base_stats'],unselected['estimate']['base_stats'])
        self.assertEqual(r['estimate']['skill']['skill_attack'],unselected['estimate']['skill']['skill_attack'])

    def test_stable_attack_bonus_scale_and_damage_taken_are_applied_once(self):
        effects=[{'kind':'attack_pct','value':.25},
                 {'kind':'damage_taken','damage_type':'physical','value':.2},
                 {'kind':'damage_taken','damage_type':'magic','value':.3}]
        r=calculate_damage(scenario(base_attack=1000,enemy_defense=1000,effects=effects))
        p=packets(r)
        self.assertAlmostEqual(p['charge']['per_hit_reference'],(1000*4.05*3*1.5-1000)*1.2)
        self.assertAlmostEqual(p['bombard']['per_hit_reference'],1000*4.05*2.6*1.5*1.3)
        self.assertAlmostEqual(p['normal']['per_hit_reference'],(1250*1.5-1000)*1.2)
        for packet in p.values():self.assertEqual(packet['source_entity'],'mechanist')

    def test_physical_floor_uses_scaled_packet(self):
        p=packets(calculate_damage(scenario(base_attack=1000,enemy_defense=100000)))
        self.assertAlmostEqual(p['charge']['per_hit_reference'],1000*3.8*3*1.5*.05)
        self.assertAlmostEqual(p['normal']['per_hit_reference'],1000*1.5*.05)

    def test_unknown_blocker_keeps_candidates_and_actual_totals_unknown(self):
        for context in ({},{BLOCKER:'unknown'},{'blocked_enemies':99,'token_conditions':{'token_10069_mcnist_mcgraf':{'blocked_enemies':99}}}):
            r=calculate_damage(scenario(relic_context=context,charge_count=2))
            self.assertIsNone(r['total_damage'])
            for p in packets(r).values():
                self.assertIsNone(p['module_attack_scale']);self.assertIsNone(p['per_hit_reference'])
                self.assertEqual(len(p['blocker_unknown_candidates']),2)
            self.assertIsNone(r['mechanist_module_reference']['conditional_count_damage_reference'])
            self.assertEqual(damage_sources(r),[])
            self.assertIn('满足阻挡条件的候选',format_report(r))
        r=calculate_damage(scenario(relic_context={},window_seconds=0,charge_count=0))
        self.assertEqual(r['mechanist_module_reference']['modeled_window_damage_reference'],0)

    def test_declared_blocker_strict_types_and_scope(self):
        for value in (True,1,{},[],'token','SELF','',.5):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError,'人数不能代替目标身份'):
                    calculate_damage(scenario(relic_context={BLOCKER:value}))
        for value in ('true',1,None,[]):
            with self.assertRaisesRegex(ValueError,'布尔值'):calculate_damage(scenario(**{FLAG:value}))
        foreign=calculate_damage({'operator':'silverash','skill':3,FLAG:'unconsumed','relic_context':{BLOCKER:[]}})
        self.assertNotIn('mechanist_module_reference',foreign)

    def test_skill1_and_shield_single_packets_keep_independent_counts(self):
        r1=calculate_damage(scenario(1,1));p1=packets(r1)['skill']
        self.assertEqual(p1['modeled_or_declared_count'],r1['hits'])
        self.assertEqual(r1['per_hit'],p1['per_hit_reference'])
        r2=calculate_damage(scenario(2,3,shield_break_count=23));p2=packets(r2)['skill']
        self.assertEqual(p2['modeled_or_declared_count'],23)
        self.assertEqual(r2['shield_break_reference']['hits_requested'],23)
        self.assertAlmostEqual(p2['conditional_count_damage_reference'],23*p2['per_hit_reference'])
        self.assertIsNone(r2['mechanist_module_reference']['modeled_window_damage_reference'])
        self.assertIsNone(r2['shield_break_reference']['actual_end_seconds'])
        self.assertFalse(r2['shield_break_reference']['events_scheduled'])

    def test_source_preconditions_and_real_clock_are_not_promoted(self):
        r=calculate_damage(scenario(charge_count=2))
        ref=r['mechanist_module_reference']
        self.assertEqual(ref['condition_source'],'manual_offline_preview')
        for key in ('actual_blocker','actual_source_valid','actual_collision_seconds','full_cast_damage','actual_window_damage','cycle_damage'):
            self.assertIsNone(ref[key])
        self.assertFalse(ref['runtime_binding_verified']);self.assertFalse(ref['current_hotfix_equivalence_verified'])
        for key in ('total_damage','phase_damage','cycle_damage','cycle_dps','window_damage','window_dps'):
            self.assertIsNone(r['estimate']['skill'][key])
        self.assertFalse(r['complete']);self.assertFalse(r['estimate']['complete'])
        self.assertNotIn('known_damage_subtotals',r)
        self.assertIsNone(r['charge_reference']['collision_times_seconds'])
        self.assertIn('完整实际技能伤害',format_report(r))

    def test_explicit_target_lifetime_zero_excludes_counts_but_owner_empty_range_is_independent(self):
        for skill in (1,2,3):
            r=calculate_damage(scenario(skill,3,shield_break_count=23,charge_count=2,
                                      timing={'target_disappears_seconds':0}))
            for p in packets(r).values():
                if p['key']=='normal':continue
                self.assertEqual(p['modeled_or_declared_count'],0)
                self.assertEqual(p['conditional_count_damage_reference'],0)
            self.assertIsNone(r['total_damage'])
        # An empty owner's acquisition range does not rule out a separate explosion.
        independent=calculate_damage(scenario(2,3,shield_break_count=23,timing={'target_windows':[]}))
        self.assertEqual(packets(independent)['skill']['modeled_or_declared_count'],23)
        self.assertIsNone(independent['mechanist_module_reference']['modeled_window_damage_reference'])

    def test_charge_window_and_existing_budget_consume_selected_packets(self):
        s=scenario(window_seconds=10);r=calculate_damage(s)
        control=packets(r)
        projected=compare_charge_windows(s,[1,5,5,10],[5,10])
        self.assertEqual([w['charge_hits'] for w in projected['windows']],[1,3])
        self.assertAlmostEqual(projected['per_hit_damage_reference'],control['charge']['per_hit_reference'])
        self.assertAlmostEqual(projected['windows'][1]['charge_damage'],3*control['charge']['per_hit_reference'])
        self.assertIsNone(projected['full_cast_damage'])
        self.assertEqual([x['per_hit'] for x in damage_sources(r)],
                         [control['bombard']['per_hit_reference'],control['charge']['per_hit_reference']])
        with self.assertRaisesRegex(ValueError,'阻挡身份'):
            compare_charge_windows(scenario(relic_context={}),[1],[5])

    def test_shield_window_uses_selected_explosion_but_does_not_place_ordinary(self):
        s=scenario(2,3);r=calculate_damage(s)
        projected=compare_shield_windows(s,{'events':[{'source':'owner','break_seconds':1,'hit_seconds':2},
                    {'source':'structure','break_seconds':1,'hit_seconds':2}],'windows_seconds':[2,3]})
        self.assertEqual(projected['rows'][0]['explosion_damage_reference'],0)
        self.assertAlmostEqual(projected['rows'][1]['explosion_damage_reference'],2*packets(r)['skill']['per_hit_reference'])
        self.assertIsNone(projected['rows'][1]['ordinary_damage_reference'])
        self.assertIsNone(projected['full_cast_damage'])
        with self.assertRaisesRegex(ValueError,'阻挡身份'):
            compare_shield_windows(scenario(2,3,relic_context={}),{'events':[],'windows_seconds':[5]})

    def test_packet_worksheet_displays_selected_scale_without_changing_input(self):
        for skill in (1,2,3):
            s=scenario(skill,3,enemy_defense=777,enemy_resistance=30);before=copy.deepcopy(s)
            worksheet=packet_worksheet(s);r=calculate_damage(s)
            expected=[p for p in packets(r).values() if p['key']!='normal']
            for row,p in zip(worksheet['rows'],expected):
                self.assertEqual(row['module_attack_scale'],1.5)
                self.assertEqual(row['pre_defense_value'],p['selected_raw_packet'])
                self.assertEqual(row['single_packet_reference'],p['per_hit_reference'])
            self.assertEqual(s,before)

    def test_public_evidence_matches_consumed_stage_rule_and_sources(self):
        proof=Path(__file__).resolve().parents[1]/'research/p2-mechanist-module-current'
        receipt=json.loads((proof/'receipt.json').read_text(encoding='utf-8'))
        self.assertTrue(receipt['physical_validation']['all_instruction_bytes_match'])
        self.assertEqual(receipt['physical_validation']['limits'],[])
        self.assertFalse(receipt['runtime_binding_verified'])
        self.assertFalse(receipt['game_dll_executed'])
        self.assertEqual(receipt['stage_skill_indices'],{'1':[0],'2':[],'3':[]})
        self.assertEqual(rule()['source']['game_dll_sha256'],receipt['physical_validation']['game_dll_sha256'])


if __name__=='__main__':unittest.main()
