"""Bind actual completed root window attempt2 to the approved saved-only audit."""
import hashlib
import json
from pathlib import Path

LOCAL = Path('/workspace/.continuation')
OUTPUT = Path('/workspace/.compat/focused095-window-attempt2')
PACK = LOCAL / 'focused095-saved-validator-pending-v4'
REVIEW = LOCAL / 'focused095-saved-validator-v4-formal-source-review'

def ref(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def checked(path, expected):
    value = ref(path)
    assert value['sha256'] == expected, path
    return value

formal_path = REVIEW / 'formal-source-review-saved-helper095-v4.json'
formal_ref = checked(formal_path, '4f77cccec5c25c0af3e46147ed1bb723c7dc0418bd55ee32d66fb34acf78ff0b')
formal = json.loads(formal_path.read_bytes())
assert formal['source_gate_passed'] is True and formal['runtime_pass'] is False
helper_ref = checked(PACK / 'verify_saved_focused095.py', formal['helper_sha256'])
manifest_ref = checked(PACK / 'public-artifacts-manifest-saved-validator095.json', formal['helper_manifest_sha256'])
prelaunch_ref = checked(LOCAL / 'root-window-095-attempt2-prelaunch.json', '41eca6d5c074d620e6f29651162811216a91944f4c1eb21243946f9b322e1e5d')
prelaunch = json.loads(Path(prelaunch_ref['path']).read_bytes())
primary = LOCAL / 'root-window-095-attempt2.exit-code'
assert primary.read_bytes() == b'0\n', 'Root must first observe actual successful process completion.'
receipt = OUTPUT / 'wine-module-report-window-095.json'
runtime = json.loads(receipt.read_bytes())
assert runtime['passed'] is True and runtime['workflow_complete'] is True
assert runtime['runtime_attempt'] == 2 and runtime['output_directory'] == str(OUTPUT)
assert runtime['source_drift'] == []
assert prelaunch['runner']['sha256'] == formal['actual_final_runner_sha256']
spec = json.loads((PACK / 'input-spec-template095.json').read_bytes())
spec.update(status='ROOT_ACTUAL_FOCUSED095_SAVED_INPUTS_READY', preparation_only=False,
            no_new_runtime_or_captured0_claim=False, receipt=ref(receipt),
            records=ref(OUTPUT / 'wine-module-report-window-095-records.json.gz'),
            primary_exit=ref(primary), root_prelaunch=prelaunch_ref,
            saved_helper_manifest=manifest_ref, saved_helper_source_review=formal_ref,
            root_observed_session_id=12020)
spec['PNGs'] = [ref(OUTPUT / name) for name in (
    'wine-module-report-095-normal-gate.png', 'wine-module-report-095-technical-raw.png',
    'wine-module-report-095-normal-dedicated.png')]
spec['root_launch'].update(actual_primary_exit_captured=True, actual_primary_exit_code=0,
    argv=prelaunch['actual_argv'], cwd=prelaunch['cwd'], primary_exit=spec['primary_exit'])
for key in ('runner', 'manifest', 'formal_review'):
    assert spec['root_launch'][key] == spec[{'runner': 'final_runner', 'manifest': 'final_manifest',
                                          'formal_review': 'final_source_review'}[key]]
assert spec['verifier_sha256'] == helper_ref['sha256']
target = LOCAL / 'root-focused095-saved-input-spec.json'
with target.open('x', encoding='utf-8') as stream:
    json.dump(spec, stream, ensure_ascii=False, allow_nan=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': spec['status'], 'spec': ref(target),
                  'actual_primary_status': 0, 'saved_audit_executed': False}, ensure_ascii=False))
