"""Isolated route controls, actual Qt painting, refresh and history protection."""
import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import copy,hashlib,json,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import cv2,numpy as np
from PySide6.QtCore import QPoint,Qt
from PySide6.QtGui import QFontDatabase,QFont,QColor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
import rouge.app as module
from rouge.recognition import ScreenReader
from rouge.map_view import MapView
from verify_relic_ui_025 import OfflineWindow


def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    folder=ROOT/'.cache/routes-049';folder.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        isolated=Path(directory)
        module.RUN_STATE=isolated/'run.json';module.OPERATOR_STATE=isolated/'operators.json'
        module.SETTINGS=isolated/'settings.json';backend=module.DesktopBackend
        module.DesktopBackend=lambda _path,callback:backend(isolated/'chat',callback)
        app=QApplication([]);font_file=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/msyh.ttc'
        if font_file.exists():
            font=QFontDatabase.addApplicationFont(str(font_file));families=QFontDatabase.applicationFontFamilies(font)
            if families:app.setFont(QFont(families[0],9))
        window=OfflineWindow();assert not window.auto.isChecked() and window.capture.target is None
        assert window.windowTitle()=='黑流树海助手 0.49 · 识别与计算测试版'
        tab=window.centralWidget();tab.setCurrentIndex(next(i for i in range(tab.count()) if tab.tabText(i)=='地图预测'))
        window.resize(1120,900);window.show();app.processEvents()
        image=cv2.imdecode(np.fromfile(ROOT/'samples/native-client/exploration-map.png',dtype=np.uint8),1)
        observed=ScreenReader().read(image);observed['captured_at']=time.time()
        window.sample_received((image,observed));app.processEvents()
        assert not window.map_view.historical
        view=window.map_view;clicks=0
        for width,height in ((1120,900),(820,1020),(1460,860)):
            window.resize(width,height);app.processEvents()
            # Recorded source coordinate, independent of the renderer's point helper.
            scale=min(view.width()/1596,view.height()/1198)
            point=QPoint(round((view.width()-1596*scale)/2+.68*1596*scale),
                         round((view.height()-1198*scale)/2+.463*1198*scale))
            QTest.mouseClick(view,Qt.MouseButton.LeftButton,pos=point);app.processEvents();clicks+=1
            assert view.selected=='1,3'
            assert '中排 · 第4列' in window.map_detail.toPlainText()
            assert '模板最短连线' in window.map_route.text()
            assert not view.route()['entry_confirmed']
        screenshot=folder/'current-route.png';assert window.grab().save(str(screenshot))
        selected=view.selected;cursor=window.map_detail.textCursor();cursor.setPosition(7);window.map_detail.setTextCursor(cursor)
        observed=copy.deepcopy(observed);observed['captured_at']=time.time()
        window.sample_received((image,observed));app.processEvents()
        assert view.selected==selected and window.map_nodes.currentData()==selected
        assert window.map_detail.textCursor().position()==7
        snapshot=copy.deepcopy(window.run.state)
        window.map_technical.setChecked(True);window.map_technical.setChecked(False)
        assert view.selected==selected and window.run.state==snapshot
        missing=copy.deepcopy(observed);missing['captured_at']=time.time()
        missing['map']['current_node']=None;missing['run']['map']=copy.deepcopy(missing['map'])
        window.sample_received((image,missing));app.processEvents()
        assert view.selected==selected and view.route()['display_path']==[]
        assert '本帧位置未确认' in window.map_route.text()
        assert view.graph['last_confirmed_current_node']=='1,0'
        hidden=copy.deepcopy(missing);hidden['captured_at']=time.time()
        hidden['map']={'status':'insufficient','zone_id':'zone_1','reason':'受控遮挡'}
        hidden['run']['map']=copy.deepcopy(hidden['map'])
        window.sample_received((np.zeros_like(image),hidden));app.processEvents()
        assert view.selected==selected and view.historical and not view.route()['display_path']
        assert '历史参考' in window.map_route.text()
        # Independent schematic graph isolates paint colors from source artwork.
        from tests.test_exploration_routes_049 import graph
        synthetic=MapView();g=graph();synthetic.set_map(g);synthetic.select_node('e');synthetic.resize(600,360)
        def has_color(color,x,y):
            bitmap=synthetic.grab().toImage()
            return any(bitmap.pixelColor(px,py).name()==color for px in range(x-5,x+6) for py in range(y-5,y+6))
        # The a-c segment midpoint has grid positions (1/5,2/4) and (2/5,3/4).
        assert has_color('#6ee7df',180,225)
        g['nodes'][2]['visible']=False;synthetic.set_map(g)
        # a-b midpoint: (1/5,2/4) and (2/5,1/4), topology-only dashed amber.
        assert has_color('#ffcb75',180,135)
        synthetic.set_map(g,historical=True)
        assert not has_color('#ffcb75',180,135)
        before=copy.deepcopy(window.run.state);window.close();app.processEvents()
        window=OfflineWindow();window.centralWidget().setCurrentIndex(next(i for i in range(tab.count()) if tab.tabText(i)=='地图预测'))
        window.show();app.processEvents();window.map_view.select_node(selected)
        # RunState intentionally changes only its notice to explain recovery.
        assert {k:v for k,v in window.run.state.items() if k!='notice'}=={k:v for k,v in before.items() if k!='notice'}
        assert window.map_view.historical and not window.map_view.route()['display_path']
        assert not window.auto.isChecked() and window.capture.target is None and not window.desktop.process
        window.close();app.processEvents()
    names=['rouge/exploration_routes.py','rouge/map_reporting.py','rouge/map_view.py','rouge/app.py',
           'scripts/verify_exploration_routes_049.py','tests/test_exploration_routes_049.py']
    result={'version':'0.49.0','passed':True,'spatial_clicks':clicks,'window_sizes':3,
        'fresh_route_reference':True,'selection_and_cursor_preserved':True,'technical_switch_preserved':True,
        'missing_marker_no_stale_route':True,'historical_and_restart_no_current_route':True,
        'actual_corridor_and_topology_paint_verified':True,'public_sample': 'samples/native-client/exploration-map.png',
        'synthetic_paint_graph':True,'private_data_isolated':True,'game_actions':0,'chat_requests':0,
        'screenshots':{str(screenshot.relative_to(ROOT)):digest(str(screenshot.relative_to(ROOT)))},
        'source_sha256':{n:digest(n) for n in names}}
    (ROOT/'EXPLORATION_UI_0.49_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','screenshots')}))


if __name__=='__main__':main()
