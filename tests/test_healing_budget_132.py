import unittest
from copy import deepcopy
from rouge.healing_budget import healing_budget, healing_sources, format_healing_budget
from rouge.damage import calculate_damage

BASE={'operator':'char_196_sunbr','skill':1,'base_attack':1000}
def preview():return {'recipients':[{'id':'甲','max_hp':3000,'hp':2000},{'id':'乙','max_hp':2000,'hp':500}], 'events':[]}
def heal(friend='甲',time=1):return {'recipient':friend,'at_seconds':time,'kind':'heal','source':'healing_0'}

class HealingBudgetTests(unittest.TestCase):
    def test_player_dialog_uses_opening_snapshot_and_only_reports_input_errors(self):
        import json
        from unittest.mock import patch
        from PySide6.QtWidgets import QApplication, QWidget
        from rouge.app import MainWindow
        from rouge import healing_budget as model
        qt = QApplication.instance() or QApplication([])
        owner = QWidget()
        self.addCleanup(owner.close)
        owner.damage_result = {'scenario': deepcopy(BASE), 'result': calculate_damage(BASE)}
        data = preview()
        data['events'] = [heal()]
        expected = healing_budget(BASE, data)
        with patch.object(model, 'calculate_damage', side_effect=AssertionError('repeat calculation')):
            MainWindow.show_healing_budget(owner)
            dialog = owner.healing_budget_dialog
            owner.damage_result.clear()
            dialog.editor.setPlainText(json.dumps(data))
            dialog.calculate()
            self.assertEqual(dialog.result, expected)
            data['events'][0]['at_seconds'] = -1
            dialog.editor.setPlainText(json.dumps(data))
            dialog.calculate()
            self.assertIsNone(dialog.result)
            self.assertIn('3600', dialog.notice.toPlainText())
            dialog.editor.setPlainText('{')
            dialog.calculate()
            self.assertIn('JSON', dialog.notice.toPlainText())
            dialog.editor.setPlainText(json.dumps(preview()))
            for error in (ValueError, TypeError, KeyError):
                with self.subTest(error=error.__name__), patch.object(dialog, 'evaluator', side_effect=error('internal')):
                    with self.assertRaises(error):
                        dialog.calculate()
        qt.processEvents()

    def test_individual_caps_effective_and_overheal(self):
        data=preview();data['events']=[heal(),heal('乙')]
        result=healing_budget(BASE,data)
        self.assertEqual(result['effective_healing'],2500);self.assertEqual(result['overhealing'],700)
        self.assertEqual([r['hp_after'] for r in result['rows']],[3000,2000])
        self.assertFalse(result['actual_acquisition_verified'])

    def test_order_loss_then_heal_and_equal_times(self):
        data=preview();data['events']=[{'recipient':'甲','at_seconds':2,'kind':'loss','amount':800},heal(time=2),heal(time=1)]
        result=healing_budget(BASE,data)
        self.assertEqual([r['input_order'] for r in result['rows']],[2,0,1])
        self.assertEqual(result['recipients'][0]['hp'],3000)
        self.assertEqual(result['recipients'][0]['effective_healing'],1800)

    def test_fixed_relic_heal_reference_and_unknown_acquisition(self):
        data=preview();data['events']=[heal()]
        result=healing_budget({**BASE,'relic_ids':['rogue_6_relic_legacy_81']},data)
        self.assertEqual(result['sources'][0]['per_heal_reference'],1920)
        self.assertIsNone(calculate_damage(BASE)['total_healing'])
        self.assertIn('实际机制待核验',format_healing_budget(result))

    def test_multiple_sources_not_combined_with_regeneration(self):
        raw=calculate_damage({'operator':'char_4202_haruka','skill':2,'base_attack':1000})
        self.assertEqual(len(healing_sources(raw)),2)
        self.assertEqual(healing_sources({'components':[{'damage_type':'regeneration','per_hit':100}]}),[])
        self.assertEqual(healing_sources({'per_heal':float('inf')}),[])
        with self.assertRaises(ValueError):healing_budget({'operator':'mechanist','skill':3},preview())

    def test_no_events_no_mutation_and_legacy_source(self):
        data=preview();saved=deepcopy((BASE,data));result=healing_budget(BASE,data)
        self.assertEqual(result['effective_healing'],0);self.assertEqual((BASE,data),saved)
        legacy=healing_sources(calculate_damage({'operator':'kaltsit','skill':1}));self.assertEqual(legacy[0]['id'],'legacy_heal')

    def test_invalid_recipient_and_event(self):
        for maximum,hp in ((0,0),(100,101),(True,1),(100,float('nan'))):
            data=preview();data['recipients'][0].update(max_hp=maximum,hp=hp)
            with self.assertRaises(ValueError):healing_budget(BASE,data)
        data=preview();data['recipients'][1]['id']='甲'
        with self.assertRaises(ValueError):healing_budget(BASE,data)
        for event in (heal('丙'),{**heal(),'source':'damage_0'},{**heal(),'at_seconds':True},{'kind':'loss','recipient':'甲','at_seconds':0,'amount':-1}):
            data=preview();data['events']=[event]
            with self.assertRaises(ValueError):healing_budget(BASE,data)
