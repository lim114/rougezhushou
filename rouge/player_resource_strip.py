"""Shared video-style resource pills, wrapping by the actual available width."""
from html import escape
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy
from .flow_layout import FlowLayout
from .player_resource_facts import resource_rows


class ResourceStrip(QWidget):
    requested = Signal(str)

    def __init__(self, state=None, parent=None, *, dark=False, leading=()):
        super().__init__(parent)
        self.rows = []
        self.chips = {}
        self.setObjectName('runResourceStrip')
        self.setAccessibleName('本局最近已读资源；未读不代表零；不是所选历史层当时数量')
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.flow = FlowLayout(self)
        self.flow.setSpacing(6)
        self.leading=leading
        for widget in leading:self.flow.addWidget(widget)
        background, foreground = ('#2d3235', '#edf0ee') if dark else ('#e5e6e9', '#44484c')
        self.foreground = foreground
        self.setStyleSheet(f'#runResourceStrip QLabel{{background:{background};color:{foreground};'
                          'border:0;border-radius:12px;padding:5px 9px;font-size:9pt;}}')
        self.refresh(state or {})

    def resizeEvent(self,event):
        for widget in self.leading:widget.setMaximumWidth(self.width())
        super().resizeEvent(event)

    def refresh(self, state):
        self.set_rows(resource_rows(state))

    def set_rows(self, rows):
        if rows == self.rows:
            return
        new_keys=[row['key'] for row in rows]
        keys=set(new_keys)
        old_keys=[row['key']for row in self.rows]
        for key in self.chips.keys()-keys:
            chip=self.chips.pop(key);self.flow.removeWidget(chip);chip.hide();chip.deleteLater()
        self.rows = rows
        for row in rows:
            key = row['key']
            if key not in self.chips:
                chip = QLabel()
                chip.setTextFormat(Qt.TextFormat.RichText)
                if key in ('items', 'parts', 'crew'):
                    chip.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse
                                                 | Qt.TextInteractionFlag.LinksAccessibleByKeyboard)
                    chip.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                    chip.linkActivated.connect(self.requested.emit)
                self.flow.addWidget(chip)
                self.chips[key] = chip
            chip = self.chips[key]
            content = escape(row['name']) + '　<b>' + escape(row['value']) + '</b>'
            if key in ('items', 'parts', 'crew'):
                content = f'<a href="{key}" style="color:{self.foreground};text-decoration:none">{content}</a>'
            chip.setText(content)
            chip.setAccessibleName(row['name'] + ' ' + row['value'])
            chip.setToolTip(row['note'])
        if old_keys!=new_keys:
            for row in rows:self.flow.removeWidget(self.chips[row['key']])
            for row in rows:self.flow.addWidget(self.chips[row['key']])
        self.flow.invalidate()
        self.updateGeometry()
