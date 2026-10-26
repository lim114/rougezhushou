"""Run the full maintained selector set and disclose migration prerequisites.

Missing .cache evidence is unavailable, never passed. Product assets and
calculation failures remain errors. --require-complete also fails for unavailable
checks. Native Windows integration is outside this offline suite.
"""
import argparse
import hashlib
import json
import platform
import re
import sys
import tempfile
import traceback
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
NEW_MODULES = (
    'tests.test_full_validation_prerequisites',
    'tests.test_recovery_attributes',
    'tests.test_sp_recovery_clock',
    'tests.test_sp_setter_reference',
    'tests.test_sp_initialization_reference',
    'tests.test_skill_sp_cost_independent_277',
    'tests.test_skill_data_cost_independent_278',
    'tests.test_skill_sp_increment_independent_279',
    'tests.test_skill_cost_rounding_consensus_independent_280',
    'tests.test_skill_data_cost_consensus_independent_281',
    'tests.test_sp_recovery_attribute_independent_282',
    'tests.test_panel_native_finalization_283',
    'tests.test_panel_native_main_283',
    'tests.test_extended_skill_native_284',
    'tests.test_extended_calibration_285',
    'tests.test_player_node_information_286',
    'tests.test_player_battle_information_286',
    'tests.test_player_information_view_286',
    'tests.test_moving_reward_reference_287',
    'tests.test_moving_reward_integration_287',
    'tests.test_direct_landmark_288',
    'tests.test_player_tile_information_288',
    'tests.test_event_named_reward_links_289',
    'tests.test_event_named_reward_integration_289',
    'tests.test_choice_recruitment_results_290',
    'tests.test_choice_recruitment_integration_290',
    'tests.test_regeneration_clock',
    'tests.test_modifier_packet_reference',
    'tests.test_route_information_scope',
    'tests.test_token_level_reference',
    'tests.test_level_panel_diagnostics',
    'tests.test_branch_position_overview',
    'tests.test_mechanist_barrier_ledger',
    'tests.test_mechanist_shield_grants',
    'tests.test_shield_source_inventory',
    'tests.test_mechanist_explosion_math',
    'tests.test_ling_fusion_reference',
    'tests.test_original_destinations',
    'tests.test_relic_panel_diagnostics_view',
    'tests.test_auxiliary_enemy_mechanisms',
    'tests.test_route_search_view',
    'tests.test_enemy_prefab_skill_gates',
    'tests.test_direct_landmark_extension',
    'tests.test_route_comparison_view',
    'tests.test_direct_landmark_mapping',
    'tests.test_enemy_skill_resources',
    'tests.test_branch_choices_046',
    'tests.test_sixth_floor_browsing',
    'tests.test_enemy_native_movement',
    'tests.test_rare_reward_sources',
    'tests.test_map_ground_extension',
    'tests.test_base_settlement_planning',
    'tests.test_choice_held_requirements',
    'tests.test_node_arrival_planning',
    'tests.test_guardian_healing_gates_view',
    'tests.test_susuro_module_healing_view',
    'tests.test_view_catalog_045',
    'tests.test_stage_context',
    'tests.test_branch_reference',
    'tests.test_enemy_configuration_view',
    'tests.test_supplemental_battle_view_142',
    'tests.test_battle_reward_planning',
    'tests.test_original_entry_planning',
    'tests.test_node_history_workflow',
    'tests.test_exploration_main_window',
    'tests.test_exploration_tools_view',
    'tests.test_node_resource_view',
    'tests.test_node_map_navigation',
    'tests.test_wang_count_dialog',
    'tests.test_node_catalog_view',
    'tests.test_offline_tools_view',
    'tests.test_batch185_mainwindow',
    'tests.test_new_run_capture_view_112',
    'tests.test_s1_neural_boundary',
    'tests.test_neural_incoming_clock',
    'tests.test_charge_reference',
    'tests.test_gnosis_attack_clock',
    'tests.test_gnosis_s1_reference',
    'tests.test_gnosis_target_lifetime',
    'tests.test_frame_buffer',
    'tests.test_difficulty_relics',
    'tests.test_inventory_tools',
    'tests.test_node_rewards',
    'tests.test_projection_screen_029',
    'tests.test_relic_screening_024',
    'tests.test_chat',
    'tests.test_numeric_recognition_024.NumericRecognition024Tests.test_verified_zero_uses_only_recognizer_across_moved_resized_panels',
    'tests.test_numeric_recognition_024.NumericRecognition024Tests.test_ten_or_empty_or_wrong_topology_cannot_shortcut_to_zero',
    'tests.test_numeric_recognition_024.NumericRecognition024Tests.test_weak_recognizer_result_falls_back_without_relaxing_threshold',
    'tests.test_node_content.NodeContentTests.test_legacy_clearing_record_recovers_only_confirmed_same_layout_history',
    'tests.test_node_content.NodeContentTests.test_passed_clearing_keeps_original_type_and_consumes_generation_budget_after_restart',
    'tests.test_node_content.NodeContentTests.test_fog_next_to_visible_vantage_point_reports_visibility_conflict',
    'tests.test_node_content.NodeContentTests.test_immediately_revealed_nodes_are_not_fog_candidates_on_later_floors',
    'tests.test_run_config.RunConfigTests.test_settings_survive_missing_pages_restart_and_only_manual_reset_clears_them',
    'tests.test_adaptive_recognition',
    'tests.test_capture_queue',
    'tests.test_dynamic_resolution',
    'tests.test_empty_inventory',
    'tests.test_map_clearing',
    'tests.test_map_templates',
    'tests.test_recognition',
    'tests.test_recognition_reuse',
    'tests.test_relic_recognition_022',
    'tests.test_run_badges',
    'tests.test_enemy_environment.EnemyEnvironmentTests.test_visible_region_updates_and_survives_partial_pages_and_restart',
    'tests.test_node_content.NodeContentTests.test_fixed_and_revealed_same_slot_count_once_and_exhaust_type_budget',
    'tests.test_node_content.NodeContentTests.test_event_same_title_and_description_preserve_ambiguous_scene_ids',
    'tests.test_node_content.NodeContentTests.test_confirmed_low_difficulty_rejects_fog_on_template_exit',
    'tests.test_node_content.NodeContentTests.test_visible_selected_battle_binds_stage_to_selection_not_current_position',
    'tests.test_node_content.NodeContentTests.test_fixed_first_floor_merchants_do_not_create_extra_random_merchants',
    'tests.test_node_content.NodeContentTests.test_two_battle_nodes_keep_different_stage_titles_across_fog_and_restart',
    'tests.test_numeric_recognition_024.NumericRecognition024Tests.test_live_capture_has_zero_items_and_six_upright_operators',
    'tests.test_numeric_recognition_024.NumericRecognition024Tests.test_multicard_and_roster_still_supply_observed_counts_and_skill_ranks',
    'tests.test_run_config.RunConfigTests.test_current_run_info_confirms_difficulty_and_strengthened_trade_squad',
)


