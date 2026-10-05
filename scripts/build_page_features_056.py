"""Build static UI-control features from authorized original captures.

This does not train on names, numbers, portraits or read private runtime files.
Run from the project root with the existing OpenCV dependency.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.page_features import _scene_features
OUTPUT = ROOT / 'rouge/data/page-features'
LONG_EDGE = 1280

# Bounding boxes below come from the matching original OCR labels. They are
# reference-image coordinates; runtime matching searches the complete new frame.
SPECS = {
    'operator_detail': {
        'source': 'operator-kaltsit',
        'anchors': [('attributes', '属性', 'left'), ('trust', '信赖值', 'left'),
                    ('elite', '精英化', 'right'), ('potential', '潜能', 'right')],
        # Leave wide context for long Chinese/English names. OCR must derive
        # identity from current pixels; a short reference name cannot size it.
        # Distinct controls locate these relative text bands in each new frame.
        # The name band remains wide and includes the taller Mechanist/SilverAsh
        # OCR lines; portrait/animation gaps between bands need no field OCR.
        'regions': [[0, .405, .30, .665], [0, .665, .56, .85],
                    [0, .835, .345, .99], [.71, .20, .99, .975]],
    },
    'operator_module': {
        'source': 'module-mechanist',
        'anchors': [('base_attributes', '基础数值', 'left'), ('trait', '特性', 'left'),
                    ('talent', '天赋', 'left'), ('original_badge', 'ORIGINAL', 'right')],
        'regions': [[.008, .12, .465, .995], [.475, .15, .995, .955]],
    },
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_orb():
    return cv2.ORB_create(nfeatures=5000, scaleFactor=1.15, nlevels=8,
                          edgeThreshold=5, patchSize=19, fastThreshold=8)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = {'schema': 1, 'feature': 'ORB', 'long_edge': LONG_EDGE,
                'facts_from_features': False, 'pages': []}
    for page, spec in SPECS.items():
        source = ROOT / 'samples/native-client' / (spec['source'] + '.png')
        labels = source.with_name(spec['source'] + '-ocr.json')
        image = cv2.imdecode(np.fromfile(source, dtype=np.uint8), cv2.IMREAD_COLOR)
        h, w = image.shape[:2]
        scale = LONG_EDGE / max(h, w)
        gray = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), None,
                          fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        sh, sw = gray.shape
        texts = json.loads(labels.read_text(encoding='utf-8'))['texts']
        points, descriptors, groups, controls = [], [], [], []
        variants = []
        for factor in (1., .8, .65):
            smaller = image if factor == 1 else cv2.resize(image, None, fx=factor, fy=factor)
            small_gray = cv2.cvtColor(smaller, cv2.COLOR_BGR2GRAY)
            small_gray = cv2.resize(small_gray, (sw, sh), interpolation=cv2.INTER_AREA)
            keypoints, all_descriptors = _scene_features(small_gray)
            variants.append((keypoints, all_descriptors))
        for group, (key, label, side) in enumerate(spec['anchors']):
            found = [t for t in texts if t['text'] == label and t['confidence'] >= .9]
            if len(found) != 1:
                raise RuntimeError('Reference label must be unique: ' + label)
            box = found[0]['box']
            x0, y0 = np.floor([min(p[0] for p in box)*sw,
                               min(p[1] for p in box)*sh]).astype(int)
            x1, y1 = np.ceil([max(p[0] for p in box)*sw,
                              max(p[1] for p in box)*sh]).astype(int)
            added = 0
            for keypoints, all_descriptors in variants:
                indices = [i for i, (x, y) in enumerate(keypoints) if x0 <= x < x1 and y0 <= y < y1]
                selected = []
                for i in indices:
                    kp = keypoints[i]
                    if all(np.linalg.norm(kp - keypoints[j]) >= 2.2 for j in selected):
                        selected.append(i)
                    if len(selected) >= 48:
                        break
                for i in selected:
                    points.append(keypoints[i])
                    descriptors.append(all_descriptors[i])
                    groups.append(group)
                added += len(selected)
            if added < 8:
                raise RuntimeError('Insufficient control features: ' + key)
            patch_name = page + '-' + key + '.png'
            patch = gray[y0:y1, x0:x1]
            cv2.imencode('.png', patch)[1].tofile(OUTPUT / patch_name)
            controls.append({'key': key, 'side': side, 'box': [int(x0), int(y0), int(x1), int(y1)],
                             'patch': patch_name, 'patch_sha256': sha(OUTPUT / patch_name),
                             'feature_count': added})
        feature_name = page + '.npz'
        np.savez_compressed(OUTPUT / feature_name, points=np.asarray(points, np.float32),
                            descriptors=np.asarray(descriptors, np.uint8),
                            groups=np.asarray(groups, np.int16))
        manifest['pages'].append({'page': page, 'source': str(source.relative_to(ROOT)).replace('\\', '/'),
                                 'source_sha256': sha(source), 'labels_sha256': sha(labels),
                                 'reference_size': [sw, sh], 'features': feature_name,
                                 'features_sha256': sha(OUTPUT / feature_name),
                                 'derived_feature_scales': [1., .8, .65],
                                 'independent_training_sources': 1,
                                 'anchors': controls,
                                 'regions': [[round(a*sw), round(b*sh), round(c*sw), round(d*sh)]
                                             for a, b, c, d in spec['regions']]})
    (OUTPUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n',
                                         encoding='utf-8')
    print(json.dumps({'pages': {p['page']: sum(a['feature_count'] for a in p['anchors'])
                               for p in manifest['pages']}, 'output': str(OUTPUT)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
