"""Visual page candidates for OCR scheduling, never operator observations.

Only independently matched static controls can authorize scheduling regions.
Their transform may be reused while every matched control has byte-identical
current pixels, shape and dtype. This is not a proof of a complete or exclusive
current page: the OCR caller must discover domain-exterior changes immediately
and validate current semantics. Unknown, clipped or ambiguous matches request
full discovery. No operator or run values come from these visual plans.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import time

import cv2
import numpy as np


def _scene_features(gray):
    """Equal spatial opportunity for controls and highly textured portraits.

    Tiles partition *each new frame*, with overlapping descriptor context. They
    are feature-budget cells, not saved field locations or page ROIs.
    """
    h, w = gray.shape
    # Edge contrast gives the pale module headings the same feature budget as
    # black attribute rows. The later grayscale control check is independent.
    feature_image = cv2.Canny(gray, 18, 48)
    orb = cv2.ORB_create(nfeatures=1000, scaleFactor=1.15, nlevels=8,
                         edgeThreshold=5, patchSize=19, fastThreshold=5)
    points, descriptions = [], []
    for top in range(0, h, 190):
        for left in range(0, w, 260):
            right, bottom = min(w, left+260), min(h, top+190)
            x0, y0, x1, y1 = max(0, left-36), max(0, top-36), min(w, right+36), min(h, bottom+36)
            kps, desc = orb.detectAndCompute(feature_image[y0:y1, x0:x1], None)
            if desc is None:
                continue
            for i, kp in enumerate(kps):
                x, y = kp.pt[0]+x0, kp.pt[1]+y0
                if left <= x < right and top <= y < bottom:
                    points.append((x, y))
                    descriptions.append(desc[i])
    return np.asarray(points, np.float32), (np.asarray(descriptions, np.uint8) if descriptions else None)


class PageFeatureRouter:
    def __init__(self, *, directory=None):
        self.directory = Path(directory) if directory is not None else Path(__file__).parent / 'data/page-features'
        manifest = json.loads((self.directory / 'manifest.json').read_text(encoding='utf-8'))
        if manifest.get('schema') != 1 or manifest.get('facts_from_features') is not False:
            raise ValueError('Invalid static-control feature manifest')
        self.long_edge = int(manifest['long_edge'])
        self.pages = []
        for page in manifest['pages']:
            path = self.directory / page['features']
            if hashlib.sha256(path.read_bytes()).hexdigest() != page['features_sha256']:
                raise ValueError('Static-control feature checksum mismatch')
            with np.load(path, allow_pickle=False) as arrays:
                record = dict(page, points=arrays['points'].copy(), descriptors=arrays['descriptors'].copy(),
                              groups=arrays['groups'].copy())
            patches = []
            for anchor in page['anchors']:
                encoded = (self.directory / anchor['patch']).read_bytes()
                expected = anchor.get('patch_sha256')
                if expected is not None and hashlib.sha256(encoded).hexdigest() != expected:
                    raise ValueError('Static-control patch checksum mismatch')
                patch = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                x0, y0, x1, y1 = anchor['box']
                if patch is None or patch.size == 0 or patch.shape != (y1-y0, x1-x0):
                    raise ValueError('Invalid static-control patch image')
                patches.append(patch)
            record['patches'] = patches
            self.pages.append(record)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
        self._plan_cache = None

    def _cached_plan(self, image):
        cache = self._plan_cache
        if cache is None or image.shape != cache['shape'] or image.dtype.str != cache['dtype']:
            return None
        for region, previous in zip(cache['regions'], cache['pixels']):
            x0,y0,x1,y1=region
            if not np.array_equal(image[y0:y1,x0:x1],previous):return None
        return deepcopy(cache['plan'])

    def _remember_plan(self, image, result):
        self._plan_cache = None
        if not result['specialized'] or len(result['candidates']) != 1:return
        regions=result['candidates'][0].get('control_regions',[])
        h,w=image.shape[:2]
        if not regions or any(not (0<=x0<x1<=w and 0<=y0<y1<=h)
                              for x0,y0,x1,y1 in regions):return
        self._plan_cache={'shape':image.shape,'dtype':image.dtype.str,
            'regions':deepcopy(regions),'pixels':[image[y0:y1,x0:x1].copy() for x0,y0,x1,y1 in regions],
            'plan':deepcopy(result)}

    def classify(self, image):
        started = time.perf_counter()
        result = {'candidates': [], 'specialized': False, 'fallback_reason': '',
                  'coordinate_space': 'input_frame_pixels', 'facts_from_features': False}
        def finish(reason=''):
            result['fallback_reason'] = reason
            result['elapsed_ms'] = (time.perf_counter() - started)*1000
            result['feature_reuse']='none'
            if isinstance(image,np.ndarray):self._remember_plan(image,result)
            else:self._plan_cache=None
            return result
        if image is None or not isinstance(image, np.ndarray) or image.size == 0:
            return finish('invalid_frame')
        if (image.dtype != np.uint8 or image.ndim not in (2, 3) or
                (image.ndim == 3 and image.shape[2] not in (3, 4))):
            return finish('invalid_frame')
        h, w = image.shape[:2]
        # Do not upscale vanished glyphs into apparent evidence.
        if w < 800 or h < 430:
            return finish('resolution_too_low')
        cached=self._cached_plan(image)
        if cached is not None:
            # This preserves a scheduling transform only while every independently
            # matched control has exactly the same current pixels. Page facts are
            # still read anew; domain-exterior changes require immediate full OCR.
            cached['elapsed_ms']=(time.perf_counter()-started)*1000
            cached['feature_reuse']='exact_controls'
            return cached
        scale = min(1., self.long_edge / max(h, w))
        gray = cv2.cvtColor(image[:, :, :3], cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        if scale != 1:
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        points, desc = _scene_features(gray)
        if desc is None:
            return finish('no_visual_controls')
        for page in self.pages:
            candidate = self._match(page, gray, points, desc, scale, w, h)
            if candidate is not None:
                result['candidates'].append(candidate)
        if len(result['candidates']) != 1:
            return finish('conflicting_page_candidates' if result['candidates'] else 'unknown_or_incomplete_controls')
        result['specialized'] = True
        return finish()

    def _match(self, page, gray, points, desc, scale, w, h):
        pairs = self.matcher.knnMatch(page['descriptors'], desc, k=2)
        good = [a for pair in pairs if len(pair) == 2 for a, b in [pair]
                if a.distance <= 65 and a.distance < .84*b.distance]
        # Derived-scale descriptors are alternative views of the same source.
        # One observed scene feature counts only once as geometric evidence.
        unique = {}
        for match in good:
            old = unique.get(match.trainIdx)
            if old is None or match.distance < old.distance:
                unique[match.trainIdx] = match
        good = list(unique.values())
        if len(good) < 8:
            return None
        source = np.asarray([page['points'][m.queryIdx] for m in good], np.float32)
        target = np.asarray([points[m.trainIdx] for m in good], np.float32)
        matrix, inliers = cv2.estimateAffinePartial2D(source, target, method=cv2.RANSAC,
                                                     ransacReprojThreshold=2.2, maxIters=1000,
                                                     confidence=.995, refineIters=10)
        if matrix is None or inliers is None:
            return None
        chosen = inliers.ravel().astype(bool)
        if int(chosen.sum()) < 8 or chosen.mean() < .25:
            return None
        # The client layout preserves scale and upright geometry. A shear or
        # perspective fit is not permitted to force unrelated controls together.
        a, b = matrix[0, 0], matrix[1, 0]
        ratio = float(np.hypot(a, b))
        if not .45 <= ratio <= 2.1 or abs(np.degrees(np.arctan2(b, a))) > 1.2:
            return None
        evidence = []
        inverse = cv2.invertAffineTransform(matrix)
        reference_w, reference_h = page['reference_size']
        aligned = cv2.warpAffine(gray, inverse, (reference_w, reference_h), flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        supported_sides = set()
        for group, (anchor, patch) in enumerate(zip(page['anchors'], page['patches'])):
            indices = [i for i, m in enumerate(good) if chosen[i] and page['groups'][m.queryIdx] == group]
            if len(indices) >= 2:
                supported_sides.add(anchor['side'])
            x0, y0, x1, y1 = anchor['box']
            search = aligned[y0-2:y1+2, x0-2:x1+2]
            if search.shape[0] < patch.shape[0] or search.shape[1] < patch.shape[1]:
                return None
            values = cv2.matchTemplate(search, patch, cv2.TM_CCOEFF_NORMED)
            _, correlation, _, location = cv2.minMaxLoc(values)
            ox, oy = location
            current = search[oy:oy+patch.shape[0], ox:ox+patch.shape[1]]
            contrast_ratio = float(np.std(current)/max(1., np.std(patch)))
            # Correlation alone would accept a dimmed underlying page beneath
            # an unsupported overlay. Require current control contrast too.
            if (np.std(current) < 12 or not .72 <= contrast_ratio <= 1.3 or
                    abs(float(np.mean(current))-float(np.mean(patch))) > 30):
                return None
            if not np.isfinite(correlation) or correlation < .85:
                return None
            evidence.append({'control': anchor['key'], 'side': anchor['side'],
                             'inliers': len(indices), 'visual_correlation': round(correlation, 5),
                             'local_offset': [ox-2, oy-2], 'contrast_ratio': round(contrast_ratio, 5)})
        # A single glyph/texture cannot fit a page. Geometric features must
        # independently locate both sides, and all four control images must
        # agree at that shared transform in this frame.
        if supported_sides != {'left', 'right'}:
            return None
        corners = cv2.transform(np.array([[[0, 0], [reference_w, 0],
                                          [reference_w, reference_h], [0, reference_h]]], np.float32), matrix)[0]
        # Complete required regions must be visible. A cropped page remains a
        # full discovery candidate; it cannot authorize inherited field values.
        tolerance = 3
        if (corners[:, 0].min() < -tolerance or corners[:, 1].min() < -tolerance or
                corners[:, 0].max() > gray.shape[1]+tolerance or
                corners[:, 1].max() > gray.shape[0]+tolerance):
            return None
        regions = []
        for x0, y0, x1, y1 in page['regions']:
            pts = cv2.transform(np.array([[[x0, y0], [x1, y0], [x1, y1], [x0, y1]]], np.float32), matrix)[0]/scale
            left, top = np.floor(pts.min(axis=0)).astype(int)
            right, bottom = np.ceil(pts.max(axis=0)).astype(int)
            padding = max(4, round(6*ratio/scale))
            regions.append([max(0, int(left)-padding), max(0, int(top)-padding),
                            min(w, int(right)+padding), min(h, int(bottom)+padding)])
        exposed = matrix.copy()/scale
        control_regions=[]
        for anchor in page['anchors']:
            x0,y0,x1,y1=anchor['box']
            points=cv2.transform(np.array([[[x0-3,y0-3],[x1+3,y0-3],
                                           [x1+3,y1+3],[x0-3,y1+3]]],np.float32),exposed)[0]
            left,top=np.floor(points.min(axis=0)).astype(int)
            right,bottom=np.ceil(points.max(axis=0)).astype(int)
            control_regions.append([int(left),int(top),int(right),int(bottom)])
        return {'page': page['page'], 'regions': regions, 'transform': exposed.tolist(),
                'control_regions':control_regions,
                'reference_size': page['reference_size'], 'evidence': evidence,
                'matched_controls': len(evidence), 'reason': 'independent_controls_and_shared_affine',
                'facts_from_features': False}
