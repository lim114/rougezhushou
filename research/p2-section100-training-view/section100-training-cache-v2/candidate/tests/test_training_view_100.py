"""Unexecuted author proposal: public UI-consumption qualification controls.

Root must apply the matching helper, run these checks, and separately verify the
actual Qt window, including the unresolved large-integer conversion boundary.
"""
import copy
import unittest

from rouge.catalog import catalog, operator_profiles
from rouge.operator_summary import format_operator_observation
from rouge.training_view import (select_training_view, training_view_issue,
                                format_run_training_observation, run_operator_metadata)


OP = 'mechanist'


def record(scope='run', fields=None, ranks=None, **extra):
    value = {'id': OP, 'scope': scope,
             'fields': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1}
                       if fields is None else fields,
             'skill_ranks': {'1': 7} if ranks is None else ranks,
             'captured_at': 100.0, 'present': True}
    value.update(extra)
    return value


class TrainingView100Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = operator_profiles()
        cls.implemented = catalog()['operators']

    def choose(self, account, member, op=OP):
        before_account, before_member = copy.deepcopy(account), copy.deepcopy(member)
        result = select_training_view(op, account, member, self.profiles, self.implemented)
        self.assertEqual(account, before_account)
        self.assertEqual(member, before_member)
        return result

    def test_no_run_record_preserves_account(self):
        account = record('operator_profile')
        self.assertIs(self.choose(account, None)['state'], account)

    def test_departed_record_does_not_supply_training(self):
        account = record('operator_profile')
        member = record(fields={'elite': []}, present=False)
        self.assertIs(self.choose(account, member)['state'], account)

    def test_valid_run_fields_keep_priority_and_account_fill(self):
        account = record('operator_profile', fields={'elite': 2, 'trust': 25, 'potential': 2})
        member = record(fields={'level': 60, 'potential': 6}, ranks={'1': 10})
        result = self.choose(account, member)
        self.assertEqual(result['selection'], 'run_and_account')
        self.assertEqual(result['state']['fields'], {'elite': 2, 'trust': 25, 'potential': 6, 'level': 60})
        self.assertEqual(result['state']['run_confirmed_fields'], ['level', 'potential'])
        self.assertEqual(result['state']['skill_ranks'], {'1': 10})

    def test_account_ranks_are_not_filled_into_run_record(self):
        account = record('operator_profile', ranks={'1': 10})
        member = record(ranks={})
        result = self.choose(account, member)
        self.assertEqual(result['state']['skill_ranks'], {})

    def test_098_omitted_fields_behavior_remains_unconfirmed(self):
        member = record(ranks={})
        member.pop('fields')
        result = self.choose({}, member)
        self.assertEqual(result['selection'], 'run_and_account')
        self.assertEqual(result['state']['fields'], {})
        self.assertEqual(result['state']['run_confirmed_fields'], [])

    def test_implemented_ui_does_not_reject_unconsumed_member_identity_metadata(self):
        for identity in (None, False, 0, [], {}, 'public_opaque_id'):
            with self.subTest(identity=identity):
                member = record(id=identity)
                result = self.choose({}, member)
                self.assertEqual(result['selection'], 'run_and_account')
                self.assertIs(result['state']['id'], identity)
        member = record()
        member.pop('id')
        result = self.choose({}, member)
        self.assertEqual(result['selection'], 'run_and_account')
        self.assertNotIn('id', result['state'])

    def test_unsafe_elite_leaf_falls_back_without_mutating_original(self):
        for elite in ([], {}, '2', None, False, 99):
            with self.subTest(elite=elite):
                account = record('operator_profile')
                result = self.choose(account, record(fields={'elite': elite}))
                self.assertIs(result['state'], account)
                self.assertEqual(result['selection'], 'account_after_unusable_run')
                self.assertTrue(result['notice'])

    def test_masked_elite_and_level_do_not_reject_safe_run_facts(self):
        account = record('operator_profile')
        member = record(fields={'elite': [], 'level': 'ignored', 'potential': 6},
                        invalid_fields=['elite', 'level'])
        result = self.choose(account, member)
        self.assertEqual(result['selection'], 'run_and_account')
        self.assertEqual(result['state']['fields']['potential'], 6)
        self.assertEqual(result['state']['fields']['elite'], 2)

    def test_masked_active_rank_is_not_validated(self):
        for rank in ('bad', [], {}):
            with self.subTest(rank=rank):
                result = self.choose({}, record(ranks={'1': rank}, invalid_skill_ranks=['1']))
                self.assertEqual(result['selection'], 'run_and_account')
                self.assertEqual(result['state']['skill_ranks'], {})

    def test_unsafe_active_rank_is_qualified_before_indexing(self):
        for rank in ('7', [], {}, None, False, 0, 11):
            with self.subTest(rank=rank):
                result = self.choose({}, record(ranks={'1': rank}))
                self.assertEqual(result['selection'], 'account_after_unusable_run')

    def test_locked_formatter_safe_ranks_keep_original_native_types(self):
        for rank in (None, False, True, 0, -1, 1.0, 99):
            with self.subTest(rank=rank):
                member = record(fields={'elite': 0}, ranks={'3': rank})
                result = self.choose({}, member)
                self.assertEqual(result['selection'], 'run_and_account')
                self.assertEqual(result['state']['skill_ranks']['3'], rank)
                self.assertIs(type(result['state']['skill_ranks']['3']), type(rank))

    def test_locked_rank_context_from_account_is_checked_before_run_defaults(self):
        account = record('operator_profile', fields={'elite': 0}, ranks={'1': 7})
        member = record(fields={'potential': 6}, ranks={'3': 99})
        result = self.choose(account, member)
        self.assertEqual(result['selection'], 'run_and_account')
        self.assertEqual(result['state']['skill_ranks'], {'3': 99})

    def test_incompatible_account_fill_keeps_valid_run_only_context(self):
        # Both inputs separately satisfy the existing policy. Account E1 cannot
        # activate mastery8; a partial run with default E2 can safely consume it.
        account = record('operator_profile', fields={'elite': 1}, ranks={'1': 7})
        member = record(fields={'potential': 6}, ranks={'1': 8})
        result = self.choose(account, member)
        self.assertEqual(result['selection'], 'run_without_account')
        self.assertEqual(result['state']['fields'], {'potential': 6})
        self.assertEqual(result['state']['skill_ranks'], {'1': 8})
        self.assertEqual(result['state']['run_confirmed_fields'], ['potential'])

    def test_unused_selected_skill_and_opaque_extra_fields_remain_untouched(self):
        for preferred in (None, False, 0, 99, '1', [], {'ignored': True}):
            with self.subTest(preferred=preferred):
                member = record(fields={'elite': 0, 'selected_skill': preferred,
                                        'future_field': {'opaque': [None, False]}}, ranks={'1': 7})
                result = self.choose({}, member)
                self.assertEqual(result['selection'], 'run_and_account')
                self.assertIs(result['state']['fields']['selected_skill'], preferred)
                self.assertIs(result['state']['fields']['future_field'], member['fields']['future_field'])

    def test_falsy_module_identity_keeps_unused_stage(self):
        for module_id in (None, False, 0, '', [], {}):
            member = record(fields={'module_id': module_id, 'module_level': {'unused': True}})
            result = self.choose({}, member)
            self.assertEqual(result['selection'], 'run_and_account')
            self.assertIs(result['state']['fields']['module_level'], member['fields']['module_level'])

    def test_no_skill_profile_keeps_unused_rank_leaves(self):
        op = 'char_285_medic2'
        member = record(fields={'elite': 0, 'level': 30}, ranks={'1': {'unused': True}})
        member['id'] = op
        result = self.choose({}, member, op)
        self.assertEqual(result['selection'], 'run_and_account')
        self.assertEqual(result['state']['skill_ranks'], member['skill_ranks'])

    def test_safe_original_none_bool_timestamp_forms_are_preserved(self):
        # Negative timestamps differ across Windows/Linux localtime; they are
        # an actual-platform comparison in the Root acceptance matrix instead.
        for stamp in (None, False, True, 0, 100.5):
            with self.subTest(stamp=stamp):
                member = record(captured_at=stamp)
                result = self.choose({}, member)
                self.assertEqual(result['selection'], 'run_and_account')
                self.assertIs(result['state']['captured_at'], stamp)

    def test_invalid_consumed_timestamp_falls_back(self):
        for stamp in ('bad', [], {}, float('inf'), float('nan')):
            with self.subTest(stamp=stamp):
                member = record(captured_at=stamp)
                # NaN equality is not a suitable caller-immutability assertion.
                result = select_training_view(OP, {}, member, self.profiles, self.implemented)
                self.assertEqual(result['selection'], 'account_after_unusable_run')
                self.assertIs(member['captured_at'], stamp)

    def test_safe_numeric_level_clamping_inputs_do_not_become_account_schema_errors(self):
        # The actual Root Wine Qt probes separately record setter output.
        # Keep original field types here; the UI widget owns its old clamping.
        for level in (False, True, -1, 0, 1, 90, 91, 0.0, 1.0, 1.5, -1.5, 90.5, 91.9,
                      -(2 ** 31), 2 ** 31 - 1, -2147483648.9, -2147483648.5,
                      -2147483648.1, -2147483648.0, -2147483647.9,
                      2147483646.9, 2147483647.0, 2147483647.1,
                      2147483647.5, 2147483647.9, -0.9, 0.9):
            with self.subTest(level=level):
                member = record(fields={'elite': 2, 'level': level})
                result = self.choose({}, member)
                self.assertEqual(result['selection'], 'run_and_account')
                self.assertIs(result['state']['fields']['level'], level)

    def test_actual_binding_rejected_level_is_not_sent_to_set_value(self):
        for level in (None, '80', [], {}, -(2 ** 31) - 1, 2 ** 31,
                      -(2 ** 63), 2 ** 63 - 1, 10 ** 100, -10 ** 100,
                      1e100, -1e100, float('inf'), -float('inf'), float('nan'),
                      2147483648.0, 2147483648.1):
            with self.subTest(level=level):
                result = self.choose({}, record(fields={'level': level}))
                self.assertEqual(result['selection'], 'account_after_unusable_run')

    def test_unused_saved_level_under_user_override_does_not_reject_other_facts(self):
        for level in (None, '80', 80.0, [], {}, 2 ** 31, 10 ** 100):
            with self.subTest(level=level):
                member = record(fields={'elite': 2, 'level': level, 'potential': 6})
                result = select_training_view(OP, {}, member, self.profiles, self.implemented,
                                              use_record_level=False)
                self.assertEqual(result['selection'], 'run_and_account')
                self.assertEqual(result['state']['fields']['potential'], 6)
                self.assertIs(result['state']['fields']['level'], level)

    def test_valid_raw_run_summary_is_identical(self):
        member = record()
        self.assertEqual(format_run_training_observation(OP, member), format_operator_observation(member))

    def test_raw_summary_checks_actual_formatter_not_calculation_schema(self):
        member = record(fields={'elite': [], 'level': 'raw safe text'}, ranks={})
        self.assertEqual(format_run_training_observation(OP, member), format_operator_observation(member))

    def test_raw_summary_uses_known_selected_key_without_rewriting_metadata(self):
        member = record(id={'opaque': True})
        original_id = member['id']
        text = format_run_training_observation(OP, member)
        self.assertIn(self.profiles[OP]['name'], text)
        self.assertIs(member['id'], original_id)
        member.pop('id')
        self.assertIn(self.profiles[OP]['name'], format_run_training_observation(OP, member))
        self.assertNotIn('id', member)

    def test_unsafe_raw_rank_gets_explicit_unavailable_summary(self):
        member = record(ranks={'1': 'bad rank'})
        before = copy.deepcopy(member)
        text = format_run_training_observation(OP, member)
        self.assertIn('暂不可显示', text)
        self.assertIn('原记录未修改', text)
        self.assertEqual(member, before)

    def test_valid_run_metadata_survives_unsafe_cultivation_fallback(self):
        member = record(fields={'elite': []}, recruitment_kind='non_emergency',
                        char_buff_ids=['public_receipt_id'], char_buffs_complete=True,
                        char_buff_absent_ids=['public_absence'], char_buff_pending_ids=['public_pending'])
        selected = self.choose({}, member)
        self.assertEqual(selected['selection'], 'account_after_unusable_run')
        metadata = run_operator_metadata(member)
        self.assertIs(metadata, member)
        for key in ('recruitment_kind', 'char_buff_ids', 'char_buffs_complete',
                    'char_buff_absent_ids', 'char_buff_pending_ids'):
            self.assertIs(metadata[key], member[key])

    def test_disabled_run_training_does_not_supply_metadata(self):
        self.assertEqual(run_operator_metadata(record(), enabled=False), {})

    def test_departed_run_record_does_not_supply_metadata(self):
        self.assertEqual(run_operator_metadata(record(present=False)), {})

    def test_account_scope_does_not_supply_run_metadata(self):
        self.assertEqual(run_operator_metadata(record('operator_profile')), {})


if __name__ == '__main__':
    unittest.main()
