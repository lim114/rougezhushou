def check(window,gui,require):
 import os,time,numpy as np
 from PySide6.QtWidgets import QWidget
 from PySide6.QtTest import QTest
 from .player_game_binding import BindingApi
 from .player_game_hover import GameHover
 window.show_compact();c=window.compact_window;c.game_binding.timer.stop();c.game_hover.close()
 fixture=QWidget();fixture.setWindowTitle('自有悬停流程验证，不是游戏');fixture.resize(800,500);fixture.show();gui.processEvents();target={'hwnd':int(fixture.winId()),'pid':os.getpid()}
 api=BindingApi();s=api.read(target);require(s is not None,'owned_hover_client_geometry_available')
 x,y,w,h=s['physical_client'];s.update(cursor=(x+245,y+170),cursor_on_game=True);old_target=window.capture.target;window.capture.target=target
 original_api=c.game_binding.api;c.game_binding.api=type('OwnedHoverApi',(),{'read':lambda _,target:s})()
 c.game_binding.snapshot=s;calls=[]
 def frame(request):
  calls.append(time.monotonic());return {'image':np.full((h,w,3),24,np.uint8),'client_rect':[0,0,w,h],'captured_at':time.time(),'target':target}
 from .player_shop_hover import ShopNameReader
 from tests.test_player_feature_417 import shop_fixture
 probe=GameHover(c,window,frame_provider=frame)
 probe.text_reader=ShopNameReader(lambda *args,**kw:([['第一法则',.99]]if kw.get('use_det')is False else shop_fixture(),None))
 from unittest.mock import patch
 stock_guard=patch('rouge.player_shop_memory.remember',return_value=True);stock_guard.start()
 try:
  probe.tick();QTest.qWait(4800);gui.processEvents();require(not calls,'no_capture_before_five_seconds')
  deadline=time.monotonic()+4
  while time.monotonic()<deadline and (probe.card is None or not probe.card.isVisible()):gui.processEvents();time.sleep(.02)
  require(len(calls)==2,'fresh_frame_rechecked_after_retrieval: '+repr({'reads':len(calls),'report':probe.last_report,'busy':probe.busy}))
  require(probe.card is not None and probe.card.isVisible(),'native_five_second_flow_shows_nonactivating_card')
  require('第一法则'in probe.card.title.text(),'exact_item_reference_loaded')
  require('不表示本局已持有'in probe.card.notice.text(),'shop_hover_does_not_claim_possession')
  from unittest.mock import patch
  s['cursor_on_game']=False
  with patch.object(probe.card,'underMouse',return_value=False):probe.tick()
  gui.processEvents();require(not probe.card.isVisible(),'cursor_leaving_game_dismisses_hover')
  require(probe.last_request is None,'old_request_invalidated_after_leave')
  c.binding_status.setText('隔离验收：5秒后触发、二次新鲜画面核对与离开清理通过；文字识别由隔离数据注入，不冒充游戏识别。')
  c.game_hover_enabled.setChecked(False);c.present(c.settings_popup);gui.processEvents();window.player_validation_target=c.settings_popup
 finally:stock_guard.stop();probe.close();fixture.close();window.capture.target=old_target;c.game_binding.api=original_api;c.game_binding.snapshot=None;c.game_binding.previous=None;c.game_binding.ever_bound=False;c.game_binding.suspended=[]
