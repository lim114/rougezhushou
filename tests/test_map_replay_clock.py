import unittest

from scripts.measure_map_replay_clock import measure


class ReplayClockTests(unittest.TestCase):
    def test_counts_from_visible_onset_with_skipped_source_frames(self):
        shown = [(0, 8.0), (5, 8.18), (7, 8.24), (12, 8.41)]
        result = measure(shown, 8.01, 690, 6, 12)
        self.assertEqual(result, {'onset_shown_frame': 7, 'onset_to_window_ms': 460,
                                  'clear_shown_frame': 12, 'clear_to_window_ms': 290})

    def test_does_not_count_a_clip_without_a_visible_transition(self):
        with self.assertRaises(ValueError):
            measure([(7, 8.1), (12, 8.4)], 8, 800, 6, 12)
        with self.assertRaises(ValueError):
            measure([(0, 8), (1, 8.1)], 8, 800, 6, 12)

    def test_allows_correct_window_before_fully_opaque_source(self):
        result = measure([(0, 8), (6, 8.2), (12, 8.4)], 8, 350, 6, 12)
        self.assertEqual(result['clear_to_window_ms'], -50)
