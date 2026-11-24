"""Read a complete, currently visible exploration map from upright text and node geometry."""
from copy import copy, deepcopy
from time import perf_counter, time

import cv2
import numpy as np
from PySide6.QtCore import QObject, QThreadPool, Qt, Signal

from .map_recognition import read_map
from .recognition import node_names
from .recognition_cache import CachedOCR
from .run_config import config_data, confirmed_config
from .viewport import map_evidence, prepare_frame


def glyph_boxes(image, proposal_width=960):
    height, width = image.shape[:2]
    scale = min(1., proposal_width / width)
    small = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    strokes = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, np.ones((7, 7), np.uint8))
    joined = cv2.dilate((strokes > 40).astype(np.uint8), np.ones((3, 4), np.uint8))
    _, _, components, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)
    boxes = []
    for x, y, w, h, area in components[1:]:
        if 5 <= h <= 28 and 14 <= w <= 140 and w > 1.2 * h and area >= .4 * w * h:
            left, right = max(0, x + 1), min(gray.shape[1], x + w - 1)
            top, bottom = max(0, y - 1), min(gray.shape[0], y + h + 1)
            boxes.append([(left, top), (right, top), (right, bottom), (left, bottom)])
    return np.asarray(boxes, np.float32).reshape(-1, 4, 2) / scale


