"""Portable calculation regression. This does not certify Windows sampling/UI."""
import json
import platform
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MODULES = (
    "tests.test_damage", "tests.test_timing", "tests.test_relics",
    "tests.test_neural_relic_034", "tests.test_ammo_counter_055",
    "tests.test_ammo_events_067", "tests.test_summon_modules_038",
    "tests.test_summon_composition_068", "tests.test_summon_limits_069",
    "tests.test_attack_speed_bounds_065",
    "tests.test_run_modifiers", "tests.test_run_config_validation", "tests.test_multi_melee_070",
    "tests.test_neural_sources_035", "tests.test_s1_neural_boundary",
    "tests.test_neural_incoming_clock", "tests.test_charge_reference", "tests.test_gnosis_attack_clock", "tests.test_gnosis_s1_reference", "tests.test_gnosis_target_lifetime", "tests.test_drone_attack_clock", "tests.test_myrtle_healing_targets", "tests.test_gummy_cooking_clock", "tests.test_drone_traits", "tests.test_gummy_expected_clock",
)

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=1).run(
        unittest.defaultTestLoader.loadTestsFromNames(MODULES)
    )
    print(json.dumps({
        "passed": result.wasSuccessful(), "platform": platform.system(),
        "tests_run": result.testsRun, "skipped": len(result.skipped),
        "failures": len(result.failures), "errors": len(result.errors),
        "scope": "portable calculation regression; no Windows UI/capture or private state",
    }, ensure_ascii=False))
    sys.exit(0 if result.wasSuccessful() else 1)
