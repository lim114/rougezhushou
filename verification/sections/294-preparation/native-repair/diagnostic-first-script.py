from pathlib import Path
from hashlib import sha256
import os,json,sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root));os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication
from rouge.battle_view import BattlePreviewPanel
from rouge.branch_choice import OVERVIEW
packet=json.loads((root/'research/p3-map-direct-checkpoints-294/build-receipt.json').read_bytes())
data=json.loads((root/'rouge/data/fixed-landmark-references.json').read_bytes())
gui=QApplication([]);panel=BattlePreviewPanel();observations=[]
def candidates(sid):
    key=data['stages'][sid]['reference']
    known={(row['row'],row['col']) for row in packet['new_agreement_comparisons'] if row['reference']==key and row['accepted_for_runtime']}
    starts={(row['route']['start']['row'],row['route']['start']['col']) for row in panel.rows if row['route']['start']}
    return [row for row in panel.rows if row.get('branch') is None and any(
        cp['type']=='MOVE' and cp['cell'] and (cp['cell']['row'],cp['cell']['col']) in known
        and (cp['cell']['row'],cp['cell']['col']) not in starts for cp in row['route']['checkpoints'])]
try:
    for sid in ('ro6_n_3_2','ro6_e_3_2','ro6_t_5','ro6_e_t_5'):
        panel._load_stage(sid);panel.include_branches.setChecked(False)
        before=candidates(sid)
        row={'stage':sid,'before_reset':{'enemy':panel.enemy_combo.currentData(),
            'branch':panel.enemy_choices.branch.currentData(),'wave':panel.wave_combo.currentData(),
            'rows':len(panel.rows),'new_MOVE_candidates':len(before)}}
        assert panel.enemy_choices.select_branch(OVERVIEW)
        assert panel.enemy_choices.select_value(None)
        panel.wave_combo.setCurrentIndex(panel.wave_combo.findData(None))
        after=candidates(sid);assert after
        row['after_reset']={'enemy':panel.enemy_combo.currentData(),'branch':panel.enemy_choices.branch.currentData(),
            'wave':panel.wave_combo.currentData(),'rows':len(panel.rows),'new_MOVE_candidates':len(after)}
        chosen=after[0];panel.wave_combo.setCurrentIndex(panel.wave_combo.findData(chosen['wave']))
        enemy=next(panel.enemy_combo.itemData(i) for i in range(panel.enemy_combo.count())
            if panel.enemy_combo.itemData(i) and panel.enemy_combo.itemData(i)[0]==chosen['action']['key'])
        assert panel.enemy_choices.select_value(enemy)
        observations.append(row)
finally:panel.close();panel.deleteLater();gui.processEvents()
report={'section':294,'kind':'actual_offscreen_fixture_filter_precondition_diagnosis',
 'observations':observations,'no_source_or_private_state_mutation':True,
 'not_native_acceptance':True,'not_game_or_chat':True,
 'source_sha256':{p:sha256((root/p).read_bytes()).hexdigest() for p in ('rouge/battle_view.py','rouge/branch_choice.py','scripts/verify_direct_map_window_294.py')}}
dest=root/'verification/sections/294-preparation/actual-filter-diagnosis.json'
with dest.open('xb') as f:f.write((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps(report,ensure_ascii=False))
