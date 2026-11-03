"""Standard-library source reading only. Never imports or executes project code."""
from pathlib import Path
import ast
import difflib
import hashlib
import json

ROOT = Path('/workspace/rougezhushou')
OUT = Path('/workspace/.continuation/p2-after097-remaining-source-audit-v1')
SURVEY = Path('/workspace/.continuation/p2-after096-account-metadata-source-survey-v1')


def digest(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


relative_sources = [
    'AGENTS.md', 'CLOUD_HANDOFF.md', 'PROJECT_PROGRESS.md', 'PROJECT_COMPLETED.md', 'WORK_IN_PROGRESS.md',
    'rouge/run_state.py', 'rouge/run_recognition.py', 'rouge/app.py', 'rouge/account_cache.py',
    'rouge/relic_counter_semantics.py', 'rouge/run_modifiers.py', 'rouge/summons.py',
    'rouge/operator_engine.py', 'rouge/estimate.py',
    'tests/test_inventory_snapshot_051.py', 'tests/test_empty_inventory.py',
    'tests/test_run_crew_count_boolean_input.py', 'tests/test_run_reuse_guards_032.py',
    'tests/test_run_config.py', 'tests/test_recipient_lifecycle_063.py',
    'research/p2-crew-count-boolean-input/author-packet/static-lead089/source-lead-receipt089.json',
    'research/p2-crew-count-boolean-input/author-packet/source089/frozen/rouge/run_state.py',
    'research/p2-crew-count-boolean-input/author-packet/author089/draft/rouge/run_state.py',
    'research/p2-section093-account-cache-safety/independent-v2/REVIEW.md',
    'research/p2-wang-token-module-reference/NOTE.md',
    'research/p2-wang-token-module-reference/source-receipt.json',
    'research/p2-token-manual-attributes/NOTE.md',
    'research/p2-technology/NOTE.md', 'research/p2-technology/source-receipt.json',
    'research/p2-squad-unlock-reference/NOTE071.md',
    'research/p2-squad-unlock-reference/source-receipt071.json',
    'research/p2-squad-unlock-reference/root-compression-receipt.json',
    'research/p2-environment-and-lifecycle/RESEARCH.md',
]
external_sources = [
    SURVEY / 'official-documents-retrieval.json',
    SURVEY / 'public-documents/python-json-3.12.html',
    Path('/workspace/.continuation/p2-condition096-candidate-v1/IMPLEMENTATION_CONTRACT096.md'),
    Path('/workspace/.continuation/p2-account-persistence-candidate-next-v1/IMPLEMENTATION_CONTRACT.md'),
]
sources = {relative: digest(ROOT / relative) for relative in relative_sources}
sources.update({str(path): digest(path) for path in external_sources})

# Copies are publicly readable source bytes, never fixtures from actual runtime state.
for relative in relative_sources:
    if relative.startswith(('rouge/', 'tests/')):
        destination = OUT / 'source-snapshots' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())

run_raw = (ROOT / 'rouge/run_state.py').read_bytes()
old_raw = (ROOT / 'research/p2-crew-count-boolean-input/author-packet/source089/frozen/rouge/run_state.py').read_bytes()
author089_raw = (ROOT / 'research/p2-crew-count-boolean-input/author-packet/author089/draft/rouge/run_state.py').read_bytes()
assert hashlib.sha256(run_raw).hexdigest() == '20c6a00a72744017ebbc0fcb3b1009dddf8a6702aa01bf273b4b51c344692fd9'
assert hashlib.sha256(old_raw).hexdigest() == '6d36bc955af40aff99ac9079706342b67e6df0bc8d1f93e55e2cc580cabcbdac'
assert run_raw == author089_raw
old_lines = old_raw.decode().splitlines(keepends=True)
current_lines = run_raw.decode().splitlines(keepends=True)
delta = ''.join(difflib.unified_diff(old_lines, current_lines, fromfile='pre089-frozen', tofile='current-maintenance095', n=3))
(OUT / 'pre089-current-maintenance-source-delta.txt').write_text(delta, encoding='utf-8')
without_crew_guard = run_raw.replace(b'        if isinstance(crew,bool):crew=None\r\n', b'', 1)
assert without_crew_guard == old_raw

tree = ast.parse(run_raw.decode())
functions = {}
for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == 'RunState':
        for method in node.body:
            if isinstance(method, ast.FunctionDef):
                functions[method.name] = {'start_line': method.lineno, 'end_line': method.end_lineno}

