"""Original-image held-card regression and explicitly derived negative cases."""
import copy
import json
from pathlib import Path
import random
import unittest
from unittest.mock import patch

from rouge.catalog import tactical_tools
from rouge.held_cards import held_card_regions, read_held_cards


FIXTURE = (Path(__file__).resolve().parents[1] /
           ".cache/research/p1-held-cards-054/fixtures.json")
TRAIN_IDS = {
    "rogue_6_relic_fight_15", "rogue_6_relic_assign_7",
    "rogue_6_relic_legacy_116", "rogue_6_relic_fight_18",
    "rogue_6_relic_fight_13", "rogue_6_relic_legacy_110",
    "rogue_6_relic_final_3", "rogue_6_relic_legacy_113",
    "rogue_6_relic_cargo_2", "rogue_6_relic_final_2",
    "rogue_6_relic_fight_26",
}


def text(value, x, y, width=.16, height=.03, confidence=.99):
    return {"text": value, "confidence": confidence,
            "box": [[x, y], [x+width, y], [x+width, y+height], [x, y+height]]}


def held(texts):
    return next(t for t in texts if t["text"] == "收起")


def transformed(texts, sx, sy, tx, ty):
    result = copy.deepcopy(texts)
    for entry in result:
        entry["box"] = [[x*sx+tx, y*sy+ty] for x, y in entry["box"]]
    return result


@unittest.skipUnless(FIXTURE.exists(), "frozen original-image OCR fixture unavailable")
class OriginalHeldCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def training(self):
        return copy.deepcopy(self.fixtures["training_multirow"]["texts"])

    def test_one_original_multirow_training_image_confirms_eleven_cards(self):
        texts = self.training()
        cards = read_held_cards(texts, held(texts))
        self.assertEqual({card["id"] for card in cards}, TRAIN_IDS)
        self.assertEqual(len(cards), 11)
        self.assertTrue(all(card["confirmed"] for card in cards))
        for card in cards:
            self.assertEqual(set(card), {"id", "candidates", "confirmed", "source", "title"})
            self.assertNotIn("recipient", card)
            self.assertNotIn("count", card)

    def test_one_independent_three_card_holdout(self):
        texts = self.fixtures["holdout_three_cards"]["texts"]
        self.assertEqual({c["id"] for c in read_held_cards(texts, held(texts))}, {
            "rogue_6_active_tool_5", "rogue_6_relic_fight_26", "rogue_6_relic_cargo_1"})

    def test_closed_panel_does_not_read_owned_cards(self):
        texts = self.fixtures["closed_map"]["texts"]
        collapsed = next(t for t in texts if t["text"] == "收藏品")
        self.assertEqual(read_held_cards(texts, collapsed), [])

    def test_same_column_cards_keep_their_own_complete_usage(self):
        texts = self.training()
        regions = held_card_regions(texts, held(texts))
        sad = next(r for r in regions if r["title"] == "悲伤的红")
        self.assertEqual(sad["description_text"], "零件箱中每有1个零件，所有干员的生命和攻击力+8%")
        self.assertNotIn("攻击和生命+30%", sad["description_text"])
        self.assertEqual(len({r["column"] for r in regions}), 3)

    def test_actual_numeric_marker_is_inside_sad_icon_search_envelope(self):
        texts = self.training()
        sad = next(r for r in held_card_regions(texts, held(texts)) if r["title"] == "悲伤的红")
        marker = next(t for t in texts if t["text"] == "15")
        x0, y0, x1, y1 = sad["icon_bounds"]
        self.assertTrue(all(x0 <= x <= x1 and y0 <= y <= y1 for x, y in marker["box"]))
        self.assertEqual(sad["candidates"], ["rogue_6_relic_cargo_2"])

    def test_two_misread_names_are_not_guessed(self):
        texts = self.training()
        cards = read_held_cards(texts, held(texts))
        self.assertNotIn("rogue_6_start_4", {c["id"] for c in cards})
        self.assertNotIn("解约协议-Y", {c["title"] for c in cards})
        self.assertNotIn("强保九头蛇", {c["title"] for c in cards})

    def test_missing_name_prevents_counter_identity_binding(self):
        texts = [t for t in self.training() if t["text"] != "悲伤的红"]
        self.assertNotIn("rogue_6_relic_cargo_2", {c["id"] for c in read_held_cards(texts, held(texts))})
        self.assertNotIn("悲伤的红", {r["title"] for r in held_card_regions(texts, held(texts))})

    def test_low_confidence_name_is_not_owned(self):
        texts = self.training()
        next(t for t in texts if t["text"] == "悲伤的红")["confidence"] = .89
        self.assertNotIn("rogue_6_relic_cargo_2", {c["id"] for c in read_held_cards(texts, held(texts))})

    def test_incomplete_usage_is_not_owned(self):
        texts = [t for t in self.training() if t["text"] != "干员的生命和攻击力+8%"]
        self.assertNotIn("rogue_6_relic_cargo_2", {c["id"] for c in read_held_cards(texts, held(texts))})

    def test_low_confidence_usage_is_not_owned(self):
        texts = self.training()
        next(t for t in texts if t["text"] == "干员的生命和攻击力+8%")["confidence"] = .84
        self.assertNotIn("rogue_6_relic_cargo_2", {c["id"] for c in read_held_cards(texts, held(texts))})

    def test_merged_background_suffix_does_not_destroy_complete_usage(self):
        texts = self.training()
        clover = next(r for r in held_card_regions(texts, held(texts)) if r["title"] == "四叶草化石")
        self.assertIn("项敌方情报", clover["description_text"])
        self.assertEqual(clover["candidates"], ["rogue_6_relic_legacy_113"])

    def test_derived_affine_layouts_reuse_same_image_and_still_match(self):
        for sx, sy, tx, ty in ((.82, .9, .07, .03), (.94, .73, .01, .12), (.71, .94, .12, .01)):
            with self.subTest(transform=(sx, sy, tx, ty)):
                texts = transformed(self.training(), sx, sy, tx, ty)
                self.assertEqual({c["id"] for c in read_held_cards(texts, held(texts))}, TRAIN_IDS)

    def test_shuffled_ocr_lines_are_equivalent(self):
        texts = self.training()
        random.Random(54).shuffle(texts)
        self.assertEqual({c["id"] for c in read_held_cards(texts, held(texts))}, TRAIN_IDS)

    def test_geometry_result_does_not_claim_inventory_completeness(self):
        texts = self.training()
        for region in held_card_regions(texts, held(texts)):
            self.assertNotIn("inventory_complete", region)
            self.assertNotIn("count", region)
            self.assertNotIn("recipient", region)


