from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import argparse, json, sys, time, subprocess, types

R=Path.cwd();sys.path.insert(0,str(R))
parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('before','after'),required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
baseline='b5ce07b802f51d42095f10fb12ce261b08dbd2f1'
changed=['current_reward_view','current_settlement_modes_view','current_battle_view','expansion_view']
from PySide6.QtWidgets import QApplication
qt=QApplication([]);assert qt.platformName()=='windows'
import rouge
source={}
for name in changed:
    path='rouge/'+name+'.py'
    raw=subprocess.check_output(['git','show',baseline+':'+path]) if args.mode=='before' else(R/path).read_bytes()
    source[path]=sha256(raw).hexdigest()
    if args.mode=='before':
        module=types.ModuleType('rouge.'+name);module.__file__=str(R/path);module.__package__='rouge'
        sys.modules[module.__name__]=module;setattr(rouge,name,module)
        exec(compile(raw,module.__file__,'exec'),module.__dict__)

from rouge.current_battle_view import CurrentBattlePanel
from rouge import current_reward_reference as rewards, current_settlement_modes_reference as settlement
from rouge.current_battle_reference import picture_for_enemy
actions=[];measures=[];counts={}
class CountBattle(CurrentBattlePanel):
    def __init__(self,*a,**k):self.action_rebuilds=0;super().__init__(*a,**k)
    def _actions_changed(self,*a,**k):self.action_rebuilds+=1;return super()._actions_changed(*a,**k)

def digest(value):return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')).hexdigest()
def snapshot(panel,label):
    v={'stage_result':panel.result,'summary':panel.summary.toPlainText(),'technical':panel.technical.toPlainText(),
       'enemy':panel.enemy_key,'enemy_text':panel.enemy_player.toPlainText(),'action':panel.action_key,
       'action_text':panel.action_player.toPlainText(),'queue':panel.queue_kind.currentData(),
       'group':panel.action_group.currentData(),'focus':panel.action_focus.currentData(),
       'enemy_choices':[(panel.enemy_combo.itemText(i),panel.enemy_combo.itemData(i))for i in range(panel.enemy_combo.count())],
       'actions':[(panel.actions.item(i).text(),panel.actions.item(i).data(256))for i in range(panel.actions.count())],
       'reward_result':panel.rewards.result,'reward_text':panel.rewards.player.toPlainText(),'reward_technical':panel.rewards.technical.toPlainText(),
       'settlement_result':panel.settlement.result,'settlement_text':panel.settlement.player.toPlainText(),'settlement_technical':panel.settlement.technical.toPlainText(),
       'tab':panel.tabs.currentIndex()}
    actions.append({'stage_id':panel.stage_id,'action':label,'complete_data_and_text_sha256':digest(v)})

for sid in ('ro6_n_5_2','ro6_b_7'):
    start=time.perf_counter()
    with patch.object(rewards,'stage_rewards',wraps=rewards.stage_rewards)as r,patch.object(settlement,'stage_reference',wraps=settlement.stage_reference)as s:
        p=CountBattle(sid)
        counts[sid]={'construction_reward_reads':r.call_count,'construction_settlement_reads':s.call_count}
    measures.append({'stage_id':sid,'action':'construct','ms':1000*(time.perf_counter()-start)})
    assert p.result is not None;snapshot(p,'initial')
    p.enemy_choices.select_value(p.result['enemies'][0]['key']);snapshot(p,'select_first_exact_enemy')
    p.action_focus.setCurrentIndex(p.action_focus.findData('enemy'));p.actions.setCurrentRow(0);snapshot(p,'enemy_action_filter')
    p.action_rebuilds=0;start=time.perf_counter();assert p.refresh_reference()
    measures.append({'stage_id':sid,'action':'filtered_refresh','ms':1000*(time.perf_counter()-start)})
    counts[sid]['filtered_refresh_rebuilds']=p.action_rebuilds;snapshot(p,'filtered_refresh')
    target=next((a for a in p.result['actions']if a['queue']['kind']=='branch'),p.result['actions'][-1])
    p.queue_kind.setCurrentIndex(p.queue_kind.findData('main'if target['queue']['kind']=='branch'else'branch'))
    p.action_rebuilds=0;assert p.focus_action(target)
    counts[sid]['focus_queue_change_rebuilds']=p.action_rebuilds;snapshot(p,'exact_action_navigation')
    p.enemy_search.setText(p.result['enemies'][0]['name']);snapshot(p,'name_search')
    p.enemy_search.clear();snapshot(p,'clear_search')
    from rouge import current_battle_reference as battle
    with patch.object(battle,'stage_reference',return_value=None):assert not p.refresh_reference()
    assert p.result is None and p.rewards.result is None and p.settlement.result is None
    snapshot(p,'source_unavailable')
    assert p.refresh_reference();snapshot(p,'source_restored_requires_manual_selection')
    p.close()

from rouge.expansion_view import ExpansionUpdatePanel
from PySide6.QtCore import Qt
e=ExpansionUpdatePanel(categories=('stages',));e.category.setCurrentIndex(e.category.findData('stages'))
for i in range(e.entries.count()):
    if e.entries.item(i).data(Qt.ItemDataRole.UserRole)=='ro6_b_7':e.entries.setCurrentRow(i);break
assert e.result and e.image_raw
expansion={'result':e.result,'player':e.player.toPlainText(),'technical':e.technical.toPlainText(),'stage_info':e.stage_info,'image_bytes_sha256':sha256(e.image_raw).hexdigest()}
e.close()
result={'mode':args.mode,'baseline_commit':baseline,'source_sha256':source,'qpa':qt.platformName(),
    'rows':actions,'measurements':measures,'work_counts':counts,'all_data_and_text_sha256':digest(actions),
    'expansion_data_and_text_sha256':digest(expansion),'real_game_or_chat_instantiated':False,
    'actual_private_state_read_or_written':False,'numeric_accuracy_claimed':False}
args.output.parent.mkdir(parents=True,exist_ok=True);assert not args.output.exists()
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'mode':args.mode,'actions':len(actions),'data_sha256':result['all_data_and_text_sha256'],'counts':counts}))
