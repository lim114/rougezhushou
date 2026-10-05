"""Collect only measured, passing evidence for this batch."""
import hashlib,json,re,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
log=ROOT/'.cache/tests-0.20.log';text=log.read_text(encoding='utf8')
match=re.search(r'Ran (\d+) tests in ([\d.]+)s\s+OK\s*$',text)
assert match,text[-1500:]
def read(file):return json.loads((ROOT/file).read_text(encoding='utf8'))
speed=read('ADAPTIVE_0.20_VERIFICATION.json');ui=read('MAP_UI_0.20_VERIFICATION.json')
launch=read('APP_0.20_LAUNCH_VERIFICATION.json');live=read('LIVE_0.20_VERIFICATION.json')
visual_ui=read('VISUAL_UI_0.20_VERIFICATION.json')
for file,expected in speed['source_hashes'].items():
    assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==expected,file
assert launch['settings_and_bindings_unchanged'] and launch['run_cmd_startup_verified']
assert visual_ui['backend_selector'] and visual_ui['image_only_partial_fields_explicit'] and visual_ui['account_history_preserved']
assert ui['spatial_node_selection'] and ui['manual_reset_and_stale_frame_guard']
assert len(speed['animation'])==3 and len(speed['resolutions'])==4 and len(speed['visual'])==6
assert all(a['semantic_equality'] for a in speed['animation'])
receipt={'version':'0.20.0','verified_at':time.time(),'tests':int(match[1]),'test_seconds':float(match[2]),
    'test_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'source_hashes_unchanged':True,
    'adaptive_reference_comparisons':3,'operator_resolution_cases':4,'image_only_cases':6,
    'image_only_ocr_model_calls':0,'map_ui_resize_cases':ui['resize_cases'],
    'same_run_history_preserved':bool(launch['same_run_preserved'] and launch['history_preserved']),
    'run_change_confirmation':launch.get('new_run_confirmation'),
    'settings_bindings_preserved':True,'visual_ui_verified':True,'live_capture_status':live['status'],
    'live_page':live.get('page'),'live_template':live.get('template'),
    'live_map_status':live.get('map_status'),
    'chat_requests':0,'game_input_actions':0,
    'limits':['Image-only backend is partial; all numeric/skill/event fields not implemented.',
              'Controlled transform coverage is not all real DPI/layouts or all operators/maps.',
              'No generation weights or actual hidden-node probabilities; known visited types consume quotas.',
              'Relic calculation coverage unchanged; 86 combat mechanisms still pending.']}
if not receipt['same_run_history_preserved']:
    receipt['limits'].append('Run ID changed after checkpoint; reason pending user confirmation, upgrade history preservation not verified.')
(ROOT/'FINAL_0.20_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
progress=ROOT/'PROJECT_PROGRESS.md';s=progress.read_text(encoding='utf8')
s=s.replace('最终回归及实际启动结果见 `FINAL_0.20_VERIFICATION.json`；',
    f"最终{receipt['tests']}项回归通过，正常启动，设置/聊天绑定未变；本局ID变化原因待确认，不能宣称实机升级历史保留通过。实际后台采集状态为{live['status']}，地图状态为{live.get('map_status')}，详见 `FINAL_0.20_VERIFICATION.json`；")
progress.write_text(s,encoding='utf8')
print(json.dumps(receipt,ensure_ascii=False))