# Complete post290 modules append after the preserved original selector union.
ADDITIONAL_MODULES = ('tests.test_battle_entry_compatibility_299', 'tests.test_battle_entry_integration_296', 'tests.test_battle_entry_reference_view_296', 'tests.test_battle_event_references_296', 'tests.test_curiosity_node_rules_304', 'tests.test_curiosity_node_rules_view_304', 'tests.test_direct_landmark_294', 'tests.test_direct_landmark_303', 'tests.test_documented_choice_item_view_295', 'tests.test_documented_choice_items_295', 'tests.test_documented_item_integration_295', 'tests.test_event_node_requirements_298', 'tests.test_event_node_requirements_integration_298', 'tests.test_event_node_requirements_view_298', 'tests.test_event_preview_filters_292', 'tests.test_expedition_integration_297', 'tests.test_expedition_results_297', 'tests.test_expedition_results_view_297', 'tests.test_future_region_effects_300', 'tests.test_future_region_effects_view_300', 'tests.test_future_region_integration_300', 'tests.test_named_reward_integration_301', 'tests.test_named_reward_items_301', 'tests.test_named_reward_items_view_301', 'tests.test_peace_guardian_integration_291', 'tests.test_peace_guardian_results_291', 'tests.test_resident_location_references_291', 'tests.test_resident_reference_signals_291', 'tests.test_resting_corner_results_293', 'tests.test_resting_corner_view_293', 'tests.test_ritual_weakening_302', 'tests.test_ritual_weakening_integration_302', 'tests.test_ritual_weakening_view_302', 'tests.test_spawn_candidates_299', 'tests.test_spawn_candidates_integration_299', 'tests.test_spawn_candidates_view_299', 'tests.test_stage_entry_configuration_296', 'tests.test_relic_exchange_flow_305', 'tests.test_relic_exchange_flow_view_305', 'tests.test_enemy_form_reference_306', 'tests.test_enemy_form_view_306')
ADDITIONAL_MODULES += ('tests.test_choice_annotations_307', 'tests.test_choice_annotation_view_307', 'tests.test_annotation_presentation_pairs_307')
ADDITIONAL_MODULES += ('tests.test_direct_landmark_308',)
ADDITIONAL_MODULES += ('tests.test_boss_phase_reference_309', 'tests.test_boss_phase_view_309', 'tests.test_boss_phase_integration_309')
ADDITIONAL_MODULES += ('tests.test_boss_cycle_reference_310', 'tests.test_boss_cycle_view_310', 'tests.test_boss_cycle_integration_310')
ADDITIONAL_MODULES += ('tests.test_boss_hunt_reference_311', 'tests.test_boss_hunt_view_311', 'tests.test_boss_hunt_integration_311')
ADDITIONAL_MODULES += ('tests.test_gold_boss_reference_312', 'tests.test_gold_boss_view_312', 'tests.test_gold_boss_integration_312')
ADDITIONAL_MODULES += ('tests.test_expansion_reference_313', 'tests.test_expansion_view_313', 'tests.test_expansion_integration_313')
ADDITIONAL_MODULES += ('tests.test_current_battle_reference_314', 'tests.test_current_battle_view_314', 'tests.test_current_battle_integration_314')
ADDITIONAL_MODULES += ('tests.test_current_reward_reference_315', 'tests.test_current_reward_view_315', 'tests.test_current_reward_integration_315')

