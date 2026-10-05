"""Exercise the fixed-image panel in an isolated Qt window, without sampling."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import copy,hashlib,json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_relic_ui_025 import OfflineWindow,module,QApplication,Qt
from verify_battle_widgets_046 import verify_battle
from PySide6.QtGui import QFontDatabase,QFont,QImage,QColor
from PySide6.QtCore import QPointF
from PySide6.QtTest import QTest
from rouge.battle_preview import battle_data,DATA
from rouge.map_projection import projection_data
from rouge.battle_view import MapOriginal


def verify_projection(window,app,folder):
    panel=window.battle_preview;original=panel.original
    window.centralWidget().setCurrentWidget(panel)
    before=copy.deepcopy(window.run.state);clicks=selection_checks=0
    for sid in projection_data()['stages']:
        panel.set_stage(sid);assert original.projection is not None
        assert '地面参考' in panel.map_caption.text()
        expected={(r['route']['start']['row'],r['route']['start']['col']) for r in panel.rows if r['route']['start']}
        assert set(original.marker_cells())==expected
        for size in ((880,700),(1050,830),(1450,950)):
            window.resize(*size);app.processEvents()
            first=next(r for r in panel.rows if r['route']['start']);cell=first['route']['start']
            point=original.cell_center(cell);assert original.cell_at(point)==cell
            QTest.mouseClick(original,Qt.MouseButton.LeftButton,pos=point.toPoint());app.processEvents()
            assert panel.grid.selected==original.selected and original.selected['route']['start']==cell
            assert '本格共有' in panel.spawn_detail.toPlainText()
            panel.occurrence.setValue(panel.occurrence.maximum())
            assert panel.grid.selected_ordinal==original.selected_ordinal==panel.occurrence.value()
            assert not original.grab().isNull();clicks+=1
        for i,row in enumerate(panel.rows):
            panel.spawn_list.setCurrentRow(i)
            assert original.selected==panel.grid.selected==row
            panel.occurrence.setValue(panel.occurrence.maximum())
            assert original.selected_ordinal==panel.grid.selected_ordinal
            selection_checks+=1
        # Clicking a non-spawn tile clears only presentation state on both maps.
        stage=original.stage
        cell=next({'row':r,'col':c} for r,line in enumerate(stage['map']) for c,_ in enumerate(line)
            if (r,c) not in expected and original.image_rect().contains(original.cell_center({'row':r,'col':c})))
        QTest.mouseClick(original,Qt.MouseButton.LeftButton,pos=original.cell_center(cell).toPoint())
        assert original.selected is None and panel.grid.selected is None and panel.occurrence_bar.isHidden()
        assert window.run.state==before
    panel.set_stage('ro6_n_1_2');original=panel.original
    standalone=MapOriginal();s=battle_data()['stages']['ro6_n_1_2']
    standalone.set_file(DATA/s['image']['file']);standalone.set_reference(s,[])
    for size in ((220,400),(900,160),(513,287),(1024,572)):
        standalone.resize(*size)
        point=standalone.cell_center({'row':3,'col':0});assert standalone.cell_at(point)=={'row':3,'col':0}
        rect=standalone.image_rect()
        outside=QPointF(rect.left()-1,rect.center().y()) if rect.left()>0 else QPointF(rect.center().x(),rect.top()-1)
        assert standalone.cell_at(outside) is None
    standalone.resize(800,450)
    # Synthetic broken/continuous references test the rendering guard only.
    a={'row':3,'col':1};b={'row':3,'col':7}
    first=copy.deepcopy(next(r for r in panel.rows if r['route']['start']))
    first['route']={'start':None,'points':[a,b],'continuous_reference':False}
    baseline=standalone.grab().toImage();standalone.selected=first
    broken=standalone.grab().toImage();first['route']['continuous_reference']=True
    continuous=standalone.grab().toImage()
    pa,pb=standalone.cell_center(a),standalone.cell_center(b)
    mx,my=round((pa.x()+pb.x())/2),round((pa.y()+pb.y())/2)
    def difference(image):
        return sum(image.pixel(x,y)!=baseline.pixel(x,y) for x in range(mx-10,mx+11) for y in range(my-3,my+4))
    assert difference(broken)==0 and difference(continuous)>0
    # Byte identity uses the exact decoded payload; a same-size replacement
    # bitmap is not accepted because its stage label and dimensions match.
    replacement=folder/'same-size-different-image.png'
    image=QImage(512,286,QImage.Format.Format_RGB32);image.fill(QColor('#435562'))
    assert image.save(str(replacement))
    standalone.set_file(str(replacement));standalone.set_reference(s,[])
    assert standalone.projection is None and standalone.cell_center(a) is None
    standalone.set_file(folder/'missing.png');standalone.set_reference(s,[])
    assert standalone.pixmap.isNull() and standalone.projection is None
    for sid in ('ro6_n_2_1','ro6_e_2_1','ro6_n_2_2'):
        panel.set_stage(sid)
        assert not original.pixmap.isNull() and original.projection is None
        assert not original.marker_cells() and original.cell_at(QPointF(100,100)) is None
        assert '尚未校准' in panel.map_caption.text()
    panel.set_stage('ro6_e_1_2');window.resize(1200,880);app.processEvents()
    panel.spawn_list.setCurrentRow(1);panel.occurrence.setValue(panel.occurrence.maximum())
    screenshot=ROOT/'.cache/branch-046/fixed-map-preview.png'
    assert window.grab().save(str(screenshot))
    standalone.set_file(DATA/s['image']['file']);standalone.set_reference(s,panel.rows)
    standalone.selected=panel.grid.selected;standalone.selected_ordinal=panel.grid.selected_ordinal
    standalone.resize(1024,572)
    detail=ROOT/'.cache/branch-046/fixed-map-detail.png';assert standalone.grab().save(str(detail))
    panel.set_stage(None)
    assert original.pixmap.isNull() and original.projection is None and original.selected is None
    assert not original.rows and not original.marker_cells()
    assert window.run.state==before
    assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
    return {'calibrated_stage_clicks':clicks,'projected_row_selection_checks':selection_checks,
        'original_and_grid_selection_synced':True,'occurrence_synced_on_original':True,
        'non_spawn_selection_clears_both_maps':True,'letterbox_sizes_checked':4,
        'letterbox_clicks_rejected':True,'same_size_wrong_bitmap_rejected':True,
        'missing_bitmap_rejected':True,'uncalibrated_map_has_no_markers_or_click_mapping':True,
        'broken_route_continuous_line_not_drawn':True,'continuous_checkpoint_reference_drawn':True,
        'unknown_stage_cleared':True,'run_state_unchanged':True,
        'fixed_map_screenshot':str(screenshot.relative_to(ROOT)),
        'fixed_map_detail_screenshot':str(detail.relative_to(ROOT))}


def main():
    started=time.perf_counter()
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);module.RUN_STATE=p/'run.json';module.OPERATOR_STATE=p/'operators.json';module.SETTINGS=p/'settings.json'
        backend=module.DesktopBackend;module.DesktopBackend=lambda _path,callback:backend(p/'chat',callback)
        app=QApplication([])
        fid=QFontDatabase.addApplicationFont(str(Path(os.environ['WINDIR'])/'Fonts/msyh.ttc'))
        assert fid>=0;app.setFont(QFont(QFontDatabase.applicationFontFamilies(fid)[0],9))
        window=OfflineWindow()
        try:
            assert window.windowTitle()=='黑流树海助手 0.46 · 识别与计算测试版'
            receipt=verify_battle(window,app)
            receipt.update(verify_projection(window,app,p))
        finally:window.close();app.processEvents()
    names=['rouge/battle_view.py','rouge/map_projection.py','rouge/data/battle-map-projections.json',
        'rouge/app.py','scripts/verify_map_projection_ui_046.py','scripts/verify_battle_widgets_046.py']
    receipt.update({'version':'0.46.0','passed':True,'private_data_isolated':True,
        'live_battle_capture_performed':False,'game_actions':0,'chat_requests':0,
        'seconds':time.perf_counter()-started,'source_hashes':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}})
    for key in ('battle_screenshot','enemy_skill_screenshot','fixed_map_screenshot','fixed_map_detail_screenshot'):
        receipt[key+'_sha256']=hashlib.sha256((ROOT/receipt[key]).read_bytes()).hexdigest()
    (ROOT/'UI_0.46_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':main()
