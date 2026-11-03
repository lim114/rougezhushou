"""Root-only exact local application after the actual original MainWindow run."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
BASE = Path('/workspace/.continuation')
PACKET = BASE / 'section109-bounded-empty-candidate-source-v2'
TRANSPORT_SHA = '96060c7b3242d96dead272e4a0e06733b02794ddb9c986fae811e2e55166c35b'
GUARD = BASE / 'resume109-original-source-v1.json'
GUARD_SHA = 'fe4e11ac6a58cb7e9bc9a17c217ce8e7d0ad7e390770310ca2de30bcf6095ae2'

def sha(raw): return hashlib.sha256(raw).hexdigest()

def source_map():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
        for folder in ('rouge', 'tests', 'scripts') for p in sorted((ROOT / folder).rglob('*'))
        if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}

def main():
    guard_raw = GUARD.read_bytes(); assert sha(guard_raw) == GUARD_SHA
    original = json.loads(guard_raw)
    assert len(original['source_sha256']) == 751 and source_map() == original['source_sha256']
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
    prior = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert prior == 'f6fafd5cd81a0cbb485a5b724be7eca9acefdae4'
    assert (BASE / 'resume109-window-gold-v1.exit-code').read_bytes() == b'0\n'
    gold = json.loads((BASE / 'resume109-window-gold-v1/receipt.json').read_text())
    assert gold['passed'] is gold['workflow_complete'] is True
    assert gold['source_before'] == gold['source_after'] == original['source_sha256']
    assert len(gold['rows']) == 18 and len(gold['windows']) == 1 and not gold['Qt_errors']
    for relative, expected in original['source_additional_sha256'].items(): assert sha((ROOT / relative).read_bytes()) == expected
    raw = (PACKET / 'local-transports.json').read_bytes(); assert sha(raw) == TRANSPORT_SHA
    transport = json.loads(raw); pending = {}
    for entry in transport['existing_changed_files']:
        path = ROOT / entry['path']; before = path.read_bytes()
        assert len(before) == entry['before_bytes'] and sha(before) == entry['before_sha256']
        after = before
        for block in entry['blocks']:
            old, new = block['old'].encode(), block['new'].encode()
            assert after.count(old) == block['occurrences']; after = after.replace(old, new)
        assert len(after) == entry['after_bytes'] and sha(after) == entry['after_sha256']
        reverse = after
        for block in reversed(entry['blocks']): reverse = reverse.replace(block['new'].encode(), block['old'].encode())
        assert reverse == before; compile(after, str(path), 'exec'); pending[entry['path']] = after
    for entry in transport['new_files']:
        path = ROOT / entry['repo_path']; assert not path.exists()
        raw = (PACKET / entry['packet_path']).read_bytes()
        assert len(raw) == entry['bytes'] and sha(raw) == entry['sha256']
        compile(raw, str(path), 'exec'); pending[entry['repo_path']] = raw
    assert len(pending) == 8 and source_map() == original['source_sha256']
    output = BASE / 'resume109-applied-source-v1.json'; assert not output.exists()
    # Only Root writes tracked source. All incoming bytes and complete old state
    # are checked before the first write, and the final complete map is exact.
    expected = {**original['source_sha256'], **{name: sha(raw) for name, raw in pending.items()}}
    for name, raw in pending.items(): (ROOT / name).write_bytes(raw)
    actual = source_map(); assert actual == expected and len(actual) == 752
    for relative, expected_hash in original['source_additional_sha256'].items(): assert sha((ROOT / relative).read_bytes()) == expected_hash
    receipt = {'kind': 'ROOT_ACTUAL109_APPLIED_SOURCE_RUNTIME_PENDING', 'section': 109,
        'root_prior_HEAD': prior, 'source_sha256': actual,
        'source_additional_sha256': original['source_additional_sha256'],
        'changed_paths': sorted(pending), 'new_source_files': ['tests/test_empty_owner_acquisition_109.py'],
        'original_guard': str(GUARD), 'original_guard_sha256': GUARD_SHA,
        'transport_sha256': TRANSPORT_SHA, 'product_applied': True,
        'candidate_tests_completed': False, 'candidate_window_completed': False,
        'native_windows_game_chat_verified': False, 'section_completed': False}
    with output.open('x', encoding='utf-8') as handle: json.dump(receipt, handle, ensure_ascii=False, indent=2); handle.write('\n')
    print(json.dumps({'applied_paths': sorted(pending), 'source_files': len(actual), 'guard': str(output)}))

if __name__ == '__main__': main()
