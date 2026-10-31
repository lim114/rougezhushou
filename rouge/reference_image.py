"""Shared fixed-map thumbnail; keep the original pixels for every resize."""
from PySide6.QtCore import Qt,QEvent
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy


class ReferenceImage(QLabel):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self.original = QPixmap()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

    def set_data(self, raw, unavailable):
        self.clear()
        if raw and self.original.loadFromData(raw, 'PNG'):
            self._fit()
            return True
        self.setText(unavailable)
        return False

    def clear(self):
        self.original = QPixmap()
        super().clear()

    def _fit(self):
        if not self.original.isNull():
            ratio=self.devicePixelRatioF();pixmap=self.original.scaled(self.contentsRect().size()*ratio,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            pixmap.setDevicePixelRatio(ratio);self.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit()

    def event(self,event):
        handled=super().event(event)
        if event.type()==QEvent.Type.DevicePixelRatioChange:self._fit()
        return handled
