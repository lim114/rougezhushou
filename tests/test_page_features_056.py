"""Current-frame page routing tests; original captures and derived stress cases."""
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch

import cv2
import numpy as np

from rouge.page_features import PageFeatureRouter

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / 'samples/native-client'


def load(name):
    return cv2.imdecode(np.fromfile(SAMPLES / (name+'.png'), dtype=np.uint8), cv2.IMREAD_COLOR)


class PageFeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = PageFeatureRouter()

    def assert_route(self, image, page):
        result = self.router.classify(image)
        self.assertTrue(result['specialized'], result)
        self.assertEqual([c['page'] for c in result['candidates']], [page])
        candidate = result['candidates'][0]
        self.assertEqual(candidate['matched_controls'], 4)
        self.assertEqual({e['side'] for e in candidate['evidence']}, {'left', 'right'})
        self.assertFalse(result['facts_from_features'])
        self.assertFalse(candidate['facts_from_features'])
        for forbidden in ('fields', 'skill_ranks', 'name', 'id', 'potential', 'trust', 'level'):
            self.assertNotIn(forbidden, candidate)
        h, w = image.shape[:2]
        for left, top, right, bottom in candidate['regions']:
            self.assertTrue(0 <= left < right <= w and 0 <= top < bottom <= h)
        return result

    def test_original_three_operator_pages(self):
        # Only Kal'tsit supplies detail training controls. Other two originals
        # independently test general controls across portraits and values.
        for name in ('operator-kaltsit', 'operator-mechanist', 'operator-silverash'):
            with self.subTest(name=name):
                self.assert_route(load(name), 'operator_detail')

    def test_original_module_and_animation(self):
        self.assert_route(load('module-mechanist'), 'operator_module')
        self.assert_route(load('operator-kaltsit-animated'), 'operator_detail')

    def test_continuous_scales(self):
        for name, page in [('operator-kaltsit', 'operator_detail'), ('operator-mechanist', 'operator_detail'),
                           ('operator-silverash', 'operator_detail'), ('module-mechanist', 'operator_module')]:
            for factor in (.65, .8, 1.25):
                with self.subTest(name=name, factor=factor):
                    self.assert_route(cv2.resize(load(name), None, fx=factor, fy=factor), page)

    def test_translation_maps_current_regions(self):
        for name, page in [('operator-kaltsit', 'operator_detail'), ('operator-mechanist', 'operator_detail'),
                           ('operator-silverash', 'operator_detail'), ('module-mechanist', 'operator_module')]:
            original = load(name)
            h, w = original.shape[:2]
            canvas = np.zeros((h+95, w+125, 3), np.uint8)
            canvas[35:35+h, 45:45+w] = original
            result = self.assert_route(canvas, page)
            transform = np.asarray(result['candidates'][0]['transform'])
            self.assertAlmostEqual(float(transform[0, 2]), 45, delta=3)
            self.assertAlmostEqual(float(transform[1, 2]), 35, delta=3)

    def test_rois_include_all_original_non_title_ocr(self):
        for name, page in [('operator-kaltsit', 'operator_detail'), ('operator-mechanist', 'operator_detail'),
                           ('operator-silverash', 'operator_detail'), ('module-mechanist', 'operator_module')]:
            image = load(name)
            result = self.assert_route(image, page)
            regions = result['candidates'][0]['regions']
            h, w = image.shape[:2]
            texts = json.loads((SAMPLES / (name+'-ocr.json')).read_text(encoding='utf-8'))['texts']
            for item in texts:
                if item['text'] == '明日方舟':
                    continue
                x0 = min(p[0] for p in item['box'])*w
                y0 = min(p[1] for p in item['box'])*h
                x1 = max(p[0] for p in item['box'])*w
                y1 = max(p[1] for p in item['box'])*h
                self.assertTrue(any(left-2 <= x0 and top-2 <= y0 and right+2 >= x1 and bottom+2 >= y1
                                    for left, top, right, bottom in regions), (name, item['text'], regions))

    def test_all_other_original_pages_fallback(self):
        excluded = {'operator-kaltsit', 'operator-kaltsit-animated', 'operator-mechanist',
                    'operator-silverash', 'module-mechanist',
                    'run-roster','run-mechanist-selected','run-emergency-mechanist'}
        for path in sorted(SAMPLES.glob('*.png')):
            if path.stem in excluded:
                continue
            with self.subTest(page=path.stem):
                result = self.router.classify(load(path.stem))
                self.assertFalse(result['specialized'], result)
                self.assertEqual(result['candidates'], [])

    def test_changed_numbers_are_never_facts(self):
        image = load('operator-kaltsit')
        h, w = image.shape[:2]
        labels = json.loads((SAMPLES / 'operator-kaltsit-ocr.json').read_text(encoding='utf-8'))['texts']
        for item in labels:
            if not re.search(r'\d', item['text']):
                continue
            x0, y0 = int(min(p[0] for p in item['box'])*w), int(min(p[1] for p in item['box'])*h)
            x1, y1 = int(max(p[0] for p in item['box'])*w), int(max(p[1] for p in item['box'])*h)
            cv2.rectangle(image, (x0, y0), (x1, y1), (32, 32, 32), -1)
            cv2.putText(image, '37', (x0+1, y1-2), cv2.FONT_HERSHEY_SIMPLEX, .7, (255, 255, 255), 1)
        self.assert_route(image, 'operator_detail')

    def test_each_missing_control_falls_back(self):
        for page in self.router.pages:
            image = cv2.imdecode(np.fromfile(ROOT / page['source'], dtype=np.uint8), cv2.IMREAD_COLOR)
            # Some authorized WGC sources include the window frame; their
            # descriptors were built from the recorded client rectangle.
            if page.get('source_client_rect'):
                left, top, right, bottom = page['source_client_rect']
                image = image[top:bottom, left:right]
            h, w = image.shape[:2]
            rw, rh = page['reference_size']
            for anchor in page['anchors']:
                with self.subTest(page=page['page'], control=anchor['key']):
                    altered = image.copy()
                    x0, y0, x1, y1 = anchor['box']
                    cv2.rectangle(altered, (int(x0*w/rw)-8, int(y0*h/rh)-8),
                                  (int(x1*w/rw)+8, int(y1*h/rh)+8), (0, 0, 0), -1)
                    result = self.router.classify(altered)
                    self.assertFalse(result['specialized'], result)

    def test_single_texture_never_confirms_page(self):
        original = load('operator-kaltsit')
        single = np.zeros_like(original)
        h, w = single.shape[:2]
        page = self.router.pages[0]
        rw, rh = page['reference_size']
        x0, y0, x1, y1 = page['anchors'][1]['box']
        x0, y0, x1, y1 = int(x0*w/rw)-15, int(y0*h/rh)-15, int(x1*w/rw)+15, int(y1*h/rh)+15
        single[y0:y1, x0:x1] = original[y0:y1, x0:x1]
        self.assertFalse(self.router.classify(single)['specialized'])

    def test_dimmed_overlay_cropped_and_low_resolution_fallback(self):
        original = load('operator-kaltsit')
        h, w = original.shape[:2]
        cases = [np.round(original*.5).astype(np.uint8), original[:int(h*.90)],
                 original[:, int(w*.12):], cv2.resize(original, None, fx=.35, fy=.35)]
        for image in cases:
            with self.subTest(shape=image.shape):
                self.assertFalse(self.router.classify(image)['specialized'])

    def test_page_conflict_retains_multiple_candidates_and_falls_back(self):
        alternatives = [{'page': 'operator_detail'}, {'page': 'operator_module'}]
        with patch.object(self.router, '_match', side_effect=alternatives+[None]*(len(self.router.pages)-len(alternatives))):
            result = self.router.classify(load('operator-kaltsit'))
        self.assertFalse(result['specialized'])
        self.assertEqual(result['fallback_reason'], 'conflicting_page_candidates')
        self.assertEqual(result['candidates'], alternatives)

    def test_no_previous_page_values_or_mutable_result_reused(self):
        original = load('operator-kaltsit')
        first = self.assert_route(original, 'operator_detail')
        first['candidates'][0]['regions'][0][0] = -999
        self.assert_route(original, 'operator_detail')
        result = self.router.classify(np.zeros_like(original))
        self.assertFalse(result['specialized'])
        self.assertEqual(result['candidates'], [])

    def test_invalid_frame_falls_back(self):
        for image in (None, np.zeros((0, 0, 3), np.uint8), np.zeros((800, 1200, 2), np.uint8),
                      np.zeros((800, 1200, 3), np.float32)):
            self.assertEqual(self.router.classify(image)['fallback_reason'], 'invalid_frame')

    def test_invalid_decoded_patch_is_explicit_value_error(self):
        with patch('rouge.page_features.cv2.imdecode', return_value=None):
            with self.assertRaisesRegex(ValueError, 'Invalid static-control patch'):
                PageFeatureRouter()

    def test_corrupt_patch_checksum_falls_back_to_whole_current_frame(self):
        from rouge.dynamic_ocr import DynamicOCR
        from rouge.recognition import ScreenReader
        with tempfile.TemporaryDirectory(prefix='feature-asset-', dir=ROOT/'.cache') as directory:
            directory = Path(directory)
            for asset in (ROOT/'rouge/data/page-features').iterdir():
                if asset.is_file():shutil.copy2(asset, directory/asset.name)
            manifest = json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
            broken = directory/manifest['pages'][0]['anchors'][0]['patch']
            broken.write_bytes(b'present-but-invalid-png')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                PageFeatureRouter(directory=directory)
            calls=[]
            image=np.zeros((1127,2052,3),np.uint8)
            def engine(current):calls.append(current.shape);return [],None
            reader=ScreenReader();reader._engine=engine;reader._frame_ocr=DynamicOCR(engine)
            reader._interpret=lambda *args, **kwargs: {'page':'unknown','operator':None,
                'run':None,'node_content':None,'performance':{'stages_ms':{}}}
            with patch('rouge.page_features.PageFeatureRouter',
                       side_effect=lambda:PageFeatureRouter(directory=directory)):
                result=reader._read(image)
            self.assertEqual(calls,[image.shape])
            self.assertEqual(result['performance']['routing']['fallback_reason'],'visual_unavailable:ValueError')


if __name__ == '__main__':
    unittest.main()
