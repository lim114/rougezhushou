"""Owned player dialogs use the pinned LGPL qframelesswindow implementation.

Upstream source and licenses: third_party/qframelesswindow/LICENSE and COPYING.
Application panels remain Qt dialogs.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QSizePolicy
from third_party.qframelesswindow import FramelessDialog, StandardTitleBar


class PlayerDialog(FramelessDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setTitleBar(StandardTitleBar(self))
        bar = self.titleBar
        # Navigation/resources can wrap: the upstream fixed 32px title is too short.
        bar.setMaximumHeight(self.maximumHeight())
        bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        bar.minBtn.hide(); bar.maxBtn.hide(); bar.iconLabel.hide()
        bar.setDoubleClickEnabled(False)
        bar.hBoxLayout.takeAt(0)
        bar.hBoxLayout.setAlignment(Qt.AlignmentFlag(0))
        for i in range(bar.hBoxLayout.count()):
            if bar.hBoxLayout.itemAt(i).spacerItem() is not None:
                bar.hBoxLayout.setStretch(i, 0)
        bar.hBoxLayout.setStretchFactor(bar.titleLabel, 1)
        bar.titleLabel.setObjectName('popoverTitle')
        bar.titleLabel.setStyleSheet('background:transparent;padding:0 4px;')
        bar.setTitle(self.windowTitle())
        bar.closeBtn.setObjectName('popoverCloseButton')
        bar.closeBtn.setAccessibleName('关闭此窗口')
        bar.closeBtn.setToolTip('关闭此窗口')
        bar.closeBtn.setFixedSize(30, 30)
        self.frame_ready = False
        self.setSizeGripEnabled(True)

    def setWindowFlag(self, flag, on=True):
        super().setWindowFlag(flag, on)
        # Qt recreates native styles when the player's stay-on-top flag changes.
        self.updateFrameless()

    def set_frame_theme(self, theme):
        foreground, control = ('#303139', '#e6e6eb') if theme == 'light' else ('#ededed', '#484848')
        button = self.titleBar.closeBtn
        for setter in (button.setNormalColor, button.setHoverColor, button.setPressedColor):
            setter(foreground)
        button.setNormalBackgroundColor(Qt.GlobalColor.transparent)
        button.setHoverBackgroundColor(control)
        button.setPressedBackgroundColor(control)

    def showEvent(self, event):
        if not self.frame_ready:
            self.frame_ready = True
            self.layout().insertWidget(0, self.titleBar)
            if self.property('playerTheme') is None:
                from .player_theme import apply_theme
                apply_theme(self, 'dark')
        super().showEvent(event)

    def resizeEvent(self, event):
        # The existing dialog layout owns the title bar's actual geometry.
        # Upstream's native frame hit-testing stays unchanged.
        QDialog.resizeEvent(self, event)
