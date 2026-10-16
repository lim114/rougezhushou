"""Generate publication producers only; never execute Git/document actions."""
import ast
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / '.cache/p3-298-publication-prep'
PARENT = 'b56cbf352cf5d171f52ba05839312950df462e8c'
OLD_PARENT = 'bb4927a2a2760d48882f3945b750053d7a5617fc'
PROD = ['rouge/battle_event_references.py', 'rouge/battle_view.py']
DOCS = ['AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json', 'PROJECT_COMPLETED.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md']
baseline = {}

def read(name):
    raw = (OLD / name).read_bytes()
    baseline[name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    return raw.decode('utf8').replace('298', '299').replace(OLD_PARENT, PARENT)

def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)

def block(text, start, end, replacement):
    a = text.index(start); b = text.index(end, a)
    return text[:a] + replacement + text[b:]

def save(name, text):
    compile(ast.parse(text, filename=name), name, 'exec')
    assert OLD_PARENT not in text
    assert 'maintenance_path' not in text and 'historical_test_maintenance' not in text and 'tests/test_node_catalog.py' not in text
    with (HERE / name).open('xb') as stream: stream.write(text.encode('utf8'))

promotion_name = 'verification/sections/299-preparation/final-promotion-repair.json'
promotion_raw = (ROOT / promotion_name).read_bytes()
promotion_sha = sha256(promotion_raw).hexdigest(); promotion = json.loads(promotion_raw)
assert len(promotion['promoted']) == 53 and set(promotion['existing_production_changes']) == set(PROD)
repair_name = 'verification/sections/299-preparation/entry-binding-repair.json'
repair_raw = (ROOT / repair_name).read_bytes(); repair_sha = sha256(repair_raw).hexdigest()
repair = json.loads(repair_raw)
assert repair['all_existing_tests_preserved'] is True
assert repair['only_controller_MANIFEST_and_MANIFEST_SHA_assignments_changed'] is True
assert repair['data_or_game_mechanics_changed'] is False
archive_name = 'verification/sections/299-preparation/preparation-archive-manifest.json'
archive_raw = (ROOT / archive_name).read_bytes(); archive = json.loads(archive_raw)
assert archive['section'] == 299 and archive['private_files_copied'] is False
assert archive['kind'] == 'immutable_public_preparation_and_actual_author_evidence_archive'
raw_relative = (
    'author-backend/backend-after-import-correction/process.exit',
    'author-backend/backend-first/process.exit',
    'author-backend/revision2/new-guard-first/process.exit',
    'author-backend/revision2/original-counterexample/process.exit',
    'future-event-effects-research/prts-database-434599-HTTP-error-body.bin',
)
raw_logs = {'verification/sections/299-preparation/' + name: archive['files'][name] for name in raw_relative}
assert len(raw_logs) == 5
for name, pin in raw_logs.items():
    path = ROOT / name
    assert name.startswith('verification/sections/299') and not path.is_symlink()
    assert sha256(path.read_bytes()).hexdigest() == pin['sha256'] and path.stat().st_size == pin['bytes']

text = read('stage_section_298.py')
text = block(text, 'tracked=[', "assert set(git(['diff','--name-only'])", 'tracked=' + repr(DOCS + PROD) + '\n')
text = block(text, 'promotion_raw=(ROOT/', "for entry in (ROOT/'verification/sections').iterdir():",
    f"promotion_raw=(ROOT/{promotion_name!r}).read_bytes()\n"
    f"assert sha256(promotion_raw).hexdigest()=={promotion_sha!r}\n"
    "promotion=json.loads(promotion_raw)\n"
    f"assert len(promotion['promoted'])==53 and set(promotion['existing_production_changes'])==set({PROD!r})\n"
    f"repair_raw=(ROOT/{repair_name!r}).read_bytes()\n"
    f"assert sha256(repair_raw).hexdigest()=={repair_sha!r}\n"
    "repair=json.loads(repair_raw)\n"
    "assert repair['all_existing_tests_preserved'] is True and repair['data_or_game_mechanics_changed'] is False\n"
    "assert repair['only_controller_MANIFEST_and_MANIFEST_SHA_assignments_changed'] is True\n"
    f"raw_archived_logs={dict((name, pin['sha256']) for name, pin in raw_logs.items())!r}\n"
    "new=[name for name in {*promotion['promoted'],*promotion['existing_production_changes']} if name not in tracked]\n")
text = block(text, "assert section['only_existing_production_sources_changed']", 'progress=(ROOT/',
    f"assert section['only_existing_production_sources_changed']=={PROD!r}\n"
    f"assert section['existing_source_changes_including_test_maintenance']=={PROD!r}\n"
    "assert section['old_tracked_test_maintenance'] is False\n"
    "assert set(section['source_sha256'])==set(promotion['promoted'])|set(promotion['existing_production_changes'])\n"
    "assert len(section['source_sha256'])==55\n"
    "compat=section['compatibility_maintenance']\n"
    "assert compat['all_old_tests_preserved'] is True and compat['controller_only_constant_AST_change_verified'] is True\n"
    "assert compat['data_or_game_mechanics_changed'] is False and compat['source_failure_still_unknown'] is True\n"
    "assert compat['first_actual_methods']==135 and compat['first_actual_failures']==1 and compat['first_actual_errors']==5\n"
    "assert compat['first_methods_not_added_to_final_pass_count'] is True\n"
    "assert compat['changed_source_bindings']==['rouge/event_planning.py','rouge/node_catalog.py']\n"
    "assert compat['current_manifest_sha256']==repair['new_manifest_sha256']\n"
    "assert section['source_promotion']['receipt']=='verification/sections/299-preparation/final-promotion-repair.json'\n"
    "assert section['source_promotion']['sha256']==sha256(promotion_raw).hexdigest()\n"
    "assert section['source_reference']['fixed_source_inventory']=={'stages':69,'original_levels':38,'groups':285,'packages':215}\n"
    "assert section['source_reference']['inventory_is_actual_enemy_or_selection_count'] is False\n"
    "assert section['remaining_global_stage_floor_gaps_unchanged']==15 and section['unparsed_notes_unchanged']==10\n"
    "assert section['actual_server_generation_or_inventory_verified'] is False\n"
    "assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]\n")