def pointer_height(image, boxes):
    """The downward pointer only schedules OCR. The marker text must also read correctly."""
    heights = []
    for box in boxes:
        x, y = box[0].astype(int)
        right, bottom = box[2].astype(int)
        h = bottom - y
        if not 3 * h < right - x < 9 * h:
            continue
        middle = (x + right) // 2
        patch = image[max(y, bottom-h//3):bottom+2*h, max(x, middle-h):min(right, middle+h)]
        if not patch.size:
            continue
        gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
        _, labels, components, _ = cv2.connectedComponentsWithStats((gray >= 165).astype(np.uint8), connectivity=8)
        for index, (left, top, w, ph, area) in enumerate(components[1:], 1):
            if not (.45*h <= ph <= 1.6*h and .55*h <= w <= 1.8*h and .72 <= w/ph <= 1.8
                    and .35 <= area/(w*ph) <= .72):
                continue
            pixels = labels[top:top+ph, left:left+w] == index
            band = max(1, ph // 3)
            if pixels[:band].sum() > 1.7 * pixels[-band:].sum():
                heights.append(h)
                break
    return heights[0] if len(heights) == 1 else None


def detached_marker(image, reader):
    """Read the word above an isolated arrow when its glyphs did not form one box."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, labels, components, centers = cv2.connectedComponentsWithStats(
        (gray >= 165).astype(np.uint8), connectivity=8)
    height, width = gray.shape
    widths, heights = components[:, 2], components[:, 3]
    possible = np.flatnonzero((widths >= 5) & (heights >= 5)
                              & (heights <= height * .035) & (widths <= width * .035))
    arrows = []
    for index in possible:
        x, y, w, h, area = components[index]
        if not (.8 <= w / h <= 1.85 and .33 <= area / (w*h) <= .74
                and .22 <= (centers[index, 1] - y + .5) / h <= .44):
            continue
        pixels = labels[y:y+h, x:x+w] == index
        yy, xx = np.ogrid[:h, :w]
        triangle = np.abs((xx + .5) / w - .5) * 2 <= 1 - (yy + .5) / h
        if np.count_nonzero(pixels & triangle) >= .70 * np.count_nonzero(pixels | triangle):
            arrows.append((x + w/2, y, w, h))
    if len(arrows) != 1:
        return None
    cx, y, w, h = arrows[0]
    left, right = max(0, round(cx - 3.3*w)), min(width, round(cx + 3.3*w))
    top, bottom = max(0, round(y - 1.45*h)), max(0, round(y - .08*h))
    if top >= bottom:
        return None
    results, _ = reader.text_rec([image[top:bottom, left:right]])
    word, score = results[0]
    if word.replace(' ', '') != 'YOUAREHERE' or score < .9:
        return None
    box = np.array([(left, top), (right, top), (right, bottom), (left, bottom)], np.float32)
    return box, float(score), h * 1.2


def preview(image, reader, known_config=None):
    """Return complete visible map evidence in analysis-image coordinates, or None."""
    boxes = glyph_boxes(image)
    height = pointer_height(image, boxes)
    marker = None
    if height is None:
        marker = detached_marker(image, reader)
        if marker is None:
            return None
        word_box, _, height = marker
        boxes = glyph_boxes(image, proposal_width=1080)
        centers = (boxes[:, 0] + boxes[:, 2]) / 2
        inside_word = ((centers >= word_box[0]) & (centers <= word_box[2])).all(axis=1)
        boxes = boxes[~inside_word]
    sizes = boxes[:, 2] - boxes[:, 0]
    boxes = boxes[(sizes[:, 0] >= 2.75*height) & (sizes[:, 1] >= .75*height) & (sizes[:, 1] <= 3*height)]
    if not 0 < len(boxes) <= 96:
        return None
    crops = reader.get_crop_img_list(image, boxes)
    results, _ = reader.text_rec(crops)
    h, w = image.shape[:2]
    texts = [{'box': (box / [w, h]).tolist(), 'text': text.replace(' ', ''), 'confidence': float(score)}
             for box, (text, score) in zip(boxes, results) if score >= .7]
    if marker is not None:
        texts.append({'box': (word_box / [w, h]).tolist(), 'text': 'YOUAREHERE', 'confidence': marker[1]})
    controls = {row['text'] for row in texts if row['confidence'] >= .9}
    if (not {'目标生命值', '指挥等级', '零件箱', '收藏品', 'YOUAREHERE'} <= controls
            or {'收起', '敌方情报', '保密等级'} & controls):
        return None
    zones = [(key, zone['name']) for row in texts if row['confidence'] >= .95
             for key, zone in config_data()['zones'].items() if row['text'] == zone['name']]
    if len(zones) != 1:
        return None
    zid, name = zones[0]
    config = {**(known_config or {}), 'zone': {'id': zid, 'name': name, 'candidates': [zid],
                                               'source': '地图顶部完整区域名'}}
    accepted = node_names()
    nodes = []
    for row in texts:
        label = {'未知的凶房': '未知的凶戾', '未知的诡利': '未知的诡秘'}.get(row['text'], row['text'])
        if label in accepted and row['confidence'] >= .9:
            nodes.append({'type': label, 'box': row['box'], 'confidence': row['confidence'],
                          'hidden': label.startswith('未知'), 'prediction': None})
    graph = read_map(image, texts, nodes, {'config': config})
    if (graph['status'] != 'matched' or not graph['current_node']
            or not all(node['visible'] and node['observed_type'] for node in graph['nodes'])):
        return None
    return {'map': graph, 'nodes': nodes, 'texts': texts, 'map_config': config}


def read_frame(frame, reader, context):
    start = perf_counter()
    image, viewport = prepare_frame(frame['image'], frame['client_rect'])
    evidence = preview(image, reader, confirmed_config(context))
    if evidence is None:
        return None
    observation = deepcopy(dict(evidence, page='exploration', size=viewport['source_size'],
                                stage=None, run=None, operator=None, node_content=None, limitations=[]))
    map_evidence(observation, viewport)
    observation['viewport'] = viewport
    elapsed = (perf_counter() - start) * 1000
    observation['performance'] = {'stages_ms': {'glyph_map': elapsed}, 'total_ms': elapsed}
    return observation


def read_alongside_full_frame(frame, engine, context, publish):
    # Reuse the loaded weights. Each thread owns its native inference request.
    age_ms = (time() - frame['captured_at']) * 1000
    reader = copy(engine.engine if isinstance(engine, CachedOCR) else engine)
    reader.text_rec = copy(reader.text_rec)
    observation = read_frame(frame, reader, context)
    if observation is not None:
        publish(observation, age_ms)


class CurrentMapPreview(QObject):
    """One active map read and at most the newest waiting frame, owned by the GUI."""
    finished = Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(1)
        self.running = False
        self.pending = None
        self.finished.connect(self._finished, Qt.ConnectionType.QueuedConnection)

    def offer(self, key, eligible, work):
        if self.pending is None or self.pending[0] < key:
            self.pending = (key, eligible, work)
        if not self.running:
            self._start_latest()

    def _start_latest(self):
        pending, self.pending = self.pending, None
        if pending is None or not pending[1]():
            return
        self.running = True
        work = pending[2]

        def read():
            try:
                work()
            finally:
                self.finished.emit()
        self.pool.start(read)

    def _finished(self):
        self.running = False
        self._start_latest()
