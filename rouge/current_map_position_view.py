"""Current static map comparison; image clicks never infer unmeasured cells."""
from PySide6.QtCore import Qt,QPointF,QRectF,Signal
from PySide6.QtGui import QPainter,QPen,QColor,QPixmap,QPainterPath
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPushButton,QSplitter,QTabWidget,QPlainTextEdit,QCheckBox,QMenu,QToolTip
from . import current_map_position as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text
from .reference_copy import mechanism_copy

class CurrentTileGrid(QWidget):
    cellSelected=Signal(int,int)
    def __init__(self,parent=None):
        super().__init__(parent);self.result=None;self.selected=None;self.highlight_cells=set();self.tile_infos=[];self.setMinimumSize(300,180);self.setAccessibleName('当前固定地图的方格图')
    def set_result(self,result,selected=None):
        if result is not self.result:
            from .current_terrain import terrain_info
            self.tile_infos=[terrain_info(tile)for tile in result['tiles']]if result else[]
        self.result=result;self.selected=selected;self.update()
    def grid_rect(self):
        if self.result is None:return QRectF()
        available=QRectF(self.contentsRect()).adjusted(27,22,-5,-5);side=min(available.width()/self.result['cols'],available.height()/self.result['rows']);return QRectF(available.center().x()-side*self.result['cols']/2,available.center().y()-side*self.result['rows']/2,side*self.result['cols'],side*self.result['rows'])
    def center(self,row,col):
        rect=self.grid_rect()
        if self.result is None or not 0<=row<self.result['rows']or not 0<=col<self.result['cols']:return None
        side=rect.width()/self.result['cols'];return QPointF(rect.left()+(col+.5)*side,rect.top()+(row+.5)*side)
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),self.palette().window().color())
        if self.result is None:return
        rect=self.grid_rect();side=rect.width()/self.result['cols']
        for row in range(self.result['rows']):
            for col in range(self.result['cols']):
                info=self.tile_infos[self.result['map'][row][col]];cell=QRectF(rect.left()+col*side,rect.top()+row*side,side,side);color=QColor(info['color']);p.fillRect(cell,color);p.setPen(QPen(QColor('#87919c'),1));p.drawRect(cell);p.setPen(QColor('#f2f4f7'if color.lightness()<120 else'#141a21'));p.drawText(cell,Qt.AlignmentFlag.AlignCenter,info['short_label'])
                if (row,col)in self.highlight_cells:p.setPen(QPen(QColor('#ffd665'),2));p.drawRect(cell.adjusted(1,1,-1,-1))
                if self.selected==(row,col):p.setPen(QPen(QColor('#f2b8f1'),3));p.drawRect(cell.adjusted(2,2,-2,-2))
        p.setPen(QColor('#f2f4f7'))
        for col in range(self.result['cols']):p.drawText(QRectF(rect.left()+col*side,rect.top()-22,side,20),Qt.AlignmentFlag.AlignCenter,str(col+1))
        for row in range(self.result['rows']):p.drawText(QRectF(rect.left()-27,rect.top()+row*side,24,side),Qt.AlignmentFlag.AlignCenter,str(row+1))
    def mousePressEvent(self,event):
        if event.button()!=Qt.MouseButton.LeftButton or self.result is None:return
        rect=self.grid_rect();point=event.position()
        if rect.left()<=point.x()<rect.right()and rect.top()<=point.y()<rect.bottom():
            side=rect.width()/self.result['cols'];self.cellSelected.emit(int((point.y()-rect.top())/side),int((point.x()-rect.left())/side))

