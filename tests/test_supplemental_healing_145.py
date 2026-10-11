import unittest
from rouge.supplemental_run import run_skill_reference,format_run_reference
from rouge.supplemental_skills import defaults,skill_reference
from tests.test_supplemental_run_141 import environment


class SupplementalHealing145Tests(unittest.TestCase):
    def test_healing_factor_then_effective_budget(self):
        for identity in ('char_209_ardign','char_120_hibisc'):
            p=defaults(identity);p.update(count=2,missing_hp=1000)
            base=skill_reference(p);r=run_skill_reference(p,environment(['rogue_6_relic_legacy_81']))
            rows={x['name']:x for x in r['rows']};a=next(x['value'] for x in base['rows'] if x['name']=='技能单次治疗')*1.2
            self.assertAlmostEqual(rows['技能单次治疗']['value'],a)
            self.assertAlmostEqual(rows['声明次数有效治疗合计']['value'],min(a*2,1000))
            self.assertAlmostEqual(rows['声明次数过量治疗合计']['value'],max(0,a*2-1000))
            self.assertAlmostEqual(rows['技能单次治疗']['delta'],a-a/1.2)

    def test_ambiguous_multiple_factors_keep_unknown_rows(self):
        p=defaults('char_120_hibisc');e=environment(['rogue_6_relic_legacy_81','rogue_6_relic_legacy_82'])
        r=run_skill_reference(p,e)
        self.assertIsNone(r['healing_reference']['healing_factor'])
        for row in r['rows']:
            if row['unit']=='治疗量':self.assertIsNone(row['value']);self.assertIsNone(row['delta'])
        self.assertIn('叠加规则',format_run_reference(r))

    def test_flat_ratio_and_single_regen_factor_use_normal_hp(self):
        p=defaults('char_209_ardign')
        e=environment(['rogue_6_relic_legacy_22','rogue_6_relic_legacy_91','rogue_6_relic_legacy_81'])
        r=run_skill_reference(p,e);ref=r['healing_reference']
        self.assertEqual(ref['regeneration_factor'],1.2)
        self.assertAlmostEqual(ref['relic_regeneration_rate'],(3+2721.6*.01)*1.2)
        row=next(x for x in r['rows'] if x['name']=='藏品常态生命回复')
        self.assertEqual(row['base_value'],0);self.assertEqual(row['delta'],row['value'])
        self.assertIsNone(row['declared_total']);self.assertFalse(ref['actual_ticks_verified'])

    def test_ordinary_hp_part_bonus_is_used_for_ratio(self):
        p=defaults('char_209_ardign');e=environment(['rogue_6_relic_cargo_2','rogue_6_relic_legacy_91'])
        e['relic_context']['parts_count']=4
        r=run_skill_reference(p,e)
        self.assertAlmostEqual(r['healing_reference']['relic_regeneration_rate'],3499.2*.01)

    def test_no_healing_or_regen_rows_added_to_attack_operator_without_source(self):
        r=run_skill_reference(defaults(),environment())
        self.assertFalse(any(x['unit'] in ('治疗量','生命/秒') for x in r['rows']))
        r=run_skill_reference(defaults(),environment(['rogue_6_relic_legacy_22']))
        self.assertEqual(r['rows'][-1]['value'],3)
        self.assertFalse(any(x['unit']=='治疗量' for x in r['rows']))

    def test_duplicate_item_does_not_square_regen_multiplier(self):
        e=environment(['rogue_6_relic_legacy_22','rogue_6_relic_legacy_81','rogue_6_relic_legacy_81'])
        r=run_skill_reference(defaults(),e)
        self.assertAlmostEqual(r['healing_reference']['relic_regeneration_rate'],3.6)