ADDITIONAL_MODULES += ('tests.test_ending_event_reference_316', 'tests.test_ending_event_view_316')

ADDITIONAL_MODULES += ('tests.test_current_stage_directory_317', 'tests.test_current_stage_directory_view_317', 'tests.test_current_stage_directory_integration_317')

ADDITIONAL_MODULES += ('tests.test_current_settlement_reference_318', 'tests.test_current_settlement_view_318', 'tests.test_current_settlement_integration_318')

ADDITIONAL_MODULES += ('tests.test_current_map_position_319', 'tests.test_current_map_position_view_319', 'tests.test_current_map_position_integration_319')

ADDITIONAL_MODULES += ('tests.test_current_action_positions_320', 'tests.test_current_action_positions_view_320')
ADDITIONAL_MODULES += ('tests.test_documented_event_flows_321', 'tests.test_documented_event_flow_view_321')
ADDITIONAL_MODULES += ('tests.test_box_event_reference_322', 'tests.test_box_event_view_322')
ADDITIONAL_MODULES += ('tests.test_current_exchange_reference_323', 'tests.test_current_exchange_view_323')
ADDITIONAL_MODULES += ('tests.test_current_ritual_reference_324', 'tests.test_current_ritual_view_324')
ADDITIONAL_MODULES += ('tests.test_current_sand_reference_325', 'tests.test_current_sand_view_325')
ADDITIONAL_MODULES += ('tests.test_current_event_battles_326', 'tests.test_current_event_battles_view_326')
ADDITIONAL_MODULES += ('tests.test_current_encounters_327', 'tests.test_current_encounters_view_327')
ADDITIONAL_MODULES += ('tests.test_current_lake_328', 'tests.test_current_lake_view_328')
ADDITIONAL_MODULES += ('tests.test_current_resource_events_329', 'tests.test_current_resource_events_view_329')
ADDITIONAL_MODULES += ('tests.test_current_unattended_shop_330', 'tests.test_current_unattended_shop_view_330')
ADDITIONAL_MODULES += ('tests.test_current_rest_travel_331', 'tests.test_current_rest_travel_view_331')
ADDITIONAL_MODULES += ('tests.test_current_node_readers_332', 'tests.test_current_node_readers_view_332')
ADDITIONAL_MODULES += ('tests.test_current_vine_events_333', 'tests.test_current_vine_events_view_333')
ADDITIONAL_MODULES += ('tests.test_current_cave_334', 'tests.test_current_cave_view_334')
ADDITIONAL_MODULES += ('tests.test_current_lone_dog_335', 'tests.test_current_lone_dog_view_335')
ADDITIONAL_MODULES += ('tests.test_current_memory_tree_336', 'tests.test_current_memory_tree_view_336')
ADDITIONAL_MODULES += ('tests.test_current_map_markers_337', 'tests.test_current_map_markers_view_337')
ADDITIONAL_MODULES += ('tests.test_current_reward_origins_338', 'tests.test_current_reward_origins_view_338')
ADDITIONAL_MODULES += ('tests.test_current_exit_339', 'tests.test_current_exit_view_339')
ADDITIONAL_MODULES += ('tests.test_current_agency_340', 'tests.test_current_agency_view_340')
ADDITIONAL_MODULES += ('tests.test_current_portal_341', 'tests.test_current_portal_view_341')
ADDITIONAL_MODULES += ('tests.test_current_scout_342', 'tests.test_current_scout_view_342')
ADDITIONAL_MODULES += ('tests.test_current_peace_343', 'tests.test_current_peace_view_343')
ADDITIONAL_MODULES += ('tests.test_current_reconstruction_344', 'tests.test_current_reconstruction_view_344')
ADDITIONAL_MODULES += ('tests.test_current_resting_345', 'tests.test_current_resting_view_345')
ADDITIONAL_MODULES += ('tests.test_current_shadow_346', 'tests.test_current_shadow_view_346')
ADDITIONAL_MODULES += ('tests.test_current_named_reward_origins_347', 'tests.test_current_named_reward_origins_view_347')
ADDITIONAL_MODULES += ('tests.test_boss_map_markers_348', 'tests.test_boss_map_markers_view_348')
ADDITIONAL_MODULES += ('tests.test_current_critical_reward_origins_349', 'tests.test_current_critical_reward_origins_view_349')
ADDITIONAL_MODULES += ('tests.test_current_startup_350', 'tests.test_current_startup_view_350')
ADDITIONAL_MODULES += ('tests.test_current_enemy_traits_351', 'tests.test_current_enemy_traits_view_351')
ADDITIONAL_MODULES += ('tests.test_common_content_352',)
ADDITIONAL_MODULES += ('tests.test_current_terrain_353', 'tests.test_current_terrain_view_353')
ADDITIONAL_MODULES += ('tests.test_current_recruit_tickets_354', 'tests.test_current_recruit_tickets_view_354')
ADDITIONAL_MODULES += ('tests.test_current_spawn_candidates_355', 'tests.test_current_spawn_candidates_view_355')
ADDITIONAL_MODULES += ('tests.test_current_bank_356', 'tests.test_current_bank_view_356')
ADDITIONAL_MODULES += ('tests.test_current_real_domain_357', 'tests.test_current_real_domain_view_357')
ADDITIONAL_MODULES += ('tests.test_current_portal_rules_358', 'tests.test_current_portal_rules_view_358')

