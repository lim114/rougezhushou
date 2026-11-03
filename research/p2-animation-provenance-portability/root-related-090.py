"""Fresh current checkout animation and friendly-clock regression."""
import sys,unittest
from pathlib import Path

repo=Path('/workspace/rougezhushou');sys.path.insert(0,str(repo))
import tests.test_original_animation_048 as old_animation
cache=repo/'.cache/research/timing-048/skeleton-downloads.json'
if not cache.exists():
 method=old_animation.OriginalAnimation048Tests.test_all_sources_match_pinned_skeleton_bytes_and_git_blob
 method.__unittest_skip__=True
 method.__unittest_skip_why__='Historical timing-048 cache absent; preserve unavailable evidence, do not recreate or download64 resources.'
modules=['tests.test_original_animation_provenance','tests.test_original_animation_048','tests.test_gummy_cooking_clock','tests.test_gummy_expected_clock','tests.test_next_attack_healing_reference','tests.test_friendly_scope_report','tests.test_gummy_back_animation_reference']
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
raise SystemExit(0 if result.wasSuccessful() else 1)
