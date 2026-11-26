"""CPU-side reference data for an OpenCL held-icon rejection pass.

Each opaque pixel belongs to one square. The tile feature consists of the BGR
sum divided by the side length, plus the norm of the within-tile residual.
A feature-distance lower bound can reject a placement. Only full-resolution
masked RGB data is used in the second pass.
"""
import atexit
from collections import OrderedDict
from contextlib import ExitStack
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from threading import Lock

import cv2
import numpy as np

from .held_icon_opencl import IconDevice, OpenCLUnavailable

def _tile_features(template, mask):
    height, width = mask.shape
    available = mask != 0
    image = template.astype(np.float64)
    positions = []
    features = []
    for level in (4, 3, 2, 1, 0):
        side = 1 << level
        tile_rows, tile_columns = height // side, width // side
        if tile_rows == 0 or tile_columns == 0:
            continue
        covered = np.s_[:tile_rows * side, :tile_columns * side]
        cells = available[covered].reshape(tile_rows, side, tile_columns, side)
        y, x = np.where(cells.all(axis=(1, 3)))
        if not len(x):
            continue
        pixels = image[covered].reshape(tile_rows, side, tile_columns, side, 3)
        selected = pixels.transpose(0, 2, 1, 3, 4)[y, x]
        scaled_means = selected.sum(axis=(1, 2)) / side
        energy = np.square(selected).sum(axis=(1, 2, 3))
        remainder = np.maximum(0, energy - np.square(scaled_means).sum(axis=1))
        feature = np.column_stack((scaled_means, np.sqrt(remainder)))
        cells.transpose(0, 2, 1, 3)[y, x] = False
        order = np.argsort(-energy)
        packed = (level << 24) | ((y[order] * side) << 12) | (x[order] * side)
        positions.append(packed.astype(np.uint32))
        features.append(feature[order].astype(np.float32))
    return np.concatenate(positions), np.concatenate(features)


def reference_bank(references):
    positions, features, geometry, limits = [], [], [], []
    colors, indices, spans, energies = [], [], [], []
    tile_offset = pixel_offset = 0
    for _, template, mask, *_ in references:
        height, width = mask.shape
        tile_positions, tile_features = _tile_features(template, mask)
        positions.append(tile_positions)
        features.append(tile_features)
        next_tile = tile_offset + len(tile_positions)
        geometry.append((tile_offset, next_tile, width, height))
        tile_offset = next_tile

        y, x = np.where(mask != 0)
        opaque = np.zeros((len(x), 4), np.uint8)
        opaque[:, :3] = template[y, x]
        colors.append(opaque)
        indices.append(((y << 16) | x).astype(np.uint32))
        next_pixel = pixel_offset + len(x)
        spans.append((pixel_offset, next_pixel))
        pixel_offset = next_pixel
        energy = np.square(opaque, dtype=np.float64).sum()
        energies.append(energy)
        limits.append((1 - 0.93 ** 2 + 0.0003) * energy + 8)
    return (
        np.concatenate(features), np.concatenate(positions),
        np.asarray(geometry, np.int32), np.asarray(limits, np.float32),
        np.concatenate(colors), np.concatenate(indices),
        np.asarray(spans, np.int32), np.asarray(energies, np.float32),
    )

_KERNEL = """
__kernel void screen(__global const float4 *moments, __global const float4 *tile_refs,
                     __global const uint *tiles, __global const int4 *geometry,
                     __global const float *bounds, __global const uchar4 *pixels,
                     __global const uchar4 *reference, __global const uint *indices,
                     __global const int2 *spans, __global const float *energy,
                     int width, int height, int start, __global int *eligible) {
    int x = get_global_id(0), y = get_global_id(1), t = start + get_global_id(2);
    int4 g = geometry[t];
    if (x + g.z > width || y + g.w > height) return;
    int origin = y * width + x;
    float cost = 0;
    for (int j = g.x; j < g.y; ++j) {
        uint pos = tiles[j];
        int tile = (pos >> 24) * width * height + ((pos >> 12) & 4095) * width + (pos & 4095);
        float4 delta = .93f * moments[origin + tile] - tile_refs[j];
        cost += dot(delta, delta);
        if ((j & 15) == 15 && cost > bounds[t]) return;
    }
    if (cost > bounds[t]) return;
    uint error = 0, image_energy = 0;
    int2 span = spans[t];
    for (int j = span.x; j < span.y; ++j) {
        uint pos = indices[j];
        int4 value = convert_int4(pixels[origin + (pos >> 16) * width + (pos & 65535)]);
        int4 delta = value - convert_int4(reference[j]);
        error += delta.x*delta.x + delta.y*delta.y + delta.z*delta.z;
        image_energy += value.x*value.x + value.y*value.y + value.z*value.z;
    }
    if ((float)error <= .122f * sqrt((float)image_energy * energy[t]) + 4.f)
        atomic_or(eligible + t, 1);
}
"""

