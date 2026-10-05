"""Gray numeric fallback retains marker, card identity and state boundaries."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from rouge.digit_counters import RULES, read_gray_glyph_number
from rouge.local_counters import locate_glyphs, read_local_counter_badges
from rouge.recognition import prepare_frame
from rouge.relic_counter_semantics import counter_resources
from rouge.run_recognition import read_held_counters
from rouge.run_state import RunState


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / ".cache/research/p1-counter-digits-054"
VIDEO = ROOT / ".cache/research/p1-recipient-training-054/source/BV14aK26bEuP-curl-first.jpg"
OCR = ROOT / ".cache/research/p1-local-integration-054/video_independent-1791122363167430400-observation.json"


class GrayCounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image, _ = prepare_frame(cv2.imdecode(np.fromfile(VIDEO, np.uint8), 1))
        cls.texts = json.loads(OCR.read_text(encoding="utf-8"))["texts"]
        cls.held = next(t for t in cls.texts if t["text"] == "收起")
        cls.glyphs, cls.regions, _ = locate_glyphs(cls.image, cls.texts, cls.held)
        cls.engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)

    def test_candidate_and_explicit_production_epoch_remain_frozen(self):
        frozen = json.loads((RESEARCH / "frozen-v1-before-new-author-holdout.json").read_text(encoding="utf-8"))
        self.assertEqual(RULES, frozen["rules"])
        for path, digest in frozen["hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)
        candidate = ast.parse((RESEARCH / "candidate_digits_v1.py").read_text(encoding="utf-8"))
        # Preserve the historical 0.55 contract against its verified pre-0.60
        # source. Current rounding behavior is covered by the 0.60 regression.
        production = ast.parse((ROOT / ".cache/batch-060-before/rouge/digit_counters.py").read_text(encoding="utf-8"))
        functions = lambda tree: {n.name: ast.dump(n, include_attributes=False) for n in tree.body if isinstance(n, ast.FunctionDef)}
        self.assertEqual(functions(candidate), functions(production))
        epoch = json.loads((RESEARCH / "production-epoch-v4.json").read_text(encoding="utf-8"))
        for path, digest in epoch["hashes"].items():
            source = ROOT / (".cache/batch-060-before/" + path if path == "rouge/digit_counters.py" else path)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)

    def test_real_new_training_gray_digits_are_one_ten_one(self):
        results = [read_gray_glyph_number(self.image, glyph, self.engine) for glyph in self.glyphs]
        self.assertEqual([badge["value"] for badge, detail in results], [1, 10, 1])
        self.assertTrue(all(detail["local_ocr_calls"] == 1 for badge, detail in results))
        self.assertTrue(all(badge["score"] >= .8 and badge["confidence"] >= .95 for badge, detail in results))
        self.assertTrue(all("id" not in badge for badge, detail in results))

    def test_integrated_fallback_keeps_watermarked_name_unbound(self):
        badges, regions, perf, _ = read_local_counter_badges(self.image, self.texts, self.held, self.engine)
        self.assertEqual([b["value"] for b in badges], [1, 10, 1])
        self.assertEqual(perf["local_ocr_calls"], 3)
        bound = read_held_counters(self.image, self.texts, self.held, badges=badges, regions=regions)
        self.assertEqual([(b["id"], b["value"]) for b in bound],
                         [("rogue_6_relic_legacy_103", 1), ("rogue_6_relic_cargo_2", 10)])
        self.assertNotIn("rogue_6_relic_fight_30", [b["id"] for b in bound])
        resources = counter_resources(bound)
        self.assertEqual(resources["altar_stacks"]["value"], 1)
        self.assertNotIn("parts_count", resources)
        self.assertNotIn("probe_stacks", resources)

    def test_confirmed_counter_semantics_save_and_restore_only_temporary_state(self):
        badges, regions, _, _ = read_local_counter_badges(self.image, self.texts, self.held, self.engine)
        bound = read_held_counters(self.image, self.texts, self.held, badges=badges, regions=regions)
        resources = counter_resources(bound)
        with tempfile.TemporaryDirectory(prefix="rouge-gray-counter-055-") as temporary:
            path = Path(temporary)/"run.json"
            state = RunState(path)
            state.apply({"relics": {"ids": [b["id"] for b in bound], "count": None, "icons": [], "source": "held_bar"},
                         "resources": resources}, time.time())
            state.save()
            restored = RunState(path)
            self.assertEqual(restored.state["resources"]["altar_stacks"]["value"], 1)
            self.assertNotIn("probe_stacks", restored.state["resources"])

    def test_strict_marker_recheck_rejects_changed_pixels_before_ocr(self):
        current = self.image.copy()
        glyph = self.glyphs[0]
        x0, y0, x1, y1 = glyph["rect"]
        current[y0:y1, x0:x1] = 0
        def forbidden(*args, **kwargs):
            raise AssertionError("unconfirmed marker must never trigger OCR")
        badge, detail = read_gray_glyph_number(current, glyph, forbidden)
        self.assertIsNone(badge)
        self.assertEqual(detail["reason"], "strict_marker_unconfirmed")
        self.assertEqual(detail["local_ocr_calls"], 0)

    def test_recognizer_is_local_and_number_character_count_must_match_ink(self):
        actual = self.glyphs[1]
        for raw in ([["10", .949]], [["10%", .999]], [["1", .999]],
                    [["100", .999]], [["10", float("nan")]], [], [["10", .999], ["10", .999]]):
            def engine(image, **kwargs):
                self.assertEqual(kwargs, {"use_det": False, "use_cls": False})
                self.assertLess(image.shape[0]*image.shape[1], self.image.shape[0]*self.image.shape[1]*.01)
                return raw, None
            badge, detail = read_gray_glyph_number(self.image, actual, engine)
            self.assertIsNone(badge)
            self.assertEqual(detail["local_ocr_calls"], 1)

    def test_missing_current_held_card_context_yields_no_reused_number(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("missing current context must not trigger OCR")
        badges, _, perf, _ = read_local_counter_badges(self.image, [], self.held, forbidden)
        self.assertEqual(badges, [])
        self.assertEqual(perf["local_ocr_calls"], 0)

    def test_input_ocr_and_marker_records_are_not_mutated(self):
        texts = copy.deepcopy(self.texts)
        glyph = copy.deepcopy(self.glyphs[1])
        before = copy.deepcopy(glyph)
        read_gray_glyph_number(self.image, glyph, self.engine)
        self.assertEqual(glyph, before)
        self.assertEqual(texts, self.texts)

    def test_half_analysis_recovers_ten_but_unconfirmed_third_marker_remains_unknown(self):
        current = cv2.resize(self.image, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA)
        badges, regions, _, _ = read_local_counter_badges(current, self.texts, self.held, self.engine)
        self.assertEqual([b["value"] for b in badges], [1, 10])
        bound = read_held_counters(current, self.texts, self.held, badges=badges, regions=regions)
        self.assertEqual([(b["id"], b["value"]) for b in bound],
                         [("rogue_6_relic_legacy_103", 1), ("rogue_6_relic_cargo_2", 10)])


if __name__ == "__main__":
    unittest.main()