class CurrentOriginalCenters(QWidget):
    markerSelected=Signal(object)
    def __init__(self,parent=None):
        super().__init__(parent);self.pixmap=QPixmap();self.image_raw=None;self.point=None;self.markers=();self.markers_visible=True;self.setMinimumSize(300,180);self.setMouseTracking(True)
    def set_image(self,raw,point=None,*,markers=()):
        if raw!=self.image_raw or markers!=self.markers:
            for menu in self.findChildren(QMenu):menu.close()
            QToolTip.hideText();self.unsetCursor()
        if raw != self.image_raw:
            self.image_raw=bytes(raw) if raw else None;self.pixmap=QPixmap()
            if raw:self.pixmap.loadFromData(raw,'PNG')
        ok=not self.pixmap.isNull();self.point=point if ok else None;self.markers=markers if ok else();self.update();return ok
    def set_markers_visible(self,visible):
        self.markers_visible=visible
        if not visible:
            for menu in self.findChildren(QMenu):menu.close()
            QToolTip.hideText();self.unsetCursor()
        self.update()
    def image_rect(self):
        if self.pixmap.isNull():return QRectF()
        ratio=min(self.width()/self.pixmap.width(),self.height()/self.pixmap.height());w,h=self.pixmap.width()*ratio,self.pixmap.height()*ratio;return QRectF((self.width()-w)/2,(self.height()-h)/2,w,h)
    def point_center(self):
        if self.point is None or self.pixmap.isNull():return None
        return self._screen_point(self.point)
    def _screen_point(self,point):
        rect=self.image_rect();x,y=point['pixel'];return QPointF(rect.left()+x*rect.width()/self.pixmap.width(),rect.top()+y*rect.height()/self.pixmap.height())
    def _markers_at(self,position):
        if not self.markers_visible:return[]
        found=[]
        for marker in self.markers:
            shape=QPainterPath();shape.addEllipse(self._screen_point(marker['point']),9,9)
            if shape.contains(position):found.append(marker)
        return found
    def mousePressEvent(self,event):
        if event.button()!=Qt.MouseButton.LeftButton:return super().mousePressEvent(event)
        found=self._markers_at(event.position())
        if len(found)==1:self.markerSelected.emit(found[0]['key'])
        elif found:
            menu=QMenu(self);menu.aboutToHide.connect(menu.deleteLater)
            for marker in found:
                action=menu.addAction(marker['label'])
                action.triggered.connect(lambda _checked=False,key=marker['key']:self.markerSelected.emit(key))
            menu.popup(event.globalPosition().toPoint())
        else:super().mousePressEvent(event)
    def mouseMoveEvent(self,event):
        found=self._markers_at(event.position())
        if found:
            self.setCursor(Qt.CursorShape.PointingHandCursor);QToolTip.showText(event.globalPosition().toPoint(),'\n'.join(m['label']for m in found),self)
        else:self.unsetCursor();QToolTip.hideText()
    def leaveEvent(self,event):
        self.unsetCursor();QToolTip.hideText();super().leaveEvent(event)
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),self.palette().window().color())
        if self.pixmap.isNull():return
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform);p.drawPixmap(self.image_rect(),self.pixmap,QRectF(self.pixmap.rect()));center=self.point_center()
        if self.markers_visible:
            p.setRenderHint(QPainter.RenderHint.Antialiasing);font=p.font();font.setPointSizeF(8);p.setFont(font)
            for marker in self.markers:
                pos=self._screen_point(marker['point']);p.setPen(QPen(QColor('#e9cf80'),1));p.setBrush(QColor('#262528'));p.drawEllipse(pos,8,8);p.setPen(QColor('#ffffff'));p.drawText(QRectF(pos.x()-8,pos.y()-8,16,16),Qt.AlignmentFlag.AlignCenter,str(marker['number']))
        if center is not None:
            p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setPen(QPen(QColor('#ffb4ee'),3));p.setBrush(Qt.BrushStyle.NoBrush);p.drawEllipse(center,8,8);p.drawLine(center+QPointF(-13,0),center+QPointF(13,0));p.drawLine(center+QPointF(0,-13),center+QPointF(0,13))

