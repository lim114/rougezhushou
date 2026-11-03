"""Owned player dialogs use the pinned LGPL qframelesswindow implementation.

Upstream source and licenses: third_party/qframelesswindow/LICENSE and COPYING.
Application panels remain Qt dialogs.
"""
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QRegion
from PySide6.QtWidgets import QDialog, QSizePolicy, QStyleOption, QStyle
from third_party.qframelesswindow import FramelessDialog, StandardTitleBar


class PlayerDialog(FramelessDialog):
    CLOSE_SIZE = 18
    CLOSE_GUTTER = 24

    def __init__(self, parent=None):
        self.frame_ready = False
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
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
        bar.hBoxLayout.removeWidget(bar.closeBtn)
        bar.closeBtn.setParent(self)
        bar.closeBtn.setFixedSize(self.CLOSE_SIZE, self.CLOSE_SIZE)
        bar.closeBtn.setMask(QRegion(bar.closeBtn.rect(), QRegion.RegionType.Ellipse))
        bar.closeBtn.show()

    def setWindowFlag(self, flag, on=True):
        super().setWindowFlag(flag, on)
        # Qt recreates native styles when the player's stay-on-top flag changes.
        self.updateFrameless()

    def set_frame_theme(self, theme):
        button = self.titleBar.closeBtn
        for setter in (button.setNormalColor, button.setHoverColor, button.setPressedColor):
            setter('#ededed')
        button.setNormalBackgroundColor('#353b3c')
        button.setHoverBackgroundColor('#50595a')
        button.setPressedBackgroundColor('#242a2b')

    def showEvent(self, event):
        if not self.frame_ready:
            self.frame_ready = True
            self.layout().insertWidget(0, self.titleBar)
            margins = self.layout().contentsMargins()
            self.layout().setContentsMargins(margins.left(), margins.top(), margins.right()+self.CLOSE_GUTTER, margins.bottom())
            self.titleBar.closeBtn.move(self.width()-self.CLOSE_SIZE, 0)
            if self.property('playerTheme') is None:
                from .player_theme import apply_theme
                apply_theme(self, 'dark')
        super().showEvent(event)

    def resizeEvent(self, event):
        # The existing dialog layout owns the title bar's actual geometry.
        QDialog.resizeEvent(self, event)
        if self.frame_ready:
            self.titleBar.closeBtn.move(self.width()-self.CLOSE_SIZE, 0)

    def paintEvent(self, event):
        option = QStyleOption()
        option.initFrom(self)
        option.rect = self.rect().adjusted(0, 0, -self.CLOSE_GUTTER, 0)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, option, painter, self)

    def nativeEvent(self, event_type, message):
        if sys.platform == 'win32' and self.frame_ready and self._isResizeEnabled:
            from ctypes.wintypes import MSG
            import win32gui, win32api, win32con
            msg = MSG.from_address(int(message))
            if msg.message == win32con.WM_NCHITTEST:
                x, y = win32gui.ScreenToClient(msg.hWnd, win32api.GetCursorPos())
                _, _, width, height = win32gui.GetClientRect(msg.hWnd)
                right = width-round(self.CLOSE_GUTTER*self.devicePixelRatioF())
                if right-self.BORDER_WIDTH < x < right:
                    return True, win32con.HTTOPRIGHT if y < self.BORDER_WIDTH else win32con.HTBOTTOMRIGHT if y > height-self.BORDER_WIDTH else win32con.HTRIGHT
        return super().nativeEvent(event_type, message)
