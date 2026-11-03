"""Origin discovery preserves owned buffs; historical repair needs exact evidence."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from rouge.run_state import RunState


OWNER = 'char_151_myrtle'
BUFFS = ['rogue_6_from_relic_1', 'rogue_6_from_relic_13']
REPAIR_KIND = 'char_buffs_origin_discovery_repaired'


class OriginDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.file = Path(self.directory.name) / 'run.json'
        self.run = RunState(self.file)
        self.at = self.run.state['started_at'] + 1

    def observe(self, **extra):
        return {'operators': [{'id': OWNER, 'scope': 'run', 'fields': {},
                               'skill_ranks': {}, **extra}]}

    def owned(self, *, complete=True, ids=None):
        ids = list(BUFFS if ids is None else ids)
        return self.observe(
            char_buff_ids=ids, char_buffs_complete=complete,
            sources={'char_buff_ids': {'source': 'owned_operator_buff_popup',
                                      'complete': complete, 'issues': []}},
            recipient_buffs={'operator_id': OWNER, 'ids': list(ids),
                             'source': 'owned_operator_buff_popup', 'complete': complete})

    def record(self):
        return self.run.state['operators'][OWNER]

    def events(self, kind):
        return [event for event in self.run.state['history'] if event.get('kind') == kind]

    def legacy_corruption(self, *, complete=True):
        """Reproduce the confirmed pre-fix events, never load private runtime data."""
        self.run.apply(self.owned(complete=complete), self.at)
        member = self.record()
        self.run.state['history'].extend([
            {'at': self.at + 1, 'kind': 'recruitment_changed', 'id': OWNER,
             'previous_kind': None, 'kind_now': 'non_emergency',
             'previous_fields': {}, 'previous_skill_ranks': {}},
            {'at': self.at + 1, 'kind': 'char_buffs_updated', 'id': OWNER,
             'previous_char_buff_ids': list(BUFFS), 'char_buff_ids': []}])
        member.update(recruitment_kind='non_emergency', char_buff_ids=[],
                      char_buffs_complete=False, present=True)
        self.run.state['last_read'] = self.at + 1
        return copy.deepcopy(self.run.state['history'])

    def test_first_origin_discovery_preserves_owned_buffs_and_cultivation(self):
        owned = self.owned()
        owned['operators'][0].update(fields={'elite': 2, 'level': 20},
                                     skill_ranks={'1': 10, '2': 10})
        self.run.apply(owned, self.at)
        self.run.apply(self.observe(recruitment_kind='non_emergency'), self.at + 1)
        self.assertEqual(self.record()['char_buff_ids'], BUFFS)
        self.assertTrue(self.record()['char_buffs_complete'])
        self.assertEqual(self.record()['invalid_fields'], [])
        self.assertEqual(self.record()['invalid_skill_ranks'], [])
        self.assertEqual(self.events('recruitment_changed'), [])
        self.run.apply(self.observe(), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], BUFFS)
        self.assertTrue(self.record()['char_buffs_complete'])

    def test_first_emergency_discovery_also_preserves_owned_buffs(self):
        self.run.apply(self.owned(), self.at)
        self.run.apply(self.observe(recruitment_kind='emergency_hire'), self.at + 1)
        self.assertEqual(self.record()['char_buff_ids'], BUFFS)
        self.assertTrue(self.record()['char_buffs_complete'])
        self.assertEqual(self.events('recruitment_changed'), [])

    def test_real_known_origin_change_still_clears_buffs(self):
        observed = self.owned()
        observed['operators'][0]['recruitment_kind'] = 'non_emergency'
        self.run.apply(observed, self.at)
        self.run.apply(self.observe(recruitment_kind='emergency_hire'), self.at + 1)
        self.assertEqual(self.record()['char_buff_ids'], [])
        self.assertFalse(self.record()['char_buffs_complete'])
        self.assertEqual(self.events('recruitment_changed')[-1]['previous_kind'], 'non_emergency')

    def test_unknown_origin_return_still_requires_new_confirmation(self):
        self.run.apply(self.owned(), self.at)
        self.run.apply({'crew_count': 0, 'operators': []}, self.at + 1)
        self.assertFalse(self.record()['present'])
        self.run.apply(self.observe(recruitment_kind='non_emergency'), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], [])
        self.assertFalse(self.record()['char_buffs_complete'])
        restored = RunState(self.file)
        self.assertEqual(restored.state['operators'][OWNER]['char_buff_ids'], [])
        self.assertFalse(any(h['kind'] == REPAIR_KIND for h in restored.state['history']))

    def test_partial_then_discovery_remains_partial_and_merges(self):
        self.run.apply(self.owned(complete=False, ids=BUFFS[:1]), self.at)
        self.run.apply(self.observe(recruitment_kind='non_emergency'), self.at + 1)
        self.assertEqual(self.record()['char_buff_ids'], BUFFS[:1])
        self.assertFalse(self.record()['char_buffs_complete'])
        self.run.apply(self.owned(complete=False, ids=BUFFS[1:]), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], BUFFS)
        self.assertFalse(self.record()['char_buffs_complete'])

    def test_explicit_complete_empty_is_current_evidence_not_legacy_recovery(self):
        self.run.apply(self.owned(), self.at)
        self.run.apply(self.owned(ids=[]), self.at + 1)
        self.run.apply(self.observe(recruitment_kind='non_emergency'), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], [])
        self.assertTrue(self.record()['char_buffs_complete'])
        restored = RunState(self.file)
        self.assertEqual(restored.state['operators'][OWNER]['char_buff_ids'], [])
        self.assertFalse(any(h['kind'] == REPAIR_KIND for h in restored.state['history']))

    def test_load_recovers_exact_legacy_clear_once_and_keeps_history(self):
        before = self.legacy_corruption()
        identity = self.run.state['id']
        self.run.save()
        restored = RunState(self.file)
        member = restored.state['operators'][OWNER]
        self.assertEqual(member['char_buff_ids'], BUFFS)
        self.assertTrue(member['char_buffs_complete'])
        self.assertEqual(restored.state['id'], identity)
        self.assertEqual(restored.state['history'][:len(before)], before)
        repairs = [h for h in restored.state['history'] if h['kind'] == REPAIR_KIND]
        self.assertEqual(len(repairs), 1)
        self.assertEqual(repairs[0]['char_buff_ids'], BUFFS)
        self.assertEqual(repairs[0]['source'], 'same_run_owned_popup_and_origin_discovery_history')
        second = RunState(self.file)
        self.assertEqual(second.state['history'], restored.state['history'])
        self.assertEqual(json.loads(self.file.read_text(encoding='utf-8'))['operators'][OWNER]['char_buff_ids'], BUFFS)

    def test_apply_recovers_legacy_clear_and_persists_without_older_run_restore(self):
        before = self.legacy_corruption()
        self.run.apply(self.observe(), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], BUFFS)
        self.assertTrue(self.record()['char_buffs_complete'])
        self.assertEqual(self.run.state['history'][:len(before)], before)
        self.assertEqual(len(self.events(REPAIR_KIND)), 1)
        self.run.apply(self.observe(), self.at + 3)
        self.assertEqual(len(self.events(REPAIR_KIND)), 1)
        self.assertEqual(RunState(self.file).state['operators'][OWNER]['char_buff_ids'], BUFFS)

    def test_partial_legacy_recovery_uses_retained_popup_completeness(self):
        self.legacy_corruption(complete=False)
        self.run.apply(self.observe(), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], BUFFS)
        self.assertFalse(self.record()['char_buffs_complete'])
        self.assertFalse(self.events(REPAIR_KIND)[0]['char_buffs_complete'])

    def test_complete_owned_source_can_repair_without_retained_popup_payload(self):
        self.legacy_corruption()
        self.record().pop('recipient_buffs')
        self.run.save()
        restored = RunState(self.file)
        self.assertEqual(restored.state['operators'][OWNER]['char_buff_ids'], BUFFS)
        self.assertTrue(restored.state['operators'][OWNER]['char_buffs_complete'])

    def test_partial_owned_source_without_positive_popup_payload_is_insufficient(self):
        self.legacy_corruption(complete=False)
        self.record().pop('recipient_buffs')
        self.run.save()
        restored = RunState(self.file)
        self.assertEqual(restored.state['operators'][OWNER]['char_buff_ids'], [])
        self.assertFalse(any(h['kind'] == REPAIR_KIND for h in restored.state['history']))

    def test_legacy_events_require_finite_ordered_timestamps_within_current_run(self):
        self.legacy_corruption()
        original = copy.deepcopy(self.run.state)
        positive = next(i for i, h in enumerate(original['history'])
                        if h['kind'] == 'char_buffs_updated' and h['char_buff_ids'])
        changes = {
            'started_after_old_events': lambda state: state.update(started_at=self.at + 2),
            'positive_nan': lambda state: state['history'][positive].update(at=float('nan')),
            'clear_infinity': lambda state: [state['history'][i].update(at=float('inf')) for i in (-2, -1)],
            'positive_after_clear': lambda state: state['history'][positive].update(at=self.at + 2),
        }
        for name, change in changes.items():
            with self.subTest(name=name):
                self.run.state = copy.deepcopy(original)
                change(self.run.state)
                self.run.save()
                restored = RunState(self.file)
                self.assertEqual(restored.state['operators'][OWNER]['char_buff_ids'], [])
                self.assertFalse(any(h['kind'] == REPAIR_KIND for h in restored.state['history']))

    def test_incoming_complete_empty_supersedes_corruption_without_repair(self):
        self.legacy_corruption()
        self.run.apply(self.owned(ids=[]), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], [])
        self.assertTrue(self.record()['char_buffs_complete'])
        self.assertEqual(self.events(REPAIR_KIND), [])
        self.assertEqual(RunState(self.file).state['operators'][OWNER]['char_buff_ids'], [])

    def test_incoming_partial_positive_can_merge_recovered_buffs(self):
        self.legacy_corruption()
        self.run.apply(self.owned(complete=False, ids=BUFFS[:1]), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], BUFFS)
        self.assertFalse(self.record()['char_buffs_complete'])
        self.assertEqual(len(self.events(REPAIR_KIND)), 1)

    def test_new_origin_change_does_not_recover_old_buff_first(self):
        self.legacy_corruption()
        self.run.apply(self.observe(recruitment_kind='emergency_hire'), self.at + 2)
        self.assertEqual(self.record()['char_buff_ids'], [])
        self.assertEqual(self.events(REPAIR_KIND), [])

    def test_stale_and_cross_run_observations_do_not_trigger_migration(self):
        self.legacy_corruption()
        self.assertFalse(self.run.apply(self.observe(), self.at))
        observed = self.observe()
        observed['config_reuse'] = {'run_id': 'another-run'}
        self.assertFalse(self.run.apply(observed, self.at + 2))
        self.assertEqual(self.record()['char_buff_ids'], [])
        self.assertEqual(self.events(REPAIR_KIND), [])

    def test_legacy_repair_rejects_missing_or_conflicting_provenance(self):
        changes = {
            'known_previous_origin': lambda run: run.state['history'][-2].update(previous_kind='emergency_hire'),
            'missing_previous_key': lambda run: run.state['history'][-2].pop('previous_kind'),
            'different_event_time': lambda run: run.state['history'][-2].update(at=self.at + .5),
            'nonadjacent_event': lambda run: run.state['history'].insert(-1, {'kind': 'unrelated', 'at': self.at + 1}),
            'absent_member': lambda run: run.state['operators'][OWNER].update(present=False),
            'wrong_scope': lambda run: run.state['operators'][OWNER].update(scope='account'),
            'current_complete_empty': lambda run: run.state['operators'][OWNER].update(char_buffs_complete=True),
            'source_not_owned': lambda run: run.state['operators'][OWNER]['sources']['char_buff_ids'].update(source='reward_preview'),
            'source_boolean_missing': lambda run: run.state['operators'][OWNER]['sources']['char_buff_ids'].pop('complete'),
            'source_boolean_invalid': lambda run: run.state['operators'][OWNER]['sources']['char_buff_ids'].update(complete=1),
            'current_kind_conflict': lambda run: run.state['operators'][OWNER].update(recruitment_kind='emergency_hire'),
            'invalid_buff_id': lambda run: run.state['history'][-1].update(previous_char_buff_ids=['not-a-buff']),
            'wrong_profession': lambda run: run.state['history'][-1].update(previous_char_buff_ids=['rogue_6_from_relic_6']),
            'last_clear_not_empty': lambda run: run.state['history'][-1].update(char_buff_ids=BUFFS[:1]),
            'last_clear_without_prior_ids': lambda run: run.state['history'][-1].update(previous_char_buff_ids=[]),
            'popup_owner_conflict': lambda run: run.state['operators'][OWNER]['recipient_buffs'].update(operator_id='mechanist'),
            'new_partial_empty_popup': lambda run: run.state['operators'][OWNER]['recipient_buffs'].update(ids=[], complete=False),
            'source_popup_complete_conflict': lambda run: run.state['operators'][OWNER]['recipient_buffs'].update(complete=False),
        }
        original = None
        for name, change in changes.items():
            with self.subTest(name=name):
                if original is None:
                    self.legacy_corruption()
                    original = copy.deepcopy(self.run.state)
                self.run.state = copy.deepcopy(original)
                change(self.run)
                self.run.save()
                restored = RunState(self.file)
                self.assertEqual(restored.state['operators'][OWNER]['char_buff_ids'], [])
                self.assertFalse(any(h['kind'] == REPAIR_KIND for h in restored.state['history']))

    def test_later_change_or_leave_rejects_historical_recovery(self):
        self.legacy_corruption()
        original = copy.deepcopy(self.run.state)
        for kind in ('recruitment_changed', 'classification_corrected', 'operator_no_longer_present',
                     'char_buffs_updated'):
            with self.subTest(kind=kind):
                self.run.state = copy.deepcopy(original)
                self.run.state['history'].append({'kind': kind, 'id': OWNER, 'at': self.at + 1.5})
                self.run.save()
                restored = RunState(self.file)
                self.assertEqual(restored.state['operators'][OWNER]['char_buff_ids'], [])
                self.assertFalse(any(h['kind'] == REPAIR_KIND for h in restored.state['history']))

    def test_departure_between_positive_popup_and_unknown_origin_clear_is_real_return(self):
        self.legacy_corruption()
        self.run.state['history'].insert(-2, {'kind': 'operator_no_longer_present',
                                             'id': OWNER, 'at': self.at + .5})
        self.run.save()
        restored = RunState(self.file)
        self.assertEqual(restored.state['operators'][OWNER]['char_buff_ids'], [])
        self.assertFalse(any(h['kind'] == REPAIR_KIND for h in restored.state['history']))


if __name__ == '__main__':
    unittest.main()
