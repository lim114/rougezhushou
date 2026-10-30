"""Five-second game-client hover, asynchronous read-only pixels, no game input."""
from copy import deepcopy
from threading import Thread
import time
from PySide6.QtCore import QObject,QTimer,Signal,Qt,QPoint
from .player_game_binding import clamp_window

class HoverGate:
    def __init__(self,delay=5.,tolerance=6):self.delay=delay;self.tolerance=tolerance;self.reset()
    def reset(self):self.key=None;self.anchor=None;self.started=None;self.fired=False
    def update(self,snapshot,now):
        if not snapshot or not snapshot['active']or not snapshot['cursor_on_game']:self.reset();return False
        key=(tuple(snapshot['key']),tuple(snapshot['physical_client']));point=tuple(snapshot['cursor'])
        moved=self.anchor is None or max(abs(a-b)for a,b in zip(point,self.anchor))>self.tolerance
        if key!=self.key or moved:self.key=key;self.anchor=point;self.started=now;self.fired=False
        if not self.fired and now-self.started>=self.delay:self.fired=True;return True
        return False

class GameHover(QObject):
    received=Signal(object)
    def __init__(self,companion,owner,*,frame_provider=None,matcher=None):
        super().__init__(companion);self.companion=companion;self.owner=owner;self.gate=HoverGate();self.enabled=True;self.busy=False;self.serial=0;self.card=None;self.last_request=None;self.last_report=None;self.text_reader=None
        self.frame_provider=frame_provider or self.read_frame;self.matcher=matcher
        self.received.connect(self.accept);self.timer=QTimer(self);self.timer.setInterval(125);self.timer.timeout.connect(self.tick);self.timer.start()
    def set_enabled(self,value):self.enabled=bool(value);self.invalidate()
    def invalidate(self):
        self.serial+=1;self.gate.reset();self.last_request=None
        if self.card:self.card.dismiss()
    def read_frame(self,request):
        frame=self.owner.capture.buffer.latest()
        from .player_hover_match import client_image
        if client_image(frame,request)is not None:return frame
        # A short separate read session does not consume the automatic sampler's FIFO.
        from .capture import GameCapture
        session=GameCapture()
        try:session.connect(request['target']);return session.capture(timeout=2.)
        finally:session.close()
    def tick(self):
        if self.owner.closing or not self.enabled or getattr(self.companion,'hidden_windows',None)is not None:self.invalidate();return
        binding=self.companion.game_binding;snapshot=binding.snapshot
        if not snapshot or not snapshot['active']:
            if self.gate.key is not None or self.last_request is not None:self.invalidate()
            return
        key=(tuple(snapshot['key']),tuple(snapshot['physical_client']))
        if self.card and self.card.isVisible()and (self.card.underMouse()or self.card.pinned)and self.gate.key==key:return
        old=self.gate.key;anchor=self.gate.anchor
        ready=self.gate.update(snapshot,time.monotonic())
        if old is not None and (self.gate.key!=old or self.gate.anchor!=anchor):
            self.serial+=1;self.last_request=None
            if self.card:self.card.dismiss()
        if self.busy:
            if ready:self.gate.fired=False
            return
        if not ready:return
        context=deepcopy(self.owner.run.recognition_context());request={k:deepcopy(snapshot[k])for k in('key','target','physical_client','cursor')}
        request.update(serial=self.serial,run_id=context.get('run_id'),difficulty=(context.get('config')or{}).get('difficulty'));self.last_request=request;self.busy=True
        def work():
            result=None;reason='没有可唯一确认的图标';began=time.monotonic()
            try:
                from .player_hover_match import client_image,hover_item
                frame=self.frame_provider(request);image=client_image(frame,request)
                if image is None:reason='新画面范围或时间无法核对'
                if image is not None:
                    point=(request['cursor'][0]-request['physical_client'][0],request['cursor'][1]-request['physical_client'][1])
                    if self.matcher is not None:result=self.matcher(image,point,cancelled=lambda:self.serial!=request['serial']or self.owner.closing,difficulty=request['difficulty'])
                    else:
                        from .player_shop_hover import ShopNameReader
                        if self.text_reader is None:self.text_reader=ShopNameReader()
                        result=self.text_reader.identify(image,point)
                        if result is None and not self.text_reader.is_shop:result=hover_item(image,point,cancelled=lambda:self.serial!=request['serial']or self.owner.closing,difficulty=request['difficulty'])
                        elif result is None:reason='商店商品名称或对应位置未能核对，未使用图标猜测'
                    if result is not None:
                        # Refresh after retrieval: expensive matching must not publish old pixels.
                        fresh=self.frame_provider(request);current=client_image(fresh,request)
                        if current is None:result=None;reason='复核画面范围或时间无法核对'
                        elif self.matcher is None:
                            if result.get('source')=='shop_exact_name_and_current_grid':result=self.text_reader.verify(current,result)
                            else:
                                from .player_hover_match import verify_again
                                result=verify_again(current,point,result,difficulty=request['difficulty'],cancelled=lambda:self.serial!=request['serial']or self.owner.closing)
                            if result is None:reason='复核画面中的名称或图标无法一致确认'
                            elif result.get('source')=='shop_exact_name_and_current_grid':result['shop_snapshot']=self.text_reader.snapshot(current)
                        request['captured_at']=fresh.get('captured_at')if current is not None else None

            except Exception as error:result=None;reason='读取或匹配未完成：'+type(error).__name__
            self.received.emit({'request':request,'item':result,'reason':reason,'elapsed_seconds':time.monotonic()-began})
        Thread(target=work,daemon=True,name='rouge-game-hover').start()
    def accept(self,result):
        self.busy=False;request=result['request'];item=result['item'];self.last_report={'reason':result.get('reason'),'elapsed_seconds':result.get('elapsed_seconds'),'item_found':item is not None,'accepted':False}
        if self.owner.closing or not self.enabled or getattr(self.companion,'hidden_windows',None)is not None or item is None or item.get('confirmed')is not True or request['serial']!=self.serial:return
        if self.owner.run.recognition_context().get('run_id')!=request['run_id']:self.last_report['reason']='本局已改变';return
        if not isinstance(request.get('captured_at'),(int,float))or not 0<=time.time()-request['captured_at']<=2:self.last_report['reason']='复核画面已过期';return
        target=self.companion.game_binding.target()
        if target is None or (target.get('hwnd'),target.get('pid'))!=tuple(request['key']):return
        snapshot=self.companion.game_binding.api.read(request['target'])
        if not snapshot or not snapshot['active']or not snapshot['cursor_on_game']:return
        if tuple(snapshot['key'])!=tuple(request['key'])or tuple(snapshot['physical_client'])!=tuple(request['physical_client']):return
        if max(abs(a-b)for a,b in zip(snapshot['cursor'],request['cursor']))>self.gate.tolerance:return
        if item.get('shop_snapshot'):
            from .player_shop_memory import remember
            remember(self.owner.run,item['shop_snapshot'],request['run_id'],request['captured_at'])
        from .expansion_reference import packet
        public=packet();record=public['current']['details']['items'].get(item['id'])if public else None
        if not record:return
        from .player_item_hover import ItemHoverCard
        panel=self.owner.inventory_panel;panel.reload_sources()
        if self.card is None:
            self.card=ItemHoverCard(self.companion)
            self.card.poolRequested.connect(lambda version,identity:self.companion.open_owner_dialog(lambda:self.owner.open_public_pool_reference(version,identity),'public_archive'))
        row={'id':item['id'],'name':record['name'],'icon':record.get('iconId')}
        if not self.card.install(row,panel.version.currentData(),panel.source_index,panel.source_signature):return
        self.card.notice.setText('游戏画面悬停资料；不表示本局已持有。\n'+self.card.notice.text())
        self.card.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating);self.card.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint,True)
        rect=snapshot['logical_client'];physical=snapshot['physical_client'];point=QPoint(round(rect.left()+(snapshot['cursor'][0]-physical[0])*rect.width()/physical[2]),round(rect.top()+(snapshot['cursor'][1]-physical[1])*rect.height()/physical[3]))
        area=rect.intersected(snapshot['screen'].availableGeometry())
        if area.width()<self.card.minimumSizeHint().width()or area.height()<self.card.minimumSizeHint().height():
            self.last_report['reason']='游戏可见范围太小，未弹出超界卡片';return
        self.card.resize(min(470,area.width()),min(620,area.height()))
        self.card.move(point+QPoint(14,14));clamp_window(self.card,area);self.card.show();self.last_report.update(accepted=True,reason='已显示鼠标下藏品资料')
    def close(self):self.timer.stop();self.enabled=False;self.invalidate()
