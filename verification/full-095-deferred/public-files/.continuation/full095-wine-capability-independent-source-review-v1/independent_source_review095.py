"""Independent file/AST/JSON audit only; never imports reviewed sources."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath

HERE = Path(__file__).resolve().parent
PACKET = Path('/workspace/.continuation/full095-wine-capability-retry-pending-v1')
ROOT = Path('/workspace/rougezhushou')
checks = []

def ref(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def read_json(path):
    return json.loads(Path(path).read_bytes())

def check(label, passed, evidence=None):
    checks.append({'id': f'S{len(checks)+1:02d}', 'check': label,
                   'passed': bool(passed), 'evidence': evidence})

def text(path):
    return Path(path).read_text(encoding='utf-8')

def node_source(source, name, cls=None):
    tree = ast.parse(source)
    scope = tree.body
    if cls:
        scope = next(n.body for n in scope if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in scope if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
    return ast.get_source_segment(source, node), {'start_line': node.lineno, 'end_line': node.end_lineno}

def has_all(source, values):
    return all(value in source for value in values)

mf_path = PACKET / 'public-artifacts-manifest-wine-capability095.json'
mf_before = ref(mf_path)
mf = read_json(mf_path)
hand = read_json(PACKET / 'final-handoff-wine-capability095.json')
rows = mf['payload_files']
check('Frozen author STOPWRITE and SOURCE-only status', hand['stopwrite'] is True
      and hand['runtime_pass'] is False and hand['source_gate_passed'] is False
      and hand['source_manifest'] == mf_before and mf['runtime_pass'] is False)
physical = {str(path.relative_to(PACKET)) for path in PACKET.rglob('*') if path.is_file()}
expected = {row['name'] for row in rows} | {mf_path.name, 'final-handoff-wine-capability095.json'}
check('Exact 13 regular physical files and 11 unique payload members', physical == expected
      and len(physical) == 13 and len(rows) == 11 and len({row['name'] for row in rows}) == 11
      and all(not path.is_symlink() and (path.is_file() or path.is_dir()) for path in PACKET.rglob('*')))
check('All actual SOURCE payload paths, lengths and SHA match frozen manifest',
      all(row['path'] == str(PACKET / row['name'])
          and ref(row['path']) == {key: row[key] for key in ('path', 'bytes', 'sha256')} for row in rows))
contract = read_json(PACKET / 'source-contract-wine-capability095.json')
inverse = read_json(PACKET / 'whole-source-inverse-wine-capability095.json')
check('Future formal/recovery/runtime prerequisites remain null and runtime flags false',
      all(value is None for value in contract['future_runtime_prerequisites'].values())
      and contract['runtime_pass'] is False and contract['section_completion_increment'] == 0
      and contract['agent_target_executions'] == contract['agent_project_imports']
      == contract['agent_tests_run'] == contract['agent_wine_executions'] == 0)
full = text(PACKET / 'wine_full095_capability_retry.py')
selected = text(PACKET / 'wine_selected095_capability.py')
shared = text(PACKET / 'wine_symlink_capability095.py')
for name, source in (('wine_full', full), ('wine_selected', selected)):
    ast.parse(source)
    delta = inverse[name]
    original_data = Path(delta['original']['path']).read_bytes()
    recovered = source
    unique = True
    for operation in reversed(delta['operations']):
        unique = unique and recovered.count(operation['new']) == 1
        recovered = recovered.replace(operation['new'], operation['old'], 1)
    maintained = ROOT / 'scripts' / ('verify_full_available.py' if name == 'wine_full' else 'verify_cloud.py')
    check(name + ' complete original byte inverse, seven exact uniquely selected deltas',
          unique and len(delta['operations']) == 7 and recovered.encode() == original_data == maintained.read_bytes(),
          {'original': ref(maintained), 'candidate': ref(delta['candidate']['path'])})
    check(name + ' actual runner refs and future exact Wine argv match frozen handoff',
          contract['runners'][name] == hand['runners'][name] == ref(delta['candidate']['path'])
          and contract['execution_argv'][name] == hand['execution_argv'][name]
          and contract['execution_argv'][name][0] == '/workspace/.compat/run-wine-python.sh'
          and contract['execution_argv'][name][1] == str(PureWindowsPath('Z:/' + delta['candidate']['path'].lstrip('/')))
          and contract['execution_argv'][name][2] == '--wine')
ast.parse(shared)
original_full = text(ROOT / 'scripts/verify_full_available.py')
original_selected = text(ROOT / 'scripts/verify_cloud.py')
for name in ('AvailableResult', 'unmigrated_path'):
    check('Original ' + name + ' body and classifier taxonomy remain byte exact',
          node_source(full, name)[0] == node_source(original_full, name)[0])
check('Original full selectors, deduplication, MODULES import and standard loader expression preserved',
      has_all(full, ["selectors = list(dict.fromkeys(historical['test_modules'] + list(NEW_MODULES) + list(MODULES)))",
                    'from verify_cloud import MODULES', 'unittest.defaultTestLoader.loadTestsFromNames(selectors)']))
def assigned_literal(source, name):
    tree = ast.parse(source)
    return ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign)
                                and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)))
check('Selected MODULES exact literal order and complete original entries unchanged',
      assigned_literal(selected, 'MODULES') == assigned_literal(original_selected, 'MODULES'))
check('Original full 342 maintained classifier map is separate from adapter source map',
      "*ROOT.glob('tests/test_*.py'), ROOT / 'scripts/verify_full_available.py']" in full
      and "before != capability_probe['prior_failed_source_sha256']" in full
      and 'adapter_sources_before' in full and 'adapter_source_drift' in full)
references = contract['runtime_evidence_references']
check('Every actual original failure, independent root probe and pinned source/DLL reference hashes match',
      all(ref(row['path']) == row for row in references.values()), {'reference_count': len(references)})
failed = read_json(references['old_failed_full_receipt']['path'])
ids = assigned_literal(shared, 'TEST_IDS')
check('Only the exact two actual pre-product failing symlink fixture IDs are allowlisted',
      list(ids) == contract['allowlisted_test_ids']
      and tuple(row['test'] for row in failed['failed_cases']) == ids
      and failed['available_checks_passed'] is False and failed['failures'] == failed['errors'] == 1
      and Path(references['old_failed_primary_exit']['path']).read_bytes() == b'1\n'
      and len(failed['source_sha256']) == 342 and failed['source_drift'] == [])
guard = read_json(references['maintained_source_guard']['path'])
guard_map = guard['source_sha256_after']
actual_map = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for folder in ('rouge', 'tests', 'scripts') for path in sorted((ROOT / folder).rglob('*'))
              if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
check('Actual maintained 735-file source map matches original source guard; no tracked change by adapter',
      len(guard_map) == 735 and actual_map == guard_map)
classifier_paths = {*ROOT.glob('rouge/**/*.py'), *ROOT.glob('rouge/data/**/*.json'),
                    *ROOT.glob('tests/test_*.py'), ROOT / 'scripts/verify_full_available.py'}
classifier_map = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in sorted(classifier_paths)}
check('Actual original classifier scope is exactly 342 and equals failed receipt',
      len(classifier_map) == 342 and classifier_map == failed['source_sha256'])
prior_text = text(references['root_capability_probe_log']['path'])
prior, _ = json.JSONDecoder().raw_decode(prior_text.lstrip())
check('Actual retained root probe zero observes both absent and existing target phantom links',
      Path(references['root_capability_probe_exit']['path']).read_bytes() == b'0\n'
      and prior['platform'] == 'Windows' and prior['python'] == '3.12.10'
      and prior['project_imports'] == 0 and prior['private_state_access'] is False
      and len(prior['observations']) == 2
      and all(row['target_present'] is present and row['creation'] == {'returned_type': 'NoneType', 'returned_repr': 'None'}
              and row['is_symlink'] is False and row['exists'] is False
              and row['lstat']['error_type'] == row['readlink']['error_type'] == 'FileNotFoundError'
              and row['lstat']['winerror'] == row['readlink']['winerror'] == 2
              and row['target_bytes_unchanged'] is True
              for row, present in zip(prior['observations'], (False, True), strict=True)))
admit, anchors = node_source(shared, 'admit_installed_wine')
check('Admission rejects implicit platform labels and requires actual explicit Windows CPython 3.12.10',
      has_all(admit, ["wine is not True or os.name != 'nt' or platform.system() != 'Windows'",
                     "platform.python_version() != '3.12.10'", 'raise RuntimeError']), anchors)
check('Wine-specific ntdll export must actually return nonempty strict-decoded version; native Windows fails closed',
      has_all(admit, ["ctypes.CDLL('ntdll')", 'wine_version = ntdll.wine_get_version',
                     'returned = wine_version()', 'if not returned:', "returned.decode('ascii', errors='strict')",
                     'native Windows cannot use this skip']), anchors)
active, active_anchors = node_source(shared, '_active_module_reference')
check('Active module identity uses GetModuleHandleW and GetModuleFileNameW then hashes actual opened module bytes',
      has_all(active, ['kernel32.GetModuleHandleW', 'kernel32.GetModuleFileNameW',
                      'get_name(handle, buffer, len(buffer))', 'file_reference(Path(buffer.value))',
                      "actual['sha256'] != expected_sha", 'raise RuntimeError'])
      and assigned_literal(shared, 'KERNELBASE_SHA') == references['installed_kernelbase']['sha256']
      and assigned_literal(shared, 'NTDLL_SHA') == references['installed_ntdll']['sha256'], active_anchors)
check('Both active diagnosed DLL identities are required before loading project suites',
      has_all(admit, ["_active_module_reference('kernelbase.dll', KERNELBASE_SHA)",
                     "_active_module_reference('ntdll.dll', NTDLL_SHA)"])
      and full.index('capability_probe = admit_installed_wine') < full.index('from verify_cloud import MODULES')
      and selected.index('capability_probe = admit_installed_wine') < selected.index('unittest.defaultTestLoader.loadTestsFromNames(MODULES)'))
check('Fresh two-shape probes use unmodified os.symlink in default Temp with same-volume checks and actual evidence',
      has_all(admit, ["Path(tempfile.gettempdir())", 'tempfile.TemporaryDirectory(',
                     'base.drive.casefold() != Path(default_temp).drive.casefold()',
                     'for present in (False, True):', 'os.symlink(target, link)',
                     'link.is_symlink()', 'link.exists()', "('lstat', 'readlink', 'read_bytes')",
                     'sorted(p.name for p in base.iterdir())', 'target.read_bytes() == original',
                     "Path(prior['observations'][0]['link']).drive.casefold() != Path(default_temp).drive.casefold()"]), anchors)
phantom, phantom_anchor = node_source(shared, '_phantom_success')
check('Unknown probe/exception/real symlink/changed target states fail closed and cannot skip',
      has_all(phantom, ["row.get('target_present') is present", "creation == {'returned_type': 'NoneType', 'returned_repr': 'None'}",
                       "row.get('is_symlink') is False", "row.get('exists') is False", "== 'FileNotFoundError'",
                       "get('winerror') == 2", "row.get('target_bytes_unchanged') is True", "actual_directory_entries"])
      and has_all(admit, ['if not all(_phantom_success', 'strict=True', 'no tests skipped']), phantom_anchor)
suite, suite_anchors = node_source(shared, 'admit_suite')
check('Suite nesting and leaf order retained; all nonallowlisted original case objects return unchanged',
      has_all(suite, ['unittest.TestSuite(walk(child) for child in current)',
                     'if current.id() in TEST_IDS:', 'return FixtureCapabilitySkip(current.id())', 'return current',
                     'set(admitted) != set(TEST_IDS) or len(admitted) != 2', 'Repeated prerequisite case']), suite_anchors)
skip, skip_anchors = node_source(shared, 'FixtureCapabilitySkip')
check('Replacement is an independent unittest skip body with same ID and no original method mutation',
      has_all(skip, ["super().__init__('runTest')", 'return self.original_id', 'self.skipTest(SKIP_REASON)'])
      and not any(isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign))
                  and any(isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                          and t.value.id in ('os', 'Path', 'AccountCache', 'AccountCache093Tests')
                          for t in (n.targets if isinstance(n, ast.Assign) else [n.target]))
                  for n in ast.walk(ast.parse(shared))), skip_anchors)
check('Both records explicitly deny original fixture execution and product assertion success',
      has_all(suite, ["'kind': 'environment_capability'", "'classification': 'declared_skip'",
                     "'pre_product_fixture_admission': True", "'actually_executed': False",
                     "'fixture_body_run': False", "'product_assertions_passed': False",
                     "'original_failure_preserved': True"]), suite_anchors)
validate, validate_anchors = node_source(shared, 'validate_result_capability_skips')
check('Actual result must record exactly two honest skips with exact original IDs and reasons',
      has_all(validate, ['result.skipped if test.id() in TEST_IDS', "[(row['test'], SKIP_REASON) for row in records]",
                        'if actual != expected:', 'raise RuntimeError']), validate_anchors)
check('Capability skips are explicitly counted passed zero and complete repository validation remains false',
      has_all(full, ["'capability_skips_counted_passed': 0", "and not capability_records and not adapter_drift"])
      and has_all(selected, ['"capability_skips_counted_passed": 0', '"complete_repository_validation": False'])
      and "args.require_complete and (result.unavailable or capability_records)" in full)
check('Original product errors and failures remain failures; adapter source drift blocks success',
      has_all(full, ["receipt['available_checks_passed'] = receipt['available_checks_passed'] and not adapter_drift",
                     "return 1 if not receipt['available_checks_passed']"])
      and 'result.wasSuccessful() and not adapter_drift else 1' in selected)
check('All 84 original historical skip identities and reasons remain in untouched standard result handling',
      failed['historical_or_declared_skips'] == len(failed['skips']) == 84
      and node_source(full, 'AvailableResult')[0] == node_source(original_full, 'AvailableResult')[0]
      and not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                  and n.func.attr in ('patch', 'mock', 'setattr') for n in ast.walk(ast.parse(shared))))
check('Full retry sinks are fresh, unique and distinct from preserved original failed sinks; selected untouched sinks are unused',
      all(not Path(path).exists() for kind in contract['outputs'].values() for path in kind.values())
      and len({path for kind in contract['outputs'].values() for path in kind.values()}) == 6
      and not ({path for kind in contract['outputs'].values() for path in kind.values()}
               & {row['path'] for row in references.values()}))
readme = text(PACKET / 'README.md')
check('SOURCE contract records real Linux/native gaps and class-transition read-only setup nuance without claiming runtime',
      'setUpClass' in readme and 'fixture' in readme and 'Native Windows' in readme
      and contract['fixture_class_transition'].startswith('Independent skip cases')
      and contract['native_windows_integration_verified'] is False)
check('Frozen packet remains unchanged after independent SOURCE inspection',
      mf_before == ref(mf_path) and all(ref(row['path']) == {key: row[key] for key in ('path', 'bytes', 'sha256')} for row in rows))
passed = all(row['passed'] for row in checks)
report = {'format_version': 1, 'section': 95, 'checked_at': datetime.now(timezone.utc).isoformat(),
          'status': 'PASS_INDEPENDENT_SOURCE_ONLY_RUNTIME_NOT_EXECUTED' if passed else 'BLOCK_INDEPENDENT_SOURCE_ONLY',
          'source_gate_passed': passed, 'runtime_pass': False,
          'manifest_sha256': mf_before['sha256'], 'source_manifest': mf_before,
          'runners': contract['runners'], 'shared_admission': contract['shared_admission'],
          'shared_helper_sha256': contract['shared_admission']['sha256'],
          'execution_argv': contract['execution_argv'], 'execution_cwd': contract['execution_cwd'],
          'source_contract': ref(PACKET / 'source-contract-wine-capability095.json'),
          'whole_source_inverse': ref(PACKET / 'whole-source-inverse-wine-capability095.json'),
          'observed_inputs': references, 'checks': checks, 'source_checks': len(checks),
          'blocking_checks': [row for row in checks if not row['passed']],
          'reviewer_operations': 'Only own stdlib file/SHA/JSON/AST checker and manual source reading; no imports of reviewed helpers or targets.',
          'agent_target_executions': 0, 'agent_project_imports': 0, 'agent_tests_run': 0,
          'agent_codec_executions': 0, 'agent_wine_executions': 0, 'agent_git_executions': 0,
          'tracked_edits': 0, 'native_windows_verified': False, 'section_completion_increment': 0,
          'future_root_recovery_spec_review': None, 'future_root_recovery_context': None,
          'future_actual_adapter_primary_exits': None,
          'required_future_root_actions': ['Bind and independently SOURCE-review actual recovery spec SHA before seal.',
              'Run only after immutable actual recovery context starts; capture both fresh actual adapter outcomes.',
              'Preserve old failure, actual Linux passes, remaining original eight gates and real UI/saved/PNG/native proofs.'],
          'precision_notes': [
              'Two exact symlink fixture bodies do not run under the diagnosed phantom stub; replacement skip bodies do run and are not product passes.',
              'All other original leaf case objects and order remain; standard unittest can repeat unchanged read-only setUpClass at replacement class transitions.',
              '84 old historical skips are preserved by whole original result/source inverse; future totals are not predicted.',
              'Wine capability unavailable plus historical/private missing prerequisites keep complete repository validation false; native Windows remains required.']}
report_path = HERE / 'formal-independent-source-review-wine-capability095-v1.json'
with report_path.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2); stream.write('\n')
manifest = {'format_version': 1, 'section': 95, 'status': 'STOPWRITE_INDEPENDENT_SOURCE_REVIEW_ONLY',
            'payload_files': [ref(HERE / 'independent_source_review095.py'), ref(report_path)],
            'runtime_pass': False, 'source_packet_manifest': mf_before}
review_mf_path = HERE / 'public-artifacts-manifest-independent-wine-capability095-v1.json'
with review_mf_path.open('x', encoding='utf-8') as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2); stream.write('\n')
handoff = {'format_version': 1, 'section': 95, 'status': 'STOPWRITE_FORMAL_SOURCE_REVIEW_RUNTIME_PENDING',
           'stopwrite': True, 'source_gate_passed': passed, 'runtime_pass': False,
           'report': ref(report_path), 'manifest': ref(review_mf_path), 'source_checks': len(checks),
           'review_pointers': {name: {'source_pass': '/source_gate_passed', 'runtime_pass': '/runtime_pass',
                                    'runner_sha256': '/runners/' + name + '/sha256',
                                    'argv': '/execution_argv/' + name} for name in ('wine_full', 'wine_selected')},
           'future_actual_root_recovery': None, 'target_executions': 0}
with (HERE / 'handoff-independent-wine-capability095-v1.json').open('x', encoding='utf-8') as stream:
    json.dump(handoff, stream, ensure_ascii=False, indent=2); stream.write('\n')
print(json.dumps({'source_gate_passed': passed, 'source_checks': len(checks),
                  'blocking_checks': report['blocking_checks'], 'report': ref(report_path),
                  'manifest': ref(review_mf_path), 'handoff': ref(HERE / 'handoff-independent-wine-capability095-v1.json')}))
raise SystemExit(0 if passed else 1)
