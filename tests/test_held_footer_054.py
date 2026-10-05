"""Exact dynamic footer reconfirm on a real independent held-page image."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from rouge.held_cards import read_held_cards
from rouge.held_footer import (MINIMUM_CONFIDENCE, reconfirm_held_footer)
from rouge.recognition import prepare_frame
from rouge.resource_recognition import read_resources
from rouge.run_recognition import expanded_held_page


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".cache/research/p1-recipient-training-054/source/BV14aK26bEuP-curl-first.jpg"
OBSERVATION = ROOT / ".cache/research/p1-local-integration-054/video_independent-1791122363167430400-observation.json"


class HeldFooterReconfirmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = cv2.imdecode(np.fromfile(SOURCE, np.uint8), 1)
        cls.image, _ = prepare_frame(cls.source)
        cls.texts = json.loads(OBSERVATION.read_text(encoding="utf-8"))["texts"]
        cls.held = next(t for t in cls.texts if t["text"] == "收起")
        cls.cards = read_held_cards(cls.texts, cls.held)
        cls.engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)

    def call(self, *, texts=None, held=None, cards=None, image=None, engine=None):
        return reconfirm_held_footer(self.image if image is None else image,
                                     self.texts if texts is None else texts,
                                     self.held if held is None else held,
                                     self.cards if cards is None else cards,
                                     self.engine if engine is None else engine)

    @staticmethod
    def must_not_ocr(*args, **kwargs):
        raise AssertionError("unverified context must never trigger OCR")

    @staticmethod
    def confirmed_engine(image, **kwargs):
        if kwargs != {"use_det": False, "use_cls": False}:
            raise AssertionError("only recognizer-only local call is allowed")
        return [["零件箱", .96]], None

    def test_independent_original_exact_label_is_reconfirmed_at_unchanged_threshold(self):
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                         "e5908633b7708102db4a1d26193e1a524a1d90bbfd8cf476f6e409cbee90c465")
        self.assertEqual(MINIMUM_CONFIDENCE, .9)
        original = next(t for t in self.texts if t["text"] == "零件箱")
        self.assertLess(original["confidence"], .9)
        record, detail = self.call()
        self.assertEqual(record["text"], "零件箱")
        self.assertGreaterEqual(record["confidence"], .9)
        self.assertEqual(record["box"], original["box"])
        self.assertEqual(detail["local_ocr_calls"], 1)
        self.assertTrue(detail["confirmed"])
        self.assertEqual(detail["crop_rect"], [1123, 1037, 1202, 1078])
        self.assertLess((1202-1123)*(1078-1037), self.image.shape[0]*self.image.shape[1]*.01)

    def test_resource_reader_accepts_reconfirmed_same_frame_label(self):
        record, _ = self.call()
        texts = [record if t["text"] == "零件箱" else t for t in self.texts]
        anchors = {t["text"]: t for t in texts if t["confidence"] >= .9}
        self.assertTrue(expanded_held_page(anchors, self.held, self.cards))
        parts = read_resources(self.image, texts)["parts_count"]
        self.assertEqual(parts["value"], 10)
        self.assertEqual(parts["capacity"], 10)

    def test_no_changes_to_original_evidence_or_shared_geometry(self):
        before = copy.deepcopy(self.texts)
        record, _ = self.call(engine=self.confirmed_engine)
        self.assertEqual(self.texts, before)
        original = next(t for t in self.texts if t["text"] == "零件箱")
        record["box"][0][0] = .1
        self.assertEqual(original, next(t for t in before if t["text"] == "零件箱"))

    def test_native_pixels_also_reconfirm_without_any_manual_region(self):
        record, detail = self.call(image=self.source)
        self.assertEqual(record["text"], "零件箱")
        self.assertEqual(detail["local_ocr_calls"], 1)
        self.assertGreaterEqual(record["confidence"], .9)

    def test_current_geometry_tracks_translation_and_scale(self):
        for scale in (.5, .75, 1.25):
            with self.subTest(scale=scale):
                image = cv2.resize(self.source, None, fx=scale, fy=scale)
                record, detail = self.call(image=image, engine=self.confirmed_engine)
                self.assertTrue(record)
                old = next(t for t in self.texts if t["text"] == "零件箱")
                x0, y0, x1, y1 = detail["crop_rect"]
                self.assertLess(x0/image.shape[1], old["box"][0][0])
                self.assertGreater(x1/image.shape[1], old["box"][1][0])
        h, w = self.source.shape[:2]
        dx, dy = 129, 71
        canvas = np.zeros((h+180, w+290, 3), np.uint8)
        canvas[dy:dy+h, dx:dx+w] = self.source
        texts = copy.deepcopy(self.texts)
        for text in texts:
            for point in text["box"]:
                point[0] = (point[0]*w+dx)/canvas.shape[1]
                point[1] = (point[1]*h+dy)/canvas.shape[0]
        held = next(t for t in texts if t["text"] == "收起")
        record, detail = self.call(image=canvas, texts=texts, held=held,
                                   cards=read_held_cards(texts, held), engine=self.confirmed_engine)
        self.assertTrue(record)
        self.assertGreater(detail["crop_rect"][0], dx)

    def test_missing_card_or_offer_identity_never_enters_reconfirm(self):
        for cards in ([], [{"confirmed": False}],
                      [{"confirmed": True, "source": "reward_preview", "id": "test", "candidates": ["test"]}]):
            with self.subTest(cards=cards):
                record, detail = self.call(cards=cards, engine=self.must_not_ocr)
                self.assertIsNone(record)
                self.assertEqual(detail["local_ocr_calls"], 0)

    def test_wrong_held_control_or_low_confidence_never_enters_reconfirm(self):
        for held in ({**self.held, "text": "收藏品"}, {**self.held, "confidence": .89}):
            record, detail = self.call(held=held, engine=self.must_not_ocr)
            self.assertIsNone(record)
            self.assertEqual(detail["local_ocr_calls"], 0)

    def test_missing_or_nonexact_candidate_never_scans_footer(self):
        for replacement in (None, "零件", "零件箱详情", "零件箱 "):
            texts = copy.deepcopy(self.texts)
            if replacement is None:
                texts = [t for t in texts if t["text"] != "零件箱"]
            else:
                next(t for t in texts if t["text"] == "零件箱")["text"] = replacement
            record, detail = self.call(texts=texts, engine=self.must_not_ocr)
            self.assertIsNone(record)
            self.assertEqual(detail["local_ocr_calls"], 0)

    def test_duplicate_candidate_or_controls_never_enters_reconfirm(self):
        for name in ("零件箱", "干员", "编队"):
            texts = copy.deepcopy(self.texts)
            texts.append(copy.deepcopy(next(t for t in texts if t["text"] == name)))
            record, detail = self.call(texts=texts, engine=self.must_not_ocr)
            self.assertIsNone(record)
            self.assertEqual(detail["local_ocr_calls"], 0)

    def test_weak_or_missing_strong_control_never_enters_reconfirm(self):
        for name in ("干员", "编队"):
            texts = copy.deepcopy(self.texts)
            next(t for t in texts if t["text"] == name)["confidence"] = .899
            record, detail = self.call(texts=texts, engine=self.must_not_ocr)
            self.assertIsNone(record)
            self.assertEqual(detail["local_ocr_calls"], 0)

    def test_valid_strong_label_needs_no_extra_call(self):
        texts = copy.deepcopy(self.texts)
        next(t for t in texts if t["text"] == "零件箱")["confidence"] = .9
        record, detail = self.call(texts=texts, engine=self.must_not_ocr)
        self.assertIsNone(record)
        self.assertEqual(detail["local_ocr_calls"], 0)

    def test_observed_order_font_height_and_alignment_are_mandatory(self):
        for mode in ("wrong_order", "wrong_height", "wrong_y", "invalid_box"):
            texts = copy.deepcopy(self.texts)
            label = next(t for t in texts if t["text"] == "零件箱")
            for point in label["box"]:
                if mode == "wrong_order":
                    point[0] -= .55
                elif mode == "wrong_height":
                    point[1] = .8 if point[1] < .94 else .98
                elif mode == "wrong_y":
                    point[1] -= .35
                else:
                    point[0] = float("nan")
            record, detail = self.call(texts=texts, engine=self.must_not_ocr)
            self.assertIsNone(record)
            self.assertEqual(detail["local_ocr_calls"], 0)

    def test_local_text_and_confidence_must_independently_pass(self):
        for raw in ([["零件箱", .899]], [["零件", .999]], [["零件箱详情", .999]],
                    [["零件箱", float("nan")]], [["零件箱", .99], ["零件箱", .99]], []):
            record, detail = self.call(engine=lambda image, **kwargs: (raw, None))
            self.assertIsNone(record)
            self.assertEqual(detail["local_ocr_calls"], 1)
            self.assertFalse(detail["confirmed"])


if __name__ == "__main__":
    unittest.main()
