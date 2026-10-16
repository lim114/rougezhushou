"""Build cache-only publication producers from the preserved296 chain; never execute them."""
import ast
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / '.cache/p3-296-publication-prep'
OLD_PARENT = 'c772147f4ee4846464b32b88f51c88f874db3fcd'
PARENT = '7706a982b84fe64148da87d6d073786704c188d1'
MAINTENANCE = 'tests/test_documented_item_integration_295.py'
MAINTENANCE_SHA = '4e946fd3579f37bc3f222f855f9c23811c1279c946a4345431161ed141fcc2f9'
baseline = {}


def read(name):
    raw = (OLD / name).read_bytes()
    baseline[name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    return raw.decode('utf8').replace('296', '297').replace(OLD_PARENT, PARENT)


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def save(name, text):
    compile(ast.parse(text, filename=name), name, 'exec')
    assert OLD_PARENT not in text and 'actually_navigated_stage_count' not in text
    assert 'actually_navigated_entry_count' not in text and 'explicit_exclusions' not in text
    with (HERE / name).open('xb') as stream:
        stream.write(text.encode('utf8'))


raw = (ROOT / 'verification/sections/297-preparation/promotion.json').read_bytes()
promotion_sha = sha256(raw).hexdigest()
record = json.loads(raw)
assert record['section'] == 297 and len(record['promoted']) == 18
assert set(record['existing_production_changes']) == {'rouge/node_catalog_view.py', 'rouge/player_node_information.py'}
migration_path = ROOT / 'verification/sections/297-preparation/historical295-presentation-scope/migration.json'
migration = json.loads(migration_path.read_bytes())
assert migration['path'] == MAINTENANCE and migration['after_sha256'] == MAINTENANCE_SHA

text = read('stage_section_296.py')
text = once(text,
    "'PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/app.py','rouge/battle_view.py','rouge/node_catalog_view.py','rouge/player_node_information.py']",
    "'PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py','rouge/player_node_information.py','" + MAINTENANCE + "']")
text = once(text,
    "assert sha256(promotion_raw).hexdigest()=='6fea735e431a588ba0de99201f073ebde8a42a56bfdd3fc9de9b3d5cc691ebe2'",
    "assert sha256(promotion_raw).hexdigest()=='" + promotion_sha + "'")
text = once(text,
    "assert set(promotion['existing_production_changes'])=={'rouge/app.py','rouge/battle_view.py','rouge/node_catalog_view.py','rouge/player_node_information.py'}",
    "assert len(promotion['promoted'])==18\n"
    + "assert set(promotion['existing_production_changes'])=={'rouge/node_catalog_view.py','rouge/player_node_information.py'}\n"
    + "maintenance_path='" + MAINTENANCE + "'\n"
    + "migration=json.loads((ROOT/'verification/sections/297-preparation/historical295-presentation-scope/migration.json').read_bytes())\n"
    + "assert migration['path']==maintenance_path and migration['after_sha256']=='" + MAINTENANCE_SHA + "'\n"
    + "assert sha256((ROOT/maintenance_path).read_bytes()).hexdigest()==migration['after_sha256']\n"
    + "assert migration['all_original_assertion_AST_preserved'] is True\n"
    + "assert migration['current_default37_nontarget_and190resource_hashes_covered_by']=='tests/test_expedition_integration_297.py'")
text = once(text,
    "assert section['only_existing_production_sources_changed']==['rouge/app.py','rouge/battle_view.py','rouge/node_catalog_view.py','rouge/player_node_information.py']",
    "assert section['only_existing_production_sources_changed']==['rouge/node_catalog_view.py','rouge/player_node_information.py']\n"
    + "assert section['existing_source_changes_including_test_maintenance']==sorted(['rouge/node_catalog_view.py','rouge/player_node_information.py',maintenance_path])\n"
    + "assert section['old_resource_query_count_unchanged']==190 and section['other_event_player_output_count_unchanged']==37\n"
    + "assert section['unparsed_notes_unchanged']==10")
text = once(text, "assert set(section['source_sha256'])==set(promotion['promoted'])",
    "assert set(section['source_sha256'])==set(promotion['promoted'])|{maintenance_path}\n"
    + "assert len(section['source_sha256'])==19 and section['source_sha256'][maintenance_path]==migration['after_sha256']")
text = once(text, "new=[name for name in promotion['promoted'] if name not in tracked]",
    "raw_archived_logs={\n"
    + " 'verification/sections/297-preparation/'+name:row['sha256']\n"
    + " for name,row in promotion['archived_inputs'].items()\n"
    + " if name in {'backend/first-real-pure-api-tests/stderr','backend/first-real-pure-api-tests/stdout',\n"
    + " 'backend/first-real-source-build/stderr','backend/first-real-source-build/stdout'}}\n"
    + "assert len(raw_archived_logs)==4\n"
    + "new=[name for name in promotion['promoted'] if name not in tracked]")
text = once(text,
    "            assert path.suffix in {'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout','.html'}",
    "            relative=path.relative_to(ROOT).as_posix()\n"
    + "            assert path.suffix in {'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout','.html'} or relative in raw_archived_logs\n"
    + "            if relative in raw_archived_logs:assert sha256(path.read_bytes()).hexdigest()==raw_archived_logs[relative]")
for prefix in ("section['next_section']", "cp['next_section']", "index['next_section']"):
    text = once(text, prefix + '==297', prefix + '==298')
save('stage_section_297.py', text)
save('push_section_297.py', read('push_section_296.py'))

text = read('verify_publication_296.py')
text = once(text, "idx=text.index('## 功能第295节')", "idx=text.index('## 功能第296节')")
text = once(text, "section['next_section']==297", "section['next_section']==298")
text = once(text, "cp['next_section']==297", "cp['next_section']==298")
text = once(text, "'next_section':297", "'next_section':298")
start = text.index(" 'scope':('Functional297 adds manual fixed-battle entry reading")
end = text.index(" 'necessary_methods_actual':", start)
text = text[:start] + """ 'scope':('Functional297 adds manual expedition references for three complete choices in 未涉足之树: '+
 'rest gives2 hope on choice; ordinary dispatch return pool/promotion stay unknown; root exploration gives2 hope and '+
 'beacon on return without inventing beacon count. The full beacon icon/usage/description is opened manually. '+
 'Four original choice identities/four scenes are preserved; return explanatory text is not a fourth current choice. Actual '+
 str(section['necessary_validation']['methods_run'])+' necessary methods and '+str(window['unique_checks'])+
 ' unique native checks, '+str(window['screenshot_count'])+' representative PNGs. '+
 'Same-scope reading is retained; source failure clears stale content and restoration never selects automatically. '+
 'Actual dispatch/return/inventory/cultivation and server execution remain unknown; metadata adds no functional section.'),
""" + text[end:]
text = once(text,
    "assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]",
    "assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]\n"
    + "assert section['unparsed_notes_unchanged']==10 and section['old_resource_query_count_unchanged']==190\n"
    + "assert section['other_event_player_output_count_unchanged']==37\n"
    + "assert section['source_sha256']['" + MAINTENANCE + "']=='" + MAINTENANCE_SHA + "'")
text = once(text,
    "'old_typed_reward_contract_unchanged':True,'typed_named_grant_count_unchanged':17,",
    "'old_typed_reward_contract_unchanged':True,'typed_named_grant_count_unchanged':17,\n"
    + " 'old_resource_query_count_unchanged':190,'other_event_player_output_count_unchanged':37,\n"
    + " 'unparsed_notes_unchanged':10,'actual_dispatch_return_inventory_or_cultivation_verified':False,")
text = once(text,
    "'本节待普通推送并核对真实远端，源码/要求/验收/索引同提交。'",
    "'待普通推送核对真实远端，源码/要求/验收/索引同提交。'")
save('verify_publication_297.py', text)

text = read('finish_publication_296.py')
text = once(text, "cp['next_section']==index['next_section']==297", "cp['next_section']==index['next_section']==298")
text = once(text, "'next_section':297", "'next_section':298")
text = once(text, 'next297 only after', 'next298 only after')
save('finish_publication_297.py', text)

value = {'kind': 'ADAPTED_FROM_ACTUAL296_STRICT_PUBLICATION_CHAIN', 'files': baseline,
         'old_tools_modified': False, 'new_tools_executed': False,
         'promotion_receipt_sha256': promotion_sha, 'promotion_provenance_entries': 18,
         'historical295_test': {'path': MAINTENANCE, 'final_sha256': MAINTENANCE_SHA,
                               'migration_sha256': sha256(migration_path.read_bytes()).hexdigest()},
         'promotion_hashes_are_historical_provenance_not_final_source_hashes': True}
with (HERE / 'BASELINE.json').open('xb') as stream:
    stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'cached_tools_generated': 4, 'AST_compile_only': True, 'publication_Git_Qt_tests_executed': False}))
