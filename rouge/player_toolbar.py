"""One-row transparent dock. Names belong inside the hovered button."""
from PySide6.QtCore import Qt,QSize,QPoint,Signal,Property,QPropertyAnimation,QEasingCurve
from PySide6.QtGui import QIcon,QPixmap,QPainter,QColor,QPen
from PySide6.QtWidgets import QToolButton,QApplication

DIAMETER=32
GAP=8
LABEL_SPACE=64
ORDER=('本局概况','聊天分析','本局藏品','地图与节点','场景笔记','干员与技能','工具设置')
NAMES=('本局','聊天','背包','地图','备忘录','计算器','设置')

def dock_icon(name,light=False):
    ink='#f8fafb'if light else'#303335'
    # Original vector artwork: familiar solid symbols, not another project's logo.
    paths={
      'overview':'<path d="M4 18Q2 10 7 6L9 3l2 3Q19 3 21 12l-1 7Q11 23 4 18Z"/><path fill="white" d="M6 15q0-5 6-5t6 5v3q-6 3-12-1Z"/><path fill="'+ink+'" d="m6 14 4-6 2 6 4-5 3 6Z"/><circle cx="10" cy="17" r=".8"/><circle cx="16" cy="17" r=".8"/>',
      'chat':'<circle fill="#5ed4e7" cx="12" cy="12" r="11"/><path fill="#fff" d="m7 5-4 6h3v4q0 5 5 5h6v-4h-5q-2 0-2-2v-3h3Z"/>',
      'bag':'<path d="M4 7h16q2 0 2 3v10H2V10q0-3 2-3Z"/><path fill="none" stroke="'+ink+'" stroke-width="2" d="M8 7V4h8v3"/><path stroke="white" stroke-width="1.5" d="M3 11h18M7 8v8M12 8v8M17 8v8"/>',
      'map':'<path d="m2 5 6-2 8 3 6-2v16l-6 2-8-3-6 2Z"/><path fill="white" d="m4 6 4-1v12l-4 1Zm12 2 4-1v11l-4 1Z"/>',
      'note':'<rect x="3" y="3" width="18" height="18" rx="1"/><path stroke="white" stroke-width="1.6" d="M7 5v14M10 10h8M10 14h8"/>',
      'calc':'<rect x="5" y="2" width="15" height="21" rx="1"/><path fill="white" d="M8 5h9v5H8Zm0 8h2v2H8Zm4 0h2v2h-2Zm4 0h2v2h-2Zm-8 4h2v2H8Zm4 0h2v2h-2Zm4 0h2v2h-2Z"/>',
      'settings':'<path d="m10 1 4 0 1 3 3 1 3 0 2 4-2 3 1 3-1 4-4 1-2 3h-5l-2-3-4-1-1-4 1-3-2-3 2-4 3 0 3-1Z"/><circle fill="white" cx="12" cy="12" r="4"/>'}
    cut='#303335'if light else'#fff'
    drawing=paths[name].replace('fill="white"','fill="'+cut+'"').replace('stroke="white"','stroke="'+cut+'"')
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 24 24"><g fill="'+ink+'">'+drawing+'</g></svg>'
    pixmap=QPixmap();pixmap.loadFromData(svg.encode(),'SVG');return QIcon(pixmap)

class DockButton(QToolButton):
    hoverChanged=Signal(object)
    geometryChanged=Signal()
    dragged=Signal(QPoint)
    def __init__(self,name,glyph,parent=None):
        super().__init__(parent);self.label=name;self.normal_icon=dock_icon(glyph);self.light_icon=dock_icon(glyph,True)
        self._amount=0.;self._target=False;self._press=None;self._last=None;self._dragging=False;self._keyboard=False
        self.setFixedSize(DIAMETER,DIAMETER);self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor);self.setIcon(self.normal_icon);self.setIconSize(QSize(18,18))
        self.setAccessibleDescription('悬停显示名称；按住图标拖动可移动工具条；键盘也可选择并打开。')
        self.setStyleSheet('QToolButton{background:transparent;border:0;padding:0;}')
        self.animation=QPropertyAnimation(self,b'amount',self);self.animation.setDuration(150);self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    def get_amount(self):return self._amount
    def set_amount(self,value):
        self._amount=max(0.,min(1.,float(value)));self.setFixedWidth(DIAMETER+round(LABEL_SPACE*self._amount));self.geometryChanged.emit();self.update()
    amount=Property(float,get_amount,set_amount)
    def set_expanded(self,value,*,animate=True):
        value=bool(value)
        if value==self._target and animate:return
        self._target=value;self.animation.stop()
        if animate:
            self.animation.setStartValue(self._amount);self.animation.setEndValue(1. if value else 0.);self.animation.start()
        else:self.set_amount(1. if value else 0.)
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.isEnabled():painter.setOpacity(.5)
        active=self._amount>.01;painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(47,50,53,240)if active else QColor('#fbfdfd'))
        painter.drawRoundedRect(self.rect().adjusted(0,0,-1,-1),DIAMETER/2,DIAMETER/2)
        (self.light_icon if active else self.normal_icon).paint(painter,7,7,18,18)
        if active:
            painter.setPen(QColor('#fff'));font=painter.font();font.setPixelSize(11);font.setWeight(font.Weight.DemiBold);painter.setFont(font)
            painter.drawText(self.rect().adjusted(DIAMETER+1,0,-7,0),Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignLeft,self.label)
        if self.hasFocus()and self._keyboard:
            painter.setPen(QPen(QColor('#54d2e2'),1.5));painter.setBrush(Qt.BrushStyle.NoBrush);painter.drawRoundedRect(self.rect().adjusted(2,2,-3,-3),14,14)
    def enterEvent(self,event):self.hoverChanged.emit(self);super().enterEvent(event)
    def leaveEvent(self,event):
        if not self._keyboard:self.hoverChanged.emit(None)
        super().leaveEvent(event)
    def focusInEvent(self,event):
        self._keyboard=event.reason()in(Qt.FocusReason.TabFocusReason,Qt.FocusReason.BacktabFocusReason,Qt.FocusReason.ShortcutFocusReason)
        if self._keyboard:self.hoverChanged.emit(self)
        super().focusInEvent(event)
    def focusOutEvent(self,event):
        self._keyboard=False;self.hoverChanged.emit(self if self.underMouse()else None);super().focusOutEvent(event)
    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:self._press=event.globalPosition().toPoint();self._last=self._press;self._dragging=False
        super().mousePressEvent(event)
    def mouseMoveEvent(self,event):
        point=event.globalPosition().toPoint()
        if self._press is not None and event.buttons()&Qt.MouseButton.LeftButton:
            if self._dragging or(point-self._press).manhattanLength()>=QApplication.startDragDistance():
                self._dragging=True;self.setDown(False);self.dragged.emit(point-self._last);self._last=point;event.accept();return
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self,event):
        dragged=self._dragging;self._press=None;self._last=None;self._dragging=False
        if dragged:self.setDown(False);event.accept();return
        super().mouseReleaseEvent(event)
