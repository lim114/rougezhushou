"""Consolidate current-code validation, actual launch and fresh background capture."""
import json,hashlib,re,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def read(name):return json.loads((root/name).read_text(encoding='utf-8'))
log=(root/'.cache/tests-0.15.log').read_text(encoding='utf-8')
assert re.search(r'Ran 137 tests',log) and log.rstrip().endswith('OK')
batch=read('ENEMY_BATCH_VERIFICATION.json');rules=read('DIFFICULTY_0.15_VERIFICATION.json');ui=read('ENEMY_UI_VERIFICATION.json')
launch=read('APP_0.15_LAUNCH_VERIFICATION.json');live=read('ENVIRONMENT_0.15_LIVE_VERIFICATION.json')
assert rules['orb_skill_scenarios']==174 and batch['skill_profiles']==87
assert ui['unrelated_enemy_controls_hidden'] and ui['orb_unknown_default_and_no_state_leak']
assert launch['same_run_preserved'] and launch['history_preserved'] and launch['settings_and_bindings_unchanged']
assert live['running_app_matches_visible_config'] and live['same_run_preserved'] and live['foreground_unchanged'] and live['game_in_background']
assert all(r['chat_requests']==0 for r in (rules,batch,ui,launch,live))
assert (root/'.cache/launch-0.15.err.log').read_text(encoding='utf-8')==''
files=['rouge/enemy_environment.py','rouge/damage.py','rouge/operator_engine.py','rouge/estimate.py',
    'rouge/reporting.py','rouge/app.py','rouge/data/enemy-difficulty-rules.json','tests/test_difficulty_rules.py',
    'scripts/verify_enemy_ui.py','scripts/verify_difficulty_batch.py','BATCH_0.15.md','pyproject.toml']
receipt={'version':'0.15.0','verified_at':time.time(),'tests_passed':137,'skill_profiles':87,'orb_scenarios':174,
    'actual_background_region_and_difficulty':True,'same_run_and_history_preserved':True,
    'private_config_unchanged':True,'chat_requests':0,
    'source_hashes':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files},
    'limitations':rules['limitations']+['低难度与专属属性来自注明来源的机制资料，尚未逐难度实战验证。','其他动态敌人机制及未覆盖藏品仍明确标注。']}
(root/'FINAL_0.15_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print('0.15 verified: 137 tests, 87 skills, 174 orb scenarios; actual background capture; same run and private configuration retained')
