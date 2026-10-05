"""Current full detection guards the region-prioritized OCR batch cache."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import numpy as np

from rouge.page_ocr import PageOCR


class _Recognizer:
    rec_batch_num = 2
    rec_image_shape = (3, 4, 8)

    def __init__(self):
        self.calls = []

    def resize_norm_img(self, crop, max_ratio):
        # The recognizable score deliberately depends on batch padding width.
        return np.full((3, 4, int(4*max_ratio)), int(crop[0, 0, 0]), np.float32)

    def session(self, tensor):
        self.calls.append(tensor.copy())
        return [tensor]

    def postprocess_op(self, predictions, word_box, *, wh_ratio_list, max_wh_ratio):
        return [(str(int(row[0, 0, 0])), .5+max_wh_ratio/1000)
                for row in predictions]


class _Provider:
    use_det = True
    use_rec = True
    use_cls = True
    text_score = .5
    max_side_len = 2000
    min_side_len = 30
    min_height = 10
    width_height_ratio = 8

    def __init__(self):
        self.text_rec = _Recognizer()
        self.crops = [np.full((10, width, 3), 10+i, np.uint8)
                      for i, width in enumerate((50, 10, 30, 20, 40))]
        self.boxes = [np.array([[x, 5], [x+6, 5], [x+6, 15], [x, 15]], np.float32)
                      for x in (10, 30, 50, 70, 90)]
        self.detection_calls = 0
        self.classification_calls = 0
        self.whole_calls = []
        self.rotate = False

    def load_img(self, image):
        return image

    def preprocess(self, image):
        return image, 1., 1.

    def maybe_add_letterbox(self, image, operations):
        return image, operations

    def auto_text_det(self, image):
        self.detection_calls += 1
        return deepcopy(self.boxes), .03

    def get_crop_img_list(self, image, boxes):
        return deepcopy(self.crops)

    def text_cls(self, crops):
        self.classification_calls += 1
        if self.rotate:
            crops = [np.flip(a, (0, 1)).copy() for a in crops]
        return crops, [['0', .99] for _ in crops], .01

    def _get_origin_points(self, boxes, operations, h, w):
        return np.array(boxes, np.float32)

    def get_final_res(self, boxes, cls_res, rec_res, det, cls, rec):
        result = [[box.tolist(), *value] for box, value in zip(boxes, rec_res)
                  if value[1] >= self.text_score]
        return result or None, [det, cls, rec]

    def __call__(self, image, **kwargs):
        self.whole_calls.append(kwargs)
        return [[[[1, 1], [2, 1], [2, 2], [1, 2]], 'full', .99]], [0.1]


class PageDetectedBatchTests(unittest.TestCase):
    def reader(self, **kwargs):
        provider = _Provider()
        reader = PageOCR(provider, **kwargs)
        reader._supported = lambda: True
        return reader, provider

    def test_first_call_uses_current_whole_detector_and_keeps_exterior_text(self):
        reader, p = self.reader()
        result, _ = reader(np.zeros((50, 120, 3), np.uint8), regions=[[8, 0, 18, 20]])
        self.assertEqual(p.detection_calls, 1)
        self.assertEqual(p.classification_calls, 1)
        self.assertEqual([r[1] for r in result], ['10', '11', '12', '13', '14'])
        self.assertEqual(reader.metrics['page_boxes'], 1)
        self.assertEqual(reader.metrics['guard_boxes'], 4)
        self.assertEqual(reader.metrics['recognized_boxes'], 5)
        self.assertTrue(reader.metrics['full_detection'])
        self.assertEqual(p.whole_calls, [])

    def test_priority_preserves_original_global_padding_batches_and_final_order(self):
        reader, p = self.reader()
        result, _ = reader(np.zeros((50, 120, 3), np.uint8), regions=[[8, 0, 18, 20]])
        # Global ratio order is crop indices [1, 3, 2, 4, 0]; original batches
        # remain [1,3], [2,4], [0]. The page batch [0] executes first.
        self.assertEqual([list(a[:, 0, 0, 0]) for a in p.text_rec.calls],
                         [[10], [11, 13], [12, 14]])
        self.assertEqual([r[2] for r in result], [.505, .502, .504, .502, .504])

    def test_exact_crop_batches_reuse_while_detector_still_reads_every_frame(self):
        reader, p = self.reader()
        frame = np.zeros((50, 120, 3), np.uint8)
        before, _ = reader(frame, regions=[[8, 0, 18, 20]])
        frame[40:, :] = 255  # Unrelated animation cannot bypass text discovery.
        after, _ = reader(frame, regions=[[8, 0, 18, 20]])
        self.assertEqual(before, after)
        self.assertEqual(p.detection_calls, 2)
        self.assertEqual(len(p.text_rec.calls), 3)
        self.assertEqual(reader.metrics['reused_batches'], 3)

    def test_current_exterior_text_change_is_recognized_without_old_value(self):
        reader, p = self.reader()
        frame = np.zeros((50, 120, 3), np.uint8)
        reader(frame, regions=[[8, 0, 18, 20]])
        p.crops[2][:] = 67
        result, _ = reader(frame, regions=[[8, 0, 18, 20]])
        self.assertEqual(result[2][1], '67')
        self.assertEqual(reader.metrics['recognized_batches'], 1)
        self.assertEqual(reader.metrics['recognized_boxes'], 2)
        self.assertEqual(reader.metrics['reused_batches'], 2)

    def test_new_exterior_overlay_is_returned_in_current_detector_order(self):
        reader, p = self.reader()
        frame = np.zeros((50, 120, 3), np.uint8)
        reader(frame, regions=[[8, 0, 18, 20]])
        p.crops.append(np.full((10, 70, 3), 99, np.uint8))
        p.boxes.append(np.array([[100, 30], [115, 30], [115, 40], [100, 40]], np.float32))
        result, _ = reader(frame, regions=[[8, 0, 18, 20]])
        self.assertEqual(result[-1][1], '99')
        self.assertEqual(reader.metrics['guard_boxes'], 5)
        self.assertEqual(reader.metrics['detected_boxes'], 6)

    def test_current_moved_boxes_use_current_coordinates_even_when_crop_is_identical(self):
        reader, p = self.reader()
        frame = np.zeros((50, 120, 3), np.uint8)
        reader(frame)
        p.boxes[1][:, 1] += 7
        result, _ = reader(frame)
        self.assertEqual(result[1][0], p.boxes[1].tolist())
        self.assertEqual(reader.metrics['reused_batches'], 3)

    def test_missing_current_boxes_does_not_emit_prior_cached_text(self):
        reader, p = self.reader()
        frame = np.zeros((50, 120, 3), np.uint8)
        reader(frame)
        p.boxes = p.crops = []
        result, _ = reader(frame)
        self.assertIsNone(result)
        self.assertEqual(reader.metrics['detected_boxes'], 0)

    def test_force_discovery_and_provider_configuration_change_bypass_cache(self):
        reader, p = self.reader()
        frame = np.zeros((50, 120, 3), np.uint8)
        reader(frame)
        reader(frame, force_discovery=True)
        self.assertEqual(reader.metrics['recognized_batches'], 3)
        p.text_score = .7
        result, _ = reader(frame)
        self.assertIsNone(result)
        self.assertEqual(reader.metrics['recognized_batches'], 3)

    def test_byte_equality_is_required_even_if_digest_collides(self):
        reader, p = self.reader()
        frame = np.zeros((50, 120, 3), np.uint8)
        class Collision:
            def digest(self): return b'collision'
        with patch('rouge.page_ocr.hashlib.sha256', return_value=Collision()):
            reader(frame)
            p.crops[0][:] = 55
            result, _ = reader(frame)
        self.assertEqual(result[0][1], '55')
        self.assertEqual(reader.metrics['recognized_batches'], 1)

    def test_cache_budget_is_bounded_and_zero_budget_remains_correct(self):
        reader, p = self.reader(max_bytes=0)
        frame = np.zeros((50, 120, 3), np.uint8)
        before, _ = reader(frame)
        after, _ = reader(frame)
        self.assertEqual(before, after)
        self.assertEqual(reader._bytes, 0)
        self.assertEqual(reader.metrics['reused_batches'], 0)

    def test_explicit_cache_opt_out_keeps_original_detection_and_batch_results(self):
        reader, p = self.reader(cache_enabled=False)
        frame = np.zeros((50, 120, 3), np.uint8)
        before, _ = reader.read(frame)
        after, _ = reader.read(frame)
        self.assertEqual(before, after)
        self.assertEqual(p.detection_calls, 2)
        self.assertEqual(len(p.text_rec.calls), 6)
        self.assertEqual(reader._bytes, 0)
        self.assertEqual(reader.metrics['reused_batches'], 0)

    def test_unsupported_provider_and_arguments_call_original_engine_once(self):
        p = _Provider()
        reader = PageOCR(p)
        result, _ = reader(np.zeros((50, 120, 3), np.uint8), regions=[[8, 0, 18, 20]])
        self.assertEqual(result[0][1], 'full')
        self.assertEqual(p.whole_calls, [{}])
        self.assertEqual(reader.metrics['fallback_reason'], 'unsupported_provider')
        self.assertTrue(reader.metrics['full_frame_input'])
        self.assertFalse(reader.metrics['coverage_verified'])
        self.assertIsNone(reader.metrics['complete_current_texts'])
        reader._supported = lambda: True
        reader(np.zeros((50, 120, 3), np.uint8), return_word_box=True)
        self.assertEqual(p.whole_calls[-1], {'return_word_box': True})
        self.assertEqual(reader.metrics['fallback_reason'], 'unsupported_arguments')

    def test_invalid_domain_keeps_every_current_box(self):
        reader, p = self.reader()
        result, _ = reader(np.zeros((50, 120, 3), np.uint8), regions=[[0, 0, float('nan'), 9]])
        self.assertEqual(len(result), 5)
        self.assertEqual(reader.metrics['page_boxes'], 0)
        self.assertEqual(reader.metrics['guard_boxes'], 5)


if __name__ == '__main__':
    unittest.main()
