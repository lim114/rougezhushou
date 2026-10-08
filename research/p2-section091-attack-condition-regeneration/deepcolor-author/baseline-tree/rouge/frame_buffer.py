"""Bounded, chronological candidates between fast capture and slow recognition.

Selection only uses a small whole-frame thumbnail. It does not assume a screen
layout, run OCR, or reject a short-lived page because it looks less sharp. Raw
images retained by the buffer (including the manual latest-frame fallback) share
one byte/count budget. Returned images are caller-owned copies, outside it.
"""
from collections import deque
import threading
import time

import cv2
import numpy as np


class FrameBuffer:
    def __init__(self, max_bytes=96 * 1024 * 1024, max_frames=16,
                 settle_seconds=.12):
        if int(max_bytes) <= 0 or int(max_frames) <= 0 or settle_seconds < 0:
            raise ValueError('Frame buffer limits must be positive.')
        self.max_bytes = int(max_bytes)
        self.max_frames = int(max_frames)
        self.settle_seconds = float(settle_seconds)
        self._lock = threading.Lock()
        self._pending = deque()
        self._latest = None
        self._reference = None
        self._seq = 0
        self._generation = 0
        self._last_taken_seq = 0
        self._last_time = float('-inf')
        self._counts = self._new_counts()

    @staticmethod
    def _new_counts():
        return dict(received=0, selected=0, deduplicated=0, overflow=0,
                    overflow_duplicates=0, overflow_low_novelty=0,
                    oversized=0, invalid=0,
                    out_of_order=0, taken=0, manual_repeats=0)

    @staticmethod
    def _thumbnail(image):
        height, width = image.shape[:2]
        factor = min(1., 640. / max(height, width))
        thumb = cv2.resize(image, (max(1, round(width * factor)),
                                   max(1, round(height * factor))),
                           interpolation=cv2.INTER_AREA)
        if thumb.ndim == 2:
            thumb = thumb[:, :, None]
        gray = (cv2.cvtColor(thumb, cv2.COLOR_BGR2GRAY)
                if thumb.shape[2] == 3 else thumb[:, :, 0])
        quality = float(cv2.Laplacian(gray, cv2.CV_32F).var())
        height, width = thumb.shape[:2]
        padded = cv2.copyMakeBorder(thumb, 0, -height % 8, 0, -width % 8,
                                    cv2.BORDER_CONSTANT, value=0)
        summary = cv2.resize(padded.astype(np.float32),
                             (padded.shape[1] // 8, padded.shape[0] // 8),
                             interpolation=cv2.INTER_AREA)
        return thumb, quality, summary

    @staticmethod
    def _similar(left, right):
        if left['key'] != right['key']:
            return False
        a, b = left['thumb'], right['thumb']
        if a.shape != b.shape:
            return False
        if np.array_equal(a, b):
            return True
        # A cheap necessary condition for the exact local difference below.
        # Mean(abs(A-B)) >= abs(mean(A)-mean(B)); rejecting here cannot discard
        # a pair that the full verifier would regard as near-identical.
        if float(np.max(np.abs(left['summary'] - right['summary']))) > 2.5:
            return False
        # Local blocks retain small labels that would vanish in a global mean.
        difference = cv2.absdiff(a, b)
        if difference.ndim == 3:
            difference = cv2.max(cv2.max(difference[:, :, 0], difference[:, :, 1]),
                                 difference[:, :, 2])
        if float(difference.mean()) > 1.2:
            return False
        height, width = difference.shape
        padded = np.pad(difference, ((0, -height % 8), (0, -width % 8)))
        blocks = padded.reshape(padded.shape[0] // 8, 8,
                                padded.shape[1] // 8, 8).mean(axis=(1, 3))
        return float(blocks.max(initial=0)) <= 2.5

    @staticmethod
    def _export(frame):
        return dict(image=frame['image'].copy(), captured_at=frame['captured_at'],
                    client_rect=(list(frame['client_rect'])
                                 if frame['client_rect'] is not None else None),
                    target=dict(frame['target']), seq=frame['seq'],
                    generation=frame['generation'])

    def _retained(self):
        retained = {id(frame['image']): frame['image'] for frame in self._pending}
        if self._latest is not None:
            retained[id(self._latest['image'])] = self._latest['image']
        return len(retained), sum(image.nbytes for image in retained.values())

    def _trim(self):
        while self._pending:
            count, size = self._retained()
            if count <= self.max_frames and size <= self.max_bytes:
                break
            duplicate_index = None
            # Keep the latest occurrence of a repeated page. Its sequence stays
            # in its original position, so surviving pages remain chronological.
            frames = list(self._pending)
            for index, candidate in enumerate(frames[:-1]):
                if any(self._similar(candidate, later)
                       for later in reversed(frames[index + 1:])):
                    duplicate_index = index
                    break
            if duplicate_index is not None:
                del self._pending[duplicate_index]
                self._counts['overflow_duplicates'] += 1
            else:
                # Under sustained animation, preserve boundaries between
                # different pages instead of repeatedly throwing away the
                # earliest short page. This is an overload preference, never a
                # hard filter: small text changes are still ordinary candidates.
                neighbours = frames
                if not neighbours or neighbours[-1] is not self._latest:
                    neighbours = neighbours + [self._latest]
                choices = []
                for index, candidate in enumerate(frames):
                    if candidate is self._latest:
                        continue
                    adjacent = []
                    if index > 0:
                        adjacent.append(self._distance(candidate, neighbours[index - 1]))
                    if index + 1 < len(neighbours):
                        adjacent.append(self._distance(candidate, neighbours[index + 1]))
                    if adjacent:
                        choices.append((max(adjacent), index))
                if choices and min(choices)[0] <= .04:
                    del self._pending[min(choices)[1]]
                    self._counts['overflow_low_novelty'] += 1
                else:
                    self._pending.popleft()
            self._counts['overflow'] += 1
            if not self._pending and self._latest['seq'] > self._last_taken_seq:
                # A one-frame budget may evict a sharper earlier representative
                # in favour of latest. Keep that latest available automatically.
                self._pending.append(self._latest)

    @staticmethod
    def _distance(left, right):
        if left['key'] != right['key']:
            return 1.
        return float(cv2.absdiff(left['novelty'], right['novelty']).mean()) / 255.

    def offer(self, image, captured_at, client_rect=None, target=None):
        """Offer a BGR uint8 frame; even rejected offers consume a unique seq.

        Near-identical consecutive observations share a recognition candidate.
        The sharper representative is retained; the exact latest observation is
        independently available for an explicit manual sample.
        """
        with self._lock:
            self._seq += 1
            seq = self._seq
            self._counts['received'] += 1
            if (not isinstance(image, np.ndarray) or image.dtype != np.uint8 or
                    image.ndim not in (2, 3) or image.size == 0 or
                    (image.ndim == 3 and image.shape[2] != 3)):
                self._counts['invalid'] += 1
                return seq
            if image.nbytes > self.max_bytes:
                self._counts['oversized'] += 1
                return seq
            if image.max() <= 4:
                self._counts['invalid'] += 1
                return seq
            timestamp = float(captured_at)
            if not np.isfinite(timestamp):
                self._counts['invalid'] += 1
                return seq
            if timestamp < self._last_time:
                self._counts['out_of_order'] += 1
                return seq
            self._last_time = timestamp
            thumb, quality, summary = self._thumbnail(image)
            thumb_height, thumb_width = thumb.shape[:2]
            novelty_scale = min(1., 96. / max(thumb_height, thumb_width))
            novelty = cv2.resize(thumb, (max(1, round(thumb_width * novelty_scale)),
                                         max(1, round(thumb_height * novelty_scale))),
                                interpolation=cv2.INTER_AREA)
            identity = dict(target or {})
            rect = tuple(client_rect) if client_rect is not None else None
            frame = dict(image=image.copy(), captured_at=timestamp,
                         client_rect=rect, target=identity, seq=seq,
                         generation=self._generation,
                         key=(image.shape, rect, identity.get('hwnd'), identity.get('pid')),
                         thumb=thumb, quality=quality, summary=summary, novelty=novelty,
                         ready_at=time.monotonic() + self.settle_seconds)
            self._latest = frame
            if self._reference is not None and self._similar(self._reference, frame):
                self._counts['deduplicated'] += 1
                if self._pending and self._similar(self._pending[-1], frame):
                    previous = self._pending[-1]
                    if quality >= previous['quality'] * .98:
                        frame['ready_at'] = previous['ready_at']
                        self._pending[-1] = frame
                # The reference thumbnail stays fixed so a series of tiny
                # changes can accumulate into a meaningful new candidate.
            else:
                self._pending.append(frame)
                self._reference = dict(key=frame['key'], thumb=thumb, summary=summary)
                self._counts['selected'] += 1
            self._trim()
            return seq

    def take(self, force=False):
        """Take oldest candidate; force bypasses settling, never skips the FIFO.

        With no pending candidate, force returns the latest observation. Normal
        polling does not repeatedly re-recognize an unchanged static page.
        """
        with self._lock:
            if self._pending:
                frame = self._pending[0]
                # Once a different page follows, preserve the preceding page
                # immediately, including pages visible for only one frame.
                if (not force and len(self._pending) == 1 and
                        time.monotonic() < frame['ready_at']):
                    return None
                self._pending.popleft()
                self._counts['taken'] += 1
            elif force and self._latest is not None:
                frame = self._latest
                self._counts['manual_repeats'] += 1
            else:
                return None
            self._last_taken_seq = max(self._last_taken_seq, frame['seq'])
            return self._export(frame)

    def latest(self):
        """Return a copy for diagnostics; recognition should use take()."""
        with self._lock:
            return self._export(self._latest) if self._latest is not None else None

    def clear(self):
        """Invalidate a capture/run generation without reusing sequence IDs."""
        with self._lock:
            self._generation += 1
            self._pending.clear()
            self._latest = None
            self._reference = None
            self._last_time = float('-inf')
            self._counts = self._new_counts()
            return self._generation

    def stats(self):
        with self._lock:
            count, size = self._retained()
            return dict(self._counts, pending=len(self._pending),
                        retained_frames=count, bytes=size,
                        max_bytes=self.max_bytes, max_frames=self.max_frames,
                        generation=self._generation, seq=self._seq,
                        last_taken_seq=self._last_taken_seq,
                        oldest_at=(self._pending[0]['captured_at'] if self._pending else None),
                        latest_at=(self._latest['captured_at'] if self._latest else None))
