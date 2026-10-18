"""Image-only geometric observation, frozen before manual cell observations."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, math
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.cache/p3-312-highland-evidence'
OUT.mkdir()
request_raw = (ROOT / '.cache/p3-311-map-assessment/candidate-request-inventory.json').read_bytes()
request = json.loads(request_raw)
catalog = json.loads((ROOT / 'rouge/data/battle-previews.json').read_bytes())

def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')

def intersection(vertices):
    a, b, c, d = np.array(vertices, dtype=np.float64)
    matrix = np.column_stack((c - a, -(d - b)))
    if abs(np.linalg.det(matrix)) < 1e-8:
        return None
    t, u = np.linalg.solve(matrix, b - a)
    if not (0 < t < 1 and 0 < u < 1):
        return None
    return (a + t * (c - a)).tolist()

outputs = {'kind': 'FROZEN_IMAGE_ONLY_GEOMETRY_NOT_CELL_ASSIGNMENT_OR_ACCEPTANCE',
    'algorithm_source_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
    'created_utc': datetime.now(timezone.utc).isoformat(),
    'input_information_used': 'Only original bitmap pixels; no logical grids, target cells, previous projections, manual readings or predicted pixels used for detection.',
    'no_actual_world_or_absolute_error_claim': True,
    'predetermined_threshold_pairs': [[25, 75], [50, 150], [90, 180]],
    'method': 'Canny edges, closed convex four-corner contours, polygon diagonal intersection; all qualified contours retained without manual selection or adjustment.',
    'images': {}}
summary = []
for item in request['candidates']:
    sid = item['stage_id']
    stage = catalog['stages'][sid]
    image = stage['image']
    raw = (ROOT / 'rouge/data' / image['file']).read_bytes()
    assert sha256(raw).hexdigest() == image['sha256'] and len(raw) == image['bytes']
    decoded = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    assert tuple(decoded.shape[1::-1]) == (image['width'], image['height'])
    gray = cv2.cvtColor(decoded, cv2.COLOR_BGR2GRAY)
    candidates = []
    for low, high in outputs['predetermined_threshold_pairs']:
        edges = cv2.Canny(gray, low, high)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for index, contour in enumerate(contours):
            perimeter = cv2.arcLength(contour, True)
            if not 25 <= perimeter <= 500:
                continue
            polygon = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            if len(polygon) != 4 or not cv2.isContourConvex(polygon):
                continue
            area = abs(cv2.contourArea(polygon))
            x, y, width, height = cv2.boundingRect(polygon)
            if not (60 <= area <= 6000 and 0.4 <= width / height <= 4 and width >= 8 and height >= 8):
                continue
            vertices = polygon[:, 0, :].tolist()
            center = intersection(vertices)
            if center is None:
                continue
            candidates.append({'edge_thresholds': [low, high], 'contour_index': index,
                'vertices': vertices, 'area_px2': area, 'diagonal_intersection_pixel': center})
    outputs['images'][sid] = {'source_image': image, 'candidates': candidates,
        'no_cell_identification_or_surface_kind_inferred': True}
    summary.append({'image': sid, 'frozen_geometric_candidates': len(candidates)})
(OUT / 'image-only-first-observations.json').write_bytes(encode(outputs))
(OUT / 'candidate-request-inventory-original.json').write_bytes(request_raw)
(OUT / 'execution-image-observation.py').write_bytes(Path(__file__).read_bytes())
digest = sha256((OUT / 'image-only-first-observations.json').read_bytes()).hexdigest()
(OUT / 'image-observation-frozen.json').write_bytes(encode({'sha256': digest,
    'bytes': (OUT / 'image-only-first-observations.json').stat().st_size,
    'manual_cell_pixels_observed_at_freeze': False,
    'image_candidate_pixel_values_not_printed_to_manual_reader': True,
    'retuning_after_manual_comparison_allowed': False}))
print(json.dumps({'source_observation_only': True, 'frozen_file_sha256': digest,
                  'counts_only_no_pixel_values': summary}, ensure_ascii=False))
