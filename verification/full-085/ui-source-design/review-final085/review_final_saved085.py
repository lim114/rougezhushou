"""Final read-only proof over exact source bytes and saved results; no app imports."""
import ast
from collections import Counter
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
AUTHOR = HERE.parent
REPO = Path('/workspace/rougezhushou')
ROOT = '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
expected_runner_sha = sys.argv[1]

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
def save(name, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    with (HERE / name).open('xb') as out: out.write(raw)
    return sha(raw)
def copy(source, relative):
    raw = source.read_bytes()
    target = HERE / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as out: out.write(raw)
    assert source.read_bytes() == raw
    return {'source_path': str(source), 'archive_path': relative, 'bytes': len(raw), 'sha256': sha(raw)}

files = ['wine-ui-smoke-085.py', 'cases085.py', 'public_contracts.py',
    'supplemental-checks.py.fragment', 'build_runner.py', 'resume_public_schema085.py',
    'resume_remaining573085.py', 'reassert_saved581085.py', 'saved69-reassertion085.json',
    'saved581-reassertion085.json', 'check_public_schema085.py',
    'public-source-freeze-085.json', 'root-source-085-proof.json', 'root-context-085-preserved.json',
    'public-schema-final-085.json.gz', 'public-schema-final-085-summary.json']
snapshots = [copy(AUTHOR / name, 'final-source-and-result-snapshot/' + name) for name in files]
SNAP = HERE / 'final-source-and-result-snapshot'
runner = (SNAP / files[0]).read_bytes()
assert sha(runner) == expected_runner_sha
body = runner.decode()
old = (HERE / 'actual080-preserved.py').read_bytes()
assert sha(old) == 'c58ff7ac462e7a9aa457e4b59471a162cbf5c6daf58192f6b5a852901fcdcc98'
entry = "if __name__ == '__main__' and False:\n    raise RuntimeError('UI085 final source/schema are pending; no Qt execution is permitted')\n\n"
assert body.startswith(entry)
helpers = (SNAP / 'public_contracts.py').read_text() + '\n' + (SNAP / 'cases085.py').read_text()
fragment = (SNAP / 'supplemental-checks.py.fragment').read_text()
assert "receipt['sections83_85_final_checks_pending']=False" in fragment
assert "receipt['sections83_85_final_checks_pending']=True" not in body
assert body.count(helpers + '\n\n') == body.count(fragment + '\n') == 1
restored = body[len(entry):].replace(fragment + '\n', '', 1).replace(helpers + '\n\n', '', 1)
for name in ['wine-ui-report-difference-080.json', 'wine-window-080.png', 'wine-ui-080.json',
    'wine-ui-failure-080.png', 'wine-sown-tile-control-080.png', 'wine-movement-reference-080.png',
    'wine-medical-trait-080.png']:
    restored = restored.replace(name.replace('-080', '-085'), name)
for key in ['preserved_old_checks', 'preserved_full_060_checks', 'preserved_full_065_checks',
            'preserved_full_070_checks', 'preserved_full_075_checks']:
    line = next(line for line in old.decode().splitlines() if line.strip().startswith(f"receipt['{key}']=len(checks)"))
    assert restored.count(line + '-(group085_end-group085_start)') == 1
    restored = restored.replace(line + '-(group085_end-group085_start)', line, 1)
added = "        receipt['preserved_full_080_checks']=len(checks)-(group085_end-group085_start)\n        assert receipt['preserved_full_080_checks']==3063,receipt['preserved_full_080_checks']\n"
assert restored.count(added) == 1
assert restored.replace(added, '', 1).encode() == old
ast.parse(runner)
case_tree = ast.parse((SNAP / 'cases085.py').read_bytes())
assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(case_tree))
local = {}
exec(compile(case_tree, '<literal-local-designs>', 'exec'), local)
cases = local['cases085']()
assert cases == json.loads((HERE / 'initial-pure-cases085.json').read_bytes())
assert len(cases) == len({canonical(case) for case in cases}) == 1154
assert len({canonical(case['input']) for case in cases}) == 1086
assert Counter(case['section'] for case in cases) == {81:136,82:216,83:450,84:88,85:264}
helper_tree = ast.parse((SNAP / 'public_contracts.py').read_bytes())
definitions = [n for n in helper_tree.body if isinstance(n, ast.FunctionDef)]
old_definitions = {n.name for n in ast.parse(old).body if isinstance(n, ast.FunctionDef)}
assert not (old_definitions & {n.name for n in definitions})
assert all(not any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(fn)) for fn in definitions)
namespace = {'json':json}
exec(compile(ast.Module(body=definitions, type_ignores=[]), '<saved-only-contracts>', 'exec'), namespace)

