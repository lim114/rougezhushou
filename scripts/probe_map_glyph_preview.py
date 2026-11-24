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

from rouge.map_text_preview import glyph_boxes, pointer_height, preview
from rouge.ocr_engine import create_engine
from rouge.viewport import prepare_frame


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
