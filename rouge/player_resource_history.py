"""Changes between actual consecutive readings, without attributing a reward."""
import math
from .player_replay import observation_time

def resource_name(key):
    from .relic_counter_semantics import RESOURCE_LABELS
    return RESOURCE_LABELS.get(key, '未核对资源')

def numeric_read(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and value >= 0
    except OverflowError:
        return False

def read_capacity(value, amount=None):
    """Known integer limit, paired with an already-qualified amount or None."""
    return value if type(value) is int and value >= 0 and (amount is None or value >= amount) else None


def resource_rows(state):
    from .relic_counter_semantics import RESOURCE_CAPACITY_LABELS
    prior = {}
    prior_capacities = {}
    rows = []
    for index, event in enumerate(state.get('history', [])):
        if not isinstance(event, dict) or event.get('kind') != 'resource_updated':
            continue
        key = event.get('resource')
        if not isinstance(key, str):
            continue
        raw = event.get('value')
        value = raw if numeric_read(raw) else None
        old = prior.get(key)
        row = {'index': index, 'resource': key, 'name': resource_name(key),
                     'value': value, 'previous': old,
                     'delta': value - old if value is not None and old is not None else None,
                     'time': observation_time(event.get('at'))}
        if key in RESOURCE_CAPACITY_LABELS and ('capacity' in event or key in prior_capacities):
            capacity = read_capacity(event.get('capacity'), value)
            previous = prior_capacities.get(key)
            row.update(capacity=capacity, previous_capacity=previous,
                capacity_delta=capacity-previous if capacity is not None and previous is not None else None)
            prior_capacities[key] = capacity
        rows.append(row)
        # An unreadable intermediate record breaks, rather than repairs, the chain.
        prior[key] = value
    return rows

def resource_text(row):
    current = f'{row["value"]:g}' if row['value'] is not None else '本条无法核对'
    delta = f'{row["delta"]:+g}' if row['delta'] is not None else '未知（缺少相邻的有效读取）'
    lines = [row['name'], row['time'], '读到数量：' + current, '相对上次已读数量：' + delta]
    if 'capacity' in row:
        from .relic_counter_semantics import RESOURCE_CAPACITY_LABELS
        label = RESOURCE_CAPACITY_LABELS[row['resource']]
        limit = str(row['capacity']) if row['capacity'] is not None else '未读'
        change = f'{row["capacity_delta"]:+g}' if row['capacity_delta'] is not None else '未知（缺少相邻的有效读取）'
        lines += ['读到' + label + '：' + limit, label + '相对上次变化：' + change]
    return '\n'.join([*lines, '',
                      '变化只覆盖两次读取之间，期间可能有多次获得或消耗。',
                      '不能据此确定某个节点的奖励、购买金额、掉落或结算收益。'])

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem, QPlainTextEdit

class ResourceHistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.key = None
        body = QVBoxLayout(self)
        self.notice = QLabel('资源变化来自已读数值；首次读到不是从0增加，不归因到相邻节点。')
        self.notice.setWordWrap(True)
        body.addWidget(self.notice)
        self.filter = QComboBox()
        body.addWidget(self.filter)
        self.entries = QListWidget()
        body.addWidget(self.entries, 1)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        body.addWidget(self.detail, 1)
        self.filter.currentIndexChanged.connect(self.show_rows)
        self.entries.currentItemChanged.connect(self.selected)

    def refresh(self, state):
        rows = resource_rows(state)
        key = repr((state.get('id'), rows))
        if key == self.key:
            return
        changed_run = getattr(self, 'run_id', None) != state.get('id')
        self.run_id = state.get('id')
        self.key, self.rows = key, rows
        if changed_run:
            self.entries.clear()
        old = self.filter.currentData()
        self.filter.blockSignals(True)
        self.filter.clear()
        self.filter.addItem('全部已读资源', None)
        for identity in dict.fromkeys(row['resource'] for row in rows):
            self.filter.addItem(resource_name(identity), identity)
        self.filter.setCurrentIndex(max(0, self.filter.findData(old)))
        self.filter.blockSignals(False)
        self.show_rows()

    def show_rows(self, *_):
        item = self.entries.currentItem()
        old = item.data(Qt.ItemDataRole.UserRole) if item else None
        offset = self.entries.verticalScrollBar().value()
        self.entries.blockSignals(True)
        self.entries.clear()
        for row in self.rows:
            if self.filter.currentData() is not None and row['resource'] != self.filter.currentData():
                continue
            value = f'{row["value"]:g}' if row['value'] is not None else '未核对'
            delta = f'（变化{row["delta"]:+g}）' if row['delta'] is not None else '（变化未知）'
            if 'capacity' in row:
                value += '/' + (str(row['capacity']) if row['capacity'] is not None else '未读')
                if row['capacity_delta'] is not None:
                    from .relic_counter_semantics import RESOURCE_CAPACITY_LABELS
                    delta += f' {RESOURCE_CAPACITY_LABELS[row["resource"]]}{row["capacity_delta"]:+g}'
            item = QListWidgetItem(row['time'] + ' · ' + row['name'] + ' ' + value + delta)
            item.setData(Qt.ItemDataRole.UserRole, row['index'])
            self.entries.addItem(item)
            if row['index'] == old:
                self.entries.setCurrentItem(item)
        self.entries.verticalScrollBar().setValue(offset)
        self.entries.blockSignals(False)
        self.selected()

    def selected(self, *_):
        item = self.entries.currentItem()
        row = next((row for row in self.rows if row['index'] == item.data(Qt.ItemDataRole.UserRole)), None) if item else None
        text = resource_text(row) if row else '选择一条资源读取记录；没有读到的变化保持未知。'
        if self.detail.toPlainText() != text:
            self.detail.setPlainText(text)
