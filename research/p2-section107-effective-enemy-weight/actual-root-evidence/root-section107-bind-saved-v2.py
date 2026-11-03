"""Root binds already completed actual artifacts; no project/native execution."""
from pathlib import Path
import datetime
import hashlib
import json

B = Path('/workspace/.continuation')
P = B / 'section107-saved-readback-source-v2'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    path = Path(path)
    assert not path.is_symlink() and path.is_file()
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def main():
    output = B / 'resume107-saved-readback-bindings-v2.json'
    assert not output.exists()
    manifest_raw = (P / 'MANIFEST.json').read_bytes()
    assert sha(manifest_raw) == '4e2734714d93289eae5f5fa368c1b68a9f06b04ce52037e2140e2bf10224dbf3'
    manifest = json.loads(manifest_raw)
    for row in manifest['payloads']:
        actual = pin(P / row['path'])
        assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
    assert pin(P / 'INDEPENDENT_SOURCE_REVIEW.md')['sha256'] == '4bb27cbd396253abce8a4464a67543400a17d257f5d6e541528c14e19cef435a'
    template_raw = (P / 'INACTIVE_BINDINGS_TEMPLATE.json').read_bytes()
    bindings = json.loads(template_raw)
    assert bindings['actual_runtime_ready'] is False
    assert sum(value is None for value in bindings.values()) == 13
    original = json.loads((B / 'section107-original-weight-actual-linux-v1/observations.json').read_bytes())
    candidate_api = json.loads((B / 'section107-candidate-weight-actual-linux-v2/observations.json').read_bytes())
    gold = json.loads((B / 'resume107-window-gold-v2/receipt.json').read_bytes())
    candidate = json.loads((B / 'resume107-window-candidate-v1/receipt.json').read_bytes())
    guard = json.loads((B / 'resume107-applied-source-v2.json').read_bytes())
    assert gold['passed'] is gold['workflow_complete'] is True
    assert candidate['passed'] is candidate['workflow_complete'] is True
    assert candidate['source_before'] == candidate['source_after'] == guard['source_sha256']
    assert candidate_api['source_before'] == candidate_api['source_after'] == guard['source_sha256']
    assert candidate['source_additional_before'] == candidate['source_additional_after'] == guard['source_additional_sha256']
    assert candidate['source_drift'] == candidate['Qt_errors'] == []
    visual_path = B / 'resume107-visual-audit-v1.json'
    visual = json.loads(visual_path.read_bytes())
    assert visual['passed'] is visual['workflow_complete'] is True
    assert visual['actually_viewed_images'] == len(visual['pngs']) == 4
    assert visual['candidate_receipt_sha256'] == pin(B / 'resume107-window-candidate-v1/receipt.json')['sha256']
    for png, viewed in zip(candidate['pngs'], visual['pngs']):
        assert viewed['actually_viewed'] is True and all(viewed[k] == v for k, v in png.items())
        actual = pin(B / 'resume107-window-candidate-v1' / png['file'])
        assert actual['bytes'] == png['bytes'] and actual['sha256'] == png['sha256']
    paths = {
        'original_primary': B / 'section107-original-weight-actual-linux-v1.exit-code',
        'original_receipt': B / 'section107-original-weight-actual-linux-v1/observations.json',
        'original_guard': Path(original['source_guard_path']),
        'candidate_API_primary': B / 'section107-candidate-weight-actual-linux-v2.exit-code',
        'candidate_API_receipt': B / 'section107-candidate-weight-actual-linux-v2/observations.json',
        'candidate_API_guard': B / 'resume107-applied-source-v2.json',
        'gold_primary': B / 'resume107-window-gold-v2.exit-code',
        'gold_receipt': B / 'resume107-window-gold-v2/receipt.json',
        'gold_guard': B / 'resume106-applied-source-v1.json',
        'candidate_primary': B / 'resume107-window-candidate-v1.exit-code',
        'candidate_receipt': B / 'resume107-window-candidate-v1/receipt.json',
        'candidate_guard': B / 'resume107-applied-source-v2.json',
        'visual': visual_path,
        'gold_window_runner': B / 'section107-window-source-v3/window107.py',
        'candidate_window_runner': B / 'section107-window-source-v4/window107.py',
    }
    for key, path in paths.items():
        if key.endswith('_primary'):
            assert path.read_bytes() == b'0\n'
        bindings[key] = pin(path)
    assert bindings['original_guard']['sha256'] == original['source_guard_sha256']
    assert bindings['candidate_API_guard']['sha256'] == candidate_api['source_guard_sha256']
    assert bindings['gold_guard']['sha256'] == gold['source_guard_sha256']
    assert bindings['candidate_guard']['sha256'] == candidate['source_guard_sha256']
    for value in bindings.values():
        if isinstance(value, dict) and {'path', 'bytes', 'sha256'} <= value.keys():
            assert pin(value['path']) == value
    assert not any(value is None for value in bindings.values())
    bindings.update(actual_runtime_ready=True, Source_only=False,
                    prepared_by='Root', prepared_at_UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    inactive_template_sha256=sha(template_raw), binding_writer_sha256=sha(Path(__file__).read_bytes()),
                    Saved_audit_executed_by_this_binding_writer=False,
                    instruction='Already collected actual artifacts bound; Root pure Saved audit remains a separate required execution.')
    with output.open('x', encoding='utf-8') as stream:
        json.dump(bindings, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'bindings': str(output), 'sha256': sha(output.read_bytes()), 'actual_artifacts_ready': True,
                      'Saved_pass_claimed': False}))


if __name__ == '__main__':
    main()
