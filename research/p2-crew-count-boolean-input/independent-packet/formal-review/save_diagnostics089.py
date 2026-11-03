"""Freeze factual preparation diagnostics with file identities; zero project calls."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

def row(name):
    path = OUT / name
    raw = path.read_bytes()
    return {'source_path': str(path), 'archive_path': name, 'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'local_file_mtime_utc': datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),
        'mtime_scope': 'Actual local saved-file metadata, not request/server timestamp.'}

fixed = (OUT / 'run_independent089.py').read_bytes()
assert fixed == (OUT / 'initial-cache-audit-run_independent089.py').read_bytes()
fixed_tree = ast.parse(fixed.decode())
assert any(isinstance(node, ast.ClassDef) and node.name == 'FixedPublicSourceLoader' for node in fixed_tree.body)
assert (OUT / 'initial-cache-audit-baseline089/runtime').is_dir()
assert not list((OUT / 'initial-cache-audit-baseline089').rglob('*.*'))
baseline_gzip = OUT / 'fresh-baseline089/complete-native-records.json.gz'
assert hashlib.sha256(baseline_gzip.read_bytes()).hexdigest() == '6841d9ae4ec5fdb298c4cc2f70d7df123a01b68b62386bb96a8b93c87b774c89'
receipt = {
    'status': 'PREPARATION_DIAGNOSTICS_RETAINED_NO_PRODUCT_RETRIES',
    'problem_counts': {
        'AST_nested_literal_count_reader': {'failed_attempts': 1, 'next_attempt': 'PASS', 'project_calls_before_failure': 0},
        'pyc_public_source_audit_import_gate': {'failed_attempts': 1, 'next_attempt': 'PASS fixed standardSourceFileLoader baseline', 'constructor_apply_before_failure': 0},
        'redundant_resume_loader_patch_context': {'failed_attempts': 1, 'patch_applied': False, 'project_calls': 0},
        'resume_packaging_move_wrong_destination': {'observed_misdestination': 1, 'restore_moves': 2, 'code_or_data_bytes_changed': False, 'product_calls': 0}},
    'original_failed_cache_script_bytes_proven_retained': False,
    'failed_cache_trace': row('initial-cache-audit-baseline-execution089.log'),
    'fixed_loader_source': row('run_independent089.py'),
    'copy_with_initial_filename_is_fixed_loader_not_failed_original': row('initial-cache-audit-run_independent089.py'),
    'original_failed_AST_script': row('initial-review_frozen_draft089.py'),
    'original_failed_AST_trace': row('initial-static-count-trace089.txt'),
    'baseline_success_original_stdout_restored': row('fresh-baseline-execution089.log'),
    'baseline_gzip_original_bytes_restored': row('fresh-baseline089/complete-native-records.json.gz'),
    'no_baseline_reexecution': True,
    'actual_resume_tools': [
        {'cmd': 'cp run_independent089.py initial-cache-audit-run_independent089.py', 'exit': 0, 'scope': 'fixed loader copy; not a raw failed-source receipt'},
        {'cmd': 'mv fresh-baseline089 initial-cache-audit-baseline089', 'exit': 0, 'effect': 'existing destination caused nested successful folder; no bytes changed'},
        {'cmd': 'mv fresh-baseline-execution089.log initial-cache-audit-execution089.log', 'exit': 0},
        {'tool': 'apply_patch redundant loader', 'result': 'verification failed: expected sys.addaudithook/audit/sys.path/import rouge context absent; loader already present', 'mutation': False},
        {'cmd': 'mv initial-cache-audit-baseline089/fresh-baseline089 fresh-baseline089', 'exit': 0, 'effect': 'restored original path'},
        {'cmd': 'mv initial-cache-audit-execution089.log fresh-baseline-execution089.log', 'exit': 0, 'effect': 'restored original success log path'}],
    'local_discovery_orchestration_only': [
        {'cmd': "rg --files --hidden rouge | rg '/__pycache__/'", 'exit': 1, 'application_failure': False},
        {'tool': 'collaboration.followup_task alternate_module_gaps', 'result': 'agent thread limit reached', 'new_child_turn': False, 'product_calls': 0}],
    'preparation_project_failures': 0,
    'actual_final_runtime_counts': {'constructors': 20, 'apply': 30, 'tests': 7, 'skips': 0},
    'same_problem_three_fail_limit_exceeded': False,
    'seal_observation_time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'All measurements refer to this independent89 external stage; root UI/selected regression are separate.'}
with (OUT / 'preparation-diagnostics089.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': receipt['status'], 'new_project_calls': 0,
    'fixed_loader_sha256': receipt['fixed_loader_source']['sha256'], 'baseline_not_repeated': True}))