def source_hashes():
    files = [*ROOT.glob('rouge/**/*.py'), *ROOT.glob('rouge/data/**/*.json'),
             *ROOT.glob('tests/test_*.py'), *ROOT.glob('scripts/**/*.py'),
             ROOT / 'tests/player_presentation_legacy_307.py',
             ROOT / 'CORE_0.70_VERIFICATION.json']
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def unmigrated_path(path):
    resolved = Path(path).resolve()
    return any(resolved.is_relative_to((ROOT / folder).resolve())
               for folder in ('.cache', 'samples/native-client'))


SYMLINK_PREREQUISITE_TESTS = frozenset({
    'tests.test_persistence_temporary_no_clobber_261.TemporaryRecordNoClobberTests.' + name
    for name in ('test_dangling_temporary_symlink_does_not_create_the_target',
                 'test_live_temporary_symlink_does_not_write_its_original_target',
                 'test_private_directory_name_collision_never_enters_an_old_namespace')
} | {
    'tests.test_restore_public_validation_inputs_261.PublicSourceIndex261Tests.'
    'test_unsafe_paths_symlinks_and_existing_receipts_are_preserved',
    'tests.test_persistence_initial_install.InitialInstallTests.'
    'test_manual_reset_retains_relative_link_text_and_target_resolution',
    'tests.test_persistence_initial_install.InitialInstallTests.'
    'test_raced_dangling_link_after_missing_load_survives_first_save',
})


