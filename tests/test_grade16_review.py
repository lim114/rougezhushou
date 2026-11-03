"""Current grade recognition and qualified subtotals, not live glyph calibration."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
import numpy as np
from PySide6.QtWidgets import QApplication
from rouge import current_battle_reference as current
from rouge.battle_preview import enemy_preview
from rouge.current_enemy_forecast import forecasts
from rouge.run_config import NORMAL_GRADES,config_data,confirmed_config,read_config
from rouge.run_badges import read_badge_grade
from rouge.run_state import RunState
from rouge.node_catalog_view import map_conditions
from rouge import node_catalog
from rouge.player_statistics_cohorts import select_cohort
from tests import test_state_calculation_updates as fixture


class Grade16ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=current.stage_reference('ro6_n_1_1')
        cls.duck=next(e for e in cls.stage['enemies']if e['id']=='enemy_2001_duckmi')

    def test_readable_range_and_existing_profiles_match_the_sealed_current_source(self):
        profiles=self.stage['difficulty_reference']
        self.assertEqual([int(k)for k in profiles],list(NORMAL_GRADES))
        self.assertEqual(profiles['16']['bossValue'],25)
        self.assertIn('25%',profiles['16']['addDesc'])
        self.assertEqual(self.stage['difficulty_source']['commit'],'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d')
        for grade in range(16):
            self.assertEqual(profiles[str(grade)],{k:config_data()['difficulties'][str(grade)][k]for k in profiles[str(grade)]})

    def test_current_profile_grows_by_region_without_claiming_the_full_panel(self):
        for depth in range(1,7):
            config={'difficulty':{'value':16,'source':'public fixture'},'zone':{'main_zone_index':depth}}
            before=deepcopy((self.stage,config))
            row=forecasts(self.stage,config)[self.duck['key']]
            self.assertAlmostEqual(row['environment_component']['maxHp'],18000*1.3*1.25**depth)
            self.assertAlmostEqual(row['environment_component']['atk'],100*1.15*1.25**depth)
            self.assertEqual(row['environment_component']['def'],200)
            self.assertEqual(row['environment_component']['magicResistance'],30)
            self.assertIsNone(row['complete_current_total'])
            self.assertFalse(row['qualified_inputs']['difficulty_fields_equal'])
            self.assertEqual(row['difficulty_profile_source'],self.stage['difficulty_source'])
            self.assertEqual((self.stage,config),before)

    def test_default_legacy_preview_still_rejects_16_but_current_packet_preserves_observed_source(self):
        config={'difficulty':{'value':16,'source':'public observation'},'zone':{'id':'zone_1'}}
        old=enemy_preview('ro6_n_1_1','enemy_2001_duckmi',0,config)
        self.assertIsNone(old['environment'])
        packet={'profiles':self.stage['difficulty_reference'],'source':self.stage['difficulty_source']}
        before=deepcopy((config,packet))
        result=enemy_preview('ro6_n_1_1','enemy_2001_duckmi',0,config,difficulty_reference=packet)
        self.assertIsNotNone(result['environment'])
        self.assertEqual((config,packet),before)

    def test_located_badge_text_and_crop_fallback_accept_16_without_accepting_17(self):
        image=np.zeros((600,1000,3),np.uint8)
        badge={'box':[[.1,.7],[.2,.7],[.2,.86],[.1,.86]]}
        record={'text':'16','confidence':.99,'box':[[.07,.8],[.09,.8],[.09,.86],[.07,.86]]}
        self.assertEqual(read_badge_grade(image,badge,[record]),16)
        self.assertIsNone(read_badge_grade(image,badge,[{**record,'text':'17'}]))
        self.assertEqual(read_badge_grade(image,badge,[],lambda crop:([([], '16',.99)],None)),16)
        self.assertIsNone(read_badge_grade(image,badge,[record,{**record,'text':'15'}]))

    def test_confirmed_grade16_and_squad_skip_repeated_badge_search(self):
        context={'run_id':'public-grade16','config':{
            'difficulty':{'value':16,'captured_at':1,'badge':{'old_geometry':True}},
            'squad':{'id':'rogue_6_band_1','name':config_data()['squads']['rogue_6_band_1']['name'],'captured_at':1}}}
        before=deepcopy(context);known=confirmed_config(context)
        self.assertEqual(known['difficulty']['value'],16)
        self.assertNotIn('badge',known['difficulty'])
        self.assertEqual(known['difficulty']['reused_from_run'],'public-grade16')
        with patch('rouge.run_badges.find_squad_badge',side_effect=AssertionError('repeated search')):
            self.assertEqual(read_config(np.zeros((60,100,3),np.uint8),[],[],known_config=known),{})
        self.assertEqual(context,before)

    def test_label_anchored_16_keeps_original_canonical_digit_requirement(self):
        image=np.zeros((100,100,3),np.uint8)
        label={'text':'保密等级','confidence':.99,'box':[[.1,.1],[.2,.1],[.2,.2],[.1,.2]]}
        digit={'text':'16','confidence':.99,'box':[[.23,.1],[.25,.1],[.25,.2],[.23,.2]]}
        with patch('rouge.run_config.units',return_value=(1,1)),patch('rouge.run_badges.find_squad_badge',return_value=None):
            self.assertEqual(read_config(image,[label,digit],[])['difficulty']['value'],16)
            self.assertNotIn('difficulty',read_config(image,[label,{**digit,'text':'00'}],[]))

    def test_same_run_retains_16_through_missing_page_and_restart(self):
        with TemporaryDirectory()as folder:
            file=Path(folder)/'run.json';state=RunState(file)
            state.state['started_at']=999
            state.apply({'config':{'difficulty':{'value':16,'source':'public fixture'}}},1000)
            identity=state.state['id'];state.apply({},1001)
            self.assertEqual(state.state['config']['difficulty']['value'],16)
            loaded=RunState(file)
            self.assertEqual(loaded.state['id'],identity)
            self.assertEqual(loaded.state['config']['difficulty']['value'],16)

    def test_grade16_is_its_own_archive_group(self):
        rows=[{'state':{'id':str(g),'config':{'difficulty':{'value':g,'captured_at':1}}}}for g in(0,15,16,17)]
        self.assertEqual([r['state']['id']for r in select_cohort(rows,difficulty=16)],['16'])

    def test_fixed_node_catalog_does_not_borrow_grade15_or_raise_on_current16(self):
        for grade in(15,16):
            context=map_conditions({'zone_id':'zone_1'},{'difficulty':{'value':grade}})
            self.assertEqual(context['difficulty'],15 if grade==15 else None)
            result=node_catalog.function_nodes('诡意行商',**context)
            self.assertIsInstance(result['rows'],list)


class Grade16WindowTests(unittest.TestCase):
    setUp=fixture.StateCalculationUpdateTests.setUp
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_main_control_shows_real16_and_does_not_reuse_previous_damage(self):
        w=self.window;w.calculate();self.assertIsNotNone(w.damage_result)
        w.run.state['config']={'difficulty':{'value':16,'captured_at':1}}
        w.sync_run_config();w.calculate()
        self.assertEqual(w.difficulty.currentData(),16)
        self.assertFalse(w.difficulty.isEnabled())
        self.assertIn('仍待适配',w.difficulty.toolTip())
        self.assertIsNone(w.damage_result)
        for name in('offline_tools','paired_calibration','timing_calibration','bounded_calibration','calibration_experiment'):
            self.assertIsNone(getattr(w,name)._scenario)
