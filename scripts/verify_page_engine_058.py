"""Read-only actual RapidOCR parity and exact-batch reuse pilot."""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
import sys
import time

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rouge.page_features import PageFeatureRouter
from rouge.page_ocr import PageOCR


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def differences(a, b, path=''):
    if type(a) is not type(b):
        return [{'path': path, 'before': a, 'after': b}]
    if isinstance(a, list):
        if len(a) != len(b):
            return [{'path': path+'.length', 'before': len(a), 'after': len(b)}]
        return [item for i, (x, y) in enumerate(zip(a, b))
                for item in differences(x, y, f'{path}[{i}]')]
    return [] if a == b else [{'path': path, 'before': a, 'after': b}]


def wire(value):
    return json.loads(json.dumps(value, default=lambda x: x.item() if isinstance(x, np.generic) else x.tolist()))


def main():
    epoch = ROOT / '.cache/research/page-ocr-058' / f'pilot-{time.time_ns()}'
    epoch.mkdir(parents=True, exist_ok=False)
    module = Path(__import__('rapidocr_onnxruntime.main', fromlist=['__file__']).__file__).parent
    code = [ROOT/'rouge/page_ocr.py', ROOT/'tests/test_page_ocr_058.py', Path(__file__),
            module/'main.py', module/'ch_ppocr_rec/text_recognize.py', module/'ch_ppocr_cls/text_cls.py']
    receipt = {'schema': 1, 'epoch': str(epoch), 'passed': False,
               'implementation_source_sha256': {str(p): sha(p) for p in code},
               'source': 'Installed rapidocr_onnxruntime 1.4.4 original source',
               'private_state_read': False, 'game_actions': 0, 'chat_requests': 0,
               'limits': ['Two preexisting public development samples, not an independent holdout.',
                          'Cold regional safety includes all exterior detector boxes.'], 'cases': []}
    engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)
    router = PageFeatureRouter()
    for name in ('operator-kaltsit', 'module-mechanist'):
        source = ROOT/'samples/native-client'/f'{name}.png'
        image = cv2.imdecode(np.fromfile(source, np.uint8), cv2.IMREAD_COLOR)
        plan = router.classify(image)
        regions = plan['candidates'][0]['regions'] if plan['specialized'] else None
        start = time.perf_counter()
        baseline, baseline_elapsed = engine(image)
        baseline_ms = (time.perf_counter()-start)*1000
        reader = PageOCR(engine)
        start = time.perf_counter()
        actual, actual_elapsed = reader.read(image, regions=regions)
        actual_ms = (time.perf_counter()-start)*1000
        cold_metrics = deepcopy(reader.metrics)
        start = time.perf_counter()
        warm, warm_elapsed = reader.read(image, regions=regions)
        warm_ms = (time.perf_counter()-start)*1000
        row = {'id': name, 'image_sha256': sha(source), 'plan': plan,
               'baseline_ms': baseline_ms, 'baseline_elapsed': baseline_elapsed,
               'page_ms': actual_ms, 'page_elapsed': actual_elapsed,
               'warm_ms': warm_ms, 'warm_elapsed': warm_elapsed,
               'cold_metrics': cold_metrics, 'warm_metrics': deepcopy(reader.metrics),
               'full_raw_differences': differences(wire(baseline), wire(actual)),
               'warm_raw_differences': differences(wire(actual), wire(warm)),
               'baseline': wire(baseline), 'actual': wire(actual), 'warm': wire(warm)}
        receipt['cases'].append(row)
        print(json.dumps({k: row[k] for k in ('id', 'baseline_ms', 'page_ms', 'warm_ms',
                                               'cold_metrics', 'warm_metrics', 'full_raw_differences')}, ensure_ascii=False), flush=True)
    receipt['implementation_source_stable'] = all(sha(p) == receipt['implementation_source_sha256'][str(p)]
                                                 for p in code)
    receipt['passed'] = (receipt['implementation_source_stable'] and
                         all(not r['full_raw_differences'] and not r['warm_raw_differences']
                             for r in receipt['cases']))
    output = epoch/'receipt.json'
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'passed': receipt['passed'], 'receipt': str(output)}, ensure_ascii=False))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
