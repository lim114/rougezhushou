"""Append roster UI-control prototypes without rebuilding the verified pages.

The two roster templates differ only in the selected-state colour of the skill
tab. They schedule a composite roster family: selection and buffs are still
facts that the current OCR/semantic readers must establish. Only the four
static control patches are written; portraits, names and values are excluded.
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
SPECS = (
    ('roster-overview', 'run-roster'),
    ('roster-selected', 'run-mechanist-selected'),
)
ANCHORS = (('skills', '技能', 'left'), ('branch', '分支+', 'left'),
           ('human_resource', 'HUMAN', 'right'), ('squad', '编队', 'right'))
# Template coordinates are transformed by the independently located controls
# on each current frame. The whole roster canvas is retained: neither number
# of cards nor a previously seen identity determines its OCR domain.
REGIONS = ((0., .115, .245, .90), (.245, .055, 1., .90),
           (0., .895, 1., 1.))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest_path = OUTPUT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    old_pages = [p for p in manifest['pages'] if p.get('template_family') != 'roster-058']
    protected = {p['features']: sha(OUTPUT / p['features']) for p in old_pages}
    protected.update({a['patch']: sha(OUTPUT / a['patch']) for p in old_pages for a in p['anchors']})
    additions = []
    for stem, source_stem in SPECS:
        source = ROOT / 'samples/native-client' / (source_stem + '.png')
        labels = source.with_name(source_stem + '-ocr.json')
        image = cv2.imdecode(np.fromfile(source, dtype=np.uint8), cv2.IMREAD_COLOR)
        h, w = image.shape[:2]
        scale = manifest['long_edge'] / max(h, w)
        gray = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), None,
                          fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        sh, sw = gray.shape
        texts = json.loads(labels.read_text(encoding='utf-8'))['texts']
        variants = []
        for factor in (1., .8, .65):
            small = image if factor == 1 else cv2.resize(image, None, fx=factor, fy=factor)
            small_gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            variants.append(_scene_features(cv2.resize(small_gray, (sw, sh), interpolation=cv2.INTER_AREA)))
        points, descriptors, groups, controls = [], [], [], []
        for group, (key, label, side) in enumerate(ANCHORS):
            found = [t for t in texts if t['text'] == label and t['confidence'] >= .9]
            if len(found) != 1:
                raise ValueError('A single verified reference label is required: ' + label)
            box = found[0]['box']
            x0, y0 = np.floor([min(p[0] for p in box)*sw, min(p[1] for p in box)*sh]).astype(int)
            x1, y1 = np.ceil([max(p[0] for p in box)*sw, max(p[1] for p in box)*sh]).astype(int)
            added = 0
            for keypoints, all_descriptors in variants:
                indices = [i for i, (x, y) in enumerate(keypoints) if x0 <= x < x1 and y0 <= y < y1]
                selected = []
                for i in indices:
                    if all(np.linalg.norm(keypoints[i] - keypoints[j]) >= 2.2 for j in selected):
                        selected.append(i)
                    if len(selected) >= 48:
                        break
                for i in selected:
                    points.append(keypoints[i]); descriptors.append(all_descriptors[i]); groups.append(group)
                added += len(selected)
            if added < 8:
                raise ValueError('Insufficient static control descriptors: ' + key)
            patch_name = stem + '-' + key + '.png'
            cv2.imencode('.png', gray[y0:y1, x0:x1])[1].tofile(OUTPUT / patch_name)
            controls.append({'key': key, 'side': side, 'box': [int(x0), int(y0), int(x1), int(y1)],
                             'patch': patch_name, 'patch_sha256': sha(OUTPUT / patch_name),
                             'feature_count': added})
        feature_name = stem + '.npz'
        np.savez_compressed(OUTPUT / feature_name, points=np.asarray(points, np.float32),
                            descriptors=np.asarray(descriptors, np.uint8), groups=np.asarray(groups, np.int16))
        additions.append({'page': 'run_roster', 'template_family': 'roster-058', 'variant': stem,
                          'source': source.relative_to(ROOT).as_posix(), 'source_sha256': sha(source),
                          'labels_sha256': sha(labels), 'reference_size': [sw, sh],
                          'features': feature_name, 'features_sha256': sha(OUTPUT / feature_name),
                          'derived_feature_scales': [1., .8, .65], 'independent_training_sources': 1,
                          'composite_page': True, 'facts_from_features': False,
                          'anchors': controls,
                          'regions': [[round(a*sw), round(b*sh), round(c*sw), round(d*sh)]
                                      for a, b, c, d in REGIONS]})
    if any(sha(OUTPUT / name) != expected for name, expected in protected.items()):
        raise ValueError('A previously verified control asset changed')
    manifest['pages'] = old_pages + additions
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'added': [p['variant'] for p in additions], 'protected_assets': len(protected),
                      'old_assets_unchanged': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
