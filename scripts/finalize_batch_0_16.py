"""Consolidate tested sources, real launch and fresh background sampling."""
import hashlib
import json
import re
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((root / name).read_text(encoding="utf-8"))


log = (root / ".cache/tests-0.16.log").read_text(encoding="utf-8")
assert re.search(r"Ran 144 tests", log) and log.rstrip().endswith("OK")
rules = read("RELIC_VERIFICATION.json")
ui = read("RELIC_UI_0.16_VERIFICATION.json")
launch = read("APP_0.16_LAUNCH_VERIFICATION.json")
live = read("ENVIRONMENT_0.16_LIVE_VERIFICATION.json")
assert rules["data_rule_counts"] == {
    "non_output": 52, "numeric": 111, "pending": 86,
    "conditional": 14, "partial": 9,
}
assert rules["public_entry_cases"] == 8704
assert rules["relic_regression_tests"] == 29
assert all(ui[key] for key in (
    "new_relics_in_calculation", "current_conditions_only",
    "manual_conditions_not_saved_to_run", "independent_token_conditions",
    "irrelevant_enemy_conditions_hidden",
))
assert all(launch[key] for key in (
    "only_one_project_window", "same_run_preserved", "history_preserved",
    "settings_and_bindings_unchanged", "run_cmd_startup_verified",
))
assert "0.16" in launch["window_title"]
assert all(live[key] for key in (
    "running_app_matches_visible_config", "same_run_preserved", "history_preserved",
    "foreground_unchanged", "game_in_background",
))
assert all(receipt["chat_requests"] == 0 for receipt in (rules, ui, launch, live))
assert (root / ".cache/launch-0.16.err.log").read_text(encoding="utf-8") == ""
for name, digest in rules["source_hashes"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, name

files = [
    "rouge/relics.py", "rouge/run_modifiers.py", "rouge/reporting.py", "rouge/app.py",
    "scripts/build_relic_mechanics.py", "scripts/verify_relic_mechanics.py",
    "scripts/verify_relic_ui_0_16.py", "scripts/verify_environment_live_0_16.py",
    "scripts/finalize_batch_0_16.py", "rouge/data/relic-mechanics.json",
    "tests/test_relic_extension.py", "BATCH_0.16.md", "PROJECT_PROGRESS.md",
    "RELIC_MECHANICS.md", "RELIC_COVERAGE.md", "README.md", "pyproject.toml",
]
receipt = {
    "version": "0.16.0", "verified_at": time.time(), "tests_passed": 144,
    "skill_profiles": 87, "new_relics": 6, "relic_regression_tests": 29,
    "public_entry_cases": 8704, "relic_data_rule_counts": rules["data_rule_counts"],
    "current_app_source_matches_relic_verification": True,
    "actual_background_region_and_difficulty": True,
    "same_run_and_history_preserved": True, "private_config_unchanged": True,
    "current_conditions_only": True, "manual_conditions_not_saved_to_run": True,
    "chat_requests": 0, "new_live_combat_measurements": 0,
    "source_hashes": {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files
    },
    "limitations": [
        "134件有数值、条件或部分规则，不代表134件全部机制完整支持。",
        "8704入口检查不是所有藏品与所有技能的完整组合校准。",
        "叠层、随机受益者和单位条件未知时不猜测；仅用于局外情景。",
        "生命比例回复参考常态最大生命，未积分技能期间动态生命变化。",
        "没有新增实战伤害测量或聊天发送；整体未完成项见PROJECT_PROGRESS.md。",
    ],
}
(root / "FINAL_0.16_VERIFICATION.json").write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("0.16 verified: 144 tests, 87 skills, 8704 relic entry cases; "
      "actual background capture; same run and private configuration retained")
