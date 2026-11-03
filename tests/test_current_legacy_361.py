import copy
import io
import unittest
from unittest.mock import patch
from rouge import current_legacy as model


class CurrentLegacy361Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = model.reference()
        assert cls.base is not None, 'The prepared candidate must be installed before execution.'

    def setUp(self): self.result = copy.deepcopy(self.base)

    def declared(self, **changes):
        values = {'origin_mode': 'NORMAL', 'origin_grade': 3, 'origin_failed': True,
                  'next_mode': 'NORMAL', 'next_grade': 3, 'next_started': False,
                  'prior_claim_consumed': False}
        return model.compare_failure_support(self.result, **(values | changes))

    def test_complete_fourteen_records_and_five_real_groups(self):
        data = self.result['data']
        self.assertEqual(len(model.rows(self.result)), 14)
        self.assertEqual({k: len(v['ids']) for k, v in data['groups'].items()},
                         {'cat': 3, 'dog': 3, 'cerberus': 1, 'feather': 6, 'hidden': 1})
        self.assertEqual([r['id'] for r in model.rows(self.result) if r['hidden_in_original']], [model.HIDDEN])
        self.assertIsNone(data['rows'][model.HIDDEN]['legacy_group_id'])
        self.assertTrue(all(r['source_unchanged_from_previous_fixed_snapshot'] for r in model.rows(self.result)))
        self.assertEqual(model.rows(self.result, 'invented'), [])

    def test_hidden_pointer_and_mode_grades_are_original_not_guessed(self):
        row = self.result['data']['rows'][model.HIDDEN]
        buff = row['relic']['buffs'][0]
        self.assertEqual(buff['key'], 'init_mode_relic')
        self.assertEqual({b['key']: b['valueStr'] for b in buff['blackboard']},
                         {'id': model.TARGET, 'cond_mode': 'NORMAL', 'cond_mode_grade': '0,1,2,3'})
        self.assertIsNone(row['seed_source_reference']); self.assertIsNone(row['startup_pointer'])
        doc = self.result['data']['failure_support_documentation']
        self.assertEqual(doc['revision'], 434554)
        self.assertIn('均需要位于', doc['plain_acquisition_and_remark'])
        self.assertIn('消耗收取判定', doc['plain_acquisition_and_remark'])

    def test_failure_and_receipt_grade_boundaries_are_independent(self):
        for origin in range(5):
            for receipt in range(5):
                result = self.declared(origin_grade=origin, next_grade=receipt)
                self.assertIs(result['listed_origin_match'], origin < 4)
                self.assertIs(result['listed_receipt_match'], receipt < 4)
                self.assertIsNone(result['actual_server_eligible'])
                self.assertIsNone(result['actual_received'])
                self.assertFalse(result['next_run_created'])

    def test_unknown_declarations_and_already_consumed_are_not_grants(self):
        result = model.compare_failure_support(self.result)
        self.assertIsNone(result['listed_origin_match']); self.assertIsNone(result['listed_receipt_match'])
        self.assertEqual(result['status'], 'conditions_incomplete')
        self.assertEqual(self.declared()['status'], 'listed_conditions_match_only')
        self.assertEqual(self.declared(origin_failed=False)['status'], 'failure_not_declared')
        self.assertEqual(self.declared(prior_claim_consumed=True)['status'], 'claim_already_declared_consumed')
        self.assertIsNone(self.declared(next_started=True)['actual_received'])

    def test_started_wrong_grade_warns_without_claiming_actual_consumption(self):
        result = self.declared(next_started=True, next_grade=4)
        self.assertEqual(result['status'], 'documented_check_consumption_risk')
        self.assertIsNone(result['actual_claim_consumed'])
        self.assertIsNone(result['actual_claim_exists'])
        text = model.player_text(self.result, model.HIDDEN, result)
        self.assertIn('仍会消耗这次收取判定', text)
        self.assertIn('没有确认实际消耗或发放', text)
        self.assertIn('主动放弃', text)

    def test_strict_input_guards_do_not_treat_bool_as_grade_or_integer_as_declaration(self):
        for kwargs in ({'origin_grade': True}, {'next_grade': 17}, {'origin_failed': 1},
                       {'next_started': 'yes'}, {'prior_claim_consumed': 0}, {'next_mode': 'MONTH_TEAM'},
                       {'origin_mode': 'OTHER', 'origin_grade': 0}, {'next_mode': 'OTHER', 'next_grade': 0}):
            self.assertIsNone(model.compare_failure_support(self.result, **kwargs))
        result = self.declared(next_mode='OTHER', next_grade=None)
        self.assertIs(result['listed_receipt_match'], False)

    def test_six_identical_named_feathers_keep_distinct_exact_targets_and_reverse_entries(self):
        rows = model.rows(self.result, 'feather')
        self.assertEqual(len({r['name'] for r in rows}), 1)
        self.assertEqual(len({r['startup_pointer']['choice_id'] for r in rows}), 6)
        for row in rows:
            pointer = row['startup_pointer']
            with patch.object(model, 'packet', return_value=self.result):
                for category, key in (('choices', pointer['choice_id']), ('relics', pointer['reward_item_id']), ('items', row['id'])):
                    self.assertEqual(model.locate(category, key)['legacy_id'], row['id'])
        self.assertEqual(sum(r['seed_source_reference']['documented_source_id'] for r in model.rows(self.result)
                             if r['seed_source_reference']), 4)
        self.assertEqual(len([r for r in model.rows(self.result) if r['seed_source_reference']]), 13)

    def test_difficulty_target_does_not_assign_a_run_and_hidden_has_no_seed_link(self):
        with patch.object(model, 'packet', return_value=self.result):
            target = model.locate('difficulty', 'NORMAL|3')
            self.assertEqual(target['legacy_id'], model.HIDDEN)
            self.assertNotIn('origin_grade', target); self.assertNotIn('next_grade', target)
            self.assertIsNone(model.locate('difficulty', 'MONTH_TEAM|0'))
            self.assertIsNone(model.locate('items', 'invented'))
        links = model.links(self.result, model.HIDDEN)
        self.assertNotIn('seed', {r['kind'] for r in links}); self.assertNotIn('startup', {r['kind'] for r in links})
        self.assertEqual([r['key'] for r in links if r['kind'] == 'difficulty'], ['NORMAL|' + str(i) for i in range(5)])

    def test_fresh_exact_source_links_reject_foreign_snapshot_and_requests(self):
        link = next(r for r in model.links(self.result, model.HIDDEN) if r['kind'] == 'item' and r['key'] == model.TARGET)
        with patch.object(model, 'packet', return_value=self.base):
            found = model.resolve_link(self.result, link, legacy_id=model.HIDDEN)
            self.assertEqual(found['original']['item']['id'], model.TARGET)
            self.assertFalse(found['run_updated'])
            self.assertIsNone(model.resolve_link(self.result, link | {'key': 'rogue_6_start_1'}, legacy_id=model.HIDDEN))
            changed = copy.deepcopy(self.result); changed['data']['rows'][model.HIDDEN]['name'] = 'foreign'
            self.assertIsNone(model.resolve_link(changed, link, legacy_id=model.HIDDEN))

    def test_seed_and_startup_provider_failures_do_not_fake_links_or_clear_hidden_reference(self):
        from rouge import seed_cultivation_planning, current_startup
        key = 'rogue_6_legacy_04'
        links = model.links(self.result, key)
        with patch.object(model, 'packet', return_value=self.base):
            with patch.object(seed_cultivation_planning, 'seed_cultivation_reference', side_effect=ValueError('bad source')):
                self.assertIsNone(model.resolve_link(self.result, next(r for r in links if r['kind'] == 'seed'), legacy_id=key))
            with patch.object(current_startup, 'packet', return_value=None):
                self.assertIsNone(model.resolve_link(self.result, next(r for r in links if r['kind'] == 'startup'), legacy_id=key))
            self.assertIn('两局', model.player_text(model.reference(), model.HIDDEN))

    def test_corrupt_manifest_and_current_source_drift_fail_closed(self):
        original_file = model.version._file
        class Damaged:
            def read_bytes(self): return b'{}'
        with patch.object(model.version, '_file', side_effect=lambda key: Damaged() if key == model.MANIFEST else original_file(key)):
            self.assertIsNone(model.packet())
        current = model.version.packet(); changed = copy.deepcopy(current)
        changed['current']['details']['relics'][model.HIDDEN]['buffs'][0]['blackboard'][2]['valueStr'] = '0,1,2,3,4'
        with patch.object(model.version, 'packet', return_value=changed): self.assertIsNone(model.packet())


if __name__ == '__main__': unittest.main()
