"""Production local-counter reading against frozen original public evidence."""
import ast
import copy
from contextlib import ExitStack
import hashlib
import itertools
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from rouge.counter_badges import _reference, _white as frozen_white
from rouge.local_counters import GEOMETRY, _white, read_local_counter_badges
from rouge.run_recognition import read_held_counters, read_run


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / ".cache/research/p1-counter-local-054"


def load(path):
    return cv2.imdecode(np.fromfile(ROOT / path, np.uint8), 1)


def anchor(texts):
    return next((t for t in texts if t["text"] == "收起" and t["confidence"] >= .9), None)


def probe(image, texts, engine, *, context=None):
    """Real branch/counter readers; unrelated expensive readers are isolated."""
    with ExitStack() as stack:
        for name, value in (("near_number", None), ("read_config", {}),
                            ("match_held_icons", []), ("resolve_difficulty_icons", []),
                            ("read_roster", []), ("read_selected_member", None)):
            stack.enter_context(patch("rouge.run_recognition."+name, return_value=value))
        stack.enter_context(patch("rouge.run_recognition.resolve_owned_icons", side_effect=lambda icons, cards: icons))
        return read_run(image, texts, engine, run_context=context)


class LocalCounterProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / ".cache/research/p1-held-cards-054/fixtures.json").read_text(encoding="utf-8"))
        cls.train_source = ".cache/research/p1-counter-images-054/source/taptap-hydra-100.jpg"
        cls.train = load(cls.train_source)
        cls.train_texts = cls.fixture["training_multirow"]["texts"]
        cls.missing_texts = [t for t in cls.train_texts if t["text"] != "15"]
        cls.independent = json.loads((ROOT / ".cache/research/p1-counter-training-054/independent-positive-ocr.json").read_text(encoding="utf-8"))
        cls.holdout = load(cls.independent["source"])
        cls.holdout_texts = cls.independent["texts"]
        cls.engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)

    def test_original_functions_geometry_and_explicit_gray_epoch_are_frozen(self):
        frozen = ast.parse((RESEARCH / "candidate_v3.py").read_text(encoding="utf-8"))
        actual = ast.parse((ROOT / "rouge/local_counters.py").read_text(encoding="utf-8"))
        wanted = {node.name: ast.dump(node, include_attributes=False) for node in frozen.body
                  if isinstance(node, ast.FunctionDef) and node.name != "bind_complete_cards"}
        observed = {node.name: ast.dump(node, include_attributes=False) for node in actual.body
                    if isinstance(node, ast.FunctionDef)}
        # V3 remains sealed. V4 adds only the documented fallback call when
        # old digit ink is absent; all location/mask/geometry functions match.
        for name in wanted.keys()-{"read_local_counter_badges"}:
            self.assertEqual(observed[name], wanted[name])
        v4 = ast.parse((ROOT / ".cache/research/p1-counter-digits-054/production-local-v4.py").read_text(encoding="utf-8"))
        sealed_v4 = {node.name: ast.dump(node, include_attributes=False) for node in v4.body
                     if isinstance(node, ast.FunctionDef)}
        self.assertEqual(observed, sealed_v4)
        freeze = json.loads((RESEARCH / "frozen-v3-before-local-holdout.json").read_text(encoding="utf-8"))
        self.assertEqual(GEOMETRY, freeze["candidate_geometry"])
        for filename, digest in freeze["hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest(), digest)

    def test_train_fifteen_is_automatically_discovered_without_numeric_ocr_line(self):
        badges, regions, performance, _ = read_local_counter_badges(self.train, self.missing_texts, anchor(self.missing_texts), self.engine)
        self.assertEqual([b["value"] for b in badges], [15])
        self.assertEqual(performance["local_ocr_calls"], 1)
        bound = read_held_counters(self.train, self.missing_texts, anchor(self.missing_texts), badges=badges, regions=regions)
        self.assertEqual([(b["id"], b["value"]) for b in bound], [("rogue_6_relic_cargo_2", 15)])

    def test_known_train_integer_does_not_call_local_ocr(self):
        def unexpected(*args, **kwargs):
            raise AssertionError("existing verified numeric candidate must not trigger local OCR")
        badges, _, performance, _ = read_local_counter_badges(self.train, self.train_texts, anchor(self.train_texts), unexpected)
        self.assertEqual([b["value"] for b in badges], [15])
        self.assertEqual(performance["local_ocr_calls"], 0)

    def test_independent_one_is_read_but_clipped_name_is_not_bound(self):
        badges, regions, performance, _ = read_local_counter_badges(self.holdout, self.holdout_texts, anchor(self.holdout_texts), self.engine)
        self.assertEqual([b["value"] for b in badges], [1])
        self.assertEqual(performance["local_ocr_calls"], 1)
        self.assertTrue(all("id" not in badge for badge in badges))
        self.assertEqual(read_held_counters(self.holdout, self.holdout_texts, anchor(self.holdout_texts), badges=badges, regions=regions), [])

    def test_run_output_distinguishes_unbound_one_from_owned_counters(self):
        observed = probe(self.holdout, self.holdout_texts, self.engine)
        self.assertEqual(observed["page"], "run_map")
        self.assertEqual(observed["relics"]["counters"], [])
        self.assertEqual([c["value"] for c in observed["relics"]["unbound_counters"]], [1])
        self.assertTrue(all(c["identity_confirmed"] is False and "id" not in c
                            for c in observed["relics"]["unbound_counters"]))
        self.assertEqual(observed["counter_performance"]["local_ocr_calls"], 1)

    def test_run_output_binds_fifteen_and_preserves_resource_crosscheck(self):
        observed = probe(self.train, self.missing_texts, self.engine)
        self.assertEqual([(c["id"], c["value"]) for c in observed["relics"]["counters"]], [("rogue_6_relic_cargo_2", 15)])
        self.assertEqual(observed["relics"]["unbound_counters"], [])
        self.assertEqual(observed["resources"]["parts_count"]["counter_crosscheck"]["value"], 15)

    def test_ten_original_negative_images_have_no_values_or_extra_ocr(self):
        negatives = [("run-relic-open", "run-relic-open-ocr.json"), ("run-map-closed", "run-map-closed-ocr.json"),
                     ("run-relic-multicard", None), ("run-roster", "run-roster-ocr.json"),
                     ("run-mechanist-selected", "run-mechanist-selected-ocr.json"),
                     ("run-emergency-mechanist", "run-emergency-mechanist-ocr.json"),
                     ("operator-kaltsit", "operator-kaltsit-ocr.json"),
                     ("operator-silverash", "operator-silverash-ocr.json"),
                     ("operator-mechanist", "operator-mechanist-ocr.json"),
                     ("module-mechanist", "module-mechanist-ocr.json")]
        for name, ocr in negatives:
            with self.subTest(original=name):
                texts = (self.fixture["holdout_three_cards"]["texts"] if ocr is None else
                         json.loads((ROOT / "samples/native-client" / ocr).read_text(encoding="utf-8"))["texts"])
                badges, _, performance, _ = read_local_counter_badges(load("samples/native-client/"+name+".png"), texts, anchor(texts), self.engine)
                self.assertEqual(badges, [])
                self.assertEqual(performance["local_ocr_calls"], 0)

    def test_derived_scales_and_translation_preserve_values_and_identity_gate(self):
        for name, original, texts, expected, ids in (("train", self.train, self.missing_texts, [15], ["rogue_6_relic_cargo_2"]),
                                                    ("independent", self.holdout, self.holdout_texts, [1], [])):
            for scale in (.5, .75, 1.25):
                with self.subTest(derived_from=name, scale=scale):
                    current = cv2.resize(original, None, fx=scale, fy=scale,
                                         interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
                    badges, regions, _, _ = read_local_counter_badges(current, texts, anchor(texts), self.engine)
                    self.assertEqual([b["value"] for b in badges], expected)
                    bound = read_held_counters(current, texts, anchor(texts), badges=badges, regions=regions)
                    self.assertEqual([b["id"] for b in bound], ids)
            h, w = original.shape[:2]
            canvas = np.zeros((h+181, w+259, 3), np.uint8)
            canvas[91:91+h, 107:107+w] = original
            moved = copy.deepcopy(texts)
            for t in moved:
                t["box"] = [[(x*w+107)/canvas.shape[1], (y*h+91)/canvas.shape[0]] for x, y in t["box"]]
            badges, regions, _, _ = read_local_counter_badges(canvas, moved, anchor(moved), self.engine)
            self.assertEqual([b["value"] for b in badges], expected)
            self.assertEqual([b["id"] for b in read_held_counters(canvas, moved, anchor(moved), badges=badges, regions=regions)], ids)

    def test_rejected_footer_never_invokes_local_counter_reader(self):
        for missing in ("零件箱", "干员", "编队"):
            with self.subTest(missing=missing):
                texts = [t for t in self.missing_texts if t["text"] != missing]
                with patch("rouge.run_recognition.read_local_counter_badges", side_effect=AssertionError("gate failed")):
                    self.assertIsNone(probe(self.train, texts, self.engine))
        texts = copy.deepcopy(self.missing_texts)
        control = next(t for t in texts if t["text"] == "零件箱")
        for point in control["box"]:
            point[1] -= .2
        with patch("rouge.run_recognition.read_local_counter_badges", side_effect=AssertionError("gate failed")):
            self.assertIsNone(probe(self.train, texts, self.engine))

    def test_roster_scope_does_not_invoke_local_counter_reader(self):
        texts = json.loads((ROOT / "samples/native-client/run-roster-ocr.json").read_text(encoding="utf-8"))["texts"]
        with patch("rouge.run_recognition.read_local_counter_badges", side_effect=AssertionError("roster must not scan local counters")):
            observed = probe(load("samples/native-client/run-roster.png"), texts, self.engine)
        self.assertEqual(observed["page"], "run_roster")
        self.assertEqual(observed["relics"]["counters"], [])
        self.assertEqual(observed["relics"]["unbound_counters"], [])

    def test_previous_context_does_not_supply_a_current_counter(self):
        context = {"run_id": "temporary-offline-test", "config": {},
                   "relics": {"counters": [{"id": "rogue_6_relic_cargo_2", "value": 99}]}}
        first = probe(self.train, self.missing_texts, self.engine, context=context)
        self.assertEqual([c["value"] for c in first["relics"]["counters"]], [15])
        texts = self.fixture["holdout_three_cards"]["texts"]
        next_frame = probe(load("samples/native-client/run-relic-multicard.png"), texts, self.engine, context=context)
        self.assertEqual(next_frame["relics"]["counters"], [])
        self.assertEqual(next_frame["relics"]["unbound_counters"], [])

    def test_multiple_badges_for_one_complete_id_are_not_bound(self):
        badges, regions, _, _ = read_local_counter_badges(self.train, self.missing_texts, anchor(self.missing_texts), self.engine)
        conflicting = copy.deepcopy(badges[0])
        conflicting["value"] = 16
        self.assertEqual(read_held_counters(self.train, self.missing_texts, anchor(self.missing_texts), badges=[badges[0], conflicting], regions=regions), [])

    def test_bad_local_ocr_remains_unknown(self):
        for raw in ([['15', .94]], [['15%', .99]], [['999', .99]]):
            with self.subTest(raw=raw):
                fake = lambda *args, result=raw, **kwargs: (result, None)
                badges, _, _, _ = read_local_counter_badges(self.train, self.missing_texts, anchor(self.missing_texts), fake)
                self.assertEqual(badges, [])

    def test_only_local_recognition_and_no_template_sweep_are_used(self):
        calls = []
        def checked(image, **kwargs):
            self.assertFalse(kwargs["use_det"])
            self.assertFalse(kwargs["use_cls"])
            self.assertLess(image.shape[0]*image.shape[1], self.holdout.shape[0]*self.holdout.shape[1]*.01)
            calls.append(image.shape)
            return self.engine(image, **kwargs)
        with patch("rouge.local_counters.cv2.matchTemplate", side_effect=AssertionError("No template sweep")):
            badges, _, _, _ = read_local_counter_badges(self.holdout, self.holdout_texts, anchor(self.holdout_texts), checked)
        self.assertEqual([b["value"] for b in badges], [1])
        self.assertEqual(len(calls), 1)

    def test_fast_white_mask_preserves_frozen_edges_and_fallbacks(self):
        settings, _ = _reference()
        edges = np.array(list(itertools.product((0, 189, 190, 191, 234, 235, 255), repeat=3)), dtype=np.uint8).reshape(1, -1, 3)
        self.assertTrue(np.array_equal(_white(edges, settings), frozen_white(edges, settings)))
        for image in (edges[:, :, 0], edges.astype(np.float32)):
            self.assertTrue(np.array_equal(_white(image, settings), frozen_white(image, settings)))


if __name__ == "__main__":
    unittest.main()
