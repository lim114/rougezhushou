"""A completed reader can seed concurrent reads without sharing mutable state."""
from concurrent.futures import ThreadPoolExecutor
import unittest

import cv2
import numpy as np

from rouge.recognition import ScreenReader


def facts(value):
    if isinstance(value, dict):
        return {key: facts(item) for key, item in value.items()
                if key not in ('performance', 'observed_at', 'elapsed_ms')}
    if isinstance(value, list):return [facts(item) for item in value]
    return value


class ReaderForkTests(unittest.TestCase):
    def test_completed_snapshot_keeps_exact_results_and_isolates_concurrent_changes(self):
        images = []
        for text in ('12345', '9988', '7001'):
            image = np.full((600, 1000, 3), 220, np.uint8)
            cv2.putText(image, text, (180, 280), cv2.FONT_HERSHEY_SIMPLEX, 2, (20, 20, 20), 3)
            images.append(image)
        reader = ScreenReader(page_routing_enabled=False)
        initial = reader.read(images[0])
        sibling = reader.fork()
        self.assertEqual(facts(sibling.read(images[0])), facts(initial))
        self.assertIsNot(reader._last_frame, sibling._last_frame)
        self.assertIsNot(reader._engine.cache.entries, sibling._engine.cache.entries)
        self.assertIsNot(reader._engine.engine.text_det, sibling._engine.engine.text_det)
        self.assertIs(reader._engine.engine.text_rec.session, sibling._engine.engine.text_rec.session)
        expected = [facts(reader.fork().read(image)) for image in images[1:]]
        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(instance.read, image)
                       for instance, image in zip((reader, sibling), images[1:])]
            actual = [facts(future.result()) for future in futures]
        self.assertEqual(actual, expected)
        np.testing.assert_array_equal(reader._last_frame, images[1])
        np.testing.assert_array_equal(sibling._last_frame, images[2])


if __name__ == '__main__':unittest.main()
