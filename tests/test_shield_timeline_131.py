import unittest
from copy import deepcopy
from rouge.shield_timeline import compare_shield_windows, format_shield_windows
from rouge.damage import calculate_damage

BASE={'operator':'mechanist','skill':2,'base_attack':1000,'skill_duration_seconds':20}
def event(source,broke,hit):return {'source':source,'break_seconds':broke,'hit_seconds':hit}

class ShieldTimelineTests(unittest.TestCase):
    def test_unsorted_and_repeated_windows_reuse_each_break_and_model(self):
        from unittest.mock import patch
        from rouge import shield_timeline as model
        events = [event('structure', 3, 6), event('owner', 0, None), event('owner', 2, 2)]
        windows = [6, 2, 6, 0, 4]
        independent = [compare_shield_windows(BASE, {'events': events, 'windows_seconds': [w]})['rows'][0]
                       for w in windows]
        budget = model.BarrierAmmoProjection(8)
        with patch.object(model, 'BarrierAmmoProjection', return_value=budget), patch.object(
                budget, 'barrier_break', wraps=budget.barrier_break) as applied, patch.object(
                model, 'calculate_damage', wraps=calculate_damage) as calculate:
            rows = compare_shield_windows(BASE, {'events': events, 'windows_seconds': windows})['rows']
        self.assertEqual(rows, independent)
        self.assertEqual(applied.call_count, 3)
        self.assertEqual(calculate.call_count, 1 + len(set(windows)))
        rows[0]['ammunition_budget_reference']['source_counts']['owner'] = 999
        self.assertEqual(rows[2], independent[2])

    def test_player_input_and_internal_calculator_error_take_different_paths(self):
        import json
        from unittest.mock import patch
        from PySide6.QtWidgets import QApplication, QWidget
        from rouge import shield_timeline as model
        from rouge.app import MainWindow
        qt = QApplication.instance() or QApplication([])
        owner = QWidget()
        self.addCleanup(owner.close)
        owner.damage_result = {'scenario': BASE}
        MainWindow.show_shield_timeline(owner)
        dialog = owner.shield_timeline_dialog
        self.assertIsNotNone(dialog.result)
        data = {'events': [event('owner', 2, 1)], 'windows_seconds': [2]}
        dialog.editor.setPlainText(json.dumps(data))
        dialog.calculate()
        self.assertIsNone(dialog.result)
        self.assertIn('命中不能早于', dialog.notice.toPlainText())
        data['events'].clear()
        dialog.editor.setPlainText(json.dumps(data))
        with patch.object(model, 'calculate_damage', side_effect=ValueError('internal model error')):
            with self.assertRaisesRegex(ValueError, 'internal model error'):
                dialog.calculate()
        qt.processEvents()

    def test_breaks_collisions_sources_and_boundary(self):
        preview={'events':[event('owner',1,2),event('structure',1,2),event('owner',2,None),event('structure',3,4)],'windows_seconds':[0,2,3,4,5]}
        result=compare_shield_windows(BASE,preview)
        self.assertEqual([r['explosion_damage_reference'] for r in result['rows']],[0,0,10000,10000,15000])
        self.assertEqual(result['rows'][2]['declared_breaks'],3)
        self.assertEqual((result['rows'][2]['owner_hits'],result['rows'][2]['structure_hits']),(1,1))
        self.assertIsNone(result['actual_end_seconds']);self.assertIsNone(result['actual_ammunition_consumption'])

    def test_no_ammo_cap_or_inferred_end(self):
        result=compare_shield_windows(BASE,{'events':[event('owner',i,i) for i in range(10)],'windows_seconds':[30]})
        self.assertEqual(result['rows'][0]['owner_hits'],10)
        self.assertEqual(result['nominal_ammunition_parameter'],8)
        self.assertIsNone(result['full_cast_damage']); self.assertIsNone(result['cycle_damage'])
        self.assertIn('实际结束',format_shield_windows(result))

    def test_preserves_original_ordinary_and_inputs(self):
        scenario={**BASE,'shield_break_count':5};preview={'events':[],'windows_seconds':[5,20]}
        before=deepcopy((scenario,preview));result=compare_shield_windows(scenario,preview)
        for row in result['rows']:
            ordinary=calculate_damage({**scenario,'shield_break_count':0,'window_seconds':row['window_seconds']})['estimate']['skill']['window_damage']
            self.assertEqual(row['ordinary_damage_reference'],ordinary)
        self.assertEqual((scenario,preview),before)

    def test_resistance_applies_to_explosions(self):
        result=compare_shield_windows({**BASE,'enemy_resistance':50}, {'events':[event('owner',0,1)],'windows_seconds':[2]})
        self.assertEqual(result['rows'][0]['explosion_damage_reference'],2500)

    def test_invalid_declarations(self):
        for events in ([event('owner',2,1)],[event('other',0,1)],[event('owner',True,1)],[event('owner',0,float('nan'))],[{}],[event('owner',0,1)]*101):
            with self.assertRaises(ValueError):compare_shield_windows(BASE,{'events':events,'windows_seconds':[10]})
        for windows in ([],[True],[-1],[3601],[1]*13):
            with self.assertRaises(ValueError):compare_shield_windows(BASE,{'events':[],'windows_seconds':windows})
        with self.assertRaises(ValueError):compare_shield_windows({**BASE,'skill':3},{'events':[],'windows_seconds':[10]})