initial = json.loads((HERE / 'initial-static-review085.json').read_bytes())
freeze = json.loads((SNAP / 'public-source-freeze-085.json').read_bytes())
proof = json.loads((SNAP / 'root-source-085-proof.json').read_bytes())
context = json.loads((SNAP / 'root-context-085-preserved.json').read_bytes())
assert freeze['base_commit'] == proof['root_commit'] == context['commit'] == ROOT
assert freeze['patches'] == [] and freeze['public_source_files'] == 125
assert freeze['base_source_sha256'] == freeze['source_sha256']
expected = initial['source723_hashes']
assert len(expected) == len(proof['files']) == len(context['source_sha256']) == 723
assert {row['source_path']: {'bytes':row['bytes'],'sha256':row['sha256']} for row in proof['files']} == expected
assert context['source_sha256'] == {name: row['sha256'] for name,row in expected.items()}
git_archive = subprocess.check_output(['git','archive','--format=tar',ROOT,*sorted(expected)],cwd=REPO)
public = {}
with tarfile.open(fileobj=io.BytesIO(git_archive)) as archive:
    for member in archive:
        if not member.isfile():continue
        raw = archive.extractfile(member).read()
        assert {'bytes':len(raw),'sha256':sha(raw)} == expected[member.name]
        if member.name.startswith('rouge/'):
            assert (AUTHOR/'public-schema-085'/member.name).read_bytes() == raw
            public[member.name] = raw
assert len(public) == 125
assert freeze['source_sha256'] == {name:sha(raw) for name,raw in public.items()}
assert set(freeze['source_sha256']) == {p.relative_to(AUTHOR/'public-schema-085').as_posix()
    for p in (AUTHOR/'public-schema-085'/'rouge').rglob('*') if p.is_file() and p.suffix in ('.py','.json')}
catalog = json.loads(public['rouge/data/catalog.json'])
options_tree = ast.parse(public['rouge/operator_options.py'])
options = next(ast.literal_eval(n.value) for n in options_tree.body if isinstance(n,ast.Assign)
    and any(isinstance(t,ast.Name) and t.id=='OPTIONS' for t in n.targets))
projection_tree = ast.parse((HERE/'audit_remaining_receivers085.py').read_bytes())
projection = next(n for n in projection_tree.body if isinstance(n,ast.FunctionDef) and n.name=='independent_json_factor')
factor_namespace = {'catalog':catalog}
exec(compile(ast.Module(body=[projection],type_ignores=[]),'<independent-JSON-projection>','exec'),factor_namespace)
factor = factor_namespace['independent_json_factor']

raw = (SNAP/'public-schema-final-085.json.gz').read_bytes()
payload = json.loads(gzip.decompress(raw))
rows = payload['records']
assert len(rows) == payload['calls'] == 1154
assert payload['root_commit'] == ROOT and payload['source_hashes'] == freeze['source_sha256']
assert payload['GUI_executed'] is False and payload['Wine_executed'] is False
assert payload['unique_requested_calculation_inputs'] == 1086
assert payload['case_design_records'] == 1154
assert payload['formatter_text_requests'] == 3390
assert payload['formatter_entry_counts'] == {'format_estimate':1130,'format_report_default':2260,'format_report_technical':1130}
assert payload['actual_formatter_function_entries'] == 4520
assert payload['source_drift'] == []
attribution=payload['actual_API_call_attribution']
assert attribution['first_preflight_calls']==69 and attribution['remaining_only_phase2_calls']==512
assert attribution['remaining_only_phase3_calls']==573 and attribution['total_actual_calls']==1154
assert attribution['previous_completed_case_request_repeated_for_retry']==0
assert attribution['old3063_cases_repeated']==0
assert attribution['same_problem_retry_count']=={'mechanist_top_healing_shape':1,'processed_enemy_id_key':1}
assert payload['external_contract_qualification_helper_calls_for_original_request_results']==480
assert payload['saved581_reassertion_qualification_data_helper_calls']==216
reassert69=json.loads((SNAP/'saved69-reassertion085.json').read_bytes())
reassert581=json.loads((SNAP/'saved581-reassertion085.json').read_bytes())
assert reassert69['application_API_calls']==reassert69['formatter_calls']==reassert69['qualification_helper_calls']==0
assert reassert581['API_calls']==reassert581['formatter_calls']==0
assert reassert581['external_contract_selected_talents_data_helper_calls']==216
summary = json.loads((SNAP/'public-schema-final-085-summary.json').read_bytes())
assert summary == {**{k:v for k,v in payload.items() if k not in ('source_hashes','records')},'full_receipt_sha256':sha(raw)}
# Reuse proofs compare every original successful row and retained counterexample exactly.
for filename, total in [('initial-mechanist-counterexample085.json.gz',69),
                        ('initial-enemy-identity-counterexample085.json.gz',581)]:
    history = json.loads(gzip.decompress((HERE/filename).read_bytes()))
    for index,historical in enumerate(history['completed_records']):
        assert canonical(rows[index]) == canonical(historical), (filename,index)
    current = rows[total-1]
    for key, historical_key in [('input','current_input'),('result','current_result'),
        ('visible_report','current_visible_report'),('report_texts','current_report_texts')]:
        assert canonical(current[key]) == canonical(history[historical_key]),(filename,key)

