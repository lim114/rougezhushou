"""285 adapter contracts; production by default, optional explicit draft overlay.

Synthetic main results below check routing/copying only. They do not constitute
another numerical, source-mechanism, native-clock or game-panel verification.
"""
from copy import deepcopy
import importlib
from importlib.machinery import ModuleSpec
import json
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name=='tests' else Path(__file__).resolve().parents[2]
DRAFT_ROOT=None
MYRTLE='char_151_myrtle'
DEEP='char_110_deepcl'
SHU='char_2025_shu'


def load_subjects():
    if DRAFT_ROOT is None:
        return importlib.import_module('rouge.calibration'),importlib.import_module('rouge.offline_tools_view')
    draft=Path(DRAFT_ROOT).resolve()
    if not all((draft/'rouge'/name).is_file() for name in ('calibration.py','offline_tools_view.py')):
        raise ValueError('Explicit draft overlay is incomplete.')
    package=types.ModuleType('section285_candidate')
    package.__path__=[str(draft/'rouge'),str(ROOT/'rouge')]
    package.__package__=package.__name__
    package.__spec__=ModuleSpec(package.__name__,loader=None,is_package=True)
    sys.modules[package.__name__]=package
    return (importlib.import_module(package.__name__+'.calibration'),
            importlib.import_module(package.__name__+'.offline_tools_view'))


