"""Append owned-popup control features from one authorized development frame.

Source identifiers and rectangles describe reference construction only. Runtime
ORB searches every current frame and requires four static controls at a shared
affine. Recipient, held count, names, icons and effect prose are not templates.
The unmodified three other operator captures remain classifier holdouts.
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
INVENTORY = ROOT / '.cache/research/page-routing-056/epoch-1791136902879484600/inventory.json'
SOURCE_ID = 'kaltsit_owned'
STEM = 'owned-popup'
REGIONS = ((0., .085, .34, .90), (.24, .075, 1., .90), (0., .895, 1., 1.))
# Manual inspection of the original source: the header prefix ends before the
# varying count digit at x=266. Neither header number nor the button's circular
# count badge is retained in any descriptor or reference patch.
STATIC_PREFIX_SOURCE_BOX = (85, 232, 260, 258)
STATIC_BUTTON_SOURCE_BOX = (262, 143, 438, 191)
VARIABLE_COUNT_SOURCE_BOXES = ((262, 228, 282, 260), (440, 129, 476, 166))
CONTROL_FEATURE_BUDGET = {'left': 96, 'right': 48}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    manifest_path = OUTPUT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    old = [p for p in manifest['pages'] if p.get('template_family') != 'owned-popup-059']
    preserved = {p['features']: sha(OUTPUT / p['features']) for p in old}
    preserved.update({a['patch']: sha(OUTPUT / a['patch']) for p in old for a in p['anchors']})
    inventory = json.loads(INVENTORY.read_text(encoding='utf-8'))
    source_record = next(s for s in inventory['samples'] if s['id'] == SOURCE_ID)
    source = ROOT / source_record['image']
    if sha(source) != source_record['sha256']:
        raise ValueError('Sealed authorized source pixels changed')
    receipt = json.loads((ROOT / source_record['origin_receipt']).read_text(encoding='utf-8'))
    labels = ROOT / receipt['observation']
    texts = json.loads(labels.read_text(encoding='utf-8'))['texts']
    full = cv2.imdecode(np.fromfile(source, dtype=np.uint8), cv2.IMREAD_COLOR)
    full_h, full_w = full.shape[:2]
    left, top, right, bottom = source_record['client_rect']
    image = full[top:bottom, left:right]
    # ORB descriptors sample neighbours outside their keypoint centre. Blank
    # changing counts in training only, so those neighbouring descriptor bits
    # cannot accidentally encode the source's held count. Current frames and
    # their independent grayscale control verification remain untouched.
    feature_image = image.copy()
    for x0, y0, x1, y1 in VARIABLE_COUNT_SOURCE_BOXES:
        feature_image[y0-top:y1-top, x0-left:x1-left] = 0
    scale = manifest['long_edge'] / max(image.shape[:2])
    gray = cv2.resize(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), None,
                      fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    sh, sw = gray.shape
    controls = []
    for key, label, side in (('owned_button', '收藏品增益', 'left'),
                             ('owned_header_prefix', None, 'left'),
                             ('collapse', '收起', 'right'), ('squad', '编队', 'right')):
        if label is None:
            source_box = STATIC_PREFIX_SOURCE_BOX
        else:
            found = [t for t in texts if t['text'] == label and t['confidence'] >= .9]
            if len(found) != 1:
                raise ValueError('Unique actual static control required: ' + label)
            b = found[0]['box']
            source_box = (min(p[0] for p in b)*full_w, min(p[1] for p in b)*full_h,
                          max(p[0] for p in b)*full_w, max(p[1] for p in b)*full_h)
            if key == 'owned_button':
                # Include the stable magnifier, excluding the count badge.
                # The actual recognized text must lie inside this source box.
                sx0, sy0, sx1, sy1 = STATIC_BUTTON_SOURCE_BOX
                if not (sx0 <= source_box[0] < source_box[2] <= sx1 and
                        sy0 <= source_box[1] < source_box[3] <= sy1):
                    raise ValueError('Static button text moved outside the inspected source control')
                source_box = STATIC_BUTTON_SOURCE_BOX
        x0, y0 = np.floor([(source_box[0]-left)*scale, (source_box[1]-top)*scale]).astype(int)
        x1, y1 = np.ceil([(source_box[2]-left)*scale, (source_box[3]-top)*scale]).astype(int)
        controls.append({'key': key, 'side': side, 'box': [int(x0), int(y0), int(x1), int(y1)],
                         'source_control_box': list(source_box)})
    points, descriptors, groups = [], [], []
    variants = []
    for factor in (1., .8, .65):
        small = feature_image if factor == 1 else cv2.resize(feature_image, None, fx=factor, fy=factor)
        small_gray = cv2.resize(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (sw, sh), interpolation=cv2.INTER_AREA)
        variants.append(_scene_features(small_gray))
    for group, anchor in enumerate(controls):
        x0, y0, x1, y1 = anchor['box']
        added = 0
        for keypoints, desc in variants:
            indices = [i for i, (x, y) in enumerate(keypoints) if x0 <= x < x1 and y0 <= y < y1]
            selected = []
            for i in indices:
                if all(np.linalg.norm(keypoints[i]-keypoints[j]) >= 2.2 for j in selected):
                    selected.append(i)
                if len(selected) >= CONTROL_FEATURE_BUDGET[anchor['side']]:
                    break
            for i in selected:
                points.append(keypoints[i]); descriptors.append(desc[i]); groups.append(group)
            added += len(selected)
        if added < 8:
            raise ValueError('Insufficient static-control evidence: ' + anchor['key'])
        patch_name = STEM + '-' + anchor['key'] + '.png'
        cv2.imencode('.png', gray[y0:y1, x0:x1])[1].tofile(OUTPUT / patch_name)
        anchor.update(patch=patch_name, patch_sha256=sha(OUTPUT / patch_name), feature_count=added)
    feature_name = STEM + '.npz'
    np.savez_compressed(OUTPUT / feature_name, points=np.asarray(points, np.float32),
                        descriptors=np.asarray(descriptors, np.uint8), groups=np.asarray(groups, np.int16))
    page = {'page': 'run_owned_popup', 'template_family': 'owned-popup-059',
            'source': source.relative_to(ROOT).as_posix(), 'source_sha256': sha(source),
            'source_client_rect': source_record['client_rect'], 'labels_sha256': sha(labels),
            'feature_only_count_redactions': [list(b) for b in VARIABLE_COUNT_SOURCE_BOXES],
            'reference_size': [sw, sh], 'features': feature_name, 'features_sha256': sha(OUTPUT / feature_name),
            'derived_feature_scales': [1., .8, .65], 'independent_training_sources': 1,
            'control_feature_budget_per_view': CONTROL_FEATURE_BUDGET,
            'composite_page': True, 'facts_from_features': False, 'anchors': controls,
            'regions': [[round(a*sw), round(b*sh), round(c*sw), round(d*sh)] for a, b, c, d in REGIONS]}
    if any(sha(OUTPUT / name) != expected for name, expected in preserved.items()):
        raise ValueError('A previously sealed control asset changed')
    manifest['pages'] = old + [page]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'page': page['page'], 'preserved_binary_assets': len(preserved),
                      'old_assets_unchanged': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
