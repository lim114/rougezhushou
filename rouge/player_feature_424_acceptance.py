def check(window,gui,require):
 import win32gui,win32con
 from PySide6.QtCore import Qt,QRect
 from .player_game_map import payload
 from tests.test_player_feature_424 import fixture
 window.show_compact();c=window.compact_window;overlay=c.game_overlay;overlay.timer.stop();a,b,s=fixture();s['logical_client']=QRect(100,200,800,450);data=payload(a,b,s,'one',100);require(data is not None,'isolated_pixel_geometry_payload_qualified')
 surface=overlay.surface;surface.data=data;surface.kind='诡意行商';surface.setGeometry(data['rect']);surface.show();gui.processEvents()
 style=win32gui.GetWindowLong(int(surface.winId()),win32con.GWL_EXSTYLE)
 require(bool(style&win32con.WS_EX_TRANSPARENT),'native_overlay_mouse_input_transparent')
 require(bool(style&win32con.WS_EX_NOACTIVATE),'native_overlay_cannot_activate_game_or_itself')
 require(surface.isVisible()and surface.geometry()==data['rect'],'actual_transparent_annotation_surface_uses_client_rect')
 require(len(data['points'])==3,'only_qualified_frame_positions_drawn')
 overlay.set_enabled(False);gui.processEvents();require(not surface.isVisible(),'disabled_overlay_hides_immediately')
 surface.data=data;surface.kind='诡意行商';surface.setGeometry(data['rect']);surface.show();gui.processEvents();window.player_validation_target=surface
