"""Read SOURCE/AST/SHA only; no target, project, test, codec, Qt or Wine imports."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

PACKET = Path(__file__).resolve().parent
ROOT = Path('/workspace/rougezhushou')


def ref(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def source_node(source, name):
    node = next(node for node in ast.parse(source).body
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.Assign))
                and (getattr(node, 'name', None) == name or
                     isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)))
    return ast.get_source_segment(source, node)


def main():
    checks = []

    def require(name, condition, evidence=None):
        checks.append({'id': 'A%02d' % (len(checks) + 1), 'check': name,
                       'passed': bool(condition), 'evidence': evidence})
        if not condition:
            raise AssertionError(name)

    contract = json.loads((PACKET / 'source-contract-wine-capability095.json').read_text())
    inverse = json.loads((PACKET / 'whole-source-inverse-wine-capability095.json').read_text())
    texts = {}
    for name in ('wine_full', 'wine_selected'):
        data = inverse[name]
        original = Path(data['original']['path']).read_text()
        source = Path(data['candidate']['path']).read_text()
        require(name + ' exact original and candidate physical references',
                ref(Path(data['original']['path'])) == data['original']
                and ref(Path(data['candidate']['path'])) == data['candidate'])
        restored = source
        for change in reversed(data['operations']):
            require(name + ' inverse replacement occurs exactly once', restored.count(change['new']) == 1)
            restored = restored.replace(change['new'], change['old'], 1)
        require(name + ' whole-source inverse restores original bytes', restored == original)
        ast.parse(source)
        texts[name] = (source, original)
    full, original_full = texts['wine_full']
    selected, original_selected = texts['wine_selected']
    shared = (PACKET / 'wine_symlink_capability095.py').read_text()
    shared_ast = ast.parse(shared)
    require('Original classifier still the maintained 6555B source',
            len(original_full.encode()) == 6555 and hashlib.sha256(original_full.encode()).hexdigest()
            == 'ea4481c9cd95fb9438f673b76c14c9386263469e12b2855fa04e9a47d7c63dcc')
    require('Complete original AvailableResult classification and pass/error/subtest counting unchanged',
            source_node(full, 'AvailableResult') == source_node(original_full, 'AvailableResult'))
    require('Original missing-cache/native-client classification unchanged',
            source_node(full, 'unmigrated_path') == source_node(original_full, 'unmigrated_path'))
    require('Original six additional full selectors unchanged',
            source_node(full, 'NEW_MODULES') == source_node(original_full, 'NEW_MODULES'))
    require('All original selected MODULES order and bytes unchanged',
            source_node(selected, 'MODULES') == source_node(original_selected, 'MODULES'))
    selected_node = next(n for n in ast.parse(selected).body if isinstance(n, ast.Assign)
                         and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'MODULES')
    require('Original selected selector count is actual 107', len(ast.literal_eval(selected_node.value)) == 107)
    selector_line = "selectors = list(dict.fromkeys(historical['test_modules'] + list(NEW_MODULES) + list(MODULES)))"
    require('Original full selector deduplication expression untouched', selector_line in full and selector_line in original_full)
    require('Original full receipt literal unchanged',
            full[full.index('    receipt = {'):full.index('\n    validate_result_capability_skips')]
            == original_full[original_full.index('    receipt = {'):original_full.index("\n    with args.output.open")])
    evidence = contract['runtime_evidence_references']
    require('Every bound original failure/probe/source/binary reference is physical and exact',
            all(ref(Path(r['path'])) == r for r in evidence.values()), list(evidence))
    failed = json.loads(Path(evidence['old_failed_full_receipt']['path']).read_text())
    require('Prior primary exit 1 remains physical', Path(evidence['old_failed_primary_exit']['path']).read_bytes() == b'1\n')
    require('Independent root capability probe primary exit 0 remains physical',
            Path(evidence['root_capability_probe_exit']['path']).read_bytes() == b'0\n')
    files = [*ROOT.glob('rouge/**/*.py'), *ROOT.glob('rouge/data/**/*.json'),
             *ROOT.glob('tests/test_*.py'), ROOT / 'scripts/verify_full_available.py']
    maintained = {p.relative_to(ROOT).as_posix(): ref(p)['sha256'] for p in sorted(set(files))}
    require('Exact original classifier map 342 stays the actual original classifier selection',
            len(maintained) == 342 and maintained == failed['source_sha256'])
    guard = json.loads(Path(evidence['maintained_source_guard']['path']).read_text())
    require('All 735 currently sealed maintained source bytes remain unchanged',
            len(guard['source_sha256_after']) == 735
            and all(ref(ROOT / k)['sha256'] == value for k, value in guard['source_sha256_after'].items()))
    ids_node = next(n for n in shared_ast.body if isinstance(n, ast.Assign)
                    and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'TEST_IDS')
    ids = list(ast.literal_eval(ids_node.value))
    require('Skip allowlist is exactly the two original failed prerequisites',
            ids == contract['allowlisted_test_ids'] == [row['test'] for row in failed['failed_cases']])
    skip_class = next(n for n in shared_ast.body if isinstance(n, ast.ClassDef) and n.name == 'FixtureCapabilitySkip')
    skip_method = next(n for n in skip_class.body if isinstance(n, ast.FunctionDef) and n.name == 'runTest')
    require('Replacement body only declares skip and never calls product/test fixture code',
            len(skip_method.body) == 1 and isinstance(skip_method.body[0], ast.Expr)
            and isinstance(skip_method.body[0].value, ast.Call)
            and isinstance(skip_method.body[0].value.func, ast.Attribute)
            and skip_method.body[0].value.func.attr == 'skipTest')
    imported = [n.module for n in ast.walk(shared_ast) if isinstance(n, ast.ImportFrom)]
    require('Shared admission imports no project/test modules',
            not any(name and (name.startswith('rouge') or name.startswith('tests')) for name in imported))
    require('No monkeypatch/setattr/sitecustomize hooks',
            all(word not in shared for word in ('mock.', 'setattr(', 'sitecustomize', '__unittest_skip__')))
    require('Both real loaded suite expressions retained exactly once',
            full.count('unittest.defaultTestLoader.loadTestsFromNames(selectors)') == 1
            and selected.count('unittest.defaultTestLoader.loadTestsFromNames(MODULES)') == 1)
    require('Actual capability admission precedes both real loader calls',
            full.index('capability_probe = admit_installed_wine') < full.index('loadTestsFromNames(selectors)')
            and selected.index('capability_probe = admit_installed_wine') < selected.index('loadTestsFromNames(MODULES)'))
    require('Native identity absence and nonmatching probe fail closed before any skip body',
            "native Windows cannot use this skip" in shared
            and "Fresh fixture capability does not match" in shared)
    require('Installed kernelbase and ntdll pins match actual SOURCE contracts',
            evidence['installed_kernelbase']['sha256'] in shared
            and evidence['installed_ntdll']['sha256'] in shared)
    require('Adapter source/contract provenance is separate from original maintained map',
            'adapter_sources_before' in full and 'adapter_sources_after' in full
            and "ROOT / 'scripts/verify_full_available.py'" in source_node(full, 'source_hashes'))
    require('Actual capability skips are checked against unittest result skip IDs/reasons',
            'validate_result_capability_skips(result, capability_records)' in full
            and 'validate_result_capability_skips(result, capability_records)' in selected)
    require('Complete validation never true for the admitted unavailable fixtures',
            "and not capability_records and not adapter_drift" in full
            and '"complete_repository_validation": False' in selected)
    require('Require-complete retains failed-first order and fails for capability skips',
            "return 1 if not receipt['available_checks_passed'] else (2 if args.require_complete and (result.unavailable or capability_records) else 0)" in full)
    require('Full/selected execution argv and all output sinks are still unexecuted/fresh',
            all(not Path(value).exists() for sinks in contract['outputs'].values() for value in sinks.values()))
    require('Contract claims SOURCE-only with actual runtime prerequisites null',
            contract['runtime_pass'] is False and contract['agent_target_executions'] == 0
            and all(value is None for value in contract['future_runtime_prerequisites'].values()))
    report = {'format_version': 1, 'section': 95,
              'checked_at': datetime.now(timezone.utc).isoformat(),
              'status': 'AUTHOR_SOURCE_ONLY_CHECKS_PASSED_PENDING_INDEPENDENT_REVIEW',
              'author_source_gate_passed': True, 'source_gate_passed': False,
              'runtime_pass': False, 'formal_source_review': None,
              'checks': checks, 'checks_passed': len(checks),
              'runners': contract['runners'], 'execution_argv': contract['execution_argv'],
              'shared_admission': ref(PACKET / 'wine_symlink_capability095.py'),
              'contract': ref(PACKET / 'source-contract-wine-capability095.json'),
              'agent_target_executions': 0, 'agent_project_imports': 0,
              'agent_tests_run': 0, 'agent_wine_executions': 0,
              'tracked_edits': 0, 'git_mutations': 0, 'section_completion_increment': 0,
              'actual_counts_not_predictable_from_source': True,
              'native_windows_integration_verified': False}
    with (PACKET / 'author-source-only-checks-wine-capability095-final.json').open('x', encoding='utf-8') as out:
        json.dump(report, out, ensure_ascii=False, indent=2)
        out.write('\n')
    print(json.dumps({'status': report['status'], 'checks_passed': len(checks), 'runtime_pass': False}))


if __name__ == '__main__':
    main()
