"""Real technology controls, temporary public accounts, no game or chat."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT=Path(sys.argv[1]); OUT=Path(sys.argv[2]); OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
import rouge.app as product
from rouge.technology_view import TechnologyReferencePanel

app=QApplication([]); cases=[]
with tempfile.TemporaryDirectory(prefix='technology-window128-') as directory:
    base=Path(directory)
    product.RUN_STATE=base/'run.json'; product.OPERATOR_STATE=base/'operator-state.json'; product.SETTINGS=base/'settings.json'
    path=base/'technology-state.json'
    window=product.MainWindow(); window.show(); app.processEvents()
    try:
        window.centralWidget().setCurrentIndex(5); app.processEvents()
        panel=window.technology_reference
        assert panel.account_state.path==path and not path.exists()
        assert panel.nodes.count()==57 and panel.account_state.counts()['unknown']==57
        assert '账户解锁状态：未知' in panel.text.toPlainText()
        before_run=copy.deepcopy(window.run.state); before_account=copy.deepcopy(window.operator_observations)
        before_damage=copy.deepcopy(window.damage_result)
        assert panel.nodes.itemData(0)=='rogue_6_outbuff_1'
        cases.append('real tab opens all57 unknown without creating a file')
        one,two='rogue_6_outbuff_25','rogue_6_outbuff_35'
        panel.search.setText('颊囊'); app.processEvents()
        assert panel.nodes.count()==2
        panel.nodes.setCurrentIndex(panel.nodes.findData(one)); panel.status_buttons['unlocked'].click(); app.processEvents()
        panel.nodes.setCurrentIndex(panel.nodes.findData(two)); panel.status_buttons['locked'].click(); app.processEvents()
        assert panel.account_state.counts()=={'unknown':55,'unlocked':1,'locked':1}
        assert panel.account_state.view(one)['status']=='unlocked' and panel.account_state.view(two)['status']=='locked'
        assert '用户记录' in panel.text.toPlainText() and '实际启用与数值效果仍未知' in panel.text.toPlainText()
        assert '账户解锁状态：未知' not in panel.text.toPlainText()
        panel.status_filter.setCurrentIndex(panel.status_filter.findData('unlocked')); app.processEvents()
        assert panel.nodes.count()==1 and panel.nodes.currentData()==one
        panel.search.setText('没有这种科技'); app.processEvents()
        assert panel.nodes.count()==0 and all(not b.isEnabled() for b in panel.status_buttons.values())
        panel.search.setText('颊囊'); panel.status_filter.setCurrentIndex(0); app.processEvents()
        cases.append('same-name IDs separate; status and text filters; empty controls disabled')
        default=panel.account_state.selected_profile
        panel.new_profile_name.setText('公开测试乙'); panel.create_profile_button.click(); app.processEvents()
        second=panel.account_state.selected_profile
        assert second!=default and panel.account_state.counts()['unknown']==57
        panel.nodes.setCurrentIndex(panel.nodes.findData(one)); panel.status_buttons['locked'].click(); app.processEvents()
        assert panel.account_state.view(one)['status']=='locked'
        panel.profiles.setCurrentIndex(panel.profiles.findData(default)); app.processEvents()
        assert panel.account_state.view(one)['status']=='unlocked'
        panel.new_profile_name.setText('公开测试乙'); panel.create_profile_button.click(); app.processEvents()
        assert panel.profiles.count()==2 and '同名' in panel.persistence.text()
        panel.new_profile_name.clear(); panel.populate()
        panel.nodes.setCurrentIndex(panel.nodes.findData(one)); panel.status_buttons['unknown'].click(); app.processEvents()
        assert panel.account_state.view(one)['status']=='unknown' and panel.account_state.view(two)['status']=='locked'
        panel.status_buttons['unlocked'].click(); app.processEvents()
        panel.search.clear(); panel.nodes.setCurrentIndex(panel.nodes.findData(one)); app.processEvents()
        assert window.run.state==before_run and window.operator_observations==before_account and window.damage_result==before_damage
        cases.append('create/switch profiles, duplicate-name refusal, explicit unknown, no run/account/damage changes')
        assert panel.grab().save(str(OUT/'technology-account.png'))
        saved=path.read_bytes()
        run_id=window.run.state['id']; window.reset_run_button.click(); app.processEvents()
        assert window.run.state['id']!=run_id and path.read_bytes()==saved
        assert window.operator_observations==before_account
        assert panel.account_state.view(one)['status']=='unlocked'
        cases.append('actual new-run button preserves saved technology and operator account')
        assert not window.auto.isChecked() and window.capture.target is None and window.desktop.process is None
    finally:
        window.close(); app.processEvents()
    # Future metadata is public fixture data, inserted while no window is open.
    saved_state=json.loads(path.read_text(encoding='utf-8'))
    saved_state['profiles'][default]['nodes'][one]['future-note']={'keep':['public fixture']}
    saved_state['profiles'][default]['nodes'][one]['actual_activation']=True
    path.write_text(json.dumps(saved_state),encoding='utf-8'); saved=path.read_bytes()
    # A second actual MainWindow verifies disk restore, without writing at load.
    restored=product.MainWindow(); restored.show(); app.processEvents()
    try:
        panel=restored.technology_reference
        assert path.read_bytes()==saved and panel.profiles.count()==2
        assert panel.account_state.selected_profile==default
        assert panel.account_state.view(one)['status']=='unlocked' and panel.account_state.view(two)['status']=='locked'
        assert panel.account_state.view(one)['actual_activation'] is None
        panel.nodes.setCurrentIndex(panel.nodes.findData(one)); panel.status_buttons['unlocked'].click(); app.processEvents()
        actual=json.loads(path.read_text(encoding='utf-8'))['profiles'][default]['nodes'][one]
        assert actual['future-note']=={'keep':['public fixture']} and actual['actual_activation'] is True
        assert panel.account_state.view(one)['actual_activation'] is None
        cases.append('manual edits retain opaque node metadata without consuming activation claims')
        panel.profiles.setCurrentIndex(panel.profiles.findData(second)); app.processEvents()
        assert panel.account_state.view(one)['status']=='locked'
        cases.append('close/reopen restores profile selection and per-account node records')
        # Independent unusable file: manual UI changes remain session-only.
        damaged=base/'damaged.json'; damaged.write_text('{broken',encoding='utf-8')
        protected=TechnologyReferencePanel(account_path=damaged); protected.show(); app.processEvents()
        protected.status_buttons['unlocked'].click(); app.processEvents()
        assert damaged.read_text(encoding='utf-8')=='{broken'
        assert protected.account_state.view('rogue_6_outbuff_1')['status']=='unlocked'
        assert '仅在当前运行有效' in protected.persistence.text()
        protected.close(); app.processEvents()
        cases.append('unreadable-file notice and session records preserve original bytes')
        assert not restored.auto.isChecked() and restored.capture.target is None and restored.desktop.process is None
    finally:
        restored.close(); app.processEvents()

receipt={'passed':True,'actual_window_cases':cases,'private_state_included':False,
    'native_windows_game_chat_verified':False,'game_capture':False,'chat_requests':0,
    'source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in (
        'rouge/app.py','rouge/technology_view.py','rouge/technology_state.py','rouge/technology.py')}}
(OUT/'window.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)},ensure_ascii=False))
