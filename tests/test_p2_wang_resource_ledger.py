import unittest
from copy import deepcopy

from rouge.p2_wang_resource_ledger import (POOLS, format_wang_resource_ledger,
    source_data, wang_resource_ledger, wang_resource_reference)


def snapshot(name='start', **values):
    return {'snapshot_id': name, 'stock': 4, 'manual_active': 0,
            'extra_active': 0, 'currency': 20, 'sp': 40, **values}


def manual(identity='manual', **values):
    return {'id': identity, 'kind': 'manual_receipt', 'stock_spent': 1,
            'manual_created': 1, 'extra_created': 1, 'currency_spent': 3,
            'sp_spent': 0, **values}


def skill(identity='skill', **values):
    return {'id': identity, 'kind': 'skill_receipt', 'accepted_stock': 2,
            'sp_spent': 16, **values}


def loss(identity='loss', **values):
    return {'id': identity, 'kind': 'loss_receipt', 'manual_lost': 1,
            'extra_lost': 1, 'stock_returned': 0, 'currency_returned': 0,
            'sp_returned': 0, **values}


class WangResourceLedgerTests(unittest.TestCase):
    def test_primary_candidates_keep_projectiles_out_of_manual_pool(self):
        for elite, potential, manual_cap, stock_cap, extra in [
            (0, 1, 4, 5, 0), (0, 3, 5, 6, 0), (1, 1, 5, 6, 8),
            (1, 3, 6, 7, 9), (2, 1, 6, 7, 9), (2, 3, 7, 8, 10)]:
            with self.subTest(elite=elite, potential=potential):
                r = wang_resource_reference({'elite': elite, 'potential': potential})
                self.assertEqual((r['manual_limit_reference'], r['stock_limit_reference'],
                                  r['base_extra_limit_parameter'], r['extra_limit_reference']),
                                 (manual_cap, stock_cap, extra, extra))
                self.assertIn('弹道', r['separate_entity_evidence']['quote'])
                self.assertIn('attack@max_spawn_cnt', str(r['talent_source']['raw']))
                self.assertIsNone(r['actual_presence'])

    def test_s1_and_s2_all_ranks_have_two_nominal_grants_and_exact_sp(self):
        for selected, expected in [(1, [22, 22, 22, 21, 21, 21, 20, 19, 18, 16]),
                                   (2, [18, 18, 18, 17, 17, 17, 16, 16, 16, 15])]:
            for rank in range(1, 11):
                with self.subTest(skill=selected, rank=rank):
                    r = wang_resource_reference({}, selected, rank)
                    self.assertEqual(r['nominal_stock_grant'], 2)
                    self.assertEqual(r['sp_cost_parameter'], expected[rank - 1])
                    self.assertIn(f'levels[{rank - 1}]', r['skill_source']['selector'])

    def test_module_changes_known_card_counts_but_not_unknown_projectile_pool(self):
        for level, applied, manual_cap, stock_cap, extra in [(59, False, 6, 7, 9),
                                                             (60, True, 7, 7, None)]:
            r = wang_resource_reference({'elite': 2, 'level': level,
                                         'module_id': 'uniequip_002_wang', 'module_level': 1})
            self.assertEqual(r['module_applied'], applied)
            self.assertEqual((r['manual_limit_reference'], r['stock_limit_reference'], r['extra_limit_reference']),
                             (manual_cap, stock_cap, extra))
        r = wang_resource_reference({'potential': 3, 'module_id': 'uniequip_002_wang', 'module_level': 3})
        self.assertEqual((r['manual_limit_reference'], r['stock_limit_reference']), (8, 8))
        self.assertEqual(r['manual_cost_reference'], 2)
        self.assertIsNone(r['extra_limit_reference'])

    def test_sequence_balances_five_independent_pools_without_invented_refunds(self):
        p = {'initial': snapshot(), 'steps': [manual(), skill(), loss()]}
        r = wang_resource_ledger({}, p, rank=10)
        self.assertEqual(r['final'], {'stock': 5, 'manual_active': 0, 'extra_active': 0,
                                      'currency': 17, 'sp': 24})
        self.assertEqual(r['rows'][0]['after']['extra_active'], 1)
        self.assertEqual(r['rows'][0]['after']['manual_active'], 1)
        self.assertEqual(r['rows'][2]['after']['stock'], 5)
        self.assertTrue(all(row['actual_clock'] is None for row in r['rows']))
        self.assertEqual(r['actual_final'], dict.fromkeys(POOLS))

    def test_declared_failed_creation_does_not_imply_free_or_refunded(self):
        failed = manual(manual_created=0, extra_created=0, stock_spent=1, currency_spent=2)
        r = wang_resource_ledger({}, {'initial': snapshot(), 'steps': [failed]})
        self.assertEqual((r['final']['stock'], r['final']['currency']), (3, 18))
        self.assertEqual((r['final']['manual_active'], r['final']['extra_active']), (0, 0))
        unknown = manual(manual_created=0, extra_created=0, stock_spent=None, currency_spent=None)
        r = wang_resource_ledger({}, {'initial': snapshot(), 'steps': [unknown]})
        self.assertIsNone(r['final']['stock']); self.assertIsNone(r['final']['currency'])

    def test_skill_acceptance_and_cap_crossing_are_distinct_and_never_clipped(self):
        for accepted, after in [(0, 7), (1, 8), (2, 9), (None, None)]:
            with self.subTest(accepted=accepted):
                r = wang_resource_ledger({}, {'initial': snapshot(stock=7),
                                             'steps': [skill(accepted_stock=accepted)]}, rank=10)
                self.assertEqual(r['rows'][0]['nominal_stock_grant'], 2)
                self.assertEqual(r['final']['stock'], after)
                self.assertEqual(r['rows'][0]['accepted_stock_declared'], accepted)
                self.assertEqual(r['rows'][0]['within_reference']['stock'], None if after is None else after <= 7)
        r = wang_resource_ledger({}, {'initial': snapshot(extra_active=9, manual_active=1),
                                     'steps': [manual(extra_created=1)]})
        self.assertFalse(r['rows'][0]['within_reference']['extra_active'])
        self.assertTrue(r['rows'][0]['within_reference']['manual_active'])
        self.assertEqual(r['final']['extra_active'], 10)

    def test_unknown_pool_survives_later_zero_or_known_receipts(self):
        r = wang_resource_ledger({}, {'initial': snapshot(stock=None),
                                     'steps': [manual(), skill(), loss(stock_returned=1)]}, rank=10)
        self.assertTrue(all(row['after']['stock'] is None for row in r['rows']))
        self.assertEqual((r['final']['manual_active'], r['final']['extra_active'], r['final']['currency'], r['final']['sp']),
                         (0, 0, 17, 24))

    def test_negative_balance_blocks_following_chain_until_named_independent_snapshot(self):
        p = {'initial': snapshot(currency=2), 'steps': [manual(), skill(),
             {'id': 'observed', 'kind': 'snapshot', 'state': snapshot('new-independent', stock=2)},
             manual('after-observation')]}
        r = wang_resource_ledger({}, p, rank=10)
        self.assertEqual([row['status'] for row in r['rows']],
                         ['contradicted_declaration', 'blocked_after_contradiction', 'independent_snapshot', 'declared_balance'])
        self.assertEqual(r['rows'][0]['contradictions'], ['currency'])
        self.assertEqual(r['rows'][1]['after'], dict.fromkeys(POOLS))
        self.assertEqual(r['final_segment_id'], 'new-independent')
        self.assertEqual((r['final']['stock'], r['final']['manual_active']), (1, 1))
        self.assertFalse(r['chain_blocked'])

    def test_snapshot_names_and_receipt_schema_cannot_accidentally_resume_chain(self):
        cases = [
            [manual(), manual()],
            [{'id': 'x', 'kind': 'snapshot', 'state': snapshot()}],
            [{'id': 'x', 'kind': 'snapshot', 'state': {'snapshot_id': 'new'}}],
            [dict(manual(), returned_stock=1)],
            [dict(skill(), accepted_stock=3)],
            [dict(manual(), manual_created=2)],
            [dict(loss(), stock_returned=True)],
            [dict(skill(), accepted_stock='2')],
            [dict(skill(), sp_spent=-1)],
            [dict(skill(), sp_spent=1.0)],
        ]
        for steps in cases:
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                wang_resource_ledger({}, {'initial': snapshot(), 'steps': steps})

    def test_s3_unknown_cultivation_and_locked_skills_rejected(self):
        for training, selected, rank in [({}, 3, 1), ({'elite': 0}, 2, 1),
                                          ({'elite': 1}, 1, 8), ({'potential': True}, 1, 1),
                                          ({'module_id': None, 'module_level': 1}, 1, 1),
                                          ({'module_id': '', 'module_level': 0}, 1, 1),
                                          ({'module_id': 'other', 'module_level': 1}, 1, 1),
                                          ({'trust': True}, 1, 1), ({'live_stock': 3}, 1, 1),
                                          ({}, True, 1), ({}, 1, 0)]:
            with self.subTest(training=training, selected=selected, rank=rank), self.assertRaises(ValueError):
                wang_resource_reference(training, selected, rank)

    def test_declared_sp_is_independent_of_the_nominal_cost(self):
        r = wang_resource_ledger({}, {'initial': snapshot(),
                                     'steps': [skill(sp_spent=0), skill('second', sp_spent=None)]}, rank=10)
        self.assertFalse(r['rows'][0]['sp_spent_matches_parameter'])
        self.assertEqual(r['rows'][0]['after']['sp'], 40)
        self.assertIsNone(r['final']['sp']); self.assertEqual(r['final']['stock'], 8)

    def test_results_and_source_records_are_independent_copies(self):
        training = {'elite': 2, 'potential': 3}
        preview = {'initial': snapshot(), 'steps': [manual(), skill()]}
        before = deepcopy((training, preview, source_data()))
        result = wang_resource_ledger(training, preview, skill=2, rank=10)
        result['reference']['skill_source']['raw']['blackboard'][0]['value'] = 1234
        result['preview']['steps'][0]['manual_created'] = 100
        self.assertEqual((training, preview, source_data()), before)
        text = format_wang_resource_ledger(wang_resource_ledger(training, preview, skill=2, rank=10))
        self.assertIn('跟子弹道', text); self.assertIn('不自动', text); self.assertIn('实际入库', text)


if __name__ == '__main__':
    unittest.main()