counts=Counter();errors=Counter();pairs=Counter();json_projection_rows=Counter();bindings=Counter()
anchors={};selected_boss_anchors={};technical_anchors={}
def exact(value, expected_value): assert canonical(value)==canonical(expected_value)
def metrics(result, section_id):
    matches=[s for s in result['report']['sections'] if s['id']==section_id]
    assert len(matches)==1
    return {m['key']:m['value'] for m in matches[0]['metrics']}
for index,(case,row) in enumerate(zip(cases,rows,strict=True)):
    before=canonical(row)
    args={key:default for key,label,default,maximum,numbers in options.get(case['input']['operator'],[]) if case['input']['skill'] in numbers}
    args.update(case['input']);exact(row['input'],args)
    assert row['section']==case['section'] and row['context']==case['context']
    counts[case['section']]+=1
    result=row['result']
    if case.get('expected_error'):
        assert result is None and row['report_texts'] is None
        assert row['actual_error_type']=='ValueError'
        assert row['actual_error']==row['expected_error']==row['visible_report']==case['expected_error']
        errors[case['section']]+=1
        continue
    assert type(result)is dict
    texts=row['report_texts'];assert set(texts)=={'estimate','default','technical'}
    assert all(type(text)is str and text for text in texts.values())
    assert texts['estimate']==texts['default']
    assert row['visible_report']==texts['technical' if case.get('technical',False) else 'default']
    assert row['all_three_texts_preserve_result_bytes']is True
    field={82:'low_cost_healing_target',84:'haruka_repeat',85:'near_previous_deployment'}.get(case['section'])
    plain=result
    if field and field in args:
        key=(case['section'],canonical({k:v for k,v in args.items()if k!=field}))
        if not args[field]:anchors[key]=result
        else:pairs[case['section']]+=1
        plain=anchors[key]
    if case['section']==81:
        namespace['require_warning_order085'](result,args,row['visible_report'],case['technical'])
        key=canonical(args)
        if not case['technical']:technical_anchors[key]=row
        else:
            exact(result,technical_anchors[key]['result']);exact(texts,technical_anchors[key]['report_texts'])
            bindings['technical_pairs_identical_calculation_JSON_and_three_texts']+=1
    elif case['section']==82:
        selected=factor(args,'微创治疗','heal_scale',1.0);json_projection_rows[82]+=1
        namespace['require_susuro_checkbox085'](result,args,row['visible_report'],plain,selected)
    elif case['section']==83:
        namespace['require_neural_checkbox085'](result,args,row['visible_report'])
        if args.get('target_enemy'):
            assert result['run_resolution']['enemy']['enemy_id']==args['target_enemy']['enemy_id']
            assert result['run_resolution']['enemy']['stage_id']==args['target_enemy']['stage_id']
            key=canonical({k:v for k,v in args.items()if k!='enemy_is_boss'})
            if args['enemy_is_boss']is False:selected_boss_anchors[key]=result
            else:exact(result,selected_boss_anchors[key]);bindings['selected_boss_overrides_manual_whole_JSON_pairs']+=1
        if 'rogue_6_relic_fight_22'in args['relic_ids']:
            river=metrics(result,'river_neural');ref=result['neural_relic_reference']
            for metric_key,ref_key in [('instant_raw','instant_raw_damage'),('instant_adjusted','instant_adjusted_damage'),
                ('periodic_raw','periodic_raw_damage'),('periodic_interval','periodic_interval')]:
                exact(river[metric_key],ref[ref_key]);bindings['River_metric_source_values']+=1
            assert river['first_tick']is None
    elif case['section']==84:
        bonus=catalog['operators'][args['operator']]['skills'][args['skill']-1]['levels'][args['skill_rank']-1]['values'].get('atk',0.0)
        namespace['require_repeat_checkbox085'](result,args,row['visible_report'],plain,bonus)
        ref=result['haruka_healing_reference'];reported=metrics(result,'haruka_healing')
        for metric_key,ref_key in [('trait_base','selected_trait_target_limit_parameter'),('skill_add','skill_target_add_parameter'),
            ('combined','conditional_target_limit_reference'),('modeled','modeled_target_limit_reference'),('declared','declared_healing_targets')]:
            exact(reported[metric_key],ref[ref_key]);bindings['Haruka_metric_source_values']+=1
        assert reported['actual_targets']is None
    elif case['section']==85:
        selected=factor(args,'翔虫机动','atk',0.0);json_projection_rows[85]+=1
        namespace['require_nearby_checkbox085'](result,args,row['visible_report'],plain,selected)
    else:raise AssertionError(case['section'])
    # Report metrics are bound to actual saved estimate fields. None stays None.
    skill=result['estimate']['skill']
    section_ids=[s['id']for s in result['report']['sections']]
    if 'damage'in section_ids:
        reported=metrics(result,'damage')
        for key,value in [('per_cast',skill['total_damage']),('window_damage',skill['window_damage']if 'window_damage'in skill else result['total_damage']),('cycle_dps',skill['cycle_dps'])]:
            if key in reported:exact(reported[key],value);bindings['damage_metric_saved_value']+=1
    if 'healing'in section_ids:
        reported=metrics(result,'healing')
        for key,skill_key in [('per_cast','total_healing'),('window_healing','window_healing'),('hps','cycle_hps')]:
            if key in reported:exact(reported[key],skill[skill_key]);bindings['healing_metric_saved_value']+=1
    if 'external_events'in section_ids:assert metrics(result,'external_events')['events']is None
    if 'unbound_cast'in section_ids:assert metrics(result,'unbound_cast')['hits']is None
    exact(row,json.loads(before))
