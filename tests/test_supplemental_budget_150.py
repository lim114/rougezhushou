import os
import unittest
from copy import deepcopy
from rouge.supplemental_skills import defaults
from rouge.supplemental_budget import (budget_reference,damage_defaults,healing_defaults,
    declared_damage_budget,declared_healing_budget,format_supplemental_damage_budget,
    format_supplemental_healing_budget)
from rouge.damage_budget import damage_sources
from rouge.healing_budget import healing_sources
from tests.test_supplemental_run_141 import environment


class Budget150Tests(unittest.TestCase):
    def test_target_defense_recomputed_before_relic_multiplier(self):
        p=defaults();e=environment(['rogue_6_relic_legacy_5'])
        data=damage_defaults(p,e);data['targets'].append({'id':'高防','hp':4000,'defense':10000,'resistance':0})
        source=data['events'][0]['source'];data['events'].append({'at_seconds':0,'target':'高防','source':source})
        r=declared_damage_budget(p,e,data)
        low,high=r['rows'];self.assertLess(high['per_hit'],low['per_hit'])
        attack=budget_reference(p,e)['supplemental']['rows'][1]['value']
        self.assertAlmostEqual(high['per_hit'],attack*.05*1.15)
        self.assertIsNone(r['actual_kill_time']);self.assertFalse(r['native_hit_clock_verified'])

    def test_damage_exhaustion_overflow_and_same_time_input_order(self):
        p=defaults();e=environment();data=damage_defaults(p,e);data['targets'][0]['hp']=100
        data['events']*=2;r=declared_damage_budget(p,e,data)
        self.assertEqual([row['input_order'] for row in r['rows']],[0,1])
        self.assertEqual(r['rows'][0]['effective_damage'],100);self.assertEqual(r['rows'][1]['effective_damage'],0)
        self.assertEqual(r['targets'][0]['hp'],0);self.assertEqual(r['targets'][0]['budget_exhausted_at'],0)
        self.assertIn('不是实际击杀时间',format_supplemental_damage_budget(r))

    def test_marginal_expectation_unknown_combo_and_regeneration_not_sources(self):
        p=defaults('char_124_kroos');e=environment()
        sources=damage_sources(budget_reference(p,e))
        self.assertTrue(sources)
        self.assertFalse(any('期望' in s['name'] or s['name']=='二连射含天赋组合' for s in sources))
        data=damage_defaults(p,e);data['events'][0]['source']='damage_2'
        with self.assertRaises(ValueError):declared_damage_budget(p,e,data)
        p=defaults('char_120_hibisc');e=environment(['rogue_6_relic_legacy_41'])
        self.assertTrue(all(s['name'] in ('普通单次治疗','技能单次治疗') for s in healing_sources(budget_reference(p,e))))

    def test_heal_multiplier_and_loss_order_effective_overhealing(self):
        p=defaults('char_120_hibisc');e=environment(['rogue_6_relic_legacy_99'])
        data=healing_defaults(p,e);data['recipients']=[{'id':'友方甲','max_hp':3000,'hp':2900},
                                                     {'id':'友方乙','max_hp':2000,'hp':1800}]
        heal=data['events'][0];data['events']=[{**heal,'at_seconds':2},
            {'at_seconds':0,'recipient':'友方甲','kind':'loss','amount':500},
            {**heal,'at_seconds':2,'recipient':'友方乙'}]
        r=declared_healing_budget(p,e,data)
        self.assertEqual([row['input_order'] for row in r['rows']],[1,0,2])
        self.assertEqual(r['effective_healing'],800)
        expected=budget_reference(p,e)['supplemental']['rows'][1]['value']
        self.assertAlmostEqual(r['overhealing'],expected*2-800)
        self.assertFalse(r['actual_acquisition_verified'])
        self.assertIn('冻结本局',format_supplemental_healing_budget(r))

    def test_self_healing_restricted_to_calculated_self_maximum(self):
        p=defaults('char_209_ardign');e=environment();data=healing_defaults(p,e)
        r=declared_healing_budget(p,e,data);self.assertEqual(r['effective_healing'],500)
        bad=deepcopy(data);bad['recipients'][0]['id']='另一位友方'
        with self.assertRaises(ValueError):declared_healing_budget(p,e,bad)
        bad=deepcopy(data);bad['recipients'][0]['max_hp']+=1
        with self.assertRaises(ValueError):declared_healing_budget(p,e,bad)

    def test_inputs_are_frozen_and_empty_events_are_declared_zero(self):
        p=defaults();e=environment();data=damage_defaults(p,e);data['events']=[]
        before=deepcopy((p,e,data));r=declared_damage_budget(p,e,data)
        self.assertEqual((p,e,data),before);self.assertEqual(r['targets'][0]['effective_damage'],0)
        e['relic_ids'].append('later');self.assertEqual(r['environment']['relic_ids'],[])

    def test_bad_event_types_duplicate_target_unknown_source_rejected(self):
        p=defaults();e=environment();data=damage_defaults(p,e)
        for time in [True,float('nan'),-1]:
            bad=deepcopy(data);bad['events'][0]['at_seconds']=time
            with self.subTest(time=time),self.assertRaises(ValueError):declared_damage_budget(p,e,bad)
        data['targets']*=2
        with self.assertRaises(ValueError):declared_damage_budget(p,e,data)
        with self.assertRaises(ValueError):damage_defaults(defaults('char_123_fang'),e)
        with self.assertRaises(ValueError):healing_defaults(defaults(),e)

    @unittest.skipUnless(os.name=="nt" or os.environ.get("QT_QPA_PLATFORM")=="offscreen" or os.environ.get("DISPLAY"),
                         "Qt entry unavailable without a display/offscreen capability")
    def test_role_specific_ui_hides_irrelevant_tools_and_opens_budgets(self):
        try:
            from PySide6.QtWidgets import QApplication
            from rouge.supplemental_run_view import SupplementalRunDialog
        except ImportError:self.skipTest('Qt unavailable')
        app=QApplication.instance() or QApplication([])
        for identity,damage,healing in [('char_208_melan',True,False),('char_123_fang',False,False),
            ('char_209_ardign',False,True),('char_120_hibisc',False,True)]:
            d=SupplementalRunDialog(defaults(identity),environment)
            self.assertEqual(d.damage_button.isHidden(),not damage);self.assertEqual(d.healing_button.isHidden(),not healing)
            if damage:d.show_damage_budget()
            if healing:d.show_healing_budget()
            if damage or healing:
                child=d.children_dialogs[-1];self.assertIsNotNone(child.result);self.assertEqual(child.table.rowCount(),1);child.close()
            if identity=='char_209_ardign':self.assertEqual(d.healing_button.text(),'自身声明治疗预算')
            d.editor.setPlainText('{}');self.assertTrue(d.damage_button.isHidden());self.assertTrue(d.healing_button.isHidden())
            d.close();app.processEvents()
