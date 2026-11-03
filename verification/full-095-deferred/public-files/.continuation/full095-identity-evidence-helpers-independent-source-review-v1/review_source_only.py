"""Independent metadata/AST/byte review only. Never execute any reviewed code."""
import ast
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/workspace/.continuation')
OUT = BASE / 'full095-identity-evidence-helpers-independent-source-review-v1'
SEEN = {}
CHECKS = []

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def ref(path):
    path = Path(path)
    assert path.is_absolute() and path.is_file() and not path.is_symlink()
    assert str(path.resolve()) == str(path)
    raw = path.read_bytes()
    value = {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}
    assert str(path) not in SEEN or SEEN[str(path)] == value
    SEEN[str(path)] = value
    return value

def doc(path):
    value = ref(path)
    return json.loads(Path(path).read_bytes()), value

def record(name, evidence):
    CHECKS.append({'name': name, 'passed': True, 'qualification': 'Source/metadata only', 'evidence': evidence})

def funcs(raw):
    tree = ast.parse(raw)
    lines = raw.splitlines(keepends=True)
    return {n.name: b''.join(lines[n.lineno-1:n.end_lineno])
            for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

def frozen(name, expected_sha):
    folder = BASE / name
    paths = list(folder.glob('public-artifacts-manifest-*.json'))
    assert len(paths) == 1
    manifest, mr = doc(paths[0])
    assert mr['sha256'] == expected_sha
    assert manifest['STOPWRITE'] is True and manifest.get('runtime_pass', False) is False
    assert manifest.get('target_execution_calls', manifest.get('runtime_calls')) == 0
    if 'files' in manifest:
        rows = manifest['files'].values()
    elif 'payload_files' in manifest:
        rows = manifest['payload_files']
    else:
        rows = ({'path': str(folder / key), **row} for key, row in manifest['artifacts'].items())
    for row in rows:
        assert ref(row['path']) == row
    hand = list(folder.glob('handoff-*.json'))
    assert len(hand) == 1
    hj, hr = doc(hand[0])
    assert hj['manifest'] == mr and hj.get('runtime_calls', 0) == 0
    return {'manifest': mr, 'handoff': hr}

def inverse(folder):
    ledger, ir = doc(next((BASE / folder).glob('exact-inverse-*.json')))
    original, candidate = ledger['original'], ledger['candidate']
    assert ref(original['path']) == original and ref(candidate['path']) == candidate
    old = Path(original['path']).read_bytes()
    new = Path(candidate['path']).read_bytes()
    restored = new
    for op in reversed(ledger['operations']):
        start, count = op['pending_byte_start'], op['pending_byte_count']
        assert digest(restored[start:start+count]) == op['pending_sha256']
        before = base64.b64decode(op['before_base64'], validate=True)
        assert digest(before) == op['before_sha256']
        restored = restored[:start] + before + restored[start+count:]
    assert restored == old
    compile(new, candidate['path'], 'exec')  # Compilation only; no execution.
    before_funcs, after_funcs = funcs(old), funcs(new)
    assert before_funcs.keys() == after_funcs.keys()
    unchanged = [n for n in before_funcs if before_funcs[n] == after_funcs[n]]
    changed = [n for n in before_funcs if before_funcs[n] != after_funcs[n]]
    assert unchanged == ledger['functions_whole_byte_unchanged']
    assert changed == ledger['functions_changed']
    return {'ledger': ir, 'original': original, 'candidate': candidate,
            'whole_byte_inverse': True, 'operations': len(ledger['operations']),
            'functions_unchanged': unchanged, 'functions_changed': changed}

PACKETS = {
 'full095-saved-control-ui-identity-source-v1': '59aa4a',
 'full095-actual-acceptance-ui-identity-source-v1': 'b6c1485e7c89ade2e577920279fa015c572bd6486276388942991d1078d371cd',
 'full095-archive-ui-identity-spec-source-v1': 'e69bc1563e9f2178ed4b68565e94355d2bc6c5f90889dd7ee338ad6e03db7cc0',
 'full095-ui-identity-archive-final-review-source-v1': '6dfa425755431dd4d1af8512b3eeb132b6b2f8fa295cf0ba353a92941a1bf689',
 'full095-ui-identity-evidence-sealer-source-v1': '4bcc',
 'full095-archive-ui-identity-spec-source-v2': '0672576bf7d64e326eb67f3961f3c11dbb97f16a2d2e728aac2918dc013a037d',
 'full095-ui-identity-evidence-sealer-source-v2': '104c29612b9926b50710be82545f9c8769a56908cc2f12b67b8fb4a301d800e1',
}
# Two caller-supplied prefixes are independently resolved to their physical full
# hash and checked against the exact prefix; they are not future-runtime hashes.
for name, expected in list(PACKETS.items()):
    if len(expected) != 64:
        mf = next((BASE / name).glob('public-artifacts-manifest-*.json'))
        actual = ref(mf)['sha256']
        assert actual.startswith(expected)
        PACKETS[name] = actual
packet_refs = {name: frozen(name, sha) for name, sha in PACKETS.items()}
record('seven_exact_frozen_packets', packet_refs)

inverse_refs = {name: inverse(name) for name in PACKETS
                if list((BASE / name).glob('exact-inverse-*.json'))}
assert inverse_refs['full095-saved-control-ui-identity-source-v1']['original']['sha256'] == 'b49a90dd0b2827497e1d826cd98822c3f12519a7579d9478ef0593aa73abb95e'
assert inverse_refs['full095-actual-acceptance-ui-identity-source-v1']['original']['sha256'] == 'ae375a68c7ff2024db88d14260bb561d317d9a224593464cfac8208bf6fe0bdf'
assert inverse_refs['full095-archive-ui-identity-spec-source-v1']['original']['sha256'] == '1914566d67f31be92783135722757562150d3d8c6ceacfe2fcce3d75041d90ae'
assert inverse_refs['full095-ui-identity-archive-final-review-source-v1']['original']['sha256'] == 'd1c8de11da2397f503966bc6fbf83a173dd993b7b1f46d8d6e1e663d91267128'
record('four_old_whole_inverse_and_two_v2_chains', inverse_refs)

source_names = {
 'saved_control': ('full095-saved-control-ui-identity-source-v1', 'assemble_saved_input095.py'),
 'acceptance': ('full095-actual-acceptance-ui-identity-source-v1', 'assemble_actual_acceptance095.py'),
 'archive': ('full095-archive-ui-identity-spec-source-v2', 'assemble_archive_spec095.py'),
 'reviewer': ('full095-ui-identity-archive-final-review-source-v1', 'review_actual_archive_spec095.py'),
 'sealer': ('full095-ui-identity-evidence-sealer-source-v2', 'seal_evidence_helpers095.py'),
}
source = {n: (BASE / folder / filename).read_text() for n,(folder,filename) in source_names.items()}
source_refs = {n: ref(BASE / folder / filename) for n,(folder,filename) in source_names.items()}
for name, text in source.items():
    tree = ast.parse(text)
    allowed = {'argparse','ast','base64','hashlib','json','re','stat','datetime','pathlib'}
    imports = [a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
    imports += [n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    assert set(imports) <= allowed
    compile(text, source_refs[name]['path'], 'exec')
record('stdlib_only_source_compile_no_target_execution', source_refs)

conf, conf_ref = doc(BASE / 'full095-archive-ui-identity-spec-source-v2/source-inputs095.json')
assert conf['runtime_pass'] is False and conf['actual_identity_final_refs_present'] is False
pending = {}
for key in ('recovery_binding','recovery_runner','ui_prelaunch'):
    row = conf['pinned_source_inputs'][key]
    assert row['bytes'] is row['sha256'] is None
    pending[key] = row
for key,row in conf['pinned_source_inputs'].items():
    if key not in pending:
        assert ref(row['path']) == row
record('typed_null_actual_slots_not_fabricated', {'config': conf_ref, 'pending': pending})

sealer = source['sealer']
assert 'full095-archive-ui-identity-spec-source-v2' in sealer
assert PACKETS['full095-archive-ui-identity-spec-source-v2'] in sealer
for text in ("context_mf['payload_files']", "binding_ref in context_payload and runner_ref in context_payload",
             "binding['recovery_spec']['root_ui_prelaunch'] == pre_ref",
             "old['bytes'] is old['sha256'] is None", "not OUTPUT.exists()", "path.open('xb')"):
    assert text in sealer
assert '__ACTUAL_UI_IDENTITY_RETRY_BINDING_SHA256_PENDING__' in source['acceptance']
assert '__ACTUAL_UI_IDENTITY_RETRY_BINDING_FULL_REF_PENDING__' in source['reviewer']
assert '__ACTUAL_UI_IDENTITY_RETRY_CONTEXT_RUNNER_SHA256_PENDING__' in source['reviewer']
assert "'style': 'payload_ref_rows'" in sealer
record('actual_final_context_prelaunch_manifest_seal_contract', {'Source_only': True, 'three_late_actual_slots': list(pending), 'exclusive_future_output': '/workspace/.continuation/full095-ui-identity-evidence-final-v1'})

required_packets = conf['source_identity_required_extra_packets']
assert len(required_packets) == 4
for row in required_packets:
    mf,mr = doc(row['path'])
    if row['style'] == 'local_artifact_dict':
        for key,meta in mf['artifacts'].items():
            assert ref(Path(row['path']).parent / key) == {'path': str(Path(row['path']).parent / key), **meta}
    else:
        assert row['style'] == 'flat_file_meta_dict' and mf['STOPWRITE'] is True and mf['runtime_pass'] is False
        for full in mf['files'].values():
            assert ref(full['path']) == full
record('producer_saved_and_flat_source_packet_style_admission', {'packets': required_packets, 'manifest_styles_explicit': True})

capsule,capsule_ref = doc(BASE / 'ROOT_CURRENT_WORK_095_UI_CACHE_SESSION_LOST_PRIMARY_UNAVAILABLE.json')
assert capsule_ref['bytes'] == 530488 and capsule_ref['sha256'] == 'bcbf9e5e3f9aeff1745387221cd0b293aca149d52cbf566750cb0afea3d80eb6'
assert capsule['primary_exit_code'] is None and capsule['primary_exit_code_captured'] is False
assert capsule['raw_primary_status_absent'] is capsule['final_UI_receipt_absent'] is True
assert capsule['native_outcome'] == 'pending'
assert capsule['same_UI_execution_problem_incomplete_attempt_count'] == 2 and capsule['third_attempt_failure_requires_deferral'] is True
chunks = capsule['all_closed_compressed_chunk_refs_verified']
assert len(chunks) == 2310 and all(ref(row['path']) == row for row in chunks)
config_refs = list(conf['supplemental_public_inputs'].values())
assert capsule_ref in config_refs and all(row in config_refs for row in chunks)
record('all_2310_real_second_lost_history_refs_qualified', {'capsule': capsule_ref, 'compressed_closed_chunk_count': len(chunks), 'primary_exit': None, 'runtime_PASS': False, 'defer_after_third_incomplete_attempt': True})

identity_text = (BASE / 'full095-regression-ui-identity-resume-source-v1/identity_binding095.py').read_text()
context_text = (BASE / 'full095-regression-ui-identity-resume-source-v1/full095_context_ui_retry_pending.py').read_text()
sealer_context_text = (BASE / 'full095-regression-ui-identity-resume-source-v1/seal_ui_retry095.py').read_text()
assert "context['ui_retry_started_at'] == '2026-10-09T00:59:43.753835+00:00'" in identity_text
assert "ui_retry_started_at=prior_ui_context['ui_retry_started_at']" in context_text
assert 'ui_identity_retry_started_at=now()' in context_text
assert "'payload_files': [file_ref(path)" in sealer_context_text
for key in ('prior_ui_retry','prior_incomplete_ui_cache','actual_ui_identity_retry','ui_identity_retry_started_at'):
    assert key in source['acceptance'] and key in source['archive'] and key in source['reviewer'] and key in context_text
record('identity_context_schema_and_fresh_time_boundary', {'prior_epoch_preserved': '2026-10-09T00:59:43.753835+00:00', 'actual_new_identity_epoch': None, 'context_Source_ref': ref(BASE / 'full095-regression-ui-identity-resume-source-v1/full095_context_ui_retry_pending.py'), 'identity_binding_Source_ref': ref(BASE / 'full095-regression-ui-identity-resume-source-v1/identity_binding095.py')})

for text in ("early['actual_source_binding'] == SOURCE_BASE_BINDING", "binding['recovery_spec']['prior_ui_retry']['binding'] == SOURCE_BASE_BINDING"):
    assert text in source['reviewer']
assert 'b83ab67ca978d1b1b9e393c6d4e2cfb6c77e3bf9600af9d7ae87fe40975dbb84' in source['reviewer']
record('early_b83_source_basis_is_ancestor_not_current_identity_binding', {'early_source_basis_unchanged': True, 'new_actual_identity_binding': None})

guard_path = Path('/workspace/rougezhushou/research/p2-section095-selected-module-source-report/root-source-095-v2.json')
guard,guard_ref = doc(guard_path)
assert guard_ref['bytes'] == 84227 and guard_ref['sha256'] == '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
assert len(guard['source_sha256_after']) == 735
record('actual_archived_guard735_no_replacement', {'guard':guard_ref, 'maintained_source_count':735, 'maintained_sources_executed':False})

for text in ("'actual_root_observed_primary_exit'", "'primary_exit_code_captured'", "'completion_tool_chunk'", "raw_paths.add(raw_ref['path'])", "check(row == old", "check(row == earlier"):
    assert text in source['acceptance']
assert "len(cache_chunks) == 2310" in source['reviewer']
assert "refs_by_path.get(row['path']) == row" in source['reviewer']
assert "incomplete['primary_exit_code'] is None" in source['archive']
assert "failed_observation['primary_exit_code'] == 1" in source['archive']
record('six_immutable_zero_rows_failed1_and_both_lost_null_preserved', {'all_eight_actual_primary_zero_required':True, 'six_passes_are_preserved_not_replayed':True, 'first_lost_primary':None, 'second_lost_primary':None})

for text in ('/actual_fullUI_saved_evidence_verified','/actual_UI_primary_exit0_verified','/original_pending_and_final_inverse_exact','/actual_phase_ledger_verified',"'actual_PNGs_viewed'", "'actual_root_view_image'"):
    assert text in source['acceptance']
assert "guard in spec['ui_binding_input_refs']" in source['acceptance']
assert "len(png_roles) == len(set(png_roles)) == len(png_paths) == 4" in source['reviewer']
record('saved_strict_control_and_four_genuine_root_png_contract', {'actual_saved_primary_exit':None, 'actual_root_png_views':None, 'Source_requires_full_native_saved_coverage':True})

archive_tree=ast.parse(source['archive'])
cli_nodes=[n for n in ast.walk(archive_tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='--next-action']
assert len(cli_nodes)==1 and any(k.arg=='required' and isinstance(k.value,ast.Constant) and k.value.value is True for k in cli_nodes[0].keywords)
assert "template['next_action'] = args.next_action" in source['archive']
assert 'args.next_action.strip()' in source['archive']
assert inverse_refs['full095-ui-identity-evidence-sealer-source-v2']['functions_changed'] == []
record('latest_user_pause_explicit_required_cli_supersedes_old_template_action', {'archive_v2_ref':source_refs['archive'], 'Source_requires_Root_pause_text':True, 'old_template_next96_text_remains_historical_only':True, 'later_sections_not_applied_or_executed_by_review':True})

helper_path=BASE/'full095-batch-archive-ui-cache-source-v1/archive_full095_pending.py'
helper_ref=ref(helper_path)
assert helper_ref['bytes']==47117 and helper_ref['sha256']=='d93ca9bb4c50248f73337ef7b6535402e3925ec1aedd80d2e74dbe78853f0936'
helper_raw=helper_path.read_bytes()
assert b'next_action=next_action' in helper_raw
formal_body=funcs(helper_raw)['formal_gate']
assert b'pointer(review, args.formal_spec_pointer) == sha(spec_raw)' in formal_body
record('unchanged_d93_archive_helper_and_late_formal_gate', {'archive_helper':helper_ref,'formal_gate_whole_body_sha256':digest(formal_body),'actual_completed_spec_sha256':None,'Root_late_independent_spec_review_still_required':True})

for full in tuple(SEEN.values()):
    assert ref(full['path'])==full
record('final_physical_immutable_input_reread', {'unique_physical_inputs':len(SEEN)})

report={'format_version':1,'section':95,'status':'PASS_INDEPENDENT_IDENTITY_EVIDENCE_HELPERS_SOURCE_ONLY_NOT_EXECUTION_READY',
 'passed':True,'source_gate_passed':True,'runtime_pass':False,'runtime_executed':False,'execution_ready':False,
 'actual_completed_archive_spec_sha256':None,'actual_completed_archive_spec_review_passed':False,
 'actual_UI_primary_exit':None,'actual_Saved_primary_exit':None,'actual_full095_finish_PASS':None,
 'helpers':source_refs,'packets':packet_refs,'inverses':inverse_refs,'checks':CHECKS,
 'passed_checks':len(CHECKS),'failed_checks':0,'blockers':[],
 'scope':'Whole-byte inverses, frozen public metadata hashes, stdlib import/AST and compile-only Source review. No reviewed module, helper, codec, project, tests, Qt, Wine, Git, API or process sampler was executed.',
 'calls':{'reviewed_helper_execution':0,'compiled_reviewed_code_execution':0,'codec_execution':0,'project_imports':0,'tests':0,'Wine':0,'Git':0,'APIs':0,'process_sampling':0},
 'qualifications':['V1 archive template automatic96 text is superseded by required V2 --next-action. Root must supply the latest user pause text and verify it in the actual completed spec and prepare-save documents.',
 'Root must independently admit the actual sealed FINAL helper bytes and their inverse records after actual binding/context/prelaunch exist. This report certifies no future actual SHA or runtime result.',
 'Third same UI execution issue after a third incomplete attempt requires deferral; this static review does not authorize another attempt or count sections96–98 complete.',
 'Native Windows/game/chat verification remains false. Actual four Root view_image operations and eight actual primary zero proofs remain required before available full95 PASS.'],
 'completed_sections_increment':0,'tracked_mutations':0,'archive_commit_push_executed':False,
 'reviewed_at':datetime.now(timezone.utc).isoformat(),'physical_refs':list(SEEN.values()),'STOPWRITE':True}
report_path=OUT/'formal-independent-source-review-identity-evidence-helpers095.json'
with report_path.open('xb') as s:
    s.write((json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())
print(json.dumps({'report':ref(report_path),'passed_checks':len(CHECKS),'runtime_executed':False,'actual_completed_archive_spec_sha256':None}))
