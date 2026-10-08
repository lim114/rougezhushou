"""Assistant-local spatial map. Source-frame coordinates never target the game."""
import copy
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget
from .map_reporting import location
from .exploration_routes import route_reference


class MapView(QWidget):
    nodeSelected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 260)
        self.setAccessibleName('探索地图位置预览')
        self.setMouseTracking(True)
        self.graph = None
        self.image = None
        self.selected = None
        self.historical = False

    def set_map(self, graph, image=None, *, historical=False):
        old_key = (self.graph or {}).get('template_id'), (self.graph or {}).get('zone_id')
        new_key = (graph or {}).get('template_id'), (graph or {}).get('zone_id')
        self.graph = copy.deepcopy(graph)
        self.image = image
        self.historical = historical
        if old_key != new_key or not graph or self.selected not in {n['id'] for n in graph['nodes']}:
            self.selected = None
        self.update()
        self.nodeSelected.emit(self.selected or '')

    def select_node(self, node_id):
        if self.graph and node_id in {n['id'] for n in self.graph['nodes']}:
            self.selected = node_id
            self.update()
            self.nodeSelected.emit(node_id)

    def _positions(self):
        canvas = QRectF(self.contentsRect())
        if self.image is not None:
            scale = min(canvas.width()/self.image.width(), canvas.height()/self.image.height())
            w, h = self.image.width()*scale, self.image.height()*scale
            canvas = QRectF(canvas.center().x()-w/2, canvas.center().y()-h/2, w, h)
        points = {}
        if self.graph:
            rows = self.graph['grid']['rows']; cols = self.graph['grid']['cols']
            for node in self.graph['nodes']:
                # Recognition has already mapped centers to the complete source frame.
                # Grid origin/pitch are in a different coordinate space and are not used.
                x, y = node['center'] if self.image is not None else ((node['col']+1)/(cols+1), (node['row']+1)/(rows+1))
                points[node['id']] = QPointF(canvas.left()+x*canvas.width(), canvas.top()+y*canvas.height())
        return canvas, points

    def _badge_width(self, points):
        xs = sorted({round(p.x(), 2) for p in points.values()})
        gap = min((b-a for a, b in zip(xs, xs[1:]) if b-a > 1), default=160)
        return min(200, max(28, gap*.92))

    def route(self):
        return route_reference(self.graph, self.selected, historical=self.historical)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor('#101820'))
        canvas, points = self._positions()
        if not self.graph:
            painter.setPen(QColor('#d1d5db'))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, '尚无地图记录；等待后台采样')
            return
        if self.image is not None:
            painter.drawImage(canvas, self.image)
            painter.fillRect(canvas, QColor(0, 0, 0, 55))
        painter.setClipRect(canvas)
        painter.setPen(QPen(QColor('#91a0ae'), 1.4, Qt.PenStyle.DashLine))
        for a, b in self.graph.get('edges', []):
            if a in points and b in points:
                painter.drawLine(points[a], points[b])
        route = self.route()
        painter.setPen(QPen(QColor('#6ee7df') if route['corridor'] else QColor('#ffcb75'), 3,
                            Qt.PenStyle.SolidLine if route['corridor'] else Qt.PenStyle.DashLine))
        for a,b in zip(route['display_path'],route['display_path'][1:]):
            painter.drawLine(points[a],points[b])
        width = self._badge_width(points)
        font = self.font(); font.setPointSize(9); painter.setFont(font)
        for node in self.graph['nodes']:
            point = points[node['id']]
            prediction = node.get('prediction') or {}
            candidates = prediction.get('candidates', [])
            observed = node.get('observed_type')
            known = observed and not observed.startswith('未知')
            if observed=='林间空地' and node.get('remembered_type'):
                color=QColor('#ffcb75');label='已通过：'+node['remembered_type']
            elif known:
                color = QColor('#59d5f3'); label = '已读：'+observed
            elif node.get('remembered_type'):
                color = QColor('#ffcb75'); label = '记录：'+node['remembered_type']
            elif candidates:
                color = QColor('#d5a4ff')
                label = '候选：'+('/'.join(candidates) if len(candidates)<=2 else f'{len(candidates)}类')
            else:
                color = QColor('#cbd5df'); label = observed or '类型未确认'
            content=node.get('content') or node.get('remembered_content')
            if content:
                label=('内容：' if node.get('content') and not self.historical else '记录：')+content['title']
            painter.setPen(QPen(color, 2, Qt.PenStyle.SolidLine if node.get('visible') else Qt.PenStyle.DashLine))
            painter.setBrush(QColor('#101820'))
            painter.drawEllipse(point, 9, 9)
            current = self.graph.get('current_node')
            last = self.graph.get('last_confirmed_current_node')
            position_label = None
            if not self.historical and current == node['id']:
                painter.setPen(QPen(QColor('#6ef39a'), 3)); position_label = '当前位置'
            elif (last or current) == node['id'] and (self.historical or not current):
                painter.setPen(QPen(QColor('#ffcb75'), 2, Qt.PenStyle.DashLine)); position_label = '最近位置（历史）'
            if position_label:
                painter.setBrush(Qt.BrushStyle.NoBrush); painter.drawEllipse(point, 15, 15)
                painter.drawText(QRectF(point.x()-width/2, point.y()-38, width, 19), Qt.AlignmentFlag.AlignCenter,
                                 painter.fontMetrics().elidedText(position_label, Qt.TextElideMode.ElideRight, int(width)))
            if self.selected == node['id']:
                painter.setPen(QPen(QColor('#ffffff'), 2)); painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(point, 20, 20)
            badge = QRectF(point.x()-width/2, point.y()+20, width, 22)
            painter.fillRect(badge, QColor(10, 16, 24, 220)); painter.setPen(color)
            painter.drawText(badge, Qt.AlignmentFlag.AlignCenter,
                             painter.fontMetrics().elidedText(label, Qt.TextElideMode.ElideRight, int(width)-6))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            node_id = self._hit(event.position())
            if node_id:
                self.select_node(node_id)
        super().mouseReleaseEvent(event)

    def _hit(self, point):
        _, points = self._positions()
        width = self._badge_width(points)
        hits = [(abs(p.x()-point.x())+abs(p.y()-point.y()), node_id)
                for node_id, p in points.items()
                if QRectF(p.x()-width/2, p.y()-20, width, 62).contains(point)]
        return min(hits)[1] if hits else None

    def mouseMoveEvent(self, event):
        node_id = self._hit(event.position())
        self.setCursor(Qt.CursorShape.PointingHandCursor if node_id else Qt.CursorShape.ArrowCursor)
        if node_id:
            node = next(n for n in self.graph['nodes'] if n['id']==node_id)
            self.setToolTip(location(node, self.graph['grid']['rows'])+'；点击查看完整类型与候选依据')
        else:
            self.setToolTip('')
        super().mouseMoveEvent(event)
