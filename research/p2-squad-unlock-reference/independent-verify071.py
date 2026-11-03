"""Strict saved-outcome and patch/source review; never rewrites author artifacts."""
from copy import deepcopy
import ast
import collections
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).parent
BASE = ROOT / 'baseline'
DRAFT = ROOT / 'draft071'


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


expected_hashes = {
    'rouge/run_modifiers.py':'c0f5de967ff160ad4ad3ad4a4823a7da158386c537297c7d032248823fe4586e',
    'rouge/reporting.py':'cad245e936cc83f5467215eedff37d3054d48d0bb2f81dd4363004c3ccbf4a0a',
    'rouge/squad_unlock_reference.py':'5ff9929aa0e01c60d3da75d26c5531384b01aab7c0123d17c6ee7c2b21429b73',
}
assert sha(ROOT / 'section71.patch') == 'b7003b715318a7ac8d01413aaed2fce0532cf8a57cd41182e32d2bbe8dcddff6'
for name, digest in expected_hashes.items():
    assert sha(DRAFT / name) == digest
patch_text = (ROOT / 'section71.patch').read_text()
test_name = 'tests/test_squad_unlock_reference.py'
assert sha(ROOT / 'test_squad_unlock_reference.py') == '3f15fa41abdb0244d9ad9f3ffd2e2b959de3d675586c9838bb13027bc00a3ece'
assert set(line.split(' b/')[1] for line in patch_text.splitlines() if line.startswith('diff --git ')) == set(expected_hashes) | {test_name}
check_dir = ROOT / 'independent-patch-check071'
for name in ('rouge/run_modifiers.py', 'rouge/reporting.py'):
    path = check_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(BASE / name, path)
assert not (check_dir / 'rouge/squad_unlock_reference.py').exists()
checked = subprocess.run(['git','apply','--check',str(ROOT / 'section71.patch')],cwd=check_dir,capture_output=True,text=True)
assert checked.returncode == 0, checked.stderr
applied = subprocess.run(['git','apply',str(ROOT / 'section71.patch')],cwd=check_dir,capture_output=True,text=True)
assert applied.returncode == 0, applied.stderr
assert all((check_dir / name).read_bytes() == (DRAFT / name).read_bytes() for name in expected_hashes)
assert (check_dir / test_name).read_bytes() == (ROOT / 'test_squad_unlock_reference.py').read_bytes()
freeze = json.loads((ROOT / 'baseline-freeze.json').read_text())
for name in freeze['files']:
    if name not in ('rouge/run_modifiers.py','rouge/reporting.py'):
        assert (DRAFT / name).read_bytes() == (BASE / name).read_bytes(), name

source = json.loads((ROOT / 'independent-source-review071.json').read_text())
conditions = source['strengthened_conditions']
config = json.loads((BASE / 'rouge/data/run-config.json').read_text())
helper = ast.parse((DRAFT / 'rouge/squad_unlock_reference.py').read_text())
mapping = next(ast.literal_eval(n.value) for n in helper.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id == '_TECHNOLOGY_IDS')
assert mapping == {key:value['technology_id_by_exact_forward_and_reverse_text'] for key,value in conditions.items() if value['technology_id_by_exact_forward_and_reverse_text']}


def expected_reference(squad):
    original = conditions[squad]
    node = original['original_node']
    gate = original['original_gate']
    node_id = original['technology_id_by_exact_forward_and_reverse_text']
    technology = None if node is None else {
        'id':node_id,'name':node['buffName'],'node_type':node['nodeType'],
        'effect_text_reference':node['rawDesc'],
        'source_selector':'$.customizeData.rogue_6.commonDevelopment.developments.'+node_id,
        'gate_reference':None if gate is None else {
            'enable_grade_parameter':gate['enableGrade'],
            'enable_description_reference':gate['enableDesc'],
            'source_selector':'$.customizeData.rogue_6.commonDevelopment.developmentsDifficultyNodeInfos.'+node_id},
    }
    return {'squad_id':squad,'base_squad_id':original['variant']['normalBandId'],
        'variant_level_parameter':1,'unlock_condition_reference':original['original_condition'],
        'technology_node_reference':technology,'account_unlocked':None,'actual_activation':None,'reference_only':True,
        'source':{'url':config['source_url'],'sha256':config['source_sha256'],'commit':config['commit'],
                  'condition_selector':original['condition_selector'],
                  'variant_selector':'$.details.rogue_6.bandRef.'+squad}}