def _image_features(roi):
    height, width = roi.shape[:2]
    pixels = np.zeros((height, width, 4), np.uint8)
    pixels[:, :, :3] = roi
    channels = pixels.astype(np.float64)
    channels[:, :, 3] = np.square(channels[:, :, :3]).sum(axis=2)
    integral = cv2.integral(channels, sdepth=cv2.CV_64F)
    moments = np.zeros((5, height, width, 4), np.float32)
    for level in range(5):
        side = 1 << level
        if min(height, width) < side:
            break
        sums = (integral[side:, side:] - integral[:-side, side:]
                - integral[side:, :-side] + integral[:-side, :-side])
        mean = sums[:, :, :3] / side
        feature = moments[level, :height-side+1, :width-side+1]
        feature[:, :, :3] = mean
        feature[:, :, 3] = np.sqrt(np.maximum(0, sums[:, :, 3] - np.square(mean).sum(axis=2)))
    return moments, pixels

class HeldIconScreen:
    """Own the queue and immutable artwork buffers shared by the GPU test readers.

    Binary masked normalized SSD <= .14 implies ||.93 I - T|| squared
    <= (1 - .93 squared) * ||T|| squared by arithmetic-geometric mean.
    Decomposing each disjoint tile into mean and centered residual gives a
    lower bound by the reverse triangle inequality. The looser tile threshold
    precedes integer RGB verification at .122. CPU coarse seeds start at .12.
    Canonical artwork is at most 72 px on its long side (+ refinement radius),
    so the integer sum of squared byte differences fits in a uint.
    """
    max_bank_bytes = 40 * 1024 * 1024

    def __init__(self):
        self.device = IconDevice(_KERNEL)
        self.lock = Lock()
        self.banks = OrderedDict()
        self.bytes = 0

    def _references(self, key, rows, call):
        if key in self.banks:
            self.banks.move_to_end(key)
            return self.banks[key][0]
        arrays = reference_bank(rows)
        size = sum(a.nbytes for a in arrays)
        with ExitStack() as owner:
            buffers = tuple(self.device.upload(a, owner) for a in arrays)
            if size > self.max_bank_bytes:
                call.enter_context(owner.pop_all())
            else:
                while self.bytes + size > self.max_bank_bytes:
                    _, (_, old_size, old) = self.banks.popitem(last=False)
                    old.close()
                    self.bytes -= old_size
                self.banks[key] = buffers, size, owner.pop_all()
                self.bytes += size
            return buffers

    def select(self, roi, key, rows):
        if not rows:
            return []
        with self.lock, ExitStack() as call:
            moments, pixels = (self.device.upload(a, call) for a in _image_features(roi))
            buffers = self._references(key, rows, call)
            flags = np.zeros(len(rows), np.int32)
            height, width = roi.shape[:2]
            self.device.execute((moments, *buffers[:4], pixels, *buffers[4:]), width, height, flags)
            return np.flatnonzero(flags)

    def close(self):
        with self.lock:
            for _, _, resources in self.banks.values():
                resources.close()
            self.banks.clear()
            self.device.close()

_init_lock = Lock()
_diagnostic = Path(__file__).resolve().parents[1] / '.local' / 'ocr-icon-diagnostics.log'

@lru_cache(maxsize=1)
def _initialize():
    try:
        screen = HeldIconScreen()
    except OpenCLUnavailable as error:
        _diagnostic.parent.mkdir(parents=True, exist_ok=True)
        reason = ' '.join(str(error).splitlines())
        with _diagnostic.open('a', encoding='utf-8') as log:
            log.write(f'{datetime.now().astimezone().isoformat()} 本次启动图标匹配使用CPU：{reason}\n')
        return None
    atexit.register(screen.close)
    return screen

def current_screen():
    with _init_lock:
        return _initialize()