def excerpt(relative, ranges):
    lines = (ROOT / relative).read_text().splitlines()
    pieces = []
    for first, last in ranges:
        pieces.extend(f'{i}: {lines[i-1]}' for i in range(first, last + 1))
    return '\n'.join(pieces) + '\n'

excerpts = {
    'run-state-startup-and-consumers.txt': ('rouge/run_state.py', [(13,48),(50,66),(76,96),(159,181),(520,537),(564,596)]),
    'run-state-inventory-count.txt': ('rouge/run_state.py', [(183,207),(244,265),(322,374)]),
    'actual-count-producer.txt': ('rouge/run_recognition.py', [(68,97),(121,142),(183,191)]),
    'actual-ui-consumers.txt': ('rouge/app.py', [(100,107),(195,201),(901,912)]),
    'existing-crew-legacy-counterevidence.txt': ('tests/test_run_crew_count_boolean_input.py', [(103,111)]),
}
for name, (relative, ranges) in excerpts.items():
    (OUT / name).write_text(excerpt(relative, ranges), encoding='utf-8')

retrieval = json.loads((SURVEY / 'official-documents-retrieval.json').read_text())
official = retrieval['retrievals'][0]
assert sources[str(SURVEY / 'public-documents/python-json-3.12.html')]['sha256'] == official['response']['sha256']

