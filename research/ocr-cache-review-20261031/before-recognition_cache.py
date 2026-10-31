"""Bounded in-memory reuse, requiring byte equality as well as geometry."""
from collections import OrderedDict
from copy import deepcopy
import hashlib
import numpy as np


class ExactImageCache:
    def __init__(self, *, max_bytes=8*1024*1024, max_entries=24):
        self.max_bytes = max_bytes
        self.max_entries = max_entries
        self.entries = OrderedDict()
        self.bytes = self.hits = self.misses = 0

    def call(self, image, context, compute):
        pixels = np.ascontiguousarray(image).tobytes()
        key = (image.shape, image.dtype.str, context, hashlib.sha256(pixels).digest())
        entry = self.entries.get(key)
        if entry is not None and entry[0] == pixels:
            self.entries.move_to_end(key)
            self.hits += 1
            return deepcopy(entry[1])
        self.misses += 1
        value = compute()
        if len(pixels) <= self.max_bytes:
            if entry is not None:
                self.bytes -= len(entry[0])
            self.entries[key] = (pixels, deepcopy(value))
            self.bytes += len(pixels)
            while self.bytes > self.max_bytes or len(self.entries) > self.max_entries:
                _, removed = self.entries.popitem(last=False)
                self.bytes -= len(removed[0])
        return value


class CachedOCR:
    """OCR parameters and crop dimensions are part of every cache identity.

    One current discovery frame plus its independently read operator/card crops
    fit together. A smaller budget evicted unchanged crops each time an animated
    full frame was admitted. This remains bounded by bytes and entry count;
    reuse still requires exact current pixels, geometry and OCR parameters.
    """
    def __init__(self, engine):
        self.engine = engine
        self.cache = ExactImageCache(max_bytes=24*1024*1024, max_entries=48)

    def __call__(self, image, **kwargs):
        return self.cache.call(image, tuple(sorted(kwargs.items())), lambda: self.engine(image, **kwargs))
