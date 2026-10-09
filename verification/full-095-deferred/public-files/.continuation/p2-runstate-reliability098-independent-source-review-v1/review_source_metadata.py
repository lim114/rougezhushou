"""Independent read-only metadata/AST review; never execute project code."""
import ast
import hashlib
import json
from pathlib import Path

PACKET = Path('/workspace/.continuation/p2-runstate-reliability098-candidate-source-v1')
OUTPUT = Path(__file__).resolve().parent

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def ref(path):
    path = Path(path)
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': digest(raw)}

def load(name):
    return json.loads((PACKET / name).read_bytes())

def span(raw, node):
    return b''.join(raw.splitlines(keepends=True)[node.lineno - 1:node.end_lineno])

def methods(raw):
    tree = ast.parse(raw)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'RunState')
    return {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}

def modules(raw):
    tree = ast.parse(raw)
    assignment = next(n for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'MODULES' for t in n.targets))
    return ast.literal_eval(assignment.value)

for name in ('formal-independent-source-review-runstate098.json', 'final-handoff.json',
             'public-artifacts-manifest.json'):
    if (OUTPUT / name).exists():
        raise FileExistsError('Fresh output required: ' + name)

whole = load('public-artifacts-manifest.json')
verified = []
for row in whole['artifacts']:
    current = ref(PACKET / row['relative_path'])
    assert current['bytes'] == row['bytes'] and current['sha256'] == row['sha256']
    verified.append(current)
assert len(verified) == whole['artifact_count'] == 32
assert sum(r['bytes'] for r in verified) == whole['total_bytes']
physical = sorted(str(p.relative_to(PACKET)) for p in PACKET.rglob('*') if p.is_file())
assert physical == sorted([r['relative_path'] for r in whole['artifacts']]
                          + ['public-artifacts-manifest.json'])

code = load('public-code-artifacts-manifest.json')
assert len(code['files']) == 3
assert code['runtime_executed'] is False and code['Product_PASS'] is None
assert all(v is None for v in code['future_guards_results'].values())
for row in code['files']:
    current = ref(row['path'])
    assert current['bytes'] == row['bytes'] and current['sha256'] == row['sha256']
    if row['expected_old'] is not None:
        previous = ref(row['expected_old']['path'])
        assert previous['bytes'] == row['expected_old']['bytes']
        assert previous['sha256'] == row['expected_old']['sha256']

fixed = load('fixed-source-evidence.json')
original_refs = []
for row in fixed['past_Root_proof_copies'] + fixed['source_consumers_producer_and_valid_legacy_refs']:
    original = ref(row['original']['path'])
    copied = ref(row['copy']['path'])
    assert original == row['original'] and copied == row['copy']
    assert Path(original['path']).read_bytes() == Path(copied['path']).read_bytes()
    original_refs.append(original)
assert len(original_refs) == 16
assert ref('/workspace/rougezhushou/rouge/run_state.py')['sha256'] == code['expected_current_RunState_sha256']
assert ref(fixed['future097_Source_registry_original']['path']) == fixed['future097_Source_registry_original']

inverse = load('exact-source-inverse.json')
inverse_proofs = []
for row in inverse['files']:
    destination = row['destination_repo_path']
    candidate = (PACKET / destination).read_bytes()
    baseline = (PACKET / 'baseline' / destination).read_bytes()
    assert digest(candidate) == row['expected_exact_candidate_sha256']
    restored = candidate
    operations = []
    for operation in reversed(row['operations_apply_in_reverse_order']):
        old = bytes.fromhex(operation['old_bytes_hex'])
        new = bytes.fromhex(operation['new_bytes_hex'])
        assert restored.count(new) == 1
        restored = restored.replace(new, old, 1)
        operations.append({'id': operation['id'], 'unique_source_span': True,
                           'old_bytes': len(old), 'new_bytes': len(new)})
    assert restored == baseline and digest(restored) == row['restored_exact_old_sha256']
    inverse_proofs.append({'file': destination, 'operations': operations,
                          'whole_baseline_exact': True, 'restored': ref(PACKET / 'baseline' / destination)})
