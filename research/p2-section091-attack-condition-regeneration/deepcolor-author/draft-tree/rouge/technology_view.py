"""Read-only browser for the local technology references."""
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget
from .technology import format_technology, technology_labels, technology_nodes


class TechnologyReferencePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('沉沦者的黑流树海 · 长期科技资料'))
        self.search = QLineEdit()
        self.search.setPlaceholderText('搜索科技名称或效果资料')
        layout.addWidget(self.search)
        self.nodes = QComboBox(); layout.addWidget(self.nodes)
        self.technical = QCheckBox('显示技术资料（原始标识与来源）')
        layout.addWidget(self.technical)
        self.text = QPlainTextEdit(); self.text.setReadOnly(True)
        layout.addWidget(self.text, 1)
        self.search.textChanged.connect(self.populate)
        self.nodes.currentIndexChanged.connect(self.render)
        self.technical.toggled.connect(self.render)
        self.populate()

    def populate(self, *_args):
        selected = self.nodes.currentData(); labels = technology_labels()
        self.nodes.blockSignals(True); self.nodes.clear()
        for node in technology_nodes(self.search.text()):
            self.nodes.addItem(labels[node['buffId']], node['buffId'])
        index = self.nodes.findData(selected)
        if index >= 0: self.nodes.setCurrentIndex(index)
        self.nodes.blockSignals(False); self.render()

    def render(self, *_args):
        node_id = self.nodes.currentData()
        self.text.setPlainText(format_technology(node_id, technical=self.technical.isChecked())
                               if node_id else '没有匹配的长期科技资料。')
