"""Root only: complete selector coverage and a real portable CJK test fixture."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace/rougezhushou')
BASE = Path('/workspace/.continuation')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def assertions(raw):
    return [ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(raw))
            if isinstance(n, ast.Assert)]


def main():
    output = BASE / 'resume105-applied-source-v1.json'
    assert not output.exists()
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    publication = json.loads((BASE/'section104-publication-v1.json').read_bytes())
    assert publication['local_HEAD'] == publication['remote_HEAD'] == head and publication['clean'] is True
    guard = json.loads((BASE/'resume104-applied-source-v1.json').read_bytes())
    assert len(guard['source_sha256']) == 748
    for name, want in {**guard['source_sha256'], **guard['source_additional_sha256']}.items():
        assert sha((ROOT/name).read_bytes()) == want, name
    registry_raw = (BASE/'section105-registry-completion-source-v1/append-selectors.json').read_bytes()
    assert sha(registry_raw) == '9ec9862991674baccd8d42ef71a27a2efd4630e94e4a1be7e1436c8cd2efab73'
    font_raw = (BASE/'section105-portable-font-fixture-source-v1/local-transport.json').read_bytes()
    assert sha(font_raw) == '7a78448839416bff03fca7baf5f2bc086518f795ede7bc0a6afc2777a911d6c9'
    registry = json.loads(registry_raw)
    font = json.loads(font_raw)
    outputs = {}
    name = 'scripts/verify_full_available.py'
    original = (ROOT/name).read_bytes()
    assert sha(original) == registry['base_helper_sha256']
    old = registry['old_assignment'].encode()
    new = registry['replacement_assignment'].encode()
    assert original.count(old) == 1
    revised = original.replace(old, new, 1)
    assert revised.replace(new, old, 1) == original
    assert sha(revised) == registry['expected_result_sha256_for_this_base_only']
    before_tree = ast.parse(original)
    after_tree = ast.parse(revised)
    before_nodes = [ast.dump(n, include_attributes=False) for n in before_tree.body
                    if not (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'NEW_MODULES' for t in n.targets))]
    after_nodes = [ast.dump(n, include_attributes=False) for n in after_tree.body
                   if not (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'NEW_MODULES' for t in n.targets))]
    assert before_nodes == after_nodes
    outputs[name] = revised
    name = font['target_file']
    original = (ROOT/name).read_bytes()
    assert sha(original) == font['base_source_sha256']
    newline = '\r\n' if b'\r\n' in original else '\n'
    revised = original
    transports = []
    for edit in font['replacements']:
        old = edit['old'].replace('\n', newline).encode()
        new = edit['new'].replace('\n', newline).encode()
        assert revised.count(old) == 1
        revised = revised.replace(old, new, 1)
        transports.append((old, new))
    restored = revised
    for old, new in reversed(transports):
        assert restored.count(new) == 1
        restored = restored.replace(new, old, 1)
    assert restored == original
    assert sha(revised) == font['expected_composed_source_sha256_for_this_base_only']
    assert assertions(original) == assertions(revised)
    outputs[name] = revised
    for name, raw in outputs.items():
        compile(raw, name, 'exec')
    # Complete all local/inverse/AST checks before the two authorized writes.
    for name, raw in outputs.items():
        (ROOT/name).write_bytes(raw)
    sources = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
               for folder in ('rouge', 'tests', 'scripts')
               for p in sorted((ROOT/folder).rglob('*'))
               if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
    assert set(sources) == set(guard['source_sha256']) and len(sources) == 748
    assert {key for key in sources if sources[key] != guard['source_sha256'][key]} == set(outputs)
    for name, want in guard['source_additional_sha256'].items():
        assert sha((ROOT/name).read_bytes()) == want
    receipt = {'section': 105, 'status': 'ACTUALLY_APPLIED_RUNTIME_PENDING',
               'baseline_HEAD': head, 'source_count': 748, 'source_sha256': sources,
               'source_additional_sha256': guard['source_additional_sha256'],
               'changed_paths': sorted(outputs), 'actual_prior_publication': publication,
               'original_assertions_unchanged': True, 'classifier_unchanged': True,
               'registered_new_selectors': 20, 'portable_font_is_native_msyh_alias': False}
    with output.open('x') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'section': 105, 'applied': True, 'source_files': 748,
                      'changed_paths': sorted(outputs)}))


if __name__ == '__main__':
    main()
