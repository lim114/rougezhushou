"""Unknown relic effects must qualify the default report, without changing math."""
from copy import deepcopy
from pathlib import Path
from types import ModuleType
from unittest.mock import patch
import unittest

from rouge import damage, reporting
from tests import test_state_calculation_updates as state_tests

ROOT=Path(__file__).resolve().parents[1]
COMPARISONS=[]


class RelicReportScopeReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=ModuleType('rouge._prior_relic_report_scope')
        cls.old.__package__='rouge'
        raw=(ROOT/'research/relic-report-scope-review-20261031/before-reporting.py').read_bytes()
        exec(compile(raw,'<own-prior-reporting>','exec'),cls.old.__dict__)

    def compare(self, scenario):
        original=deepcopy(scenario)
        with patch.object(reporting,'build_report',self.old.build_report):
            before=damage.calculate_damage(scenario)
        after=damage.calculate_damage(scenario)
        self.assertEqual(scenario,original)
        self.assertEqual({k:v for k,v in before.items() if k!='report'},
                         {k:v for k,v in after.items() if k!='report'})
        COMPARISONS.append({'input':scenario,'numeric_state_and_original_unknowns_equal':True,
                            'relic_scope_partial':after['report'].get('relic_coverage',{}).get('status')=='partial'})
        return before,after

    def test_missing_gold_reproduces_old_ambiguity_and_qualifies_all_nine_skills(self):
        for op in ('kaltsit','silverash','mechanist'):
            for skill in (1,2,3):
                with self.subTest(op=op,skill=skill):
                    before,after=self.compare({'operator':op,'skill':skill,'relic_ids':['rogue_6_relic_legacy_60']})
                    self.assertNotIn('藏品尚未计全',self.old.format_report(before))
                    scope=after['report']['relic_coverage']
                    self.assertIsNone(scope['complete_result'])
                    self.assertEqual(scope['numeric_scope'],'confirmed_effects_reference')
                    self.assertIn('gold','\n'.join(scope['warnings']))
                    for technical in (False,True):
                        text=reporting.format_report(after,technical=technical)
                        self.assertLess(text.index('完整结果未知'),text.index('生命值：'))
                        self.assertIn('不保证是最低值',text)
                        self.assertIn('【已计效果下的属性参考】',text)
                    for block in after['report']['sections']:
                        if block['id'] in ('timing','skill_stats','damage','healing'):
                            self.assertIn('已计效果参考',block['title'])

    def test_known_zero_and_positive_gold_keep_exact_original_report(self):
        for gold in (0,24,25):
            before,after=self.compare({'operator':'mechanist','skill':3,
                'relic_ids':['rogue_6_relic_legacy_60'],'relic_context':{'gold':gold}})
            self.assertEqual(after['report'],before['report'])
            self.assertEqual(reporting.format_report(after),self.old.format_report(before))

    def test_recruitment_unknown_then_confirmed_keeps_partial_values_and_clears_notice(self):
        scenario={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_cargo_10']}
        _,unknown=self.compare(scenario)
        self.assertIn('relic_coverage',unknown['report'])
        for kind in ('non_emergency','emergency_hire'):
            before,known=self.compare({**scenario,'recruitment_kind':kind})
            self.assertEqual(before['report'],known['report'])
            self.assertNotIn('relic_coverage',known['report'])
        self.assertGreater(known['estimate']['base_stats']['attack'],unknown['estimate']['base_stats']['attack'])

    def test_unverified_combination_remains_unknown_and_original_subtotals_are_preserved(self):
        before,after=self.compare({'operator':'mechanist','skill':3,
            'relic_ids':['rogue_6_relic_legacy_84','rogue_6_relic_legacy_85']})
        self.assertTrue(any('叠加规则' in w for w in after['relic_resolution']['warnings']))
        self.assertIsNone(after['report']['relic_coverage']['complete_result'])
        self.assertEqual(after['total_damage'],before['total_damage'])

    def test_capability_sections_are_not_added_for_other_professions(self):
        for op,skill,absent in [('char_298_susuro',1,('damage','dp')),
                               ('char_151_myrtle',1,('healing',))]:
            before,after=self.compare({'operator':op,'skill':skill,'relic_ids':['rogue_6_relic_cargo_10']})
            self.assertIn('relic_coverage',after['report'])
            ids={b['id'] for b in after['report']['sections']}
            for key in absent:self.assertNotIn(key,ids)
            self.assertEqual(ids-{ 'relic_coverage'}, {b['id']for b in before['report']['sections']})

    def test_unconfirmed_training_and_reference_only_relic_do_not_claim_missing_relic_math(self):
        for extra in ({'unconfirmed_training':['当前等级']},
                      {'relic_ids':['rogue_6_relic_legacy_100']},{}):
            before,after=self.compare({'operator':'mechanist','skill':1,**extra})
            self.assertEqual(before['report'],after['report'])
            self.assertNotIn('藏品尚未计全',reporting.format_report(after))

    def test_real_mainwindow_default_technical_raw_and_refresh_views_use_scope(self):
        fixture=state_tests.StateCalculationUpdateTests('test_run_update_calculates_final_inputs_once_before_return')
        fixture.setUpClass();fixture.setUp()
        try:
            window=fixture.window
            scenario={'operator':'mechanist','skill':3,'relic_ids':['rogue_6_relic_legacy_60']}
            for context,partial in [({},True),({'gold':25},False),({},True)]:
                result=damage.calculate_damage({**scenario,'relic_context':context})
                window.damage_result={'scenario':scenario,'result':result}
                for technical in (False,True):
                    window.raw_damage.setChecked(False);window.damage_technical.setChecked(technical)
                    window.render_damage()
                    self.assertEqual('完整结果未知' in window.damage_text.toPlainText(),partial)
                window.raw_damage.setChecked(True);window.render_damage()
                self.assertEqual('confirmed_effects_reference' in window.damage_text.toPlainText(),partial)
        finally:
            fixture.doCleanups()
