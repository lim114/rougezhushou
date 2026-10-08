"""Read-only reward references attached to visible, possibly ambiguous content.

No grant is applied to RunState and no raw spawn weight becomes a drop rate.
"""
import copy
import json
import re
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _reference():
    path = Path(__file__).with_name("data") / "node-reward-reference.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized(value):
    return re.sub(r"[\W_]+", "", value or "")


def _ids(values):
    return list(dict.fromkeys(value for value in values or [] if isinstance(value, str)))


def preview_node_rewards(content):
    """Return conditional references, retaining all input scene/option variants.

    ``content`` has the public ``read_node_content`` shape. Event rewards require
    matching visible title, scene-title candidate, option title and reviewed ID.
    Their applicability remains unknown: no source-scene edge or resource state
    is assumed. Battle variants require an explicit ID or candidate IDs from the
    content reader, never title-only inference.
    """
    data = _reference()
    content = content if isinstance(content, dict) else {}
    kind = content.get("kind")
    result = {"status": "unknown", "kind": kind, "title": content.get("title"),
              "event_options": [], "battle_variants": [], "unresolved_pools": [],
              "limitations": list(data["limitations"]), "probability": None}
    if kind == "event":
        _event_preview(content, data, result)
    elif kind == "battle":
        _battle_preview(content, data, result)
    else:
        result["unresolved_pools"].append({"scope": "content", "status": "unknown",
                                            "reason": "尚无可对应的可见事件或关卡身份。"})
    return result


def _event_preview(content, data, result):
    scenes = _ids(content.get("scene_candidates"))
    title = content.get("title")
    matching_scenes = [scene for scene in scenes if data["scene_titles"].get(scene) == title]
    result["scene_candidates"] = scenes
    result["unresolved_scene_ids"] = [scene for scene in scenes if scene not in matching_scenes]
    unresolved_ids = []
    for visible in content.get("visible_options") or []:
        if not isinstance(visible, dict):
            continue
        ids = _ids(visible.get("choice_candidates"))
        row = {"title": visible.get("title"), "choice_candidates": ids,
               "status": "unknown", "reward_candidates": [], "unresolved_choice_ids": []}
        for choice_id in ids:
            reference = data["event_rewards"].get(choice_id)
            if (not reference or not matching_scenes or reference["event_title"] != title
                    or _normalized(reference["choice_title"]) != _normalized(visible.get("title"))):
                row["unresolved_choice_ids"].append(choice_id)
                continue
            candidate = copy.deepcopy(reference)
            candidate["context_scene_candidates"] = list(matching_scenes)
            candidate["source_scene_link_verified"] = False
            row["reward_candidates"].append(candidate)
        if row["reward_candidates"]:
            row["status"] = "ambiguous" if (len(ids) != 1 or len(scenes) != 1
                                               or row["unresolved_choice_ids"]) else "conditional_reference"
            result["status"] = "partial_reference"
        result["event_options"].append(row)
        unresolved_ids.extend(row["unresolved_choice_ids"])
    result["unresolved_pools"].append({
        "scope": "event_random_rewards", "status": "unknown",
        "choice_ids": _ids(unresolved_ids),
        "reason": "仅接入已核验的具名选项奖励；其余选项和随机奖励的完整候选池、权重、解锁条件尚未恢复。",
    })
    if not result["event_options"]:
        result["limitations"].append("未读取到可对应的可见选项，不用事件标题猜测当前能选的奖励。")


def _battle_preview(content, data, result):
    selected = content.get("variant_id")
    if selected:
        ids = [selected]
    else:
        ids = _ids([variant.get("id") for variant in content.get("variants") or []
                    if isinstance(variant, dict)])
    result["variant_candidates"] = ids
    result["unresolved_variant_ids"] = []
    for stage_id in ids:
        stage = data["stages"].get(stage_id)
        if not stage or stage["name"] != content.get("title"):
            result["unresolved_variant_ids"].append(stage_id)
            continue
        level = data["levels"][stage["level_key"]]
        variant = copy.deepcopy(stage)
        variant["level_evidence"] = copy.deepcopy(level["evidence"])
        variant["battle_chest_groups"] = copy.deepcopy(level["battle_chest_groups"])
        variant["rare_enemy_groups"] = copy.deepcopy(level["rare_enemy_groups"])
        variant["activation_status"] = "not_evaluated"
        variant["status"] = "raw_group_reference" if (level["battle_chest_groups"] or level["rare_enemy_groups"]) else "unknown"
        result["battle_variants"].append(variant)
        if variant["status"] == "raw_group_reference":
            result["status"] = "partial_reference"
    result["unresolved_pools"].append({
        "scope": "battle_settlement", "status": "unknown",
        "reason": "尚未恢复该关卡完整结算掉落池；宝箱/敌人的生成候选不等于击破奖励或战后实际掉落。",
    })
    result["unresolved_pools"].append({
        "scope": "run_modifiers", "status": "unknown",
        "reason": "分队、加工品行进触发、追猎、收藏品、难度及事件条件对额外奖励的共同影响尚未完整求值。",
    })
