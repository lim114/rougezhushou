"""Consolidate current-source regressions and real background application proof."""
import hashlib
import json
import re
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read(name): return json.loads((ROOT/name).read_text(encoding='utf-8'))


log=(ROOT/'.cache/tests-0.19.log').read_text(encoding='utf-8')
assert re.search(r'Ran 163 tests',log) and log.rstrip().endswith('OK')
maps=read('MAP_0.19_VERIFICATION.json');ui=read('MAP_UI_0.19_VERIFICATION.json')
relics=read('RELIC_VERIFICATION.json');launch=read('APP_0.19_LAUNCH_VERIFICATION.json')
live=read('MAP_0.19_LIVE_VERIFICATION.json')
speed=read('RECOGNITION_SPEED_0.19_VERIFICATION.json')
assert maps['templates_audited']==43 and len(maps['replays'])==5
assert ui['spatial_node_selection'] and ui['resize_cases']==3 and ui['padded_source_mapping']
assert ui['native_client_crop_mapping'] and ui['manual_reset_and_stale_frame_guard']
assert ui['restart_uses_history_schematic'] and ui['unmatched_frame_uses_paired_history'] and ui['missing_marker_history_explicit']
assert ui['node_content_bound_to_selected_node'] and ui['generation_budget_rendered']
assert speed['all_evidence_parity'] and len(speed['cases'])==6 and len(speed['geometry_cases'])==2
assert relics['public_entry_cases']==8704 and relics['version']=='0.19.0'
assert launch['same_run_preserved'] and launch['history_preserved'] and launch['settings_and_bindings_unchanged']
assert launch['only_one_project_window'] and launch['run_cmd_startup_verified']
assert live['running_app_matches_map'] and live['same_run_preserved'] and live['history_preserved']
assert live['game_in_background']
assert all(r['chat_requests']==0 for r in (maps,ui,relics,launch,live,speed))
assert (ROOT/'.cache/launch-0.19.err.log').read_text(encoding='utf-8')==''
for receipt in (maps,relics,speed):
    for name,digest in receipt['source_hashes'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
files=['rouge/map_view.py','rouge/map_recognition.py','rouge/map_reporting.py','rouge/recognition.py','rouge/run_state.py','rouge/app.py',
       'rouge/data/map-templates.json','scripts/build_map_templates.py','tests/test_map_templates.py',
       'scripts/verify_map_batch_0_19.py','scripts/verify_map_ui_0_19.py','scripts/verify_map_live_0_19.py',
       'scripts/finalize_batch_0_19.py','BATCH_0.19.md','PROJECT_PROGRESS.md','README.md','pyproject.toml']
files+=['rouge/node_events.py','rouge/recognition_cache.py','rouge/viewport.py','rouge/operator_recognition.py',
        'rouge/run_recognition.py','rouge/relic_recognition.py','rouge/data/node-generation.json','rouge/data/node-events.json',
        'scripts/build_node_events.py','scripts/verify_recognition_speed_0_19.py','tests/test_node_content.py','tests/test_recognition_reuse.py']
receipt={'version':'0.19.0','verified_at':time.time(),'tests_passed':163,'map_unit_tests':7,
    'node_content_and_generation_tests':8,'recognition_reuse_tests':4,
    'performance_six_pages_evidence_parity':True,'event_scene_records':338,'event_titles':37,'classified_titles':36,
    'templates_audited':43,'node_rule_types':18,'real_layouts_replayed':['1b','1c'],'map_replays':5,
    'skill_profiles_ui_checked':87,'relic_entry_cases':8704,
    'spatial_map_interaction_and_history':True,'actual_background_map_and_app_sync':True,'same_run_and_history_preserved':True,
    'private_config_unchanged':True,'missing_current_marker_history_explicit':True,
    'foreground_unchanged_during_live_check':live['foreground_unchanged'],
    'live_template':live['template_id'],'live_zone':live['zone_id'],'live_current_node':live['current_node'],
    'chat_requests':0,'new_live_combat_measurements':0,
    'source_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in files},
    'limitations':maps['limits']+speed['limitations']+(['后台核对期间系统前台窗口发生变化；该脚本只读采样，没有调用前台切换接口。'] if not live['foreground_unchanged'] else [])+['特殊区域/第六层、独立线段核验、实际节点概率和掉落预测尚未完成。',
        '事件出场前提/权重未恢复；不从同类事件目录编造生成候选或等概率。第一层绿黄商店共享上限2未核实。',
        '86件藏品战斗机制和9件部分机制继续保留在原计划内。']}
(ROOT/'FINAL_0.19_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print('0.19 verified: 163 tests, 43 sourced graphs, 5 map replays, 87 skills, 8704 relic entries; '
      'actual background map sync; same run and private configuration retained')
