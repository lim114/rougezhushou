"""Only decode actual A3 saved output and inspect exact source; never run application."""
from pathlib import Path
import ast, collections, copy, gzip, hashlib, importlib.util, json, subprocess, sys
sys.dont_write_bytecode=True
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'verification/full-275/legacy-window-attempt3'
BUNDLE = ARCHIVE / 'executed-tools'
FREEZE = ROOT / 'verification/full-275/source-freeze-reset-repair.json'
BASE = ROOT / '.cache/full275-saved-readback-attempt3'
BASE.mkdir(exist_ok=False)
SNAPSHOT = ROOT
CONTAINER = BASE / 'audit-input-container'
CONTAINER.mkdir()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(path.read_bytes())
def write(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def ordered(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def copy_exclusive(source,target,expected):
    assert source.is_file() and not source.is_symlink()
    raw=source.read_bytes();assert sha(raw)==expected
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(raw)
    assert sha(target.read_bytes())==expected
    return {'from':source.relative_to(ROOT).as_posix(),'to':target.relative_to(BASE).as_posix(),'sha256':expected,'bytes':len(raw)}
manifest=read(ARCHIVE/'archive-manifest.json')
original_hashes={name:sha((ARCHIVE/name).read_bytes()) for name in manifest['files']}
assert all(original_hashes[name]==pin['sha256'] and (ARCHIVE/name).stat().st_size==pin['bytes'] for name,pin in manifest['files'].items())
original_hashes['archive-manifest.json']=sha((ARCHIVE/'archive-manifest.json').read_bytes())
live_pins=read(FREEZE)['source_sha256']
live_before={name:sha((ROOT/name).read_bytes()) for name in live_pins}
assert live_before==live_pins
guard=read(BUNDLE/'current-source-guard.json')
for group in ('source_sha256','source_additional_sha256'):
    for name,pin in guard[group].items():assert sha((ROOT/name).read_bytes())==pin,name
copied=[]
for source in sorted((ARCHIVE/'actual').rglob('*')):
    if source.is_file():
        relative='actual/'+source.relative_to(ARCHIVE/'actual').as_posix()
        copied.append(copy_exclusive(source,CONTAINER/relative,original_hashes[relative]))
copied.append(copy_exclusive(ARCHIVE/'supervisor.json',CONTAINER/'supervisor.json',original_hashes['supervisor.json']))
supervisor=read(ARCHIVE/'supervisor.json')
assert supervisor['status']=='completed' and supervisor['child_primary_exit']==supervisor['supervisor_exit']==0
assert supervisor['timed_out'] is False and supervisor['owned_job_no_live_execution_verified'] is True
with (CONTAINER/'process.exit').open('x',encoding='ascii') as f:f.write(str(supervisor['supervisor_exit'])+'\n')
write(BASE/'input-preparation.json',{
    'kind':'READONLY_A3_SAVED_OUTPUT_FROM_REAL_SEALED_BYTES',
    'current_root_source_count':len(live_pins),'current_root_freeze_sha256':sha(FREEZE.read_bytes()),
    'guard_source_count':len(guard['source_sha256']),'guard_additional_source_count':len(guard['source_additional_sha256']),
    'current_checkout_replaced_or_application_executed':False,
    'original_archive_files_hash_before':original_hashes,
    'process_exit':'DERIVED_INPUT_ONLY_FROM_TERMINAL_REAL_SUPERVISOR_NOT_ORIGINAL_RAW_CONSOLE',
    'process_exit_authority':{'path':(ARCHIVE/'supervisor.json').relative_to(ROOT).as_posix(),
        'sha256':original_hashes['supervisor.json'],'terminal_status':supervisor['status'],
        'child_primary_exit':supervisor['child_primary_exit'],'supervisor_exit':supervisor['supervisor_exit'],
        'timed_out':supervisor['timed_out'],'owned_job_no_live_execution_verified':supervisor['owned_job_no_live_execution_verified']},
    'copies':copied,'private_state_or_game_samples_read':False})
tool = BUNDLE/'audit_full261_saved_readback.py'
assert sha(tool.read_bytes()) == original_hashes['executed-tools/audit_full261_saved_readback.py']
argv = [str(ROOT/'.venv/Scripts/python.exe'),'-X','utf8',str(tool),'--root',str(SNAPSHOT),
        '--container',str(CONTAINER),'--bundle',str(BUNDLE),'--freeze',str(FREEZE)]
run = subprocess.run(argv,cwd=ROOT,capture_output=True)
with (BASE/'trusted-tool-stdout.log').open('xb') as f:f.write(run.stdout)
with (BASE/'trusted-tool-stderr.log').open('xb') as f:f.write(run.stderr)
write(BASE/'trusted-tool-process.json',{'argv':argv,'actual_exit':run.returncode,
    'tool_sha256':sha(tool.read_bytes()),'tool_original_bytes_unchanged':True,
    'stdout_sha256':sha(run.stdout),'stderr_sha256':sha(run.stderr),
    'GUI_or_game_process_started':False,'process_exit_input_was_derived_not_original_raw':True})
if run.returncode != 0:
    print(json.dumps({'actual_exit':run.returncode,'stderr_log':str(BASE/'trusted-tool-stderr.log')},ensure_ascii=False))
    sys.exit(run.returncode)

trusted = read(CONTAINER/'independent-saved-readback-audit.json')
assert trusted['readonly_trace_empty_rows_not_invented'] == 26
assert trusted['saved_rows'] == 52 and trusted['complete_runtime_checks'] == 4283
window_raw = (BUNDLE/'window.py').read_bytes()
old_raw = (BUNDLE/'original261-window.py').read_bytes()
window_text, old_text = window_raw.decode('utf8'),old_raw.decode('utf8')
tree, old_tree = ast.parse(window_text),ast.parse(old_text)
def assert_vector(tree):
    return [ast.dump(node,include_attributes=False) for node in sorted(
        (x for x in ast.walk(tree) if isinstance(x,ast.Assert)),key=lambda x:(x.lineno,x.col_offset))]
assert len(assert_vector(tree)) == 862 and assert_vector(tree) == assert_vector(old_tree)
def maintry(text, parsed):
    nodes=[x for x in parsed.body if isinstance(x,ast.Try) and sum(isinstance(a,ast.Assert) for a in ast.walk(x))==552]
    assert len(nodes)==1
    return ast.get_source_segment(text,nodes[0]).encode('utf8')
assert maintry(window_text,tree) == maintry(old_text,old_tree)
assert sha(maintry(window_text,tree)) == '11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922'

rows_literal = next(x for x in ast.walk(tree) if isinstance(x,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id=='rows090' for t in x.targets))
literal_rows = ast.literal_eval(rows_literal.value)
assert len(literal_rows)==52
archive = json.loads(gzip.decompress((ARCHIVE/'actual/wine-ui-new-states-100.json.gz').read_bytes()))
saved = archive['actual_new_window_states']
saved_by_identity={(r['section'],r['pair_id'],r['widget_checked']):r for r in saved}
assert len(saved_by_identity)==52
pure = next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='projection090')
namespace = {}
exec(compile(ast.Module(body=[pure],type_ignores=[]),'sealed-pure-projection090','exec'),namespace)
spec = importlib.util.spec_from_file_location('sealed_readback275',tool)
module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
ledger=read(ARCHIVE/'actual/full125-113-bridge-ledger.json')
admitted={r['literal_index']:r for r in ledger['actual_admissions']}
assert sorted(admitted)==[18,19,20,21,38,39,40,41,44,45]
projection_controls=[]
for index,row in enumerate(literal_rows):
    identity=(row['section'],row['pair_id'],row['widget_checked'])
    captured=saved_by_identity[identity]
    result=module.decode(captured['result_native'],collections.Counter())
    projected=namespace['projection090'](result)
    untouched_sha=sha(ordered(module.encode(projected)).encode())
    if index in admitted:
        assert untouched_sha==admitted[index]['actual_candidate_projection_native090_sha256']
        comparison=copy.deepcopy(projected)
        for path in admitted[index]['comparison_only_exceptions']:
            assert path in {'estimate.skill.window_seconds','estimate.skill.window_dps','estimate.skill.window_hps'}
            name=path.rsplit('.',1)[1]
            comparison['estimate']['skill'][name]=row['expected_public_projection']['estimate']['skill'][name]
        category='EXACT_ADMITTED_COMPARISON_ONLY_METRIC_LEAVES'
    else:
        comparison=projected
        category='UNCHANGED_HISTORICAL_PROJECTION'
    assert json.loads(ordered(comparison))==json.loads(ordered(row['expected_public_projection'])),index
    projection_controls.append({'literal_index':index,'category':category,
        'actual_projection_native_sha256':untouched_sha,
        'comparison_equals_original_literal':True,
        'raw_saved_result_unchanged':module.encode(result)==captured['result_native']})
assert sum(x['category']=='UNCHANGED_HISTORICAL_PROJECTION' for x in projection_controls)==42
after={name:sha((ARCHIVE/name).read_bytes()) for name in original_hashes}
assert after==original_hashes
live_after={name:sha((ROOT/name).read_bytes()) for name in live_pins}
assert live_after==live_before
write(BASE/'independent-full275-saved-readback-summary.json',{
    'kind':'INDEPENDENT_FULL275_NATIVE_ATTEMPT2_SAVED_READBACK','passed':True,
    'actual_section':275,'actual_native_attempt':3,'trusted_historical_tool_labels_retained':True,
    'current_checkout_replaced_or_application_reexecuted':False,
    'audit_root':str(ROOT), 'source_scope':'Exact A3 root source still matches source-freeze-reset-repair; no previous phase reused',
    'trusted_tool_actual_exit':run.returncode,'real_native_fixture_child_exit':supervisor['child_primary_exit'],
    'real_native_fixture_supervisor_exit':supervisor['supervisor_exit'],
    'runtime_records':4283,'passed_flag_records':4281,'metadata_records':2,
    'saved_typed_rows':52,'three_formatter_requests':156,'real_empty_trace_rows':26,
    'current862_assert_AST_order_matches_original261':True,'original552_maintry_bytes_unchanged':True,
    'original552_maintry_sha256':sha(maintry(window_text,tree)),
    'historical_projection_controls':42,'exact_bridge_indices':sorted(admitted),
    'all52_projections_independently_decoded_and_compared':True,'projection_controls':projection_controls,
    'original_archive_files_sha_before_after_equal':True,'live_maintenance_sources_sha_before_after_equal':True,
    'typed_saved_roundtrip_and_floathex_preserved':trusted['codec_exact_typed_roundtrip'],
    'historical_original_Windows_game_or_chat_verified':False,'GUI_process_started_by_this_readback':False,
    'process_exit_input':'explicitly derived from real terminal supervisor, not original raw console',
    'trusted_output':(CONTAINER/'independent-saved-readback-audit.json').relative_to(ROOT).as_posix(),
    'trusted_output_sha256':sha((CONTAINER/'independent-saved-readback-audit.json').read_bytes()),
    'command':argv})
print(json.dumps({'passed':True,'actual_exit':run.returncode,'records':4283,'typed_rows':52,'projection_controls':42,
    'exact_bridge_indices':sorted(admitted),'real_empty_trace_rows':26,
    'summary':str(BASE/'independent-full275-saved-readback-summary.json')},ensure_ascii=False))