new_test = inverse['new_file_inverse']
assert ref(PACKET / new_test['destination_repo_path'])['sha256'] == new_test['exact_candidate_sha256']
assert not Path('/workspace/rougezhushou/tests/test_run_state_reliability.py').exists()

old_raw = (PACKET / 'baseline/rouge/run_state.py').read_bytes()
new_raw = (PACKET / 'rouge/run_state.py').read_bytes()
old_methods = methods(old_raw)
new_methods = methods(new_raw)
assert list(old_methods) == list(new_methods)
unchanged = []
changed = []
for name in old_methods:
    old_span = span(old_raw, old_methods[name])
    new_span = span(new_raw, new_methods[name])
    if old_span != new_span:
        changed.append(name)
    else:
        unchanged.append({'method': name, 'whole_bytes': len(new_span), 'sha256': digest(new_span),
                          'baseline_line': old_methods[name].lineno,
                          'candidate_line': new_methods[name].lineno, 'whole_bytes_equal': True})
assert changed == ['__init__', 'apply'] and len(unchanged) == 14
assert new_raw.count(b'\n') == new_raw.count(b'\r\n')
old_registry = (PACKET / 'baseline/scripts/verify_cloud.py').read_bytes()
new_registry = (PACKET / 'scripts/verify_cloud.py').read_bytes()
old_modules = modules(old_registry)
new_modules = modules(new_registry)
assert new_modules[0] == 'tests.test_run_state_reliability' and new_modules[1:] == old_modules

