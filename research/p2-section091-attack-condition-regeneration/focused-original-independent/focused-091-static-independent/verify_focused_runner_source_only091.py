"""Frozen focused runner static/bytes/AST audit; never import or execute project code."""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/ui-091-focused-final')
ROOT = Path('/workspace/rougezhushou')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def literal(tree, name):
    nodes = [n.value for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    assert len(nodes) == 1, (name, len(nodes))
    return ast.literal_eval(nodes[0])


manifest_path = AUTHOR / 'public-artifacts-manifest-focused-mainwindow091.json'
manifest_raw = manifest_path.read_bytes()
assert sha(manifest_raw) == '8633d5a32689580a1977820f586432a8ecba13a67923892ce4fe898066be9dd8'
manifest = json.loads(manifest_raw)
assert manifest['format_version'] == 1 and len(manifest['files']) == 23
assert sum(r['bytes'] for r in manifest['files']) == 695823
seen = set()
for row in manifest['files']:
    p, name = Path(row['source_path']), row['archive_path']
    rel = PurePosixPath(name)
    assert p.is_absolute() and p.is_file() and not p.is_symlink()
    assert name == rel.as_posix() and not rel.is_absolute() and '\\' not in name
    assert rel.parts and not any(v in ('.', '..', '.git') for v in rel.parts)
    assert name not in seen
    seen.add(name)
    raw = p.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], name

runner_path = AUTHOR / 'wine-focused-mainwindow-091-final.py'
runner_raw = runner_path.read_bytes()
assert len(runner_raw) == 114326
assert sha(runner_raw) == '648389a4dafefc8775d39b07f79eb895689a4a417dc2155dc8118679b30552c5'
tree = ast.parse(runner_raw)
assert literal(tree, 'PENDING_PREPARATION') is False
guard = literal(tree, 'SOURCE_HASHES')
plan = literal(tree, 'PLAN')
plan_path = AUTHOR / 'focused-window-state-plan091.json'
plan_raw = plan_path.read_bytes()
assert sha(plan_raw) == '6bd3c6af6e7615b76f9fdf0f7270676cf5c56af49bf74ebed74fcf02558eb4c0'
assert json.loads(plan_raw) == plan
assert len(plan['rows']) == 24
numeric = [r for r in plan['rows'] if r.get('numerical_result_expected', True)]
early = [r for r in plan['rows'] if not r.get('numerical_result_expected', True)]
buttons = [r for r in plan['rows'] if r.get('explicit_click')]
screenshots = [r['screenshot'] for r in plan['rows'] if r.get('screenshot')]
assert len(numeric) == 21 and len(early) == 3
assert len(buttons) == 5 and all(r in numeric for r in buttons)
assert len(set(r['id'] for r in plan['rows'])) == 24
assert screenshots == ['wine-focused-continuous-091.png', 'wine-focused-deepcolor-091.png']
assert plan['planned_explicit_three_text_requests'] == 3 * len(numeric) == 63

snapshot_path = AUTHOR / 'root-source-091-exact-snapshot.json'
snapshot_raw = snapshot_path.read_bytes()
assert sha(snapshot_raw) == '1f5301f3e8ff53ee7338af3e3a8869a5b56d3422f231db52c26233e1ca747209'
snapshot = json.loads(snapshot_raw)
assert snapshot['passed'] is True and snapshot['source_sha256_after'] == guard
assert len(guard) == snapshot['current_maintained'] == 730
working = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
           for folder in ('rouge', 'tests', 'scripts') for p in sorted((ROOT / folder).rglob('*'))
           if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
assert working == guard
binding = json.loads((AUTHOR / 'actual-joined730-source-binding091.json').read_bytes())
assert binding['source_map_count'] == 730 and binding['unchanged_maintained'] == 726
assert binding['HEAD_identity'] == '2cbc45f03f99ed4f04b9c7e2612b58542f909168'
assert binding['changed_maintained'] == ['rouge/app.py', 'rouge/operator_engine.py', 'rouge/reporting.py', 'scripts/verify_damage_ui.py']
assert {r['relative_path']: r['sha256'] for r in binding['actual_files']} == guard
for row in binding['actual_files']:
    assert (ROOT / row['relative_path']).stat().st_size == row['bytes']
assert snapshot_raw == Path('/workspace/.continuation/root-source-091.json').read_bytes()

release = json.loads((AUTHOR / 'pending-to-final-release-proof091.json').read_bytes())
pending_raw = Path(release['original_pending']['source_path']).read_bytes()
assert sha(pending_raw) == release['original_pending']['sha256']
assert pending_raw.count(b'PENDING_PREPARATION = True') == 1
assert pending_raw.replace(b'PENDING_PREPARATION = True', b'PENDING_PREPARATION = False', 1) == runner_raw