class ExtendedCalibration285Tests(unittest.TestCase):
    calibration=None
    view=None

    @classmethod
    def setUpClass(cls):
        if cls.calibration is None or cls.view is None:
            cls.calibration,cls.view=load_subjects()

    def fake_calculator(self, calls, returned=None):
        """Explicit synthetic owner markers; no asserted production numbers."""
        def calculate(scenario):
            calls.append(deepcopy(scenario))
            entry=self.calibration.catalog()['operators'][scenario['operator']]['skills'][scenario['skill']-1]
            result={'estimate':{'skill':{'name':entry['levels'][scenario['skill_rank']-1]['name'],
                'total_damage':None,'total_healing':None},'complete':False,'notes':['合成主结果，仅验证适配器归属。']},
                'components':[{'name':'合成归属分项','owner':scenario['operator']}],
                'complete_definition':'synthetic adapter contract only',
                'panel_native_finalization':{'source_valid':False,'fields':[],
                    'synthetic_identity':{'operator':scenario['operator'],'skill':scenario['skill']}}}
            if returned is not None:returned.append(result)
            return result
        return calculate

    def test_01_public_legacy_default_still_nine_with_three_identities(self):
        c=self.calibration;calls=[];payload=self.view.public_payload('calibration','skills')
        with patch.object(c,'calculate_damage',side_effect=self.fake_calculator(calls)):
            result=c.skill_matrix(**payload)
        self.assertEqual(result['selection_mode'],'legacy_first_three')
        self.assertEqual(len(result['rows']),9)
        self.assertEqual([r['operator_key'] for r in result['rows']],
            ['kaltsit']*3+['silverash']*3+['mechanist']*3)
        self.assertEqual(result['selected_operator']['key'],'mechanist')
        self.assertEqual(len(calls),9)
        self.assertTrue(all(r['name'] and r['identity']['skill_id']==r['skill_id'] for r in result['rows']))
        self.assertTrue(all(r['full_skill_damage'] in (None,0) and r['full_skill_healing'] in (None,0)
                            and not r['native_verified'] and not r['native_clock_verified'] for r in result['rows']))

    def test_02_all_twenty_nine_extended_owners_route_all_seventy_eight_skills_to_self(self):
        c=self.calibration;calls=[];results=[];catalog=c.catalog()['operators']
        with patch.object(c,'calculate_damage',side_effect=self.fake_calculator(calls)):
            for op,profile in catalog.items():
                if op in c.OPERATORS:continue
                scenario={'operator':op};before=deepcopy(scenario)
                result=c.skill_matrix(scenario);results.append(result)
                self.assertEqual(scenario,before)
                self.assertEqual(result['selection_mode'],'current_operator')
                self.assertEqual(result['selected_operator'],{'key':op,'id':profile['id'],'name':profile['name']})
                self.assertEqual([r['skill'] for r in result['rows']],list(range(1,len(profile['skills'])+1)))
                self.assertTrue(all(r['operator_key']==op and r['operator_id']==profile['id'] for r in result['rows']))
                self.assertTrue(all(r['full_skill_damage'] is None and r['full_skill_healing'] is None for r in result['rows']))
        self.assertEqual(len(results),29)
        self.assertEqual(sum(len(r['rows']) for r in results),78)
        self.assertEqual(len(calls),78)
        self.assertTrue(all(s['level']==catalog[s['operator']]['phases'][2]['max_level'] for s in calls))

    def test_03_matrix_copies_corresponding_main_native_and_special_components(self):
        c=self.calibration;calls=[];returned=[]
        with patch.object(c,'calculate_damage',side_effect=self.fake_calculator(calls,returned)):
            result=c.skill_matrix({'operator':MYRTLE},operators=[MYRTLE])
        self.assertEqual(result['selection_mode'],'explicit_current_operator')
        for row,main in zip(result['rows'],returned):
            self.assertEqual(row['native_panel_reference'],main['panel_native_finalization'])
            self.assertIsNot(row['native_panel_reference'],main['panel_native_finalization'])
            self.assertEqual(row['declared_components'],main['components'])
            row['native_panel_reference']['synthetic_identity']['skill']=99
            self.assertNotEqual(main['panel_native_finalization']['synthetic_identity']['skill'],99)

    def test_04_locked_skills_keep_names_reasons_and_never_call_calculate(self):
        c=self.calibration;calls=[]
        with patch.object(c,'calculate_damage',side_effect=self.fake_calculator(calls)):
            result=c.skill_matrix({'operator':SHU,'elite':0,'skill_rank':7})
        self.assertEqual([s['skill'] for s in calls],[1])
        locked=result['rows'][1:]
        self.assertEqual([r['skill'] for r in locked],[2,3])
        self.assertTrue(all(r['name'] and not r['unlocked'] and r['unlock_reasons'] and
            r['status']=='培养条件未开放' and r['native_panel_reference'] is None and
            r['full_skill_damage'] is None and r['full_skill_healing'] is None for r in locked))
        with patch.object(c,'calculate_damage',side_effect=AssertionError('Locked skill calculated')):
            all_locked=c.skill_matrix({'operator':SHU,'elite':1,'skill_rank':10})
        self.assertTrue(all(not r['unlocked'] and any('专精' in reason for reason in r['unlock_reasons']) for r in all_locked['rows']))

    def test_05_extended_cross_owner_conditions_and_malformed_selector_are_rejected(self):
        c=self.calibration
        for scenario,operators in (({'operator':MYRTLE},['kaltsit']),
            ({'operator':MYRTLE},[MYRTLE,'kaltsit']),
            ({'operator':'mechanist'},['mechanist',MYRTLE]),
            ({'operator':MYRTLE},MYRTLE),({'operator':MYRTLE},[]),
            ({'operator':MYRTLE},[False]),({'operator':MYRTLE},['unknown'])):
            with self.subTest(operators=operators),self.assertRaises(ValueError):
                c.skill_matrix(scenario,operators=operators)
        for rank in (0,True,11):
            with self.subTest(rank=rank),self.assertRaises(ValueError):
                c.skill_matrix({'operator':SHU,'elite':0,'skill_rank':rank})

    def test_06_first_three_explicit_subset_retains_its_existing_owner_isolation(self):
        c=self.calibration;calls=[]
        scenario={'operator':'mechanist','module_id':'uniequip_002_mcnist','module_level':3,
                  'charge_count':2,'companion_attack':123}
        with patch.object(c,'calculate_damage',side_effect=self.fake_calculator(calls)):
            result=c.skill_matrix(scenario,operators=['mechanist','silverash'])
        self.assertEqual(result['selection_mode'],'explicit_first_three')
        self.assertEqual(len(result['rows']),6)
        own=[s for s in calls if s['operator']=='mechanist'];other=[s for s in calls if s['operator']=='silverash']
        self.assertTrue(all(s['module_id']==scenario['module_id'] and s['charge_count']==2 for s in own))
        self.assertTrue(all('module_id' not in s and 'charge_count' not in s and 'companion_attack' not in s for s in other))

    def test_07_actual_extended_four_layers_copy_main_and_pair_context_is_still_strict(self):
        c=self.calibration;calculate=c.calculate_damage;captured=[]
        def spy(s):
            result=calculate(s);captured.append(result);return result
        scenario={'operator':MYRTLE,'skill':1};before=deepcopy(scenario)
        with patch.object(c,'calculate_damage',side_effect=spy):
            layers=c.panel_layers(scenario)
        self.assertEqual(len(captured),1)
        self.assertEqual(scenario,before)
        self.assertEqual(list(layers['panels']),['培养与模组','藏品与分队符文写回','已覆盖常态天赋与效果','技能期间参考'])
        self.assertEqual(layers['operator_key'],MYRTLE)
        self.assertEqual(layers['native_panel_reference'],captured[0]['panel_native_finalization'])
        self.assertIsNot(layers['native_panel_reference'],captured[0]['panel_native_finalization'])
        observation={'context_token':layers['context_token'],'panel':'培养与模组',
            'evidence_kind':'formula_reference','source':'本测试仅声明同条件公式参考，非游戏观察。',
            'values':{'attack':layers['panels']['培养与模组']['attack']}}
        compared=c.compare_panel(scenario,observation)
        self.assertTrue(compared['all_compared_values_match'])
        self.assertFalse(compared['native_verified'])
        with self.assertRaisesRegex(ValueError,'条件不一致'):
            c.compare_panel({**scenario,'potential':2},observation)

    def test_08_actual_deepcolor_skill_unknown_is_preserved_with_main_components(self):
        c=self.calibration;calculate=c.calculate_damage;captured=[]
        def spy(s):
            result=calculate(s);captured.append(result);return result
        with patch.object(c,'calculate_damage',side_effect=spy):
            result=c.skill_matrix({'operator':DEEP})
        self.assertEqual(len(captured),2)
        for row,main in zip(result['rows'],captured):
            self.assertEqual(row['native_panel_reference'],main['panel_native_finalization'])
            self.assertEqual(row['declared_components'],main['components'])
            skill_attack=next(r for r in row['native_panel_reference']['fields'] if r['phase']=='skill' and r['field']=='attack')
            self.assertFalse(skill_attack['conditional_complete'])
            self.assertIsNone(row['full_skill_damage']);self.assertIsNone(row['full_skill_healing'])

    def test_09_other_worksheets_remain_first_three_and_internal_fields_are_not_accepted(self):
        c=self.calibration
        for function in (c.cultivation_curve,c.module_stages,c.talent_states,c.animation_events):
            with self.subTest(function=function.__name__),self.assertRaisesRegex(ValueError,'首批三名'):
                function({'operator':MYRTLE})
        for function in (c.panel_layers,c.skill_matrix):
            with self.subTest(function=function.__name__),self.assertRaisesRegex(ValueError,'内部字段'):
                function({'operator':MYRTLE,'_panel_native_skill_qualification':{'attack':True}})

    def test_10_chinese_renderer_names_locked_skills_and_separates_conditional_native_values(self):
        c=self.calibration;v=self.view
        locked=c.skill_matrix({'operator':SHU,'elite':0,'skill_rank':7})
        text=v.render_offline_result('calibration','skills',locked)
        self.assertIn('全部技能与条件分项',text)
        self.assertIn('当前条件归属：黍',text)
        for row in locked['rows']:
            self.assertIn(row['name'],text)
            for reason in row['unlock_reasons']:self.assertIn(reason,text)
        self.assertIn('对应主结果 · 技能攻击与攻速',text)
        self.assertIn('此项不等于原生完整总量',text)
        self.assertIn('完整原生面板与实际技能时钟仍未知',text)
        self.assertEqual(len(v.QUERIES['calibration']),27)