def probe_windows_symlink_prerequisite():
    """Actual same-kind prerequisite only; never change privileges or substitute a link."""
    if sys.platform != 'win32':
        return {'platform': platform.system(), 'attempted': False, 'available': None}
    folder = Path(tempfile.mkdtemp(prefix='rouge-public-symlink-prerequisite-')).resolve()
    assert folder.parent == Path(tempfile.gettempdir()).resolve()
    link = folder / 'public-link'; target = folder / 'public-absent-target'
    record = {'platform': 'Windows', 'attempted': True, 'available': None,
              'system_configuration_changed': False, 'private_state_used': False}
    try:
        link.symlink_to(target.name)
        record['available'] = link.is_symlink() and link.readlink() == Path(target.name)
    except OSError as exc:
        record.update(winerror=getattr(exc, 'winerror', None), errno=exc.errno,
                      reason=str(exc), exception_type=type(exc).__name__)
        if getattr(exc, 'winerror', None) == 1314:
            record['available'] = False
    finally:
        if link.is_symlink():
            link.unlink()
        # Only the two owned leaf names are inspected. No recursive removal.
        assert not target.exists() and not link.exists()
        folder.rmdir()
    return record


class AvailableResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unavailable = []
        self.passed_count = 0
        self.unavailable_parents = set()
        self.native_symlink_prerequisite = probe_windows_symlink_prerequisite()

    def symlink_prerequisite_unavailable(self, test, reported_test, err):
        exc = err[1]
        proof = self.native_symlink_prerequisite
        if not (sys.platform == 'win32' and proof.get('available') is False
                and proof.get('winerror') == 1314
                and isinstance(exc, OSError) and getattr(exc, 'winerror', None) == 1314
                and test.id() in SYMLINK_PREREQUISITE_TESTS):
            return False
        frames = []
        tb = err[2]
        while tb is not None:
            frames.append(tb.tb_frame)
            tb = tb.tb_next
        # A product failure or a merely similar message must remain an error.
        # Require the actual pathlib→os.symlink creation frame and original test.
        if not any(f.f_code is Path.symlink_to.__code__ for f in frames):
            return False
        if any(Path(f.f_code.co_filename).resolve().is_relative_to(ROOT / 'rouge')
               for f in frames):
            return False
        test_method = test.id().rsplit('.', 1)[-1]
        if not any(f.f_code.co_name == test_method and
                   Path(f.f_code.co_filename).resolve().is_relative_to(ROOT / 'tests')
                   for f in frames):
            return False
        self.unavailable_parents.add(test.id())
        self.unavailable.append({'test': reported_test.id(),
            'kind': 'native_symlink_privilege_prerequisite', 'reason': str(exc),
            'winerror': 1314, 'errno': exc.errno,
            'traceback': ''.join(traceback.format_exception(*err)),
            'actual_prerequisite_creation_attempted': proof['attempted'],
            'actual_test_creation_attempted': True, 'counted_as_passed': False})
        if self.dots:
            self.stream.write('U'); self.stream.flush()
        return True

    def addSuccess(self, test):
        if test.id() not in self.unavailable_parents:
            self.passed_count += 1
            super().addSuccess(test)

    def addError(self, test, err):
        if self.symlink_prerequisite_unavailable(test, test, err):
            return
        exc = err[1]
        missing = getattr(exc, 'filename', None)
        if isinstance(exc, FileNotFoundError) and missing and unmigrated_path(missing):
            self.unavailable_parents.add(test.id())
            self.unavailable.append({'test': test.id(), 'kind': 'unmigrated_cache',
                                     'reason': str(exc)})
            if self.dots:
                self.stream.write('U'); self.stream.flush()
            return
        wrapped = re.search(r"ModuleNotFoundError: No module named '([^']+)'", str(exc)) if type(test).__name__ == '_FailedTest' else None
        module_name = exc.name if isinstance(exc, ModuleNotFoundError) else (wrapped.group(1) if wrapped else None)
        if module_name and module_name.split('.')[0] in (
                'PySide6', 'PIL', 'rapidocr_onnxruntime', 'win32gui', 'win32process',
                'win32api', 'windows_capture'):
            self.unavailable_parents.add(test.id())
            self.unavailable.append({'test': test.id(), 'kind': 'environment_dependency',
                                     'reason': str(exc)})
            if self.dots:
                self.stream.write('U'); self.stream.flush()
            return
        super().addError(test, err)

    def addSubTest(self, test, subtest, err):
        if err is not None and self.symlink_prerequisite_unavailable(test, subtest, err):
            return
        if err is not None and isinstance(err[1], FileNotFoundError):
            missing = getattr(err[1], 'filename', None)
            if missing and unmigrated_path(missing):
                self.unavailable_parents.add(test.id())
                self.unavailable.append({'test': subtest.id(), 'kind': 'unmigrated_cache',
                                         'reason': str(err[1])})
                # The parent remains unavailable even when other subtests pass.
                if self.dots:
                    self.stream.write('U'); self.stream.flush()
                return
        super().addSubTest(test, subtest, err)


