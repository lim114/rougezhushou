"""Stdlib-only public Source quoting and fixture composition, no project import."""
from pathlib import Path
import ast
import copy
import hashlib
import json

P = Path(__file__).parent
REPO = Path('/workspace/rougezhushou')
ORIGINAL = Path('/workspace/.continuation/p2-scenario-state-source-v1/public-sources')


def write_json(name, value):
    path = P / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)+'\n', encoding='utf-8')


official = {'rfc8259.txt': '61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7',
            'python312-json.html': '1a5e4ba18342b32f5f174d129f9c226a21a9445a89384f13a3f33ec327c2b68f'}
sources = P / 'public-sources'; sources.mkdir(exist_ok=True)
for name, expected in official.items():
    raw = (ORIGINAL / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected
    (sources / name).write_bytes(raw)
    name += '.download.json'
    (sources / name).write_bytes((ORIGINAL / name).read_bytes())
plain = (ORIGINAL / 'python312-json-plain.txt').read_bytes()
(sources / 'python312-json-plain.txt').write_bytes(plain)
rfc = (sources / 'rfc8259.txt').read_text()
python = plain.decode()
quotes = []
for file, text, needle, size in (
        ('rfc8259.txt', rfc, 'A JSON value MUST be an object', 520),
        ('python312-json-plain.txt', python, 'Performs the following translations in decoding by default:', 360)):
    offset = text.index(needle)
    quotes.append({'source_file': file, 'character_offset': offset, 'quote': text[offset:offset+size]})
write_json('public-sources/SOURCE_QUOTES_122.json', {
    'kind': 'ACTUAL_ORIGINAL_OFFICIAL_TEXT_REUSED_SOURCE_NOT_RUNTIME',
    'reused_from': str(ORIGINAL), 'original_download_ledgers_preserved': True,
    'new_download_count': 0, 'original_bytes_hash_checked': official,
    'plain_rendering_original_120': True, 'quotes': quotes,
    'application_policy': 'Exact bool qualifies retained presence/possession; missing historical defaults stay. Other legal JSON values remain raw unknown, not invalid JSON.',
    'game_lifecycle_claims_added': False})

game_sources = []
for name, table, ids in (
        ('relic-mechanics.json', 'relics', ['rogue_6_relic_legacy_15', 'rogue_6_relic_legacy_103',
                                         'rogue_6_relic_assign_13', 'rogue_6_relic_assign_15']),
        ('recipient-lifecycle.json', 'rules', ['rogue_6_relic_assign_13', 'rogue_6_relic_assign_15'])):
    path = REPO / 'rouge/data' / name; raw = path.read_bytes(); value = json.loads(raw)
    game_sources.append({'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                         'source_url': value['source_url'], 'original_source_sha256': value['source_sha256'],
                         'records': {identity: value[table][identity] for identity in ids}})
write_json('public-sources/PINNED_EXISTING_GAME_RECORDS.json', {
    'kind': 'ACTUAL_EXISTING_PUBLIC_JSON_SOURCE_READ_NOT_NEW_DOWNLOAD_OR_RUNTIME',
    'new_game_rules_added': False,
    'scope': 'These existing attack/counter/snack/gain_random records support meaningful consumption controls; qualification does not alter their mechanics.',
    'sources': game_sources})

operator = {'id': 'mechanist', 'scope': 'run', 'present': 'false',
            'fields': {'elite': 2, 'level': 80, 'trust': 100, 'potential': 1},
            'skill_ranks': {'1': 7}, 'captured_at': 900.0,
            'recruitment_kind': 'emergency_hire', 'advanced': False,
            'char_buff_ids': ['rogue_6_from_relic_13'], 'char_buffs_complete': True,
            'char_buff_absent_ids': ['rogue_6_from_relic_9'], 'char_buff_pending_ids': [],
            'public_opaque': {'zero': -0.0, 'nullable': None}}
relic = 'rogue_6_relic_legacy_15'; tool = 'rogue_6_active_tool_5'
saved = {'id': 'public-window122', 'started_at': 0.0, 'last_read': 1000.0,
         'operators': {'mechanist': operator}, 'relics': {relic: {'held': 'false'}},
         'tactical_tools': {tool: {'held': 'false'}}, 'history': [],
         'relic_icon_memory': None, 'relic_count': 0, 'inventory_verified': True,
         'public_opaque': {'nullable': None, 'order': ['public', False], 'negative_zero': -0.0}}
for label, value in [('string_false', 'false'), ('numeric_one', 1), ('null', None),
                     ('true_control', True), ('false_control', False), ('missing_control', 'missing')]:
    case = copy.deepcopy(saved)
    for record, key in [(case['operators']['mechanist'], 'present'),
                        (case['relics'][relic], 'held'), (case['tactical_tools'][tool], 'held')]:
        if label == 'missing_control': record.pop(key)
        else: record[key] = value
    if label in ('true_control', 'missing_control'): case['relic_count'] = 2
    write_json('public-inputs/raw/'+label+'.json', case)
account = {'id': 'mechanist', 'scope': 'operator_profile', 'fields':
           {'elite': 2, 'level': 40, 'trust': 25, 'potential': 2},
           'skill_ranks': {'1': 3}, 'captured_at': 800.0}
write_json('public-inputs/account-reference.json', account)
write_json('PUBLIC_VALIDATION_PLAN.json', {
    'kind': 'UNEXECUTED_AUTHOR_ACCEPTANCE_PLAN', 'planned_section': 122,
    'runtime_result': None, 'project_imports_by_author': 0,
    'tracked_mutations_by_author': 0, 'private_reads_or_copies': 0,
    'actual_application': {
        'root_only': True, 'branch': 'codex/p2-development',
        'rebind_to': 'Actual completed section121 sources and receipts',
        'rule': 'Require every old local block exactly once, preserve line endings and all other bytes. Add helper/new test; prepend module without deleting prior selections. Do not overwrite full future app snapshot.'},
    'public_inputs': 'public-inputs/raw/*.json and public-inputs/account-reference.json; the temporary directory must never contain private state.',
    'qualified_controls': {
        'True': 'Held relic/tool active, current roster/cultivation/metadata active, original labels and alias receipt exact.',
        'False': 'Held items/current member inactive; original departure label and old lifecycle events exact.',
        'missing': 'Historical default True; do not add missing flag keys or require a migration.',
        'nonbool': 'Unknown for every JSON native kind; no automatic holdings/roster/cultivation/buffs/counters, no acquisition/departure/upgrade inference.'},
    'native_receipt': {
        'before_after': ['Entire run.state', 'caller observed graph', 'account and member', 'scenario and entire API result', 'all report formatter inputs/outputs'],
        'preserve': ['Exact builtin type', 'dict iteration order', 'list order', 'float.hex including -0.0', 'same-reference and shared-reference graph', 'unchanged disk bytes for read-only views'],
        'method': 'Root actual native-f040 or exact typed byte verifier, not JSON-only equality, loose float tolerance or sorted mapping normalization.',
        'explicit_change': 'Non-bool held/present qualification and independent history/masks intentionally change behavior; exact bool and missing controls compare prior native receipt.'},
    'actual_temporary_api_and_disk_cases': [
        'Load six raw public controls, original bytes unchanged, query every view and read disk again; no tmp, no record deletion/coercion.',
        'All fourteen non-bool values from the new test exercise exact raw retention, inventory unknown reporting and historical source labels.',
        'Unknown held attack relic is absent from actual calculate_damage input; its complete output equals plain baseline. True control changes the existing real melee attack effect.',
        'Unknown current operator helper selects the account dict rank3/E2L40 while retained rank7/E2L80 stays raw. Actual118 MainWindow preserves its default grade10 E2 preview; only explicitly enabling account-reference rank selection may use rank3, marked as account reference rather than current-run read.',
        'Stored signature without memory key cannot restore unknown held claims; stored memory with family legacy24 and grade3 is retained suspended; unqualified cards cannot erase it.',
        'Fresh held IDs/bar qualify unknown with separate event carrying native previous_record; unknown gain_random parent15 does not fabricate a grant, exactFalse reacquisition keeps original negative invalidation.',
        'Full zero inventory/crew directly closes unknown True/False state claims without pretending old loss/departure, retaining previous proof and values.',
        'Unknown presence ID-only -> True keeps cultivation and metadata masks; save/close/reload; subsequent fresh origin/elite/advanced cannot compare against masked old values as lifecycle baselines.',
        'Partial popup B qualifies B only, raw A retained but masked; repeated ID-only page preserves subset; next partial A qualifies A; full empty popup replaces recipient group under old policy.',
        'Actual skill3 cost plain35, masked oldsnack35, fresh own popup snack28 under pinned existing cost multiplier; do not infer source from held snackparent.',
        'Counter oldproof retained unknown/inactive; unknownTrue requal cutoff suppresses oldproof; unknownFalse -> True cannot revive it; fresh samepacket proof timestamp equality qualifies.',
        'Stale and wrong-run observations reject atomically, preserving full native caller/run graphs and original bytes.'
    ],
    'actual_mainwindow_matrix': [
        {'case': 'constructor_and_overview', 'checks': 'Three unknown flags controls omit mechanist from automatic current overview and holdings, show unconfirmed notice; True/missing controls include it; False preserves departure.'},
        {'case': 'manual_account_preview', 'checks': 'Select mechanist explicitly; account fields E2L40 may fill reference, default skill grade remains the118 E2 preview10. Explicit account-reference control selects rank3 with account label; neither path confirms retained current-run rank7. Manual skill/rank-source, operator/new-run reset and checkbox current-grade semantics from118 remain.'},
        {'case': 'metadata_and_raw_summary', 'checks': 'No oldemergency source/advanced/positive buff claim from unknown or retained masks; raw records remain; source/field specific rereads unmask only their own facts.'},
        {'case': 'closed_reload_sequence', 'checks': 'Observe ID-only in temporary run, close project window, reread original retained history/masks and disk, reopen; no startup repair requalifies old metadata.'},
        {'case': 'partial_and_full_popup', 'checks': 'Fresh partial B alone in actual automatic target metadata and damage scenario; A stays stored but absent; fresh full popup resolves group; manual buff test remains explicitly marked preview.'},
        {'case': 'inventory_and_counter', 'checks': 'Fresh actual held bar/zero/tool/card/status pathways update independent qualification consistently; no saved-memory replay on fresh difficulty-only page; current proof cutoff reflected in actual calculation conditions.'},
        {'case': 'reports_and_modes', 'checks': 'Continuous and frames inputs render actual three existing report formatters; unknown source never becomes actual confirmed held/recipient input. Healthy report text and native result preserve116–121 changes.'},
        {'case': 'all_consumers', 'checks': 'Direct formatting, training fallback, recruitment metadata, automatic heldIDs/toolIDs, inventory summary, originrepair and recipient lifecycle reach the same qualification, not only the new helper.'}
    ],
    'meaningful_regressions': {
        'new_module': 'tests.test_retained_presence_122 (28 methods, unexecuted)',
        'related_modules': ['tests.test_cache_consumers_101', 'tests.test_training_view_100',
                            'tests.test_run_state_reliability', 'tests.test_run_persistence_099',
                            'tests.test_inventory_confirmation_102', 'tests.test_account_cache_093',
                            'tests.test_recipient_lifecycle_063', 'tests.test_recipient_live_055',
                            'tests.test_recipient_integration_054', 'tests.test_relic_grade_sync_032',
                            'tests.test_chen_motion_reference', 'tests.test_reproducible_report_117'],
        'full_available': 'Run current actual scripts/verify_cloud.py plus existing Wine and project test-window workflow, preserve actual counts/exit codes/failure receipts.',
        'healthy_115_source_controls': 'Five saved89_states090 literals Source checked as nine bool members: six True, three False; actual Root native/window results still required.',
        'future_group': 'This is section122; do not label125 full acceptance complete until actual group completion.'},
    'limitations': ['Source review is not Runtime or native Windows acceptance.',
                    'No private state, personal screenshots, actual game actions or desktop chat sending.',
                    'No new game acquisition/loss/recipient grant/timing/reset mechanism.',
                    'Keep95/109 original three-attempt failures deferred; do not recreate their stalled tests.']})

for path in (P / 'candidate').rglob('*.py'):
    tree = ast.parse(path.read_text()); compile(tree, str(path), 'exec')
test_tree = ast.parse((P / 'candidate/tests/test_retained_presence_122.py').read_text())
assert sum(isinstance(node, ast.FunctionDef) and node.name.startswith('test_') for node in ast.walk(test_tree)) == 28
print('official_source_hash_checks', len(official), 'public_input_files', 7,
      'candidate_AST_compile_noexec', True, 'project_imports', 0, 'runtime_tests', 0)
