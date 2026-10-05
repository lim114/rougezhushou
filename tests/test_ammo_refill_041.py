"""Evidence-backed ammunition counts through the public calculation interface."""
import copy,hashlib,json,math,unittest
from pathlib import Path
from unittest.mock import patch

from rouge.ammo_reference import refill_parameters,refill_before_empty_is_safe,refill_source
from rouge.damage import calculate_damage
from rouge.relic_events import ammunition_rounds
from rouge.relics import mechanics

BOOK='rogue_6_relic_legacy_139'
YA='rogue_6_relic_legacy_140'
ROOT=Path(__file__).resolve().parents[1]


def calc(op,skill,rid=None,**kwargs):
    return calculate_damage({'operator':op,'skill':skill,**kwargs,
        'relic_ids':[] if rid is None else [rid] if isinstance(rid,str) else rid})


def ammo_section(result):
    return next((b for b in result['report']['sections'] if b['id']=='ammo_refill_reference'),None)


def rule(maximum,ratio=.3,cost=1):
    params=refill_parameters(maximum,.3,ratio);params['attack_cost_reference']=cost
    return {'kind':'ammo_refill','relic_id':BOOK,'ammo_parameters':params}


class AmmoRefillReferenceTests(unittest.TestCase):
    def test_native_binary32_parameters_supersede_the_prior_q32_product_assumption(self):
        source=refill_source()
        proof=ROOT/source['native_parameter_proof']
        self.assertEqual(source['native_parameter_proof_sha256'],hashlib.sha256(proof.read_bytes()).hexdigest())
        self.assertEqual(source['parameter_arithmetic'],'binary32_multiply_then_round')
        self.assertFalse(source['client_frame_calibration_verified'])
        # The actual mulss product rounds10*0.3 to exactly3 before ceil;
        # at50 it remains just above15. This is neither decimal nor Q32 mul.
        self.assertEqual(refill_parameters(10,.3,.3)['refill_count'],3)
        self.assertEqual(refill_parameters(10,.3,.3)['refill_product_binary32'],3)
        self.assertEqual(refill_parameters(50,.3,.3)['refill_product_binary32'],15.000000953674316)
        self.assertEqual(refill_parameters(50,.3,.3)['refill_count'],16)
        self.assertEqual(refill_parameters(50,.3,.5)['refill_count'],25)

    def test_floor_threshold_and_ceil_refill_for_all_supported_capacities(self):
        for maximum,threshold,a,b in ((3,0,1,2),(6,1,2,3),(8,2,3,4),(10,3,3,5),(50,15,16,25)):
            for ratio,quota in ((.3,a),(.5,b)):
                with self.subTest(maximum=maximum,ratio=ratio):
                    params=refill_parameters(maximum,.3,ratio)
                    self.assertEqual((params['threshold'],params['refill_count']),(threshold,quota))
                    self.assertEqual(params['can_trigger_before_empty'],threshold>0)

    def test_unverified_ratios_are_rejected_instead_of_extrapolated(self):
        for ratio in (0,.1,.6,1,float('nan'),float('inf'),True,'0.3',None):
            self.assertIsNone(refill_parameters(10,.3,ratio))
            self.assertIsNone(refill_parameters(10,ratio,.3))

    def test_invalid_or_nonintegral_maximum_has_no_default(self):
        for maximum in (None,True,'10',0,-1,3.5,10001,10**400,float('nan'),float('inf')):
            self.assertIsNone(refill_parameters(maximum,.3,.3))

    def test_zero_ammo_is_not_revived_even_with_positive_quota(self):
        for ratio in (.3,.5):
            self.assertEqual(ammunition_rounds(3,1,{'_relic_rules':[rule(3,ratio)]}),3)
        self.assertEqual(ammunition_rounds(10,10,{'_relic_rules':[rule(10,cost=10)]},minimum_interval=10),1)

    def test_single_use_not_repeated_at_second_threshold_crossing(self):
        self.assertEqual(ammunition_rounds(10,1,{'_relic_rules':[rule(10)]},minimum_interval=1),13)
        self.assertEqual(ammunition_rounds(10,1,{'_relic_rules':[rule(10,.5)]},minimum_interval=1),15)

    def test_no_relic_preserves_existing_partial_last_attack_behavior(self):
        self.assertEqual(ammunition_rounds(6,5,{}),2)
        self.assertEqual(ammunition_rounds(50,5,{}),10)

    def test_periodic_check_boundary_requires_a_strict_surviving_window(self):
        params=refill_parameters(6,.3,.3)
        self.assertFalse(refill_before_empty_is_safe(params,1,4/30))
        self.assertTrue(refill_before_empty_is_safe(params,1,5/30))
        for interval in (None,False,True,0,-1,'1',float('nan'),float('inf'),10**400):
            self.assertFalse(refill_before_empty_is_safe(params,1,interval))
        # Five-at-a-time uses the first reachable positive band, not 15 shots.
        params=refill_parameters(50,.3,.5)
        self.assertFalse(refill_before_empty_is_safe(params,5,4/90))
        self.assertTrue(refill_before_empty_is_safe(params,5,5/90))

    def test_invalid_attack_cost_and_mismatched_preparation_are_rejected(self):
        params=refill_parameters(10,.3,.3)
        for cost in (0,-1,True,1.5,None):
            with self.assertRaises(ValueError):refill_before_empty_is_safe(params,cost,1)
        with self.assertRaises(ValueError):
            ammunition_rounds(8,1,{'_relic_rules':[rule(10)]},minimum_interval=1)
        with self.assertRaises(ValueError):
            ammunition_rounds(10,5,{'_relic_rules':[rule(10)]},minimum_interval=1)

    def test_kaltsit_total_damage_healing_duration_and_cycle_include_extra_shots(self):
        for mode in ('frames','continuous'):
            base=calc('kaltsit',2,timing_mode=mode)
            for rid,shots in ((BOOK,13),(YA,15)):
                r=calc('kaltsit',2,rid,timing_mode=mode);s=r['estimate']['skill'];b=base['estimate']['skill']
                self.assertEqual(r['hits'],shots)
                self.assertAlmostEqual(s['total_damage'],b['total_damage']*shots/10)
                self.assertAlmostEqual(s['total_healing'],b['total_healing']*shots/10)
                self.assertGreater(s['duration_seconds'],b['duration_seconds'])
                self.assertEqual(s['initial_seconds'],b['initial_seconds'])
                self.assertEqual(s['recharge_seconds'],b['recharge_seconds'])
                self.assertAlmostEqual(s['cycle_seconds'],s['duration_seconds']+s['recharge_seconds'])
                self.assertAlmostEqual(s['cycle_dps'],s['cycle_damage']/s['cycle_seconds'])
                self.assertAlmostEqual(s['cycle_hps'],s['cycle_healing']/s['cycle_seconds'])

    def test_continuous_reference_has_exact_13_attack_skill_clock(self):
        s=calc('kaltsit',2,BOOK,timing_mode='continuous')['estimate']['skill']
        # Catalog interval2.85s and4845 damage per attack,13 attacks.
        self.assertAlmostEqual(s['duration_seconds'],37.05)
        self.assertAlmostEqual(s['cycle_seconds'],72.05)
        self.assertAlmostEqual(s['total_damage'],62985)
        self.assertAlmostEqual(s['recharge_seconds'],35)

    def test_mechanist_skill_one_is_known_no_refill_not_fractional_unknown(self):
        for mode in ('frames','continuous'):
            base=calc('mechanist',1,timing_mode=mode)
            for rid in (BOOK,YA):
                r=calc('mechanist',1,rid,timing_mode=mode)
                self.assertTrue(r['relic_resolution']['complete'])
                self.assertEqual(r['estimate']['skill'],base['estimate']['skill'])
                self.assertEqual(r['total_damage'],base['total_damage'])
                section=ammo_section(r)
                self.assertIsNotNone(section)
                self.assertTrue(any('不能触发补弹' in note for note in section['notes']))

    def test_wisdel_and_angel_skill_one_apply_integer_refill_through_events(self):
        for op,n,name,base_count,counts in (
                ('char_1035_wisdel',3,'维什戴尔主攻击',6,(8,9)),
                ('char_1041_angel2',1,'技能攻击',8,(11,12))):
            for mode in ('frames','continuous'):
                b=calc(op,n,timing_mode=mode)
                for rid,count in zip((BOOK,YA),counts):
                    r=calc(op,n,rid,timing_mode=mode)
                    self.assertEqual(r['estimate']['skill']['hit_counts'][name],count)
                    self.assertGreater(r['estimate']['skill']['total_damage'],b['estimate']['skill']['total_damage'])
                    self.assertGreater(r['estimate']['skill']['duration_seconds'],b['estimate']['skill']['duration_seconds'])
                    self.assertTrue(r['relic_resolution']['complete'])

    def test_all_skill_ranks_and_modes_consume_the_same_verified_count_rules(self):
        for op,n,maximum in (('kaltsit',2,10),('mechanist',1,3),('char_1035_wisdel',3,6),('char_1041_angel2',1,8)):
            for rank in range(1,11):
                for mode in ('frames','continuous'):
                    for rid,ratio in ((BOOK,.3),(YA,.5)):
                        r=calc(op,n,rid,skill_rank=rank,timing_mode=mode)
                        p=refill_parameters(maximum,.3,ratio)
                        expected=maximum+(p['refill_count'] if p['threshold'] else 0)
                        name='维什戴尔主攻击' if op=='char_1035_wisdel' else '技能攻击'
                        actual=r['hits']//5 if op=='mechanist' else r.get('hits') or r['estimate']['skill']['hit_counts'][name]
                        self.assertEqual(actual,expected,(op,rank,mode,rid))
                        self.assertTrue(r['relic_resolution']['complete'])

    def test_five_at_a_time_50_percent_path_remains_75_ammunition(self):
        for rank in range(1,11):
            for mode in ('frames','continuous'):
                r=calc('char_1041_angel2',3,YA,skill_rank=rank,timing_mode=mode)
                self.assertEqual(r['estimate']['skill']['hit_counts']['技能攻击'],75)
                self.assertTrue(r['relic_resolution']['complete'])

    def test_sixteen_round_refill_completes_documented_partial_final_packet(self):
        for mode in ('frames','continuous'):
            r=calc('char_1041_angel2',3,BOOK,timing_mode=mode)
            self.assertTrue(r['relic_resolution']['complete'])
            self.assertEqual(r['estimate']['skill']['hit_counts']['技能攻击'],70)
            self.assertEqual(r['estimate']['skill']['hit_counts']['火力电台本体生命回复'],70)
            self.assertEqual(r['relic_resolution']['rules'][0]['ammo_parameters']['partial_packet_reference']['skill'],3)
            for key in ('total_damage','duration_seconds','cycle_seconds','cycle_dps'):
                self.assertIsNotNone(r['estimate']['skill'][key])
            self.assertIsNotNone(r['estimate']['skill']['initial_seconds'])
            self.assertIsNotNone(r['estimate']['skill']['recharge_seconds'])

    def test_dynamic_steal_shields_manual_and_walk_ammo_remain_explicit_unknown(self):
        for op,n in (('char_1041_angel2',2),('mechanist',2),('char_2027_wang',3),('char_1015_aglna2',3)):
            for rid in (BOOK,YA):
                r=calc(op,n,rid)
                self.assertFalse(r['relic_resolution']['complete'])
                self.assertTrue(any('特殊耗弹路径未核验' in s for s in r['relic_resolution']['records'][0]['pending']))
                self.assertIsNone(r['estimate']['skill']['total_damage'])
                self.assertIsNone(r['estimate']['skill']['cycle_seconds'])

    def test_acquisition_order_is_not_inferred_from_input_list_order(self):
        for op,n in (('kaltsit',2),('char_1041_angel2',1),('char_1041_angel2',2),('char_1041_angel2',3)):
            for ids in ([BOOK,YA],[YA,BOOK]):
                r=calc(op,n,ids)
                if op=='char_1041_angel2' and n==2:
                    self.assertFalse(r['relic_resolution']['complete'])
                    self.assertIsNone(r['estimate']['skill']['total_damage'])
                    continue
                self.assertEqual(len(r['relic_resolution']['rules']),2)
                self.assertTrue(r['relic_resolution']['complete'])
                reference=r['ammo_refill_reference']
                self.assertFalse(reference['order_verified'])
                self.assertTrue(reference['count_order_invariant'])
                self.assertEqual(len(reference['cases']),2)
                self.assertEqual({tuple(c['order']) for c in reference['cases']},{(BOOK,YA),(YA,BOOK)})
                self.assertIsNotNone(r['estimate']['skill']['total_damage'])
                self.assertIsNotNone(r['estimate']['skill']['cycle_seconds'])

    def test_poll_race_masks_derived_metrics_without_hiding_independent_training(self):
        with patch('rouge.ammo_reference.refill_before_empty_is_safe',return_value=False):
            r=calc('kaltsit',2,BOOK)
        self.assertFalse(r['relic_resolution']['complete'])
        self.assertTrue(r['relic_resolution']['rules'][0]['ammo_polling_pending'])
        s=r['estimate']['skill']
        for key in ('total_damage','total_healing','duration_seconds','cycle_seconds','phase_damage',
                    'phase_healing','window_damage','window_healing','cycle_dps','cycle_hps'):
            self.assertIsNone(s[key])
        self.assertIsNone(r['total_damage'])
        self.assertIsNone(r['timing']['cycle_seconds'])
        self.assertEqual(s['recharge_seconds'],35)
        self.assertIsNotNone(s['initial_seconds'])
        self.assertEqual(r['estimate']['training']['level'],90)
        self.assertTrue(any('耗尽前检查窗口不足' in s for s in ammo_section(r)['notes']))

    def test_report_shows_quota_distinct_from_actual_returned_ammo(self):
        r=calc('kaltsit',2,BOOK);section=ammo_section(r)
        values={v['key']:v['value'] for v in section['metrics']}
        self.assertEqual(values,{'ammo_max_'+BOOK:10,'ammo_threshold_'+BOOK:3,'ammo_refill_'+BOOK:3})
        self.assertTrue(any('检查相位' in s for s in section['notes']))
        self.assertTrue(any(refill_source()['template_url'] in s for s in section['notes']))

    def test_unrelated_operators_skills_and_unheld_books_have_no_refill_panel(self):
        for op,n,rid in (('kaltsit',1,BOOK),('kaltsit',3,YA),('mechanist',3,BOOK),
                         ('char_151_myrtle',1,YA),('kaltsit',2,None),('mechanist',1,None)):
            self.assertIsNone(ammo_section(calc(op,n,rid)))

    def test_fast_attack_and_limited_supply_do_not_repeat_or_create_infinite_refills(self):
        for speed in (0,500,2000):
            r=calc('kaltsit',2,BOOK,effects=[{'kind':'attack_speed','value':speed}])
            self.assertEqual(r['hits'],13)
        short=calc('kaltsit',2,BOOK,window_seconds=1)
        self.assertEqual(short['total_damage'],0)
        self.assertEqual(short['estimate']['skill']['total_damage'],calc('kaltsit',2,BOOK)['estimate']['skill']['total_damage'])

    def test_repeated_requests_and_deployment_wine_clock_do_not_mutate_input_or_source(self):
        # Wine periodic ticks apply to attack/received SP, not time recovery.
        sc={'operator':'mechanist','skill':1,'relic_ids':[BOOK,'rogue_6_relic_legacy_95']}
        before=copy.deepcopy(sc);data=copy.deepcopy(mechanics()['relics'][BOOK])
        a=calculate_damage(sc);b=calculate_damage(sc)
        self.assertEqual(a,b);self.assertEqual(sc,before);self.assertEqual(mechanics()['relics'][BOOK],data)
        self.assertNotIn('phase_estimate',a['relic_resolution'])
        self.assertEqual(a['deployment_clock_reference']['origin'],'deployment')
        self.assertEqual(a['hits'],15)
        self.assertNotIn('ammo_polling_pending',a['relic_resolution']['rules'][0])

    def test_pinned_extracted_template_has_positive_gate_floor_ceil_and_lifecycle(self):
        excerpt=json.loads((ROOT/'.cache/research/ammo-041/ammo-template-excerpt.json').read_text(encoding='utf-8'))
        blob=json.dumps(excerpt,ensure_ascii=True)
        for fact in ('originalMaxCount','_finalFloor','_finalCeil','recoverSkipLimitCheck',
                     'ON_SKILL_START','ON_SKILL_FINISH','waitFirstTriggerInterval','0.10000000149011612'):
            self.assertIn(fact,blob)
        self.assertIn('"GT"',blob)
        self.assertIn('ammo_remaining',blob)
        self.assertEqual(set(excerpt),{'add_remaining_ammo_by_max_ratio','add_remaining_ammo_by_max_ratio[recover_ammo]'})


if __name__=='__main__':unittest.main()