ADDITIONAL_MODULES += ('tests.test_current_regions_359', 'tests.test_current_region_view_359')

ADDITIONAL_MODULES += ('tests.test_current_upgrade_tickets_360', 'tests.test_current_upgrade_tickets_view_360')

ADDITIONAL_MODULES += ('tests.test_current_legacy_361', 'tests.test_current_legacy_view_361')

ADDITIONAL_MODULES += ('tests.test_current_settlement_modes_362', 'tests.test_current_settlement_modes_view_362')

ADDITIONAL_MODULES += ('tests.test_current_non_event_origins_363', 'tests.test_current_non_event_origins_view_363')

ADDITIONAL_MODULES += ('tests.test_current_initial_recruit_364', 'tests.test_current_initial_recruit_view_364')

ADDITIONAL_MODULES += ('tests.test_current_hanko_365', 'tests.test_current_hanko_view_365')

ADDITIONAL_MODULES += ('tests.test_current_elbert_366', 'tests.test_current_elbert_view_366')

ADDITIONAL_MODULES += ('tests.test_current_cannot_367', 'tests.test_current_cannot_view_367')

ADDITIONAL_MODULES += ('tests.test_current_sun_boss_368', 'tests.test_current_sun_boss_view_368')

ADDITIONAL_MODULES += ('tests.test_current_boss_documents_369', 'tests.test_current_boss_documents_view_369')

ADDITIONAL_MODULES += ('tests.test_current_enemy_stage_index_370', 'tests.test_current_enemy_stage_index_view_370')

ADDITIONAL_MODULES += ('tests.test_current_enemy_spawns_371', 'tests.test_current_enemy_spawns_view_371')

