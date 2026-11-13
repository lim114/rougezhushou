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
    def test_newer_only_take_leaves_historical_candidates_for_the_other_reader(self):
        buffer = FrameBuffer(settle_seconds=0)
        for i in range(3):buffer.offer(page(30 + i * 50), i)
        self.assertEqual(buffer.take(prefer_latest=True)['seq'], 3)
        self.assertIsNone(buffer.take(prefer_latest=True, after_seq=3))
        self.assertEqual(buffer.stats()['pending'], 2)
        buffer.offer(page(200), 4)
        self.assertEqual(buffer.take(prefer_latest=True, after_seq=3)['seq'], 4)
        self.assertEqual([buffer.take()['seq'], buffer.take()['seq']], [1, 2])
        self.assertIsNone(buffer.take(force=True, after_seq=4))

    def test_dedup_tracks_source_shape_across_sizes_and_color_modes(self):
        # The first two sizes produce the same resized width and height.
        buffer = FrameBuffer(settle_seconds=0)
        shapes = [(321, 641), (322, 643), (322, 643, 3), (17, 29, 3), (17, 29)]
        for index, shape in enumerate(shapes):
            pixels = np.full(shape, 80, dtype=np.uint8)
            buffer.offer(pixels, 2 * index)
            buffer.offer(pixels.copy(), 2 * index + 1)
        self.assertEqual(buffer.stats()['deduplicated'], len(shapes))
        for index, shape in enumerate(shapes):
            frame = buffer.take()
            self.assertEqual(frame['image'].shape, shape)
            self.assertEqual(frame['captured_at'], 2 * index + 1)
        self.assertIsNone(buffer.take())

    def test_take_transfers_only_the_popped_older_image(self):
        copies=[]
        class TrackedImage(np.ndarray):
            def copy(self,*args,**kwargs):
                copies.append(self.nbytes)
                return super().copy(*args,**kwargs)
        buffer=FrameBuffer(settle_seconds=0)
        first=page(30).view(TrackedImage)
        last=page(130).view(TrackedImage)
        buffer.offer(first,1);buffer.offer(last,2)
        self.assertEqual(len(copies),2)
        result=buffer.take()
        self.assertEqual(len(copies),2)
        result['image'][:]=0
        self.assertTrue(first.any())
        result=buffer.take()
        self.assertEqual(len(copies),3)
        result['image'][:]=0
        np.testing.assert_array_equal(buffer.take(force=True)['image'],last)

    def test_pointer_exclusion_belongs_to_retained_frame_not_latest_mouse(self):
        buffer=FrameBuffer(settle_seconds=0);bounds=[4,8,28,40]
        buffer.offer(page(30),1,pointer_bounds=bounds)
        bounds[0]=100
        buffer.offer(page(130),2,pointer_bounds=[50,60,80,100])
        first=buffer.take();last=buffer.latest()
        self.assertEqual(first['pointer_bounds'],(4,8,28,40))
        self.assertEqual(last['pointer_bounds'],(50,60,80,100))

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
            self.assertAlmostEqual(buffer.stats()['settle_remaining_ms'], 120)
            self.assertEqual(buffer.latest(settling_only=True)['captured_at'], 10)
            self.assertIsNone(buffer.take())
        with patch('rouge.frame_buffer.time.monotonic', return_value=1.13):
            self.assertEqual(buffer.stats()['settle_remaining_ms'], 0)
            self.assertIsNone(buffer.latest(settling_only=True))
            self.assertEqual(buffer.take()['captured_at'], 10)
        # A following distinct page makes the preceding candidate ready now.
        with patch('rouge.frame_buffer.time.monotonic', return_value=2):
            buffer.offer(page(90), 11)
            buffer.offer(page(160), 11.1)
            self.assertIsNone(buffer.latest(settling_only=True))
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

    def test_eviction_compares_each_adjacent_pair_once(self):
        buffer = FrameBuffer(max_frames=3, settle_seconds=0)
        for index, value in enumerate((30, 90, 150)):
            buffer.offer(page(value), index)
        with patch.object(buffer, '_distance', wraps=buffer._distance) as distance:
            buffer.offer(page(210), 3)
        pairs = [(call.args[0]['seq'], call.args[1]['seq']) for call in distance.call_args_list]
        self.assertEqual(pairs, [(1,2),(2,3),(3,4)])

    def test_same_reference_and_representative_need_one_similarity_check(self):
        buffer = FrameBuffer(settle_seconds=0)
        image = page(90)
        buffer.offer(image, 1)
        with patch.object(buffer, '_similar', wraps=buffer._similar) as compare:
            buffer.offer(image.copy(), 2)
        compare.assert_called_once()
        self.assertEqual(buffer.take()['captured_at'], 2)

    def test_replaced_representative_still_needs_its_own_comparison(self):
        buffer = FrameBuffer(settle_seconds=0)
        for timestamp, shade in enumerate((100, 101, 99), 1):
            buffer.offer(np.full((80, 80, 3), shade, dtype=np.uint8), timestamp)
        # Both later frames are near 100, but 99 is too far from 101 to replace it.
        self.assertEqual(buffer.take()['captured_at'], 2)
        self.assertEqual(buffer.latest()['captured_at'], 3)

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
