"""Independent static/saved-evidence review. Performs no API, Qt or Wine calls."""
import ast
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

P = Path('/workspace/.continuation/ui-075-draft')
OUT = P / 'independent'
REPO = Path('/workspace/rougezhushou')
COMMIT = '225cb66dc89143a3cd3a884bd6c62f47ed9d36bc'
RUNNER_SHA = '645ebd2e90ab3aef1fa5c9318300bd5e690c5f1dd6cfb67f94ed74f355ca4f03'
BASE_SHA = '3bba0d28376165b84938906b45048f31b75d89cf6e1c4d1e5246d17f6272f9b3'
API_SHA = 'f3ce13a69c742bc78e8b1633781f098f412fc84338419c8f7bc485ad2c91ab28'
ACTUAL = Path('/workspace/.compat/wine-ui-075.json')
ACTUAL_SHA = 'cde597aa4e6582b7d50fed1240d40bde62d78fdbf0d849ac1efb6c84e5951d1f'
EXPECTED = {71:106,72:280,73:72,74:108,75:48}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read_json(path):
    return json.loads(path.read_bytes())

def load_public_helper(name):
    spec = importlib.util.spec_from_file_location('independent_' + name, P / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

raw = (P / 'wine-ui-smoke-075.py').read_bytes()
assert sha(raw) == RUNNER_SHA
text = raw.decode()
ast.parse(text)
base = (P / 'wine-ui-smoke-070-preserved.py').read_bytes()
assert sha(base) == BASE_SHA
assert base == Path('/workspace/.compat/wine-ui-smoke-070.py').read_bytes()
helpers = (P / 'public_contracts.py').read_text() + '\n' + (P / 'cases075.py').read_text()
fragment = (P / 'supplemental-checks.py.fragment').read_text()
assert text.count(fragment + '\n') == 1 and text.count(helpers + '\n\n') == 1
rebuilt = text.replace(fragment + '\n', '', 1).replace(helpers + '\n\n', '', 1)
for name in ('wine-ui-report-difference-070.json','wine-window-070.png','wine-ui-070.json',
             'wine-ui-failure-070.png','wine-sown-tile-control-070.png'):
    rebuilt = rebuilt.replace(name.replace('-070','-075'), name)
rebuilt = rebuilt.replace('-(current_end-current_start)', '')
wrapper = "        receipt['preserved_full_070_checks']=len(checks)\n        assert receipt['preserved_full_070_checks']==841,receipt['preserved_full_070_checks']\n"
assert rebuilt.count(wrapper) == 1
rebuilt = rebuilt.replace(wrapper, '', 1)
assert rebuilt.encode() == base
assert "receipt['section75_final_checks_pending']=False" in fragment
assert "receipt['section75_final_checks_pending']=True" not in text
assert 'from PySide6.QtWidgets import QDoubleSpinBox' in fragment

freeze = read_json(P / 'public-source-freeze-75.json')
assert freeze['commit'] == COMMIT and freeze['source_file_count'] == 125
assert freeze['gui_executed'] is False and freeze['wine_executed'] is False
assert len(freeze['source_files']) == 125
for name, meta in freeze['source_files'].items():
    content = (P / 'public-schema-75' / name).read_bytes()
    assert len(content) == meta['bytes'] and sha(content) == meta['sha256'], name
    blob = subprocess.run(['git','cat-file','blob',COMMIT + ':' + name], cwd=REPO,
                          check=True, stdout=subprocess.PIPE).stdout
    assert content == blob, name

case_module = load_public_helper('cases075')
contract = load_public_helper('public_contracts')
bundle = P / 'public-schema-75'
config = read_json(bundle / 'rouge/data/run-config.json')
battle = read_json(bundle / 'rouge/data/battle-previews.json')
planned = case_module.cases075(config['squads']) + case_module.preview_cases075(battle['stages'])
assert dict(Counter(row['section'] for row in planned)) == EXPECTED
for sid in ('ro6_n_3_6','ro6_e_3_6'):
    roster = battle['stages'][sid]['enemies']
    assert len(roster) == len({row['id'] for row in roster}) == 12

api_raw = (P / 'public-schema-final-75.json.gz').read_bytes()
assert sha(api_raw) == API_SHA
saved = json.loads(gzip.decompress(api_raw))
assert saved['calls'] == len(saved['records']) == len(planned) == 614
assert saved['gui_executed'] is False and saved['wine_executed'] is False
assert saved['source_drift'] == []
assert {int(k):v for k,v in saved['cases_by_section'].items()} == EXPECTED
e0 = {}
for design, row in zip(planned, saved['records'], strict=True):
    section = design['section']
    assert row['section'] == section
    if section == 75:
        assert row['input'] == design
        contract.require_movement075(row['preview'],row['visible_text'],design['technical'],
                                     battle['stages'][design['stage_id']])
        continue
    args = dict(design['input'])
    # The API preflight adds the actual visible S2 owner's default checkbox.
    # The pure design list leaves it implicit; reset_owner_options sets False.
    if args['operator'] == 'char_1035_wisdel' and args['skill'] == 2:
        args['overload'] = False
    assert row['input'] == args
    result = row['result']; report = row['human_report']
    if section == 71:
        contract.require_squad075(result,args,report,config['squads'][args['run_config']['squad']['id']])
    elif section == 72:
        key = (args['potential'],args['timing_mode'],args['drone_warmup_hits'])
        if args['elite'] == 0 and args['deployment_elapsed_seconds'] == 0:
            e0[key] = result
        contract.require_headwolf075(result,args,report,e0.get(key) if args['elite'] == 0 else None)
    elif section == 73:
        contract.require_mei075(result,args,report,args['elite'] == 2 and args['level'] >= 40,args['module_level'])
    elif section == 74:
        contract.require_wisdel_routes075(result,args,report)

# Static binding evidence: selection signals and finally cleanup belong to real Qt controls.
view = (bundle / 'rouge/battle_view.py').read_text()
app_source = (bundle / 'rouge/app.py').read_text()
for needle in ('self.stage_combo.currentIndexChanged.connect(self._stage_changed)',
               'self.enemy_combo.currentIndexChanged.connect(self.render_rows)',
               'self.technical.toggled.connect(self._technical_changed)',
               'self._load_stage(sid);self.stageSelected.emit(sid)'):
    assert needle in view
assert 'self.battle_preview.stageSelected.connect(self.select_battle_stage)' in app_source
assert 'self.target_stage_choices.select_value(sid)' in app_source
assert 'if hasattr(self,\'battle_preview\'):self.battle_preview.set_stage(sid)' in app_source
assert '._render' not in fragment
assert 'window.run.state=state075;window.operator_observations=account075' in fragment
assert 'window.use_run_training.setChecked(run_training075)' in fragment
assert 'window.difficulty.setCurrentIndex(difficulty075)' in fragment
assert 'preview075.technical.setChecked(technical075)' in fragment
assert 'window.target_stage_choices.select_value(stage075)' in fragment
assert 'window.target_enemy_choices.select_value(enemy075)' in fragment
assert 'window.centralWidget().setCurrentIndex(page075)' in fragment

# Read root's completed run as separately attributed evidence; this reviewer does not execute it.
actual_raw = ACTUAL.read_bytes()
assert sha(actual_raw) == ACTUAL_SHA
actual = json.loads(actual_raw)
assert actual['passed'] is True and actual['complete_ui_validation'] is True
assert actual['source_drift'] == []
assert actual['total_actual_checks'] == len(actual['checks']) == 1455
assert actual['preserved_full_070_checks'] == 841
assert actual['supplemental_checks_71_75'] == 614
assert {int(k):v for k,v in actual['supplemental_checks_by_section_71_75'].items()} == EXPECTED
assert actual['native_windows_verified'] is False
assert actual['game_captures'] == actual['chat_requests'] == 0
for name, meta in freeze['source_files'].items():
    assert actual['source_sha256'][name] == actual['source_sha256_after'][name] == meta['sha256'], name
qt75 = [row for row in actual['checks'] if row.get('scope') == 'actual_stage_enemy_combo_and_technical_movement_source_reference']
assert len(qt75) == 48 and all(row['passed'] is True for row in qt75)
assert [(r['stage_id'],r['enemy_id'],r['level'],r['technical']) for r in qt75] == [
       (r['stage_id'],r['enemy_id'],r['level'],r['technical']) for r in planned if r['section']==75]

receipt = {
 'status':'independent_static_review_passed', 'blockers':[],
 'reviewer_gui_executed':False,'reviewer_wine_executed':False,'reviewer_new_public_api_calls':0,
 'runner_sha256':RUNNER_SHA,'commit':COMMIT,'baseline070_sha256':BASE_SHA,
 'baseline841_full_source_reconstructed_exactly':True,'baseline_skills':87,'syntax_valid':True,
 'frozen_public_files_git_blob_verified':125,
 'case_design_by_section':EXPECTED,'new_case_design_count':614,'total_case_design_count':1455,
 'saved_api_contracts_rechecked':614,'saved_api_sha256':API_SHA,
 'saved_input_normalization':'36 Wisdel S2 records explicitly include overload=False, matching the owner checkbox default and reset_owner_options; pure design leaves this default implicit.',
 'root_actual_evidence':{'path':str(ACTUAL),'sha256':ACTUAL_SHA,'passed':True,
   'total_checks':1455,'new_checks':614,'section75_real_selection_checks':48,
   'elapsed_seconds':actual['elapsed_seconds'],'source_drift':[],
   'execution_attribution':'root; independent reviewer only read the completed receipt',
   'scope':'Current Wine/PySide6/Windows CPython environment; native Windows remains unverified'},
 'static_selection_review':{
   'real_stage_enemy_technical_signals':True,'direct_private_render_calls':False,
   'two_stages_each_12_unique_enemy_ids':True,
   'tuple_platform_question':{
     'finding':'The new enemy select_value path depends on Qt QVariant tuple lookup/rebuild representation.',
     'resolution':'Root current fixed645 actual Qt receipt passed all48 identity/currentData/body assertions. No v2 or rerun needed.',
     'remaining_boundary':'No claim for other Qt versions or native Windows.'}},
 'restoration_review':{
   'public_config_state_account_observations_run_training_summary_preset_restored':True,
   'target_stage_enemy_page_preview_technical_restored':True,
   'boundary':'Cultivation/module records are temporary readonly label observations. No squad/module selector, account unlock, actual activation, target air status or movement clock is certified.'},
 'artifact_hashes':{name:sha((P/name).read_bytes()) for name in (
   'public_contracts.py','cases075.py','supplemental-checks.py.fragment',
   'public-source-freeze-75.json','runner-075.patch')}
}
target = OUT / 'runner-review075.json'
target.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'receipt_sha256':sha(target.read_bytes()),
                  'saved_contracts_rechecked':614,'git_blob_verified':125,
                  'root_actual_checks_read':1455,'gui_executed_by_reviewer':False},ensure_ascii=False))