assert counts=={81:136,82:216,83:450,84:88,85:264}and errors=={83:24}
assert pairs=={82:108,84:40,85:132}
assert json_projection_rows=={82:216,85:264}
assert bindings['technical_pairs_identical_calculation_JSON_and_three_texts']==68
assert bindings['selected_boss_overrides_manual_whole_JSON_pairs']==8
receipt={'status':'PASS_FINAL_STATIC_AND_ALL_SAVED1154_0_NEW_PRODUCT_CALLS',
    'root_commit':ROOT,'final_runner_sha256':sha(runner),'saved_result_gzip_sha256':sha(raw),
    'complete_old3063_body_inverse_exact':True,'planned_actual_UI_case_count':4217,
    'pure_UI_case_objects':1154,'unique_calculation_inputs':1086,'section_counts':dict(counts),
    'successful_saved_results':1130,'exact_existing_ValueError_rows':24,
    'strict_whole_saved_history_prefixes_and_counterexamples_unchanged':[69,581],
    'false_before_true_pairs':dict(pairs),'metric_binding_counts':dict(bindings),
    'independent_JSON_qualification_projection_rows':dict(json_projection_rows),
    'saved_text_requests':3390,'author_instrumented_actual_formatter_entries':4520,
    'saved_three_texts_per_success':True,'exact_estimate_default_text_equality':True,
    'technical_selected_visible_text_exact':True,'source723_named_commit_bytes_verified':True,
    'public125_complete_named_git_blobs_verified':True,'frozen_public_tree_extra_py_json_files':[],
    'author_API_call_attribution':payload['actual_API_call_attribution'],
    'author_original_result_source_qualification_helpers':480,
    'author_saved581_reassertion_source_qualification_helpers':216,
    'author_total_external_source_helpers_separate_from_API_and_formatters':696,
    'public_tree_omitted_from_review_archive':True,
    'public_tree_reconstructable_from_named_commit_and_all125_hashes':True,
    'unknown_clock_target_native_composition_None_and_false_preserved':True,
    'reviewer_application_API_calls':0,'reviewer_formatter_calls':0,'reviewer_production_helper_calls':0,
    'reviewer_Qt_calls':0,'reviewer_Wine_calls':0,'reviewer_tracked_mutations':False,
    'source_and_result_snapshots':snapshots,
    'scope':'Static/API saved proof permits root actual Qt/Wine execution; it is not an actual UI pass or native Windows/game validation.'}
digest=save('final-static-and-saved1154-review085.json',receipt)
print(json.dumps({'status':receipt['status'],'receipt_sha256':digest,'runner_sha256':sha(runner),
    'records':1154,'success':1130,'existing_errors':24,'API':0,'formatters':0,'Qt':0,'Wine':0},ensure_ascii=False))
