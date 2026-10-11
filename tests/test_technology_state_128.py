import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from rouge.damage import calculate_damage
from rouge.run_state import RunState
from rouge.technology import format_technology
from rouge.technology_state import TechnologyState

FIRST = 'rogue_6_outbuff_1'
SECOND = 'rogue_6_outbuff_2'


class TechnologyStateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='technology128-')
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.path = self.root / 'account' / 'technology-state.json'
        self.state = TechnologyState(self.path)

    def write(self, value):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(value), encoding='utf-8')

    def test_initial_unknowns_and_read_only_start_do_not_create_files(self):
        self.assertFalse(self.path.exists())
        self.assertEqual(self.state.counts(), {'unknown': 57, 'unlocked': 0, 'locked': 0})
        self.assertEqual(self.state.view(FIRST)['status'], 'unknown')
        self.assertIsNone(self.state.view(FIRST)['actual_activation'])
        profiles = self.state.profiles(); profiles[0]['name'] = 'changed'
        snapshot = self.state.snapshot(); snapshot['profiles'].clear()
        self.assertEqual(self.state.profile_name, '默认资料档案')
        self.assertFalse(self.path.exists())

    def test_manual_statuses_survive_close_reload_with_source_and_time(self):
        self.assertTrue(self.state.set_status(FIRST, 'unlocked'))
        self.assertTrue(self.state.set_status(SECOND, 'locked'))
        restored = TechnologyState(self.path)
        self.assertEqual(restored.counts(), {'unknown': 55, 'unlocked': 1, 'locked': 1})
        record = restored.view(FIRST)
        self.assertEqual(record['source'], 'manual')
        self.assertTrue(record['updated_at'])
        self.assertFalse(record['game_account_identity_verified'])
        self.assertIn('用户记录', restored.describe(FIRST))

    def test_same_named_nodes_have_separate_persisted_statuses(self):
        one, two = 'rogue_6_outbuff_25', 'rogue_6_outbuff_35'
        self.state.set_status(one, 'unlocked'); self.state.set_status(two, 'locked')
        restored = TechnologyState(self.path)
        self.assertEqual((restored.view(one)['status'], restored.view(two)['status']), ('unlocked', 'locked'))

    def test_account_labelled_profiles_and_selected_profile_are_isolated(self):
        initial = self.state.selected_profile
        self.state.set_status(FIRST, 'unlocked')
        second = self.state.create_profile('另一个账户🐱')
        self.assertEqual(self.state.counts()['unknown'], 57)
        self.state.set_status(FIRST, 'locked')
        restored = TechnologyState(self.path)
        self.assertEqual(restored.selected_profile, second)
        self.assertEqual(restored.profile_name, '另一个账户🐱')
        self.assertEqual(restored.view(FIRST)['status'], 'locked')
        restored.select_profile(initial)
        self.assertEqual(restored.view(FIRST)['status'], 'unlocked')
        self.assertEqual(TechnologyState(self.path).selected_profile, initial)

    def test_explicit_unknown_affects_only_current_node_and_profile(self):
        self.state.set_status(FIRST, 'unlocked'); self.state.set_status(SECOND, 'locked')
        self.state.set_status(FIRST, 'unknown')
        restored = TechnologyState(self.path)
        self.assertEqual(restored.counts(), {'unknown': 56, 'unlocked': 0, 'locked': 1})
        self.assertEqual(restored.view(FIRST)['source'], 'manual')
        self.assertEqual(restored.view(SECOND)['status'], 'locked')

    def test_predecessor_status_never_proves_child_unlock_or_activation(self):
        self.state.set_status(FIRST, 'unlocked')
        self.assertEqual(self.state.view(SECOND)['status'], 'unknown')
        self.assertIsNone(self.state.view(FIRST)['actual_activation'])
        self.assertIn('数值效果仍未知', self.state.describe(FIRST))

    def test_bad_node_status_profile_and_name_do_not_modify_saved_data(self):
        self.state.set_status(FIRST, 'locked')
        before = self.path.read_bytes(); snapshot = self.state.snapshot()
        for action in (
            lambda: self.state.set_status('unrecognized', 'unlocked'),
            lambda: self.state.set_status(FIRST, True),
            lambda: self.state.set_status(FIRST, ['unlocked']),
            lambda: self.state.set_status(FIRST, 'active'),
            lambda: self.state.select_profile('absent'),
            lambda: self.state.create_profile('默认资料档案'),
            lambda: self.state.create_profile(' '),
            lambda: self.state.create_profile('x' * 61),
            lambda: self.state.create_profile('bad\nname'),
            lambda: self.state.create_profile('\ud800'),
        ):
            with self.assertRaises(ValueError): action()
            self.assertEqual(self.state.snapshot(), snapshot)
            self.assertEqual(self.path.read_bytes(), before)

    def test_unknown_metadata_and_future_node_records_survive_round_trip(self):
        self.state.set_status(FIRST, 'unlocked')
        saved = self.state.snapshot()
        saved['future'] = {'opaque': [1, '保留']}
        saved['profiles']['default']['nodes']['future-node'] = [True, {'status': 'future'}]
        saved['profiles']['default']['nodes'][FIRST]['actual_activation'] = True
        self.write(saved)
        restored = TechnologyState(self.path)
        self.assertEqual(restored.counts()['unlocked'], 1)
        self.assertIsNone(restored.view(FIRST)['actual_activation'])
        restored.set_status(SECOND, 'locked')
        restored.set_status(FIRST, 'unknown')
        actual = json.loads(self.path.read_text(encoding='utf-8'))
        self.assertEqual(actual['future'], saved['future'])
        self.assertEqual(actual['profiles']['default']['nodes']['future-node'], [True, {'status': 'future'}])
        self.assertTrue(actual['profiles']['default']['nodes'][FIRST]['actual_activation'])
        self.assertEqual(actual['profiles']['default']['nodes'][FIRST]['status'], 'unknown')

    def test_unreadable_or_foreign_files_are_preserved_during_session_edits(self):
        base = self.state.snapshot()
        bad_record = copy.deepcopy(base)
        bad_record['profiles']['default']['nodes'][FIRST] = {'status': True, 'source': 'manual', 'updated_at': '2026-10-11T00:00:00Z'}
        for raw in ('{', '[]', '{"schema_version":1,"schema_version":2}',
                    json.dumps({**base, 'schema_version': True}),
                    json.dumps({**base, 'topic_id': 'rogue_1'}), json.dumps(bad_record)):
            self.path.parent.mkdir(parents=True, exist_ok=True); self.path.write_text(raw, encoding='utf-8')
            restored = TechnologyState(self.path)
            self.assertTrue(restored.preserve_original)
            self.assertEqual(restored.counts()['unknown'], 57)
            self.assertFalse(restored.set_status(FIRST, 'unlocked'))
            self.assertEqual(restored.view(FIRST)['status'], 'unlocked')
            self.assertEqual(self.path.read_text(encoding='utf-8'), raw)
            self.assertIn('仅在当前运行有效', restored.persistence_notice())

    def test_second_window_cannot_overwrite_first_windows_newer_records(self):
        self.state.set_status(FIRST, 'locked')
        second = TechnologyState(self.path)
        self.state.set_status(FIRST, 'unlocked')
        before = self.path.read_bytes()
        self.assertFalse(second.set_status(SECOND, 'unlocked'))
        self.assertIn('其他窗口', second.persistence_notice())
        self.assertEqual(self.path.read_bytes(), before)
        second.create_profile('只在本次运行')
        self.assertEqual(self.path.read_bytes(), before)

    def test_failed_atomic_save_keeps_old_file_and_cleans_owned_temporary(self):
        self.state.set_status(FIRST, 'locked')
        before = self.path.read_bytes()
        unrelated = self.path.parent / 'technology-unrelated.tmp'; unrelated.write_text('keep')
        with patch('rouge.technology_state.os.replace', side_effect=OSError('injected replacement failure')) as replace:
            self.assertFalse(self.state.set_status(FIRST, 'unlocked'))
            self.assertEqual(replace.call_count, 1)
            self.assertFalse(self.state.set_status(SECOND, 'locked'))
            self.assertEqual(replace.call_count, 1)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob('technology-*.tmp')), [unrelated])
        self.assertEqual(self.state.view(FIRST)['status'], 'unlocked')
        self.assertIn('保存未完成', self.state.persistence_notice())

    def test_new_run_preserves_technology_account_and_calculation(self):
        args = {'operator': 'mechanist', 'skill': 3, 'base_attack': 1000}
        before_damage = calculate_damage(args)
        account = self.root / 'operator-state.json'; account.write_text('{"public-fixture":true}')
        self.state.set_status(FIRST, 'unlocked')
        before_technology = self.path.read_bytes(); before_account = account.read_bytes()
        run = RunState(self.root / 'run.json'); run.reset()
        self.assertEqual(self.path.read_bytes(), before_technology)
        self.assertEqual(account.read_bytes(), before_account)
        self.assertEqual(calculate_damage(args), before_damage)

    def test_record_times_require_usable_timezone_and_display_beijing(self):
        base = self.state.snapshot()
        for stamp in ('2026-10-11T06:07:08', 'bad', '9999-12-31T23:00:00+00:00', True):
            saved = copy.deepcopy(base)
            saved['profiles']['default']['nodes'][FIRST] = {'status': 'unlocked', 'source': 'manual', 'updated_at': stamp}
            self.write(saved)
            self.assertTrue(TechnologyState(self.path).preserve_original)
        saved['profiles']['default']['nodes'][FIRST]['updated_at'] = '2026-10-11T06:07:08+00:00'
        self.write(saved)
        self.assertIn('2026-10-11 14:07:08', TechnologyState(self.path).describe(FIRST))

    def test_optional_temporary_panel_state_is_explicitly_not_persistent(self):
        state = TechnologyState(); state.set_status(FIRST, 'unlocked')
        self.assertEqual(state.view(FIRST)['status'], 'unlocked')
        self.assertIn('关闭后不保留', state.persistence_notice())

    def test_manual_reference_report_distinguishes_status_from_game_activation(self):
        self.assertIn('账户解锁状态：未知', format_technology(FIRST, account_state=self.state))
        self.state.set_status(FIRST, 'unlocked')
        text = format_technology(FIRST, account_state=self.state)
        self.assertIn('本档案手动记录：已解锁（用户记录）', text)
        self.assertIn('实际启用与数值效果仍未知', text)
        self.assertIn('未将科技效果加入本局计算', text)
        self.assertNotIn('账户解锁状态：未知', text)
        self.assertIn('账户解锁状态：未知', format_technology(FIRST))


if __name__ == '__main__':
    unittest.main()
