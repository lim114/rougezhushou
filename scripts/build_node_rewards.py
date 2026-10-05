"""Build auditable reward references from pinned game data, never inferred rates.

Run with the project Python from the repository root. No network or private state.
"""
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache/game-data"
COMMIT = "a550f5e048bb94e7cdefc6eb97a4091f0c4c7add"
TOPIC_HASH = "f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86"

# This list was reviewed against the named grant text, not inferred from itemId.
# A nextSceneId is the destination, never an asserted source-scene choice edge.
NAMED_CHOICES = {
    "choice_ro6_relic1_1": "血衣之下", "choice_ro6_relic1_2": "血衣之下",
    "choice_ro6_relic1_3": "血衣之下", "choice_ro6_relic2_1": "擒与缚",
    "choice_ro6_relic2_2": "擒与缚", "choice_ro6_normal1_1": "沉寂之屋",
    "choice_ro6_normal1_2": "沉寂之屋", "choice_ro6_normal2_1": "黑诞",
    "choice_ro6_normal4_26": "被歌颂的影子", "choice_ro6_normal5_1": "愈创之心",
    "choice_ro6_normal5_2": "愈创之心", "choice_ro6_normal5_3": "愈创之心",
    "choice_ro6_task1_1": "和平守卫者", "choice_ro6_task2_1": "独活",
    "choice_ro6_rest_4": "金色凝滞", "choice_ro6_chimera2_1": "泪之聚落",
    "choice_ro6_sacrifice2_21": "回滚文明",
}
CHESTS = {"trap_321_shnbox", "trap_322_shrbox", "trap_320_shtlbx", "trap_323_shsbox"}
RARE_ENEMIES = {"enemy_2001_duckmi", "enemy_2002_bearmi", "enemy_2034_sythef", "enemy_2085_skzjxd"}


def plain(text):
    return re.sub(r"<[^>]*>", "", text or "")


def normalized(text):
    return re.sub(r"[\W_]+", "", plain(text))


def checked_json(path, receipt):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != receipt["sha256"]:
        raise ValueError(f"Source hash mismatch: {path}")
    return json.loads(raw)


def evidence(receipt, field_path):
    return {"url": receipt["url"], "sha256": receipt["sha256"], "field_path": field_path}


def walk(value, path="$"):
    yield path, value
    if isinstance(value, dict):
        for key, item in value.items():
            yield from walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from walk(item, f"{path}[{i}]")


def named_choices(detail, receipt):
    result = {}
    for choice_id, context_title in NAMED_CHOICES.items():
        choice = detail["choices"][choice_id]
        display = choice["displayData"]
        item = detail["items"][display["itemId"]]
        description = plain(choice["description"])
        # type ITEM alone is not enough: hidden starting buffs also use it.
        if (display["type"] != "ITEM" or display["effectHintType"] != "ITEM"
                or choice["type"] != "TRADE" or choice["isHiddenChoice"]
                or "获得" not in description
                or normalized(item["name"]) not in normalized(description.split("获得", 1)[1])):
            raise ValueError(f"Named grant evidence failed for {choice_id}")
        destination = detail["choiceScenes"][choice["nextSceneId"]]
        if destination["title"] != context_title:
            raise ValueError(f"Reviewed event title changed for {choice_id}")
        condition = description.split("，获得", 1)[0] if "，获得" in description else None
        conditions = [{"kind": "text_condition", "text": condition}] if condition else []
        if choice_id == "choice_ro6_normal2_1":
            conditions = [{"kind": "requires_item", "item_id": "rogue_6_scrap_G_12",
                           "name": "笼控器", "text": condition}]
        result[choice_id] = {
            "choice_id": choice_id, "choice_title": plain(choice["title"]),
            "event_title": context_title, "description": description,
            "condition_text": condition, "conditions": conditions,
            "locked_cover_text": plain(choice.get("lockedCoverDesc")) or None,
            "eligibility": None,
            "reward": {"item_id": item["id"], "name": item["name"], "type": item["type"],
                       "quantity": None, "quantity_status": "not_serialized_in_display_data"},
            "next_scene_id": choice["nextSceneId"],
            "evidence": evidence(receipt, f"$.details.rogue_6.choices.{choice_id}"),
            "item_evidence": evidence(receipt, f"$.details.rogue_6.items.{item['id']}"),
            "scope": "named_grant_in_visible_choice_description",
        }
    return result


