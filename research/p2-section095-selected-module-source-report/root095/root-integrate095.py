"""Root-only apply of frozen report code after actual94 and baseline acceptance."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
CODE = LOCAL / 'p2-report095-candidate-v1'
REVIEW = LOCAL / 'p2-report095-final-code-source-review'
HEAD = 'f509d186e501bfcfd042e45b46e398ec756840ec'
GUARD = '259370708fe45e974511d1c1c010901d66981ee9dc2d53e7bce1ac978d463211'
MANIFEST = '216d5c31a9bc89dbc51f0b875db073a4fe8ea8b85fb5c9b624f5d9d6f56a461a'
FORMAL = 'a5121ed38fe8be09a1137a3b1fb5ed63662b65ead7a79488ab2030e960600d8b'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def maintained():
    return {p.relative_to(ROOT).as_posix(): sha(p)
            for base in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / base).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json')
            and '__pycache__' not in p.parts}


def completion(number):
    receipt_path = ROOT / f'verification/sections/{number:03d}.json'
    closure_path = LOCAL / f'section{number:03d}-archived-working-tree-closure.json'
    receipt = json.loads(receipt_path.read_bytes())
    closure = json.loads(closure_path.read_bytes())
    assert receipt['section'] == closure['section'] == number
    assert receipt['passed'] is receipt['workflow_complete'] is True
    assert closure['all_archive_index_blobs_exact'] is True
    assert closure['actual_HEAD_unchanged'] == HEAD
    archive = ROOT / receipt['research_archive']
    manifest = archive / 'archive-manifest.json'
    assert sha(manifest) == closure['archive_manifest_sha256']
    rows = json.loads(manifest.read_bytes())
    actual = {p.relative_to(archive).as_posix() for p in archive.rglob('*')
              if p.is_file()}
    assert actual == set(rows) | {'archive-manifest.json'}
    assert not any(p.is_symlink() for p in archive.rglob('*'))
    assert len(actual) == closure['archive_files']
    staged = {}
    for entry in subprocess.check_output(
            ['git', 'ls-files', '--stage', '-z', '--', str(archive.relative_to(ROOT))],
            cwd=ROOT).split(b'\0'):
        if entry:
            meta, name = entry.split(b'\t', 1)
            staged[name.decode()] = meta.decode().split()[1]
    assert set(staged) == {str((archive / name).relative_to(ROOT)) for name in actual}
    for name in actual:
        path = archive / name
        raw = path.read_bytes()
        if name != 'archive-manifest.json':
            assert len(raw) == rows[name]['bytes'] and sha(path) == rows[name]['sha256']
        key = str(path.relative_to(ROOT))
        assert staged[key] == hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    return {'receipt_path': str(receipt_path), 'receipt_sha256': sha(receipt_path),
            'closure_path': str(closure_path), 'closure_sha256': sha(closure_path)}


def gates():
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT,
                                   text=True).strip() == 'codex/p2-development'
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                   text=True).strip() == HEAD
    guard_path = LOCAL / 'root-source-094.json'
    assert sha(guard_path) == GUARD
    guard = json.loads(guard_path.read_bytes())
    assert guard['passed'] is True and maintained() == guard['source_sha256_after']
    checkpoint = json.loads((ROOT / 'DEVELOPMENT_CHECKPOINT.json').read_bytes())
    assert checkpoint['completed_sections'] == 94
    assert checkpoint['policy']['commit_after_full_validation_pass'] is True
    assert checkpoint['policy']['push_after_batch_commit'] is True
    chain = {str(n): completion(n) for n in (93, 94)}
    assert chain['94']['receipt_sha256'] == '55dba304fe8075531e92de36f369c142f790da59ef69091edffc28299b97bac5'
    assert chain['94']['closure_sha256'] == '613d5956762bd7b0a19d15c15173df698890a8545a8d0e14253086aaf728f806'
    for name in ('root-baseline094-for095.exit-code',
                 'root-saved-baseline094-for095-review.exit-code'):
        assert (LOCAL / name).read_bytes() == b'0\n'
    saved_path = LOCAL / 'root-saved-baseline094-for095-review.json'
    saved = json.loads(saved_path.read_bytes())
    baseline_path = Path('/workspace/.compat/wine-module-report-baseline-094-for095.json')
    baseline = json.loads(baseline_path.read_bytes())
    assert saved['passed'] is baseline['passed'] is baseline['workflow_complete'] is True
    assert saved['actual_runtime_receipt_sha256'] == sha(baseline_path)
    native = baseline_path.with_name(baseline['records']['file'])
    assert saved['actual_native_archive_sha256'] == sha(native)
    assert baseline['source_sha256_before'] == baseline['source_sha256_after'] == guard['source_sha256_after']
    mf = CODE / 'public-code-artifacts-manifest095.json'
    assert sha(mf) == MANIFEST
    files = json.loads(mf.read_bytes())['files']
    assert len(files) == 5 and len({row['destination_repo_path'] for row in files}) == 5
    for row in files:
        path = Path(row['source_path'])
        assert path.resolve().is_relative_to(CODE.resolve())
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
        assert row['destination_repo_path'] in (
            'rouge/module_source_reference.py', 'rouge/data/module-source-reference.json',
            'tests/test_selected_module_source_reference.py',
            'rouge/reporting.py', 'scripts/verify_cloud.py')
    rp = REVIEW / 'formal-code-source-review095.json'
    assert sha(rp) == FORMAL
    formal = json.loads(rp.read_bytes())
    assert formal['source_gate_passed'] is True and formal['runtime_pass'] is False
    assert formal['code_manifest_sha256'] == MANIFEST
    assert formal['base_source_guard_sha256'] == GUARD
    assert formal['interface_sha256'] == sha(CODE / 'implementation-code-freeze095.json')
    inverse_path = CODE / 'exact-inverse095.json'
    assert sha(inverse_path) == 'a13975cd7492d53c4c94f9e66e11f5d28e04ce332591c330d9525489de7d3c86'
    for row in json.loads(inverse_path.read_bytes())['changed_files']:
        old = (ROOT / row['path']).read_bytes()
        new = (CODE / 'candidate' / row['path']).read_bytes()
        assert hashlib.sha256(old).hexdigest() == row['before_sha256']
        assert hashlib.sha256(new).hexdigest() == row['after_sha256']
        restored = new
        for edit in reversed(row['edits']):
            before, after = edit['old'].encode(), edit['new'].encode()
            assert restored.count(after) == 1
            restored = restored.replace(after, before, 1)
        assert restored == old
    correction = CODE / 'interface-tail-correction095.json'
    assert sha(correction) == '7d3d57a2e71dd2f321e1a288486a708d5a4bfd7baa238ccacdafbf3383124a6e'
    correction_json = json.loads(correction.read_bytes())
    assert correction_json['actual_complete_append_tail_prefix'] == '\n\n【所选模组原件追溯】\n'
    assert correction_json['exact_code_product_manifest_sha256'] == MANIFEST
    return guard, files, chain, {'path': str(saved_path), 'sha256': sha(saved_path)}


phase = sys.argv[1]
guard, files, chain, saved = gates()
if phase == 'prepare':
    save(LOCAL / 'root-integration-plan095.json',
         {'format_version': 1, 'passed': True, 'actual_HEAD_unchanged92': HEAD,
          'actual94_guard_sha256': GUARD, 'completed93_94_chain': chain,
          'actual94_Wine_baseline_saved_review': saved,
          'code_manifest_sha256': MANIFEST, 'formal_source_review_sha256': FORMAL,
          'candidate_files': files, 'root_only_apply_not_yet_performed': True,
          'project_calls': 0, 'technical_tail_old_interface_correction_explicitly_bound': True})
    print(json.dumps({'prepare_PASS': True, 'applied': False, 'project_calls': 0}))
elif phase == 'apply':
    plan = json.loads((LOCAL / 'root-integration-plan095.json').read_bytes())
    assert plan['candidate_files'] == files and plan['completed93_94_chain'] == chain
    old_map = guard['source_sha256_after']
    expected = dict(old_map)
    for row in files:
        expected[row['destination_repo_path']] = row['sha256']
    for row in files:
        destination = ROOT / row['destination_repo_path']
        if row['destination_repo_path'] not in old_map:
            assert not destination.exists()
    for row in files:
        (ROOT / row['destination_repo_path']).write_bytes(Path(row['source_path']).read_bytes())
    after = maintained()
    assert after == expected
    changed = [name for name in old_map if old_map[name] != after[name]]
    new = sorted(set(after) - set(old_map))
    assert sorted(changed) == ['rouge/reporting.py', 'scripts/verify_cloud.py'] and len(new) == 3
    save(LOCAL / 'root-integration-applied095.json',
         {'format_version': 1, 'passed': True, 'root_only_apply': True,
          'candidate_bytes_exact': True, 'changed_paths': changed + new, 'project_calls': 0})
    save(LOCAL / 'root-source-095.json',
         {'format_version': 1, 'passed': True, 'actual_base_section': 94,
          'actual_HEAD_unchanged92': HEAD, 'base_source_guard_sha256': GUARD,
          'actual94_completed_working_tree_binding': chain['94'],
          'completed93_94_chain': chain, 'actual94_Wine_baseline_saved_review': saved,
          'old_maintained': len(old_map), 'current_maintained': len(after),
          'unchanged_maintained': len(old_map) - len(changed),
          'changed_maintained': changed, 'new_maintained': new,
          'source_sha256_after': after, 'candidate_bytes_exact': True,
          'formal_code_source_review_sha256': FORMAL, 'project_calls': 0,
          'section095_completed': False, 'full095_runtime_PASS': False})
    print(json.dumps({'applied': True, 'current_maintained': len(after),
                      'unchanged_maintained': len(old_map) - len(changed),
                      'new_maintained': new, 'project_calls': 0}))
else:
    raise ValueError(phase)
