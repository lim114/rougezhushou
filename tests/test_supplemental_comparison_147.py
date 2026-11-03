import os
import unittest
from copy import deepcopy
from rouge.supplemental_skills import defaults
from rouge.supplemental_run import run_skill_reference
from rouge.supplemental_comparison import compare_ranks,format_comparison
from tests.test_supplemental_run_141 import environment


class RankComparison147Tests(unittest.TestCase):
    def test_all_seven_levels_match_independent_run_calculation(self):
        p=defaults();e=environment(['rogue_6_relic_legacy_5'])
        result=compare_ranks(p,e,{'ranks':list(range(1,8))})
        for variant in result['variants']:
            direct=run_skill_reference({**p,'skill_rank':variant['rank']},e)
            self.assertEqual(variant['result'],direct)
        self.assertGreater(next(r['delta'] for r in result['rows'] if r['rank']==7 and r['key']=='skill:技能单次物理伤害'),-1e-9)
        self.assertLess(next(r['delta'] for r in result['rows'] if r['rank']==1 and r['key']=='skill:技能单次物理伤害'),0)

    def test_sp_and_dp_use_each_original_rank(self):
        p=defaults('char_123_fang');e=environment(['rogue_6_relic_book_1'])
        result=compare_ranks(p,e,{'ranks':[7,1]})
        a,b=result['variants'];self.assertEqual(a['result']['rows'][0]['value'],9)
        self.assertEqual(b['result']['rows'][0]['value'],9)
        self.assertNotEqual(a['result']['sp_reference']['cost_parameter'],b['result']['sp_reference']['cost_parameter'])

    def test_unknown_damage_combination_stays_unknown(self):
        r=compare_ranks(defaults('char_124_kroos'),environment(),{'ranks':[1,7]})
        rows=[row for row in r['rows'] if row['name']=='二连射含天赋组合']
        self.assertTrue(all(row['value'] is None and row['delta'] is None for row in rows))
        self.assertIn('未知',format_comparison(r))

    def test_healing_recomputed_without_damage_or_dp_fields(self):
        r=compare_ranks(defaults('char_120_hibisc'),environment(),{'ranks':[1,7]})
        values=[row['value'] for row in r['rows'] if row['name']=='技能单次治疗']
        self.assertLess(values[0],values[1])
        self.assertFalse(any(row['unit']=='物理伤害' or row['name']=='单次回费' for row in r['rows']))

    def test_inputs_frozen_and_invalid_lists_rejected(self):
        p=defaults();e=environment();old=deepcopy((p,e))
        r=compare_ranks(p,e,{'ranks':[7]});self.assertEqual((p,e),old)
        e['relic_ids'].append('later');self.assertNotIn('later',r['environment']['relic_ids'])
        for ranks in [[],[True],[0],[8],[1,1],list(range(1,9)),'7']:
            with self.subTest(ranks=ranks),self.assertRaises(ValueError):compare_ranks(p,old[1],{'ranks':ranks})

    @unittest.skipUnless(os.name=="nt" or os.environ.get("QT_QPA_PLATFORM")=="offscreen" or os.environ.get("DISPLAY"),
                         "Qt entry unavailable without a display/offscreen capability")
    def test_visible_entry_freezes_conditions_and_keeps_operator(self):
        try:
            from PySide6.QtWidgets import QApplication
            from rouge.supplemental_run_view import SupplementalRunDialog
        except ImportError:self.skipTest('Qt unavailable')
        app=QApplication.instance() or QApplication([])
        e=environment();p=defaults('char_210_stward');d=SupplementalRunDialog(p,lambda:e)
        d.show_ranks();child=d.children_dialogs[-1]
        self.assertIsNotNone(child.result);self.assertEqual(len(child.result['variants']),7)
        e['relic_ids'].append('rogue_6_relic_legacy_8');d.refresh_environment()
        self.assertEqual(d.result['preview']['operator'],p['operator'])
        self.assertEqual(child.result['environment']['relic_ids'],[])
        child.close();d.close();app.processEvents()
