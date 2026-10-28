"""Statistics of qualified archived observations, never of unobserved outcomes."""
from copy import deepcopy
from .record_flags import active_record, record_flag
import sys

def nonnegative_integer(value):
    return type(value) is int and 0 <= value <= sys.float_info.max

def complete_inventory(state):
    from .catalog import catalog, tactical_tools
    if state.get('inventory_verified') is not True or not nonnegative_integer(state.get('relic_count')):
        return False
    collections = [('relics', catalog()['relics']), ('tactical_tools', tactical_tools())]
    total = 0
    for field, known in collections:
        records = state.get(field, {})
        if not isinstance(records, dict):
            return False
        for identity, record in records.items():
            if not isinstance(record, dict) or record_flag(record, 'held') is None:
                return False
            if active_record(record, 'held'):
                if identity not in known:
                    return False
                total += 1
    return total == state['relic_count']

def unique_archives(records):
    result = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get('state'), dict):
            continue
        identity = record['state'].get('id')
        if not isinstance(identity, str) or not identity:
            continue
        # The store returns newest first. Never count two versions of one run twice.
        result.setdefault(identity, record)
    return list(result.values())

def statistics(records, relic_id=None):
    records = unique_archives(records)
    result = {'archive_count': len(records), 'measures': {},
              'outcomes_observed': False, 'relic': None}
    for key, name, getter in [
            ('gold', '归档前最近读到的源石锭', lambda state: state.get('resources', {}).get('gold', {}).get('value')),
            ('parts_count', '归档前最近读到的零件数', lambda state: state.get('resources', {}).get('parts_count', {}).get('value')),
            ('relic_count', '归档前最近读到的藏品栏总数（含道具）', lambda state: state.get('relic_count'))]:
        values = []
        for record in records:
            try:
                value = getter(record['state'])
            except (AttributeError, TypeError):
                value = None
            if nonnegative_integer(value):
                values.append(value)
        result['measures'][key] = {'name': name, 'sample_count': len(values),
                                   'missing_count': len(records) - len(values),
                                   'mean': sum(values) / len(values) if values else None}
    if relic_id is not None:
        from .catalog import catalog
        if relic_id not in catalog()['relics']:
            raise ValueError('所选收藏品不在固定资料中。')
        eligible = [record['state'] for record in records if complete_inventory(record['state'])]
        held = sum(active_record(state.get('relics', {}).get(relic_id, {'held': False}), 'held') for state in eligible)
        result['relic'] = {'id': relic_id, 'name': catalog()['relics'][relic_id]['name'],
                           'sample_count': len(eligible), 'held_count': held,
                           'excluded_incomplete_count': len(records) - len(eligible),
                           'fraction': held / len(eligible) if eligible else None}
    return deepcopy(result)

def statistics_text(result):
    lines = [f'本机已归档{result["archive_count"]}局读取记录',
             '归档来自手动开始新局，不表示通关、失败或完整结算。']
    for row in result['measures'].values():
        mean = f'{row["mean"]:.2f}' if row['mean'] is not None else '未知'
        lines += ['', row['name'], f'平均数：{mean}；有效{row["sample_count"]}局，缺失{row["missing_count"]}局']
    row = result['relic']
    if row:
        fraction = f'{row["fraction"]:.1%}' if row['fraction'] is not None else '未知'
        lines += ['', row['name'] + ' · 归档时持有率：' + fraction,
                  f'持有{row["held_count"]}局 / 完整清单{row["sample_count"]}局；另有{row["excluded_incomplete_count"]}局清单不完整，未计入。',
                  '这是个人已记录样本的持有情况，不是掉落概率或抽取权重。']
    lines += ['', '未读值不会按0计入。没有胜负、最终结算和完整过程依据，不显示胜率、最终收益或全程获得率。',
              '不同游戏版本、个人选择与读取误差可能影响这些记录；不能代表全体玩家或分队强弱。',
              '只在本机计算与显示，不上传这些记录。']
    return '\n'.join(lines)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPlainTextEdit, QPushButton

class PersonalStatisticsPage(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.records = []
        self.result = None
        self.key = None
        self.source_available = False
        body = QVBoxLayout(self)
        self.notice = QLabel('个人统计只使用本机历史归档；尚未归档的当前对局不混入样本。')
        self.notice.setWordWrap(True)
        body.addWidget(self.notice)
        self.relic = QComboBox()
        self.relic.addItem('不查看单件持有率', None)
        from .catalog import catalog
        for identity, row in catalog()['relics'].items():
            self.relic.addItem(row['name'], identity)
        body.addWidget(self.relic)
        self.detail = QPlainTextEdit()
        self.detail.setReadOnly(True)
        body.addWidget(self.detail, 1)
        from .player_cohort_ui import attach_filters
        attach_filters(self,body)
        self.reload = QPushButton('重新读取本机历史')
        body.addWidget(self.reload)
        from .player_statistics_card import CardControls
        self.card_controls=CardControls(self,body)
        self.reload.clicked.connect(self.refresh)
        self.relic.currentIndexChanged.connect(self.render)
        self.refresh()

    def refresh(self):
        try:
            records, issues = self.store.records()
        except (OSError, ValueError, UnicodeError, TypeError, RecursionError) as error:
            from .player_file_messages import file_issue
            self.records = []
            self.source_available = False
            self.notice.setText('本机历史暂时不可用：' + file_issue(error) + ' 旧统计已清除，原件未改动。')
            self.notice.setToolTip(str(error))
            self.key = None
            from .player_cohort_ui import refresh_filters
            refresh_filters(self)
            self.render()
            return
        self.records = records
        from .player_cohort_ui import refresh_filters
        refresh_filters(self)
        self.source_available = True
        self.notice.setToolTip('')
        self.notice.setText(f'读取到{len(records)}局本机历史；另有{len(issues)}份记录无法核对，未计入。当前未归档对局不混入。')
        self.render()

    def render(self, *_):
        if not self.source_available:
            self.result = None
            self.card_controls.sync()
            self.detail.setPlainText('本机历史暂未读到，统计未知；没有用0局或旧结果替代。')
            return
        from .player_cohort_ui import selected_records,filter_notes
        self.result = statistics(selected_records(self), self.relic.currentData())
        self.card_controls.sync()
        text = filter_notes(self)+'\n\n'+statistics_text(self.result)
        if self.detail.toPlainText() != text:
            self.detail.setPlainText(text)
