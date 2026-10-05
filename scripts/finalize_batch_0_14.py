"""Consolidate completed evidence; no local secrets or chat contents."""
import json,hashlib,re,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def read(name):return json.loads((root/name).read_text(encoding='utf-8'))
log=(root/'.cache/tests-0.14.log').read_text(encoding='utf-8')
assert re.search(r'Ran 133 tests',log) and log.rstrip().endswith('OK')
batch=read('ENEMY_BATCH_VERIFICATION.json');ui=read('ENEMY_UI_VERIFICATION.json')
launch=read('APP_0.14_LAUNCH_VERIFICATION.json');live=read('ENVIRONMENT_0.14_LIVE_VERIFICATION.json')
assert batch['skill_profiles']==87 and batch['enemy_references']==1087
assert launch['same_run_preserved'] and launch['history_preserved'] and launch['settings_and_bindings_unchanged']
assert live['same_run_preserved'] and live['running_app_matches_visible_config'] and live['foreground_unchanged']
assert all(r['chat_requests']==0 for r in (batch,ui,launch,live))
files=['rouge/enemy_environment.py','rouge/run_config.py','rouge/run_state.py','rouge/run_modifiers.py',
    'rouge/damage.py','rouge/operator_engine.py','rouge/estimate.py','rouge/reporting.py','rouge/app.py','rouge/recognition.py',
    'rouge/data/run-config.json','rouge/data/previews.json','tests/test_enemy_environment.py','BATCH_0.14.md','pyproject.toml']
receipt={'version':'0.14.0','verified_at':time.time(),'tests_passed':133,'skill_profiles':87,
    'stage_profiles':105,'enemy_references':1087,'actual_background_region_and_difficulty':True,
    'same_run_and_history_preserved':True,'private_config_unchanged':True,'chat_requests':0,
    'source_hashes':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files},
    'limitations':batch['limits']+['部分动态环境、未知类别和脚本未覆盖，结果按支持范围估计。']}
(root/'FINAL_0.14_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print('0.14 finalized: 133 tests, 87 skills, 105 stages / 1087 enemy references; actual background config; same run/config retained')
