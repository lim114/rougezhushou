import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

BASE = Path('/workspace/.continuation')
def ref(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

assert len(sys.argv) == 5 and sys.argv[3] == '--binding-sha256'
expected_binding_sha256 = sys.argv[4]
assert len(expected_binding_sha256) == 64 and all(c in '0123456789abcdef' for c in expected_binding_sha256)
name, job_path = sys.argv[1], Path(sys.argv[2])
assert name in ('wine_ui', 'saved_review')
binding_path = BASE / 'full095-regression-ui-identity-resume-final-v1/actual-full095-source-binding.json'
assert ref(binding_path)['sha256'] == expected_binding_sha256
binding = json.loads(binding_path.read_bytes())
assert binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
assert binding.get('actual_original_epoch_recovery') is True and binding.get('actual_ui_retry') is True
assert binding.get('root_spec_projection_from_ui_retry') is True and binding.get('actual_ui_identity_retry') is True
contract = binding['actual_inputs']['execution_contracts'][name]
paths = binding['actual_inputs']['global_output_plan']['paths']
job = json.loads(job_path.read_bytes())
assert type(job['primary_exit_code']) is int and job['primary_exit_code'] == job['last_tool_result']['exit_code'] == 0
for key in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index'):
    assert job[key] == contract[key]
assert job['stdout_path'] == paths[contract['stdout_key']]
assert job['exit_code_path'] == contract['exit_code_path']
assert Path(job['exit_code_path']).read_bytes() in (b'0\n', b'0\r\n')
assert ref(contract['runner']['path']) == contract['runner']
context = json.loads(Path(paths['context_start']).read_bytes())
assert datetime.fromisoformat(context['ui_identity_retry_started_at']) <= datetime.fromisoformat(job['started_at']) <= datetime.fromisoformat(job['completed_at'])
root = Path(job['cwd'])
guard = json.loads((BASE / 'root-source-095-v2.json').read_bytes())['source_sha256_after']
current = {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
           for folder in ('rouge', 'tests', 'scripts') for path in (root / folder).rglob('*')
           if path.is_file() and path.suffix in ('.py', '.json')}
assert len(current) == 735 and current == guard == binding['actual_inputs']['source_sha256']
row = {key: contract[key] for key in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index')}
row.update(actual_root_observed_primary_exit=True, primary_exit_code_captured=True,
           primary_exit_code=0, fresh_execution=True, started_at=job['started_at'], completed_at=job['completed_at'],
           stdout_log=ref(job['stdout_path']), exit_code_file=ref(job['exit_code_path']),
           actual_tool_observation={'session_id': job['launch_result'].get('session_id'), 'completion_tool_chunk': job['completion_tool_chunk']},
           runtime_environment={'PYTHONDONTWRITEBYTECODE': '1'})
if name == 'wine_ui':
    receipt = json.loads(Path(paths['wine_ui']).read_bytes())
    assert receipt['passed'] is True and receipt['complete_ui_validation'] is True and receipt['source_drift'] == []
    row['UI_receipt'] = ref(paths['wine_ui'])
    alias_path = BASE / 'root-full095-wine_ui-identity-retry-v1-observation.json'
else:
    receipt = json.loads(Path(paths['saved_review_receipt']).read_bytes())
    assert receipt['passed'] is True and receipt['actual_UI_primary_exit0_verified'] is True and receipt['project_calls'] == 0
    row['output_receipt'] = ref(paths['saved_review_receipt'])
    alias_path = BASE / 'root-full095-saved_review-ui-identity-retry-v1-observation.json'
standard_path = BASE / ('root-full095-' + name + '-observation.json')
alias_receipt_path = BASE / ('root-full095-' + name + '-ui-identity-retry-v1-metadata-alias.json')
assert all(not path.exists() and not path.is_symlink() for path in (standard_path, alias_path, alias_receipt_path))
data = (json.dumps(row, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
for path in (standard_path, alias_path):
    with path.open('xb') as handle:
        handle.write(data)
assert standard_path.read_bytes() == alias_path.read_bytes()
alias = {'kind': 'TWO_BYTE_IDENTICAL_METADATA_SNAPSHOTS_OF_ONE_ACTUAL_EXECUTION',
         'execution_name': name, 'actual_execution_count': 1, 'additional_execution_claimed': False,
         'standard_observation': ref(standard_path), 'versioned_observation': ref(alias_path),
         'actual_tool_observation': row['actual_tool_observation'], 'actual_completion': ref(job_path),
         'contract_binding': ref(binding_path), 'metadata_rows_byte_identical': True}
with alias_receipt_path.open('x', encoding='utf-8') as handle:
    json.dump(alias, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps(alias))
