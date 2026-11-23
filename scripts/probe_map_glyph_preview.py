"""Measure a current-frame map preview on a local image, without starting capture.

Run with the project's Python from the repository root. The optional client
rectangle is in physical pixels relative to the saved image. The elapsed time
ends at a verified graph in memory and excludes model loading and window paint.
"""
import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rouge.map_recognition import read_map
from rouge.ocr_engine import create_engine
from rouge.recognition import node_names
from rouge.run_config import config_data
from rouge.viewport import prepare_frame


def glyph_boxes(image):
    height, width = image.shape[:2]
    scale = min(1., 960 / width)
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


def preview(image, reader, known_config=None):
    """Return complete visible map evidence in analysis-image coordinates, or None."""
    boxes = glyph_boxes(image)
    height = pointer_height(image, boxes)
    if height is None:
        return None
    sizes = boxes[:, 2] - boxes[:, 0]
    boxes = boxes[(sizes[:, 0] >= 2.75*height) & (sizes[:, 1] >= .75*height) & (sizes[:, 1] <= 3*height)]
    if not 0 < len(boxes) <= 96:
        return None
    crops = reader.get_crop_img_list(image, boxes)
    results, _ = reader.text_rec(crops)
    h, w = image.shape[:2]
    texts = [{'box': (box / [w, h]).tolist(), 'text': text.replace(' ', ''), 'confidence': float(score)}
             for box, (text, score) in zip(boxes, results) if score >= .7]
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('images', type=Path, nargs='+')
    parser.add_argument('--client-rect', type=int, nargs=4, metavar=('LEFT', 'TOP', 'RIGHT', 'BOTTOM'))
    args = parser.parse_args()
    reader = create_engine(backend='openvino-gpu')
    for path in args.images:
        frame = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            parser.error(f'无法读取图片 {path}')
        start = perf_counter()
        image, _ = prepare_frame(frame, args.client_rect)
        result = preview(image, reader)
        elapsed = round((perf_counter()-start)*1000, 1)
        graph = result['map'] if result else {}
        print(json.dumps({'image': path.name, 'frame_to_graph_ms': elapsed,
                          'template': graph.get('template_id'), 'current': graph.get('current_node'),
                          'cells': {n['id']: n['observed_type'] for n in graph.get('nodes', [])}},
                         ensure_ascii=False))


if __name__ == '__main__':
    main()
