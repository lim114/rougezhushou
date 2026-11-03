"""Crew booleans are unread observations; retained integer roster evidence wins."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from rouge.run_state import RunState

OWNER = 'mechanist'
OTHER = 'char_151_myrtle'


def member(owner=OWNER, **fields):
    return {'id': owner, 'scope': 'run', 'fields': fields, 'skill_ranks': {}}


class RunCrewCountBooleanInputTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.sequence = 0

    def seed_run(self, ids=(OWNER,), crew=1):
        self.sequence += 1
        run = RunState(self.directory / str(self.sequence) / 'run.json')
        observed = {'operators': [member(owner, elite=0, level=1) for owner in ids],
                    'crew_count': crew}
        before = json.dumps(observed, ensure_ascii=False, sort_keys=True)
        self.assertTrue(run.apply(observed, run.state['started_at'] + 1))
        self.assertEqual(json.dumps(observed, ensure_ascii=False, sort_keys=True), before)
        return run

    def observe(self, run, observed, *, at=None, expected=True):
        before = json.dumps(observed, ensure_ascii=False, sort_keys=True)
        returned = run.apply(observed, run.state['started_at'] + 2 if at is None else at)
        self.assertIs(returned, expected)
        self.assertEqual(json.dumps(observed, ensure_ascii=False, sort_keys=True), before)
        return json.loads(run.file.read_text(encoding='utf-8'))

    def assert_members(self, run, expected):
        present = {owner for owner, value in run.state['operators'].items() if value['present']}
        self.assertEqual(present, set(expected))

    def reload_run(self, run):
        saved = deepcopy(run.state)
        restored = RunState(run.file)
        for key in ('id', 'started_at', 'last_read', 'operators', 'crew_count',
                    'history', 'resources', 'config', 'relics'):
            self.assertEqual(restored.state[key], saved[key], key)
        self.assertIs(type(restored.state['crew_count']), type(saved['crew_count']))
        return restored

    def test_false_empty_observation_preserves_known_count_members_and_reload(self):
        run = self.seed_run()
        disk = self.observe(run, {'operators': [], 'crew_count': False})
        self.assert_members(run, (OWNER,))
        self.assertEqual(run.state['crew_count'], 1)
        self.assertIs(type(run.state['crew_count']), int)
        self.assertEqual(disk['crew_count'], 1)
        self.assertFalse(any(event['kind'] == 'operator_no_longer_present' for event in run.state['history']))
        self.assert_members(self.reload_run(run), (OWNER,))

    def test_true_subset_keeps_other_member_and_merges_positive_observation(self):
        run = self.seed_run((OWNER, OTHER), 2)
        disk = self.observe(run, {'operators': [member(level=9)], 'crew_count': True})
        self.assert_members(run, (OWNER, OTHER))
        self.assertEqual(run.state['crew_count'], 2)
        self.assertIs(type(run.state['crew_count']), int)
        self.assertEqual(run.state['operators'][OWNER]['fields']['level'], 9)
        self.assertTrue(disk['operators'][OTHER]['present'])
        self.assert_members(self.reload_run(run), (OWNER, OTHER))

    def test_none_and_integer_zero_one_keep_existing_roster_contract(self):
        for count, members, expected in ((None, [], (OWNER, OTHER)),
                                        (0, [], ()), (1, [member()], (OWNER,))):
            with self.subTest(count=count):
                run = self.seed_run((OWNER, OTHER), 2)
                self.observe(run, {'operators': members, 'crew_count': count})
                self.assert_members(run, expected)
                self.assertEqual(run.state['crew_count'], 2 if count is None else count)
                self.assertIs(type(run.state['crew_count']), int)

    def test_duplicate_ids_keep_unique_integer_count_semantics_and_bool_is_unread(self):
        for count, expected in ((True, (OWNER, OTHER)), (1, (OWNER,))):
            with self.subTest(count=count):
                run = self.seed_run((OWNER, OTHER), 2)
                self.observe(run, {'operators': [member(level=2), member(trust=25)],
                                   'crew_count': count})
                self.assert_members(run, expected)
                self.assertEqual(run.state['crew_count'], 2 if type(count) is bool else 1)
                self.assertEqual(run.state['operators'][OWNER]['fields']['level'], 2)
                self.assertEqual(run.state['operators'][OWNER]['fields']['trust'], 25)

    def test_valid_partial_roster_keeps_unseen_member_and_positive_fields(self):
        run = self.seed_run((OWNER, OTHER), 2)
        self.observe(run, {'operators': [member(trust=40)], 'crew_count': 2})
        self.assert_members(run, (OWNER, OTHER))
        self.assertEqual(run.state['operators'][OWNER]['fields']['trust'], 40)
        self.assertEqual(run.state['crew_count'], 2)

    def test_nonboolean_legacy_values_remain_compatible_without_producer_claim(self):
        # This protects legacy behavior; recognition's actual producer uses int/None.
        for count, expected in ((0.0, ()), ('0', (OWNER,))):
            with self.subTest(count=count):
                run = self.seed_run()
                self.observe(run, {'operators': [], 'crew_count': count})
                self.assert_members(run, expected)
                self.assertEqual(run.state['crew_count'], count)
                self.assertIs(type(run.state['crew_count']), type(count))

    def test_stale_and_cross_run_observations_keep_old_early_ignored_contract(self):
        for reason in ('stale', 'cross_run'):
            with self.subTest(reason=reason):
                run = self.seed_run()
                observed = {'operators': [], 'crew_count': False}
                at = run.state['started_at'] + 2
                if reason == 'stale':
                    at = run.state['started_at'] - 1
                else:
                    observed['config_reuse'] = {'run_id': 'another-run'}
                before = deepcopy(run.state)
                disk_before = run.file.read_bytes()
                self.observe(run, observed, at=at, expected=False)
                self.assertEqual(run.state, before)
                self.assertEqual(run.file.read_bytes(), disk_before)


if __name__ == '__main__':
    unittest.main()