test_raw = (PACKET / 'tests/test_run_state_reliability.py').read_bytes()
test_tree = ast.parse(test_raw)
test_methods = [{'class': cls.name, 'method': n.name, 'line': n.lineno, 'end_line': n.end_lineno}
                for cls in test_tree.body if isinstance(cls, ast.ClassDef)
                for n in cls.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
assert len(test_methods) == 17
assert sum(r['class'] == 'RunStateCacheShapeTests' for r in test_methods) == 8
assert sum(r['class'] == 'RunStateInventoryCountQualificationTests' for r in test_methods) == 9
assertion_sites = sum(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                      and n.func.attr.startswith('assert') for n in ast.walk(test_tree))
compile_only = []
for filename in ('rouge/run_state.py', 'tests/test_run_state_reliability.py', 'scripts/verify_cloud.py'):
    raw = (PACKET / filename).read_bytes()
    ast.parse(raw)
    compile(raw, str(PACKET / filename), 'exec', dont_inherit=True)
    compile_only.append({'file': ref(PACKET / filename), 'AST_parsed': True,
                         'in_memory_compile_only': True, 'code_object_executed': False})

past = load('evidence/Root-past-actual-lead-observations.json')
assert past['status'] == 'ACTUAL_LEAD_OBSERVATIONS_COLLECTED'
assert past['Product_PASS'] is None and past['completed_section_increment'] == 0
assert len(past['cases']) == 14 and all(r['Product_PASS'] is None for r in past['cases'])
assert all(v is None for v in past['future_guards'].values())
assert past['source_before'] == past['source_after'] and past['source_before_after_equal735'] is True
past_case_rows = []
for row in past['cases']:
    consumers = row.get('consumers')
    consumer_rows = ([{'call': item['call'], 'outcome': item['outcome'],
                      'exception_type': (item.get('exception') or {}).get('type')}
                     for item in consumers] if isinstance(consumers, list) else consumers)
    past_case_rows.append({'id': row['id'], 'kind': row['kind'],
                          'constructor_outcome': row['constructor']['outcome'],
                          'constructor_exception_type': (row['constructor'].get('exception') or {}).get('type'),
                          'consumers': consumer_rows, 'Product_PASS': None})

checks = [
    ('whole_manifest', 'All 32 payload refs and exact physical-file inventory verified; manifest itself separately bound.'),
    ('code_transport', 'Exactly RunState, new meaningful regression module, and one registry insertion; none applied.'),
    ('source_preconditions', 'Current RunState original and future097 Source registry exact; actual future097 equality still required.'),
    ('whole_inverse', 'Two production insertions and one registry insertion independently reverse to complete expected-old bytes.'),
    ('unchanged_methods', 'All 14 other RunState methods whole-byte equal; changed methods only __init__ and apply.'),
    ('preinstall_gate', 'Candidate22-29 rejects outer consumed structures before saved state.update30, restoration or possible save34.'),
    ('existing_protection', 'ValueError uses original except path36-38; reset(save=False) bootstrap13-16 and save/reset methods unchanged.'),
    ('consumer_contract', 'Operator/relic records .get, maps .items/graph .get and history event .get have real fixed-source consumers.'),
    ('legacy_qualification', 'No added deep/ID/numeric/provenance schema; missing maps/history, empty dict/list, opaque extra leaves untouched.'),
    ('bool_local_copy', 'Candidate274 copies incoming relics;275-276 only native bool simultaneously changes local count and local copied field.'),
    ('bool_consumer_order', 'Normalization precedes reconcile323-324 and expected/count/full_bar/removal343-382; both consumers see None.'),
    ('early_error_order', 'Stale/cross-run254-258 and existing member validation260-272 remain before normalization; no broadened exception catch.'),
    ('nonbool_preservation', 'All other input values take original whole Source flow; original crew bool normalization383-384 exact retained.'),
    ('caller_contract', 'New assignment does not address original caller; nested icon copying and other reconciliation are original unchanged methods.'),
    ('regression_tests', '17 actual Source testmethods,8+9; baseline seeds/full persisted raw, caller graph, int0/int1/None and valid-restart contrasts.'),
    ('test_native_identity', 'Caller receipt inspects types, insertion order, float.hex and within-one-fixture id/ref/cycle; not cross-time alias proof.'),
    ('past_evidence', 'Original16dd collection and16 Source/proof original-copy refs exact;14 cases and551 source frame-entry rows are historical collection.'),
    ('recognition_scope', 'Sealed scope erratum retained; normal resolver imports possible; no whole-project zero recognition API inference.'),
    ('future_admission', 'Plan/codeMF/handoff guard slots remain NULL; Source registry is unapplied future097, not completed prerequisite.'),
    ('runtime_plan', 'Fresh actual baseline/candidate raw/native pairing, regressions, real Wine MainWindow and saved+restart required before product acceptance.'),
    ('compile_only', 'Three candidate sources parse/compile in memory without executing code objects, project imports or tests.'),
    ('second_source_view', 'Second read-only reviewer found no new production blocker; confirmed17 tests and existing deeper consumer risks.'),
]
residuals = [
    {'id': 'history_outer_branch_coverage_gap', 'classification': 'Required future actual098 paired acceptance fixture',
     'source': 'candidate28 checks history list before event dictionaries; tests98 has history[None] only',
     'finding': 'No direct new test fixture covers history present but non-list. Add fresh actual baseline/candidate public fixture before098 acceptance; do not modify frozen candidate packet.',
     'actual_reproduced_here': False, 'new_production_regression_identified': False},
    {'id': 'maps_nodes_and_clearing_history', 'classification': 'Existing deeper consumed-shape Source risk outside five leads',
     'source': 'candidate45-50; baseline36-41 same whole method',
     'finding': 'graph dictionary with nodes=None or null node can still reach iteration/get; clearing recovery with matching history event missing kind can reach event["kind"]. Gate does not authenticate nodes/event keys.',
     'actual_reproduced_here': False, 'new_production_regression_identified': False},
    {'id': 'record_nested_sources_and_icon_evidence', 'classification': 'Existing deeper record Source risk',
     'source': 'candidate111/178/586; whole restore_origin_discovery_buffs/restore_relic_icon_memory/summary unchanged',
     'finding': 'member.sources=None can still reach .get when preceding repair predicates match; relic.icon_evidence=None can reach .get in eligible migration or summary. Outer dict qualification does not cover those fields.',
     'actual_reproduced_here': False, 'new_production_regression_identified': False},
    {'id': 'other_containers_and_unknown_ids', 'classification': 'Existing Source risks intentionally unqualified',
     'source': 'candidate541/579/586/592-598; same old consumers',
     'finding': 'tactical_tools/resources/config malformed containers or records and unknown catalog/operator IDs can still fail downstream. No full-schema or all-loaded-caches certification.',
     'actual_reproduced_here': False, 'new_production_regression_identified': False},
    {'id': 'RunState_consumer_acceptance_not_MainWindow_acceptance', 'classification': 'Concrete separate GUI prerequisite',
     'source': 'tests178-191 versus fixed source-refs/rouge/app.py790-798 especially794',
     'finding': 'Truthy member {public_nullable:None} in the RunState visible-consumers fixture has no fields. Selected member with run training enabled reaches member["fields"].items in existing app Source. A future passing four-consumer RunState test cannot certify whole MainWindow startup or valid GUI cache.',
     'required': 'Future actualWine legacy fixtures explicitly cover all consumed fields; retain unqualified partial-member outcomes as separate evidence. No newly reproduced GUI fault claim.',
     'actual_reproduced_here': False, 'new_production_regression_identified': False},
    {'id': 'None_semantics_and_historical_counts', 'classification': 'Narrow inventory contract qualification',
     'source': 'candidate194-196 and343-382; tests249-271/193-209',
     'finding': 'Incoming bool equals the existing unread-None path; that path may use prior count/memory. This does not repair saved bool counts, guarantee no removals under all legacy states, or establish actual OCR bool production.',
     'actual_reproduced_here': False, 'new_production_regression_identified': False},
    {'id': 'save_IO_and_unicode', 'classification': 'Unchanged RunState save risks and future prerequisite',
     'source': 'candidate70-75 whole-byte same baseline save',
     'finding': 'RunState mkdir/write/replace and UTF8 serialization unchanged; future097 concerns AccountCache only. No RunState IO/Unicode repair or actual completed097 claim.'},
]
runtime_gaps = [
    'Actual095 saved batch/publication refs and actual completed096/097 Source guards and receipts are still NULL.',
    'Actual098 fresh complete maintenance before/after source guards, source/layout/data/runtime environment freeze and new-test absence must be verified.',
    'No final reviewed Linux paired runner or actual baseline/candidate return/exception/native/raw results exist in this packet.',
    'History non-list present fixture must be included in fresh actual baseline/candidate acceptance; counts are derived from actual logs.',
    '17 Source methods and144 assertion sites are not actual discovery/run/assertion counts; related regressions and final registry remain unrun.',
    'Real Wine MainWindow isolated startup/application/reset/selection/report/calculation/close-restart/save PNG and receipts are unrun.',
    'Root past collection primary0 is not productPASS or098baseline; nativeWindows/game/OCR/private corruption frequency remain unverified.',
]
report = {
    'status': 'QUALIFIED_INDEPENDENT_SOURCE_REVIEW_PASSED_NOT_RUNTIME_ADMITTED',
    'reviewer': '/root/runstate098_independent_candidate_source_review_v1',
    'passed': True, 'Source_review_passed': True,
    'scope': 'Independent exact metadata/AST/whole-byte and human Source review of sealed candidate; no runtime product verification.',
    'runtime_executed': False, 'project_imports_executed': False, 'tests_executed': False,
    'Product_PASS': None, 'completed_section_increment': 0, 'runtime_admission': False,
    'actual_runtime_results': None, 'actualguardsandresults': None,
    'actual_future_guards_results': code['future_guards_results'],
    'candidate_whole_manifest': ref(PACKET / 'public-artifacts-manifest.json'),
    'candidate_code_manifest': ref(PACKET / 'public-code-artifacts-manifest.json'),
    'candidate_RunState': ref(PACKET / 'rouge/run_state.py'),
    'candidate_test': ref(PACKET / 'tests/test_run_state_reliability.py'),
    'candidate_registry': ref(PACKET / 'scripts/verify_cloud.py'),
    'all_candidate_payload_refs_verified': verified,
    'original_and_copy_refs_verified': original_refs,
    'physical_packet_file_count': len(physical), 'whole_manifest_payload_count': len(verified),
    'exact_inverse_proofs_metadata_only': inverse_proofs,
    'production_method_count_Source': len(new_methods),
    'production_changed_methods': changed, 'unchanged_whole_methods': unchanged,
    'original_CRLF_all_preserved': True,
    'Source_registry_module_counts': {'future097_expected_old': len(old_modules), 'candidate': len(new_modules)},
    'all_old_registry_modules_same_order': True,
    'new_test_methods_Source_only': test_methods,
    'new_test_methods_Source_count': len(test_methods), 'Source_assertion_call_sites': assertion_sites,
    'actual_test_discovery_run_or_assertion_counts': None,
    'compile_only_proofs': compile_only,
    'past_original_actual_collection': {'file': ref(PACKET / 'evidence/Root-past-actual-lead-observations.json'),
        'Root_observation': ref(PACKET / 'evidence/Root-past-observation.json'),
        'case_rows': past_case_rows, 'source_body_frame_entry_rows': len(past['RunState_method_entry_log']),
        'entry_scope': 'Includes module/class/generator/lambda entries; not551 unique methods or all-project helper/API calls.',
        'actual_imported_source_rows': len(past['actual_imported_source_log']), 'Product_PASS': None,
        'is_actual098_baseline': False},
    'qualified_Source_checks': [{'id': k, 'Source_passed': True, 'finding': v} for k,v in checks],
    'Source_blocking_findings': [],
    'concrete_qualifications_and_unreproduced_existing_risks': residuals,
    'required_actual_verification_gaps': runtime_gaps,
    'Source_review_conclusion': 'No new production Source defect identified in the two insertions. Qualified only for later exact-source transport after real097 prerequisites and fresh review; no fullschema/GUI/game/runtime certification.',
    'second_Source_reviewer': {'name': '/root/runstate098_independent_candidate_source_review_v1/consumed_shape_residuals',
        'read_only': True, 'runtime_executed': False, 'reported_new_production_blockers': [],
        'reported_tests_Source_count': 17, 'reported_extra_qualification': 'RunState four-consumer fixtures do not certify MainWindow member[fields] consumers.'},
    'review_metadata_inspection_limit': 'Past receipt consumers have list rows on completed constructors and dict not-called sentinel on raised constructors; their schema was inspected without project codecs.'
}

report_path = OUTPUT / 'formal-independent-source-review-runstate098.json'
with report_path.open('xb') as f:
    f.write((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
handoff = {'status': 'STOPWRITE_SOURCE_REVIEW_COMPLETE_NOT_RUNTIME_ADMITTED',
           'formal_review': ref(report_path), 'Source_review_passed': True,
           'candidate_whole_manifest': report['candidate_whole_manifest'],
           'candidate_code_manifest': report['candidate_code_manifest'],
           'qualified_Source_checks': len(checks), 'Source_blocker_count': 0,
           'Source_test_method_count': len(test_methods),
           'required_history_nonlist_pair_before_actual098_acceptance': True,
           'qualification': 'Five lead repair only; deeper schemas and GUI safety not established. Actual Root lead collection not098baseline.',
           'runtime_executed': False, 'Product_PASS': None, 'completed_section_increment': 0,
           'future_guards_results': code['future_guards_results'], 'runtime_admission': False}
handoff_path = OUTPUT / 'final-handoff.json'
with handoff_path.open('xb') as f:
    f.write((json.dumps(handoff, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
for row in whole['artifacts']:
    current = ref(PACKET / row['relative_path'])
    assert current['bytes'] == row['bytes'] and current['sha256'] == row['sha256']
manifest = {'status': 'STOPWRITE_INDEPENDENT_SOURCE_REVIEW_WHOLEMF_EXCLUDES_ITSELF',
            'runtime_executed': False, 'Product_PASS': None, 'completed_section_increment': 0,
            'artifacts': [dict(relative_path=p.name, bytes=ref(p)['bytes'], sha256=ref(p)['sha256'])
                          for p in (report_path, handoff_path, Path(__file__))]}
manifest['artifact_count'] = len(manifest['artifacts'])
manifest['total_bytes'] = sum(r['bytes'] for r in manifest['artifacts'])
mf = OUTPUT / 'public-artifacts-manifest.json'
with mf.open('xb') as f:
    f.write((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
print(json.dumps({'metadata_Source_review_only': True, 'project_runtime': False,
                  'formal_review': ref(report_path), 'handoff': ref(handoff_path),
                  'manifest': ref(mf), 'qualified_Source_checks': len(checks)}, indent=2))
