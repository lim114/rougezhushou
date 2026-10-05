"""Deterministic one-source glyph build; independent holdout is never loaded.

This is supervised shape-template training, not a digit OCR model. Resized train
variants calibrate robustness but are explicitly not independent validation.
"""
from pathlib import Path
import hashlib
import json
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.counter_badges import _candidate_matches

OUT = ROOT / '.cache/research/p1-counter-training-054'
DATA = ROOT / 'rouge/data'
SOURCE = ROOT / '.cache/research/p1-counter-images-054/source/taptap-hydra-100.jpg'
SOURCE_HASH = '00f11513e0effadc0a0611aae7ac5353156dcbfdfec7002988675bbd7981012f'
MARKER = (549, 898, 576, 923)
OCR_BOX = [[.172379, .619420], [.199093, .619420], [.199093, .647321], [.172379, .647321]]
NEGATIVES = (
    ('run-relic-open.png', 'run-relic-open-ocr.json'),
    ('run-map-closed.png', 'run-map-closed-ocr.json'),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    image = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f'Cannot decode {path.name}')
    return image


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def build():
    if sha(SOURCE) != SOURCE_HASH:
        raise ValueError('Pinned training source changed')
    source = load(SOURCE)
    assert source.shape[:2] == (1440, 3168)
    settings = {
        'schema_version': 1, 'template_file': 'ui-icons/counter-badge-up-054.png',
        'white_min': 190, 'chroma_max': 45, 'ocr_min': .95,
        'left_search_fonts': 1.8, 'right_search_fonts': .95,
        'minimum_score': None,
        'training_source_sha256': sha(SOURCE),
        'scope': 'White upward counter glyph next to high-confidence OCR integer; no item binding',
        'value_range': [0, 999],
        'observed_positive_values': [15],
    }
    x0, y0, x1, y1 = MARKER
    pixels = source[y0:y1, x0:x1]
    template = ((pixels.min(axis=2) >= settings['white_min']) &
                (pixels.max(axis=2).astype(np.int16) - pixels.min(axis=2) <= settings['chroma_max']))
    template_path = DATA / settings['template_file']
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_bytes = cv2.imencode('.png', template.astype(np.uint8) * 255,
                                 [cv2.IMWRITE_PNG_COMPRESSION, 9])[1].tobytes()
    template_path.write_bytes(template_bytes)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'train-original.jpg').write_bytes(SOURCE.read_bytes())
    (OUT / 'train-marker.png').write_bytes(template_bytes)
    cv2.imencode('.png', source[875:955, 530:652], [cv2.IMWRITE_PNG_COMPRESSION, 9])[1].tofile(OUT / 'train-context.png')
    ocr = {'text': '15', 'confidence': .99, 'box': OCR_BOX}
    positives = []
    for scale in (.5, .75, 1., 1.25):
        scaled = cv2.resize(source, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA if scale <= 1 else cv2.INTER_LINEAR)
        candidates = _candidate_matches(scaled, [ocr], settings, template)
        valid = [candidate for candidate in candidates if candidate['value'] == 15]
        if len(valid) != 1:
            raise ValueError(f'Training variant {scale} has {len(valid)} geometry-valid counters')
        positives.append({'scale': scale, 'score': valid[0]['score'], 'source_sha256': sha(SOURCE),
                          'role': 'derived_training_only', 'split_group': 'taptap-user-33684794'})
    negatives = []
    for image_name, ocr_name in NEGATIVES:
        image_path = ROOT / 'samples/native-client' / image_name
        ocr_path = image_path.with_name(ocr_name)
        image = load(image_path)
        texts = json.loads(ocr_path.read_text(encoding='utf-8'))['texts']
        candidates = _candidate_matches(image, texts, settings, template)
        negatives.append({'file': str(image_path.relative_to(ROOT)).replace('\\', '/'),
                          'sha256': sha(image_path), 'ocr_file': str(ocr_path.relative_to(ROOT)).replace('\\', '/'),
                          'ocr_sha256': sha(ocr_path), 'max_score': max((c['score'] for c in candidates), default=0.),
                          'candidate_count': len(candidates), 'role': 'negative_calibration',
                          'split_group': 'native-legacy-calibration'})
    minimum_positive = min(item['score'] for item in positives)
    maximum_negative = max(item['max_score'] for item in negatives)
    # The gap is computed only from train and calibration negatives. Holdout
    # cannot alter a threshold or become another training variant.
    if minimum_positive - maximum_negative < .08:
        raise ValueError('No reliable training/negative separation; keep unsupported')
    settings['minimum_score'] = round(max(.80, (minimum_positive + maximum_negative) / 2), 6)
    if settings['minimum_score'] >= minimum_positive:
        raise ValueError('Training examples do not meet the conservative minimum')
    settings['template_sha256'] = hashlib.sha256(template_bytes).hexdigest()
    settings['calibration'] = {'minimum_train_score': minimum_positive,
                             'maximum_negative_score': maximum_negative,
                             'method': 'max(0.80, midpoint of minimum derived-train and maximum negative score)',
                             'holdout_used': False}
    save_json(DATA / 'counter-badge-reference.json', settings)
    save_json(OUT / 'calibration.json', {'settings': settings, 'train_variants': positives, 'negatives': negatives})
    save_json(OUT / 'ANNOTATIONS.json', {
        'schema_version': 1,
        'training': {'source': str(SOURCE.relative_to(ROOT)).replace('\\', '/'), 'sha256': sha(SOURCE),
                     'page_url': 'https://www.taptap.cn/moment/850014064758230845', 'author': '玲珑',
                     'split_group': 'taptap-user-33684794', 'marker_box_xyxy': MARKER,
                     'numeric_value': 15, 'digit_ink_box_xyxy': [588, 899, 623, 925],
                     'ocr_box': OCR_BOX, 'ocr_confidence_fixture': .99,
                     'confidence_note': 'Confidence fixture for glyph-only test; no general OCR accuracy claim',
                     'annotation': 'Manual review of original public pixels: white upward glyph and 15 under 悲伤的红'},
        'negative_calibration': negatives,
        'holdout': {'source': '.cache/research/p1-counter-images-054/source/taptap-hydra-run-2.jpg',
                    'page_url': 'https://www.taptap.cn/moment/835181757304145324', 'author': '打工人哈基芹',
                    'split_group': 'taptap-user-591798893', 'numeric_value': 1,
                    'item_identity': None, 'item_identity_reason': 'Name above frame; no ID label used',
                    'pixels_loaded_by_build': False},
        'split_policy': 'One original article/author/run per split; every crop/scale of training original stays training',
        'limits': ['Only one positive glyph source in training; digit model is the existing OCR',
                   'Not an inventory completeness, used-state or arbitrary counter accuracy model',
                   'No missing marker is interpreted as zero', 'No full-frame template search'],
    })
    print(json.dumps({'training_min_score': minimum_positive, 'negative_max_score': maximum_negative,
                      'minimum_score': settings['minimum_score'], 'holdout_loaded': False}))


if __name__ == '__main__':
    build()
