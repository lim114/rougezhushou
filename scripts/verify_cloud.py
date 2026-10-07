"""Portable calculation regression. This does not certify Windows sampling/UI."""
import json
import platform
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MODULES = (
    "tests.test_known_recruitment_condition_label",
    "tests.test_shu_periodic_sp_reference",
    "tests.test_damage_subtotal_sources",
    "tests.test_emergency_recruitment_condition",
    "tests.test_declared_count_input_types",
    "tests.test_module_qualification_notes",
    "tests.test_target_count_input_types",
    "tests.test_amiya_continuous_lifetime",
    "tests.test_damage", "tests.test_timing", "tests.test_relics",
    "tests.test_neural_relic_034", "tests.test_ammo_counter_055",
    "tests.test_ammo_events_067", "tests.test_summon_modules_038",
    "tests.test_summon_composition_068", "tests.test_summon_limits_069", "tests.test_token_manual_attributes", "tests.test_wang_token_module_reference",
    "tests.test_attack_speed_bounds_065",
    "tests.test_run_modifiers", "tests.test_run_config_validation", "tests.test_training_input_types", "tests.test_multi_melee_070",
    "tests.test_neural_sources_035", "tests.test_s1_neural_boundary",
    "tests.test_neural_incoming_clock", "tests.test_charge_reference", "tests.test_shield_break_reference", "tests.test_gnosis_attack_clock", "tests.test_gnosis_s1_reference", "tests.test_gnosis_target_lifetime", "tests.test_gnosis_isw_a_reference", "tests.test_drone_attack_clock", "tests.test_myrtle_healing_targets", "tests.test_gummy_cooking_clock", "tests.test_drone_traits", "tests.test_gummy_expected_clock", "tests.test_headwolf_phase_clock", "tests.test_wisdel_secondary_reference", "tests.test_wisdel_ghost_clock", "tests.test_mizuki_talent_identity", "tests.test_mizuki_amb_y_reference", "tests.test_mizuki_s1_reference", "tests.test_mei_s1_reference", "tests.test_ines_dot_reference", "tests.test_manual_close_reference", "tests.test_aglna_liftoff_reference", "tests.test_next_attack_healing_reference", "tests.test_snow_field_reference", "tests.test_snow_entry_reference", "tests.test_xiangzi_notes_reference", "tests.test_shield_contact_reference", "tests.test_orchid_arrow_reference", "tests.test_orchid_redeploy_reference", "tests.test_haruka_event_reference", "tests.test_haruka_healing_targets", "tests.test_healing_subtotal_scaling", "tests.test_wang_passive_reference", "tests.test_mantra_manual_events", "tests.test_deployment_independent_sources", "tests.test_empty_enemy_scope", "tests.test_friendly_scope_report", "tests.test_susuro_recipient_factor", "tests.test_chen_phase_reference", "tests.test_amiya_phase_reference", "tests.test_amiya_input_qualification", "tests.test_yato_deployment_reference", "tests.test_enemy_rune_selectors", "tests.test_aglna_manual_weight", "tests.test_drone_aura_reference", "tests.test_drone_arrival_reference", "tests.test_token_duration_reference", "tests.test_technology_reference",
    "tests.test_zero_lifetime_aliases",
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
