"""Real current popup reconfirmation without changing names or icon gates."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

from rouge.recipient_recognition import read_recipient_buffs
from rouge.run_state import RunState


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / ".cache/research/p1-live-recipient-055"
EPOCH = "1791126165174762500"


class LiveRecipientReconfirmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image_path = RESEARCH / ("current-game-"+EPOCH+".png")
        cls.image = cv2.imdecode(np.fromfile(cls.image_path, np.uint8), 1)
        cls.observation = json.loads((RESEARCH / ("observation-"+EPOCH+".json")).read_text(encoding="utf-8"))
        cls.texts = cls.observation["texts"]
        cls.member = next(member for member in cls.observation["run"]["operators"] if member["id"] == "kaltsit")
        cls.engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)
        cls.baseline = read_recipient_buffs(cls.image, cls.texts, cls.member, engine=cls.engine)

    def read(self, *, image=None, texts=None, member=None, engine=None):
        return read_recipient_buffs(self.image if image is None else image,
                                   self.texts if texts is None else texts,
                                   self.member if member is None else member,
                                   engine=self.engine if engine is None else engine)

    @staticmethod
    def forbidden(*args, **kwargs):
        raise AssertionError("unattributed popup must never trigger local OCR")

    def test_real_failed_ocr_is_preserved_and_opt_in_reconfirm_matches_exact_buff(self):
        failed = read_recipient_buffs(self.image, self.texts, self.member)
        self.assertEqual(failed["ids"], [])
        self.assertFalse(failed["complete"])
        self.assertTrue(any("）1，并使其" in text["text"] for text in self.texts))
        result = self.baseline
        self.assertEqual(result["operator_id"], "kaltsit")
        self.assertEqual(result["ids"], ["rogue_6_from_relic_6"])
        self.assertEqual(result["count"], 1)
        self.assertTrue(result["complete"])
        self.assertEqual(result["issues"], [])
        self.assertGreaterEqual(result["entries"][0]["icon"]["score"], .94)
        self.assertEqual(result["entries"][0]["description_verification"]["local_ocr_calls"], 2)

    def test_original_ocr_and_shared_output_geometry_are_not_mutated(self):
        texts = deepcopy(self.texts)
        before = deepcopy(texts)
        result = self.read(texts=texts)
        self.assertEqual(texts, before)
        result["entries"][0]["description_evidence"][0]["box"][0][0] = .1
        self.assertEqual(texts, before)

    def test_wrong_owner_account_scope_and_missing_roster_or_header_do_no_local_ocr(self):
        for member in ({**self.member, "scope": "account"}, {**self.member, "name": "凛御银灰"},
                       {"id": "silverash", "name": "凛御银灰", "scope": "run"}):
            with self.subTest(member=member):
                self.assertIsNone(self.read(member=member, engine=self.forbidden))
        for label in ("技能", "分支+", "收起", "收藏品增益"):
            texts = [text for text in self.texts if text["text"] != label]
            self.assertIsNone(self.read(texts=texts, engine=self.forbidden))
        texts = [text for text in self.texts if "此干员已拥有以下" not in text["text"]]
        self.assertIsNone(self.read(texts=texts, engine=self.forbidden))

    def test_low_or_wrong_full_name_cannot_be_rescued_by_description(self):
        for change in ({"confidence": .89}, {"text": "医者-新典"}):
            texts = deepcopy(self.texts)
            next(text for text in texts if text["text"] == "医者-新典训").update(change)
            result = self.read(texts=texts, engine=self.forbidden)
            self.assertEqual(result["ids"], [])
            self.assertFalse(result["complete"])

    def test_no_direct_number_deletion_or_confidence_relaxation(self):
        for raw in ([["）1，并使其：治疗时使目标获得2技力", .999]],
                    [["），并使其：治疗时使目标获得3技力", .999]],
                    [["），并使其：治疗时使目标获得2技力", .899]], []):
            calls = []
            def engine(crop, **kwargs):
                self.assertEqual(kwargs, {"use_det": False, "use_cls": False})
                self.assertLess(crop.shape[0]*crop.shape[1], self.image.shape[0]*self.image.shape[1]*.1)
                calls.append(1)
                if len(calls) == 1:
                    return [["立即进阶一个【医疗】干员（不消耗希望", .99]], None
                return raw, None
            result = self.read(engine=engine)
            self.assertEqual(result["ids"], [])
            self.assertFalse(result["complete"])

    def test_covering_real_icon_still_rejects_reconfirmed_name_and_description(self):
        image = self.image.copy()
        points = self.baseline["entries"][0]["icon"]["box"]
        h, w = image.shape[:2]
        x0, x1 = round(min(p[0] for p in points)*w), round(max(p[0] for p in points)*w)
        y0, y1 = round(min(p[1] for p in points)*h), round(max(p[1] for p in points)*h)
        image[y0:y1, x0:x1] = 0
        result = self.read(image=image)
        self.assertEqual(result["ids"], [])
        self.assertFalse(result["complete"])
        self.assertIn("icon_unconfirmed", result["issues"])

    def test_header_count_mismatch_retains_partial_identity_without_claiming_full_list(self):
        texts = deepcopy(self.texts)
        header = next(text for text in texts if "此干员已拥有以下" in text["text"])
        header["text"] = header["text"].replace("以下1个", "以下2个")
        result = self.read(texts=texts)
        self.assertEqual(result["ids"], ["rogue_6_from_relic_6"])
        self.assertEqual(result["count"], 2)
        self.assertFalse(result["complete"])

    def test_dynamic_translation_and_scale_do_not_use_actual_screen_coordinates(self):
        old_h, old_w = self.image.shape[:2]
        for scale in (.75, 1.25):
            with self.subTest(scale=scale):
                resized = cv2.resize(self.image, None, fx=scale, fy=scale,
                                     interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
                image = cv2.copyMakeBorder(resized, 37, 19, 53, 21, cv2.BORDER_CONSTANT, value=(180, 180, 180))
                h, w = image.shape[:2]
                texts = deepcopy(self.texts)
                for text in texts:
                    text["box"] = [[(x*old_w*scale+53)/w, (y*old_h*scale+37)/h] for x, y in text["box"]]
                result = self.read(image=image, texts=texts)
                self.assertEqual(result["ids"], ["rogue_6_from_relic_6"])
                self.assertTrue(result["complete"])

    def test_confirmed_actual_buff_only_saves_to_temporary_run_state(self):
        result = self.baseline
        member = {**self.member, "char_buff_ids": result["ids"], "char_buffs_complete": result["complete"],
                  "recipient_buffs": result}
        with tempfile.TemporaryDirectory(prefix="rouge-live-recipient-unit-055-") as temporary:
            path = Path(temporary)/"run.json"
            state = RunState(path)
            state.apply({"operators": [member]}, time.time())
            state.save()
            restored = RunState(path).state["operators"]["kaltsit"]
            self.assertEqual(restored["char_buff_ids"], ["rogue_6_from_relic_6"])
            self.assertTrue(restored["char_buffs_complete"])


if __name__ == "__main__":
    unittest.main()
