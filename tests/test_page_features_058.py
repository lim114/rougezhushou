"""Roster controls locate an OCR domain; they never supply current run facts."""
import json
from pathlib import Path
import re
import unittest

import cv2
import numpy as np

from rouge.page_features import PageFeatureRouter

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / 'samples/native-client'
ROSTERS = ('run-roster', 'run-mechanist-selected', 'run-emergency-mechanist')
OLD_POSITIVES = {'operator-kaltsit', 'operator-kaltsit-animated', 'operator-mechanist',
                 'operator-silverash', 'module-mechanist'}


def load(name):
    return cv2.imdecode(np.fromfile(SAMPLES / (name + '.png'), dtype=np.uint8), cv2.IMREAD_COLOR)


class RosterPageFeatureTests(unittest.TestCase):
    def setUp(self):
        self.router = PageFeatureRouter()

    def route(self, image):
        result = self.router.classify(image)
        self.assertTrue(result['specialized'], result)
        self.assertEqual([c['page'] for c in result['candidates']], ['run_roster'])
        candidate = result['candidates'][0]
        self.assertEqual(candidate['matched_controls'], 4)
        self.assertEqual({e['control'] for e in candidate['evidence']},
                         {'skills', 'branch', 'human_resource', 'squad'})
        self.assertEqual({e['side'] for e in candidate['evidence']}, {'left', 'right'})
        self.assertFalse(candidate['facts_from_features'])
        self.assertFalse(result['facts_from_features'])
        self.assertTrue(all(e['visual_correlation'] >= .85 for e in candidate['evidence']))
        for key in ('operators', 'selected_operator', 'level', 'skill_ranks', 'relics', 'fields'):
            self.assertNotIn(key, candidate)
        h, w = image.shape[:2]
        self.assertTrue(all(0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h
                            for x0, y0, x1, y1 in candidate['regions']))
        return candidate

    def test_originals_and_untrained_emergency_capture(self):
        sources = {Path(p['source']).stem for p in self.router.pages if p.get('template_family') == 'roster-058'}
        self.assertEqual(sources, {'run-roster', 'run-mechanist-selected'})
        self.assertNotIn('run-emergency-mechanist', sources)
        for name in ROSTERS:
            with self.subTest(name=name):
                self.route(load(name))

    def test_dynamic_scale_regions(self):
        for name in ROSTERS:
            for factor in (.65, .8, 1.25):
                with self.subTest(name=name, factor=factor):
                    self.route(cv2.resize(load(name), None, fx=factor, fy=factor))

    def test_current_translation_and_aspect_padding(self):
        for name in ROSTERS:
            original = load(name)
            h, w = original.shape[:2]
            canvas = np.zeros((h + 83, w + 123, 3), np.uint8)
            canvas[31:31+h, 47:47+w] = original
            candidate = self.route(canvas)
            affine = np.asarray(candidate['transform'])
            self.assertAlmostEqual(float(affine[0, 2]), 47, delta=3)
            self.assertAlmostEqual(float(affine[1, 2]), 31, delta=3)
            for original_box, transformed_box in zip(self.route(original)['regions'], candidate['regions']):
                # Runtime clipping/padding may shift an edge by a few pixels.
                self.assertAlmostEqual(transformed_box[1] - original_box[1], 31, delta=3)

    def test_all_current_original_ocr_fields_inside_domain(self):
        for name in ROSTERS:
            image = load(name)
            regions = self.route(image)['regions']
            h, w = image.shape[:2]
            texts = json.loads((SAMPLES / (name + '-ocr.json')).read_text(encoding='utf-8'))['texts']
            for item in texts:
                if item['text'] == '明日方舟':
                    continue
                x0, y0 = min(p[0] for p in item['box'])*w, min(p[1] for p in item['box'])*h
                x1, y1 = max(p[0] for p in item['box'])*w, max(p[1] for p in item['box'])*h
                self.assertTrue(any(a-2 <= x0 and b-2 <= y0 and c+2 >= x1 and d+2 >= y1
                                    for a, b, c, d in regions), (name, item['text'], regions))

    def test_other_pages_still_reject_roster(self):
        for path in sorted(SAMPLES.glob('*.png')):
            if path.stem in ROSTERS:
                continue
            with self.subTest(name=path.stem):
                result = self.router.classify(load(path.stem))
                self.assertNotIn('run_roster', [c['page'] for c in result['candidates']])
                if path.stem not in OLD_POSITIVES:
                    self.assertFalse(result['specialized'], result)

    def test_each_control_missing_requires_discovery(self):
        for page in self.router.pages:
            if page.get('template_family') != 'roster-058':
                continue
            image = cv2.imdecode(np.fromfile(ROOT / page['source'], dtype=np.uint8), cv2.IMREAD_COLOR)
            h, w = image.shape[:2]
            rw, rh = page['reference_size']
            for anchor in page['anchors']:
                with self.subTest(source=page['source'], control=anchor['key']):
                    altered = image.copy()
                    x0, y0, x1, y1 = anchor['box']
                    cv2.rectangle(altered, (round(x0*w/rw)-8, round(y0*h/rh)-8),
                                  (round(x1*w/rw)+8, round(y1*h/rh)+8), (0, 0, 0), -1)
                    self.assertFalse(self.router.classify(altered)['specialized'])

    def test_dimmed_clipped_low_resolution_discovery(self):
        original = load('run-roster')
        h, w = original.shape[:2]
        for image in (np.round(original*.5).astype(np.uint8), original[:round(h*.88)],
                      original[:, round(w*.15):], cv2.resize(original, None, fx=.35, fy=.35)):
            with self.subTest(shape=image.shape):
                self.assertFalse(self.router.classify(image)['specialized'])

    def test_values_and_names_never_become_visual_facts(self):
        image = load('run-emergency-mechanist')
        labels = json.loads((SAMPLES / 'run-emergency-mechanist-ocr.json').read_text(encoding='utf-8'))['texts']
        h, w = image.shape[:2]
        for item in labels:
            if not (re.search(r'\d', item['text']) or item['text'] in ('机械师', '望', '桃金娘', '梅')):
                continue
            x0, y0 = round(min(p[0] for p in item['box'])*w), round(min(p[1] for p in item['box'])*h)
            x1, y1 = round(max(p[0] for p in item['box'])*w), round(max(p[1] for p in item['box'])*h)
            cv2.rectangle(image, (x0, y0), (x1, y1), (160, 160, 160), -1)
        self.route(image)


if __name__ == '__main__':
    unittest.main()
