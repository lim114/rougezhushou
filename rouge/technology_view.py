"""Technology references and explicitly edited account-labelled records."""
from PySide6.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget)
from .technology import format_technology, technology_labels, technology_nodes
from .technology_state import STATUS_LABELS, TechnologyState


class TechnologyReferencePanel(QWidget):
    def __init__(self, parent=None, *, account_path=None):
        super().__init__(parent)
        self.account_state = TechnologyState(account_path)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('沉沦者的黑流树海 · 长期科技资料'))
        scope = QLabel('选择与游戏账户对应的资料档案，逐项手动记录科技解锁状态。当前不自动读取账户，也不将科技效果加入计算。' + ('已保存资料在下次启动和开始新局后保留。' if account_path is not None else ''))
        scope.setWordWrap(True); layout.addWidget(scope)
        profiles = QHBoxLayout()
        self.profiles = QComboBox(); profiles.addWidget(self.profiles, 1)
        self.new_profile_name = QLineEdit(); self.new_profile_name.setPlaceholderText('新资料档案名称（区分不同账户）')
        self.create_profile_button = QPushButton('新建资料档案')
        profiles.addWidget(self.new_profile_name, 1); profiles.addWidget(self.create_profile_button)
        layout.addLayout(profiles)
        self.summary = QLabel(); self.summary.setWordWrap(True); layout.addWidget(self.summary)
        self.persistence = QLabel(); self.persistence.setWordWrap(True); layout.addWidget(self.persistence)
        self.search = QLineEdit()
        self.search.setPlaceholderText('搜索科技名称或效果资料')
        layout.addWidget(self.search)
        self.status_filter = QComboBox()
        for label, status in (('全部科技', None), ('尚未知', 'unknown'), ('已解锁（手动）', 'unlocked'), ('未解锁（手动）', 'locked')):
            self.status_filter.addItem(label, status)
        layout.addWidget(self.status_filter)
        self.nodes = QComboBox(); layout.addWidget(self.nodes)
        edits = QHBoxLayout()
        self.status_buttons = {}
        for status in ('unlocked', 'locked', 'unknown'):
            button = QPushButton('手动记录：' + STATUS_LABELS[status])
            button.clicked.connect(lambda _checked=False, value=status: self.record_status(value))
            self.status_buttons[status] = button; edits.addWidget(button)
        layout.addLayout(edits)
        self.technical = QCheckBox('显示技术资料（原始标识与来源）')
        layout.addWidget(self.technical)
        self.text = QPlainTextEdit(); self.text.setReadOnly(True)
        layout.addWidget(self.text, 1)
        self.search.textChanged.connect(self.populate)
        self.status_filter.currentIndexChanged.connect(self.populate)
        self.profiles.currentIndexChanged.connect(self.select_profile)
        self.create_profile_button.clicked.connect(self.create_profile)
        self.nodes.currentIndexChanged.connect(self.render)
        self.technical.toggled.connect(self.render)
        self.populate_profiles(); self.populate()

    def populate_profiles(self):
        self.profiles.blockSignals(True); self.profiles.clear()
        for profile in self.account_state.profiles():
            self.profiles.addItem(profile['name'], profile['id'])
        self.profiles.setCurrentIndex(self.profiles.findData(self.account_state.selected_profile))
        self.profiles.blockSignals(False)

    def select_profile(self, *_args):
        identity = self.profiles.currentData()
        if identity is not None:
            self.account_state.select_profile(identity)
            self.populate()

    def create_profile(self):
        try:
            self.account_state.create_profile(self.new_profile_name.text())
        except ValueError as error:
            self.persistence.setText(str(error)); return
        self.new_profile_name.clear(); self.populate_profiles(); self.populate()

    def record_status(self, status):
        identity = self.nodes.currentData()
        if identity is not None:
            self.account_state.set_status(identity, status)
            self.populate()

    def populate(self, *_args):
        selected = self.nodes.currentData(); labels = technology_labels()
        self.nodes.blockSignals(True); self.nodes.clear()
        for node in technology_nodes(self.search.text()):
            state = self.account_state.view(node['buffId'])['status']
            if self.status_filter.currentData() is not None and state != self.status_filter.currentData():
                continue
            label = labels[node['buffId']]
            if state != 'unknown': label += '（手动：' + STATUS_LABELS[state] + '）'
            self.nodes.addItem(label, node['buffId'])
        index = self.nodes.findData(selected)
        if index >= 0: self.nodes.setCurrentIndex(index)
        self.nodes.blockSignals(False); self.render()

    def render(self, *_args):
        node_id = self.nodes.currentData()
        counts = self.account_state.counts()
        self.summary.setText(f"本档案{len(self.account_state.known_ids)}项科技：已解锁{counts['unlocked']}、未解锁{counts['locked']}、未知{counts['unknown']}；当前筛选{self.nodes.count()}项。")
        self.persistence.setText(self.account_state.persistence_notice())
        for button in self.status_buttons.values(): button.setEnabled(node_id is not None)
        self.text.setPlainText(format_technology(node_id, technical=self.technical.isChecked(), account_state=self.account_state)
                               if node_id else '没有匹配的长期科技资料。')
