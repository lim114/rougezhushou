import unittest
from copy import deepcopy
from rouge.damage_budget import damage_sources,damage_budget,format_damage_budget
from rouge.damage import calculate_damage


class DamageBudget139Tests(unittest.TestCase):
    scenario={'operator':'mechanist','skill':3,'base_attack':1000}
    def proposal(self):
        return {'targets':[{'id':'甲','hp':1000,'defense':0,'resistance':0},
                           {'id':'乙','hp':10000,'defense':500,'resistance':50}],
                'events':[{'at_seconds':0,'target':'甲','source':'damage_0'},
                          {'at_seconds':0,'target':'甲','source':'damage_1'},
                          {'at_seconds':1,'target':'乙','source':'damage_0'}]}

    def test_budget_sources_skip_only_invalid_amounts_in_both_formats(self):
        from unittest.mock import patch
        from rouge import damage_budget as damage, healing_budget as healing
        for module, sources, field, kind in (
                (damage, damage.damage_sources, 'per_hit', 'physical'),
                (healing, healing.healing_sources, 'per_heal', 'healing')):
            bad = {'damage_type': kind, 'name': '无效', 'per_hit': -1}
            good = {'damage_type': kind, 'name': '有效', 'per_hit': 0}
            with self.subTest(kind=kind):
                self.assertEqual([row['name'] for row in sources({'components': [bad, good]})], ['有效'])
                self.assertEqual(sources({'damage_type': kind, field: -1}), [])
                for data in ({'components': [good]}, {'damage_type': kind, field: 0}):
                    with patch.object(module, '_amount', side_effect=ValueError('internal amount failure')):
                        with self.assertRaisesRegex(ValueError, 'internal amount failure'):
                            sources(data)

    def test_equal_mitigation_shares_calculation_only_within_one_budget(self):
        from unittest.mock import patch
        from rouge import damage_budget as model
        data = self.proposal()
        first, second = data['targets']
        second.update(defense=first['defense'], resistance=first['resistance'])
        with patch.object(model, 'calculate_damage', wraps=calculate_damage) as calculate:
            result = damage_budget(self.scenario, data)
            self.assertEqual(calculate.call_count, 1)
            second['resistance'] = 50
            changed = damage_budget(self.scenario, data)
            self.assertEqual(calculate.call_count, 3)
        self.assertEqual(result['targets'][0], changed['targets'][0])
        self.assertNotEqual(result['targets'][0]['hp'], result['targets'][1]['hp'])
        self.assertNotEqual(result['references']['乙']['sources'], changed['references']['乙']['sources'])
        result['references']['甲']['sources'].clear()
        self.assertTrue(result['references']['乙']['sources'])

    def test_player_dialog_reports_bad_target_and_exposes_calculator_failure(self):
        import json
        from unittest.mock import patch
        from PySide6.QtWidgets import QApplication, QWidget
        from rouge import damage_budget as model
        from rouge.app import MainWindow
        qt = QApplication.instance() or QApplication([])
        owner = QWidget()
        self.addCleanup(owner.close)
        owner.damage_result = {'scenario': self.scenario, 'result': calculate_damage(self.scenario)}
        MainWindow.show_damage_budget(owner)
        dialog = owner.damage_budget_dialog
        self.assertIsNotNone(dialog.result)
        data = self.proposal()
        data['targets'][0]['resistance'] = 101
        dialog.editor.setPlainText(json.dumps(data))
        dialog.calculate()
        self.assertIsNone(dialog.result)
        self.assertIn('抗性', dialog.notice.toPlainText())
        dialog.editor.setPlainText(json.dumps(self.proposal()))
        for error in (ValueError, TypeError, KeyError):
            with self.subTest(error=error.__name__), patch.object(model, 'calculate_damage', side_effect=error('internal')):
                with self.assertRaises(error):
                    dialog.calculate()
        qt.processEvents()

    def test_each_target_recomputed_and_overkill(self):
        p=self.proposal();s=deepcopy(self.scenario);before=deepcopy(p);r=damage_budget(s,p)
        first=r['rows'][0];self.assertEqual(first['effective_damage'],1000);self.assertGreater(first['overkill'],0)
        self.assertEqual(r['rows'][1]['effective_damage'],0)
        expected=calculate_damage({**s,'enemy_resistance':50,'enemy_defense':500})['components'][0]['per_hit']
        self.assertEqual(r['rows'][2]['per_hit'],expected);self.assertEqual(r['targets'][0]['budget_exhausted_at'],0)
        self.assertIsNone(r['actual_kill_time']);self.assertEqual(s,self.scenario);self.assertEqual(p,before)
        self.assertIn('不是实际击杀',format_damage_budget(r))

    def test_order_and_empty_events(self):
        p=self.proposal();p['events'].reverse();r=damage_budget(self.scenario,p)
        self.assertEqual([x['input_order'] for x in r['rows']],[1,2,0])
        p['events']=[];r=damage_budget(self.scenario,p)
        self.assertEqual(r['rows'],[]);self.assertIsNone(r['targets'][0]['budget_exhausted_at'])
        self.assertEqual(r['targets'][0]['hp'],1000)

    def test_target_binding_replaced_without_mutation(self):
        s={**self.scenario,'target_enemy':{'stage_id':'bad'}}
        r=damage_budget(s,self.proposal());self.assertNotIn('target_enemy',r['references']['甲']['scenario'])
        self.assertIn('target_enemy',s)

    def test_healing_and_unknown_not_damage(self):
        self.assertEqual(damage_sources({'components':[{'name':'治疗','damage_type':'healing','per_hit':500},
            {'name':'未知','damage_type':'physical','per_hit':None}]}),[])
        with self.assertRaises(ValueError):damage_budget({'operator':'char_2025_shu','skill':1},self.proposal())

    def test_invalid_inputs(self):
        for path,value in [('hp',0),('hp',True),('defense',-1),('resistance',101),('id','')]:
            p=self.proposal();p['targets'][0][path]=value
            with self.subTest(path=path),self.assertRaises(ValueError):damage_budget(self.scenario,p)
        for key,value in [('at_seconds',True),('source','unknown'),('target','unknown')]:
            p=self.proposal();p['events'][0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):damage_budget(self.scenario,p)
        p=self.proposal();p['targets'].append(deepcopy(p['targets'][0]))
        with self.assertRaises(ValueError):damage_budget(self.scenario,p)
