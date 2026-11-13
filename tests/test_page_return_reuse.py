"""Returning to a fully verified page must not repeat whole-page recognition."""
import unittest
from unittest.mock import Mock

import numpy as np

from rouge.recognition import ScreenReader


class PageReturnReuseTests(unittest.TestCase):
    def reader(self):
        reader = ScreenReader()
        reader._read = Mock(side_effect=lambda image, **kwargs: {
            'observed_at': 0, 'page': 'test', 'texts': [int(image[0, 0, 0])],
            'performance': {}})
        return reader

    def test_return_reuses_complete_facts_without_caller_mutations(self):
        reader = self.reader()
        first = np.zeros((20, 30, 3), np.uint8)
        other = first + 1
        result = reader.read(first)
        result['texts'][0] = 99
        reader.read(other)
        returned = reader.read(first.copy())
        self.assertEqual(reader._read.call_count, 2)
        self.assertEqual(returned['texts'], [0])
        self.assertEqual(returned['performance']['reuse'], 'exact_page_return')
        np.testing.assert_array_equal(reader._last_frame, first)
        self.assertEqual(reader._last_result['texts'], [0])
        self.assertEqual(reader.read(first)['performance']['reuse'], 'exact_frame')

    def test_changed_pixel_or_source_or_run_cannot_reuse_old_page(self):
        for changed in ('pixel', 'rect', 'source', 'run', 'config'):
            with self.subTest(changed=changed):
                reader = self.reader()
                first = np.zeros((20, 30, 3), np.uint8)
                options = {'client_rect': [0, 0, 30, 20], 'hud_source': (1, 2, 3),
                           'run_context': {'run_id': 'a', 'config': {}}}
                reader.read(first, **options)
                reader.read(first + 1, **options)
                if changed == 'pixel':first[-1, -1, -1] = 1
                if changed == 'rect':options['client_rect'] = [1, 0, 30, 20]
                if changed == 'source':options['hud_source'] = (2, 2, 3)
                if changed == 'run':options['run_context']['run_id'] = 'b'
                if changed == 'config':
                    options['run_context']['config']['difficulty'] = {'value': 3, 'captured_at': 1}
                self.assertEqual(reader.read(first, **options)['performance']['reuse'], 'none')
                self.assertEqual(reader._read.call_count, 3)

    def test_old_pages_are_evicted_and_disabled_cache_recomputes(self):
        for enabled in (True, False):
            reader = self.reader()
            reader.cache_enabled = enabled
            image = np.zeros((20, 30, 3), np.uint8)
            for number in range(5):reader.read(image + number)
            self.assertEqual(reader.read(image)['performance']['reuse'], 'none')
            self.assertEqual(reader._read.call_count, 6)

    def test_completed_fork_preserves_returns_without_sharing_mutable_results(self):
        reader = self.reader()
        image = np.zeros((20, 30, 3), np.uint8)
        reader.read(image)
        reader.read(image + 1)
        sibling = reader.fork()
        result = sibling.read(image)
        self.assertEqual(result['performance']['reuse'], 'exact_page_return')
        result['texts'][0] = 99
        self.assertEqual(reader.read(image)['texts'], [0])

    def test_changed_frame_after_return_uses_returned_page_as_preview_source(self):
        reader = self.reader()
        image = np.zeros((20, 30, 3), np.uint8)
        reader.read(image)
        reader.read(image + 1)
        reader.read(image)
        changed = image.copy()
        changed[-1, -1] = 2
        reader.read(changed, on_hud=lambda _: None)
        self.assertEqual(reader._read.call_args.kwargs['gold_seed']['texts'], [0])

    def test_pixel_storage_obeys_byte_budget(self):
        reader = self.reader()
        reader._page_results.max_bytes = 2000
        image = np.zeros((20, 30, 3), np.uint8)
        reader.read(image)
        reader.read(image + 1)
        self.assertLessEqual(reader._page_results.bytes, 2000)
        self.assertEqual(reader.read(image)['performance']['reuse'], 'none')


if __name__ == '__main__':unittest.main()
