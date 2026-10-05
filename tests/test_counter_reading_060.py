"""Actual image digits through local recognition, temporary state and calculation.

The frozen full-frame OCR labels are deliberately explicit: these are local
reader tests, not evidence that half-resolution source frames are fully read.
"""
import json
from pathlib import Path
import tempfile
import time
import unittest

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from rouge.damage import calculate_damage
from rouge.local_counters import read_local_counter_badges
from rouge.recognition import prepare_frame
from rouge.relic_counter_semantics import counter_resources
from rouge.run_recognition import read_held_counters
from rouge.run_state import RunState

ROOT = Path(__file__).resolve().parents[1]
ALTAR = 'rogue_6_relic_legacy_103'
RED = 'rogue_6_relic_cargo_2'


class CounterReading060Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / '.cache/research/p1-recipient-training-054/source/BV14aK26bEuP-curl-first.jpg'
        cls.image, _ = prepare_frame(cv2.imdecode(np.fromfile(path, np.uint8), 1))
        row = ROOT / '.cache/research/p1-local-integration-054/video_independent-1791122363167430400-observation.json'
        cls.texts = json.loads(row.read_text(encoding='utf-8'))['texts']
        cls.held = next(t for t in cls.texts if t['text'] == '收起')
        cls.engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)

    def read(self, scale):
        image = cv2.resize(self.image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        badges, regions, perf, _ = read_local_counter_badges(image, self.texts, self.held, self.engine)
        bound = read_held_counters(image, self.texts, self.held, badges=badges, regions=regions)
        return badges, bound, perf

    def test_continuous_scales_keep_card_identity_and_strict_thresholds(self):
        for scale in (.5, .65, .8, 1, 1.25):
            with self.subTest(scale=scale):
                badges, bound, perf = self.read(scale)
                self.assertEqual([b['value'] for b in badges], [1, 10] if scale == .5 else [1, 10, 1])
                self.assertEqual([(b['id'], b['value']) for b in bound], [(ALTAR, 1), (RED, 10)])
                self.assertTrue(all(b['score'] >= .8 and b['confidence'] >= .95 for b in badges))
                self.assertEqual(perf['local_ocr_calls'], len(badges))

    def test_half_analysis_count_persists_and_enters_calculation_without_guessing_parts(self):
        _, bound, _ = self.read(.5)
        resources = counter_resources(bound)
        self.assertEqual(set(resources), {'altar_stacks'})
        with tempfile.TemporaryDirectory(prefix='rouge-counter-060-') as directory:
            path = Path(directory) / 'run.json'
            state = RunState(path)
            state.apply({'relics': {'ids': [ALTAR, RED], 'count': None, 'icons': [], 'source': 'held_bar'},
                         'resources': resources}, time.time())
            state.save()
            restored = RunState(path)
            # This is the same confirmed-resource projection used by the UI.
            context = {key: record['value'] for key, record in restored.state['resources'].items()}
            result = calculate_damage({'operator': 'mechanist', 'skill': 3,
                                       'relic_ids': restored.held_relic_ids(), 'relic_context': context})
            stats = result['estimate']['base_stats']
            self.assertEqual(stats['attack'], 602)
            self.assertEqual(stats['defense'], 803)
            records = {record['id']: record for record in result['relic_resolution']['records']}
            self.assertEqual(records[ALTAR]['missing_conditions'], [])
            self.assertEqual(records[RED]['missing_conditions'], ['parts_count'])

    def test_original_failed_diagnostic_remains_available_as_historical_evidence(self):
        path = ROOT / '.cache/research/counter-reading-060/diagnosis-1791195600883958000.json'
        original = json.loads(path.read_text(encoding='utf-8'))
        half = next(row for row in original['rows'] if row['scale'] == .5)
        self.assertEqual(half['values'], [1])


if __name__ == '__main__':
    unittest.main()