groups = [
    {
        'id': 'A_offline_run_snapshot_startup_safety',
        'status': 'STATIC_SOURCE_LEAD_PENDING_PUBLIC_TEMPORARY_REPRODUCTION',
        'development_phase': 'future P2; priority-1 todo table relevance does not resume paused P1',
        'functional_boundary': 'Read persisted public RunState snapshot, screen only fields actually consumed at restart/display, preserve original on unusable structure, start usable offline window without changing valid current-run facts.',
        'source_refs': ['rouge/run_state.py','rouge/app.py','rouge/relic_counter_semantics.py',str(SURVEY/'public-documents/python-json-3.12.html')],
        'source_facts': [
            'RunState.__init__13-29 only requires top-level dict plus operators/relics dict, then shallow state.update(saved). It calls restore_relic_icon_memory, restore_passed_node_types and restore_origin_discovery_buffs under an except(OSError,ValueError) boundary.',
            'restore_passed_node_types33 requires state.maps.items(), graph.get and node.get. No preceding maps/graph/node shape screening occurs in current constructor.',
            'restore_origin_discovery_buffs86 correctly rejects non-list history, but91 unconditionally calls member.get for each operators value. This local history guard does not screen other loaded fields.',
            'summary564-596 consumes profile/catalog identities, relic/tool values, config mapping and resource record fields; app199 calls this at window construction, before new observations.',
            'Official pinned Python3.12-family JSONDecoder table528-550 maps JSON object to dict, array to list, true/false to bool and null to None; syntax-valid JSON does not validate an application snapshot schema.',
            'Existing malformed/read-error catch already sets preserve_unreadable and a clear notice; save61 exits before filesystem IO when that flag is set. This existing protection is retained, not reimplemented as a new97 save repair.',
        ],
        'unexecuted_public_cases_to_confirm': [
            {'json_text': '{"operators":{},"relics":{},"maps":[]}', 'source_only_branch': 'Passes the initial three predicates; maps.items is demanded by restore_passed_node_types. Expected actual outcome must be recorded by fresh RunState constructor, not inferred as a measured failure.'},
            {'json_text': '{"operators":{"mechanist":null},"relics":{}}', 'source_only_branch': 'Passes initial operators dict gate; member.get is demanded by origin-discovery restore after default maps/history paths. No project call performed.'},
            {'json_text': '{"operators":{},"relics":{"rogue_6_relic_cargo_1":null}}', 'source_only_branch': 'Constructor may finish with absent signature; held_relic_ids and app startup summary later demand record.get. Exact entry/outcome remains unmeasured.'},
        ],
        'counterevidence_already_checked': [
            'Current42446-byte RunState exactly equals archived author089 draft; sole delta against pinned pre089 source is crew bool→None. No later startup shape repair found in these current source bodies.',
            'Section093 account safety explicitly states it neither validates nor modifies RunState. AccountCache screening cannot protect app RunState constructor or run-summary consumers.',
            'Existing targeted same-run clearing/origin repairs are evidence-limited migrations, not a generic schema validator. They must remain intact for valid history.',
            'Current temporary regression source covers valid restart/config and recipient/inventory retention. Search of selected production/tests/research found no RunState malformed-maps/member fixture check; search absence is bounded, not exhaustive project proof.',
        ],
        'candidate_after_repro_only': [
            'Select exact reproduced consumed-shape failures only. Stage/screen decoded snapshot before installing unsafe consumed fields; define clear unavailable-memory notice and preserve_original behavior.',
            'Keep valid persisted state exact, including current id, started_at, last_read, members, recruitment/recipient evidence, history order, partial inventory and source timestamps. Retain omitted-field defaults and valid old-history migrations.',
            'Do not introduce a broad deep-copy/schema rewrite, auto reset/save, reconstitute old runs, sanitize numerical leaves without source, or infer any missing recruitment/acquisition event.',
        ],
        'validation_plan_not_executed': [
            'Fresh exact-source public fixtures: malformed JSON/top-level control versus syntax-valid maps/list/graph/node/member/relic/tool/resource/config structures actually consumed. Record constructor and summary errors, args, state graph, original bytes, temporary sibling absence and all file IO entries.',
            'Valid producer-generated temporary snapshot paired against unchanged baseline: complete native graph/type/alias, id/time, caller, original disk and outputs exact. Include default omitted keys and authorized old clearing/origin migration fixtures rather than disabling repairs.',
            'New public positive observations on a protected unusable-original session: usable facts can be shown according to selected confirmed contract, while no original/tmp overwrite occurs. Manual reset contract is verified explicitly; no automated clear/reset.',
            'Related current restart/config, reuse, inventory snapshot, crew89 and recipient lifecycle regressions, then relevant selected Linux checks and actual temporary-state MainWindow startup/browse/summary/calculation. All current numeric API/native/caller/three texts remain identical for valid inputs.',
        ],
        'unknowns_and_restart': [
            'No actual RunState constructor/summary/public-window reproduction in this audit. No actual user snapshot failure, corruption frequency, historical migration scope or native game behavior established.',
            'Root must bind real completed95/96/97 prerequisites and current source, perform bounded fresh public temporary reproduction, and only then decide the coherent implementation scope.',
            'Native Windows startup/path behavior remains separately unverified; public offline malformed-state reproduction does not require game/private captures.',
        ],
        'actual_guard': None, 'actual_reproduction': None, 'actual_validation': None,
    },
    {
        'id': 'B_inventory_boolean_count_qualification',
        'status': 'STATIC_SOURCE_LEAD_PENDING_PUBLIC_TEMPORARY_REPRODUCTION',
        'development_phase': 'future P2 offline inventory-state qualification; not recognition optimization or paused P1 sampling/event work',
        'functional_boundary': 'Make inventory snapshot count qualification consistent across retained icon memory, relic/tool possession, completeness and restart, while preserving every nonboolean legacy count behavior and positive page evidence.',
        'source_refs': ['rouge/run_state.py','rouge/run_recognition.py','tests/test_inventory_snapshot_051.py','tests/test_run_crew_count_boolean_input.py','research/p2-crew-count-boolean-input/author-packet/static-lead089/source-lead-receipt089.json'],
        'source_facts': [
            'near_number68-97 returns values from int-converted sets, literal int0 for verified zero, or None; read_run122 passes this result as inventory count. No current source emits bool inventory count.',
            'RunState.apply265 stores local count from relics.get(count) without excluding bool; reconcile_relic_icons188 uses count==0/count!=prior to clear memory; apply360 uses count==0 as the explicit-empty removal authority.',
            'apply333 compares signature length to any non-None expected count;343 stores any non-None count; inventory_status523 compares known+tools against that stored count. Current code uses exact-int checks in selected neighboring memory paths, but not these paths.',
            'Current crew handling373 already changes bool to None. Prior089 raw source receipt separately documents numeric bool equality as a static fact; its actual crew reproductions do not reproduce inventory behavior.',
            'Inventory051 tests distinguish empty/unread/full/partial/duplicate slots, tactical tools, grade corrections and positive owned cards, but the inspected tests do not cover bool count input. Genuine recognized bool counts are not established.',
        ],
        'unexecuted_public_cases_to_confirm': [
            'Seed a public temporary complete relic+tool inventory, then apply empty-page countFalse versus countNone and int0 from the same original bytes. Record actual memory/relic/tool/history/status/disk outcome; expected static branch condition is not a runtime failure receipt.',
            'Seed two held items, then apply one confirmed public icon with countTrue versus countNone and int1; inspect count storage, complete-bar authority, removal events and positive field retention.',
            'Exercise bool count with current difficulty, grade correction and positive exact tool/card evidence to ensure a future guard does not lose unrelated positive evidence or resurrect contradicted inventory.',
        ],
        'counterevidence_already_checked': [
            'Current RunState exactly equals author089 draft; its only new type guard is local crew bool handling. No inventory bool guard added by subsequent93-95 sources.',
            'Recognition read_run142 already demotes real int0 when icons are visibly nonempty. It guards its producer path; it does not screen direct RunState observed input.',
            'tests/test_run_crew_count_boolean_input103-111 explicitly preserves nonboolean legacy0.0 and string0 behavior; this excludes any general strict-int crew rewrite and argues against unrequested inventory float/string policy expansion.',
            'There is no Source evidence that game/OCR emits these invalid bool inputs. This is a defensive observed-input contract lead analogous in type only to89, not a measured OCR bug.',
        ],
        'candidate_after_repro_only': [
            'If fresh public reproduction confirms the undesirable countFalse/countTrue authorization, normalize only bool inventory count to unread locally before all retained-memory/count/completeness consumers; do not mutate caller observation.',
            'Preserve valid integer0 removal, matching positive full counts, unread prior-count reuse, partial positive evidence, duplicate-slot semantics, stale/cross-run early returns, existing error order and all nonboolean legacy behavior.',
            'Keep relic/game re-acquisition stacking, true snapshot-page union, recruitment changes and counters unknown; no new mechanism or count cap.',
        ],
        'validation_plan_not_executed': [
            'Paired public exact starting disk with False/True/None/int0/int1 controls; compare complete native state/aliases/caller/disk/history and preserve natural id/time per pair. No UUID/time normalization across independent cases.',
            'Inventory complete/partial/duplicate multiplicity, inherited remembered bar, exact new relic and tool cards, grade correction, manual-run reset boundary and stale/cross-run gates. Invalid bool count alone must not supply removal authority; unrelated normal positive updates remain.',
            'Selected nonbool legacy count controls remain exact baseline; malformed member-buff earlier ValueError and caller/disk atomicity remain exact. Existing crew89 new7 are run unmodified.',
            'Related inventory/tools/config/recipient/crew regression and temporary-state actual MainWindow inventory summary/relic selection/calculation; valid numerical/native/caller/three-text outputs remain unchanged. No native capture or game automation.',
        ],
        'unknowns_and_restart': [
            'No RunState.apply call or new inventory reproduction performed here; no confirmed user-facing bug, positive trigger frequency or natural bool producer path.',
            'Root must confirm current maintenance/source plus actual95-97 prerequisites and public temp counterexamples before choosing implementation. If prior validation or semantics already differ at that point, rebind a new sidecar rather than alter this audit.',
        ],
        'actual_guard': None, 'actual_reproduction': None, 'actual_validation': None,
    },
]

