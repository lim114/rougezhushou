import unittest
from itertools import permutations
from copy import deepcopy
from rouge.supplemental_run import run_skill_reference,format_run_reference
from rouge.supplemental_skills import defaults,skill_reference
from rouge.relic_healing_factors import healing_factor,regeneration_factor,COMPOSITION_EVIDENCE
from rouge.relics import mechanics
from rouge.damage import calculate_damage
from tests.test_supplemental_run_141 import environment

FLOWERS=['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82','rogue_6_relic_legacy_83']


class FlowerHealingCompositionTests(unittest.TestCase):
    def test_direct_healing_and_regen_have_distinct_literal_oracles(self):
        p=defaults('char_120_hibisc');p.update(count=2,missing_hp=1000)
        base=skill_reference(p);amount=next(x['value']for x in base['rows']if x['name']=='技能单次治疗')
        r=run_skill_reference(p,environment(FLOWERS));ref=r['healing_reference']
        self.assertAlmostEqual(ref['healing_factor'],2.184)
        self.assertAlmostEqual(ref['regeneration_factor'],1.9)
        self.assertAlmostEqual(next(x['value']for x in r['rows']if x['name']=='技能单次治疗'),amount*2.184)
        self.assertEqual(next(x['value']for x in r['rows']if x['name']=='声明次数有效治疗合计'),1000)
        self.assertAlmostEqual(next(x['value']for x in r['rows']if x['name']=='声明次数过量治疗合计'),amount*2.184*2-1000)
        self.assertIn('独立乘算因子2.184',format_run_reference(r))

    def test_three_sources_order_and_duplicate_ids_do_not_square_channels(self):
        for order in permutations(FLOWERS):
            e=environment([*order,order[0],'rogue_6_relic_legacy_22','rogue_6_relic_legacy_91'])
            before=deepcopy(e);r=run_skill_reference(defaults('char_209_ardign'),e)
            ref=r['healing_reference'];hp=r['attributes']['hp']
            self.assertAlmostEqual(ref['healing_factor'],2.184)
            self.assertAlmostEqual(ref['relic_regeneration_rate'],(3+hp*.01)*1.9)
            self.assertEqual(e,before)
            self.assertEqual(len(ref['regeneration_source_ids']),3)
            self.assertFalse(ref['actual_ticks_verified'])
            self.assertIsNone(r['cycle_output'])

    def test_attack_operator_gains_regen_parameter_without_direct_healing_rows(self):
        r=run_skill_reference(defaults(),environment(FLOWERS+['rogue_6_relic_legacy_22']))
        self.assertAlmostEqual(r['healing_reference']['relic_regeneration_rate'],5.7)
        self.assertFalse(any(x['unit']=='治疗量'for x in r['rows']))
        row=next(x for x in r['rows']if x['name']=='藏品常态生命回复')
        self.assertIsNone(row['declared_total'])

    def test_all_main_healing_subtotals_use_the_same_proved_product(self):
        s={'operator':'char_1037_amiya3','skill':1,'timing':{'windup_frames':6,'recovery_frames':9}}
        plain=calculate_damage(s);r=calculate_damage({**s,'relic_ids':FLOWERS})
        self.assertEqual(r['total_damage'],plain['total_damage'])
        for key in ('total_healing','phase_healing','window_healing','cycle_healing'):
            expected=plain['estimate']['skill'].get(key)
            if expected is not None:self.assertAlmostEqual(r['estimate']['skill'][key],expected*2.184)
            else:self.assertIsNone(r['estimate']['skill'].get(key))
        self.assertEqual(r['estimate']['skill']['cycle_seconds'],plain['estimate']['skill']['cycle_seconds'])

    def test_unproven_source_or_attachment_index_cannot_generalize_composition(self):
        known=[]
        for identity in FLOWERS[:2]:
            known.extend({**e,'relic_id':identity,'_verified_rule':True}
                for e in mechanics()['relics'][identity]['effects'])
        heal=[r for r in known if r['kind']=='healing_factor']
        regen=[r for r in known if r['kind']=='regeneration_factor']
        self.assertAlmostEqual(healing_factor(heal),1.56)
        self.assertAlmostEqual(regeneration_factor(regen),1.5)
        for field,value in (('relic_id','unknown'),('source_buff_index',9),
                            ('source_buff_key','char_attribute_mul'),('composition_evidence','unknown')):
            bad=deepcopy(heal);bad[1][field]=value
            self.assertIsNone(healing_factor(bad))
            bad=deepcopy(regen);bad[-1][field]=value
            self.assertIsNone(regeneration_factor(bad))

    def test_inventory_unknown_still_blocks_complete_run_claim(self):
        e=environment(FLOWERS);e['inventory_status']['complete']=False
        r=run_skill_reference(defaults('char_120_hibisc'),e)
        self.assertAlmostEqual(r['healing_reference']['healing_factor'],2.184)
        self.assertFalse(r['attribute_resolution']['complete_for_attribute_scope'])
        self.assertIn('清单尚未确认完整',format_run_reference(r))

    def test_data_marks_only_the_three_source_bound_flower_families(self):
        marked=[]
        for rid,entry in mechanics()['relics'].items():
            for e in entry['effects']:
                if e.get('composition_evidence')==COMPOSITION_EVIDENCE:marked.append((rid,e))
        self.assertEqual(len(marked),9)
        self.assertEqual({rid for rid,_ in marked},set(FLOWERS))
        self.assertEqual({e['kind']for _,e in marked},{'healing_factor','regeneration_factor'})
