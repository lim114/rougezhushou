"""Current static map comparison; image clicks never infer unmeasured cells."""
from PySide6.QtCore import Qt,QPointF,QRectF,Signal
from PySide6.QtGui import QPainter,QPen,QColor,QPixmap
from PySide6.QtWidgets import QWidget,QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QPushButton,QSplitter,QTabWidget,QPlainTextEdit
from . import current_map_position as model
from .boss_hunt_view import _technical_json
from .ui_state import replace_text

class CurrentTileGrid(QWidget):
    cellSelected=Signal(int,int)
    def __init__(self,parent=None):
        super().__init__(parent);self.result=None;self.selected=None;self.setMinimumSize(300,180);self.setAccessibleName('当前固定地图的方格图')
    def set_result(self,result,selected=None):self.result=result;self.selected=selected;self.update()
    def grid_rect(self):
        if self.result is None:return QRectF()
        available=QRectF(self.contentsRect()).adjusted(27,22,-5,-5);side=min(available.width()/self.result['cols'],available.height()/self.result['rows']);return QRectF(available.center().x()-side*self.result['cols']/2,available.center().y()-side*self.result['rows']/2,side*self.result['cols'],side*self.result['rows'])
    def center(self,row,col):
        rect=self.grid_rect()
        if self.result is None or not 0<=row<self.result['rows']or not 0<=col<self.result['cols']:return None
        side=rect.width()/self.result['cols'];return QPointF(rect.left()+(col+.5)*side,rect.top()+(row+.5)*side)
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('#15212b'))
        if self.result is None:return
        rect=self.grid_rect();side=rect.width()/self.result['cols'];colors={'tile_start':'#75403e','tile_end':'#285d78','tile_floor':'#40594b','tile_road':'#52645a','tile_wall':'#685e4b','tile_forbidden':'#252e37'};names={'tile_start':'入口','tile_end':'目标','tile_floor':'地','tile_road':'路','tile_wall':'高'}
        for row in range(self.result['rows']):
            for col in range(self.result['cols']):
                tile=self.result['tiles'][self.result['map'][row][col]];cell=QRectF(rect.left()+col*side,rect.top()+row*side,side,side);p.fillRect(cell,QColor(colors.get(tile.get('tileKey'),'#3c4350')));p.setPen(QPen(QColor('#87919c'),1));p.drawRect(cell);p.setPen(QColor('#f2f4f7'));p.drawText(cell,Qt.AlignmentFlag.AlignCenter,names.get(tile.get('tileKey'),''))
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
    def __init__(self,parent=None):
        super().__init__(parent);self.pixmap=QPixmap();self.point=None;self.setMinimumSize(300,180);self.setToolTip('请在左侧选格子；右侧只标出已核对的近似中心，不点击图片猜测其它格子。')
    def set_image(self,raw,point=None):
        self.pixmap=QPixmap();ok=bool(raw)and self.pixmap.loadFromData(raw,'PNG');self.point=point if ok else None;self.update();return ok
    def image_rect(self):
        if self.pixmap.isNull():return QRectF()
        ratio=min(self.width()/self.pixmap.width(),self.height()/self.pixmap.height());w,h=self.pixmap.width()*ratio,self.pixmap.height()*ratio;return QRectF((self.width()-w)/2,(self.height()-h)/2,w,h)
    def point_center(self):
        if self.point is None or self.pixmap.isNull():return None
        rect=self.image_rect();x,y=self.point['pixel'];return QPointF(rect.left()+x*rect.width()/self.pixmap.width(),rect.top()+y*rect.height()/self.pixmap.height())
    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('#15212b'))
        if self.pixmap.isNull():return
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform);p.drawPixmap(self.image_rect(),self.pixmap,QRectF(self.pixmap.rect()));center=self.point_center()
        if center is not None:
            p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setPen(QPen(QColor('#ffb4ee'),3));p.setBrush(Qt.BrushStyle.NoBrush);p.drawEllipse(center,8,8);p.drawLine(center+QPointF(-13,0),center+QPointF(13,0));p.drawLine(center+QPointF(0,-13),center+QPointF(0,13))