def level_groups(level, receipt, enemy_names, enemy_receipt, characters, character_receipt):
    aliases = {}
    for container in ("predefines", "hardPredefines"):
        for i, instance in enumerate((level.get(container) or {}).get("tokenInsts") or []):
            alias = instance.get("alias")
            if alias:
                aliases[alias] = (instance.get("inst", {}).get("characterKey"),
                                  f"$.{container}.tokenInsts[{i}].inst.characterKey")
    chest_groups, rare_groups = [], []
    for wi, wave in enumerate(level.get("waves") or []):
        for fi, fragment in enumerate(wave.get("fragments") or []):
            groups = defaultdict(list)
            for ai, action in enumerate(fragment.get("actions") or []):
                key = action.get("randomSpawnGroupKey")
                if key:
                    groups[key].append((ai, action))
            for key, actions in groups.items():
                chest = any(aliases.get(a.get("key"), (None,))[0] in CHESTS for _, a in actions)
                rare = any(a.get("key") in RARE_ENEMIES for _, a in actions)
                if not (chest or rare):
                    continue
                path = f"$.waves[{wi}].fragments[{fi}].actions"
                group = {"group_key": key, "wave_index": wi, "fragment_index": fi,
                         "kind": "chest_spawn" if chest else "rare_enemy_spawn",
                         "probability": None, "activation_status": "not_evaluated",
                         "evidence": evidence(receipt, path), "candidates": []}
                for ai, action in actions:
                    alias = action.get("key") or ""
                    resolved, alias_path = aliases.get(alias, (alias or None, None))
                    candidate = {"action_type": action.get("actionType"), "key": alias,
                                 "entity_id": resolved, "raw_weight": action.get("weight"),
                                 "count": action.get("count"), "hidden_group": action.get("hiddenGroup"),
                                 "pack_key": action.get("randomSpawnGroupPackKey"),
                                 "random_type": action.get("randomType"),
                                 "refresh_type": action.get("refreshType"),
                                 "evidence": evidence(receipt, f"{path}[{ai}]")}
                    if alias_path:
                        candidate["entity_evidence"] = evidence(receipt, alias_path)
                    if not alias:
                        candidate["name"] = "空分支（原始 key 为空）"
                    elif resolved in CHESTS:
                        candidate["name"] = characters[resolved]["name"]
                        candidate["entity_kind"] = "device"
                        candidate["name_evidence"] = evidence(character_receipt, f"$.{resolved}.name")
                    elif resolved in enemy_names:
                        candidate["name"], name_path = enemy_names[resolved]
                        candidate["name_evidence"] = evidence(enemy_receipt, name_path)
                    else:
                        candidate["name"] = resolved or alias
                    group["candidates"].append(candidate)
                (chest_groups if chest else rare_groups).append(group)
    return chest_groups, rare_groups


