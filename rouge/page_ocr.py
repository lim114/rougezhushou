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


def frame_signature(image):
    """Bind complete-current coverage to exact input pixels and geometry."""
    if not isinstance(image, np.ndarray):
        return None
    return {'shape': list(image.shape), 'dtype': image.dtype.str,
            'sha256': hashlib.sha256(np.ascontiguousarray(image)).digest().hex()}


def _callable_identity(value):
    """Bound method wrapper objects are recreated by every attribute read."""
    if hasattr(value, '__self__') and hasattr(value, '__func__'):
        return id(value.__self__), id(value.__func__)
    return id(value)


def _batch_input(recognizer, crops):
    """Normalize one original RapidOCR batch at its shared padded width."""
    ratios = [crop.shape[1] / float(crop.shape[0]) for crop in crops]
    height, width = recognizer.rec_image_shape[1:]
    max_ratio = max(width / height, *ratios)
    tensor = np.stack([recognizer.resize_norm_img(crop, max_ratio) for crop in crops])
    return tensor.astype(np.float32, copy=False), ratios, max_ratio


class PageOCR:
    """Use the original engine when its split-inference contract is unknown.

    ``regions`` is a priority hint in current image pixels. It never authorizes
    discarding exterior detections. ``force_discovery`` bypasses batch reuse;
    every ordinary call already detects the whole current frame.
    """

    def __init__(self, engine, *, cache_enabled=True, max_bytes=24*1024*1024, max_entries=64,
                 reuse_text_rows=False):
        self.engine = engine
        self.provider = engine.engine if type(engine) is CachedOCR else engine
        self.cache_enabled = cache_enabled
        self.reuse_text_rows = reuse_text_rows
        self.max_bytes = max_bytes
        self.max_entries = max_entries
        self._cache = OrderedDict()
        self._bytes = 0
        self._context = None
        self.metrics = {}
        self._current_frame = None

    def complete_frame_matches(self, image):
        """Require pixel equality too; a digest collision is not frame identity."""
        current = self._current_frame
        return (isinstance(image, np.ndarray) and current is not None
                and image.shape == current.shape and image.dtype == current.dtype
                and np.array_equal(image, current))

    def release_frame_snapshot(self):
        self._current_frame = None

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

    def _recognize_batch(self, crops, *, force_discovery=False):
        if self.reuse_text_rows:
            return self._recognize_rows(crops,force_discovery=force_discovery)
        key = tuple((a.shape, a.dtype.str, np.ascontiguousarray(a).tobytes())
                    for a in crops) if self.cache_enabled else None
        entry = self._cache.get(key) if self.cache_enabled else None
        if not force_discovery and entry is not None:
            self._cache.move_to_end(key)
            return deepcopy(entry[0]), 0.0, True
        r = self.provider.text_rec
        # These are precisely the original globally sorted RapidOCR batches.
        # Splitting into arbitrary page/crop groups would change padding and
        # can change confidence; retain the original maximum width and order.
        tensor, ratios, max_ratio = _batch_input(r, crops)
        started = time.perf_counter()
        predictions = r.session(tensor)[0]
        elapsed = time.perf_counter() - started
        result = r.postprocess_op(predictions, False, wh_ratio_list=ratios,
                                  max_wh_ratio=max_ratio)
        if self.cache_enabled:
            size = sum(len(pixels) for _, _, pixels in key)
            if size <= self.max_bytes:
                if entry is not None:
                    self._bytes -= entry[1]
                self._cache[key] = (deepcopy(result), size)
                self._bytes += size
                while self._bytes > self.max_bytes or len(self._cache) > self.max_entries:
                    _, old = self._cache.popitem(last=False)
                    self._bytes -= old[1]
        return result, elapsed, False

    def _recognize_rows(self, crops, *, force_discovery=False):
        """Reuse exact normalized model inputs, retaining original batch padding.

        RapidOCR's original width ordering and maximum ratio still determine
        each row's tensor and decoder length. Only uncached rows enter inference;
        current detector boxes and classifier transforms are never cached here.
        """
        r=self.provider.text_rec
        tensor, ratios, maximum = _batch_input(r, crops)
        keys=[('normalized_row',row.shape,row.dtype.str,ratios[i],maximum,row.tobytes())
              for i,row in enumerate(tensor)]
        records=[self._cache.get(key) if self.cache_enabled and not force_discovery else None
                 for key in keys]
        missing=[i for i,entry in enumerate(records) if entry is None]
        result=[deepcopy(entry[0]) if entry is not None else None for entry in records]
        elapsed=0.
        if missing:
            started=time.perf_counter()
            inputs = tensor if len(missing) == len(crops) else tensor[missing]
            predictions=r.session(inputs)[0]
            elapsed=time.perf_counter()-started
            values=r.postprocess_op(predictions,False,wh_ratio_list=[ratios[i] for i in missing],
                                   max_wh_ratio=maximum)
            for i,value in zip(missing,values):
                result[i]=value
                key=keys[i];size=len(key[-1])
                if self.cache_enabled and size<=self.max_bytes:
                    old=self._cache.pop(key,None)
                    if old is not None:self._bytes-=old[1]
                    self._cache[key]=(deepcopy(value),size);self._bytes+=size
        for key,entry in zip(keys,records):
            if entry is not None:self._cache.move_to_end(key)
        while self._bytes>self.max_bytes or len(self._cache)>self.max_entries:
            _,old=self._cache.popitem(last=False);self._bytes-=old[1]
        self.metrics['inferred_text_rows']=self.metrics.get('inferred_text_rows',0)+len(missing)
        self.metrics['reused_text_rows']=self.metrics.get('reused_text_rows',0)+len(keys)-len(missing)
        return result,elapsed,not missing

    def __call__(self, image, *, regions=None, force_discovery=False, **kwargs):
        self._current_frame = None
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
        # Detection and recognition share one immutable current-frame snapshot.
        # A caller changing its input during inference must not seed another
        # strategy with that frame's text under different pixels.
        current = image.copy() if isinstance(image, np.ndarray) else image
        signature = frame_signature(current)
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
                        'recognized_boxes': 0, 'page_first_batches': 0,
                        'frame_signature': signature}
        img = p.load_img(current)
        raw_h, raw_w = img.shape[:2]
        self.metrics['raw_frame_size'] = [raw_w, raw_h]
        domain = normalize_regions(regions, (raw_h, raw_w))
        img, ratio_h, ratio_w = p.preprocess(img)
        operations = {'preprocess': {'ratio_h': ratio_h, 'ratio_w': ratio_w}}
        img, operations = p.maybe_add_letterbox(img, operations)
        boxes, det_elapsed = p.auto_text_det(img)
        if boxes is None:
            self._current_frame = current if isinstance(current, np.ndarray) else None
            return None, None
        crops = p.get_crop_img_list(img, boxes)
        cls_result, cls_elapsed = None, 0.0
        if p.use_cls:
            crops, cls_result, cls_elapsed = p.text_cls(crops)
        origin = p._get_origin_points(boxes, operations, raw_h, raw_w)
        inside = [False] * len(origin)
        if domain:
            for index, box in enumerate(origin):
                box_bounds = bounds(box)
                inside[index] = any(positive_overlap(box_bounds, area) for area in domain)
        ratios = [a.shape[1] / float(a.shape[0]) for a in crops]
        indices = np.argsort(np.array(ratios))
        batch_size = p.text_rec.rec_batch_num
        # Prioritize whole original batches without changing their padding or row order.
        page_batches, other_batches = [], []
        for start in range(0, len(crops), batch_size):
            batch = indices[start:start+batch_size]
            if any(inside[i] for i in batch):
                page_batches.append(batch)
            else:
                other_batches.append(batch)
        self.metrics['page_first_batches'] = len(page_batches)
        rec_result = [('', 0.0)] * len(crops)
        rec_elapsed = 0.0
        for batch in (*page_batches, *other_batches):
            result, elapsed, reused = self._recognize_batch([crops[i] for i in batch],
                                                           force_discovery=force_discovery)
            for index, value in zip(batch, result):
                rec_result[index] = value
            rec_elapsed += elapsed
            self.metrics['reused_batches' if reused else 'recognized_batches'] += 1
            self.metrics['recognized_boxes'] += 0 if reused else len(batch)
        self.metrics.update(detected_boxes=len(crops), page_boxes=sum(inside),
                            guard_boxes=len(crops)-sum(inside), cache_bytes=self._bytes)
        result = p.get_final_res(origin, cls_result, rec_result,
                                 det_elapsed, cls_elapsed, rec_elapsed)
        self._current_frame = current if isinstance(current, np.ndarray) else None
        return result

    def read(self, image, *, regions=None, force_discovery=False):
        return self(image, regions=regions, force_discovery=force_discovery)
