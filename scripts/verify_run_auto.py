"""Verify authorized background sampling and persistent run state, without chatting."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import win32gui
from PySide6.QtWidgets import QApplication
from rouge.app import MainWindow

root=Path(__file__).resolve().parents[1]
app=QApplication([])
foreground=win32gui.GetForegroundWindow()
started=time.time()
window=MainWindow()
frames=set()
try:
    window.auto.setChecked(True)
    deadline=time.monotonic()+55
    while time.monotonic()<deadline:
        app.processEvents()
        observed=window.observation or {}
        run=observed.get('run') or {}
        if run.get('page')=='run_roster' and any(m['id']=='mechanist' for m in run.get('operators',[])) and observed.get('captured_at',0)>=started and not window.busy:
            frames.add(observed['captured_at'])
            if len(frames)>=2 and window.run.inventory_status()['complete']:break
        time.sleep(.02)
    status=window.capture_status.text()
    window.auto.setChecked(False)
    if len(frames)<2:
        (root/'.cache/run-auto-last.json').write_text(json.dumps(window.observation,ensure_ascii=False,indent=2),encoding='utf-8')
        raise RuntimeError(json.dumps({'capture_status':status,'page':(window.observation or {}).get('page'),
            'run':(window.observation or {}).get('run'),'target':window.capture.target},ensure_ascii=True))
    selected=window.observation['run']['selected_operator'] or 'mechanist'
    window.operator.setCurrentIndex(window.operator.findData(selected))
    scenario=window.damage_result['scenario']
    member=window.run.state['operators'][selected]
    assert selected=='mechanist' and scenario['operator']==selected
    assert scenario['elite']==member['fields']['elite'] and scenario['level']==member['fields']['level']
    assert member['skill_ranks']
    assert member.get('recruitment_kind')=='emergency_hire'
    wang=next((m for m in window.observation['run']['operators'] if m['id']=='char_2027_wang'),None)
    if wang:
        assert wang.get('advanced') and wang.get('recruitment_kind')=='non_emergency'
    assert scenario['skill_rank']==member['skill_ranks'][str(scenario['skill'])]
    assert scenario['inventory_status']['complete']
    foreground_unchanged=foreground==win32gui.GetForegroundWindow()
    session=window.run.state['id']
    observed_members=[m['name'] for m in window.observation['run']['operators']]
    receipt={'verified_at':time.time(),'fresh_frames':len(frames),'foreground_unchanged':foreground_unchanged,
        'game_in_background':window.capture.target['hwnd']!=foreground,
        'run_id':session,'members_this_frame':observed_members,
        'emergency_hires':[m['name'] for m in window.observation['run']['operators'] if m.get('recruitment_kind')=='emergency_hire'],
        'advanced_members':[m['name'] for m in window.observation['run']['operators'] if m.get('advanced')],
        'operator':scenario['operator'],'elite':scenario['elite'],'level':scenario['level'],
        'confirmed_run_fields':member['fields'],'recruitment_kind':member.get('recruitment_kind'),
        'calculation_module_reference':{'module_id':scenario['module_id'],'module_level':scenario['module_level']},
        'skill_ranks':window.run.state['operators']['mechanist']['skill_ranks'],
        'inventory_status':scenario['inventory_status'],'relic_ids':scenario['relic_ids'],
        'unconfirmed_training':scenario['unconfirmed_training'],'chat_requests':0,
        'limits':['潜能、信赖与未读取的模组使用标明的账号参考，不能声称本局全部必需字段均已读到。',
                  '图标与页面布局只在开发样本和当前客户端验证，尚无独立识别率。']}
    if not foreground_unchanged:
        receipt['limits'].append('验收期间前台窗口变化，不能用本次前后比较证明前台保持不变；脚本未调用前台窗口操作。')
    window.close()
    window=MainWindow()
    assert window.run.state['id']==session
    assert window.run.held_relic_ids()==sorted(receipt['relic_ids'])
    receipt['restart_restored_same_run']=True
    (root/'RUN_AUTO_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=True))
finally:window.close()
