from pathlib import Path
import sys,json,time,subprocess,tempfile,ctypes,os
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
assert sys.platform=='win32','Actual Windows is required.'
os.environ['QT_QPA_PLATFORM']='windows'
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import Qt
import win32gui,win32con,win32process,psutil
from rouge.player_game_binding import BindingApi,physical_pixels
from rouge.player_game_map import OverlaySurface
from player_ui_verification import source_hashes
out=R/'verification/sections/425-overlay-input-probe-attempt2';assert not out.exists();out.mkdir();(out/'parent-source.py').write_bytes(Path(__file__).read_bytes());(out/'child-source.py').write_bytes((R/'.cache/overlay425_owned_fixture.py').read_bytes());source=source_hashes();app=QApplication([]);assert app.platformName()=='windows';owner=QWidget();surface=None;child=None;owned_target=None
with tempfile.TemporaryDirectory(prefix='rouge-overlay-input-')as folder:
 path=Path(folder)/'owned.json'
 with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',str(R/'.cache/overlay425_owned_fixture.py'),str(path)],cwd=R,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+10
   while not path.exists()and time.monotonic()<deadline:
    assert child.poll()is None;time.sleep(.05)
   target=json.loads(path.read_bytes());assert child.poll() is None
   actual=psutil.Process(target['pid']);chain=[actual.pid]
   while chain[-1]!=child.pid:
    actual=actual.parent();assert actual is not None;chain.append(actual.pid);assert len(chain)<=4
   runtime=psutil.Process(target['pid']);assert Path(runtime.cwd()).resolve()==R
   assert any(str(arg).replace('\\','/').endswith('/.cache/overlay425_owned_fixture.py')for arg in runtime.cmdline())
   assert win32process.GetWindowThreadProcessId(target['hwnd'])[1]==target['pid'];owned_target=target
   s=BindingApi().read(target);assert s and s['active'];rect=s['logical_client'];cx,cy=rect.width()/2,rect.height()/2
   surface=OverlaySurface(owner);surface.data={'graph':{'zone_id':'zone_1','nodes':[{'id':'probe','observed_type':'诡意行商','distance':2}]},'points':[('probe',cx,cy)]};surface.kind='诡意行商';surface.setGeometry(rect);foreground_before_show=win32gui.GetForegroundWindow();surface.show();app.processEvents();time.sleep(.1);app.processEvents();assert win32gui.GetForegroundWindow()==foreground_before_show,'Own annotation show unexpectedly changed foreground.'
   style=win32gui.GetWindowLong(int(surface.winId()),win32con.GWL_EXSTYLE);assert all(style&flag for flag in(win32con.WS_EX_LAYERED,win32con.WS_EX_TRANSPARENT,win32con.WS_EX_NOACTIVATE))
   query_points=((cx+30,cy),(cx,cy+45));pixels=surface.grab();rendered=pixels.toImage();ratio=pixels.devicePixelRatio()
   alphas=[rendered.pixelColor(round(lx*ratio),round(ly*ratio)).alpha()for lx,ly in query_points];assert all(a>0 for a in alphas),'Probe points must lie on actual painted pixels, not empty transparent areas.'
   # Verify the painted overlay is really above the own underlay. Otherwise a
   # successful hit-test could merely mean the overlay was behind the target.
   z_order=[];seen=set();cursor=int(surface.winId())
   for _ in range(2048):
    assert cursor not in seen,'Z-order traversal cycle; no pass may be inferred.'
    seen.add(cursor);z_order.append(cursor)
    if cursor==target['hwnd']:break
    cursor=win32gui.GetWindow(cursor,win32con.GW_HWNDNEXT)
    if not cursor:break
   assert z_order[-1]==target['hwnd'],'Own underlay must actually be below the overlay in native Z order.'
   points=[];x,y,w,h=s['physical_client']
   with physical_pixels():
    for lx,ly in query_points:
     physical=(round(x+lx*w/rect.width()),round(y+ly*h/rect.height()));hit=win32gui.WindowFromPoint(physical);root=win32gui.GetAncestor(hit,2);points.append(root==target['hwnd'])
   assert all(points),'Actual WindowFromPoint did not bypass the own layered overlay to the separate own fixture.'
   result={'section':425,'passed':True,'scope':'actual cross-process own fixture and actual project OverlaySurface; not game integration','qualified_point_count':len(points),'all_native_point_hits_reached_underlying_owned_process':all(points),'native_layered_transparent_noactivate_styles':True,'own_underlay_verified_below_overlay_in_native_z_order':True,'z_order_handles_traversed':len(z_order),'foreground_unchanged_by_own_annotation_show':True,'mouse_moved':False,'keyboard_or_mouse_input_sent':False,'game_operated':False,'chat_sent':False,'private_state_opened':False,'source_sha256_before':source,'source_sha256_after':source_hashes()};assert source==result['source_sha256_after']
  finally:
   if surface:surface.close()
   if child and child.poll()is None and owned_target is not None:
    if win32gui.IsWindow(owned_target['hwnd'])and win32process.GetWindowThreadProcessId(owned_target['hwnd'])[1]==owned_target['pid']:win32gui.PostMessage(owned_target['hwnd'],win32con.WM_CLOSE,0,0)
   code=child.wait(timeout=15);assert code==0
   from qt_verification_cleanup import shutdown_verification_qt
   cleanup=shutdown_verification_qt()
  result['actual_owned_child_exit']=code;result['actual_retained_child_pid']=child.pid;result['actual_native_fixture_pid']=target['pid'];result['actual_parent_process_id']=os.getpid();result['verified_owned_runtime_to_retained_launcher_chain']=chain;result['launcher_and_runtime_pid_equality_assumed']=False;result['all_query_points_verified_on_painted_overlay_pixels']=all(a>0 for a in alphas);result['qt_cleanup']=cleanup;(out/'receipt.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
assert (out/'parent-source.py').read_bytes()==Path(__file__).read_bytes()and(out/'child-source.py').read_bytes()==(R/'.cache/overlay425_owned_fixture.py').read_bytes()
print(json.dumps({'passed':True,'underlying_own_process_hit_count':len(points),'no_mouse_moves_or_game_input':True}))
