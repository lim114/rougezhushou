from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROMOTE=('rouge/ritual_weakening_view.py','tests/test_ritual_weakening_view_302.py')
def pin(path):
    raw=path.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def methods(path):
    parsed=ast.parse(path.read_bytes())
    return {node.name:ast.dump(node,include_attributes=False)for cls in parsed.body if isinstance(cls,ast.ClassDef)
            for node in cls.body if isinstance(node,ast.FunctionDef)and node.name.startswith('test_')}
first=HERE/'first-real-direct-dialog'
corrected=HERE/'corrected-direct-dialog'
initial=json.loads((first/'actual-result.json').read_bytes())
actual=json.loads((corrected/'actual-result.json').read_bytes())
process=json.loads((corrected/'process.json').read_bytes())
old=methods(first/'source-before'/PROMOTE[1]);new=methods(HERE/'candidate'/PROMOTE[1])
if not all(new.get(name)==body for name,body in old.items()):
    raise ValueError('Original necessary test body changed.')
if not(process['actual_exit']==0 and process['source_unchanged']is True and actual['successful']is True):
    raise ValueError('Actual cache checks did not pass.')
out={
 'kind':'SECTION302_VIEW_CACHE_READY_NOT_FORMAL_PRODUCT_OR_NATIVE_ACCEPTANCE',
 'created_at':datetime.now(timezone.utc).isoformat(),
 'candidate_root':str(HERE/'candidate'),
 'promote_files':{name:pin(HERE/'candidate'/name)for name in PROMOTE},
 'backend_handoff':{'file':'.cache/p3-302-backend/HANDOFF_FINAL.json',
                    **pin(ROOT/'.cache/p3-302-backend/HANDOFF_FINAL.json')},
 'API':{'class':'RitualWeakeningPanel','set_reference':'set_reference(event_id, *, scope_key=None)',
        'controls':['choice','reading_tabs','player_text','source_text','packet','open_stage_button',
                    'battle_window','battle_preview'],
        'default_choice':-1,'choice_opens_battle':False,
        'combo_data':'full choice_key / reference_id','combo_label':'流程N · 选项M：标题',
        'tabs':['玩家说明','资料与依据'],
        'stage_button':'查看相关作战：畸症','button_method':'open_related_stage() -> bool',
        'battle_type':'independent QDialog containing existing BattlePreviewPanel',
        'related_stage':'ro6_b_6','no_new_signal_or_token':True,
        'dialog_size':[900,680],'battle_size':[1180,850],
        'same_valid_scope_preserves_battle_objects_and_readers':True,
        'source_failure_or_scope_change_closes_deletes_battle_tree':True,
        'source_restore_requires_manual_selection_and_click':True},
 'actual_cache_checks':{
     'first_directory':'first-real-direct-dialog','first_actual_methods':initial['actual_tests_run'],
     'first_failures':initial['failures'],'first_errors':initial['errors'],
     'first_reason':'isolated runtime copied catalog.py but missed public node-events.json required by battle stage_groups',
     'corrected_directory':'corrected-direct-dialog','actual_tests_run':actual['actual_tests_run'],
     'actual_exit':process['actual_exit'],'failures':actual['failures'],'errors':actual['errors'],
     'skipped':actual['skipped'],'source_unchanged':process['source_unchanged'],
     'original_test_methods_unchanged_AST':len(old),
     'new_test_methods':sorted(set(new)-set(old)),
     'bound_source_count':len(process['source_before']),'QPA_platform':actual['QPA_platform'],
     'excluded_modules_not_loaded':actual['excluded_modules_not_loaded'],
     'counts_not_additive_to_formal_product_or_native':True},
 'player_limits':['First-disaster no-destroy limitation retained; no inferred later-phase immunity',
                  'Narrative cannot swallow life is explicitly not no-damage or no-HP-loss',
                  'Private key replaces the corresponding one requirement, not all three at once',
                  'Damage scale0.5 remains technical configuration only; no numerical application',
                  'Related fixed battle is not an immediate transition or actual entered battle',
                  'All8 actual fields unknown, calculation_applied/run_state_updated false'],
 'production_docs_Git_MainWindow_game_chat_private_modified_or_executed':False,
 'owned_files':{p.relative_to(HERE).as_posix():pin(p)for p in HERE.rglob('*')
                if p.is_file()and p.name!='HANDOFF.json'and'__pycache__'not in p.parts}}
(HERE/'HANDOFF.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'HANDOFF':pin(HERE/'HANDOFF.json'),'promote_files':out['promote_files'],
                 'actual_cache_checks':out['actual_cache_checks']},ensure_ascii=False))
