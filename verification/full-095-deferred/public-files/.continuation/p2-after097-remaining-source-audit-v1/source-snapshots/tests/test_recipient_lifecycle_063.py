"""Temporary same-run evidence sequences, not fabricated live gameplay."""
import copy
import tempfile
import unittest
from pathlib import Path

from rouge.damage import calculate_damage
from rouge.run_state import RunState

OWNER = 'mechanist'
OTHER = 'char_151_myrtle'
COOKIE = 'rogue_6_relic_assign_15'
COOKIE_BUFF = 'rogue_6_from_relic_15'
SNACK = 'rogue_6_relic_assign_13'
SNACK_BUFF = 'rogue_6_from_relic_13'


def full_bar(*ids):
    return {'relics': {'ids': list(ids), 'icons': [
        {'id': rid, 'candidates': [rid], 'confirmed': True, 'source': 'held_icon_and_usage'} for rid in ids],
        'count': len(ids), 'source': 'held_bar'}}


def member(oid=OWNER, **values):
    return {'id': oid, 'scope': 'run', 'fields': {}, 'skill_ranks': {}, **values}


def popup(ids=(), oid=OWNER, complete=True, **values):
    return member(oid, char_buff_ids=list(ids), char_buffs_complete=complete, **values)


class RecipientLifecycle063Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.path = Path(temp.name)/'run.json';self.run = RunState(self.path)
        self.at = self.run.state['started_at'] + 1

    def apply(self, observed):
        self.run.apply(observed, self.at);self.at += 1

    def record(self, oid=OWNER):
        return self.run.state['operators'][oid]

    def result(self):
        state = self.record()
        return calculate_damage({'operator': OWNER, 'skill': 3, 'relic_ids': self.run.held_relic_ids(),
            'char_buff_ids': state.get('char_buff_ids', []), 'char_buffs_complete': state.get('char_buffs_complete', False),
            'char_buff_absent_ids': state.get('char_buff_absent_ids', []),
            'char_buff_pending_ids': state.get('char_buff_pending_ids', [])})

    def binding(self, rid):
        return next(r['recipient_binding']['state'] for r in self.result()['relic_resolution']['records'] if r['id'] == rid)

    def test_new_cookie_invalidates_old_absence_without_assigning_a_recipient(self):
        self.apply({'operators': [popup(), popup(oid=OTHER)]})
        self.apply(full_bar(COOKIE))
        for oid in (OWNER, OTHER):
            self.assertFalse(self.record(oid)['char_buffs_complete'])
            self.assertEqual(self.record(oid)['char_buff_ids'], [])
            self.assertEqual(self.record(oid)['char_buff_pending_ids'], [COOKIE_BUFF])
        self.assertEqual(self.binding(COOKIE), 'unknown')
        self.assertEqual(self.result()['estimate']['skill']['sp_recovery_per_second'], 1)

    def test_unrelated_absence_is_reused_after_cookie_gain(self):
        self.apply(full_bar(SNACK))
        self.apply({'operators': [popup()]})
        self.apply(full_bar(SNACK, COOKIE))
        self.assertEqual(self.binding(COOKIE), 'unknown')
        self.assertEqual(self.binding(SNACK), 'absent')

    def test_confirmed_buff_survives_new_item_and_parent_loss(self):
        self.apply({'operators': [popup([SNACK_BUFF])]})
        self.apply(full_bar(COOKIE))
        self.assertEqual(self.record()['char_buff_ids'], [SNACK_BUFF])
        self.assertEqual(self.result()['estimate']['skill']['sp_cost'], 28)  # pinned S3 cost 35 * .8
        self.apply(full_bar())
        self.assertEqual(self.record()['char_buff_ids'], [SNACK_BUFF])

    def test_new_cookie_does_not_revoke_already_confirmed_cookie(self):
        self.apply({'operators': [popup([COOKIE_BUFF])]})
        self.apply(full_bar(COOKIE))
        self.assertTrue(self.record()['char_buffs_complete'])
        self.assertEqual(self.binding(COOKIE), 'confirmed')

    def test_same_frame_complete_popup_overrides_gain_uncertainty(self):
        self.apply({'operators': [popup()]})
        self.apply({**full_bar(COOKIE), 'operators': [popup()]})
        self.assertTrue(self.record()['char_buffs_complete'])
        self.assertEqual(self.binding(COOKIE), 'absent')

    def test_partial_current_popup_only_confirms_visible_positive(self):
        self.apply({'operators': [popup()]})
        self.apply({**full_bar(COOKIE), 'operators': [popup([SNACK_BUFF], complete=False)]})
        self.assertEqual(self.binding(COOKIE), 'unknown')
        self.assertEqual(self.record()['char_buff_ids'], [SNACK_BUFF])

    def test_repeated_item_and_unknown_page_do_not_repeat_invalidation(self):
        self.apply({'operators': [popup()]});self.apply(full_bar(COOKIE))
        history = copy.deepcopy(self.run.state['history'])
        self.apply(full_bar(COOKIE));self.apply({'operators': [member()]})
        self.assertEqual(self.run.state['history'], history)
        self.assertEqual(self.binding(COOKIE), 'unknown')

    def test_explicit_partial_popup_does_not_reassert_old_full_negative_list(self):
        self.apply(full_bar(SNACK, COOKIE));self.apply({'operators': [popup()]})
        self.apply({'operators': [popup([SNACK_BUFF], complete=False)]})
        self.assertEqual(self.binding(COOKIE), 'unknown')
        self.assertEqual(self.binding(SNACK), 'confirmed')
        self.assertEqual(self.record()['char_buff_absent_ids'], [])

    def test_save_reload_and_later_full_popup_resolve_pending_once(self):
        self.apply({'operators': [popup()]});self.apply(full_bar(COOKIE))
        old = copy.deepcopy(self.run.state['history']);identity = self.run.state['id']
        self.run = RunState(self.path)
        self.assertEqual(self.binding(COOKIE), 'unknown')
        self.apply({'operators': [popup([COOKIE_BUFF])]})
        self.assertEqual(self.record()['char_buff_pending_ids'], [])
        self.assertEqual(self.binding(COOKIE), 'confirmed')
        self.assertEqual(self.result()['estimate']['skill']['sp_recovery_per_second'], 1.8)
        self.assertEqual(self.run.state['id'], identity)
        self.assertEqual(self.run.state['history'][:len(old)], old)

    def test_new_snack_waits_for_observed_promotion(self):
        self.apply({'operators': [popup(fields={'elite': 1}, advanced=False)]})
        self.apply(full_bar(SNACK))
        self.assertEqual(self.binding(SNACK), 'absent')
        self.apply({'operators': [member(fields={'elite': 2}, advanced=True)]})
        self.assertEqual(self.binding(SNACK), 'unknown')
        self.assertEqual(self.record()['char_buff_pending_ids'], [SNACK_BUFF])

    def test_first_discovery_of_advanced_state_is_not_a_promotion_event(self):
        self.apply(full_bar(SNACK));self.apply({'operators': [popup()]})
        self.apply({'operators': [member(fields={'elite': 2}, advanced=True)]})
        self.assertEqual(self.binding(SNACK), 'absent')

    def test_other_operator_promotion_does_not_invalidate_current_operator(self):
        self.apply(full_bar(SNACK))
        self.apply({'operators': [popup(fields={'elite': 1}), popup(oid=OTHER, fields={'elite': 1})]})
        self.apply({'operators': [member(OTHER, fields={'elite': 2})]})
        self.assertEqual(self.binding(SNACK), 'absent')
        self.assertEqual(self.record(OTHER)['char_buff_pending_ids'], [SNACK_BUFF])

    def test_profession_specific_upgrade_ticket_only_affects_compatible_operator(self):
        sniper = 'char_133_mm'
        self.apply({'operators': [popup(), popup(oid=sniper)]})
        self.apply(full_bar('rogue_6_relic_assign_5'))
        self.assertTrue(self.record()['char_buffs_complete'])
        self.assertFalse(self.record(sniper)['char_buffs_complete'])
        self.assertEqual(self.record(sniper)['char_buff_pending_ids'], ['rogue_6_from_relic_5'])

    def test_leave_rejoin_clears_old_negative_evidence_as_well_as_positive(self):
        self.apply(full_bar(COOKIE));self.apply({'operators': [popup()]})
        self.apply({'crew_count': 0, 'operators': []})
        self.apply({'operators': [member()]})
        self.assertEqual(self.record()['char_buff_absent_ids'], [])
        self.assertEqual(self.binding(COOKIE), 'unknown')

    def test_unknown_to_known_origin_preserves_negative_evidence(self):
        self.apply(full_bar(COOKIE));self.apply({'operators': [popup()]})
        self.apply({'operators': [member(recruitment_kind='non_emergency')]})
        self.assertEqual(self.binding(COOKIE), 'absent')

    def test_reacquisition_invalidates_newer_negative_but_not_historical_positive(self):
        self.apply(full_bar(COOKIE));self.apply({'operators': [popup([SNACK_BUFF])]})
        self.apply(full_bar());self.apply(full_bar(COOKIE))
        self.assertEqual(self.binding(COOKIE), 'unknown')
        self.assertEqual(self.record()['char_buff_ids'], [SNACK_BUFF])

    def test_unknown_recipient_is_not_forgotten_when_parent_leaves_inventory(self):
        self.apply({'operators': [popup()]});self.apply(full_bar(COOKIE));self.apply(full_bar())
        result=self.result()
        self.assertFalse(result['relic_resolution']['complete'])
        self.assertFalse(result['estimate']['complete'])
        self.assertEqual(result['relic_resolution']['recipient_evidence_pending'], [COOKIE_BUFF])
        self.assertTrue(any('幸运饼干' in warning and '归属仍待更新' in warning for warning in result['warnings']))
        self.run=RunState(self.path)
        self.assertFalse(self.result()['estimate']['complete'])

    def test_pending_recipient_contract_rejects_conflicting_certainty(self):
        base={'operator':OWNER, 'skill':3, 'char_buff_pending_ids':[COOKIE_BUFF]}
        for extra in ({'char_buff_ids':[COOKIE_BUFF]}, {'char_buff_absent_ids':[COOKIE_BUFF]},
                      {'char_buff_ids':[], 'char_buffs_complete':True}, {'char_buff_pending_ids':'bad'}):
            with self.subTest(extra=extra),self.assertRaises(ValueError):
                calculate_damage({**base,**extra})

    def test_out_of_order_observation_and_manual_new_run_do_not_leak_evidence(self):
        self.apply({'operators': [popup()]});before = copy.deepcopy(self.run.state)
        self.assertFalse(self.run.apply(full_bar(COOKIE), self.at - 2))
        self.assertEqual(self.run.state, before)
        self.run.reset();self.at = self.run.state['started_at'] + 1
        self.apply(full_bar(COOKIE))
        self.assertEqual(self.run.state['operators'], {})

    def test_explicit_absence_contract_rejects_invalid_or_conflicting_evidence(self):
        base = {'operator': OWNER, 'skill': 3}
        for values in ({'char_buff_absent_ids': 'bad'}, {'char_buff_absent_ids': ['unknown']},
                       {'char_buff_ids': [COOKIE_BUFF], 'char_buff_absent_ids': [COOKIE_BUFF]}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                calculate_damage({**base, **values})


if __name__ == '__main__':
    unittest.main()