class CurrentMapPositionPanel(QWidget):
    def __init__(self,stage_id,parent=None,*,defer_load=False,reference_loader=None,initial_reference=...):
        super().__init__(parent);self.stage_id=stage_id;self.result=None;self.selected=None;self.image_raw=None
        self.reference_loader=reference_loader
        layout=QVBoxLayout(self);self.notice=QLabel('点选原图编号或格子，查看对应位置。');self.notice.setWordWrap(True);layout.addWidget(self.notice)
        bar=QHBoxLayout();self.combo=QComboBox();self.combo.setAccessibleName('已核对的格子中心');self.refresh_button=QPushButton('刷新位置');self.marker_toggle=QCheckBox('位置标记');self.marker_toggle.setChecked(True);bar.addWidget(self.combo,1);bar.addWidget(self.marker_toggle);bar.addWidget(self.refresh_button);layout.addLayout(bar)
        terrain_bar=QHBoxLayout();self.terrain_kind=QComboBox();self.terrain_kind.setAccessibleName('本图地形类型');self.terrain_cells=QComboBox();self.terrain_cells.setAccessibleName('按地形定位格子');terrain_bar.addWidget(QLabel('查找地形'));terrain_bar.addWidget(self.terrain_kind);terrain_bar.addWidget(self.terrain_cells,1);layout.addLayout(terrain_bar)
        split=self.map_split=QSplitter();self._map_sizes={};self.grid=CurrentTileGrid();self.original=CurrentOriginalCenters();split.addWidget(self.grid);split.addWidget(self.original);split.setSizes([500,650]);layout.addWidget(split,2)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.player.setReadOnly(True);self.technical=QPlainTextEdit();self.technical.setReadOnly(True);self.tabs.addTab(self.player,'格子与位置说明');self.tabs.addTab(self.technical,'地形与核对依据');layout.addWidget(self.tabs,1)
        self.grid.cellSelected.connect(self.select_cell);self.combo.currentIndexChanged.connect(lambda _:self._combo_selected(self.combo));self.refresh_button.clicked.connect(self.refresh_reference)
        if not defer_load:self.refresh_reference(prepared_reference=initial_reference)
        self.original.markerSelected.connect(lambda key:self.combo.setCurrentIndex(self.combo.findData(key)));self.marker_toggle.toggled.connect(self.original.set_markers_visible)
        self.terrain_kind.currentIndexChanged.connect(self._terrain_changed);self.terrain_cells.currentIndexChanged.connect(lambda _:self._combo_selected(self.terrain_cells))
    def clear_reference(self):
        for combo in(self.terrain_kind,self.terrain_cells):
            blocked=combo.blockSignals(True);combo.clear();combo.setEnabled(False);combo.blockSignals(blocked)
        self.grid.highlight_cells=set()
        self.result=None;self.selected=None;self.image_raw=None;self.grid.set_result(None);self.original.set_image(None);blocked=self.combo.blockSignals(True);self.combo.clear();self.combo.blockSignals(blocked);self.combo.setEnabled(False);replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)
    def refresh_reference(self, *, prepared_reference=...):
        if prepared_reference is ...:
            loader=model.stage_reference if self.reference_loader is None else self.reference_loader
            fresh=loader(self.stage_id)
        else:
            fresh=prepared_reference
        if fresh is None:self.clear_reference();return False
        raw=model.battle.version.image_bytes(fresh['image'])
        if raw is None:self.clear_reference();return False
        keep=self.result is not None and self.result['source_identity']==fresh['source_identity']and self.result['stage_id']==fresh['stage_id'];selected=self.selected if keep else None;kind=self.terrain_kind.currentData()if keep else None;self.result=fresh;self.image_raw=raw
        from .current_terrain import terrain_info
        blocked=self.terrain_kind.blockSignals(True);self.terrain_kind.clear();self.terrain_kind.addItem('总览（全部地形）',None);seen=set()
        for row in fresh['map']:
            for index in row:
                tile=fresh['tiles'][index];key=tile.get('tileKey')
                if key not in seen:self.terrain_kind.addItem(terrain_info(tile)['name'],key);seen.add(key)
        self.terrain_kind.setCurrentIndex(max(0,self.terrain_kind.findData(kind)));self.terrain_kind.setEnabled(True);self.terrain_kind.blockSignals(blocked);self._populate_terrain_cells()
        blocked=self.combo.blockSignals(True);self.combo.clear();self.combo.addItem('选择位置，或点击原图编号',None)
        for i,p in enumerate(fresh['points'],1):self.combo.addItem(str(i)+' · '+(p['label']+' · 'if p.get('kind')=='visible_map_symbol'else'')+f"第{p['row']+1}行 · 第{p['col']+1}列",str(p['row'])+':'+str(p['col']))
        self.combo.setEnabled(bool(fresh['points']));self.combo.blockSignals(blocked)
        if selected is None:self.selected=None;self._render(None,preserve=keep)
        else:self.select_cell(*selected,preserve=keep)
        return self.result is not None
    def _combo_selected(self,combo):
        value=combo.currentData()
        if value is not None:self.select_cell(*(int(x)for x in value.split(':')))
    def _populate_terrain_cells(self):
        key=self.terrain_kind.currentData();locations=model.terrain_locations(self.result,key)if key is not None else[]
        blocked=self.terrain_cells.blockSignals(True);self.terrain_cells.clear();self.terrain_cells.addItem('选择地形后，可从这里定位对应格子',None)
        for row in locations:self.terrain_cells.addItem(row['name']+f" · 第{row['row']+1}行 第{row['col']+1}列 · "+('原图中心已核对'if row['mapped_to_original']else'仅格图位置'),str(row['row'])+':'+str(row['col']))
        self.terrain_cells.setEnabled(bool(locations));self.terrain_cells.blockSignals(blocked);self.grid.highlight_cells={(p['row'],p['col'])for p in locations};self.grid.update()
    def _terrain_changed(self,*_):
        if self.result is None:return
        self._populate_terrain_cells();self.selected=None;self._render(None,preserve=False)
    def select_cell(self,row,col,*,preserve=False):
        cell=model.cell_reference(self.result,row,col)
        if cell is None:return False
        kind=self.terrain_kind.currentData()
        if kind is not None and kind!=cell['tile'].get('tileKey'):
            blocked=self.terrain_kind.blockSignals(True);self.terrain_kind.setCurrentIndex(max(0,self.terrain_kind.findData(cell['tile'].get('tileKey'))));self.terrain_kind.blockSignals(blocked);self._populate_terrain_cells()
        keep=preserve and self.selected==(row,col);self.selected=(row,col);self._render(cell,preserve=keep);return self.result is not None
    def _render(self,cell,*,preserve=False):
        self.grid.set_result(self.result,self.selected)
        markers=[]
        for i,p in enumerate(self.result['points'],1):
            name=p['label']if p.get('kind')=='visible_map_symbol'else self.grid.tile_infos[self.result['map'][p['row']][p['col']]]['name']
            markers.append({'key':str(p['row'])+':'+str(p['col']),'point':p,'number':i,'label':f"{i} · {name} · 第{p['row']+1}行 第{p['col']+1}列"})
        if not self.original.set_image(self.image_raw,cell['point']if cell else None,markers=markers):self.clear_reference();return
        value=str(self.selected[0])+':'+str(self.selected[1])if self.selected is not None else None
        for combo in(self.combo,self.terrain_cells):
            blocked=combo.blockSignals(True);combo.setCurrentIndex(max(0,combo.findData(value)));combo.blockSignals(blocked)
        full_text=model.cell_text(self.result,cell)
        replace_text(self.player,mechanism_copy(full_text,'')[0],preserve=preserve);replace_text(self.technical,_technical_json({'完整说明':full_text,'reference':self.result,'selected_cell':cell}),preserve=preserve)
        if not preserve:self.tabs.setCurrentIndex(0)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        orientation=Qt.Orientation.Vertical if event.size().width()<self.fontMetrics().horizontalAdvance('界')*60 else Qt.Orientation.Horizontal
        if self.map_split.orientation()!=orientation:
            self._map_sizes[self.map_split.orientation()]=self.map_split.sizes();self.map_split.setOrientation(orientation);self.map_split.setSizes(self._map_sizes.get(orientation,[1,1]))

from .player_window_frame import PlayerDialog


class CurrentMapPositionDialog(PlayerDialog):
    def __init__(self,stage_id,parent=None,*,initial_reference=...):
        super().__init__(parent);self.setWindowTitle('固定地图 · 格子与原图位置对照');layout=QVBoxLayout(self);self.panel=CurrentMapPositionPanel(stage_id,self,initial_reference=initial_reference);layout.addWidget(self.panel)
        from .player_map_reader import prepare_reference_window
        prepare_reference_window(self,960,640)
