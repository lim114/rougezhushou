from unittest import TestCase
from unittest.mock import patch
from rouge import bounded_calibration as bounded, paired_calibration as paired


class BoundedEntryReuseTests(TestCase):
    def test_combined_entry_validates_each_tolerance_once_and_reuses_record_shape(self):
        payload = bounded.public_bounded_payload()
        with patch.object(bounded, '_number', wraps=bounded._number) as check, patch.object(paired, '_record', side_effect=AssertionError('duplicate shape check')):
            result = bounded.bounded_calibration(**payload)
        self.assertIsNotNone(result['panel'])
        self.assertIsNotNone(result['timing'])
        labels = [call.args[1] for call in check.call_args_list]
        self.assertEqual(labels.count('明确面板容差'), 1)
        self.assertEqual(labels.count('明确秒数容差'), 1)
        self.assertNotIn('面板容差', labels)

    def test_unused_channel_tolerance_still_validated(self):
        payload = bounded.public_bounded_payload()
        with self.assertRaises(ValueError):
            bounded.bounded_calibration(panel=payload['panel'], timing_tolerance_seconds=-1)
        with self.assertRaises(ValueError):
            bounded.bounded_calibration(timing=payload['timing'], panel_tolerance=-1)

    def test_independent_entries_keep_input_checks(self):
        payload = bounded.public_bounded_payload()
        with self.assertRaises(ValueError):
            bounded.compare_bounded_panels(**payload['panel'], tolerance=-1)
        with self.assertRaises(ValueError):
            bounded.compare_bounded_timing(**payload['timing'], tolerance_seconds=-1)
        with self.assertRaises(ValueError):
            paired.compare_paired_panels({}, {})
