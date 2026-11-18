"""Prepare current-frame text boxes while the capture buffer selects a frame."""
from concurrent.futures import ThreadPoolExecutor
from copy import copy

import numpy as np

from .viewport import prepare_frame


def detector_input(provider, image):
    img, rh, rw = provider.preprocess(image)
    return provider.maybe_add_letterbox(img, {'preprocess': {'ratio_h': rh, 'ratio_w': rw}})


def _prepare(provider, frame):
    # RapidOCR's detector sets its preprocess_op on each call. Only its native
    # session is shared with the actual reader; that session owns per-thread requests.
    isolated = copy(provider)
    isolated.text_det = copy(provider.text_det)
    image, _ = prepare_frame(frame['image'], frame['client_rect'])
    img, _ = detector_input(isolated, isolated.load_img(image))
    return provider, img, isolated.auto_text_det(img)


class SettlingDetection:
    def __init__(self):
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix='rouge-settling-det')
        self.future = None
        self.seq = None
        self.generation = None

    def offer(self, buffer, provider):
        if self.future is not None and not self.future.done():
            return
        frame = buffer.latest(after_seq=self.seq, settling_only=True)
        if frame is not None:
            self.seq, self.generation = frame['seq'], frame['generation']
            self.future = self.worker.submit(_prepare, provider, frame)

    def for_frame(self, frame):
        if frame is not None and (frame['seq'], frame['generation']) == (self.seq, self.generation):
            return self.future
        return None

    def close(self):
        self.worker.shutdown(wait=False, cancel_futures=True)
        self.future = None


def detect_boxes(provider, img, future):
    if future is not None and future.done():
        owner, prepared, result = future.result()
        if owner is provider and img.dtype == prepared.dtype and np.array_equal(img, prepared):
            return result
    return provider.auto_text_det(img)
