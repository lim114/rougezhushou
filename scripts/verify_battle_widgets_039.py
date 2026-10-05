"""Qt preview checks called within the isolated cultivation-panel run."""
import copy,json,time
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import numpy as np
from rouge.battle_preview import battle_data

ROOT=Path(__file__).resolve().parents[1]

def verify_battle(window,app):
    panel=window.battle_preview;tabs=window.centralWidget()
    assert tabs.tabText(tabs.indexOf(panel))=='战斗预览'
    tabs.setCurrentWidget(panel);window.show();app.processEvents()
    snapshot=copy.deepcopy(window.run.state)
    stages=0;enemy_panels=0;main_rows=branches=0
    start=time.perf_counter()
    for sid,stage in battle_data()['stages'].items():
        # This is the same combo signal used by an identified node detail.
        window.target_stage.setCurrentIndex(window.target_stage.findData(sid));app.processEvents()
        assert panel.current_stage==sid and panel.stage_combo.currentData()==sid
        assert not panel.original.pixmap.isNull()
        assert panel.original.pixmap.width()==stage['image']['width']
        assert panel.grid.stage['id']==sid
        for row in panel.rows:
            main_rows+=bool(row['wave']);branches+=bool(row['branch'])
            assert row['absolute_time'] is None
        for i in range(1,panel.enemy_combo.count()):
            panel.enemy_combo.setCurrentIndex(i)
            assert panel.enemy_detail.toPlainText(),(sid,i)
            assert '基础' in panel.enemy_detail.toPlainText() or '引用' in panel.enemy_detail.toPlainText()
            enemy_panels+=1
        panel.enemy_combo.setCurrentIndex(0)
        panel.grid.grab() # Exercise painting for every map/route selection.
        stages+=1
    assert stages==105 and enemy_panels==1087
    assert main_rows==3639 and branches==299
    assert window.run.state==snapshot
    # Manual selection propagates to damage's stage without recursion.
    sid='ro6_n_1_2';panel.stage_combo.setCurrentIndex(panel.stage_combo.findData(sid))
    assert window.target_stage.currentData()==sid
    panel.wave_combo.setCurrentIndex(panel.wave_combo.findData(1))
    assert all(r['wave']==1 for r in panel.rows)
    panel.wave_combo.setCurrentIndex(0)
    panel.include_branches.setChecked(False)
    assert all(r['wave'] for r in panel.rows)
    panel.include_branches.setChecked(True)
    eid='enemy_1093_ccsbr';ei=next(i for i in range(1,panel.enemy_combo.count())
        if panel.enemy_combo.itemData(i)[0]==eid)
    panel.enemy_combo.setCurrentIndex(ei)
    assert panel.rows and all(r['action']['key']==eid for r in panel.rows)
    context={'difficulty':{'value':15},'zone':{'id':'zone_3'}}
    panel.set_context(context);high=panel.enemy_detail.toPlainText()
    assert '5,840' not in high # Numeric format remains exact reference text, no thousands-rounding.
    panel.set_context({'difficulty':{'value':0},'zone':{'id':'zone_3'}})
    assert high!=panel.enemy_detail.toPlainText()
    panel.set_context({'difficulty':{'value':16}})
    assert '环境无法确认' in panel.enemy_detail.toPlainText()
    panel.set_context({});assert '保密等级尚未确认' in panel.enemy_detail.toPlainText()
    rows_at=panel.rows;panel.set_context({});assert panel.rows is rows_at
    assert context['difficulty']['value']==15 and window.run.state==snapshot
    clicks=0;sizes=[]
    for width,height in ((880,700),(1050,830),(1450,950)):
        window.resize(width,height);app.processEvents()
        cell=panel.rows[0]['route']['start'];point=panel.grid.cell_center(cell)
        assert panel.grid.cell_at(point)==cell
        QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=point.toPoint())
        app.processEvents();assert panel.grid.selected['route']['start']==cell
        assert '本格共有' in panel.spawn_detail.toPlainText()
        assert '绝对出场时刻：未知' in panel.spawn_detail.toPlainText()
        assert panel.spawn_detail.isReadOnly() and panel.enemy_detail.isReadOnly()
        sizes.append({'window':[window.width(),window.height()],
            'grid':[panel.grid.width(),panel.grid.height()],'cell':cell})
        clicks+=1
    window.resize(1050,830);app.processEvents()
    screenshot=ROOT/'.cache/battle-039/offline-preview.png'
    assert window.grab().save(str(screenshot))
    # A synthetic node sample exercises the actual sample_received entry point,
    # without capture, game inputs, OCR or private-state updates.
    urgent=next(k for k,s in battle_data()['stages'].items()
        if s['name']==battle_data()['stages'][sid]['name'] and s['difficulty']=='FOUR_STAR')
    observation={'page':'node_detail','captured_at':time.time(),'nodes':[],
        'stage':{'name':battle_data()['stages'][urgent]['name'],'id':urgent,'visible_variant_id':urgent}}
    window.sample_received((np.zeros((180,320,3),dtype=np.uint8),observation));app.processEvents()
    assert panel.current_stage==urgent and window.target_stage.currentData()==urgent
    assert window.run.state==snapshot
    panel.set_stage('unrecognized-variant');assert panel.current_stage is None
    assert not panel.rows and panel.original.pixmap.isNull()
    window.target_stage.setCurrentIndex(0)
    assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
    return {'battle_stages_checked':stages,'battle_enemy_panels_checked':enemy_panels,
        'battle_main_spawn_rows':main_rows,'battle_branch_rows':branches,
        'battle_resize_clicks':clicks,'battle_sizes':sizes,
        'battle_preview_seconds':time.perf_counter()-start,'battle_data_readonly':True,
        'battle_context_correction_verified':True,'battle_unchanged_context_render_reused':True,
        'battle_sample_received_synthetic_verified':True,'battle_variant_sync_bidirectional':True,
        'battle_empty_unknown_variant_cleared':True,'battle_screenshot':str(screenshot.relative_to(ROOT))}
