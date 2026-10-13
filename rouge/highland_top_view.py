"""Prototype display of one explicit highland top; no mouse/grid inference."""
import hashlib
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import QWidget, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QDialog

from .highland_top_mapping import highland_top_data, highland_top_reference_for
from .battle_preview import DATA, battle_data


def draw_top_marker(painter, image_rect, reference, cell):
    """Render a surface symbol; deliberately independent of ground routes."""
    pixel = reference.top_center(cell) if reference else None
    if pixel is None:
        return False
    x, y = pixel
    center = QPointF(image_rect.left() + x * image_rect.width() / reference.width,
                     image_rect.top() + y * image_rect.height() / reference.height)
    painter.save()
    painter.setPen(QPen(QColor('#7cefff'), 2))
    painter.setBrush(QColor(70, 215, 245, 70))
    painter.drawPolygon(QPolygonF([center + QPointF(0, -7), center + QPointF(7, 0),
                                  center + QPointF(0, 7), center + QPointF(-7, 0)]))
    painter.restore()
    return True


class HighlandTopCanvas(QWidget):
    """Isolated source inspector; integration must keep existing ground separate."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap()
        self.reference = None
        self.selected_cell = None
        self.source_id = None
        self.setMinimumSize(260, 190)

    def set_source(self, stage, path, data):
        raw = Path(path).read_bytes()
        picture = QPixmap(); picture.loadFromData(raw)
        identity = (stage['id'], hashlib.sha256(raw).hexdigest(), stage['level_source']['sha256'])
        if self.source_id != identity:
            self.selected_cell = None
        self.source_id = identity; self.pixmap = picture
        self.reference = highland_top_reference_for(stage, identity[1], (picture.width(), picture.height()), data)
        self.update()

    def set_cell(self, cell):
        self.selected_cell = dict(cell) if isinstance(cell, dict) else None
        self.update()

    def image_rect(self):
        if self.pixmap.isNull():
            return QRectF()
        scale = min(self.width() / self.pixmap.width(), max(0, self.height() - 36) / self.pixmap.height())
        width, height = self.pixmap.width() * scale, self.pixmap.height() * scale
        return QRectF((self.width() - width) / 2, (self.height() - 36 - height) / 2 + 36, width, height)

    def caption(self):
        point = self.reference.top_center(self.selected_cell) if self.reference else None
        return ('高台名义表面参考；脚点、出生位置与绝对误差未知' if point else
                '本格高台表面位置未直接核对；不使用地面或相邻格补齐')

    def paintEvent(self, event):
        painter = QPainter(self); painter.fillRect(self.rect(), QColor('#18222e'))
        painter.setPen(QColor('white'))
        painter.drawText(QRectF(4, 0, self.width() - 8, 34), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.caption())
        if not self.pixmap.isNull():
            rectangle = self.image_rect()
            painter.drawPixmap(rectangle, self.pixmap, QRectF(self.pixmap.rect()))
            draw_top_marker(painter, rectangle, self.reference, self.selected_cell)


class HighlandTopPanel(QWidget):
    """Source-backed highland selector, with unknown cells kept individually."""
    def __init__(self, stage_id='ro6_n_4_1', parent=None, data=None):
        super().__init__(parent)
        self.data = highland_top_data() if data is None else data
        self.stage = None; self._selection_by_stage = {}; self._source_identity = None
        layout = QVBoxLayout(self)
        intro = QLabel('仅显示独立核对的高台名义表面。脚点、出生位置和实际战斗坐标仍未知；未核对格不借用地面或相邻格。')
        intro.setWordWrap(True); layout.addWidget(intro)
        row = QHBoxLayout(); self.stage_combo = QComboBox(); self.cell_combo = QComboBox()
        for sid in self.data['stages']:
            self._add_stage(sid)
        row.addWidget(QLabel('固定关卡')); row.addWidget(self.stage_combo)
        row.addWidget(QLabel('逻辑高台格')); row.addWidget(self.cell_combo); layout.addLayout(row)
        self.status = QLabel(); self.status.setWordWrap(True); layout.addWidget(self.status)
        self.canvas = HighlandTopCanvas(); layout.addWidget(self.canvas, 1)
        self.stage_combo.currentIndexChanged.connect(lambda: self.set_stage(self.stage_combo.currentData()))
        self.cell_combo.currentIndexChanged.connect(self._cell_changed)
        self.set_stage(stage_id)

    def _add_stage(self, sid):
        stage = battle_data()['stages'][sid]
        difficulty = {'NORMAL': '普通', 'FOUR_STAR': '紧急'}.get(stage['difficulty'], '固定版本')
        self.stage_combo.addItem(stage['name'] + ' · ' + difficulty, sid)

    def set_stage(self, stage_id):
        if stage_id not in battle_data()['stages']:
            raise ValueError('高台资料需要固定目录中的真实关卡ID。')
        selected = self.cell_combo.currentData()
        previous = self.stage
        if previous is not None:
            self._selection_by_stage[previous['id']] = dict(selected) if isinstance(selected, dict) else None
        stage = battle_data()['stages'][stage_id]
        same_source = (previous is not None and previous['image']['sha256'] == stage['image']['sha256'] and
                       previous['level_source']['sha256'] == stage['level_source']['sha256'] and previous['map'] == stage['map'] and
                       previous['tiles'] == stage['tiles'])
        wanted = selected if same_source else self._selection_by_stage.get(stage_id)
        self.stage_combo.blockSignals(True)
        if self.stage_combo.findData(stage_id) < 0:
            self._add_stage(stage_id)
        self.stage_combo.setCurrentIndex(self.stage_combo.findData(stage_id)); self.stage_combo.blockSignals(False)
        self.stage = stage
        self.canvas.set_source(stage, DATA / stage['image']['file'], self.data)
        self.cell_combo.blockSignals(True); self.cell_combo.clear()
        for r, line in enumerate(stage['map']):
            for c, tile_id in enumerate(line):
                tile = stage['tiles'][tile_id]
                if tile['tileKey'] != 'tile_wall' or tile['heightType'] != 'HIGHLAND':
                    continue
                cell = {'row': r, 'col': c}
                point = self.canvas.reference.top_center(cell) if self.canvas.reference else None
                state = '表面参考已核对' if point is not None else '表面位置未知'
                self.cell_combo.addItem(f'第{r + 1}行、第{c + 1}列 · {state}', cell)
        if isinstance(wanted, dict):
            for index in range(self.cell_combo.count()):
                if self.cell_combo.itemData(index) == wanted:
                    self.cell_combo.setCurrentIndex(index); break
        self.cell_combo.blockSignals(False); self._cell_changed()

    def _cell_changed(self):
        cell = self.cell_combo.currentData(); self.canvas.set_cell(cell)
        point = self.canvas.reference.top_center(cell) if self.canvas.reference else None
        if point is None:
            self.status.setText('本格高台名义表面没有独立一致读数；原图位置未知。旧点已清除，不插值、不反算或连路线。')
        else:
            self.status.setText('当前逻辑高台格对应原图上的菱形表面参考。目视读数一致不证明绝对误差、脚点或出生位置；现有地面参考独立保留。')
        if self.stage:
            self._selection_by_stage[self.stage['id']] = dict(cell) if isinstance(cell, dict) else None


class HighlandTopDialog(QDialog):
    def __init__(self, stage_id='ro6_n_4_1', parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle('高台名义表面资料（局外）'); self.resize(1050, 720)
        layout = QVBoxLayout(self); self.panel = HighlandTopPanel(stage_id, self, data)
        layout.addWidget(self.panel)

    def set_stage(self, stage_id):
        self.panel.set_stage(stage_id)