for prefix in ("section['next_section']", "cp['next_section']", "index['next_section']"):
    text = once(text, prefix + '==299', prefix + '==300')
save('stage_section_299.py', text)
save('push_section_299.py', read('push_section_298.py'))

text = read('verify_publication_298.py')
for old, new in (("section['next_section']==299", "section['next_section']==300"),
                 ("cp['next_section']==299", "cp['next_section']==300"),
                 ("'next_section':299", "'next_section':300"),
                 ("idx=text.index('## 功能第297节')", "idx=text.index('## 功能第298节')")):
    text = once(text, old, new)
text = block(text, "assert section['unparsed_notes_unchanged']", "assert section['remaining_global_stage_floor_gaps_unchanged']",
    "assert section['unparsed_notes_unchanged']==10 and section['old_tracked_test_maintenance'] is False\n"
    "assert len(section['source_sha256'])==55\n"
    "compat=section['compatibility_maintenance']\n"
    "assert compat['all_old_tests_preserved'] is True and compat['controller_only_constant_AST_change_verified'] is True\n"
    "assert compat['data_or_game_mechanics_changed'] is False and compat['source_failure_still_unknown'] is True\n"
    "assert compat['first_actual_methods']==135 and compat['first_actual_failures']==1 and compat['first_actual_errors']==5\n"
    "assert compat['first_methods_not_added_to_final_pass_count'] is True\n"
    "assert 'tests.test_spawn_candidates_integration_299' in necessary['modules']\n"
    "assert 'tests.test_battle_entry_compatibility_299' in necessary['modules']\n"
    "assert len(necessary['modules'])==11\n")
text = block(text, " 'scope':(", " 'necessary_methods_actual':",
    " 'scope':('Functional299 adds manual Chinese reading of exact main-queue candidate groups and package '+\n"
    " 'members from the current spawn entry or all fixed stage relations, with a fresh source-bound unique-SPAWN '+\n"
    " 'independent fixed-map/enemy preview. Parent state is preserved. EMPTY/empty-key activation, queue, ordinary/emergency '+\n"
    " 'and same-name actions remain distinct; memberships do not establish actual choice, count, exclusivity, cooccurrence, '+\n"
    " 'probability or global clock. Source loss disables prior links. A new source-only authority rebinds the unchanged296 '+\n"
    " '14/11/3 entry graph to two current parser-source bytes; only two controller constants change and all old tests remain. '+\n"
    " 'Actual '+str(section['necessary_validation']['methods_run'])+' necessary methods and '+str(window['unique_checks'])+\n"
    " ' unique native checks with '+str(window['screenshot_count'])+' representative PNGs are read from final receipts. '+\n"
    " 'Original first135/1F5E and backend counterexample/author checks remain separate, not added to final counts. '+\n"
    " 'Historical290 full validation is not relabelled299; metadata adds no functional section.'),\n")
text = once(text, " 'default_resource_query_count_unchanged':190,'default_event_player_output_count_unchanged':38,\n",
    " 'old_resource_and_player_information_production_pipelines_not_modified':True,\n")
text = once(text, " 'unparsed_notes_unchanged':10,'actual_server_generation_or_inventory_verified':False,",
    " 'unparsed_notes_unchanged':10,'actual_server_generation_or_inventory_verified':False,\n"
    " 'candidate_record_scope':{'stages':69,'original_levels':38,'groups':285,'packages':215},\n"
    " 'candidate_record_counts_are_not_actual_enemy_counts_or_probabilities':True,\n"
    " 'old_tracked_tests_changed':False,'source_compatibility_controller_constants_only':True,")
save('verify_publication_299.py', text)

text = read('finish_publication_298.py')
text = once(text, "cp['next_section']==index['next_section']==299", "cp['next_section']==index['next_section']==300")
text = once(text, "'next_section':299", "'next_section':300")
text = once(text, 'next299 only after', 'next300 only after')
save('finish_publication_299.py', text)

value = {'kind': 'ADAPTED_FROM_ACTUAL298_STRICT_PUBLICATION_CHAIN', 'files': baseline,
         'old_tools_modified': False, 'new_tools_executed': False, 'promotion_receipt': promotion_name,
         'promotion_receipt_sha256': promotion_sha, 'new_promoted_entries': 53, 'existing_production_entries': 2,
         'final_functional_and_compatibility_source_entries': 55, 'tracked_public_entries': 9,
         'old_tracked_test_maintenance': False, 'source_compatibility_repair': repair_name,
         'source_compatibility_repair_sha256': repair_sha, 'raw_public_files_exact': raw_logs,
         'public_preparation_archive_manifest': archive_name,
         'public_preparation_archive_manifest_sha256': sha256(archive_raw).hexdigest(),
         'promotion_hashes_do_not_substitute_for_final_actual_validation_maps': True}
with (HERE / 'BASELINE.json').open('xb') as stream: stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'cached_scripts_generated': 4, 'AST_compile_only': True, 'publication_Git_Qt_tests_executed': False}))
