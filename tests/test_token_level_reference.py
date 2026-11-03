import hashlib
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import unittest

from rouge.token_level_reference import (interpolate_field, token_modules_by_host_level,
    native_source, format_token_level_reference)
from rouge.p2_supplemental_token_modules import source_data

L = 'char_2023_ling'; M = 'char_248_mgllan'


class TokenLevelReferenceTests(unittest.TestCase):
    def test_midlevel_literal_and_module_then_form_layer(self):
        r = token_modules_by_host_level(L, {'elite': 2, 'level': 60}, 10)
        v = r['variants'][2]
        numeric = next(x for x in v['branches'] if x['branch'] == 'numeric_lerp')
        self.assertEqual(tuple(numeric['stages'][0]['values'][k] for k in ('hp','attack','defense')), (3473,792,407))
        self.assertEqual(tuple(numeric['stages'][3]['values'][k] for k in ('hp','attack','defense')), (3723,852,407))
        f = next(x for x in r['ling_forms'] if x['module_level']==3 and x['cultivation_branch']=='numeric_lerp'
                 and x['form']=='advanced' and x['skill_active_declared'])
        self.assertEqual(f['values']['hp'],7446)
        self.assertAlmostEqual(f['values']['attack'],2385.6)
        self.assertAlmostEqual(f['values']['defense'],1139.6)
        self.assertEqual(len(v['branches']),8)
        self.assertEqual(len(r['ling_forms']),128)
        self.assertTrue(all(x['actual_current_panel'] is None for x in r['ling_forms']))

    def test_every_legal_level_matches_independent_rational_integer_oracle(self):
        raw = source_data()
        for operator in (L,M):
            for elite,max_level in enumerate((50,80,90)):
                for level in range(1,max_level+1):
                    r = token_modules_by_host_level(operator, {'elite':elite,'level':level})
                    for variant,record in zip(r['variants'],raw['operators'][operator]['variants']):
                        frames=record['token_raw']['phases'][elite]['attributesKeyFrames'];a,b=frames[0],frames[-1]
                        branch=next(x for x in variant['branches'] if x['branch']=='numeric_lerp')
                        for field,key in [('hp','maxHp'),('attack','atk'),('defense','def')]:
                            exact=Fraction(a['data'][key])+Fraction((level-a['level'])*(b['data'][key]-a['data'][key]),b['level']-a['level'])
                            self.assertEqual(branch['traces'][field]['value'],round(exact))
                            if variant['skill_qualified']:
                                self.assertEqual(branch['stages'][0]['values'][field],round(exact))
                            else:
                                self.assertIsNone(branch['stages'][0]['values'][field])
                    self.assertIsNone(r['full_current_panel'])

    def test_independent_mixed_flags_are_kept_not_only_two_uniform_panels(self):
        r=token_modules_by_host_level(L,{'elite':2,'level':60})
        v=r['variants'][2]
        mixed=next(x for x in v['branches'] if x['keep_lower_declared_for_varying_fields']=={'hp':True,'attack':False,'defense':True})
        self.assertEqual(tuple(mixed['stages'][0]['values'][k] for k in ('hp','attack','defense')),(3210,792,376))
        self.assertIsNone(v['actual_keep_lower_flags'])
        self.assertIn('not_actual_distribution',v['combination_scope'])
        self.assertIsNone(mixed['traces']['hp']['product_single'])
        endpoint=token_modules_by_host_level(L,{'elite':2,'level':1})
        self.assertEqual(len(endpoint['variants'][2]['branches']),1)

    def test_explicit_rounding_and_single_precision_loss_differ_from_naive_math(self):
        self.assertEqual(interpolate_field(0,1,.5,integer=True,keep_lower=False)['value'],0)
        self.assertEqual(interpolate_field(1,2,.5,integer=True,keep_lower=False)['value'],2)
        self.assertEqual(interpolate_field(2,3,.5,integer=True,keep_lower=False)['value'],2)
        x=interpolate_field(100000000,100000008,.5,integer=True,keep_lower=False)
        self.assertEqual(x['value'],100000000)
        self.assertNotEqual(x['value'],100000004)

    def test_magallan_zero_attack_and_module_stats_remain_independent(self):
        r=token_modules_by_host_level(M,{'elite':2,'level':60})
        zero=r['variants'][0];self.assertEqual(len(zero['branches']),1)
        self.assertEqual(zero['branches'][0]['stages'][0]['values']['attack'],0)
        self.assertEqual(zero['branches'][0]['stages'][3]['values']['attack_speed'],100)
        self.assertEqual(r['variants'][1]['branches'][0]['stages'][3]['values']['attack_speed'],103)
        self.assertEqual(r['ling_forms'],[])
        self.assertEqual(len(r['variants'][1]['branches']),2)

    def test_missing_training_and_locked_host_never_borrow_max_or_module(self):
        for training in ({},{'elite':2},{'elite':2,'level':None},{'elite':True,'level':90},{'elite':2,'level':True}):
            with self.subTest(training=training),self.assertRaises(ValueError):token_modules_by_host_level(L,training)
        r=token_modules_by_host_level(L,{'elite':1,'level':50})
        self.assertTrue(all(v is None for b in r['variants'][2]['branches'] for s in b['stages'] for v in s['values'].values()))
        r=token_modules_by_host_level(L,{'elite':2,'level':59})
        self.assertTrue(all(v is None for b in r['variants'][0]['branches'] for s in b['stages'][1:] for v in s['values'].values()))

    def test_source_binding_rejects_old_pair_and_keeps_flags_unknown(self):
        d=native_source();self.assertEqual(d['metadata_record_size'],92)
        self.assertEqual(d['unique_instruction_count'],1006)
        self.assertEqual(d['dll_sha256'],'583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5')
        self.assertIsNone(d['actual_keep_lower_value_flags'])
        self.assertFalse(d['current_hotfix_equivalence_proven'])
        for file,expected in d['retained_source_sha256'].items():
            self.assertEqual(hashlib.sha256(Path(file).read_bytes()).hexdigest(),expected)
        for name in ['hp','attack','defense','deployment_cost','block']:self.assertTrue(d['fields'][name]['integer_write'])
        for name in ['resistance','attack_speed','base_interval']:self.assertFalse(d['fields'][name]['integer_write'])

    def test_invalid_math_and_inputs_are_preserved(self):
        for alpha in (True,None,-.1,1.1,float('nan'),float('inf')):
            with self.subTest(alpha=alpha),self.assertRaises(ValueError):interpolate_field(1,2,alpha,keep_lower=False)
        with self.assertRaises(TypeError):interpolate_field(1,2,.5)
        with self.assertRaises(ValueError):interpolate_field(1,2,.5,keep_lower=None)
        training={'elite':2,'level':60,'trust':0,'potential':6};before=deepcopy(training)
        r=token_modules_by_host_level(L,training);self.assertEqual(training,before)
        plain=token_modules_by_host_level(L,{'elite':2,'level':60,'trust':100,'potential':1})
        self.assertEqual(r['variants'],plain['variants'])
        text=format_token_level_reference(r)
        self.assertIn('逐属性混合条件',text);self.assertIn('完整当前面板',text)


class TokenLevelViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.app=QApplication.instance() or QApplication([])

    def test_host_mode_uses_captured_training_hides_endpoint_controls_and_keeps_forms(self):
        from rouge.p2_supplemental_token_module_view import SupplementalTokenModuleDialog
        w=SupplementalTokenModuleDialog(L,{'elite':2,'level':60})
        try:
            w.show();self.app.processEvents()
            w.cultivation_mode.setCurrentIndex(w.cultivation_mode.findData('host_level'))
            self.assertFalse(w.phase.isVisible());self.assertFalse(w.endpoint.isVisible())
            w.ling_rank.setCurrentIndex(w.ling_rank.findData(10));w.calculate_button.click()
            self.assertIsNotNone(w.level_result);self.assertEqual(w.table.rowCount(),96)
            self.assertEqual(w.ling_forms.rowCount(),128)
            self.assertIn('等级60',w.qualification.text())
            self.assertIn('逐属性混合条件',w.details.toPlainText())
            w.cultivation_mode.setCurrentIndex(0)
            self.assertIsNone(w.level_result);self.assertEqual(w.table.rowCount(),0)
            self.assertTrue(w.phase.isVisible());self.assertEqual(w.training['level'],60)
        finally:w.close();w.deleteLater();self.app.processEvents()

    def test_magallan_has_no_ling_controls_and_no_missing_level_default(self):
        from rouge.p2_supplemental_token_module_view import SupplementalTokenModuleDialog
        w=SupplementalTokenModuleDialog(M,{'elite':2,'level':None})
        try:
            self.assertFalse(hasattr(w,'ling_rank'))
            w.cultivation_mode.setCurrentIndex(w.cultivation_mode.findData('host_level'));w.calculate_button.click()
            self.assertIsNone(w.level_result);self.assertIn('未读取不能默认满级',w.details.toPlainText())
        finally:w.close();w.deleteLater();self.app.processEvents()


if __name__=='__main__':unittest.main()