excluded = [
    {'scope': '96 condition qualification presentation and97 AccountCache save/Unicode/IO', 'reason': 'Already planned external source candidates; no duplicate group, no application/completion assumption.'},
    {'scope': 'Additional source-supported numerical mechanic', 'reason': 'None selected. Reviewed existing token/module/technology/SP/mechanic receipts do not provide a new evidence-closed numerical change beyond completed scopes.'},
    {'scope': 'Wang max_deploy_count and other summons', 'source': 'research/p2-wang-token-module-reference/NOTE.md32-36', 'known': 'Pinned battle_equip token cost-1 and max_deploy_count+1, base4/5/6, hidden potential token talent+1.', 'blocked': 'Cost reference already completed42; actual max-count mapping needs exact token prefab/hidden attachment/dontOccupyMaxDeployCnt/S3 lifecycle binding. Cannot add parameters as real in-field limit.'},
    {'scope': 'Long-term technology and strengthened-squad activation', 'source': 'research/p2-technology/NOTE.md19-27;research/p2-squad-unlock-reference/NOTE071.md15', 'known': 'Pinned57 display nodes/9tokens/6textgroups/3difficulty gates; source display edges and gate3/6/9 are known.', 'blocked': 'Catalogue/qualification reference completed; current account unlock, actual rogue6_outbuff mapping/layer/target/mode/persistence still unknown. Display numbers do not close numeric model.'},
    {'scope': 'Hydra growth, relic ability events, SP multiplier/negative mechanics, attack/periodic/secondary clocks', 'blocked': 'Remaining todo requires exact native mechanism and/or current-game paired observation. Existing source parameters/archived CFG receipts do not supply missing activation, stacking, tick phase or current heat-update equality. No invented negative-SP repair.'},
    {'scope': 'Manual all_units token panel source', 'reason': 'Prior42 follow-on is completed44; do not repeat old bug as current gap.'},
    {'scope': 'Crew float/string count policy', 'reason': 'Current explicit test protects legacy behavior;89 bool fix is already complete. No new evidence authorizes broad type rewrite.'},
    {'scope': 'P3, paused P1, recognition optimization, cosmetics, source-collection/report-only milestone', 'reason': 'Outside future coherent P2 implementation scope; no progress increment.'},
]

