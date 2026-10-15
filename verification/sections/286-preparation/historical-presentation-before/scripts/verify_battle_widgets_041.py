"""Qt local occurrence/speed references in an isolated offline window."""
import copy,time
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
import numpy as np
from rouge.battle_preview import battle_data
from rouge.spawn_reference import local_sequence,ordinal_offset

ROOT=Path(__file__).resolve().parents[1]


def verify_battle(window,app):
    panel=window.battle_preview;tabs=window.centralWidget()
    assert tabs.tabText(tabs.indexOf(panel))=='战斗预览'
    tabs.setCurrentWidget(panel);window.show();app.processEvents()
    snapshot=copy.deepcopy(window.run.state)
    stages=enemy_panels=main_rows=branches=main_instances=branch_instances=occurrence_selections=0
    start=time.perf_counter()
    for sid,stage in battle_data()['stages'].items():
        window.target_stage.setCurrentIndex(window.target_stage.findData(sid));app.processEvents()
        assert panel.current_stage==sid and panel.stage_combo.currentData()==sid
        assert not panel.original.pixmap.isNull()
        assert panel.original.pixmap.width()==stage['image']['width']
        assert panel.grid.stage['id']==sid
        for index,row in enumerate(panel.rows):
            main_rows+=bool(row['wave']);branches+=bool(row['branch'])
            if row['wave']:main_instances+=row['action']['count']
            else:branch_instances+=row['action']['count']
            assert row['absolute_time'] is None and row['probability'] is None
            panel.spawn_list.setCurrentRow(index)
            seq=local_sequence(row,limit=0)
            assert not seq['pending'] and seq['count']
            assert not panel.occurrence_bar.isHidden()
            assert panel.occurrence.value()==panel.grid.selected_ordinal==1
            assert panel.occurrence.maximum()==seq['count']
            assert '名义偏移不是开局绝对时刻' in panel.spawn_detail.toPlainText()
            assert '队列后 +' in panel.spawn_list.currentItem().text()
            for ordinal in sorted({1,seq['count']}):
                panel.occurrence.setValue(ordinal)
                assert panel.grid.selected_ordinal==ordinal
                expected=ordinal_offset(row,ordinal)
                assert '+'+format(expected,'g')+'秒' in panel.occurrence_label.text()
                anchor='所选阶段' if row['branch'] else '本片段'
                assert anchor in panel.occurrence_label.text()
                occurrence_selections+=1
            if row['branch']:
                assert row['route']['start'] is None
                assert 'useExtraRoute' in panel.spawn_detail.toPlainText()
            assert panel.spawn_detail.isReadOnly()
        for i in range(1,panel.enemy_combo.count()):
            panel.enemy_combo.setCurrentIndex(i)
            text=panel.enemy_detail.toPlainText()
            assert text and '基础移速属性（未乘关卡倍率）' in text,(sid,i)
            assert '关卡移速倍率：0.5' in text
            assert '仅基础属性×关卡倍率的速度参考（格/秒）' in text
            assert '完整有效移速：未知' in text
            enemy_panels+=1
        panel.enemy_combo.setCurrentIndex(0);panel.grid.grab()
        stages+=1
    assert stages==105 and enemy_panels==1087
    assert main_rows==3639 and branches==299
    assert main_instances==5314 and branch_instances==334
    assert window.run.state==snapshot
    sid='ro6_n_1_2';panel.stage_combo.setCurrentIndex(panel.stage_combo.findData(sid))
    assert window.target_stage.currentData()==sid
    panel.wave_combo.setCurrentIndex(panel.wave_combo.findData(1))
    assert all(r['wave']==1 for r in panel.rows)
    panel.wave_combo.setCurrentIndex(0);panel.include_branches.setChecked(False)
    assert all(r['wave'] for r in panel.rows)
    panel.include_branches.setChecked(True)
    eid='enemy_1093_ccsbr';ei=next(i for i in range(1,panel.enemy_combo.count())
        if panel.enemy_combo.itemData(i)[0]==eid)
    panel.enemy_combo.setCurrentIndex(ei)
    assert panel.rows and all(r['action']['key']==eid for r in panel.rows)
    context={'difficulty':{'value':15},'zone':{'id':'zone_3'}}
    panel.set_context(context);high=panel.enemy_detail.toPlainText()
    assert '仅基础属性×关卡倍率的速度参考（格/秒）：0.4' in high
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
        assert panel.occurrence.value()==1
        panel.occurrence.setValue(panel.occurrence.maximum())
        assert panel.grid.selected_ordinal==panel.occurrence.maximum()
        assert panel.spawn_detail.isReadOnly() and panel.enemy_detail.isReadOnly()
        assert not panel.grid.grab().isNull()
        sizes.append({'window':[window.width(),window.height()],
            'grid':[panel.grid.width(),panel.grid.height()],'cell':cell})
        clicks+=1
    window.resize(1050,830);app.processEvents()
    screenshot=ROOT/'.cache/ammo-041/offline-preview.png'
    assert window.grab().save(str(screenshot))
    # A non-spawn cell clears only the visual selection; no state mutation.
    stage=panel.grid.stage
    cell=next({'row':r,'col':c} for r,line in enumerate(stage['map']) for c,_ in enumerate(line)
        if not any(row['route']['start']=={'row':r,'col':c} for row in panel.rows))
    QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=panel.grid.cell_center(cell).toPoint())
    assert panel.occurrence_bar.isHidden() and panel.grid.selected is None
    # Native SPAWN data may be absent in an existing wave (non-spawn actions).
    empty=next((s,w['index']) for s,d in battle_data()['stages'].items() for w in d['waves']
        if not any(a['action']['actionType']=='SPAWN' for f in w['fragments'] for a in f['actions']))
    panel.set_stage(empty[0]);panel.wave_combo.setCurrentIndex(panel.wave_combo.findData(empty[1]))
    assert not panel.rows and panel.occurrence_bar.isHidden() and not panel.occurrence_label.text()
    urgent=next(k for k,s in battle_data()['stages'].items()
        if s['name']==battle_data()['stages'][sid]['name'] and s['difficulty']=='FOUR_STAR')
    observation={'page':'node_detail','captured_at':time.time(),'nodes':[],
        'stage':{'name':battle_data()['stages'][urgent]['name'],'id':urgent,'visible_variant_id':urgent}}
    window.sample_received((np.zeros((180,320,3),dtype=np.uint8),observation));app.processEvents()
    assert panel.current_stage==urgent and window.target_stage.currentData()==urgent
    assert window.run.state==snapshot
    panel.set_stage('unrecognized-variant');assert panel.current_stage is None
    assert not panel.rows and panel.original.pixmap.isNull() and panel.occurrence_bar.isHidden()
    window.target_stage.setCurrentIndex(0)
    assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
    return {'battle_stages_checked':stages,'battle_enemy_panels_checked':enemy_panels,
        'battle_main_spawn_rows':main_rows,'battle_branch_rows':branches,
        'battle_main_nominal_instances':main_instances,'battle_conditional_nominal_instances':branch_instances,
        'battle_occurrence_selections':occurrence_selections,'battle_occurrence_reset_verified':True,
        'battle_occurrence_empty_filter_hidden':True,'battle_occurrence_non_spawn_cell_hidden':True,
        'battle_local_queue_anchor_visible':True,'battle_speed_reference_units_checked':True,
        'battle_resize_clicks':clicks,'battle_sizes':sizes,
        'battle_preview_seconds':time.perf_counter()-start,'battle_data_readonly':True,
        'battle_context_correction_verified':True,'battle_unchanged_context_render_reused':True,
        'battle_sample_received_synthetic_verified':True,'battle_variant_sync_bidirectional':True,
        'battle_empty_unknown_variant_cleared':True,'battle_screenshot':str(screenshot.relative_to(ROOT))}