def build():
    root_receipt = json.loads((CACHE / "receipt.json").read_text(encoding="utf-8"))
    level_receipt = json.loads((CACHE / "level-receipt.json").read_text(encoding="utf-8"))
    if root_receipt["commit"] != COMMIT or level_receipt["commit"] != COMMIT:
        raise ValueError("Review the new source revision before rebuilding")
    topic_receipt = root_receipt["files"]["roguelike_topic_table"]
    if topic_receipt["sha256"] != TOPIC_HASH:
        raise ValueError("Review the topic table hash before rebuilding")
    raw = checked_json(CACHE / "roguelike_topic_table.json", topic_receipt)
    detail = raw["details"]["rogue_6"]
    character_receipt = root_receipt["files"]["character_table"]
    characters = checked_json(CACHE / "character_table.json", character_receipt)
    enemy_receipt = level_receipt["files"]["enemydata/enemy_database.json"]
    enemies = checked_json(CACHE / "levels/enemydata/enemy_database.json", enemy_receipt)
    enemy_names = {}
    for i, enemy in enumerate(enemies["enemies"]):
        for j, variant in enumerate(enemy["Value"]):
            name = variant["enemyData"]["name"]
            if name["m_defined"] and enemy["Key"] not in enemy_names:
                enemy_names[enemy["Key"]] = (name["m_value"], f"$.enemies[{i}].Value[{j}].enemyData.name")
    levels, stages = {}, {}
    for stage_id, stage in detail["stages"].items():
        relative = stage["levelId"].lower() + ".json"
        if relative not in levels:
            source = level_receipt["files"].get(relative)
            if not source:
                raise ValueError(f"Missing recorded level source: {relative}")
            level = checked_json(CACHE / "levels" / relative, source)
            chest_groups, rare_groups = level_groups(level, source, enemy_names, enemy_receipt,
                                                     characters, character_receipt)
            levels[relative] = {"level_id": stage["levelId"], "evidence": evidence(source, "$"),
                                "battle_chest_groups": chest_groups, "rare_enemy_groups": rare_groups}
        stages[stage_id] = {
            "stage_id": stage_id, "name": stage["name"], "difficulty": stage["difficulty"],
            "is_elite": stage["isElite"], "is_boss": stage["isBoss"],
            "level_key": relative, "linked_stage_id": stage["linkedStageId"],
            "level_replacements": stage["levelReplaceIds"],
            "evidence": evidence(topic_receipt, f"$.details.rogue_6.stages.{stage_id}"),
        }
    refs = defaultdict(list)
    for field_path, value in walk(detail, "$.details.rogue_6"):
        if isinstance(value, str) and value.startswith("pool_"):
            refs[value].append(field_path)
    definitions = [path for path, value in walk(raw) if isinstance(value, dict)
                   for key in value if key.startswith("pool_")]
    data = {
        "schema_version": 1, "commit": COMMIT, "source": topic_receipt,
        "event_rewards": named_choices(detail, topic_receipt),
        "scene_titles": {key: value["title"] for key, value in detail["choiceScenes"].items()},
        "stages": stages, "levels": levels,
        "unresolved_pool_references": [{"raw_reference": key,
                                        "pool_id": key if ":" not in key else None,
                                        "reference_kind": "pool_id" if ":" not in key else "colon_expression",
                                        "status": "definition_missing_in_inspected_table",
                                        "references": [evidence(topic_receipt, path) for path in paths]}
                                       for key, paths in sorted(refs.items())],
        "inspection": {"table_pool_definition_keys": len(definitions), "stages": len(stages),
                       "unique_levels": len(levels), "explicit_named_choices": len(NAMED_CHOICES),
                       "direct_pool_reference_names": sum(":" not in key for key in refs),
                       "pool_colon_expressions": sum(":" in key for key in refs),
                       "excluded_placeholder_examples": ["choice_ro6_evacuate_3", "choice_ro6_scout_4"]},
        "limitations": [
            "资料预览不表示当前已获得奖励；选项解锁、资源足够及分支执行状态尚未核验。",
            "nextSceneId 是选择后的场景；原始表未提供完整的来源场景到选项映射，不据此恢复选择链。",
            "宝箱与稀有敌人仅列关卡 waves 中的原始随机组；不假定激活条件、独立性或归一化算法，不换算掉率。",
            "普通/紧急关卡各自保留身份；共享 levelId 不代表所有难度脚本与产出相同。",
            "尚未恢复完整结算掉落池、池权重、解锁条件及局内额外奖励修正。",
            "未穷尽 branches、固定生成和脚本动态生成；未找到随机组不代表不会出现宝箱。",
        ],
    }
    destination = ROOT / "rouge/data/node-reward-reference.json"
    destination.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data["inspection"], ensure_ascii=False))


if __name__ == "__main__":
    build()