class HeldCardContractTests(unittest.TestCase):
    def test_all_six_legacy_tool_single_card_contracts(self):
        for rid, item in tactical_tools().items():
            with self.subTest(tool=rid):
                title = text(item["name"], .2, .19, .5, .02)
                usage = text(item["usage"], .2, .34, .5, .02)
                anchor = text("收起", .2, .89, .5, .02)
                self.assertEqual(read_held_cards([title, usage], anchor), [{
                    "id": rid, "candidates": [rid], "confirmed": True,
                    "source": "held_name_and_usage", "title": item["name"]}])

    def test_without_verified_expand_anchor_rewards_are_not_owned(self):
        texts = [text("长生者之证", .2, .2), text("目标生命上限+6", .2, .25)]
        self.assertEqual(read_held_cards(texts, None), [])
        self.assertEqual(read_held_cards(texts, text("领取", .2, .9)), [])

    def test_invalid_anchor_boxes_and_confidence_are_rejected(self):
        for anchor in ({"text": "收起", "confidence": 1, "box": []},
                       text("收起", .2, .9, confidence=float("nan")),
                       text("收起", .2, .9, confidence=.89)):
            self.assertEqual(read_held_cards([], anchor), [])

    def test_unknown_next_card_cannot_supply_missing_previous_usage(self):
        anchor = text("收起", .1, .92)
        texts = [text("悲伤的红", .2, .2, .11),
                 text("零件箱中每有1个零件，所有", .2, .24, .4),
                 text("未辨识的标题", .2, .43, .15),
                 text("干员的生命和攻击力+8%", .2, .48, .4),
                 text("长生者之证", .2, .65, .11),
                 text("目标生命上限+6", .2, .69, .4)]
        cards = read_held_cards(texts, anchor)
        self.assertEqual([c["id"] for c in cards], ["rogue_6_relic_legacy_110"])

    def test_same_name_and_complete_usage_ambiguity_is_preserved(self):
        items = {"a": {"name": "同名藏品", "usage": "攻击力+10%"},
                 "b": {"name": "同名藏品", "usage": "攻击力+10%"}}
        texts = [text("同名藏品", .2, .2), text("攻击力+10%", .2, .25)]
        with patch("rouge.held_cards._inventory", return_value=(items, {"同名藏品": ["a", "b"]})):
            self.assertEqual(read_held_cards(texts, text("收起", .1, .92)), [{
                "id": None, "candidates": ["a", "b"], "confirmed": False,
                "source": "held_name_and_usage", "title": "同名藏品"}])

    def test_two_columns_cannot_combine_halves_of_a_usage(self):
        anchor = text("收起", .1, .92)
        texts = [text("悲伤的红", .2, .2, .1), text("长生者之证", .6, .2, .1),
                 text("零件箱中每有1个零件，所有", .2, .24, .25),
                 text("干员的生命和攻击力+8%", .6, .24, .25)]
        self.assertEqual(read_held_cards(texts, anchor), [])


if __name__ == "__main__":
    unittest.main()