def compare(before, after):
    assert len(before['records']) == len(after['records'])
    counts = collections.Counter()
    for old,new in zip(before['records'],after['records']):
        assert old['request'] == new['request']
        for row in (old,new):
            if 'full_result' in row:
                assert hashlib.sha256(canonical(row['full_result']).encode()).hexdigest() == row['full_result_sha256']
        request = old['request']
        squad = ((request.get('run_config') or {}).get('squad') or {}).get('id')
        if 'error' in old:
            assert new.get('error') == old['error'] and 'full_result' not in new
            counts['prior_complete_errors_unchanged'] += 1
        elif squad in conditions:
            trimmed = deepcopy(new['full_result'])
            reference = trimmed['run_resolution'].pop('squad_unlock_reference')
            assert reference == expected_reference(squad)
            sections = trimmed['report']['sections']
            added = [section for section in sections if section['id']=='squad_unlock_reference']
            assert len(added) == 1
            assert {row['key']:row['value'] for row in added[0]['metrics']} == {'account_unlock':None,'activation':None}
            assert added[0]['title'] == '强化分队 · 条件资料'
            trimmed['report']['sections'] = [section for section in sections if section['id']!='squad_unlock_reference']
            assert trimmed == old['full_result']
            counts['only_new_source_reference_and_report_section'] += 1
        else:
            assert new.get('full_result') == old['full_result'] and 'error' not in new
            counts['full_json_unchanged'] += 1
    return dict(counts)


author_before = json.loads((ROOT / 'baseline-results071.json').read_text())
author_after = json.loads((ROOT / 'draft-results071.json').read_text())
assert author_before['public_calls'] == author_after['public_calls'] == 1264
assert author_before['caller_and_catalog_run_config_technology_cache_preserved'] is True
assert author_after['caller_and_catalog_run_config_technology_cache_preserved'] is True
author_counts = compare(author_before,author_after)
assert author_counts == {'full_json_unchanged':365,'only_new_source_reference_and_report_section':843,'prior_complete_errors_unchanged':56}
own_before = json.loads((ROOT / 'independent-baseline-results071.json').read_text())
own_after = json.loads((ROOT / 'independent-draft-results071.json').read_text())
assert own_before['calls'] == own_after['calls'] == 127
assert own_before['caller_and_caches_unchanged'] is True and own_after['caller_and_caches_unchanged'] is True
own_counts = compare(own_before,own_after)
assert own_counts == {'only_new_source_reference_and_report_section':76,'full_json_unchanged':34,'prior_complete_errors_unchanged':17}
for row in own_after['records']:
    if row['request'].get('four_sui') and 'full_result' in row:
        result = row['full_result']
        ref = result['shu_periodic_sp_reference']
        assert ref['events_scheduled'] is False
        assert result['estimate']['skill']['sp_recovery_per_second'] == 1
        assert all(ref[key] is None for key in ('first_tick_seconds','actual_tick_times_seconds','clock_origin','reset_rule','blocked_credit_rule'))
        if row['request']['window_seconds'] == 0:
            assert result['total_damage'] == result['total_healing'] == 0

report = {
    'status':'independent_review_passed', 'blockers':[],
    'baseline_commit':source['baseline_commit'],
    'patch_sha256':sha(ROOT / 'section71.patch'),
    'patch_reconstructed_three_exact_source_files':True,
    'patch_reconstructed_exact_new_test_file':True,
    'unchanged_baseline_public_files_in_draft':2177,
    'independent_source_checked_baseline_git_blobs':2179,
    'raw_topic_sha256':source['raw_sha256'],
    'complete_squad_source_records':22,'strengthened_conditions':7,'exact_bidirectional_technology_links':6,
    'complete_technology_nodes':57,'difficulty_reference_gates':3,
    'fresh_independent_paired_scenarios':127,'fresh_independent_public_calls':254,
    'fresh_independent_counts':own_counts,
    'author_saved_pairs_strictly_recompared':1264,'author_prior_calls_not_rerun':2528,
    'author_saved_counts':author_counts,
    'independent_new_tests':9,'independent_new_tests_passed':9,
    'author_related_tests':{'ran':59,'passed':58,'skipped_missing_committed_public_screenshot':1},
    'bounded_scope':'Only original strengthened-squad unlock-condition and matching technology/gate references plus one report section are added. Exact current explicit effect confirmation, identity, mode, qualification, formulas, SP clocks, scope, errors and all other JSON remain unchanged.',
    'known_unknowns':['Account unlock state','Actual condition activation','Prerequisite AND/OR behavior','Runtime outbuff binding and attribute layers','Mode execution semantics'],
    'no_tracked_edits':True,'no_private_state_reads':True,'no_wine_or_gui':True,
    'changed_source_hashes':expected_hashes,
    'artifact_sha256':{name:sha(ROOT / name) for name in ('independent-source-review071.py','independent-source-review071.json','independent-probe071.py','independent-baseline-results071.json','independent-draft-results071.json','independent-new-tests071.log','independent-initial-patch-extractor-error071.json','independent-verify071.py','source-receipt071.json','baseline-results071.json','draft-results071.json','matrix-comparison071.json','test_squad_unlock_reference.py','section71.patch')},
}
output = ROOT / 'independent-review071.json'
output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'fresh_pairs':127,'fresh_calls':254,'fresh_counts':own_counts,
                  'saved_pairs':1264,'saved_counts':author_counts,'tests':9,'receipt_sha256':sha(output)},ensure_ascii=False))