# Readiness checks of frozen source structure; these do not invoke its helpers.
source = runner_raw.decode()
required = [
    "assert not RECEIPT.exists() and not CHECKPOINT.exists()",
    "previous_profile=sys.getprofile();sys.setprofile(profile)",
    "checkbox.toggled.connect(observed_toggle)",
    "assert checkbox.isChecked() is True",
    "assert id(checkbox)==checkbox_identity",
    "assert delta(before_button,entry_counts).get('calculate_damage',0)==1",
    "assert type(raw['continuous_attacks']) is bool and raw['continuous_attacks'] is row['checked']",
    "assert window.damage_result is None",
    "assert delta(before,entry_counts).get('calculate_damage',0)==0",
    "'input_native_before':native(frame.f_locals['scenario'])",
    "record['input_native_after']=native(frame.f_locals['scenario'])",
    "record['caller_native_unchanged']=record['input_native_after']==record['input_native_before']",
    "'returned_dict' if type(value) is dict else 'returned_None_or_exception_unwind'",
    "record['result_native_before']=native(result)",
    "record['scenario_native_before']=native(raw)",
    "assert native(raw)==record['scenario_native_before'] and native(result)==record['result_native_before']",
    "'estimate':format_estimate(result),'default':format_report(result)",
    "'technical':format_report(result,technical=True)",
    "assert window.damage_text.toPlainText()==reports['default'].replace(chr(160),' ')",
    "assert window.damage_text.toPlainText()==reports['technical'].replace(chr(160),' ')",
    "compressed=gzip.compress(decoded,mtime=0);CHECKPOINT.write_bytes(compressed)",
    "'decoded_sha256':hashlib.sha256(decoded).hexdigest()",
    "receipt['source_sha256_after']=after",
    "sys.setprofile(None)",
    "assert 'amiya_continuous_reference' not in result",
    "assert not raw.get('timing')",
    "record['ordinary_parameter_clock_not_native_clock']=True",
    "assert not window.auto.isChecked() and window.capture.target is None",
    "assert not window.desktop.process and not isolated.joinpath('chat').exists()",
]
assert all(v in source for v in required)
assert 'blockSignals' not in source
assert 'window.calculate=' not in source and 'module.calculate_damage=' not in source
assert 'for row in PLAN[\'rows\']' in source

receipt = {
    'format_version': 1, 'status': 'STATIC_SOURCE_HASH_GUARD_PLAN_SINK_LEDGER_PASS_PENDING_ROOT_WINDOW',
    'public_manifest': {'source_path': str(manifest_path), 'sha256': sha(manifest_raw), 'files': 23, 'bytes': 695823},
    'runner': {'source_path': str(runner_path), 'sha256': sha(runner_raw), 'bytes': len(runner_raw)},
    'all23_bytes_sha_safe_archive_paths_pass': True,
    'current_joined_source_guard': {'files': 730, '726_unchanged_4_joined_product_changes': True,
        'exact_current_inventory_equal_guard_and_root_snapshot': True, 'source_is_working_files_not_old_HEAD_blobs': True,
        'runtime_after_scope': 'every original730 guard key byte hash; root may independently enumerate inventory after execution'},
    'pending_release': 'only first True→False literal, original body/plan/source guard identical',
    'state_plan': {'states': 24, 'numeric_result_states': 21, 'actual_existing_early_states': 3,
        'explicit_buttons': 5, 'explicit_three_text_requests': 63, 'two_screenshot_sinks': screenshots,
        'full90_or4217_rerun': False},
    'counter_scope': 'Python function entries only, current main thread after sys.setprofile hook; startup and common setup measured separately. Not all-thread or all-import totals.',
    'automatic_counter_label_boundary': 'actual_automatic_numerical_entries is actual calculate_damage function entries minus five runtime-asserted explicit-button entries; not successful numerical calculation count. API_events outcomes returned_dict/None-or-unwind must be inspected after execution.',
    'capture_scope': 'All instrumented API caller native before/after and outcome; full native result/JSON/scenario and own three report texts for21 final state results only. Per-state raw scenario capture is after API and before formatter checks; API input before-call is separately captured by profile.',
    'talent_trace_scope': 'Existing talent return observations are actual frame/step/operator/elite/potential grouped per action, not exclusive final-result enclosing API sequence. Native SP clock not certified.',
    'lossless_design': 'Checkpoint saves full tagged native tree plus JSON and texts, SHA/bytes for raw and gzip; root must actually decompress/verify those proofs after its sole execution.',
    'isolation': 'run/account/settings/chat paths replaced before actual window construction; no auto sampling target/game/chat process and no backend calculator/signal suppression in runner',
    'actual_GUI_or_trace_or_screenshot_pass_claimed': False,
    'project_calls': {'API': 0, 'helper': 0, 'formatter': 0, 'constructor': 0, 'tests': 0, 'Qt': 0, 'Wine': 0},
    'source_preparation_failures': 0,
}
(HERE / 'source-guard-ledger-formal-receipt091.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'files': 23, 'bytes': 695823, 'source_guard': 730,
                  'states': 24, 'numeric': 21, 'early': 3, 'project_calls': receipt['project_calls']}))
