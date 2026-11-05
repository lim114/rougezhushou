"""Output annotation consumes an existing clock without rebuilding its input."""
import unittest
from unittest.mock import patch
from rouge import timing


class TimingAnnotationEntryTests(unittest.TestCase):
    def test_existing_clock_retains_identity_and_notes_without_reconstruction(self):
        scenario = {'operator': 'mechanist', 'skill': 1, 'timing_mode': 'continuous'}
        clock = {'mode': 'continuous', 'target_scope_notes': ['已计算的目标条件']}
        result = {'timing': clock, 'estimate': {'notes': []}}
        with patch.object(timing, 'AttackTimeline', wraps=timing.AttackTimeline) as constructor:
            timing.annotate_result(scenario, result)
        constructor.assert_not_called()
        self.assertIs(result['timing'], clock)
        self.assertEqual(result['estimate']['notes'], ['已计算的目标条件'])

    def test_missing_clock_is_built_once(self):
        scenario = {'operator': 'mechanist', 'skill': 1, 'timing_mode': 'continuous'}
        result = {'estimate': {'notes': []}}
        with patch.object(timing, 'AttackTimeline', wraps=timing.AttackTimeline) as constructor:
            timing.annotate_result(scenario, result)
        constructor.assert_called_once_with(scenario)
        self.assertEqual(result['timing']['mode'], 'continuous')


if __name__ == '__main__':
    unittest.main()
