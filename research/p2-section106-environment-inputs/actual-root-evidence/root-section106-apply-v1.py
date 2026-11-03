"""Root local section106 application; prepared only until real105 closure/Gold."""
import ast
import collections
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
BASE = Path('/workspace/.continuation')
PACKET = BASE / 'section106-environment-candidate-source-v2'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def unchanged_functions(raw, changed):
    return collections.Counter(ast.dump(node, include_attributes=False)
        for node in ast.walk(ast.parse(raw))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name not in changed)

def main():
    assert not (BASE / 'resume106-applied-source-v1.json').exists()
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    publication = json.loads((BASE / 'section105-publication-v1.json').read_bytes())
    assert publication['local_HEAD'] == publication['remote_HEAD'] == head
    assert publication['clean'] is True and publication['push_primary_exit'] == 0
    checkpoint = json.loads((ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes())
    assert checkpoint['completed_sections'] == 105 and checkpoint['next_section'] == 106
    assert checkpoint['full_validation_due'] is False
    guard = json.loads((BASE / 'resume105-applied-source-v1.json').read_bytes())
    assert len(guard['source_sha256']) == 748
    for name, want in {**guard['source_sha256'], **guard['source_additional_sha256']}.items():
        assert sha((ROOT / name).read_bytes()) == want, name
    gold_path = BASE / 'resume106-window-gold-v1/receipt.json'
    gold = json.loads(gold_path.read_bytes())
    assert (BASE / 'resume106-window-gold-v1.exit-code').read_bytes() == b'0\n'
    assert gold['passed'] is gold['workflow_complete'] is True
    assert gold['phase'] == 'gold' and len(gold['rows']) == 9
    assert gold['source_before'] == gold['source_after'] == guard['source_sha256']
    assert gold['source_additional_before'] == gold['source_additional_after'] == guard['source_additional_sha256']
    assert not gold['source_drift'] and not gold['Qt_errors']
    runner_raw = (BASE / 'section106-window-source-v1/window106.py').read_bytes()
    assert sha(runner_raw) == 'd4076884a45a8044778a6d358e1a4e54921edde7f6baeb545a3a4c35ed65d520'
    assert gold['runner_sha256'] == sha(runner_raw)
    original_path = BASE / 'section106-original-environment-actual-linux-v1/observations.json'
    assert sha(original_path.read_bytes()) == 'c09e542f3d1cee720c31daa638663a133bd1894268eb7bb20abc062ccfb92b25'
    assert (BASE / 'section106-original-environment-actual-linux-v1.exit-code').read_bytes() == b'0\n'
    assert sha((PACKET / 'INDEPENDENT_SOURCE_REVIEW.md').read_bytes()) == '651268ecb8ffe31232f63463d6032bdd2d88214f0ca24bb381861f5615b833cb'
    transport_raw = (PACKET / 'exact-local-transports.json').read_bytes()
    # Source pin is filled from the actual frozen packet, never guessed.
    assert len(transport_raw) == 7008
    assert sha(transport_raw) == '028063cf676eee596c07046fd009b18cf48b2bc71ed2665ac12fc477988e9624'
    transport = json.loads(transport_raw)
    assert len(transport['changes']) == 5
    assert transport['original_actual_receipt']['sha256'] == sha(original_path.read_bytes())
    outputs = {}
    for change in transport['changes']:
        name = change['path']; original = (ROOT / name).read_bytes()
        assert sha(original) == change['before_source_sha256'], name
        newline = change['newline']
        assert newline in ('\n', '\r\n')
        before = change['before'].replace('\n', newline).encode()
        after = change['after'].replace('\n', newline).encode()
        assert original.count(before) == 1, name
        raw = original.replace(before, after, 1)
        assert raw.count(after) == 1 and raw.replace(after, before, 1) == original
        assert sha(raw) == change['after_source_sha256'], name
        changed = set(change['changed_methods'])
        assert len(changed) == 1
        assert unchanged_functions(original, changed) == unchanged_functions(raw, changed), name
        assert sum(unchanged_functions(raw, changed).values()) == change['unchanged_method_count'], name
        old = [ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(original)) if isinstance(n, ast.FunctionDef) and n.name in changed]
        new = [ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(raw)) if isinstance(n, ast.FunctionDef) and n.name in changed]
        assert len(old) == len(new) == 1 and old != new, name
        outputs[name] = raw
    test_name = 'tests/test_environment_input_106.py'
    assert not (ROOT / test_name).exists()
    test_raw = (PACKET / 'test_environment_input_106.py').read_bytes()
    assert len(test_raw) == 15174
    assert sha(test_raw) == '6cd75f91e466daa6b231a6e318b44795f596a2b8d292c0fd6939329117521a8e'
    outputs[test_name] = test_raw
    cloud = 'scripts/verify_cloud.py'; cloud_raw = (ROOT / cloud).read_bytes()
    needle = b'MODULES = (\n'; insert = b'    "tests.test_environment_input_106",\n'
    assert cloud_raw.count(needle) == 1 and insert not in cloud_raw
    outputs[cloud] = cloud_raw.replace(needle, needle + insert, 1)
    assert outputs[cloud].replace(needle + insert, needle, 1) == cloud_raw
    for name, raw in outputs.items():
        compile(raw, name, 'exec')
    for name, raw in outputs.items():
        (ROOT / name).write_bytes(raw)
    sources = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
        for folder in ('rouge', 'tests', 'scripts')
        for p in sorted((ROOT / folder).rglob('*'))
        if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
    assert len(sources) == 749
    assert set(sources) - set(guard['source_sha256']) == {test_name}
    assert set(guard['source_sha256']) - set(sources) == set()
    assert {key for key in guard['source_sha256'] if sources[key] != guard['source_sha256'][key]} == set(outputs) - {test_name}
    for name, want in guard['source_additional_sha256'].items():
        assert sha((ROOT / name).read_bytes()) == want
    receipt = {'section': 106, 'status': 'ACTUALLY_APPLIED_RUNTIME_PENDING',
        'baseline_HEAD': head, 'actual_prior_publication': publication,
        'applied_at_Beijing': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
        'source_sha256': sources, 'source_additional_sha256': guard['source_additional_sha256'],
        'source_count': 749, 'changed_paths': sorted(outputs),
        'exact_local_transport_sha256': sha(transport_raw),
        'original_actual_environment_observations_sha256': sha(original_path.read_bytes()),
        'actual_healthy_Gold_receipt_sha256': sha(gold_path.read_bytes()),
        'test_source_sha256': sha(test_raw), 'window_source_sha256': sha(runner_raw),
        'scope': ['Mode alias eligibility', 'Active bool enemy level identity', 'Non-text source report', 'UI and summary eligibility'],
        'native_windows_verified': False}
    with (BASE / 'resume106-applied-source-v1.json').open('x') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps({'section': 106, 'applied': True, 'source_files': len(sources), 'changed_paths': sorted(outputs)}))

if __name__ == '__main__':
    main()
