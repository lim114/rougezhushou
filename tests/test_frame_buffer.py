import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge.frame_buffer import FrameBuffer


def page(value=30, shape=(240, 400, 3), label='PAGE'):
    image = np.full(shape, value, dtype=np.uint8)
    cv2.putText(image, label, (15, 70), cv2.FONT_HERSHEY_SIMPLEX,
                1.2, (240, 220, 180), 2)
    return image


class FrameBufferTests(unittest.TestCase):
    def test_transient_pages_are_read_after_the_user_has_already_left(self):
        buffer = FrameBuffer(settle_seconds=0)
        # Recognition is busy while the capture callback observes three short
        # pages. No second visit, OCR, or user pause is needed to retrieve them.
        for index, label in enumerate(('OPERATOR', 'RELICS', 'MAP')):
            for repeat in range(3):
                buffer.offer(page(30 + index * 40, label=label),
                             index * .3 + repeat * .1, target={'hwnd': 7})
        result = [buffer.take() for _ in range(3)]
        self.assertEqual([round(f['captured_at'], 1) for f in result], [.2, .5, .8])
        self.assertTrue(all(f['target'] == {'hwnd': 7} for f in result))
        self.assertIsNone(buffer.take())
        self.assertEqual(buffer.stats()['deduplicated'], 6)

    def test_static_page_does_not_requeue_after_recognition(self):
        buffer = FrameBuffer(settle_seconds=0)
        image = page()
        buffer.offer(image, 1)
        self.assertIsNotNone(buffer.take())
        for index in range(2, 32):
            buffer.offer(image, index)
        self.assertIsNone(buffer.take())
        self.assertEqual(buffer.stats()['pending'], 0)
        manual = buffer.take(force=True)
        self.assertEqual(manual['captured_at'], 31)
        self.assertEqual(manual['seq'], 31)
        self.assertEqual(buffer.stats()['retained_frames'], 1)

    def test_single_short_frame_is_not_discarded_or_kept_waiting_forever(self):
        buffer = FrameBuffer(settle_seconds=.12)
        with patch('rouge.frame_buffer.time.monotonic', return_value=1):
            buffer.offer(page(), 10)
            self.assertIsNone(buffer.take())
        with patch('rouge.frame_buffer.time.monotonic', return_value=1.13):
            self.assertEqual(buffer.take()['captured_at'], 10)
        # A following distinct page makes the preceding candidate ready now.
        with patch('rouge.frame_buffer.time.monotonic', return_value=2):
            buffer.offer(page(90), 11)
            buffer.offer(page(160), 11.1)
            self.assertEqual(buffer.take()['captured_at'], 11)

    def test_same_page_sharper_representative_preserves_fifo(self):
        buffer = FrameBuffer(settle_seconds=0)
        image = page()
        # Tiny noise remains a near duplicate; it must not become a third page.
        noisy = image.copy()
        noisy[0, 0] += 1
        buffer.offer(image, 1)
        buffer.offer(noisy, 1.1)
        buffer.offer(page(100), 2)
        first, second = buffer.take(), buffer.take()
        self.assertLess(first['captured_at'], second['captured_at'])
        self.assertIsNone(buffer.take())

    def test_capacity_keeps_latest_duplicate_and_distinct_short_page(self):
        image_a, image_b, image_c = page(30), page(90), page(150)
        buffer = FrameBuffer(max_frames=3, max_bytes=image_a.nbytes * 3,
                             settle_seconds=0)
        for stamp, image in enumerate((image_a, image_b, image_a, image_c), 1):
            buffer.offer(image, stamp)
        frames = [buffer.take() for _ in range(3)]
        self.assertEqual([f['captured_at'] for f in frames], [2, 3, 4])
        self.assertEqual(buffer.stats()['overflow_duplicates'], 1)
        self.assertLessEqual(buffer.stats()['bytes'], image_a.nbytes * 3)

    def test_capacity_is_shared_with_latest_and_drops_oldest_when_needed(self):
        size = page().nbytes
        buffer = FrameBuffer(max_bytes=size * 2, max_frames=2, settle_seconds=0)
        for timestamp in range(1, 8):
            buffer.offer(page(timestamp * 20), timestamp)
            self.assertLessEqual(buffer.stats()['bytes'], size * 2)
            self.assertLessEqual(buffer.stats()['retained_frames'], 2)
        self.assertEqual([buffer.take()['captured_at'] for _ in range(2)], [6, 7])
        self.assertEqual(buffer.stats()['overflow'], 5)

    def test_short_distinct_page_survives_later_local_animation_overload(self):
        buffer = FrameBuffer(max_frames=4, settle_seconds=0)
        buffer.offer(page(30, label='OPERATOR'), 1)
        for index in range(30):
            animated = page(150, label='MAP')
            cv2.rectangle(animated, (20 + index * 5, 140),
                          (40 + index * 5, 160), (220, 100, 40), -1)
            buffer.offer(animated, 2 + index * .1)
        result = []
        while buffer.stats()['pending']:
            result.append(buffer.take())
        self.assertEqual(result[0]['captured_at'], 1)
        self.assertEqual(result[-1]['captured_at'], 4.9)
        self.assertEqual([f['captured_at'] for f in result],
                         sorted(f['captured_at'] for f in result))
        self.assertGreater(buffer.stats()['overflow_low_novelty'], 0)
        self.assertLessEqual(buffer.stats()['retained_frames'], 4)

    def test_one_frame_budget_still_automatically_exposes_latest_representative(self):
        buffer = FrameBuffer(max_frames=1, settle_seconds=0)
        sharper = np.full((240, 400, 3), 30, dtype=np.uint8)
        sharper[160, 160] = 255
        softer = sharper.copy()
        softer[160, 160] = 210
        buffer.offer(sharper, 1)
        buffer.offer(softer, 2)
        self.assertEqual(buffer.stats()['retained_frames'], 1)
        self.assertEqual(buffer.stats()['pending'], 1)
        self.assertEqual(buffer.take()['captured_at'], 2)

    def test_clear_invalidates_generation_without_reusing_sequence(self):
        buffer = FrameBuffer(settle_seconds=0)
        first_seq = buffer.offer(page(), 10)
        first = buffer.take()
        generation = buffer.clear()
        self.assertIsNone(buffer.take(force=True))
        second_seq = buffer.offer(page(), 1)
        second = buffer.take()
        self.assertGreater(second_seq, first_seq)
        self.assertGreater(generation, first['generation'])
        self.assertEqual(second['generation'], generation)

    def test_resolution_client_geometry_and_target_changes_are_candidates(self):
        buffer = FrameBuffer(settle_seconds=0)
        buffer.offer(page(), 1, [0, 0, 400, 240], {'hwnd': 1, 'pid': 7})
        buffer.offer(page(shape=(360, 640, 3)), 2,
                     [0, 0, 640, 360], {'hwnd': 1, 'pid': 7})
        buffer.offer(page(shape=(360, 640, 3)), 3,
                     [5, 10, 640, 360], {'hwnd': 1, 'pid': 7})
        buffer.offer(page(shape=(360, 640, 3)), 4,
                     [5, 10, 640, 360], {'hwnd': 2, 'pid': 8})
        self.assertEqual([buffer.take()['captured_at'] for _ in range(4)], [1, 2, 3, 4])

    def test_small_label_change_is_not_lost_in_global_image_difference(self):
        buffer = FrameBuffer(settle_seconds=0)
        first = page(shape=(1080, 1920, 3))
        second = first.copy()
        cv2.putText(second, '90', (1600, 900), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (220, 220, 220), 2)
        buffer.offer(first, 1)
        buffer.offer(second, 2)
        self.assertEqual([buffer.take()['captured_at'] for _ in range(2)], [1, 2])

    def test_offer_owns_pixels_and_outputs_cannot_mutate_the_latest(self):
        buffer = FrameBuffer(settle_seconds=0)
        original = page()
        expected = original.copy()
        buffer.offer(original, 1, [0, 0, 400, 240], {'hwnd': 1})
        original.fill(0)
        result = buffer.take()
        np.testing.assert_array_equal(result['image'], expected)
        result['image'].fill(0)
        result['target']['hwnd'] = 9
        result['client_rect'][0] = 99
        latest = buffer.take(force=True)
        np.testing.assert_array_equal(latest['image'], expected)
        self.assertEqual(latest['target']['hwnd'], 1)
        self.assertEqual(latest['client_rect'][0], 0)

    def test_oversized_black_and_stale_frames_do_not_replace_usable_latest(self):
        image = page()
        buffer = FrameBuffer(max_bytes=image.nbytes, settle_seconds=0)
        buffer.offer(image, 5)
        buffer.offer(page(shape=(480, 800, 3)), 6)
        buffer.offer(np.zeros_like(image), 7)
        buffer.offer(page(130), 4)
        self.assertEqual(buffer.latest()['captured_at'], 5)
        stats = buffer.stats()
        self.assertEqual(stats['oversized'], 1)
        self.assertEqual(stats['invalid'], 1)
        self.assertEqual(stats['out_of_order'], 1)
        self.assertLessEqual(stats['bytes'], image.nbytes)


if __name__ == '__main__':
    unittest.main()