class CurrentMapPositionPanel(QWidget):
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.stage_id=stage_id;self.result=None;self.selected=None;self.image_raw=None
        layout=QVBoxLayout(self);self.notice=QLabel('左侧点格子，右侧看已核对的近似中心。只读固定资料，不读取或操作战斗。');self.notice.setWordWrap(True);layout.addWidget(self.notice)
        bar=QHBoxLayout();self.combo=QComboBox();self.combo.setAccessibleName('已核对的格子中心');self.refresh_button=QPushButton('重新核对本图位置');bar.addWidget(self.combo,1);bar.addWidget(self.refresh_button);layout.addLayout(bar)
        split=QSplitter();self.grid=CurrentTileGrid();self.original=CurrentOriginalCenters();split.addWidget(self.grid);split.addWidget(self.original);split.setSizes([500,650]);layout.addWidget(split,2)
        self.tabs=QTabWidget();self.player=QPlainTextEdit();self.player.setReadOnly(True);self.technical=QPlainTextEdit();self.technical.setReadOnly(True);self.tabs.addTab(self.player,'格子与位置说明');self.tabs.addTab(self.technical,'地形与核对依据');layout.addWidget(self.tabs,1)
        self.grid.cellSelected.connect(self.select_cell);self.combo.currentIndexChanged.connect(self._combo_selected);self.refresh_button.clicked.connect(self.refresh_reference);self.refresh_reference()
    def clear_reference(self):
        self.result=None;self.selected=None;self.image_raw=None;self.grid.set_result(None);self.original.set_image(None);blocked=self.combo.blockSignals(True);self.combo.clear();self.combo.blockSignals(blocked);self.combo.setEnabled(False);replace_text(self.player,model.UNAVAILABLE,preserve=False);replace_text(self.technical,'',preserve=False);self.tabs.setCurrentIndex(0)
    def refresh_reference(self):
        fresh=model.stage_reference(self.stage_id)
        if fresh is None:self.clear_reference();return False
        raw=model.battle.version.image_bytes(fresh['image'])
        if raw is None:self.clear_reference();return False
        keep=self.result is not None and self.result['source_identity']==fresh['source_identity']and self.result['stage_id']==fresh['stage_id'];selected=self.selected if keep else None;self.result=fresh;self.image_raw=raw
        blocked=self.combo.blockSignals(True);self.combo.clear();self.combo.addItem('选择已核对格子，或在左侧点选其它格子',None)
        for p in fresh['points']:self.combo.addItem((p['label']+' · 'if p.get('kind')=='visible_map_symbol'else'')+f"第{p['row']+1}行 · 第{p['col']+1}列",str(p['row'])+':'+str(p['col']))
        self.combo.setEnabled(bool(fresh['points']));self.combo.blockSignals(blocked)
        if selected is None:self.selected=None;self._render(preserve=keep)
        else:self.select_cell(*selected,preserve=keep)
        return self.result is not None
    def _combo_selected(self,*_):
        value=self.combo.currentData()
        if value is not None:self.select_cell(*(int(x)for x in value.split(':')))
    def select_cell(self,row,col,*,preserve=False):
        if model.cell_reference(self.result,row,col)is None:return False
        keep=preserve and self.selected==(row,col);self.selected=(row,col);self._render(preserve=keep);return self.result is not None
    def _render(self,*,preserve=False):
        cell=model.cell_reference(self.result,*self.selected)if self.selected is not None else None;self.grid.set_result(self.result,self.selected)
        if not self.original.set_image(self.image_raw,cell['point']if cell else None):self.clear_reference();return
        blocked=self.combo.blockSignals(True);self.combo.setCurrentIndex(max(0,self.combo.findData(str(self.selected[0])+':'+str(self.selected[1])if self.selected is not None else None)));self.combo.blockSignals(blocked)
        replace_text(self.player,model.cell_text(self.result,cell),preserve=preserve);replace_text(self.technical,_technical_json({'reference':self.result,'selected_cell':cell}),preserve=preserve)
        if not preserve:self.tabs.setCurrentIndex(0)

class CurrentMapPositionDialog(QDialog):
    def __init__(self,stage_id,parent=None):
        super().__init__(parent);self.setWindowTitle('固定地图 · 格子与原图位置对照');self.resize(1150,800);layout=QVBoxLayout(self);self.panel=CurrentMapPositionPanel(stage_id,self);layout.addWidget(self.panel)
