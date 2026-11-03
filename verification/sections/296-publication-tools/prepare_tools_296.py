"""Pure cached producer; never imports or executes generated publication tools."""
from pathlib import Path
from hashlib import sha256
import ast
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / '.cache/p3-295-publication-prep'
PARENT = 'c772147f4ee4846464b32b88f51c88f874db3fcd'
OLD_PARENT = 'e517095f388baad3aa7824dbd5b9dee6a68fb450'
baseline = {}


def read(name):
    raw = (OLD / name).read_bytes()
    baseline[name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    return raw.decode('utf8').replace('295', '296').replace(OLD_PARENT, PARENT)


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def save(name, text):
    ast.parse(text, filename=name)
    compile(text, name, 'exec')
    assert OLD_PARENT not in text
    assert 'alpha-item' not in text and 'all38' not in text and 'and38 full reward' not in text
    with (HERE / name).open('xb') as stream:
        stream.write(text.encode('utf8'))


text = read('stage_section_295.py')
text = replace_once(text,
    "'PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py','rouge/player_node_information.py']",
    "'PROJECT_COMPLETED.md','PROJECT_REQUIREMENTS.md','WORK_IN_PROGRESS.md','rouge/app.py','rouge/battle_view.py','rouge/node_catalog_view.py','rouge/player_node_information.py']")
promotion_path = ROOT / 'verification/sections/296-preparation/promotion.json'
promotion_hash = sha256(promotion_path.read_bytes()).hexdigest()
text = replace_once(text,
    "promotion=json.loads((ROOT/'verification/sections/296-preparation/promotion.json').read_bytes())",
    "promotion_raw=(ROOT/'verification/sections/296-preparation/promotion.json').read_bytes()\n"
    + f"assert sha256(promotion_raw).hexdigest()=='{promotion_hash}'\n"
    + "promotion=json.loads(promotion_raw)\n"
    + "assert set(promotion['existing_production_changes'])=={'rouge/app.py','rouge/battle_view.py','rouge/node_catalog_view.py','rouge/player_node_information.py'}")
for prefix in ("section['next_section']", "cp['next_section']", "index['next_section']"):
    text = replace_once(text, prefix + '==296', prefix + '==297')
text = replace_once(text,
    "assert section['only_existing_production_sources_changed']==['rouge/node_catalog_view.py','rouge/player_node_information.py']",
    "assert section['only_existing_production_sources_changed']==['rouge/app.py','rouge/battle_view.py','rouge/node_catalog_view.py','rouge/player_node_information.py']\n"
    + "assert set(section['source_sha256'])==set(promotion['promoted'])\n"
    + "assert section['remaining_global_stage_floor_gaps_unchanged']==15\n"
    + "assert section['existing_engine_or_typed_reward_qualification_or_run_state_changed'] is False")
text = replace_once(text,
    "    assert actual['source_sha256_before']==actual['source_sha256_after']",
    "    assert actual['source_sha256_before']==actual['source_sha256_after']\n"
    + "    if label=='necessary_validation':assert actual['exit_code']==0\n"
    + "    else:assert actual['passed'] is True and actual['qt_exit_code']==0 and actual['verification_window_closed'] is True")
save('stage_section_296.py', text)

save('push_section_296.py', read('push_section_295.py'))

text = read('verify_publication_295.py')
text = replace_once(text, "idx=text.index('## 功能第294节')", "idx=text.index('## 功能第295节')")
text = replace_once(text, "cp['next_section']==296", "cp['next_section']==297")
text = replace_once(text, "'next_section':296", "'next_section':297")
start = text.index(" 'scope':('Functional296 adds one")
end = text.index(" 'necessary_methods_actual':", start)
text = text[:start] + """ 'scope':('Functional296 adds manual fixed-battle entry reading: actual '+
 str(window['actually_navigated_stage_count'])+' exact stages and '+str(window['actually_navigated_entry_count'])+
 ' admitted event/scene/choice navigations, '+str(len(window['explicit_exclusions']))+
 ' explicit ordinary-version exclusions, plus four separately sourced autopsy configurations. Actual '+
 str(section['necessary_validation']['methods_run'])+' necessary and '+str(window['unique_checks'])+
 ' unique native checks, '+str(window['screenshot_count'])+
 ' representative PNGs. Global floor/actual entry/quantity gaps stay open. Metadata adds no functional section.'),
""" + text[end:]
text = replace_once(text,
    "'old_typed_reward_contract_unchanged':True,'all38_old_reward_query_outputs_unchanged':True,\n 'PROJECT_PROGRESS_unchanged':True,'original_entry_gaps_unchanged':[25,57]",
    "'old_typed_reward_contract_unchanged':True,'typed_named_grant_count_unchanged':17,\n"
    + " 'PROJECT_PROGRESS_unchanged':True,'original_entry_gaps_unchanged':[25,57],\n"
    + " 'remaining_global_stage_floor_gaps_unchanged':15,'partial_direct_reference_scope_unchanged':[10,18,58],\n"
    + " 'whole_map_gaps_unchanged':[81,59],'actual_game_entry_verified':False")
text = replace_once(text,
    "window=load(section['native_windows_validation']['receipt'])",
    "window=load(section['native_windows_validation']['receipt'])\n"
    + "assert section['section']==296 and section['next_section']==297 and section['prior_commit']=='" + PARENT + "'\n"
    + "assert necessary['exit_code']==0 and window['passed'] is True and window['qt_exit_code']==0\n"
    + "assert necessary['source_sha256_before']==necessary['source_sha256_after']\n"
    + "assert window['source_sha256_before']==window['source_sha256_after']\n"
    + "assert section['typed_named_grant_count_unchanged']==17 and section['original_entry_gaps_unchanged']==[25,57]\n"
    + "assert section['remaining_global_stage_floor_gaps_unchanged']==15\n"
    + "assert section['partial_direct_reference_scope_unchanged']==[10,18,58] and section['whole_map_gaps_unchanged']==[81,59]\n"
    + "assert section['full_validation']['after_section']==290 and section['full_validation']['full_suite_rerun'] is False")
save('verify_publication_296.py', text)

text = read('finish_publication_295.py')
text = replace_once(text, "cp['next_section']==index['next_section']==296", "cp['next_section']==index['next_section']==297")
text = replace_once(text, "'next_section':296", "'next_section':297")
text = replace_once(text, 'next296 only after', 'next297 only after')
save('finish_publication_296.py', text)

with (HERE / 'BASELINE.json').open('xb') as stream:
    stream.write((json.dumps({'kind': 'ADAPTED_FROM_ACTUAL295_STRICT_PUBLICATION_CHAIN',
        'files': baseline, 'old_tools_modified': False, 'new_tools_executed': False,
        'promotion_receipt_sha256': promotion_hash,
        'promotion_hashes_are_historical_provenance_not_final_source_hashes': True}, indent=2) + '\n').encode('utf8'))
print(json.dumps({'cached_tools_generated': 4, 'AST_compile_only': True,
                  'publication_Git_Qt_tests_executed': False}))
