"""Qualify the initial handoff's abbreviated parent without changing candidates."""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
original = HERE / 'HANDOFF.json'
packet = json.loads(original.read_bytes())
scope_path = ROOT / 'verification/sections/302-preparation/scope.json'
scope = json.loads(scope_path.read_bytes())
assert scope['section'] == 302 and scope['parent_commit'].startswith(packet['source_parent'])
packet['source_parent'] = scope['parent_commit']
packet['parent_identity_correction'] = {
    'original_handoff': 'HANDOFF.json', 'original_sha256': sha256(original.read_bytes()).hexdigest(),
    'original_value_was_abbreviated_not_false_branch': '87a622e',
    'root_scope': 'verification/sections/302-preparation/scope.json',
    'root_scope_sha256': sha256(scope_path.read_bytes()).hexdigest(),
    'candidate_source_data_or_tests_changed': False}
with (HERE / 'HANDOFF_FINAL.json').open('xb') as stream:
    stream.write((json.dumps(packet, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'handoff': 'HANDOFF_FINAL.json', 'sha256': sha256((HERE / 'HANDOFF_FINAL.json').read_bytes()).hexdigest(),
                  'candidate_changed': False, 'source_parent': packet['source_parent']}))