class ExtendedCalibrationImport285Tests(unittest.TestCase):
    view=None

    @classmethod
    def setUpClass(cls):
        if cls.view is None:
            _,cls.view=load_subjects()
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])

    def setUp(self):self.panel=self.view.OfflineToolsPanel()
    def tearDown(self):
        self.panel.close();self.panel.deleteLater();self.app.processEvents()

    def test_11_skills_explicit_import_always_restricts_to_current_owner_and_preserves_cached_edit(self):
        self.panel.select_query('calibration','skills')
        for op in (MYRTLE,'silverash'):
            before=self.panel.editor.toPlainText()
            self.panel.set_scenario({'operator':op,'skill':1,'_private_marker':'must not import'})
            self.assertEqual(self.panel.editor.toPlainText(),before)
            self.panel._import_scenario()
            payload=json.loads(self.panel.editor.toPlainText())
            self.assertEqual(payload['operators'],[op])
            self.assertEqual(payload['scenario']['operator'],op)
            self.assertNotIn('_private_marker',payload['scenario'])

    def test_12_extended_panel_and_pair_import_preserve_observation_but_legacy_query_rejects(self):
        self.panel.set_scenario({'operator':MYRTLE,'skill':1})
        self.panel.select_query('calibration','panel');self.panel._import_scenario()
        self.assertEqual(json.loads(self.panel.editor.toPlainText())['scenario']['operator'],MYRTLE)
        self.panel.select_query('calibration','pair')
        before=deepcopy(json.loads(self.panel.editor.toPlainText())['observation'])
        self.panel._import_scenario();payload=json.loads(self.panel.editor.toPlainText())
        self.assertEqual(payload['scenario']['operator'],MYRTLE)
        self.assertEqual(payload['observation'],before)
        with self.assertRaisesRegex(ValueError,'条件不一致'):
            self.view.run_offline_query('calibration','pair',payload)
        self.panel.select_query('calibration','cultivation');text=self.panel.editor.toPlainText()
        self.panel._import_scenario()
        self.assertEqual(self.panel.editor.toPlainText(),text)
        self.assertIn('仅支持',self.panel.status.text())


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--draft-root',type=Path)
    arguments,remaining=parser.parse_known_args()
    DRAFT_ROOT=arguments.draft_root
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    unittest.main(argv=[sys.argv[0],*remaining])