audit = {
    'format_version': 1,
    'status': 'READ_ONLY_SOURCE_AUDIT_TWO_BOUNDED_UNREPRODUCED_FUNCTIONAL_LEADS',
    'runtime_executed': False,
    'completed_section_increment': 0,
    'actualguardsandresults': None,
    'branch': {'task_stated': 'codex/p2-development', 'read_with_Git': False, 'actual_branch_guard': None},
    'prerequisites': {'full095_completed': None, 'batch95_commit_push': None, 'section096_completed': None, 'section097_completed': None, 'current_runtime_source_guard': None},
    'source_only_selection': {'groups': 2, 'new_numerical_mechanic_groups': 0, 'implementation_ready_groups': 0, 'public_temp_reproduction_needed_before_selection': True, 'grouping_recommendation': 'If both leads reproduce and remain compatible, combine their complete validation into one coherent RunState offline reliability implementation section; do not automatically turn these two source leads into two numbered milestones.'},
    'source_index': sources,
    'source_ast_metadata': {'RunState_method_lines': functions, 'project_body_executed': False},
    'counterevidence': {'current_RunState_equals_author089_draft': True, 'current_minus_crew_bool_guard_equals_pre089': True, 'current_vs_pre089_delta_path': str(OUT/'pre089-current-maintenance-source-delta.txt')},
    'official_document': {'url': official['requested_url'], 'version': official['document_version'], 'local_path': official['response']['path'], 'sha256': official['response']['sha256'], 'reused_exact_existing_public_response': True, 'new_downloads': 0},
    'groups': groups,
    'excluded_or_deferred': excluded,
    'executions': {'project_imports': 0, 'project_calls': 0, 'project_tests': 0, 'fixture_codec_or_helper_calls': 0, 'Wine': 0, 'Qt': 0, 'Git': 0, 'native_game': 0, 'chat': 0, 'private_state_reads': 0, 'repo_writes': 0, 'process_manipulation': 0, 'scheduled_automation': 0, 'network_source_downloads': 0},
    'actual_attempts_and_results': None,
    'no_readiness_or_P2_completion_claim': True,
}
write_json('remaining-source-audit.json', audit)

write_json('preparation-diagnostics.json', {
    'runtime_executed': False,
    'project_failures': None,
    'read_only_lookup_diagnostics': [
        {'tool_chunk': 'a130fa', 'exit_code': 2, 'requested_path': 'rouge/data/relic-rules.json', 'diagnostic': 'Path does not exist; corrected file inventory found rouge/data/relic-mechanics.json. No module/data executed.'},
        {'tool_chunk': '27641b', 'exit_code': 2, 'requested_path': 'research/p2-crew-count-boolean-input/source-receipt.json', 'diagnostic': 'Receipt located under author-packet/static-lead089/source-lead-receipt089.json and was read later.'},
        {'tool_chunk': 'b1183d', 'exit_code': 2, 'requested_path': 'rouge/run_observation.py', 'diagnostic': 'Path does not exist; actual producer is rouge/run_recognition.py and actual UI forwarder is MainWindow.apply_run_observation.'},
        {'requested_path': 'tests/test_run_state.py', 'diagnostic': 'Path absent; rg identified current run/inventory/recipient test modules and their source was inspected. No test executed.'},
    ],
    'delegation': 'Independent child source review could not start because all team thread slots were occupied; no child execution or writes resulted.',
    'source_sealing_only': 'seal_source_audit.py runs pathlib/hashlib/json/ast/difflib source metadata and dedicated-output writes; primary0 does not establish any project runtime result.',
})

