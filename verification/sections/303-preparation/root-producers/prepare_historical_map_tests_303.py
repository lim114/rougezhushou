from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'verification/sections/303-preparation/historical-tests/before'
pins={
 'tests/test_direct_landmark_294.py':'447b1d84f2eb40fce01e90a9145ce056ea85d21a1f2e399aab060bc2d7ebdfa0',
 'tests/test_map_projection_048.py':'c9055a58b2d02014c2e12c360e061c0cd7164cee7f4405e354bb7b2892625b2c',
}
for name,pin in pins.items():
    raw=(ROOT/name).read_bytes();assert sha256(raw).hexdigest()==pin
    target=base/name;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(raw)
plan={
 'section':303,'kind':'historical_input_compatibility_plan_before_new_data_or_formal_tests',
 'original_test_sha256':pins,
 '294':{'production_builder_changed':False,'reason':'Pure historical builder requires whole current input to equal its40/58 snapshot; append-only303 is not that historical input.',
  'planned_change':'Only setUpClass supplies an exact SHA-pinned public58 temporary snapshot to the unchanged original builder and its CLI. Keep all18 original test method ASTs and every assertion unchanged; actual current appended records are verified separately by303.',
  'private_data_or_runtime_current_replaced':False},
 '048':{'planned_change':'Only if n2_3 gains accepted direct points, migrate its old no-direct expectation to exact independently observed sparse centers; keep rejected plane, fallback-disabled unknown, original two8-point records and unresolved n3_5 assertions.',
  'actual_patch_not_applied':True},
 'actual_failure_or_new_validation_claimed':False,'original_sources_archived_before_any_change':True,
 'threshold_or_source_reading_adjusted':False}
target=base.parent/'plan.json';assert not target.exists();target.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'original_tests_archived':2,'production_or_tests_modified':False,'all_original294_methods_to_preserve':18}))
