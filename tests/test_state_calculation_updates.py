"""Real UI state-to-calculation updates; public fixtures and temporary files only."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

import numpy as np
from PySide6.QtWidgets import QApplication
from rouge import app as module, public_archive, public_node_statistics
from rouge.run_state import RunState
from rouge.ui_state import calculation_batch


def observation():
    fields = {'elite': 1, 'level': 80, 'potential': 1, 'trust': 100,
              'module_id': None, 'module_level': 0, 'selected_skill': 1}
    return {'operators': [{'id': 'mechanist', 'scope': 'run', 'fields': fields,
                          'skill_ranks': {'1': 7}, 'present': True}],
            'selected_operator': 'mechanist',
            'relics': {'ids': [], 'icons': [], 'count': 0, 'source': 'held_bar'},
            'config': {'difficulty': {'value': 10, 'source': 'label'}}}


class StateCalculationUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        folder = self.enterContext(TemporaryDirectory(prefix='rouge-state-update-test-'))
        root = Path(folder)
        for key, path in {'ROOT': root, 'SETTINGS': root/'settings.json',
                          'RUN_STATE': root/'run.json', 'OPERATOR_STATE': root/'account.json'}.items():
            self.enterContext(patch.object(module, key, path))
        backend = module.DesktopBackend
        self.enterContext(patch.object(module, 'DesktopBackend', lambda _p, cb: backend(root/'chat', cb)))
        self.enterContext(patch.object(module, 'list_game_windows', return_value=[]))
        self.forbidden = []

        def fail(name):
            def called(*args, **kwargs):
                self.forbidden.append(name)
                raise AssertionError(name)
            return called

        for name in ('connect', 'capture', 'next_frame'):
            self.enterContext(patch.object(module.GameCapture, name, side_effect=fail(name)))
        for name in ('start', 'request'):
            self.enterContext(patch.object(backend, name, side_effect=fail('desktop_'+name)))
        for owner, name in ((module, 'stream_chat'), (module, 'read_key'),
                            (public_archive, 'fetch'), (public_node_statistics, 'fetch')):
            self.enterContext(patch.object(owner, name, side_effect=fail(name)))
        self.window = module.MainWindow()
        self.window.select_operator('mechanist')
        self.window.run.state['started_at'] = 1000
        self.window.run.state['id'] = 'public-state-update-test'
        self.addCleanup(self.assertEqual, self.forbidden, [])
        self.addCleanup(self.window.close)

    def test_run_update_calculates_final_inputs_once_before_return(self):
        incoming = observation()
        before = deepcopy(incoming)
        with patch.object(module, 'calculate_damage', wraps=module.calculate_damage) as calculate:
            self.assertTrue(self.window.apply_run_observation(incoming, 1001))
        self.assertEqual(calculate.call_count, 1)
        self.assertEqual(incoming, before)
        scenario = self.window.damage_result['scenario']
        self.assertEqual((scenario['operator'], scenario['elite'], scenario['level'], scenario['skill_rank']),
                         ('mechanist', 1, 80, 7))
        self.assertEqual(scenario['run_config']['difficulty']['value'], 10)
        self.assertEqual(scenario['relic_ids'], [])
        self.assertIn('机械师', self.window.damage_text.toPlainText())

    def test_manual_level_skill_and_browsing_survive_repeated_input(self):
        w = self.window
        w.apply_run_observation(observation(), 1001)
        w.level.setValue(75)
        w.skill.setCurrentIndex(w.skill.findData(2))
        incoming = observation()
        incoming['operators'][0]['fields']['level'] = 72
        with patch.object(module, 'calculate_damage', wraps=module.calculate_damage) as calculate:
            w.apply_run_observation(incoming, 1002)
        self.assertEqual(calculate.call_count, 1)
        self.assertEqual((w.level.value(), w.skill.currentData()), (75, 2))
        self.assertEqual(w.damage_result['scenario']['level'], 75)
        self.assertEqual(w.run.state['operators']['mechanist']['fields']['level'], 72)
        # The existing E1 preview is rank7, explicitly unconfirmed. It is not
        # evidence that reading S1 confirmed S2's cultivation.
        self.assertEqual(w.damage_result['scenario']['skill_rank'], 7)
        self.assertFalse(w.skill_rank_selection()['known'])
        self.assertNotIn('2', w.run.state['operators']['mechanist']['skill_ranks'])
        w.select_operator('silverash')
        with patch.object(module, 'calculate_damage', wraps=module.calculate_damage) as calculate:
            w.apply_run_observation(incoming, 1003)
        self.assertEqual(calculate.call_count, 1)
        self.assertEqual(w.operator.currentData(), 'silverash')
        self.assertEqual(w.damage_result['scenario']['operator'], 'silverash')

    def test_one_frame_combines_run_and_account_without_intermediate_calculation(self):
        incoming = observation()
        account = {'id': 'mechanist', 'scope': 'operator_profile',
                   'fields': {**incoming['operators'][0]['fields'], 'elite': 2, 'level': 90},
                   'skill_ranks': {'1': 10}}
        frame = {'captured_at': 1001, 'page': 'operator_detail', 'nodes': [],
                 'run': incoming, 'operator': account}
        with patch.object(module, 'calculate_damage', wraps=module.calculate_damage) as calculate:
            self.window.sample_received((np.zeros((64, 96, 3), dtype=np.uint8), frame))
        self.assertEqual(calculate.call_count, 1)
        self.assertEqual(self.window.damage_result['scenario']['level'], 80)
        self.assertEqual(self.window.damage_result['scenario']['skill_rank'], 7)
        self.assertEqual(self.window.account_cache.view('mechanist')['fields']['level'], 90)
        self.assertIn('界面更新', self.window.capture_status.text())

    def test_restart_uses_saved_state_and_only_manual_reset_clears_it(self):
        w = self.window
        w.apply_run_observation(observation(), 1001)
        raw = Path(w.run.file).read_bytes()
        before = deepcopy(w.run.state)
        w.run = RunState(w.run.file)
        w.update_operator()
        self.assertEqual(w.run.state['id'], before['id'])
        self.assertEqual(w.run.state['operators'], before['operators'])
        self.assertEqual(w.run.state['config'], before['config'])
        self.assertEqual(Path(w.run.file).read_bytes(), raw)
        self.assertEqual(w.damage_result['scenario']['level'], 80)
        old_id = w.run.state['id']
        w.reset_run()  # Temporary fixture only, never the user's actual run.
        self.assertNotEqual(w.run.state['id'], old_id)
        self.assertEqual(w.run.state['operators'], {})
        self.assertEqual(w.run.state['config'], {})
        with patch.object(module, 'calculate_damage', wraps=module.calculate_damage) as calculate:
            self.assertFalse(w.apply_run_observation(observation(), 1002))
        self.assertEqual(calculate.call_count, 0)

    def test_failed_nested_update_releases_batch_and_direct_controls_still_work(self):
        w = self.window
        w.apply_run_observation(observation(), 1001)
        previous = w.damage_result
        with patch.object(module, 'calculate_damage', wraps=module.calculate_damage) as calculate:
            with self.assertRaisesRegex(ValueError, 'public failure'):
                with calculation_batch(w):
                    with calculation_batch(w):
                        w.level.setValue(74)
                    raise ValueError('public failure')
            self.assertEqual(calculate.call_count, 0)
            self.assertIs(w.damage_result, previous)
            self.assertEqual(w._calculation_batch_depth, 0)
            self.assertFalse(w._calculation_requested)
            w.level.setValue(73)
        self.assertEqual(calculate.call_count, 1)
        self.assertEqual(w.damage_result['scenario']['level'], 73)

    def test_relic_ui_uses_one_current_held_collection_for_all_checkboxes(self):
        w = self.window
        w.apply_run_observation(observation(), 1001)
        with patch.object(w.run, 'held_relic_ids', wraps=w.run.held_relic_ids) as held:
            with patch.object(w, 'calculate') as calculate:
                w.sync_run_relics()
        self.assertEqual(held.call_count, 1)
        self.assertEqual(calculate.call_count, 1)
        self.assertTrue(all(w.relic_list.item(i).checkState() == module.Qt.CheckState.Unchecked
                            for i in range(w.relic_list.count())))


if __name__ == '__main__':
    unittest.main()
