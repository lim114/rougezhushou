from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROMOTE=('rouge/named_reward_items_view.py','tests/test_named_reward_items_view_301.py')
def pin(path):
    raw=path.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
process=json.loads((HERE/'first-real-direct-dialog/process.json').read_bytes())
actual=json.loads((HERE/'first-real-direct-dialog/actual-result.json').read_bytes())
if not(process['actual_exit']==0 and process['source_unchanged']is True and actual['successful']is True):
    raise ValueError('Actual cache dialog check did not pass.')
out={
 'kind':'SECTION301_VIEW_CACHE_READY_NOT_FORMAL_PRODUCT_OR_NATIVE_ACCEPTANCE',
 'created_at':datetime.now(timezone.utc).isoformat(),
 'candidate_root':str(HERE/'candidate'),
 'promote_files':{name:pin(HERE/'candidate'/name)for name in PROMOTE},
 'backend_handoff':{'file':'.cache/p3-301-backend/HANDOFF.json',
                    **pin(ROOT/'.cache/p3-301-backend/HANDOFF.json')},
 'API':{'class':'NamedRewardItemsPanel','set_reference':'set_reference(event_id, *, scope_key=None)',
        'controls':['choice','reading_tabs','player_text','source_text','icon','packet'],
        'default_choice':-1,'selection_opens_item_directly':True,'second_item_button':False,
        'combo_data':'full choice_key / reference_id',
        'combo_label':'流程N · 选项M：标题 → 物品名',
        'tabs':['玩家说明','资料与依据'],
        'image_accessibleName':'固定资料图标：<物品名>',
        'image_width':96,
        'reading_identity':['event','parent_scope','packet.scope_key','scene?','choice?','reference?'],
        'same_valid_selected_and_unselected_reading_preserved':True,
        'scope_change_or_source_failure_clears_then_manual_reselect':True},
 'actual_cache_checks':{
     'directory':'first-real-direct-dialog','actual_tests_run':actual['actual_tests_run'],
     'actual_exit':process['actual_exit'],'failures':actual['failures'],'errors':actual['errors'],
     'skipped':actual['skipped'],'source_unchanged':process['source_unchanged'],
     'bound_source_count':len(process['source_before']),
     'QPA_platform':actual['QPA_platform'],
     'excluded_modules_not_loaded':actual['excluded_modules_not_loaded'],
     'first_actual_run_failed':False,
     'test_log':'first-real-direct-dialog/stderr',
     'counts_not_additive_to_formal_product_or_native':True},
 'scope_limits':['13 item descriptions and16 exact choice references; no new grant or numeric mechanism',
                 'quantity/full_pool/actual eligibility/claim/held/effect remain unknown',
                 'relic and scrap remain separate; item unlock text is not option eligibility',
                 '17 typed,25/57 entry gaps,10 notes and15 stage floors unchanged'],
 'production_docs_Git_MainWindow_game_chat_private_modified_or_executed':False,
 'owned_files':{p.relative_to(HERE).as_posix():pin(p)for p in HERE.rglob('*')
                if p.is_file()and p.name not in('HANDOFF.json',)and'__pycache__'not in p.parts}}
(HERE/'HANDOFF.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'HANDOFF':pin(HERE/'HANDOFF.json'),'promote_files':out['promote_files'],
                 'actual_cache_checks':out['actual_cache_checks']},ensure_ascii=False))