ADDITIONAL_MODULES += ('tests.test_current_event_directory_372', 'tests.test_current_event_directory_view_372')

def maintained_selectors():
    """Original maintained ordered union, then all explicit post290 additions."""
    historical = json.loads((ROOT / 'CORE_0.70_VERIFICATION.json').read_bytes())
    from verify_cloud import MODULES
    original = list(dict.fromkeys(historical['test_modules'] + list(NEW_MODULES) + list(MODULES)))
    return list(dict.fromkeys(original + list(ADDITIONAL_MODULES)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--wine', action='store_true', help='Label Windows binaries run via Wine')
    parser.add_argument('--require-complete', action='store_true')
    parser.add_argument('--verbosity', type=int, choices=(1, 2), default=1,
                        help='Use 2 to record each test ID while a long run is in progress')
    args = parser.parse_args()
    before = source_hashes()
    historical = json.loads((ROOT / 'CORE_0.70_VERIFICATION.json').read_text(encoding='utf-8'))
    # Pick up future cloud selectors automatically as the project advances.
    selectors = maintained_selectors()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.with_suffix('.log').open('x', encoding='utf-8') as log:
        result = unittest.TextTestRunner(stream=log, verbosity=args.verbosity,
            resultclass=AvailableResult).run(unittest.defaultTestLoader.loadTestsFromNames(selectors))
    # Explicitly destroy the real Qt application after every assertion has run.
    # Record failure and retain the ordinary process exit; never bypass teardown.
    from qt_verification_cleanup import shutdown_verification_qt
    try:
        qt_shutdown = shutdown_verification_qt()
        qt_shutdown_error = None
    except Exception as error:
        qt_shutdown = None
        qt_shutdown_error = repr(error)
    after = source_hashes()
    drift = [name for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)]
    unavailable_parents = result.unavailable_parents
    receipt = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'platform': ('Windows' if sys.platform == 'win32' else platform.system()), 'wine_compatibility': args.wine,
        'verbosity': args.verbosity,
        'native_windows_integration_verified': False,
        'available_checks_passed': result.wasSuccessful() and not drift and qt_shutdown_error is None,
        'complete_repository_validation': result.wasSuccessful() and not drift and qt_shutdown_error is None and not result.unavailable,
        'qt_shutdown': qt_shutdown, 'qt_shutdown_error': qt_shutdown_error,
        'tests_run': result.testsRun, 'tests_passed': result.passed_count,
        'historical_or_declared_skips': len(result.skipped),
        'failures': len(result.failures), 'errors': len(result.errors),
        'unavailable_records': len(result.unavailable),
        'unavailable_parent_count': len(unavailable_parents),
        'native_symlink_prerequisite': result.native_symlink_prerequisite,
        'unavailable': result.unavailable,
        'failed_cases': [{'test': t.id(), 'reason': e.splitlines()[-1]}
                         for t, e in result.failures + result.errors],
        'skips': [{'test': t.id(), 'reason': why} for t, why in result.skipped],
        'selectors': selectors, 'source_sha256': before, 'source_drift': drift,
        'scope': 'All maintained offline selectors; absent migrated evidence is unavailable, not passed; no game or chat actions',
    }
    with args.output.open('x', encoding='utf-8') as out:
        json.dump(receipt, out, ensure_ascii=False, indent=2); out.write('\n')
    print(json.dumps({key: receipt[key] for key in (
        'available_checks_passed', 'complete_repository_validation', 'tests_run',
        'tests_passed', 'historical_or_declared_skips', 'failures',
        'errors', 'unavailable_records', 'source_drift')}, ensure_ascii=False))
    return 1 if not receipt['available_checks_passed'] else (2 if args.require_complete and result.unavailable else 0)


ADDITIONAL_MODULES += ('tests.test_current_stage_objects_373','tests.test_current_stage_objects_view_373')

ADDITIONAL_MODULES += ('tests.test_current_event_resources_374', 'tests.test_current_event_resources_view_374')

if __name__ == '__main__':
    sys.exit(main())

