"""Current quantities flow to persistence, history and readable player chips."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from PySide6.QtWidgets import QApplication
from rouge.run_state import RunState
from rouge.player_resource_facts import resource_rows
from rouge.player_resource_history import resource_rows as history_rows
from rouge.player_floor_resources import snapshots, snapshot_text
from rouge.player_resource_strip import ResourceStrip


class HUDResourceFlow441Tests(unittest.TestCase):
    def setUp(self):
        folder = self.enterContext(TemporaryDirectory(prefix='rouge-hud441-'))
        self.file = Path(folder) / 'run.json'
        self.run = RunState(self.file)
        self.at = self.run.state['started_at'] + 1
        self.resources = {'life': {'value': 6, 'capacity': 8}, 'shield': {'value': 0},
            'command': {'value': 3}, 'hope': {'value': 7}, 'action': {'value': 4}, 'valuation': {'value': 27}}

    def observe(self, resources, **extra):
        observed = {'page': 'run_map', 'relics': {'ids': [], 'count': None}, 'resources': resources, **extra}
        before = deepcopy(observed)
        self.run.apply(observed, self.at)
        self.assertEqual(observed, before)
        self.at += 1

    def test_all_six_reach_saved_state_and_reopen_without_reconstruction(self):
        self.observe(self.resources)
        saved = self.file.read_bytes()
        restored = RunState(self.file)
        self.assertEqual(self.file.read_bytes(), saved)
        for key, record in self.resources.items():
            self.assertEqual(restored.state['resources'][key]['value'], record['value'])
            self.assertEqual(restored.state['resources'][key]['captured_at'], self.at-1)
        rows = {r['key']:r for r in resource_rows(restored.state)}
        self.assertEqual(rows['life']['value'], '6/8')
        self.assertEqual(rows['shield']['value'], '0')
        self.assertEqual(rows['hope']['value'], '7')
        self.assertIn('最近读到', rows['valuation']['note'])

    def test_unread_page_retains_each_last_quantity_and_its_original_time(self):
        self.observe(self.resources)
        old = deepcopy(self.run.state['resources'])
        self.observe({})
        self.assertEqual(self.run.state['resources'], old)
        self.observe({'hope': {'value': 0}})
        self.assertEqual(self.run.state['resources']['hope']['value'], 0)
        for key in set(old)-{'hope'}:
            self.assertEqual(self.run.state['resources'][key], old[key])

    def test_unknown_or_malformed_new_field_does_not_erase_confirmed_quantity(self):
        self.observe(self.resources)
        old = deepcopy(self.run.state['resources']['action'])
        for bad in ({}, {'value': None}, {'value': True}, {'value': '3'}, {'value': -1}):
            self.observe({'action': bad})
            self.assertEqual(self.run.state['resources']['action'], old)
        self.observe({'unrelated_internal_counter': {'value': 9}})
        self.assertNotIn('unrelated_internal_counter', self.run.state['resources'])

    def test_changes_have_chinese_names_and_are_not_assigned_to_rewards(self):
        self.observe(self.resources)
        self.observe({'hope': {'value': 2}})
        history = history_rows(self.run.state)
        hope = [r for r in history if r['resource']=='hope']
        self.assertEqual([r['delta'] for r in hope], [None,-5])
        self.assertEqual(hope[-1]['name'], '希望')
        self.assertEqual(next(r for r in history if r['resource']=='command')['name'], '指挥等级')

    def test_same_frame_floor_snapshot_contains_only_that_frames_observations(self):
        from rouge.run_config import config_data
        zid = next(iter(config_data()['zones']))
        self.observe(self.resources, config={'zone': {'id': zid,
            'name': config_data()['zones'][zid]['name'], 'source': 'public-contract441'}})
        rows = snapshots(self.run.state)
        self.assertTrue(rows)
        self.assertEqual(rows[-1]['values'], {k:r['value'] for k,r in self.resources.items()})
        self.assertIn('目标生命', snapshot_text(rows[-1]))
        self.assertIn('不是入层、出层或结算', snapshot_text(rows[-1]))

    def test_new_display_fields_do_not_become_relic_calculation_inputs(self):
        self.observe({**self.resources, 'gold': {'value': 10}, 'parts_count': {'value': 2}})
        self.assertEqual(set(self.run.calculation_resources()), {'gold','parts_count'})

    def test_only_explicit_temporary_new_run_clears_saved_resources(self):
        self.observe(self.resources)
        old_id = self.run.state['id']
        self.run.reset()
        self.assertNotEqual(self.run.state['id'], old_id)
        self.assertEqual(self.run.state['resources'], {})


class HUDResourceStrip441Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_visible_chips_refresh_in_place_and_do_not_invent_other_fields(self):
        strip = ResourceStrip()
        self.addCleanup(strip.close)
        strip.resize(560, 180)
        strip.show()
        self.qt.processEvents()
        before = dict(strip.chips)
        state = {'resources': {'life': {'value': 5,'capacity': 6,'captured_at': 10},
                              'hope': {'value': 0,'captured_at': 10}}}
        strip.refresh(state)
        self.qt.processEvents()
        self.assertTrue(strip.isVisible())
        self.assertEqual(strip.chips, before)
        self.assertEqual(strip.chips['life'].accessibleName(), '目标生命 5/6')
        self.assertEqual(strip.chips['hope'].accessibleName(), '希望 0')
        self.assertEqual(strip.chips['shield'].accessibleName(), '护盾 未读')
        self.assertIn('最近读到', strip.chips['hope'].toolTip())
        self.assertNotIn('尚未覆盖', strip.chips['life'].toolTip())


class FullEntrySelection441Tests(unittest.TestCase):
    def test_executable_full_check_selects_the_same_ordered_scope_as_import(self):
        import runpy,sys
        from unittest.mock import patch
        root=Path(__file__).resolve().parents[1]
        path=root/'scripts/verify_full_available.py'
        sys.path.insert(0,str(root/'scripts'))
        expected=runpy.run_path(str(path))['maintained_selectors']()
        selected=[]
        class SelectionObserved(Exception):
            pass
        def observe(names):
            selected.extend(names)
            raise SelectionObserved()
        with TemporaryDirectory(prefix='rouge-scope441-')as folder:
            argv=[str(path),'--output',str(Path(folder)/'not-a-test-result.json')]
            with patch.object(sys,'argv',argv),patch.object(unittest.defaultTestLoader,'loadTestsFromNames',side_effect=observe):
                with self.assertRaises(SelectionObserved):
                    runpy.run_path(str(path),run_name='__main__')
        self.assertEqual(selected,expected)


if __name__ == '__main__':
    unittest.main()
