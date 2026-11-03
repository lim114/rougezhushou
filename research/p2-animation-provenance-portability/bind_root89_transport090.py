"""Bind frozen product bytes to the root's actual section-089 tag; no tests."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('root', type=Path)
parser.add_argument('commit')
args = parser.parse_args()
assert re.fullmatch('[0-9a-f]{40}', args.commit)
sha = lambda raw: hashlib.sha256(raw).hexdigest()
tag = subprocess.check_output(['git', 'rev-parse', 'p2-section-089^{commit}'], cwd=args.root).decode().strip()
assert tag == args.commit, 'The actual root section-089 tag must match the supplied commit'
freeze = json.loads((HERE / 'review-freeze090.json').read_bytes())
registry_proposal = json.loads((HERE / 'registry-proposal090.json').read_bytes())
literal = registry_proposal['new_entry_literal'].encode()
registry = subprocess.check_output(['git', 'show', args.commit + ':scripts/verify_cloud.py'], cwd=args.root)
assert literal not in registry and registry.count(b'MODULES = (\n') == 1
proposed = registry.replace(b'MODULES = (\n', b'MODULES = (\n' + literal, 1)
assert proposed.count(literal) == 1 and proposed.replace(literal, b'', 1) == registry
frozen_readme = (HERE / 'baseline/README.md').read_bytes()
actual_readme = subprocess.check_output(['git', 'show', args.commit + ':README.md'], cwd=args.root)
assert actual_readme == frozen_readme, 'README transport requires review if it changed'
old_transport = json.loads((HERE / 'source-transport-619090.json').read_bytes())
transport = []
for item in old_transport['files']:
    rel = item['repository_path']
    raw = subprocess.check_output(['git', 'show', args.commit + ':' + rel], cwd=args.root)
    assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], rel
    transport.append({'path': rel, 'bytes': len(raw), 'sha256': sha(raw),
                      'actual_git_commit': args.commit})
for rel in ('scripts/verify_original_animation_provenance.py', 'tests/test_original_animation_provenance.py'):
    result = subprocess.run(['git', 'cat-file', '-e', args.commit + ':' + rel], cwd=args.root, capture_output=True)
    assert result.returncode == 128, 'A proposed new path already exists: ' + rel
result = subprocess.run(['git', 'apply', '--check', str(HERE / 'product090.patch')], cwd=args.root,
                        capture_output=True, text=True)
assert result.returncode == 0, result.stderr
for name, raw in [('root89-verify_cloud.py', registry), ('registered-verify_cloud090-root89.py', proposed)]:
    with (HERE / name).open('xb') as stream:
        stream.write(raw)
report = {
    'format_version': 1, 'status': 'ACTUAL_ROOT89_TRANSPORT_PASS_NO_NEW_TESTS',
    'root_baseline_commit': args.commit, 'actual_root_tag': 'p2-section-089',
    'source_files': transport, 'frozen_product_files': freeze['product_files'],
    'README_baseline_inverse_still_exact': True, 'patch_apply_check_passed': True,
    'registry_path': 'scripts/verify_cloud.py', 'registry_entry_literal': literal.decode(),
    'baseline_registry_bytes': len(registry), 'baseline_registry_sha256': sha(registry),
    'proposed_registry_bytes': len(proposed), 'proposed_registry_sha256': sha(proposed),
    'proposed_registry_inverse_to_actual_root89_exact': True,
    'author_28_passed_verifier_entries_not_repeated': True,
    'new_CLI_verifier_application_helper_formatter_test_parser_network_Qt_Wine_calls': 0}
with (HERE / 'root89-transport090.json').open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'transport_passed': True, 'root89': args.commit,
                  'actual_source_files': len(transport), 'new_verifier_or_test_entries': 0}))
