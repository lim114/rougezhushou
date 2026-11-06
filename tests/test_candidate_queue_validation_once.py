from collections import Counter
from copy import deepcopy
from unittest.mock import patch
import unittest
from rouge import current_spawn_candidates as model
from tests.test_current_spawn_candidates_355 import make_current, relation_action


class CandidateQueueValidationOnceTests(unittest.TestCase):
    def setUp(self):
        level = {'waves': [{'fragments': [{'actions': [
            relation_action('one', group='g', package='p'),
            relation_action('two', group='g', package='p'),
        ]}]}], 'branches': {}}
        self.current = make_current('test', level)

    def test_each_action_and_queue_checked_once_for_both_relations(self):
        objects = {id(a[key]): (a['key'], key) for a in self.current['actions'] for key in ('raw', 'queue')}
        calls = Counter()
        original = model._same
        def same(left, right):
            if id(left) in objects:
                calls[objects[id(left)]] += 1
            return original(left, right)
        with patch.object(model, '_same', same):
            relations, _ = model._build(self.current, {})
        self.assertEqual(calls, Counter({key: 1 for key in objects.values()}))
        for kind in ('group', 'package'):
            self.assertEqual([m['action_key'] for m in relations[kind][0]['members']], ['0', '1'])

    def test_mismatched_raw_and_queue_still_rejected(self):
        for field in ('raw', 'queue'):
            current = deepcopy(self.current)
            current['actions'][0][field]['unexpected'] = True
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'original queue'):
                model._build(current, {})
