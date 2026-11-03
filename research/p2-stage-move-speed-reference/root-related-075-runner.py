import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
modules=['tests.test_stage_move_speed_reference','tests.test_spawn_reference_040','tests.test_battle_preview_039','tests.test_enemy_environment','tests.test_enemy_rune_selectors','tests.test_shu_periodic_sp_reference']
unavailable={'test_all_options_and_extra_routes_match_pinned_levels','test_all_images_match_pinned_receipt','test_visible_region_updates_and_survives_partial_pages_and_restart'}
def flatten(suite):
    for test in suite:
        if isinstance(test,unittest.TestSuite):yield from flatten(test)
        else:yield test
tests=list(flatten(unittest.defaultTestLoader.loadTestsFromNames(modules)))
excluded=[x.id() for x in tests if x.id().rsplit('.',1)[-1] in unavailable]
assert len(excluded)==3
suite=unittest.TestSuite(x for x in tests if x.id().rsplit('.',1)[-1] not in unavailable)
print('Related selector excludes three known unavailable original fixture methods; full-075 reports them separately.',flush=True)
result=unittest.TextTestRunner(verbosity=1).run(suite)
assert not result.skipped
sys.exit(0 if result.wasSuccessful() else 1)
