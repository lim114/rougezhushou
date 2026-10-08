"""Check the applied root source/registry bytes, without running provenance APIs."""
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('root', type=Path)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
freeze = json.loads((HERE / 'review-freeze090.json').read_bytes())
transport = json.loads((HERE / 'root89-transport090.json').read_bytes())
checked = []
for item in freeze['product_files']:
    raw = (args.root / item['path']).read_bytes()
    assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], item['path']
    if item['path'].endswith('.py'):
        assert b'\r\n' not in raw, item['path']
    checked.append(item)
registry = (args.root / transport['registry_path']).read_bytes()
literal = transport['registry_entry_literal'].encode()
assert len(registry) == transport['proposed_registry_bytes']
assert sha(registry) == transport['proposed_registry_sha256']
assert registry.count(literal) == 1
inverse = registry.replace(literal, b'', 1)
assert len(inverse) == transport['baseline_registry_bytes']
assert sha(inverse) == transport['baseline_registry_sha256']
for item in transport['source_files']:
    raw = (args.root / item['path']).read_bytes()
    assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], item['path']
report = {
    'format_version': 1, 'passed': True, 'root': str(args.root),
    'baseline_commit': transport['root_baseline_commit'], 'actual_root_tag': transport['actual_root_tag'],
    'frozen_product_files_checked': checked,
    'unchanged_source_file_count': len(transport['source_files']),
    'registry_inverse_to_actual_root89_exact': True,
    'historical_manifest_generator_and_production_data_unchanged': True,
    'source21_transport_only_not_full301_102_or315_closure': True,
    'CLI_verifier_application_helper_formatter_test_source_parser_network_Qt_Wine_calls': 0}
raw = (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode()
if args.output:
    with args.output.open('xb') as stream:
        stream.write(raw)
print(raw.decode(), end='')
