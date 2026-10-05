"""Conditional reference previews must never turn UI artwork into awarded loot."""
import copy
import unittest

from rouge.node_rewards import preview_node_rewards


def event(title, scenes, *options):
    return {"kind": "event", "title": title, "scene_candidates": scenes,
            "visible_options": [{"title": title, "choice_candidates": ids}
                                for title, ids in options]}


class NodeRewardTests(unittest.TestCase):
    def test_blood_clothes_alternatives_stay_separate_and_conditional(self):
        content = event("血衣之下", ["scene_ro6_relic1_enter"],
                        ("拽出衣服寻找可用物资", ["choice_ro6_relic1_1"]),
                        ("割下怪花", ["choice_ro6_relic1_2"]),
                        ("砍断藤蔓", ["choice_ro6_relic1_3"]))
        before = copy.deepcopy(content)
        result = preview_node_rewards(content)
        self.assertEqual(content, before)
        self.assertEqual(result["status"], "partial_reference")
        self.assertEqual(result["scene_candidates"], ["scene_ro6_relic1_enter"])
        self.assertEqual([o["reward_candidates"][0]["reward"]["item_id"]
                          for o in result["event_options"]],
                         ["rogue_6_relic_fight_11", "rogue_6_relic_legacy_142", "rogue_6_relic_legacy_141"])
        for option in result["event_options"]:
            reward = option["reward_candidates"][0]
            self.assertIsNone(reward["eligibility"])
            self.assertIsNone(reward["reward"]["quantity"])
            self.assertEqual(reward["evidence"]["field_path"],
                             f"$.details.rogue_6.choices.{reward['choice_id']}")
            self.assertEqual(len(reward["evidence"]["sha256"]), 64)

    def test_black_birth_requires_cage_controller_without_assuming_owned(self):
        result = preview_node_rewards(event("黑诞", ["scene_ro6_normal2_enter"],
                      ("掏出笼控器控制猎狗", ["choice_ro6_normal2_1"])))
        reward = result["event_options"][0]["reward_candidates"][0]
        self.assertEqual(reward["reward"]["name"], "猎印")
        self.assertEqual(reward["condition_text"], "持有笼控器")
        self.assertEqual(reward["conditions"][0]["item_id"], "rogue_6_scrap_G_12")
        self.assertIsNone(reward["eligibility"])

    def test_placeholder_item_id_is_not_a_named_reward(self):
        result = preview_node_rewards(event("三重身", ["scene_ro6_evacuate_enter"],
                      ("接受它的提议", ["choice_ro6_evacuate_3"])))
        self.assertEqual(result["status"], "unknown")
        self.assertFalse(result["event_options"][0]["reward_candidates"])
        self.assertEqual(result["event_options"][0]["unresolved_choice_ids"], ["choice_ro6_evacuate_3"])
        self.assertTrue(result["unresolved_pools"])

    def test_ambiguous_choice_and_scene_identity_are_not_hidden(self):
        result = preview_node_rewards(event("被歌颂的影子", ["scene_ro6_normal4_26", "scene_ro6_normal4_27"],
                      ("收下", ["choice_ro6_normal4_26", "choice_ro6_normal4_10"])))
        option = result["event_options"][0]
        self.assertEqual(option["status"], "ambiguous")
        self.assertEqual(option["choice_candidates"], ["choice_ro6_normal4_26", "choice_ro6_normal4_10"])
        self.assertEqual(option["unresolved_choice_ids"], ["choice_ro6_normal4_10"])
        self.assertEqual(option["reward_candidates"][0]["reward"]["name"], "犬植浆")
        self.assertEqual(result["scene_candidates"], ["scene_ro6_normal4_26", "scene_ro6_normal4_27"])

    def test_title_scene_and_visible_choice_mismatch_rejects_reward(self):
        for content in [
            event("黑诞", ["scene_ro6_relic1_enter"], ("掏出笼控器控制猎狗", ["choice_ro6_normal2_1"])),
            event("黑诞", ["scene_ro6_normal2_enter"], ("收下", ["choice_ro6_normal2_1"])),
            event("血衣之下", ["scene_ro6_relic1_enter"], ("掏出笼控器控制猎狗", ["choice_ro6_normal2_1"])),
        ]:
            with self.subTest(content=content):
                self.assertEqual(preview_node_rewards(content)["status"], "unknown")

    def test_normal_and_emergency_battle_variants_are_not_merged(self):
        content = {"kind": "battle", "title": "遗忘时间", "variant_id": None,
                   "variants": [{"id": "ro6_n_1_2", "difficulty": "NORMAL"},
                                {"id": "ro6_e_1_2", "difficulty": "FOUR_STAR"}]}
        result = preview_node_rewards(content)
        self.assertEqual([v["stage_id"] for v in result["battle_variants"]], ["ro6_n_1_2", "ro6_e_1_2"])
        self.assertEqual([v["difficulty"] for v in result["battle_variants"]], ["NORMAL", "FOUR_STAR"])
        first = result["battle_variants"][0]
        self.assertEqual(len(first["battle_chest_groups"]), 2)
        self.assertEqual([c["raw_weight"] for c in first["battle_chest_groups"][0]["candidates"]],
                         [850, 105, 35, 35, 15])
        for group in first["battle_chest_groups"]:
            self.assertIsNone(group["probability"])
            self.assertFalse(any("probability" in c for c in group["candidates"]))
            self.assertEqual(len(group["evidence"]["sha256"]), 64)
        self.assertTrue(first["rare_enemy_groups"])
        self.assertTrue(result["unresolved_pools"])
        content["variant_id"] = "ro6_e_1_2"
        self.assertEqual([v["stage_id"] for v in preview_node_rewards(content)["battle_variants"]], ["ro6_e_1_2"])

    def test_unknown_stage_or_content_does_not_borrow_another_variant(self):
        for content in [None, {}, {"kind": "event", "title": "未收录事件"},
                        {"kind": "battle", "title": "遗忘时间", "variant_id": "not_real"},
                        {"kind": "battle", "title": "未收录", "variant_id": "ro6_n_1_2"}]:
            with self.subTest(content=content):
                result = preview_node_rewards(content)
                self.assertEqual(result["status"], "unknown")
                self.assertFalse(result["battle_variants"])

    def test_public_results_do_not_mutate_cached_reference(self):
        content = event("黑诞", ["scene_ro6_normal2_enter"],
                        ("掏出笼控器控制猎狗", ["choice_ro6_normal2_1"]))
        result = preview_node_rewards(content)
        result["event_options"][0]["reward_candidates"][0]["reward"]["name"] = "changed"
        self.assertEqual(preview_node_rewards(content)["event_options"][0]["reward_candidates"][0]["reward"]["name"], "猎印")


if __name__ == "__main__":
    unittest.main()
