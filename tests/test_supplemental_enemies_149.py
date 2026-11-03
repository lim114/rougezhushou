import os
import unittest
from copy import deepcopy
from rouge.catalog import catalog,stage_previews
from rouge.supplemental_skills import defaults
from rouge.supplemental_run import run_skill_reference
from rouge.supplemental_enemies import enemy_defaults,compare_fixed_enemies,format_fixed_enemies
from tests.test_supplemental_run_141 import environment


class Enemy149Tests(unittest.TestCase):
    def test_identity_overrides_manual_defense_and_resistance(self):
        p=defaults('char_210_stward');p.update(enemy_defense=99999,enemy_resistance=99)
        e=environment();r=compare_fixed_enemies(p,e,enemy_defaults(e))
        for v in r['variants']:
            result=v['result'];enemy=result['target_enemy']['stats'];atk=result['attributes']['attack']
            scale=next(b['value'] for b in result['skill_parameter']['blackboard'] if b['key']=='atk_scale')
            factor=result['damage_reference']['damage_factors']['magic']
            self.assertAlmostEqual(result['rows'][1]['value'],atk*scale*(1-min(enemy['magicResistance'],95)/100)*factor)
            self.assertEqual(result['preview'],p)

    def test_grade5_hp_threshold_and_same_target_baseline(self):
        e=environment();data=enemy_defaults(e);data.update(enemies=data['enemies'][:1],grades=[4,5])
        r=compare_fixed_enemies(defaults(),e,data);a,b=r['variants']
        self.assertAlmostEqual(b['result']['target_enemy']['stats']['maxHp'],a['result']['target_enemy']['stats']['maxHp']*1.3)
        row=next(row for row in r['rows'] if row['grade']==5 and row['key']=='enemy:maxHp')
        self.assertAlmostEqual(row['delta'],row['base_value']*.3)
        skill=b['result']['rows'][2];self.assertEqual(skill['delta'],0)

    def test_enemy_relic_hp_def_and_per_hit_scale_only_once(self):
        e=environment(['rogue_6_relic_legacy_84','rogue_6_relic_legacy_5'])
        data=enemy_defaults(e);data['enemies']=data['enemies'][:1]
        r=compare_fixed_enemies(defaults(),e,data)['variants'][0]['result']
        panel=r['target_enemy']['stats'];original=r['target_enemy']['reference_stats']
        self.assertAlmostEqual(panel['maxHp'],original['maxHp']*.95)
        self.assertAlmostEqual(panel['def'],original['def']*.9)
        self.assertEqual(r['damage_reference']['effective_target_defense'],panel['def'])
        atk=r['rows'][1]['value'];self.assertAlmostEqual(r['rows'][2]['value'],max(atk-panel['def'],atk*.05)*1.15)
        self.assertFalse(any(x['kind']=='enemy_hp_factor' for x in r['attribute_resolution']['unsupported']))

    def test_boss_damage_factor_and_pending_sources_visible(self):
        sid,record=next((sid,r) for sid,p in stage_previews().items() for r in p['possible_enemies'] if r['level_type']=='BOSS')
        data={'stage_id':sid,'enemies':[{'enemy_id':record['id'],'level':record['level']}],'grades':[10,11],'orb_mode':'unknown'}
        r=compare_fixed_enemies(defaults(),environment(),data)
        self.assertEqual(r['variants'][1]['result']['damage_reference']['damage_factors']['physical'],.8)
        self.assertIn('脚本',format_fixed_enemies(r));self.assertIn('不保证出场',format_fixed_enemies(r))

    def test_orb_unknown_and_explicit_column_remain_separate(self):
        sid,record=next((sid,r) for sid,p in stage_previews().items() for r in p['possible_enemies'] if r['id']=='enemy_2148_shorbb')
        data={'stage_id':sid,'enemies':[{'enemy_id':record['id'],'level':record['level']}],'grades':[4],'orb_mode':'unknown'}
        a=compare_fixed_enemies(defaults(),environment(),data)['variants'][0]['result']
        self.assertTrue(any('来源列未确认' in n for n in a['attribute_resolution']['warnings']))
        data['orb_mode']='active_other_column'
        b=compare_fixed_enemies(defaults(),environment(),data)['variants'][0]['result']
        self.assertLess(b['damage_reference']['damage_factors']['physical'],a['damage_reference']['damage_factors']['physical'])

    def test_bound_target_does_not_mutate_run_or_catalog(self):
        e=environment();e['run_config']={'zone':{'id':'zone_4','source':'public fixture'}}
        p=defaults();data=enemy_defaults(e);old=deepcopy((e,p,data,catalog(),stage_previews()))
        compare_fixed_enemies(p,e,data)
        self.assertEqual((e,p,data,catalog(),stage_previews()),old)

    def test_invalid_selection_types_mode_and_duplicates(self):
        e=environment();p=defaults();data=enemy_defaults(e)
        for grades in ([],[True],[4,4],list(range(7)),[16]):
            with self.subTest(grades=grades),self.assertRaises(ValueError):compare_fixed_enemies(p,e,{**data,'grades':grades})
        for target in ({},False,{'stage_id':'ro6_n_1_1','enemy_id':'wrong','level':True}):
            with self.subTest(target=target),self.assertRaises(ValueError):run_skill_reference(p,e,target_enemy=target)
        data['enemies']=[data['enemies'][0]]*2
        with self.assertRaises(ValueError):compare_fixed_enemies(p,e,data)

    @unittest.skipUnless(os.name=="nt" or os.environ.get("QT_QPA_PLATFORM")=="offscreen" or os.environ.get("DISPLAY"),
                         "Qt entry unavailable without a display/offscreen capability")
    def test_qt_fixed_target_entry_returns_readable_result(self):
        try:
            from PySide6.QtWidgets import QApplication
            from rouge.supplemental_run_view import SupplementalRunDialog
        except ImportError:self.skipTest('Qt unavailable')
        app=QApplication.instance() or QApplication([])
        d=SupplementalRunDialog(defaults('char_210_stward'),environment)
        d.show_enemies();child=d.children_dialogs[-1]
        self.assertIsNotNone(child.result);self.assertIn('候选',child.notice.toPlainText())
        self.assertGreater(child.table.rowCount(),0);child.close();d.close();app.processEvents()
