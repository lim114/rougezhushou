from pathlib import Path
import sys,unittest,json,hashlib
ROOT=Path('/workspace/rougezhushou')
sys.path.insert(0,str(ROOT))
guard=json.loads(Path('/workspace/.continuation/root-source-095.json').read_bytes())
assert guard['passed'] is True
for rel,expected in guard['source_sha256_after'].items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected
names=(
 'tests.test_selected_module_source_reference',
 'tests.test_report','tests.test_module_qualification_notes',
 'tests.test_mei_airborne_module_reference','tests.test_drone_traits',
 'tests.test_gnosis_isw_a_reference','tests.test_mizuki_amb_y_reference',
 'tests.test_haruka_healing_targets','tests.test_haruka_bubble_talent_qualification',
 'tests.test_summon_modules_038','tests.test_summon_limits_069',
 'tests.test_wang_token_module_reference','tests.test_amiya_module_healing_trait',
 'tests.test_amiya_regeneration_talent_qualification',
)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
for rel,expected in guard['source_sha256_after'].items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected
raise SystemExit(0 if result.wasSuccessful() and result.testsRun>0 else 1)