note = '''This is a bounded Source audit after planned96-97, not a numbered section. Two P2 offline-state leads need fresh isolated public reproduction before implementation selection. Zero new numerical mechanics have evidence-closed implementation scope. Runtime executed=false; completed section increment=0; actual guards, prerequisites and results=NULL.

Current rouge/run_state.py is42446B, SHA25620c6a00a72744017ebbc0fcb3b1009dddf8a6702aa01bf273b4b51c344692fd9. It exactly matches archived author089 draft. Its sole difference from pinned pre089 source is local crew bool→None. This provides direct counterevidence that a later existing RunState load or inventory type repair has not already been applied. Current tests deliberately preserve crew0.0/string0 legacy behavior, excluded from proposals.

A. Offline run-snapshot startup safety. Constructor only screens top/operators/relics container shapes, shallow-installs data, then maps/member restoration and actual MainWindow summary consume deeper shapes. Syntax-valid public maps=[] or operators={mechanist:null} is a concrete static entry lead. It has not been run here. Scope after confirmation: consumed-shape qualification and original-file protection at restart/use; preserve valid state, current-run precedence and old evidence-limited migrations. No save-IO/Unicode repair repeated from97, auto reset, old-run restore, new event rules or number sanitization.

B. Inventory boolean count qualification. Current int/None producer is unchanged. Direct RunState input countFalse can reach count==0 removal authority; countTrue can compare equal to full length1. These are source branch facts, not measured inventory failures. Scope after confirmation: only bool→unread before retained memory/count/completeness consumers, preserving real int0, all nonbool legacy behavior, positive cards/tools, partial/duplicate bars, stale/cross-run and caller immutability. Do not broaden this into recognition optimization, snapshot-union guessing or event reset mechanics.

Fresh reproduction must bind actual completed95/96/97 prerequisites, use exact paired public temporary disk snapshots, preserve native types/alias/id/time without cross-case normalization, record all actual constructor/apply/summary/errors/IO, and confirm old valid outputs. Then relevant regressions and actual temporary-state MainWindow are required. Native Windows/game/private screenshots remain unverified. Existing unknown technology/outbuff layers, Wang count/lifecycle mapping, Hydra and all missing native clocks stay deferred. Current top WIP was read; full095 active window and96/97 source candidates are not treated as completed.

Detailed source paths/hashes, counterevidence, exact source facts, unknowns and validation boundary plans are in remaining-source-audit.json. If both leads reproduce, prefer one coherent RunState reliability implementation with complete shared validation; these are not automatically two numbered sections. No new Source collection milestone is proposed.
'''
(OUT/'AUDIT_HANDOFF.md').write_text(note, encoding='utf-8')

# Rehash every source after reading/snapshotting; changes during the read are not hidden.
drift = []
for key, item in sources.items():
    actual = digest(Path(item['path']))
    if actual != item:
        drift.append({'key': key, 'before': item, 'after': actual})
write_json('source-reread-metadata.json', {'runtime_executed': False, 'source_drift': drift, 'note': 'Documentation may be concurrently updated by root. A changed source is recorded, never relabeled unchanged.'})
assert not any(x['key'].startswith(('rouge/','tests/')) for x in drift)

artifacts = []
for path in sorted(OUT.rglob('*')):
    if path.is_file() and path.name not in {'public-artifacts-manifest.json','final-handoff.json'}:
        artifacts.append({'relative_path': str(path.relative_to(OUT)), **digest(path)})
manifest = {'format_version': 1, 'runtime_executed': False, 'completed_section_increment': 0, 'actualguardsandresults': None, 'artifacts': artifacts}
write_json('public-artifacts-manifest.json', manifest)
handoff = {
    'status': audit['status'], 'runtime_executed': False, 'completed_section_increment': 0, 'actualguardsandresults': None,
    'actual_prerequisites': audit['prerequisites'],
    'groups': [group['id'] for group in groups], 'groups_ready_for_implementation': 0,
    'new_numerical_mechanic_groups': 0,
    'next_action': 'Root may select a bounded fresh public temporary reproduction only after actual full095/batch persistence and96/97 prerequisites. No implementation selected or authorized by this source artifact alone.',
    'audit': digest(OUT/'remaining-source-audit.json'),
    'note': digest(OUT/'AUDIT_HANDOFF.md'),
    'manifest': digest(OUT/'public-artifacts-manifest.json'),
    'executions': audit['executions'],
}
write_json('final-handoff.json', handoff)
print(json.dumps({'status': audit['status'], 'group_count': 2, 'implementation_ready': 0, 'artifact_count': len(artifacts), 'source_drift_count': len(drift), 'runtime_executed': False, 'completed_section_increment': 0, 'actualguardsandresults': None, 'directory': str(OUT)}, ensure_ascii=False))
