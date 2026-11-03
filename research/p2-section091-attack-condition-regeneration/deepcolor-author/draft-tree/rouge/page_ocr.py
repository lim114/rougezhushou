"""Region-prioritized recognition with current full-frame text detection.

Static visual controls choose the order of OCR work, never its observations.
Every current detector box remains in the result, including boxes outside the
suggested regions. Exact crop batches may reuse their recognition results.
The detector, crop transform, classifier, batch layout, confidence filtering
and coordinate conversion follow the installed RapidOCR 1.4.4 implementation.
"""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
import hashlib
from importlib.metadata import PackageNotFoundError, version
import time

import numpy as np

from .dynamic_ocr import bounds, normalize_regions, positive_overlap
from .recognition_cache import CachedOCR


def _callable_identity(value):
    """Bound method wrapper objects are recreated by every attribute read."""
    if hasattr(value, '__self__') and hasattr(value, '__func__'):
        return id(value.__self__), id(value.__func__)
    return id(value)


class PageOCR:
    """Use the original engine when its split-inference contract is unknown.

    ``regions`` is a priority hint in current image pixels. It never authorizes
    discarding exterior detections. ``force_discovery`` bypasses batch reuse;
    every ordinary call already detects the whole current frame.
    """

    def __init__(self, engine, *, cache_enabled=True, max_bytes=24*1024*1024, max_entries=64):
        self.engine = engine
        self.provider = engine.engine if type(engine) is CachedOCR else engine
        self.cache_enabled = cache_enabled
        self.max_bytes = max_bytes
        self.max_entries = max_entries
        self._cache = OrderedDict()
        self._bytes = 0
        self._context = None
        self.metrics = {}

    def _supported(self):
        try:
            from rapidocr_onnxruntime import RapidOCR
            installed_version = version('rapidocr-onnxruntime')
        except (ImportError, PackageNotFoundError):
            return False
        return (type(self.provider) is RapidOCR and installed_version == '1.4.4'
                and self.provider.use_det is True and self.provider.use_rec is True
                and isinstance(self.provider.text_rec.rec_batch_num, int)
                and self.provider.text_rec.rec_batch_num > 0)

    def _configuration(self):
        p = self.provider
        r = p.text_rec
        return (id(p), id(r), _callable_identity(r.session), _callable_identity(r.postprocess_op),
                int(r.rec_batch_num), tuple(r.rec_image_shape), float(p.text_score),
                bool(p.use_cls), _callable_identity(p.text_cls), float(p.max_side_len),
                float(p.min_side_len), float(p.min_height), float(p.width_height_ratio))

    def _cache_key(self, crops):
        payload = tuple((a.shape, a.dtype.str, np.ascontiguousarray(a).tobytes()) for a in crops)
        key = tuple((shape, dtype, hashlib.sha256(pixels).digest())
                    for shape, dtype, pixels in payload)
        return key, payload

    def _recognize_batch(self, crops, *, force_discovery=False):
        key, payload = self._cache_key(crops)
        entry = self._cache.get(key)
        if self.cache_enabled and not force_discovery and entry is not None and entry[0] == payload:
            self._cache.move_to_end(key)
            return deepcopy(entry[1]), 0.0, True
        r = self.provider.text_rec
        # These are precisely the original globally sorted RapidOCR batches.
        # Splitting into arbitrary page/crop groups would change padding and
        # can change confidence; retain the original maximum width and order.
        ratios = [a.shape[1] / float(a.shape[0]) for a in crops]
        max_ratio = max(r.rec_image_shape[2] / r.rec_image_shape[1], *ratios)
        tensor = np.concatenate([r.resize_norm_img(a, max_ratio)[np.newaxis, :]
                                 for a in crops]).astype(np.float32)
        started = time.perf_counter()
        predictions = r.session(tensor)[0]
        elapsed = time.perf_counter() - started
        result = r.postprocess_op(predictions, False, wh_ratio_list=ratios,
                                  max_wh_ratio=max_ratio)
        size = sum(len(pixels) for _, _, pixels in payload)
        if self.cache_enabled and size <= self.max_bytes:
            if entry is not None:
                self._bytes -= entry[2]
            self._cache[key] = (payload, deepcopy(result), size)
            self._bytes += size
            while self._bytes > self.max_bytes or len(self._cache) > self.max_entries:
                _, old = self._cache.popitem(last=False)
                self._bytes -= old[2]
        return result, elapsed, False

    def __call__(self, image, *, regions=None, force_discovery=False, **kwargs):
        if kwargs or not self._supported():
            self._cache.clear()
            self._bytes = 0
            self._context = None
            self.metrics = {'mode': 'full_discovery', 'full_frame_input': True,
                            'coverage_verified': False, 'full_detection': None,
                            'full_text_coverage': None, 'complete_current_texts': None,
                            'fallback_reason': 'unsupported_arguments' if kwargs else 'unsupported_provider'}
            engine = self.provider if force_discovery else self.engine
            return engine(image, **kwargs)
        p = self.provider
        context = self._configuration()
        if context != self._context:
            self._cache.clear()
            self._bytes = 0
            self._context = context
        self.metrics = {'mode': 'page_detected_batches', 'full_frame_input': True,
                        'coverage_verified': True, 'full_detection': True,
                        'full_text_coverage': True, 'complete_current_texts': True, 'fallback_reason': None,
                        'detected_boxes': 0, 'page_boxes': 0, 'guard_boxes': 0,
                        'recognized_batches': 0, 'reused_batches': 0,
                        'recognized_boxes': 0, 'page_first_batches': 0}
        img = p.load_img(image)
        raw_h, raw_w = img.shape[:2]
        domain = normalize_regions(regions, (raw_h, raw_w))
        img, ratio_h, ratio_w = p.preprocess(img)
        operations = {'preprocess': {'ratio_h': ratio_h, 'ratio_w': ratio_w}}
        img, operations = p.maybe_add_letterbox(img, operations)
        boxes, det_elapsed = p.auto_text_det(img)
        if boxes is None:
            return None, None
        crops = p.get_crop_img_list(img, boxes)
        cls_result, cls_elapsed = None, 0.0
        if p.use_cls:
            crops, cls_result, cls_elapsed = p.text_cls(crops)
        origin = p._get_origin_points(boxes, operations, raw_h, raw_w)
        inside = [bool(domain and any(positive_overlap(bounds(box), area) for area in domain))
                  for box in origin]
        ratios = [a.shape[1] / float(a.shape[0]) for a in crops]
        indices = np.argsort(np.array(ratios))
        batch_size = p.text_rec.rec_batch_num
        batches = [list(indices[start:start+batch_size])
                   for start in range(0, len(crops), batch_size)]
        # Stable partition changes execution order only. Tensor row order,
        # maximum ratio and original final detector order stay unchanged.
        ordered = sorted(enumerate(batches),
                         key=lambda item: (not any(inside[i] for i in item[1]), item[0]))
        rec_result = [('', 0.0)] * len(crops)
        rec_elapsed = 0.0
        for _, batch in ordered:
            result, elapsed, reused = self._recognize_batch([crops[i] for i in batch],
                                                           force_discovery=force_discovery)
            for index, value in zip(batch, result):
                rec_result[index] = value
            rec_elapsed += elapsed
            self.metrics['reused_batches' if reused else 'recognized_batches'] += 1
            self.metrics['recognized_boxes'] += 0 if reused else len(batch)
            self.metrics['page_first_batches'] += int(any(inside[i] for i in batch))
        self.metrics.update(detected_boxes=len(crops), page_boxes=sum(inside),
                            guard_boxes=len(crops)-sum(inside), cache_bytes=self._bytes)
        return p.get_final_res(origin, cls_result, rec_result,
                               det_elapsed, cls_elapsed, rec_elapsed)

    def read(self, image, *, regions=None, force_discovery=False):
        return self(image, regions=regions, force_discovery=force_discovery)
